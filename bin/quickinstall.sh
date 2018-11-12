#!/bin/bash
# Name: SCUTUM QuickInstall Script
# Author: K4YT3X
# Date Created: Sep 27, 2017
# Last Modified: November 12, 2018
# Version 1.1.1

# Check if user is root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

# Remove older versions of scutum
if [ -d "/usr/share/scutum/" ]; then
  echo "Removing old SCUTUM files..."
  rm -rf /usr/share/scutum/
fi

# Clone the newest version of scutum
git clone https://github.com/K4YT3X/scutum.git /usr/share/scutum

# Run installation
/usr/bin/env python3 /usr/share/scutum/bin/scutum.py --install
