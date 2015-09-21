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

def insertModule(module_id, pin_id, pin_name, pin_message):

	sql = "INSERT into security_modules (app_module_id, module_name, pin_id, message, active, last_change_date) VALUES (" + str(module_id) + ", '" + str(pin_name) + "', " + str(pin_id) + ", '" + str(pin_message) + "', 1, now())" 

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

logMessage("Beginning script to add new module to your HomePiSecurity system...")
logMessage("First need to obtain information:")
logMessage("")


# Get Module ID from user:
module_id = raw_input("Please enter module id (default should be 1): ")
pin_id = raw_input("Please enter GPIO pin id for module (window, door, etc.) to be created: ")
pin_name = raw_input("What name should be used for this module? (ex. Front Door, Back Door, etc.): ")
pin_message = raw_input("What alert message should be sent when this module is triggered? (i.e. this will be the alert message): ")


# ########################################################################################## #
# Execute Add Module
logMessage("Sending the following information to be added: ")
logMessage("Module ID: " + str(module_id))
logMessage("GPIO Pin ID: " + str(pin_id))
logMessage("Module Name: " + str(pin_name))
logMessage("Module Alert Message: " + str(pin_message))

returnValue = insertModule(module_id, pin_id, pin_name, pin_message)

if (returnValue):
	logMessage("Operation Successful.")
else:
	logMessage("Operation did not complete successfully.")


# ########################################################################################## #


