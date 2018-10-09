#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: SCUTUM Easy TCP: openport
Author: K4YT3X
Date Created: Sep 15, 2017
Last Modified: April 25, 2018

Description: This script opens ports on UFW Firewall

This class is migrated from Project: DefenseMatrix

Version 1.2
"""

from ufw import Ufw
import avalon_framework as avalon
import sys
LOGPATH = '/var/log/scutum.log'

log = open(LOGPATH, 'a+')
ufwctrl = Ufw(log=log)
try:
    ports = []
    for port in sys.argv[1:]:
        ports.append(int(port))
    for port in ports:
        ufwctrl.allow(port)
except ValueError:
    avalon.error("Not a valid port number!")
