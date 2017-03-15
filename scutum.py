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

For tutorial please look at the Github Page: https://github.com/K4YT3X/SCUTUM

"""
from __future__ import print_function
import socket
import struct
import os
import datetime
import time
import argparse

LOGPATH = '/var/log/scutum.log'
VERSION = '1.3'


# -------------------------------- Classes --------------------------------

class NotRoot(Exception):
	pass


class ccm():
	"""
		This Class defines some output styles and
		All UNIX colors
	"""

	# Define Global Color
	global W, R, G, OR, Y, B, P, C, GR, H, BD, NH
	# Console colors
	# Unix Console colors
	W = '\033[0m'  # white (normal / reset)
	R = '\033[31m'  # red
	G = '\033[32m'  # green
	OR = '\033[33m'  # orange
	Y = '\033[93m'  # yellow
	B = '\033[34m'  # blue
	P = '\033[35m'  # purple
	C = '\033[96m'  # cyan
	GR = '\033[37m'  # grey
	H = '\033[8m'  # hidden
	BD = '\033[1m'  # Bold
	NH = '\033[28m'  # not hidden

	def __init__(self, arg):
		super(ccm, self).__init__()
		self.arg = arg

	def info(msg):
		print(G + '[+] INFO: ' + str(msg) + W)

	def t_info(msg):
		print(W + str(datetime.datetime.now()) + G + ' [+] INFO: ' + str(msg) + W)

	def warning(msg):
		print(Y + BD + '[!] WARNING: ' + str(msg) + W)

	def error(msg):
		print(R + BD + '[!] ERROR: ' + str(msg) + W)

	def debug(msg):
		print(R + BD + '[*] DBG: ' + str(msg) + W)

	def input(msg):
		res = input(Y + BD + '[?] USER: ' + msg + W)
		return res

	def ask(msg, default=False):
		if default is False:
			while True:
				ans = ccm.input(msg + ' [y/N]: ')
				if ans == '' or ans[0].upper() == 'N':
					return False
				elif ans[0].upper() == 'Y':
					return True
				else:
					ccm.error('Invalid Input!')
		elif default is True:
			while True:
				ans = ccm.input(msg + ' [Y/n]: ')
				if ans == '' or ans[0].upper() == 'Y':
					return True
				elif ans[0].upper() == 'N':
					return False
				else:
					ccm.error('Invalid Input!')
		else:
			raise TypeError('invalid type for positional argument: \' default\'')


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


def processArguments():
	"""
	This funtion takes care of all arguments
	"""
	global args
	parser = argparse.ArgumentParser()
	action_group = parser.add_argument_group('ACTIONS')
	action_group.add_argument("-w", "--wicd", help="Wicd Daemon Argument, only used when called by wicd", action="store_true", default=False)
	action_group.add_argument("-r", "--reset", help="Allow all ARP packets", action="store_true", default=False)
	action_group.add_argument("-p", "--purgelog", help="Purge Log File", action="store_true", default=False)
	action_group.add_argument("--install", help="Install Scutum Automatically", action="store_true", default=False)
	action_group.add_argument("--uninstall", help="Uninstall Scutum Automatically", action="store_true", default=False)
	args = parser.parse_args()


# -------------------------------- Execute --------------------------------

processArguments()
try:
	if not (args.purgelog or args.install or args.uninstall):
		log = open(LOGPATH, 'a+')  # Just for debugging
		log.write(str(datetime.datetime.now()) + ' ---- START ----\n')
		log.write(str(datetime.datetime.now()) + '  UID: ' + str(os.getuid()) + '\n')
	if os.getuid() != 0:  # Arptables requires root
		ccm.error('Scutum requires root access to run!')
		raise NotRoot(str(datetime.datetime.now()) + ' Not Root')
	if args.install:
		ccm.info('Start Installing Scutum...')
		os.rename(os.path.abspath(__file__), '/usr/bin/scutum')
		os.system('chown root: /usr/bin/scutum')
		os.system('chmod 755 /usr/bin/scutum')
		if os.path.isdir('/etc/wicd/scripts'):
			with open('/etc/wicd/scripts/postconnect/scutum_connect', 'w') as postconnect:
				postconnect.write('#!/bin/bash\n')
				postconnect.write('scutum')
				postconnect.close()
			with open('/etc/wicd/scripts/postdisconnect/scutum_disconnect', 'w') as postdisconnect:
				postdisconnect.write('#!/bin/bash\n')
				postdisconnect.write('scutum --reset')
				postdisconnect.close()
			os.system('chown root: /etc/wicd/scripts/postconnect/scutum_connect')
			os.system('chmod 755 /etc/wicd/scripts/postconnect/scutum_connect')
			os.system('chown root: /etc/wicd/scripts/postdisconnect/scutum_disconnect')
			os.system('chmod 755 /etc/wicd/scripts/postdisconnect/scutum_disconnect')
		else:
			ccm.error('WICD folder not found!')
			ccm.error('Scutum Depends on WICD to run!')
			exit(1)
		ccm.info('Installation Complete!')
		exit(0)
	elif args.uninstall:
		confirmed = ccm.ask('Removal Confirm: ', False)
		if confirmed:
			os.remove('/usr/bin/scutum')
			os.remove('/etc/wicd/scripts/postconnect/scutum_connect')
			os.remove('/etc/wicd/scripts/postdisconnect/scutum_disconnect')
			ccm.info('Scutum sucessfully removed!')
			exit(0)
		else:
			ccm.warning('Removal Canceled')
			exit(0)
	elif args.reset:
		log.write(str(datetime.datetime.now()) + ' ---- START ----\n')
		os.system('arptables -P INPUT ACCEPT')
		os.system('arptables --flush')
		ccm.info('RST OK')
		log.write(str(datetime.datetime.now()) + ' RESET OK\n')
		log.write(str(datetime.datetime.now()) + ' ---- FINISH ----\n')
	elif args.purgelog:
		os.remove(LOGPATH)
		ccm.info('LOG PURGE OK')
		exit(0)
	else:
		os.system('arptables -P INPUT ACCEPT')  # Accept to get Gateway Cached
		updateArpTables()
		ccm.info('OK')
except Exception as er:
	ccm.error(str(er))
	if not (args.purgelog or args.install or args.uninstall):
		log.write(str(datetime.datetime.now()) + ' -!-! ERROR !-!-\n')
		log.write(str(er) + '\n')
finally:
	if not (args.purgelog or args.install or args.uninstall):
		log.write(str(datetime.datetime.now()) + ' ---- FINISH ----\n\n')
		log.close()
