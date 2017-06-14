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

For WICD and Network-Manager

For tutorial please look at the Github Page: https://github.com/K4YT3X/SCUTUM

"""
from __future__ import print_function
import socket
import struct
import os
import datetime
import time
import argparse
import avalon_framework as avalon

LOGPATH = '/var/log/scutum.log'
VERSION = '1.4'


# -------------------------------- Classes --------------------------------

class NotRoot(Exception):
	"""
	The Exception raised when run with insufficient
	"""
	pass


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
	This function takes care of all arguments
	"""
	global args
	parser = argparse.ArgumentParser()
	action_group = parser.add_argument_group('ACTIONS')
	action_group.add_argument("-r", "--reset", help="Allow all ARP packets", action="store_true", default=False)
	action_group.add_argument("-p", "--purgelog", help="Purge Log File", action="store_true", default=False)
	action_group.add_argument("--install", help="Install Scutum Automatically", action="store_true", default=False)
	action_group.add_argument("--uninstall", help="Uninstall Scutum Automatically", action="store_true", default=False)
	args = parser.parse_args()


def installScutum():
	def install4WICD():
		avalon.info('Installing scutum for WICD')
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

	def install4NM():
		avalon.warning('Installing for network manager')
		with open('/etc/network/if-up.d/scutum_connect', 'w') as postconnect:
			postconnect.write('#!/bin/bash\n')
			postconnect.write('scutum')
			postconnect.close()
		with open('/etc/network/if-post-down.d/scutum_disconnect', 'w') as postdown:
			postdown.write('#!/bin/bash\n')
			postdown.write('scutum --reset')
			postdown.close()
		os.system('chown root: /etc/network/if-up.d/scutum_connect')
		os.system('chmod 755 /etc/network/if-up.d/scutum_connect')
		os.system('chown root: /etc/network/if-post-down.d/scutum_disconnect')
		os.system('chmod 755 /etc/network/if-post-down.d/scutum_disconnect')

	while True:
		print(avalon.FM.BD + 'Which network controller do you want to install for?' + avalon.FM.RST)
		print('1. WICD')
		print('2. Network-Manager')
		print('3. Both')

		selection = avalon.gets('Please select: ')

		if selection == '1':
			install4WICD()
			break
		elif selection == '2':
			install4NM()
			break
		elif selection == '3':
			install4WICD()
			install4NM()
			break
		else:
			avalon.error('Invalid Input!')


# -------------------------------- Execute --------------------------------

processArguments()

if os.getuid() != 0:
	avalon.error('This program must be run as root!')
	exit(0)

try:
	if not (args.purgelog or args.install or args.uninstall):
		log = open(LOGPATH, 'a+')  # Just for debugging
		log.write(str(datetime.datetime.now()) + ' ---- START ----\n')
		log.write(str(datetime.datetime.now()) + '  UID: ' + str(os.getuid()) + '\n')
	if os.getuid() != 0:  # Arptables requires root
		avalon.error('Scutum requires root access to run!')
		raise NotRoot(str(datetime.datetime.now()) + ' Not Root')
	if args.install:
		avalon.info('Start Installing Scutum...')
		os.rename(os.path.abspath(__file__), '/usr/bin/scutum')
		os.system('chown root: /usr/bin/scutum')
		os.system('chmod 755 /usr/bin/scutum')
		installScutum()
		avalon.info('Installation Complete!')
		exit(0)
	elif args.uninstall:
		confirmed = avalon.ask('Removal Confirm: ', False)
		if confirmed:
			os.remove('/usr/bin/scutum')
			try:
				os.remove('/etc/wicd/scripts/postconnect/scutum_connect')
				os.remove('/etc/wicd/scripts/postdisconnect/scutum_disconnect')
			except FileNotFoundError:
				pass
			try:
				os.remove('/etc/network/if-up.d/scutum_connect')
				os.remove('/etc/network/if-post-down.d/scutum_disconnect')
			except FileNotFoundError:
				pass
			avalon.info('Scutum sucessfully removed!')
			exit(0)
		else:
			avalon.warning('Removal Canceled')
			exit(0)
	elif args.reset:
		log.write(str(datetime.datetime.now()) + ' ---- START ----\n')
		os.system('arptables -P INPUT ACCEPT')
		os.system('arptables --flush')
		avalon.info('RST OK')
		log.write(str(datetime.datetime.now()) + ' RESET OK\n')
		log.write(str(datetime.datetime.now()) + ' ---- FINISH ----\n')
	elif args.purgelog:
		os.remove(LOGPATH)
		avalon.info('LOG PURGE OK')
		exit(0)
	else:
		os.system('arptables -P INPUT ACCEPT')  # Accept to get Gateway Cached
		updateArpTables()
		avalon.info('OK')
except KeyboardInterrupt:
	print('\n')
	avalon.warning('^C Pressed! Exiting...')
	exit(0)
except Exception as er:
	avalon.error(str(er))
	if not (args.purgelog or args.install or args.uninstall):
		log.write(str(datetime.datetime.now()) + ' -!-! ERROR !-!-\n')
		log.write(str(er) + '\n')
finally:
	if not (args.purgelog or args.install or args.uninstall):
		log.write(str(datetime.datetime.now()) + ' ---- FINISH ----\n\n')
		log.close()
