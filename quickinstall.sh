#!/bin/bash
# Name: SCUTUM QuickInstall Script
# Author: K4YT3X
# Date Created: Sep 27, 2017
# Last Modified: Sep 29, 2017

# Description: Installs SCUTUM

# Version 1.0

if [ -d "/usr/share/scutum/" ]; then
  echo "Removing old SCUTUM files..."
  rm -rf /usr/share/scutum/
fi


git clone https://github.com/K4YT3X/SCUTUM.git /usr/share/scutum
cd /usr/share/scutum
/usr/bin/env python3 scutum.py --install