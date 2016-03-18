#!/usr/bin/env python

import time
import datetime
import MySQLdb
import smtplib
import sys
import subprocess
import RPi.GPIO as io
import configSettings
import logging
import logging.handlers


# Establish the GPIO Pins from the Raspberry Pi
io.setmode(io.BCM)

# Define variables
REOCCURRING_LOOP_TIME = 1
MAX_COUNT = 1
MAX_SECONDS = 60
FIVE_MINUTES_IN_SECONDS = 300
DB_REFRESH_TIME = 30
MAX_ALERT_SEND_COUNT = 5
MAX_ALERT_SEND_INTERVAL = 300
EVAL_ALERT_ACTION_INTERVAL = 30

#Get configuration values from config file

# Should events be logged to DB?
LOG_ENTRIES = configSettings.LOG_ENTRIES
LOG_ENTRIES_EXCEPTION_ONLY = configSettings.LOG_ENTRIES_EXCEPTION_ONLY

# DB connection details
HOST_NAME = configSettings.HOST_NAME 
DB_USER = configSettings.DB_USER
DB_PASSWORD = configSettings.DB_PASSWORD
DB_DATABASE = configSettings.DB_DATABASE
TIME_ZONE_OFFSET = configSettings.TIME_ZONE_OFFSET
DAY_OF_WEEK_OFFSET = configSettings.DAY_OF_WEEK_OFFSET

# Find these values at https://twilio.com/user/account
ACCOUNT_SID = configSettings.ACCOUNT_SID
AUTH_TOKEN = configSettings.AUTH_TOKEN
TWILIO_NUMBER = configSettings.TWILIO_NUMBER

# Set the global values for logging
DEBUG = configSettings.DEBUG
DEBUGDETAIL = configSettings.DEBUGDETAIL

# These values provide the email settings
EMAIL_SMTP = configSettings.EMAIL_SMTP
EMAIL_SEND_ACCT = configSettings.EMAIL_SEND_ACCT
EMAIL_PWD = configSettings.EMAIL_PWD
EMAIL_FROM = configSettings.EMAIL_FROM

#SirenDetails
SIREN_PIN = configSettings.SIREN_PIN

# ########################################################################################## #
#  Setup logging #

LOG_FILENAME = "/tmp/SecuritySystem.log"
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"

# Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
# Give the logger a unique name (good practice)
logger = logging.getLogger(__name__)
# Set the log level to LOG_LEVEL
logger.setLevel(LOG_LEVEL)
# Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
# Format each log message like this
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
# Attach the formatter to the handler
handler.setFormatter(formatter)
# Attach the handler to the logger
logger.addHandler(handler)

# Make a class we can use to capture stdout and sterr in the log
class MyLogger(object):
        def __init__(self, logger, level):
                """Needs a logger and a logger level."""
                self.logger = logger
                self.level = level

        def write(self, message):
                # Only log if there is a message (not just a new line)
                if message.rstrip() != "":
                        self.logger.log(self.level, message.rstrip())

# Replace stdout with logging to file at INFO level
sys.stdout = MyLogger(logger, logging.INFO)
# Replace stderr with logging to file at ERROR level
sys.stderr = MyLogger(logger, logging.ERROR)

# ########################################################################################## #
#  Class Definitions #

class SystemState:
	def __init__(self, area, active, start_date, app_mod_id, override, active_schedule, deactivate_override, override_alert_rule, general_alert_rule):
		self.area = area
		self.active = active
		self.app_mod_id = app_mod_id
		self.active_override = override
		self.override_alert_rule = override_alert_rule
		self.general_alert_rule = general_alert_rule
		self.active_schedule = active_schedule
		self.deactivate_override = deactivate_override
		self.startup_date = start_date

class Users:
	def __init__(self, user_id, user_name, sms_number, send_email, send_sms):
		self.id = user_id
		self.name = user_name
		self.sms_number = sms_number
		self.send_email = send_email
		self.send_sms = send_sms

class SecurityRule:
	def __init__(self, rule_name, pin_id, sms_message, current_state, check_count, app_mod_id):
		self.name = rule_name
		self.pin = pin_id
		self.message = sms_message
		self.state = current_state
		self.checkcount = check_count
		self.app_mod_id = app_mod_id

class SecuritySchedule:
	def __init__(self, start_day, start_hour, start_minute, end_day, end_hour, end_minute, alert_rule_id, active, update_date, schedule_id, app_mod_id):
		self.startday = start_day
		self.starthour = start_hour
		self.startminute = start_minute
		self.endday = end_day
		self.endhour = end_hour
		self.endminute = end_minute
		self.alertrule = alert_rule_id
		self.active = active
		self.updatedate = update_date
		self.id = schedule_id
		self.app_mod_id = app_mod_id

class StatusChanges:
	def __init__(self, pin_id, last_state):
		self.pin_id = pin_id
		self.last_state = last_state

class ScheduleState:
	def __init__(self, app_mod_id, state, active_schedule_id):
		self.app_mod_id = app_mod_id
		self.state = state
		self.active_schedule_id = active_schedule_id

class AlertRules:
	def __init__(self, rule_id, rule_name, send_email, send_sms, send_siren, alert_start, alert_end, active):
		self.id = rule_id
		self.rule_name = rule_name
		self.send_email = send_email
		self.send_sms = send_sms
		self.send_siren = send_siren
		self.alert_start = alert_start
		self.alert_end = alert_end
		self.active = active

