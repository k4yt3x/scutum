#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
	╬##################╬
	##       ##       ##
	##  #    ##    #  ##
	##  #    ##    #  ##
	##  #    ##    #  ##
	##   #   ##   #   ##
	##    ## ## ##    ##     ___   __  _  _  ____  _  _  __  __
	##      ####      ##    / __) / _)( )( )(_  _)( )( )(  \/  )
	####################    \__ \( (_  )()(   )(   )()(  )    (
	##      ####      ##    (___/ \__) \__/  (__)  \__/ (_/\/\_)
	##    ## ## ##    ##
	##   #   ##   #   ##               ARP Firewall
	##  #    ##    #  ##
	##  #    ##    #  ##
	##  #    ##    #  ##
	##       ##       ##
	╬##################╬


Name: SCUTUM Firewall
Author: K4T
Date: 3/8/17

Licensed under the GNU General Public License Version 3 (GNU GPL v3),
	available at: https://www.gnu.org/licenses/gpl-3.0.txt

(C) 2017 K4YT3X

Description: Scutum Prevents the system from being arp spoofed by others
and allows you to be invisible on LAN if used properly with iptables

!!! DEPENDS ON WICD !!!

Usage:
	1. Put this application in wicd post connect scripts folder:
		cp scutum.py /etc/wicd/scripts/postconnect/scutum

	2. Set the attributes correctly:
		chmod 755 /etc/wicd/scripts/postconnect/scutum
		chown root: /etc/wicd/scripts/postconnect/scutum

	3. Reload wicd service:
		service wicd restart
		# If this doesn't work, reboot

	4. You're ready to roll

Log file is at /var/log/scutum.log

"""
import socket
import struct
import os
import datetime
import time

VERSION = '1.0.2'


# -------------------------------- Functions --------------------------------

def getGateway():
	"""Get Linux Default Gateway"""
	with open("/proc/net/route") as fh:
		for line in fh:
			fields = line.strip().split()
			if fields[1] != '00000000' or not int(fields[3], 16) & 2:
				continue

			return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))
	return 0


def getGatewayMac():
	"""Get Gateway Mac Address"""
	with open('/proc/net/arp') as arpf:
		for line in arpf:
			if line.split(' ')[0] == getGateway():
				for field in line.split(' '):
					if len(field) == 17 and ':' in field:
						return field
	return 0


def updateArpTables():
	"""Update Arptables"""
	while True:  # Wait Until Gateway ARP is cached
		gatewayMac = str(getGatewayMac())
		# os.system('nslookup google.ca')  # Works as well as the following
		try:
			ac = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			ac.settimeout(0)
			ac.connect((getGateway(), 0))  # Connect to gateway to cache gateway MAC
			ac.close()
		except Exception:
			pass
		if gatewayMac != '00:00:00:00:00:00' and len(gatewayMac) == 17:  # Check if it's a valid MAC Address
			break
		time.sleep(0.5)  # Be nice to CPU
	log.write(str(datetime.datetime.now()) + '  MAC: ' + gatewayMac + '\n')
	log.write(str(datetime.datetime.now()) + '  IP: ' + socket.gethostbyname(socket.gethostname()) + '\n')
	os.system('arptables --flush')
	os.system('arptables -P INPUT DROP')
	os.system('arptables -A INPUT --source-mac ' + gatewayMac + ' -j ACCEPT')


# -------------------------------- Execute --------------------------------

log = open('/var/log/scutum.log', 'a+')  # Just for debugging
try:
	log.write(str(datetime.datetime.now()) + ' ---- START ----\n')
	log.write(str(datetime.datetime.now()) + '  UID: ' + str(os.getuid()) + '\n')
	if os.getuid() != 0:  # Arptables requires root
		raise Exception(str(datetime.datetime.now()) + ' Root Required\n')
	os.system('arptables -P INPUT ACCEPT')  # Accept to get Gateway Cached
	updateArpTables()
	print('OK')
except Exception as er:
	log.write(str(datetime.datetime.now()) + ' -!-! ERROR !-!-\n')
	log.write(str(er) + '\n')
log.write(str(datetime.datetime.now()) + ' ---- FINISH ----\n')
log.write('\n\n')
log.close()
exit(0)
