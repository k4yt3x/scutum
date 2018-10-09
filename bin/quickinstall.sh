#!/bin/bash
# Name: SCUTUM QuickInstall Script
# Author: K4YT3X
# Date Created: Sep 27, 2017
# Last Modified: October 9, 2018

# Description: Installs SCUTUM

# Version 1.1

if [ -d "/usr/share/scutum/" ]; then
  echo "Removing old SCUTUM files..."
  rm -rf /usr/share/scutum/
fi


git clone https://github.com/K4YT3X/scutum.git /usr/share/scutum
cd /usr/share/scutum/bin
/usr/bin/env python3 scutum.py --install
