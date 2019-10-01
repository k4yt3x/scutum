#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: scutum network manager hook
Author: K4YT3X
Date Created: September 23, 2019
Last Modified: September 23, 2019
"""

# built-in imports
import subprocess
import sys

# get network manager arguments
try:
    interface = sys.argv[1]
    status = sys.argv[2]
except IndexError:
    exit(0)

if status == "down":
    exit(subprocess.run(['scutum', '--reset']).returncode)

if status == "up":
    exit(subprocess.run(['scutum']).returncode)