class ArmedStatus:
	def __init__(self, armed, active_schedule, alert_rule):
		self.armed = armed
		self.active_schedule = active_schedule
		self.alert_rule = alert_rule

class ArmedState:
	def __init__(self, app_id, arm_state, arm_type, active_schedule, alert_id):
		self.app_id = app_id
		self.arm_state = arm_state
		self.arm_type = arm_type
		self.active_schedule = active_schedule
		self.alert_id = alert_id

class AlertActions:
	def __init__(self, app_mod_id, pin_id, pin_state, pin_state_previous, alert_actions_count, exception_event, exception_event_type, exception_event_type_id, start_event_date, end_event_date, action_date_time):
		self.app_mod_id = app_mod_id
		self.pin_id = pin_id
		self.pin_state = pin_state
		self.pin_state_previous = pin_state_previous
		self.alert_actions_count = alert_actions_count
		self.exception_event = exception_event
		self.exception_event_type = exception_event_type
		self.exception_event_type_id = exception_event_type_id
		self.start_event_date = start_event_date
		self.end_event_date = end_event_date
		self.action_date_time = action_date_time


# ########################################################################################## #
#  Functions and Methods #

def getDataResultSet(sql):
	global HOST_NAME
	global DB_USER
	global DB_PASSWORD
	global DB_DATABASE

	# Open database connection
	db = MySQLdb.connect(HOST_NAME, DB_USER, DB_PASSWORD, DB_DATABASE)

	# prepare a cursor object using cursor() method
	cursor = db.cursor()

	# Prepare SQL query to INSERT a record into the database.
	try:
		# Execute the SQL command
		cursor.execute(sql)
		# Fetch all the rows in a list of lists.
		results = cursor.fetchall()

	except Exception as e:
		logMessage("method: getDataResultSet - Error occurred: " + str(e.__doc__) + ": " + str(e.message))

	# disconnect from server
	db.close()

	return results   


def executeSQL(sql):
	global HOST_NAME
	global DB_USER
	global DB_PASSWORD
	global DB_DATABASE

	returnStatus = 0

	# Open database connection
	db = MySQLdb.connect(HOST_NAME, DB_USER, DB_PASSWORD, DB_DATABASE)

	# prepare a cursor object using cursor() method
	cursor = db.cursor()

	# Prepare SQL query to INSERT a record into the database.
	try:
		# Execute the SQL command
		cursor.execute(sql)
		# Commit your changes in the database
   		db.commit()
		returnStatus = 1

	except Exception as e:
		# Rollback in case there is any error
		db.rollback()
		logMessage("method: executeSQL - Error occurred: " + str(e.__doc__) + ": " + str(e.message) + ".  Trying to execute: " + str(sql))

	# disconnect from server
	db.close()

	return returnStatus


def setCurrentStateDB(pin_id, state):
	returnStatus = 0
	sql = "UPDATE current_state SET state = " + `state` + " WHERE pin_id = " + str(pin_id)
	if (DEBUGDETAIL): logMessage("method: setCurrentStateDB - Update current state - setCurrentStateDB - SQL: " + `sql`)
	try:
		if (executeSQL(sql)):
			returnStatus = 1
	except:
		if (DEBUG): logMessage("method: setCurrentStateDB - Error occurred while trying to update state for pin_id: " + str(pin_id))

	return returnStatus


def updateOverride(app_mod_id):
	returnStatus = 0
	sql = "UPDATE system_state SET active_override = 0, deactivate_override = 0 WHERE id = " + str(app_mod_id) + " and active_override <> 1"
	if (DEBUGDETAIL): logMessage("method: updateOverride - Update override state - updateOverride - SQL: " + `sql`)
	try:
		if (executeSQL(sql)):
			returnStatus = 1
	except:
		if (DEBUG): logMessage("method: updateOverride - Error occurred while trying to update override state for app_mod_id: " + str(app_mod_id))

	return returnStatus


def updateActiveSchedule(app_mod_id, active_schedule, state):
	returnStatus = 0
	outputState = 0

	if (state > 0):
		outputState = active_schedule

	sql = "UPDATE system_state SET active_schedule = " + str(outputState) + ", deactivate_override = 0, last_change_date = now() WHERE id = " + str(app_mod_id)
	if (DEBUGDETAIL): logMessage("method: updateActiveSchedule - Update active Schedule - updateActiveSchedule - SQL: " + `sql`)
	try:
		if (executeSQL(sql)):
			returnStatus = 1
	except Exception as e:
		logMessage("method: updateActiveSchedule - Error occurred: " + str(e.__doc__) + ": " + str(e.message))

	return returnStatus


def loadSchedules():
	outputRules = []
	
	# Prepare SQL query to get values from the db
	sql = "SELECT start_day, start_hour, start_minute, end_day, end_hour, end_minute, alert_rule_id, active, last_change_date, id, app_module_id FROM security_schedules WHERE active = 1 and deleted <> 1 ORDER BY start_day, start_hour"
	try:
		results = getDataResultSet(sql)

		for row in results:
			# Create new class objects from results
			outputRules.append(SecuritySchedule(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]))
			#print "start_day=%d, start_hour=%d, start_minute=%d, end_day=%d, end_hour=%d, end_minute=%d" % (row[0], row[1], row[2], row[3], row[4], row[5])

	except Exception as e:
		logMessage("method: loadSchedules - Error occurred: " + str(e.__doc__) + ": " + str(e.message))

	return outputRules   


