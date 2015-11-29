#!/usr/bin/env python

# ########################################################################################## #
# Define imports

import time
import datetime
import MySQLdb
import configSettings


# ########################################################################################## #
# DB connection details - this will import settings from the configSetting.py file

HOST_NAME = configSettings.HOST_NAME 
DB_USER = configSettings.DB_USER
DB_PASSWORD = configSettings.DB_PASSWORD
DB_DATABASE = configSettings.DB_DATABASE

# ########################################################################################## #
#  Functions and Methods #

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

def updateAdmin(username, sms_number):

	sql = "UPDATE users SET user_name = '" + str(username) + "', sms_number = '" + str(sms_number) + "', last_change_date = now() where id = 1;" 
	
	try:
		logMessage("SQL string to be executed: " + str(sql))
		if (executeSQL(sql)):
			returnStatus = 1
			
	except Exception as e:
		logMessage("Error occurred: " + str(e.__doc__) + ": " + str(e.message) + " - SQL: " + str(sql))

	return returnStatus

def logMessage(message):
	logtime = getCurrentDateTime()
	print("Log message: " + `logtime.strftime("%B %d, %Y %H:%M:%S.%f")` + "  -  " + message)
	

def getCurrentDateTime():
	mydate = datetime.datetime.utcnow()
	return mydate


# ########################################################################################## #
#  Initialize values #

logMessage("Beginning script to update admin account details for your HomePiSecurity system...")
logMessage("First need to obtain information:")

# Get Module ID from user:
email = raw_input("Please enter admin email address: ")
sms = raw_input("Please enter mobile number for admin (must be in this format: +18015551234) ")


# ########################################################################################## #
# Execute Add Module
logMessage("Sending the following information to be added: ")
logMessage("Email Address for Admin: " + str(email))
logMessage("Mobile Phone Number: " + str(sms))

returnValue = updateAdmin(email, sms)

if (returnValue):
	logMessage("Operation Successful.")
else:
	logMessage("Operation did not complete successfully.")


# ########################################################################################## #


