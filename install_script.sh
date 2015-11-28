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

serverAddress=$(/sbin/ifconfig | grep -e "inet:" -e "addr:" | grep -v "inet6" | grep -v "127.0.0.1" | head -n 1 | awk '{print $2}' | cut -c6-)
serverPort="8443"

#installdir=$PWD
installdir=$(dirname $0)
printf "install_script.sh install directory: $installdir"

printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
echo "Start time: $(date)"
printf "\n"

printf "Install Directory: $installdir\n"

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
printf "** Executing: sudo apt-get -q -y install mysql-server"
sudo apt-get -q -y install mysql-server

# Install the Python MySQL components
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
printf "# Step 2 -  Execute install of Python MySQL components...#\n"
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
printf "** Executing: sudo apt-get -y install python-mysqldb -q"
sudo apt-get -y install python-mysqldb -q

# Install the Twilio interface components
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
printf "# Step 3 -  Execute install of Twilio components...#\n"
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
printf "** Executing: sudo apt-get -y install python-setuptools -q"
sudo apt-get -y install python-setuptools -q
printf "** Executing: sudo easy_install pip"
sudo easy_install pip
printf "** Executing: yes | sudo pip install twilio"
yes | sudo pip install twilio

# Install Apache Web Server
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
printf "# Step 4 -  Execute install of Apache Web Server...#\n"
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
printf "** Executing: sudo apt-get install apache2 -y -q"
sudo apt-get install apache2 -y -q

# Install the HomePiSecurity Database
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
printf "# Step 5 -  Execute install of MySQL database...#\n"
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
# mysql -u root -p$MySQLPass < /apps/HomePiSecurity/database/home_security_db_script.sql
printf "** Executing: mysql -u root -p$MySQLPass < $installdir/database/home_security_db_script.sql \n"
mysql -u root -p$MySQLPass < $installdir/database/home_security_db_script.sql

# Copy execution file to startup location
# sudo cp /apps/HomePiSecurity/engine/armed-engine.sh /etc/init.d/armed-engine.sh
printf "** Executing: sudo cp $installdir/engine/armed-engine.sh /etc/init.d/armed-engine.sh \n"
sudo cp $installdir/engine/armed-engine.sh /etc/init.d/armed-engine.sh

# Install Java Tools to create SSL cert
# printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
# printf "# Step 6 -  Install of Java tools (Openjdk...)#\n"
# printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
#sudo apt-get install openjdk-7-jdk

# Setup Python Engine service
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
printf "# Step 6 -  Configure SSL communications...#\n"
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
# First update the service file
# ReplaceHomeDirectory
printf "** Executing: sudo sed -i s:ReplaceHomeDirectory:$installdir/engine:g $installdir/engine/armed-engine.sh \n"
sudo sed -i "s:ReplaceHomeDirectory:$installdir/engine:g" $installdir/engine/armed-engine.sh
# Move file to service director
printf "** Executing: sudo cp $installdir/engine/armed-engine.sh /etc/init.d/armed-engine.sh \n"
sudo cp $installdir/engine/armed-engine.sh /etc/init.d/armed-engine.sh


