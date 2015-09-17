#!/usr/bin/python

# Database connection details
HOST_NAME = "localhost"
DB_USER = "root"
DB_PASSWORD = "123456"
DB_DATABASE = "HomeSecuritySystem"

# SMS Settings - Only Twilio is supported with this version
# The following values are examples of what is expected
ACCOUNT_SID = "ACfc2e23fef3120eb9a5eeac6a61b85ffb"
AUTH_TOKEN = "4b28d8dc6fab93b37ddabd468555b5a8"
TWILIO_NUMBER = "+18015559060"

# These values provide the email settings
EMAIL_SMTP = "smtp.gmail.com:587"
EMAIL_SEND_ACCT = "useremailsend@gmail.com"
EMAIL_PWD = "88499300300"
EMAIL_FROM = "emailsenderfrom@gmail.com"

# Siren Settings.  
# If you have a Siren enabled you will need to provide
# the GPIO pin for the Siren
SIREN_PIN = 0

# Set the global values for logging
# Values of "0" mean very minimal logging.  "1" will provide all logging.
DEBUG = 0
DEBUGDETAIL = 0

# Time and Date settings
TIME_ZONE_OFFSET = 6 #This will ensure MST
DAY_OF_WEEK_OFFSET = 1 #This will make Sunday as day 1

# Should events be logged to DB?
LOG_ENTRIES = 1
LOG_ENTRIES_EXCEPTION_ONLY = 0
