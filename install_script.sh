#!/bin/sh
 
# ################################################################ # 
# Installation script for HomePiSecurity

# System Update and Upgrade
sudo apt-get update -q
sudo apt-get upgrade -q
 
# Install MySQL Server
apt-get -q -y install mysql-server
mysqladmin -u root password TheMySQLPass1

# Install the Python MySQL components
sudo apt-get install python-mysqldb -q

# Install the Twilio interface components
sudo apt-get install python-setuptools -q
sudo easy_install pip
yes | sudo pip install twilio

# Install Apache Web Server
sudo apt-get install apache2 -y -q

# Clone the git repository for HomePiSecurity
sudo mkdir /apps
cd /apps
sudo git clone https://github.com/darinbunker/HomePiSecurity.git

# Install the HomePiSecurity Database
mysql -u root -pTheMySQLPass1 < /apps/HomePiSecurity/database/home_security_db_script.sql

exit 0