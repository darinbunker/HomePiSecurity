# Installation Instructions
This guide provides the instructions to install the Home Pi Security System

## Overview
The installation process will walk through installing the pre-requisites, configuration and initializaiton of the system.

## Version Dependencies
* Raspberry Pi Hardware: Version 2
* Raspbian Image: Release date: 2015-05-05, Kernel version:3.18
* MySQL - version 5.5
* Python 2.7.3
* python-mysqldb (1.2.3-2)
* Apache - Apache/2.2.22 (Debian)
* Java 1.8

## Detail Steps
1. Raspberry Pi Configuration
  * Get the latest Raspbian image
    * https://www.raspberrypi.org/downloads/
  * Install image to SD card
    * https://www.raspberrypi.org/documentation/installation/installing-images/mac.md
    * Steps
      * Find disk identifier (I have a built in card reader…for this example I will use “disk2")
      * Unmount any partitions using the “Disk Utility"
        * Execute: `diskutil unmountDisk /dev/disk2`
      * On my Mac, open a terminal and navigate to the unzipped image file for the Raspbian operating system
        * Execute: `sudo dd bs=1m if=./raspbian.img of=/dev/rdisk2`
1. Raspberry Pi Communication Setup
  * Now that we have the operating system ready, we need to logon for the first time and setup SSH (so we can access the RaspberryPi from other machines…it’s easier to work with), Wifi, etc.
  * Step-by-step:
    * Plugin the RaspberryPi and boot up
    * Run through the configuration tools to setup the RaspberryPi
      * I always do the following:
        * Expand Filesystem - Use everything available
        * Change User Password
        * Advanced Options:
          * Hostname - Give new name: “HomePiSecurity"
          * SSH - This is very helpful to work on the pi from a different computer
    * Reboot
    * Login with the username “pi” and the password of “raspberry" (unless you change the password above)
      * You should change this password
    * Setup Wifi (this is optional if you are using a wired connection to the Raspberry Pi)
      * update `/etc/network/interfaces`
        * Example:
          * auto lo <br>
            iface lo inet loopback <br><br>
            auto eth0 <br>
            allow-hotplug eth0 <br>
            iface eth0 inet dhcp <br><br>
            auto wlan0 <br>
            allow-hotplug wlan0 <br>
            iface wlan0 inet dhcp <br>
            wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf
      * update `/etc/wpa_supplicant/wpa_supplicant.conf`
        * Example (place at the end of the file):
          * network={<br>
            ssid=“MyAccessPoint"<br>
            psk=“123456"<br>
            }
  * Connect via SSH from a different computer
    * Execute: `ssh pi@10.0.0.100`
      * use the password for the pi user
1. Get the HomePiSecurity Code
  * Create the directory on the RaspberryPi
  * Commands to execute:
    * `cd /`
    * `sudo mkdir apps`
    * `cd /apps`
  * Get code from Git
    * The following commands will download the HomePiSecurity code from GitHub
    * Execute: `sudo git clone https://github.com/darinbunker/HomePiSecurity.git`
1. Execute the install script
  * Execute: `sudo sh /apps/HomePiSecurity/install_script.sh`
    * Optionally, you can provide a unique password to be used for the MySQL installation (default password is "TheMySQLPass!")
      * `sudo sh /apps/HomePiSecurity/install_script.sh MyPassword`
    * Approximate install time is between 20-30 minutes
1. Obtain settings values:
  * To use SMS you will need to create an account from Twilio and get the following:
    * Account_SID
    * Auth_Token
    * Twilio_number (the configuration number must have a “+” in front of it.  You also need to make sure the numbers that are sent to twilio are in this exact format: +18015551234 - without the "+" or the "1" in front you will get errors.) 
  * To use Email you will need to get the following information from your email provider (Hint: since you will need to hardcode the password in the settings file, it might be a good idea to create a new email account so that it doesn’t expose your full email.  This account is just for sending…not receiving.
    * EMAIL_SMTP
    * EMAIL_SEND_ACCT
    * EMAIL_PWD
    * EMAIL_FROM
1. Update configuration file for Security Engine
  * edit the file: `/apps/HomePiSecurity/engine/configSettings.py`
  * Update the following sections:
    * Database connection details
    * SMS Settings
    * Email Settings
1. Set the GPIO pins for your doors and windows
  * First, configure the security sensors to the GPIO Pins
    * Each sensor requires two wires, black and red (or something similar)
    * All of the black wires from each door or window are connected together
    * Connect red wire to an individual GPIO pin
    * YouTube video on how to set it up: https://youtu.be/Rc2NDygT4Ms
  * Second, determine which pins are assigned to which doors or windows
    * Execute the “display_pin_status.py” file to determine which GPIO pins are associated to door or window
      * `sudo python /apps/HomePiSecurity/engine/display_pin_status.py`
    * Get a baseline
      * Run the display_pin_status.py file to get a base of which pins have which status
    * Open a door and re-run display_pin_status.py
  * Third, update the database with the GPIO pin details
    * For each GPIO pin, run the following to insert into the database:
      * Execute: `sudo python /apps/HomePiSecurity/engine/add_module.py`
        * Follow the prompts of the script to provide the details needed to insert into the database
1. Configure system users and security schedules
  * A default user account has been added to the system.  Since the password is already hashed you need to will need to update the existing user.
    * Execute this command to update the default admin account (You need to replace your email and sms_number):
      * `sudo python /apps/HomePiSecurity/engine/update_admin.py`
        * Follow the prompts to complete the update
        * The default password for the admin user is 123456.
1. Start Security System Service
  * Start the System
    * Execute: `sudo sh /etc/init.d/armed-engine.sh start`
  * Check service status
    * Execute: `sudo sh /etc/init.d/armed-engine.sh status`









