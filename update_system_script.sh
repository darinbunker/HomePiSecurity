#!/bin/sh
 
# ################################################################ # 
# Update System Script 

# System Update and Upgrade
printf "Execute apt-get update...\n"
sudo apt-get update -q
printf "Execute apt-get upgrade...\n"
sudo apt-get upgrade -y --force-yes -qq


exit 0