# Setup SSL for Web Server
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
printf "# Step 7 -  Configure SSL communications...#\n"
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
printf "** Executing: sudo a2ensite default-ssl \n"
sudo a2ensite default-ssl
printf "** Executing: sudo a2enmod ssl \n"
sudo a2enmod ssl
## Restart apache services
printf "** Executing: sudo service apache2 restart \n"
sudo service apache2 restart
printf "** Executing: sudo /etc/init.d/apache2 restart \n"
sudo /etc/init.d/apache2 restart
## Generate the certificate and copy it to configured location
# sudo sh /apps/HomePiSecurity/create_cert.sh homepisecurity
printf "** Executing: sudo sh $installdir/install/cert/create_cert.sh homepisecurity \n"
sudo sh $installdir/install/cert/create_cert.sh homepisecurity
printf "** Executing: sudo mkdir /etc/apache2/ssl \n"
sudo mkdir /etc/apache2/ssl
#sudo cp ./homepisecurity.crt /etc/apache2/ssl/homepisecurity.pem
printf "** Executing: sudo cp $installdir/install/cert/homepisecurity.crt /etc/apache2/ssl/homepisecurity.pem \n"
sudo cp $installdir/install/cert/homepisecurity.crt /etc/apache2/ssl/homepisecurity.pem
#sudo cp ./homepisecurity.key /etc/apache2/ssl/homepisecurity.key
printf "** Executing: sudo cp $installdir/install/cert/homepisecurity.key /etc/apache2/ssl/homepisecurity.key \n"
sudo cp $installdir/install/cert/homepisecurity.key /etc/apache2/ssl/homepisecurity.key
#sudo cp ./homepisecurity.p12 /etc/apache2/ssl/homepisecurity.p12
printf "** Executing: sudo cp $installdir/install/cert/homepisecurity.p12 /etc/apache2/ssl/homepisecurity.p12 \n"
sudo cp $installdir/install/cert/homepisecurity.p12 /etc/apache2/ssl/homepisecurity.p12
printf "** Executing: sudo cp $installdir/install/cert/homepisecurity.p12 $installdir/service/latest/homepisecurity.p12 \n"
sudo cp $installdir/install/cert/homepisecurity.p12 $installdir/service/latest/homepisecurity.p12
printf "** Executing: sudo chmod 600 /etc/apache2/ssl/homepisecurity.key \n"
sudo chmod 600 /etc/apache2/ssl/homepisecurity.key

## Create a copy of current default-ssl file
#printf "** Executing: sudo cp /etc/apache2/sites-enabled/default-ssl /etc/apache2/sites-enabled/default-ssl-backup"
#sudo cp /etc/apache2/sites-enabled/default-ssl /etc/apache2/sites-enabled/default-ssl-backup

## Update default-ssl file to point to new certificate file
printf "** Executing: sudo sed -i s:/etc/ssl/certs/ssl-cert-snakeoil.pem:/etc/apache2/ssl/homepisecurity.pem:g /etc/apache2/sites-enabled/default-ssl \n"
sudo sed -i "s:/etc/ssl/certs/ssl-cert-snakeoil.pem:/etc/apache2/ssl/homepisecurity.pem:g" /etc/apache2/sites-enabled/default-ssl
printf "** Executing: sudo sed -i s:/etc/ssl/private/ssl-cert-snakeoil.key:/etc/apache2/ssl/homepisecurity.key:g /etc/apache2/sites-enabled/default-ssl \n"
sudo sed -i "s:/etc/ssl/private/ssl-cert-snakeoil.key:/etc/apache2/ssl/homepisecurity.key:g" /etc/apache2/sites-enabled/default-ssl

# We have to update the following two lines
# 1 SSLCertificateFile /etc/ssl/certs/ssl-cert-snakeoil.pem
# 2 SSLCertificateKeyFile /etc/ssl/private/ssl-cert-snakeoil.key

# with the following two lines
# 1 SSLCertificateFile /etc/apache2/ssl/homepisecurity.pem
# 2 SSLCertificateKeyFile /etc/apache2/ssl/homepisecurity.key
printf "** Executing: sudo /etc/init.d/apache2 restart \n"
sudo /etc/init.d/apache2 restart

# Setup Java Service
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
printf "# Step 8 -  Setup Java Service...#\n"
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
# sudo sed -i "s:ReplaceConnectionUsername:$dbuser:g" /apps/HomePiSecurity/service/latest/application.properties
printf "** Executing: sudo sed -i s:ReplaceConnectionUsername:$dbuser:g $installdir/service/latest/application.properties \n"
sudo sed -i "s:ReplaceConnectionUsername:$dbuser:g" $installdir/service/latest/application.properties
# sudo sed -i "s:ReplaceConnectionPassword:$MySQLPass:g" /apps/HomePiSecurity/service/latest/application.properties
printf "** Executing: sudo sed -i s:ReplaceConnectionPassword:$MySQLPass:g $installdir/service/latest/application.properties \n"
sudo sed -i "s:ReplaceConnectionPassword:$MySQLPass:g" $installdir/service/latest/application.properties

# Update the service process
printf "** Executing: sudo sed -i s:addpathtojar:$installdir/service/latest/dbunk-0.0.4:g $installdir/service/pi-service.sh \n"
sudo sed -i "s:addpathtojar:$installdir/service/latest/dbunk-0.0.4:g" $installdir/service/pi-service.sh
printf "** Executing: sudo sed -i s:ReplaceConfigLocation:$installdir/service/latest:g $installdir/service/pi-service.sh \n"
sudo sed -i "s:ReplaceConfigLocation:$installdir/service/latest:g" $installdir/service/pi-service.sh
printf "** Executing: sudo sed -i s:ReplaceDirectoryPath:$installdir/service/latest:g $installdir/service/latest/application.properties \n"
sudo sed -i "s:ReplaceDirectoryPath:$installdir/service/latest:g" $installdir/service/latest/application.properties

