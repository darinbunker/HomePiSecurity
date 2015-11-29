#!/bin/sh
 
# ################################################################ # 
# update settings file for security engine

installdir=$(cd $(dirname $0); pwd -P)

printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
printf "# Step 1 -  Obtain Email Settings \n"
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
printf "\n"
printf "Please enter email SMTP servername: \n"

read email_smtp

printf "\n"
printf "Please enter email SMTP port number (default is usually 587): \n"

read email_smtp_port

# Now check settings

# Update settings file
sudo sed -i "s:ReplaceSMTPServername:$email_smtp:g" $installdir/configSettings.py
sudo sed -i "s:ReplaceSMTPServerPort:$email_smtp_port:g" $installdir/configSettings.py

printf "\n"
printf "Please enter email address account (i.e. myemailaddress@gmail.com): \n"

read email_send_acct
sudo sed -i "s:ReplaceEmailSendAccount:$email_send_acct:g" $installdir/configSettings.py

printf "\n"
printf "Please enter email address account password: \n"

read email_send_acct_pass
sudo sed -i "s:ReplaceEmailAccountPassword:$email_send_acct_pass:g" $installdir/configSettings.py


printf "\n"
printf "Please enter email address who is sending message (i.e. this is the from account): \n"

read email_from_acct
sudo sed -i "s:ReplaceEmailFromAccount:$email_from_acct:g" $installdir/configSettings.py


printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
printf "# Step 2 -  Configure Twilio Settings \n"
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
printf "\n"
printf "Please enter Account SID (i.e. Af8d2dcc20eCf18e231b85ffbac6fee3a6: \n"

read sms_acct

# Update settings file
sudo sed -i "s:ReplaceSMSAccountID:$sms_acct:g" $installdir/configSettings.py

printf "\n"
printf "Please enter SMS Authentication Token (i.e. 82b546e6fdaab955b5bdaa53b37d84b9): \n"

read sms_auth_token
sudo sed -i "s:ReplaceSMSAuthToken:$sms_auth_token:g" $installdir/configSettings.py


printf "\n"
printf "Please enter SMS phone number - must start with '+' (i.e. +18015551234): \n"

read sms_number
sudo sed -i "s:ReplaceSMSNumber:$sms_number:g" $installdir/configSettings.py

printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
printf "# Setting Update Complete \n"
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
printf "\n"


exit 0