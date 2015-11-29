#!/usr/bin/python

# Database Settings 
HOST_NAME = "localhost"
DB_USER = "ReplaceDBUser"
DB_PASSWORD = "ReplaceDBPassword"
DB_DATABASE = "HomeSecuritySystem"

# SMS Settings - Only Twilio is supported with this version
# The following values are examples of what is expected
ACCOUNT_SID = "3fef3120eb9a5ACfc2e2eeac6a61b85ffb"
AUTH_TOKEN = "d8dc6fab93b37dd4b28abd468555b5a8"
TWILIO_NUMBER = "+18015559060"

# Email Settings
EMAIL_SMTP = "smtp.gmail.com:587"
EMAIL_SEND_ACCT = "useremailsend@gmail.com"
EMAIL_PWD = "88499300300"
EMAIL_FROM = "emailsenderfrom@gmail.com"

# Siren Settings.  
# If you have a Siren enabled you will need to provide
# the GPIO pin for the Siren
SIREN_PIN = 0

# Debug and Logging Settings
# Set the global values for logging
# Values of "0" mean very minimal logging.  "1" will provide all logging.
DEBUG = 0
DEBUGDETAIL = 0
# Should events be logged to DB?
LOG_ENTRIES = 1
LOG_ENTRIES_EXCEPTION_ONLY = 0

# Time and Date Settings
TIME_ZONE_OFFSET = 6 #This will ensure MST
DAY_OF_WEEK_OFFSET = 1 #This will make Sunday as day 1
