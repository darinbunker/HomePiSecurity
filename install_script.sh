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

# System Update and Upgrade
printf "Execute apt-get update...\n"
sudo apt-get update -q
printf "Execute apt-get upgrade...\n"
sudo apt-get upgrade -y --force-yes -qq

# Install MySQL Server
printf "Execute install of MySQL...\n"
echo mysql-server-5.1 mysql-server/root_password password $MySQLPass | debconf-set-selections
echo mysql-server-5.1 mysql-server/root_password_again password $MySQLPass | debconf-set-selections
apt-get -q -y install mysql-server

# Install the Python MySQL components
printf "Execute install of Python MySQL components...\n"
sudo apt-get -y install python-mysqldb -q

# Install the Twilio interface components
printf "Execute install of Twilio components...\n"
sudo apt-get -y install python-setuptools -q
sudo easy_install pip
yes | sudo pip install twilio

# Install Apache Web Server
printf "Execute install of Apache Web Server...\n"
sudo apt-get install apache2 -y -q

# Install the HomePiSecurity Database
printf "Execute install of MySQL database...\n"
mysql -u root -p$MySQLPass < /apps/HomePiSecurity/database/home_security_db_script.sql

# Copy execution file to startup location
sudo cp /apps/HomePiSecurity/engine/armed-engine.sh /etc/init.d/armed-engine.sh

# Setup SSL for Web Server
printf "Setup SSL on Apache Web Server...\n"

## Enable SSL
sudo a2ensite default-ssl
sudo a2enmod ssl
## Restart apache services
sudo service apache2 restart
sudo /etc/init.d/apache2 restart
## Generate the certificate and copy it to configured location
sudo sh create_cert.sh homepisecurity
sudo mkdir /etc/apache2/ssl
sudo cp ./homepisecurity.crt /etc/apache2/ssl/homepisecurity.pem
sudo cp ./homepisecurity.key /etc/apache2/ssl/homepisecurity.key
sudo chmod 600 /etc/apache2/ssl/homepisecurity.key

## Create a copy of current default-ssl file
sudo cp /etc/apache2/sites-enabled/default-ssl /etc/apache2/sites-enabled/default-ssl-backup

## Update default-ssl file to point to new certificate file
sudo sed -i "s:SSLCertificateFile /etc/ssl/certs/ssl-cert-snakeoil.pem:SSLCertificateFile /etc/apache2/ssl/homepisecurity.pem:g" /etc/apache2/sites-enabled/default-ssl
sudo sed -i "s:SSLCertificateKeyFile /etc/ssl/private/ssl-cert-snakeoil.key:SSLCertificateKeyFile /etc/apache2/ssl/homepisecurity.key:g" /etc/apache2/sites-enabled/default-ssl

# We have to update the following two lines
# 1 SSLCertificateFile /etc/ssl/certs/ssl-cert-snakeoil.pem
# 2 SSLCertificateKeyFile /etc/ssl/private/ssl-cert-snakeoil.key

# with the following two lines
# 1 SSLCertificateFile /etc/apache2/ssl/homepisecurity.pem
# 2 SSLCertificateKeyFile /etc/apache2/ssl/homepisecurity.key

sudo /etc/init.d/apache2 restart


exit 0