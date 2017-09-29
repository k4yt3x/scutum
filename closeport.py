#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: SCUTUM Easy TCP: closeport
Author: K4YT3X
Date Created: Sep 15, 2017
Last Modified: Sep 28, 2017

Description: This script closes oprts on UFW Firewall

This class is migrated from Project: DefenseMatrix
"""

from iptables import Ufw
from logger import Logger
import avalon_framework as avalon
import sys

log = Logger()
ufwctrl = Ufw(log)
try:
    ports = []
    for port in sys.argv[1:]:
        ports.append(int(port))
    for port in ports:
        ufwctrl.expire(port)
except ValueError:
    avalon.error("Not a valid port number!")
