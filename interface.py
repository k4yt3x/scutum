#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: SCUTUM Interface Class
Author: K4YT3X
Date Created: Sep 26, 2017
Last Modified: April 17, 2018

Description: This class controls all system configuring activities
ex. set arptables, set iptables, etc.

Version 1.2
"""

from installer import Installer
import avalon_framework as avalon
import os
import re
import socket
import struct
import subprocess
import time


class Interface:
    """
    The Interface class handles the arp firewall
    This is the core part of this program (maybe, in some ways)
    """

    def __init__(self, adapter, log):
        """
        Arguments:
            adapter {string} -- name of adapter to handle
            log {object} -- object of logger (default: {False})

        Raises:
            FileNotFoundError -- raised when arptables not installed
        """
        self.gateway_mac = False
        self.interface = adapter
        installer = Installer()
        if not os.path.isfile('/usr/bin/arptables') and not os.path.isfile('/sbin/arptables'):  # Detect if arptables installed
            print(avalon.FM.BD + avalon.FG.R + '\nWe have detected that you don\'t have arptables installed!' + avalon.FM.RST)
            print('SCUTUM requires arptables to run')
            if not installer.sysInstallPackage('arptables'):
                avalon.error('arptables is required for scutum. Exiting...')
                raise FileNotFoundError('File: \"/usr/bin/arptables\" and \"/sbin/arptables\" not found')

    def get_gateway(self):
        """Get Linux Default Gateway"""
        with open('/proc/net/route') as fh:
            for line in fh:
                if self.interface in line:
                    fields = line.strip().split()
                    if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                        continue
                    return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))
        return 0

    def get_gateway_mac(self):
        """Get Gateway Mac Address"""
        with open('/proc/net/arp') as arpf:
            for line in arpf:
                if line.split(' ')[0] == self.get_gateway() and self.interface in line:
                    for field in line.split(' '):
                        if len(field) == 17 and ':' in field:
                            return field
        return 0

    def get_ip(self):
        """
        Returns the IP address for current machine
        More accurate than socket, but only works when there's only one interface
        Might be improved or removed in future
        """
        ip = re.compile('(([2][5][0-5]\.)|([2][0-4][0-9]\.)|([0-1]?[0-9]?[0-9]\.)){3}' +
                        '(([2][5][0-5])|([2][0-4][0-9])|([0-1]?[0-9]?[0-9]))')
        output = subprocess.Popen(['ip', 'addr', 'show', self.interface], stdout=subprocess.PIPE).communicate()[0]
        ipv4 = ip.search(output.decode())
        if ipv4:
            return ipv4.group()
        else:
            return False

    def is_up(self):
        # Determine if interface is up
        with open('/sys/class/net/{}/operstate'.format(self.interface), "r") as state:
            for line in state:
                if 'up' in line.lower():
                    return True
        return False

    def update_gateway_addrs(self):
        """
        This function adds the gateway's mac address into
        arptable's whitelist
        """
        if not self.is_up():
            return
        while True:  # Wait Until Gateway ARP is cached
            self.gateway_mac = str(self.get_gateway_mac())
            # os.system('nslookup google.ca')  # Works as well as the following
            try:
                ac = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ac.settimeout(0)
                # Connect to gateway to cache gateway MAC
                ac.connect((self.get_gateway(), 0))
                ac.close()
            except Exception:
                pass
            # Check if it's a valid MAC Address
            if self.gateway_mac != '00:00:00:00:00:00' and len(self.gateway_mac) == 17:
                break
            time.sleep(0.5)  # Be nice to CPU
