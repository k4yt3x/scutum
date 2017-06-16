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

Description: Scutum is a firewall designed for personal computers.

For WICD and Network-Manager

For tutorial please look at the Github Page: https://github.com/K4YT3X/SCUTUM

"""
from __future__ import print_function
import argparse
import avalon_framework as avalon
import datetime
import ipaddress
import os
import socket
import struct
import subprocess
import time

LOGPATH = '/var/log/scutum.log'
VERSION = '2.0 beta'


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


def getIP():
	output = subprocess.Popen(["ifconfig"], stdout=subprocess.PIPE).communicate()[0]
	output = output.decode().split('\n')
	ips = []
	for line in output:
		if 'inet' in line:
			ips.append(line[8:].split(' ')[1])
	for ip in ips:
		if ip != '127.0.0.1' and not ipaddress.ip_address(ip).is_loopback:
			return ip
	return False


def allowRouter():
	if ipaddress.ip_address(getIP()).is_private:
		os.system('iptables -P INPUT DROP')
		os.system('iptables -P FORWARD DROP')
		os.system('iptables -P OUTPUT ACCEPT')
		os.system('iptables -A INPUT -p tcp --match multiport --dports 1025:65535 -j ACCEPT')
		os.system('iptables -A INPUT -p udp -s 208.67.222.222 -j ACCEPT')
		os.system('iptables -A INPUT -p udp -s 208.67.220.220 -j ACCEPT')
		os.system('iptables -A INPUT -m iprange --src-range 10.0.0.0-10.255.255.255 -j DROP')
		os.system('iptables -A INPUT -m iprange --src-range 172.16.0.0-172.31.255.255 -j DROP')
		os.system('iptables -A INPUT -m iprange --src-range 192.168.0.0-192.168.255.255 -j DROP')
	"""
	while True:  # Just keep trying forever until the router is found
		if getGateway() != 0:
			avalon.subLevelTimeInfo('Accepting Traffic from ' + getGateway())
			os.system('iptables -A INPUT -s ' + getGateway() + ' -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT')
			break
	"""


def iptablesReset():
	os.system('iptables -F && iptables -X')
	os.system('iptables -P INPUT ACCEPT')
	os.system('iptables -P FORWARD ACCEPT')
	os.system('iptables -P OUTPUT ACCEPT')


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

	print(avalon.FM.BD + '\nEnable SCUTUM iptables firewall?' + avalon.FM.RST)
	print('This firewall uses linux iptables to establish a relatively secure environment')
	print('However, professional firewall softwares like ufw is recommended')
	print('Enable this only if you don\'t have a firewall already')
	avalon.warning('This feature will erase all existing iptables settings!')
	if avalon.ask('Enable?', False):
		with open('/etc/scutum.conf', 'w') as scutum_config:
			scutum_config.write('[SCUTUM CONFIG]\n')
			scutum_config.write('firewall=true\n')
		scutum_config.close()
	else:
		with open('/etc/scutum.conf', 'w') as scutum_config:
			scutum_config.write('[SCUTUM CONFIG]\n')
			scutum_config.write('firewall=false\n')
		scutum_config.close()


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
		if not os.path.isfile('/etc/scutum.conf'):
			avalon.error('SCUTUM Config file not found! Please re-install SCUTUM!')
			avalon.warning('Please run "scutum --install" before using it for the first time')
			exit()
		with open('/etc/scutum.conf', 'r') as scutum_config:
			for line in scutum_config:
				if 'firewall' in line and 'true' in line:
					iptablesEnabled = True
				elif 'firewall' in line and 'false' in line:
					iptablesEnabled = False
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

		if iptablesEnabled:
			iptablesReset()
			allowRouter()
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