# Move service process file to init.d 
printf "** Executing: sudo cp $installdir/service/pi-service.sh /etc/init.d/pi-service.sh \n"
sudo cp $installdir/service/pi-service.sh /etc/init.d/pi-service.sh
#printf "** Executing: sudo cp $installdir/service/latest/application.properties /etc/init.d/application.properties \n"
#sudo cp $installdir/service/latest/application.properties /etc/init.d/application.properties

# Start the service
printf "Starting HomePiSecurity Service..."
printf "** Executing: sudo sh /etc/init.d/pi-service.sh start"
sudo sh /etc/init.d/pi-service.sh start


# Setup Web Service
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
printf "# Step 9 -  Setup Web Service...#\n"
printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
# Update new web configuration files
printf "** Executing: sudo sed -i s:ReplaceDirectoryNameRoot:$installdir/web/www:g $installdir/web/config/homepimanage.conf \n"
sudo sed -i "s:ReplaceDirectoryNameRoot:$installdir/web/www:g" $installdir/web/config/homepimanage.conf
printf "** Executing: sudo sed -i s:ReplaceDirectoryNameDirectory:$installdir/web/www/:g $installdir/web/config/homepimanage.conf \n"
sudo sed -i "s:ReplaceDirectoryNameDirectory:$installdir/web/www/:g" $installdir/web/config/homepimanage.conf
printf "** Executing: sudo sed -i s:ReplaceDirectoryNameRoot:$installdir/web/www:g $installdir/web/config/homepimanage-ssl.conf \n"
sudo sed -i "s:ReplaceDirectoryNameRoot:$installdir/web/www:g" $installdir/web/config/homepimanage-ssl.conf
printf "** Executing: sudo sed -i s:ReplaceDirectoryNameDirectory:$installdir/web/www/:g $installdir/web/config/homepimanage-ssl.conf \n"
sudo sed -i "s:ReplaceDirectoryNameDirectory:$installdir/web/www/:g" $installdir/web/config/homepimanage-ssl.conf
# Move the configuration files
printf "** Executing: sudo cp $installdir/web/config/homepimanage.conf /etc/apache2/sites-available/homepimanage.conf \n"
sudo cp $installdir/web/config/homepimanage.conf /etc/apache2/sites-available/homepimanage.conf
printf "** Executing: sudo cp $installdir/web/config/homepimanage-ssl.conf /etc/apache2/sites-available/homepimanage-ssl.conf \n"
sudo cp $installdir/web/config/homepimanage-ssl.conf /etc/apache2/sites-available/homepimanage-ssl.conf 
# Set properties values for web site
printf "** Executing: sudo sed -i s:SetServicePathVariable:$serverAddress:g $installdir/web/www/js/app.js \n"
sudo sed -i "s:SetServicePathVariable:$serverAddress:g" $installdir/web/www/js/app.js
printf "** Executing: sudo sed -i s:SetServicePortVariable:$serverPort:g $installdir/web/www/js/app.js \n"
sudo sed -i "s:SetServicePortVariable:$serverPort:g" $installdir/web/www/js/app.js
# Disable the existing default website
printf "** Executing: sudo a2dissite default \n"
sudo a2dissite default
printf "** Executing: sudo a2dissite default-ssl \n"
sudo a2dissite default-ssl
printf "** Executing: sudo rm /etc/apache2/sites-enabled/default-ssl \n"
sudo rm /etc/apache2/sites-enabled/default-ssl

# Enable the HomePiSecuritySite
printf "** Executing: sudo a2ensite homepimanage.conf \n"
sudo a2ensite homepimanage.conf
printf "** Executing: sudo a2ensite homepimanage-ssl.conf \n"
sudo a2ensite homepimanage-ssl.conf 
# Reload the service
printf "** Executing: sudo service apache2 reload \n"
sudo service apache2 reload



printf "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n"
echo "End time: $(date)"
printf "\n"





exit 0