#!/bin/sh
 
# ################################################################ # 
# Installation script for HomePiSecurity

# Set variables - MySQL Password
if [ $# -gt 0 ]
then
    MySQLPass=$1
else
    MySQLPass="TheMySQLPass1"
fi

sysname=$HOSTNAME
dbuser="root"

printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
echo "Start time: $(date)"
printf "\n"


# System Update and Upgrade
# printf "Execute apt-get update...\n"
# sudo apt-get update -q
# printf "Execute apt-get upgrade...\n"
# sudo apt-get upgrade -y --force-yes -qq

# Install MySQL Server
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
printf "# Step 1 -  Execute install of MySQL...#\n"
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
echo mysql-server-5.1 mysql-server/root_password password $MySQLPass | debconf-set-selections
echo mysql-server-5.1 mysql-server/root_password_again password $MySQLPass | debconf-set-selections
sudo apt-get -q -y install mysql-server

# Install the Python MySQL components
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
printf "# Step 2 -  Execute install of Python MySQL components...#\n"
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
sudo apt-get -y install python-mysqldb -q

# Install the Twilio interface components
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
printf "# Step 3 -  Execute install of Twilio components...#\n"
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
sudo apt-get -y install python-setuptools -q
sudo easy_install pip
yes | sudo pip install twilio

# Install Apache Web Server
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
printf "# Step 4 -  Execute install of Apache Web Server...#\n"
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
sudo apt-get install apache2 -y -q

# Install the HomePiSecurity Database
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
printf "# Step 5 -  Execute install of MySQL database...#\n"
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
mysql -u root -p$MySQLPass < /apps/HomePiSecurity/database/home_security_db_script.sql

# Copy execution file to startup location
sudo cp /apps/HomePiSecurity/engine/armed-engine.sh /etc/init.d/armed-engine.sh

# Install Java Tools to create SSL cert
# printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
# printf "# Step 6 -  Install of Java tools (Openjdk...)#\n"
# printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
#sudo apt-get install openjdk-7-jdk

# Setup SSL for Web Server
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
printf "# Step 6 -  Configure SSL communications...#\n"
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
sudo a2ensite default-ssl
sudo a2enmod ssl
## Restart apache services
sudo service apache2 restart
sudo /etc/init.d/apache2 restart
## Generate the certificate and copy it to configured location
sudo sh /apps/HomePiSecurity/create_cert.sh homepisecurity
sudo mkdir /etc/apache2/ssl
sudo cp ./homepisecurity.crt /etc/apache2/ssl/homepisecurity.pem
sudo cp ./homepisecurity.key /etc/apache2/ssl/homepisecurity.key
sudo cp ./homepisecurity.p12 /etc/apache2/ssl/homepisecurity.p12
sudo chmod 600 /etc/apache2/ssl/homepisecurity.key

## Create a copy of current default-ssl file
sudo cp /etc/apache2/sites-enabled/default-ssl /etc/apache2/sites-enabled/default-ssl-backup

## Update default-ssl file to point to new certificate file
sudo sed -i "s:/etc/ssl/certs/ssl-cert-snakeoil.pem:/etc/apache2/ssl/homepisecurity.pem:g" /etc/apache2/sites-enabled/default-ssl
sudo sed -i "s:/etc/ssl/private/ssl-cert-snakeoil.key:/etc/apache2/ssl/homepisecurity.key:g" /etc/apache2/sites-enabled/default-ssl

# We have to update the following two lines
# 1 SSLCertificateFile /etc/ssl/certs/ssl-cert-snakeoil.pem
# 2 SSLCertificateKeyFile /etc/ssl/private/ssl-cert-snakeoil.key

# with the following two lines
# 1 SSLCertificateFile /etc/apache2/ssl/homepisecurity.pem
# 2 SSLCertificateKeyFile /etc/apache2/ssl/homepisecurity.key

sudo /etc/init.d/apache2 restart

# Setup Java Service
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
printf "# Step 7 -  Setup Java Service...#\n"
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
sudo sed -i "s:ReplaceConnectionUsername:$dbuser:g" /apps/HomePiSecurity/service/latest/application.properties
sudo sed -i "s:ReplaceConnectionPassword:$MySQLPass:g" /apps/HomePiSecurity/service/latest/application.properties

printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
echo "End time: $(date)"
printf "\n"

exit 0