# HomePiSecurity
Home Security System using a Raspberry Pi

This project provides the code necessary for a home security system using a Raspberry Pi.  It is broken into the following parts:
* Raspberry Pi (A, B, B+ or 2)
* Engine - this uses python to check the status of the GPIO pins every second
* Database - a MySQL database stores all state for the system.  It is installed on the Raspberry Pi
* Service - This provides REST services to allow communication with the DB and Engine
* Web App - This is an Angular project, also using ngMaterial, to provide an interface to the security system

