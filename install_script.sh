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
mysql -u root -p$MySQLPass < /apps/HomePiSecurity/database/home_security_db_script.sql

# Copy execution file to startup location
sudo cp /apps/HomePiSecurity/engine/armed-engine.sh /etc/init.d/armed-engine.sh

exit 0