# Load System State
def loadSystemState():
	outputState = []

	# Prepare SQL query to INSERT a record into the database.
	sql = "SELECT app_module, active, last_change_date, id, active_override, active_schedule, deactivate_override, override_alert_rule, general_alert_rule FROM system_state WHERE active = 1"
	try:
		results = getDataResultSet(sql)

		for row in results:
			# Create new class objects from results
			outputState.append(SystemState(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))

	except Exception as e:
		logMessage("method: loadSystemState - Error occurred: " + str(e.__doc__) + ": " + str(e.message))

	return outputState


# Load all the users
def loadUsers():
	outputUsers = []

	# Prepare SQL query to INSERT a record into the database.
	sql = "SELECT id, user_name, sms_number, send_email, send_sms FROM users WHERE active = 1 and deleted <> 1"
	try:
		results = getDataResultSet(sql)

		for row in results:
			# Create new class objects from results
			outputUsers.append(Users(row[0], row[1], row[2], row[3], row[4]))
	except Exception as e:
		logMessage("method: loadUsers - Error occurred: " + str(e.__doc__) + ": " + str(e.message))

	return outputUsers


def loadMonitorRules():
	outputRules = []

	# Prepare SQL query to INSERT a record into the database.
	sql = "SELECT module_name, pin_id, message, app_module_id FROM security_modules WHERE active = 1"
	try:
		results = getDataResultSet(sql)

		for row in results:
			# Create new class objects from results
			outputRules.append(SecurityRule(row[0], row[1], row[2], 0, 0, row[3]))

	except Exception as e:
		logMessage("method: loadMonitorRules - Error occurred: " + str(e.__doc__) + ": " + str(e.message))

	return outputRules


