#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: SCUTUM Adapter Class
Author: K4YT3X
Date Created: Sep 26, 2017
Last Modified: Oct 8, 2017

Description: This class controls all system configuring activities
ex. set arptables, set iptables, etc.

Version 1.1
"""

from installer import Installer
import avalon_framework as avalon
import datetime
import os
import socket
import struct
import subprocess
import time


class Adapter:
    """
    The Adapter class handles the arp firewall
    This is the core part of this program (maybe, in some ways)
    """

    def __init__(self, interface, log=False):
        """
        Arguments:
            interface {string} -- name of interface to handle
            log {object} -- object of logger (default: {False})

        Raises:
            FileNotFoundError -- raised when arptables not installed
        """
        self.log = log
        self.gatewayMac = False
        if log is False:
            from logger import Logger
            self.log = Logger()
        self.interface = interface
        installer = Installer()
        if not os.path.isfile('/usr/bin/arptables') and not os.path.isfile('/sbin/arptables'):  # Detect if arptables installed
            print(avalon.FM.BD + avalon.FG.R + '\nWe have detected that you don\'t have arptables installed!' + avalon.FM.RST)
            print('SCUTUM requires arptables to run')
            if not installer.sysInstallPackage("arptables"):
                avalon.error("arptables is required for scutum. Exiting...")
                raise FileNotFoundError("File: \"/usr/bin/arptables\" and \"/sbin/arptables\" not found")

    def getGateway(self):
        """Get Linux Default Gateway"""
        with open("/proc/net/route") as fh:
            for line in fh:
                if self.interface in line:
                    fields = line.strip().split()
                    if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                        continue
                    return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))
        return 0

    def getGatewayMac(self):
        """Get Gateway Mac Address"""
        with open('/proc/net/arp') as arpf:
            for line in arpf:
                if line.split(' ')[0] == Adapter.getGateway(self) and self.interface in line:
                    for field in line.split(' '):
                        if len(field) == 17 and ':' in field:
                            return field
        return 0

    def getIP(self):
        """
        Returns the IP address for current machine
        More accurate than socket, but only works when there's only one interface
        Might be improved or removed in future
        """
        output = subprocess.Popen(["ifconfig"], stdout=subprocess.PIPE).communicate()[0]
        iface_splited = output.decode().split('\n\n')
        for line in iface_splited:
            if line.split(':')[0] == self.interface:
                for section in line.split('\n'):
                    if 'inet ' in section:
                        ipv4_address = section.split('inet ')[1].split(' ')[0]
                    """ In case needed in the future
                    if 'inet6 ' in section:
                        ipv6_address = section.split('inet6 ')[1].split(' ')[0]
                    if 'ether ' in section:
                        mac_address = section.split('ether ')[1].split(' ')[0]
                    """
                if ipv4_address:
                    return ipv4_address
        return False

    def isUp(self):
        with open("/sys/class/net/{}/operstate".format(self.interface), "r") as state:
            for line in state:
                if "up" in line.lower():
                    return True
        return False

    def updateGatewayAddrs(self):
        """
        This function adds the gateway's mac address into
        arptable's whitelist
        """
        if not self.isUp():
            return
        while True:  # Wait Until Gateway ARP is cached
            self.gatewayMac = str(Adapter.getGatewayMac(self))
            # os.system('nslookup google.ca')  # Works as well as the following
            try:
                ac = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ac.settimeout(0)
                # Connect to gateway to cache gateway MAC
                ac.connect((Adapter.getGateway(self), 0))
                ac.close()
            except Exception:
                pass
            # Check if it's a valid MAC Address
            if self.gatewayMac != '00:00:00:00:00:00' and len(self.gatewayMac) == 17:
                break
            time.sleep(0.5)  # Be nice to CPU
        self.log.writeLog(str(datetime.datetime.now()) + '  MAC: ' + self.gatewayMac)
        self.log.writeLog(str(datetime.datetime.now()) + '  IP: ' + str(Adapter.getIP(self)))
