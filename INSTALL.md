# Installation Instructions
This guide provides the instructions to install the Home Pi Security System

# Overview
The installation process will walk through installing the pre-requisites, configuration and initializaiton of the system.

# Detail Steps
1. Prepare Raspberry Pi (Connectivity)
* The first step is to get a Raspberry Pi and do the following:
** Install latest RASPBIAN distro of the Raspberry Pi
** Setup SSH - This will allow you to remotely connect from other machines
2. Install MySQL
* sudo apt-get install mysql-server
3. Install Python
* Install the latest Python package compatible with your Raspberry Pi
4. Create Database & Install Schema
* Execute the install script as part of this repository: home_security_db_script.sql
5. Set Configuration Settings (email, sms, siren, etc.)
* Update the configuration file for the Python engine: configSettings.py
6. Install Engine Service
* Install service script to execute engine as a service: armed-engine.sh
7. Run System