def loadAlertRules():
	outputRules = []

	# Prepare SQL query to INSERT a record into the database.
	sql = "SELECT id, rule_name, send_email, send_sms, send_siren, alert_start, alert_end, active FROM alert_rules WHERE active = 1"
	try:
		results = getDataResultSet(sql)

		for row in results:
			# Create new class objects from results
			outputRules.append(AlertRules(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

	except Exception as e:
		logMessage("method: loadAlertRules - Error occurred: " + str(e.__doc__) + ": " + str(e.message))

	return outputRules


def insertEventLogEntry(logEvent, eventDateTime):

	# Check to log entries from configuration settings
	returnStatus = 0
	if (LOG_ENTRIES):

		# determine if log all entries
		logEventDB = 0
		if (LOG_ENTRIES_EXCEPTION_ONLY):
			if (DEBUGDETAIL): logMessage("method: insertEventLogEntry - Log only exceptions enabled")
			# Check to see if it was an exception
			if (logEvent.exception_event):
				logEventDB = 1
		else:
			logEventDB = 1

		if (logEventDB):
			sql = "INSERT into incident_logs (app_module_id, pin_id, alert_actions_count, exception_event, \
					exception_event_type, exception_event_type_id, start_event_date, end_event_date) \
					VALUES ('%d', '%d', '%d', '%d', '%s', '%d', '%s', '%s' )" % \
					(logEvent.app_mod_id, logEvent.pin_id, logEvent.alert_actions_count, logEvent.exception_event, 
						logEvent.exception_event_type, logEvent.exception_event_type_id, logEvent.start_event_date, 
						logEvent.end_event_date)


			if (DEBUGDETAIL): logMessage("method: insertEventLogEntry - Insert log entry event - SQL: " + `sql`)
			try:
				if (executeSQL(sql)):
					returnStatus = 1
			
			except Exception as e:
				logMessage("method: insertEventLogEntry - Error occurred: " + str(e.__doc__) + ": " + str(e.message) + " - SQL: " + str(sql))
	else:
		if (DEBUGDETAIL): logMessage("method: insertEventLogEntry - Log entries to DB is NOT enableddisa")
	
	return returnStatus


#set the current state of monitoring rules
def updateCurrentRuleState():
	global monitorRules
	for i in range(len(monitorRules)):
		if (DEBUGDETAIL): logMessage("method: updateCurrentRuleState - Previous State for pin %d is %d" % (monitorRules[i].pin, monitorRules[i].state))
		monitorRules[i].state = io.input(monitorRules[i].pin)
		if (DEBUGDETAIL): logMessage("method: updateCurrentRuleState - Previous State for pin %d is %d" % (monitorRules[i].pin, monitorRules[i].state))


# Function send message
def sendSMS(message_string, username, sms_number):
	#global userList
	global ACCOUNT_SID 
	global AUTH_TOKEN
	global TWILIO_NUMBER

	try:
		#import the library to send the message
		from twilio.rest import TwilioRestClient
	 
		client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

		# Loop through users and send messages
		#for i in range(len(userList)):
		message = client.messages.create(to=str(sms_number), from_=TWILIO_NUMBER, body=message_string)
		time.sleep(1.5)

		if (DEBUG): logMessage("method: sendSMS - SMS message sent to " + `username` + " at " + `sms_number` + ": " + message_string)
	except Exception as e:
		logMessage("method: sendSMS - Error occurred: " + str(e.__doc__) + ": " + str(e.message) + ".  Trying to send: " + str(message_string))
	


def sendEmail(message_string, to_addr):
	global EMAIL_SEND_ACCT
	global EMAIL_SMTP
	global EMAIL_PWD
	global EMAIL_FROM

	# First create the email body
	msg = "\r\n".join(["From: Bunker Home Security System","To: " + str(to_addr), "Subject: Security System Message","",message_string])

	try:
		server = smtplib.SMTP(EMAIL_SMTP)
		server.ehlo()
		server.starttls()
		server.login(EMAIL_SEND_ACCT,EMAIL_PWD)
		server.sendmail(EMAIL_FROM, to_addr, msg)
		server.quit()

		if (DEBUG): logMessage("method: sendEmail - Email message sent to " + str(to_addr) + " message: " + message_string)
	except Exception as e:
		logMessage("method: sendEmail - Error occurred: " + str(e.__doc__) + ": " + str(e.message) + ".  Trying to send: " + str(msg))


def soundSiren():
	# launch the siren pin
	if (DEBUG): logMessage("method: soundSiren - sounding siren ")
	try:
		io.output(SIREN_PIN, io.LOW)
		time.sleep(2)
		io.output(SIREN_PIN, io.HIGH)
		time.sleep(1)
		io.output(SIREN_PIN, io.LOW)
		time.sleep(2)
		io.output(SIREN_PIN, io.HIGH)
		time.sleep(1)
		io.output(SIREN_PIN, io.LOW)
		time.sleep(2)
		io.output(SIREN_PIN, io.HIGH)
	except Exception as e:
		logMessage("method: soundSiren - Error occurred: " + str(e.__doc__) + ": " + str(e.message))



# This function will check if a schedule should fire
def activeSchedule(checkDate, app_mod_id):
	global schedules
	global DAY_OF_WEEK_OFFSET

	returnCheck = 0

	# Set the current date and time values
	checkYear = checkDate.year
	checkMonth = checkDate.month  
	checkDay = checkDate.day  
	checkDayofWeek = checkDate.weekday()

	if (checkDayofWeek == 6):
		checkDayofWeek = 0
	else:
		checkDayofWeek += DAY_OF_WEEK_OFFSET

	if (DEBUGDETAIL): logMessage("method: activeSchedule - Day of week value being evaluated: " + str(checkDayofWeek))

	for i in range(len(schedules)):

		# Only run this code if the mod id is the same as the schedule
		if (schedules[i].app_mod_id == app_mod_id):
			needs_evaluation = 0
		
			if (checkDayofWeek == 0):
				if (schedules[i].startday == 0 or schedules[i].startday == 6):
					if (schedules[i].startday == 0):
						validateStart = getScheduleDateTime(checkDate, schedules[i], "current", 1)
						needs_evaluation = 1
						if (schedules[i].endday == schedules[i].startday):
							validateEnd = getScheduleDateTime(checkDate, schedules[i], "current", 0)
						else:
							validateEnd = getScheduleDateTime(checkDate, schedules[i], "future", 0)
					else:
						validateStart = getScheduleDateTime(checkDate, schedules[i], "past", 1)
						needs_evaluation = 1
						if (schedules[i].endday == schedules[i].startday):
							validateEnd = getScheduleDateTime(checkDate, schedules[i], "past", 0)
						else:
							validateEnd = getScheduleDateTime(checkDate, schedules[i], "current", 0)

			elif (checkDayofWeek-1 == schedules[i].startday or checkDayofWeek == schedules[i].startday):
				if (checkDayofWeek-1 == schedules[i].startday):
					validateStart = getScheduleDateTime(checkDate, schedules[i], "past", 1)
					needs_evaluation = 1
					if (schedules[i].endday == schedules[i].startday):
						validateEnd = getScheduleDateTime(checkDate, schedules[i], "past", 0)
					else:
						validateEnd = getScheduleDateTime(checkDate, schedules[i], "current", 0)
				else:
					validateStart = getScheduleDateTime(checkDate, schedules[i], "current", 1)
					needs_evaluation = 1
					if (schedules[i].endday == schedules[i].startday):
						validateEnd = getScheduleDateTime(checkDate, schedules[i], "current", 0)
					else:
						validateEnd = getScheduleDateTime(checkDate, schedules[i], "future", 0)

			if (needs_evaluation):

				if (DEBUGDETAIL): logMessage("method: activeSchedule - Schedule being evaluated: - ID: " + str(schedules[i].id))
				if (DEBUGDETAIL): logMessage("method: activeSchedule - Checking the date schedules: value of checkDate: " + `checkDate.strftime("%B %d, %Y %H:%M")`)
				if (DEBUGDETAIL): logMessage("method: activeSchedule - validateStart date value: " + `validateStart.strftime("%B %d, %Y %H:%M")`)
				if (DEBUGDETAIL): logMessage("method: activeSchedule - validateEnd date value: " + `validateEnd.strftime("%B %d, %Y %H:%M")`)

				if (validateStart <= checkDate and validateEnd >= checkDate):
					returnCheck = schedules[i].id
					if (DEBUG): logMessage("method: activeSchedule - Active schedule has been found and confirmed: " + str(schedules[i].id))
					break

	return returnCheck


def getScheduleDateTime(currentDate, checkSchedule, Datetype, start):
	
	returnDate = currentDate

	if (Datetype == "past"):
		PreviousDate = currentDate
		PreviousDate -= datetime.timedelta(days=1)

		if (start):
			returnDate = datetime.datetime(PreviousDate.year, PreviousDate.month, PreviousDate.day, checkSchedule.starthour, checkSchedule.startminute, 0, 0)
		else:
			returnDate = datetime.datetime(PreviousDate.year, PreviousDate.month, PreviousDate.day, checkSchedule.endhour, checkSchedule.endminute, 0, 0)

	elif (Datetype == "future"):
		NextDate = currentDate
		NextDate += datetime.timedelta(days=1)

		if (start):
			returnDate = datetime.datetime(NextDate.year, NextDate.month, NextDate.day, checkSchedule.starthour, checkSchedule.startminute, 0, 0)
		else:
			returnDate = datetime.datetime(NextDate.year, NextDate.month, NextDate.day, checkSchedule.endhour, checkSchedule.endminute, 0, 0)

	elif (Datetype == "current"):
		if (start):
			returnDate = datetime.datetime(currentDate.year, currentDate.month, currentDate.day, checkSchedule.starthour, checkSchedule.startminute, 0, 0)
		else:
			returnDate = datetime.datetime(currentDate.year, currentDate.month, currentDate.day, checkSchedule.endhour, checkSchedule.endminute, 0, 0)

	return returnDate

	# First check to see if the state is already set

def getCurrentDate():
	global TIME_ZONE_OFFSET
	mydate = datetime.datetime.utcnow()
	mydate -= datetime.timedelta(hours=TIME_ZONE_OFFSET)
	return mydate


def armedStatus(checkDate, app_mod_id, monitorState):
	returnValue = 0
	returnSchedule = 0
	returnAlert = 0
	outputResult = []

	if (monitorState.active_override == 1):
		# This means that we are armed with no override
		returnValue = 1
		returnAlert = monitorState.override_alert_rule
		if (DEBUG): logMessage("method: armedStatus - Override state means active armed system.  Alert rule: " + str(returnAlert))
	else:
		# If the deactivate flag is set then return not armed
		if (monitorState.deactivate_override == 0):

			if (monitorState.active_override > 0):
				returnValue = 1
				if (DEBUG): logMessage("method: armedStatus - Override state has been set for app_mod_id: " + str(app_mod_id))
				returnAlert = monitorState.override_alert_rule

			if (monitorState.active_override == 0):  # This means there is not override on the armed status
				# Check to see if an active schedule exists
				checkvalue = activeSchedule(checkDate, app_mod_id)

				# Evaluate the active schedules to return status
				if (checkvalue > 0):
					returnSchedule = checkvalue
					returnAlert = getAlertRule(returnSchedule)
					returnValue = 1

	outputResult.append(ArmedStatus(returnValue, returnSchedule, returnAlert))

	return outputResult


def getAlertRule(schedule_id):
	global schedules
	returnValue = 0

	if (DEBUG): logMessage("method: getAlertRule - Get Alert Rule from Schedule ID: " + str(schedule_id))
	for i in range(len(schedules)):
		if (schedules[i].id == schedule_id):
			returnValue = schedules[i].alertrule

	return returnValue


def getCurrentArmedState(checkDate, monitorStates):
	returnOutput = []

	for x in range(len(monitorStates)):
		if (monitorStates[x].active == 1):
			armState = armedStatus(checkDate, monitorStates[x].app_mod_id, monitorStates[x])
			# Need to determine Arm Type
			armType = ""
			if (armState[0].active_schedule == 0):
				armType = "override"
			elif (armState[0].active_schedule > 0):
				armType = "schedule"

			returnOutput.append(ArmedState(monitorStates[x].app_mod_id, armState[0].armed, armType, armState[0].active_schedule, armState[0].alert_rule))

	return returnOutput


def reloadSystemState(checkDate):
	global monitorState
	global monitorRules
	global schedules
	global userList
	global armedState

	if (DEBUG): logMessage("method: reloadSystemState - Reloading System State: " + `checkDate.strftime("%B %d, %Y %H:%M:%S.%f")`)

	#print("Reloading monitorState...")
	monitorState = loadSystemState()
	#print("Reloading schedules...")
	schedules = loadSchedules()
	#print("Reloading users...")
	userList = loadUsers()

	# Now check to see if the armed status has changed for all App IDs

	current = getCurrentArmedState(checkDate, monitorState)

	for i in range(len(current)):
		for n in range(len(armedState)):
			if (current[i].app_id == armedState[n].app_id):

				if (current[i].arm_state != armedState[n].arm_state):
					#Determine App Name
					appName = ""
					generalAlertRule = 0
					if (len(monitorState) > 1):
						for o in range(len(monitorState)):
							if (monitorState[o].app_mod_id == current[i].app_id):
								appName = "  For app - " + str(monitorState[o].area) + ". "
								generalAlertRule = monitorState[o].general_alert_rule
					# Alert users to the changes in armed state
					if (current[i].arm_state):
						outMessage = "Security System is now ARMED!" + appName + " Start time: " + `checkDate.strftime("%B %d, %Y %H:%M")`
					else:
						outMessage = "Security System has been disarmed." + appName + " Disarm time: " + `checkDate.strftime("%B %d, %Y %H:%M")`
					sendAlertMessage(outMessage, generalAlertRule)
					# Set the current armed state
					armedState[n] = current[i]
					if (DEBUG): logMessage("method: reloadSystemState - Armed status has changed.  Current Status: " + str(armedState[n].arm_state))

	# Check if active schedule has changed
	returnValue = checkScheduleStates(checkDate, monitorState)


def checkScheduleStates(checkDate, monitorStates):
	global scheduleState
	current_state = 0
	schedule_id = 0
	status_change = 0

	for i in range(len(monitorStates)):
		schedule_id = activeSchedule(checkDate, monitorStates[i].app_mod_id)
		if (schedule_id > 0):
			if (DEBUG): logMessage("method: checkScheduleStates - Active schedule found:  " + str(schedule_id))
			current_state = 1

		#check if status has changed

		for x in range(len(scheduleState)):
			if (monitorStates[i].app_mod_id == scheduleState[x].app_mod_id):
				if (scheduleState[x].state != current_state):
					# Update the schedule state
					scheduleState[x].state = current_state

					# Update the DB state table with the latest active schedule
					updateActiveSchedule(monitorStates[i].app_mod_id, schedule_id, current_state)
					# Update the overrides
					updateOverride(monitorStates[i].app_mod_id)

					# Remove the temporary override - if applicable
					if (monitorStates[i].active_override == 2):
						# Send update to db to remove override
						if (updateOverride(monitorStates[i].app_mod_id) == 0):
							if (DEBUG): logMessage("method: checkScheduleStates - Removal of Temporary System Override did NOT succeed:  " + str(monitorStates[i].app_mod_id))
					status_change = 1 

	return status_change


def sendAlertMessage(outMessage, alert_rule):
	global alertRules
	global userList

	if (DEBUG): logMessage("method: sendAlertMessage - Sending alert for rule id:  " + str(alert_rule) + ".  OutMessage: " + str(outMessage))

	# First, get find the alert rule details
	if (alert_rule):
		for i in range(len(alertRules)):
			if (alertRules[i].id == alert_rule):
				# This rule is now applied to notifications to users
				# First sound Siren

				try:
					if (alertRules[i].send_siren):		
						soundSiren()
				except Exception as e:
					logMessage("method: sendAlertMessage - soundSiren - Error occurred: " + str(e.__doc__) + ": " + str(e.message))

				try:
					if (alertRules[i].send_email):
						for i in range(len(userList)):	
							if (userList[i].send_email):
								sendEmail(outMessage, userList[i].name)
				except Exception as e:
					logMessage("method: sendAlertMessage - sendEmail - Error occurred: " + str(e.__doc__) + ": " + str(e.message))

					
				try:
					if (alertRules[i].send_sms):
						for i in range(len(userList)):
							if (userList[i].send_sms):
								sendSMS(outMessage, userList[i].name, userList[i].sms_number)
				except Exception as e:
					logMessage("method: sendAlertMessage - sendSMS - Error occurred: " + str(e.__doc__) + ": " + str(e.message))

				break


def setScheduleState(checkDate, monitorStates):
	outputState = []
	current_state = 0
	schedule_id = 0

	for i in range(len(monitorStates)):
		# Check for active Schedules
		schedule_id = activeSchedule(checkDate, monitorStates[i].app_mod_id)
		if (schedule_id > 0):
			if (DEBUG): logMessage("method: setScheduleState - Active schedule found:  " + str(schedule_id))
			current_state = 1
			updateActiveSchedule(monitorStates[i].app_mod_id, schedule_id, current_state)
		else:
			# Update the db with a zero state status
			updateActiveSchedule(monitorStates[i].app_mod_id, 0, 0)

		if (DEBUG): logMessage("method: setScheduleState - Schedule State: System State id:  " + str(monitorStates[i].app_mod_id) + " with status: " + str(current_state))
		# Set values for this state
		outputState.append(ScheduleState(monitorStates[i].app_mod_id, current_state, schedule_id))

	return outputState

	
def loadStatusChanges(securityRules, inputDateTime):
	global alertActions

	outputRules = []

	for i in range(len(securityRules)):
		pin_status = io.input(securityRules[i].pin)
		outputRules.append(StatusChanges(securityRules[i].pin, pin_status))

		# If the pin_status is open, add the pin item to the alertActions
		if (pin_status):
			if (DEBUGDETAIL): logMessage("method: loadStatusChanges - add to alertActions for open pin: " + str(securityRules[i].pin))
			alertActions.append(AlertActions(securityRules[i].app_mod_id, securityRules[i].pin, pin_status, pin_status, 0, 0, "", 0, inputDateTime, "", inputDateTime))

		# Update the db with the current status of each pin
		if (setCurrentStateDB(securityRules[i].pin, pin_status)):
			if (DEBUGDETAIL): logMessage("method: loadStatusChanges - Initial Load - Pin status updated successfully to DB. pin_id: " + str(securityRules[i].pin) + " with status: " + str(pin_status))
		else:
			if (DEBUG): logMessage("method: loadStatusChanges - Initial Load - Update DB Status Failed for pin: " + str(securityRules[i].pin) + " with status: " + str(pin_status))
		
	return outputRules


def confirmStatusChange(inputStatus):

	returnValue = 0

	for i in range(len(inputStatus)):
		status = io.input(inputStatus[i].pin_id)
		if (inputStatus[i].last_state != status):
			inputStatus[i].last_state = status
			returnValue = 1
			# Update the DB with the status changes
			if (setCurrentStateDB(inputStatus[i].pin_id, status)):
				if (DEBUGDETAIL): logMessage("method: confirmStatusChange - Pin status updated successfully to DB. pin_id: " + str(inputStatus[i].pin_id) + " with status: " + str(status))
			else:
				if (DEBUG): logMessage("method: confirmStatusChange - Update DB Status Failed for pin: " + str(inputStatus[i].pin_id) + " with status: " + str(status))

	return returnValue


def logMessage(message):
	# logtime = getCurrentDate()
	# print("Log message: " + `logtime.strftime("%B %d, %Y %H:%M:%S.%f")` + "  -  " + message)
	print(message)

def setupGPIO():
	global monitorRules

	try:
		# Setup pins for monitoring rules and schedules
		for i in range(len(monitorRules)):
			io.setup(int(monitorRules[i].pin), io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
		
		# Setup pin for siren
		io.setup(int(SIREN_PIN), io.OUT)
		io.output(int(SIREN_PIN), io.HIGH)
	except Exception as e:
		logMessage("method: setupGPIO - Error occurred: " + str(e.__doc__) + ": " + str(e.message))


def alertActionExists(pin_id):
	alertExists = False
	global alertActions

	for i in range(len(alertActions)):
		if alertActions[i].pin_id == pin_id:
			alertExists = True

	return alertExists


def removeAlertAction(pin_id, log_date):
	global alertActions

	actionExists = 0
	removeActionID = 0

	if (DEBUG): logMessage("method: removeAlertAction - Action to be removed: " + str(pin_id))
	if (DEBUG): logMessage("method: removeAlertAction - alertActions count: " + str(len(alertActions)))

	# First find the alert action that needs to be logged and removed
	for i in range(len(alertActions)):
		if (alertActions[i].pin_id == pin_id):
			# Log the action
			alertActions[i].end_event_date = log_date
			insertEventLogEntry(alertActions[i], log_date)
			# Remove the action item
			actionExists = 1
			removeActionID = i

	if (actionExists):
		alertActions.pop(removeActionID)


def getAlertMessage(pin_id):
	global monitorRules

	returnMessage = ""

	for i in range(len(monitorRules)):
		if (monitorRules[i].pin == pin_id):
			returnMessage = monitorRules[i].message

	return returnMessage


def processAlertActions(processAlertDateTime):
	global alertActions
	global monitorState

	# Instructions for sending alerts to users
	# 1. First, only send alerts after a 60 second delay from the time of arming
	# 2. Send alerts 5 times in an interval of 5 minutes each and then stop sending
	# 3. Only send alerts if the system is armed

	currentArmedState = getCurrentArmedState(processAlertDateTime, monitorState)

	# If no armed state then skip the evaluation of each alert
	isarmed = False
	if (currentArmedState):
		for n in range(len(currentArmedState)):
			if (currentArmedState[n].arm_state):
				isarmed = True

	if (isarmed):
		# Loop through each alertAction and determine action to be taken
		if (DEBUGDETAIL): logMessage("method: processAlertActions - Number of alertActions: " + str(len(alertActions)))
		for i in range(len(alertActions)):

			sendAlert = False

			# Is the app_mod_id in an armed state
			appIsArmed = False
			alertID = 0
			for x in range(len(currentArmedState)):
				if (DEBUGDETAIL): logMessage("method: processAlertActions - Armed State - ID: " + str(currentArmedState[x].app_id))
				if (alertActions[i].app_mod_id == currentArmedState[x].app_id):
					if (currentArmedState[x].arm_state):
						appIsArmed = True
						alertID = currentArmedState[x].alert_id
						alertActions[i].exception_event = 1
						alertActions[i].exception_event_type = currentArmedState[x].arm_type
						alertActions[i].exception_event_type_id = currentArmedState[x].active_schedule

						# Setting Alert Values
						if (DEBUGDETAIL): logMessage("method: processAlertActions - Set Armed Values.  alertID: " + str(currentArmedState[x].alert_id) + ", AppID: " + str(currentArmedState[x].app_id))


			if (DEBUGDETAIL): logMessage("method: processAlertActions - appIsArmed: " + str(appIsArmed))

			# Is this the first time for this alert
			if (appIsArmed and alertActions[i].alert_actions_count == 0):
				sendAlert = True

			if (DEBUGDETAIL): logMessage("method: processAlertActions - alertActions[i].alert_actions_count: " + str(alertActions[i].alert_actions_count))

			# Check to see if we have exceeded the number of sent messages for this Alert
			if (appIsArmed and alertActions[i].alert_actions_count < MAX_ALERT_SEND_COUNT):
				# Is the timing sufficient to resend alert
				if (DEBUGDETAIL): logMessage("method: processAlertActions - total seconds since last send: " + str((processAlertDateTime-alertActions[i].action_date_time).total_seconds()))
				if ((processAlertDateTime-alertActions[i].action_date_time).total_seconds() > MAX_ALERT_SEND_INTERVAL):
					sendAlert = True
			elif (appIsArmed and alertActions[i].alert_actions_count == MAX_ALERT_SEND_COUNT):
				# Log the change
				logMessage("method: processAlertActions - AlertAction has exceeded the maximum notifications: alertActions[i].pin_id: " + str(alertActions[i].pin_id))

			if (DEBUGDETAIL): logMessage("method: processAlertActions - sendAlert: " + str(sendAlert))

			# Send alert
			if (sendAlert):
				sendMessage = getAlertMessage(alertActions[i].pin_id)
				if (DEBUGDETAIL): logMessage("method: processAlertActions - sendMessage being sent for pin: " + str(alertActions[i].pin_id))

				if (alertActions[i].alert_actions_count > 0):
					# Append to the send message the number of times being sent:
					sendMessage += " - duplicate message (" + str(alertActions[i].alert_actions_count) + ")"

				# Log the alert
				logMessage("method: processAlertActions - Triggered Alert! Message: " + str(sendMessage) + ", Pin_id: " + str(alertActions[i].pin_id))

				sendAlertMessage(sendMessage, alertID)
				# Update the counter for the number of alerts sent for this AlertAction
				alertActions[i].alert_actions_count += 1
				# Update action_date_time to identify when the last action took place
				alertActions[i].action_date_time = processAlertDateTime


# ########################################################################################## #
#  Initialize values #

#Set the starting DateTime for the script execution
prev_datetime = getCurrentDate()
#Set the Alert Evaluation Date&Time
last_alert_action_datetime = prev_datetime

logMessage("Initial Load: Startup Date and Time: " + `prev_datetime.strftime("%B %d, %Y %H:%M:%S.%f")`)
prev_checkup = prev_datetime

if (DEBUG): logMessage("Initial Load: Beginning the loading of system values")

# Get the current state from the DB
monitorState = loadSystemState()
# Get the current schedules to follow
schedules = loadSchedules()
# Get the list of users to notify 
userList = loadUsers()
# Get the rules to be applied 
monitorRules = loadMonitorRules()
# Get the initial list of Alert Rules
alertRules = loadAlertRules()
# Create the empty array for AlertActions
alertActions = []

# Get the statup Armed Status
armedState = getCurrentArmedState(prev_datetime, monitorState)

#Log current status of armed state
initialArmedState = False
for a in range(len(armedState)):
	if (armedState[a].arm_state):
		logMessage("Initial Load: System is ARMED!  App ID: " + str(armedState[a].app_id))
		initialArmedState = True
if not (initialArmedState):
	logMessage("Initial Load: The System is NOT armed at initial loading")

# Get Active Schedule status
scheduleState = setScheduleState(prev_datetime, monitorState)
if (initialArmedState):
	for b in range(len(scheduleState)):
		# def __init__(self, app_mod_id, state, active_schedule_id):
		if (scheduleState[b].state):
			logMessage("Initial Load: The following schedule is currently active: " + str(scheduleState[b].active_schedule_id) + " for app id: " + str(scheduleState[b].app_mod_id))

# Now setup the inputs to monitor
setupGPIO()

updateCurrentRuleState()

# Now set the base state of the pin values
statusChecker = loadStatusChanges(monitorRules, prev_datetime)

# ########################################################################################## #

try: 
	while True:
		currentDateTime = getCurrentDate()

		# Let's check to see if the status has changes from the last loop
		if (confirmStatusChange(statusChecker)):
			if (DEBUGDETAIL): logMessage("method: Reoccuring Loop - Status has changed for monitored GPIO pins.  Beginning evaluation.")

			for x in range(len(monitorState)):

				#First check for an active Monitoring State
				if (monitorState[x].active == 1):

					# Loop through all the rules to evaluate
					for n in range(len(monitorRules)):
						# If any of the rules have been triggered then perform the following

						if (monitorRules[n].app_mod_id == monitorState[x].app_mod_id):

							checkstatus = 0
							checkstatus = io.input(monitorRules[n].pin)
							if (checkstatus):
								# The rule has been triggered - Has the state changed?

								# Add to the array of AlertActions...first check to see if it's already there
								if not (alertActionExists(monitorRules[n].pin)):
									alertActions.append(AlertActions(monitorRules[n].app_mod_id, monitorRules[n].pin, checkstatus, monitorRules[n].state, 0, 0, "", 0, currentDateTime, "", currentDateTime))

								#update state
								monitorRules[n].state = checkstatus	

							else:
								# Validate if the state is different and set it back to base state
								if (monitorRules[n].state == 1):
									monitorRules[n].state = checkstatus
									monitorRules[n].checkcount = 0

									# Remove from alertActions array
									removeAlertAction(monitorRules[n].pin, currentDateTime)

									if (DEBUG): logMessage("method: Reocurring Loop - State has changed for " + `monitorRules[n].name` + ". Setting state to closed")
							
							#Process the Alert Actions
							if (alertActions):
								processAlertActions(currentDateTime)
								last_alert_action_datetime = currentDateTime

		else:
			# Check AlertActions on interval (EVAL_ALERT_ACTION_INTERVAL)
			if (alertActions):
				if ((currentDateTime-last_alert_action_datetime).total_seconds() > EVAL_ALERT_ACTION_INTERVAL):
					if (DEBUGDETAIL): logMessage("method: Reocurring Loop - Alert Actions exist.  Count: " + str(len(alertActions)))
					processAlertActions(currentDateTime)
					last_alert_action_datetime = currentDateTime

		# Wait for specific timing and loop back for next evaluation
		time.sleep(REOCCURRING_LOOP_TIME)

		# Determine if there is a need to update the system state from the db
		if ((currentDateTime-prev_checkup).total_seconds() > DB_REFRESH_TIME):
			#monitorState = loadSystemState()
			reloadSystemState(currentDateTime)
			prev_checkup = currentDateTime
		
except KeyboardInterrupt:
        if (DEBUG): logMessage("method: Reocurring Loop - KeyboardInterrupt ")
        io.cleanup()

# ########################################################################################## #


