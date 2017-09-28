#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: SCUTUM Adapter Class
Author: K4YT3X
Date Created: Sep 26, 2017
Last Modified: Sep 27, 2017

Description: This class controls all system configuring activities
ex. set arptables, set iptables, etc.
"""
import datetime
import ipaddress
import os
import socket
import struct
import subprocess
import time


class Adapter:

    def __init__(self, interface, log):
        self.interface = interface
        self.log = log

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

    def updateIPTables(self):
        """
        Add router to iptables whitelist
        """
        if ipaddress.ip_address(Adapter.getIP(self)).is_private:
            os.system('iptables -P INPUT DROP')
            os.system('iptables -P FORWARD DROP')
            os.system('iptables -P OUTPUT ACCEPT')
            os.system('iptables -A INPUT -p tcp --match multiport --dports 1025:65535 -j ACCEPT')
            with open('/etc/resolv.conf', 'r') as resolv:
                dnsServers = []
                for line in resolv:
                    if 'nameserver' in line:
                        for element in line.replace('\n', '').split(' '):
                            try:
                                if ipaddress.ip_address(element):
                                    dnsServers.append(element)
                            except ValueError:
                                pass
            for address in dnsServers:  # Accept all DNS within /etc/resolv.conf
                os.system('iptables -A INPUT -p udp -s ' + address + ' -j ACCEPT')
            # os.system('iptables -A INPUT -p udp -s 208.67.222.222 -j ACCEPT')
            # os.system('iptables -A INPUT -p udp -s 208.67.220.220 -j ACCEPT')
            os.system('iptables -A INPUT -m iprange --src-range 10.0.0.0-10.255.255.255 -j DROP')
            os.system('iptables -A INPUT -m iprange --src-range 172.16.0.0-172.31.255.255 -j DROP')
            os.system('iptables -A INPUT -m iprange --src-range 192.168.0.0-192.168.255.255 -j DROP')
        """  # this part adds gateway into iptables whitelist, might not be necessary
        while True:  # Just keep trying forever until the router is found
            if getGateway() != 0:
                avalon.subLevelTimeInfo('Accepting Traffic from ' + getGateway())
                os.system('iptables -A INPUT -s ' + getGateway() + ' -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT')
                break
        """

    def iptablesReset(self):
        """
        Flush everything in iptables completely
        This function will reset iptables and flush all custom settings
        """
        os.system('iptables -F && iptables -X')
        os.system('iptables -P INPUT ACCEPT')
        os.system('iptables -P FORWARD ACCEPT')
        os.system('iptables -P OUTPUT ACCEPT')

    def updateArpTables(self):
        """
        This function adds the gateway's mac address into
        arptable's whitelist
        """
        while True:  # Wait Until Gateway ARP is cached
            gatewayMac = str(Adapter.getGatewayMac(self))
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
            if gatewayMac != '00:00:00:00:00:00' and len(gatewayMac) == 17:
                break
            time.sleep(0.5)  # Be nice to CPU
        self.log.write(str(datetime.datetime.now()) + '  MAC: ' + gatewayMac + '\n')
        self.log.write(str(datetime.datetime.now()) + '  IP: ' + str(Adapter.getIP(self)) + '\n')
        os.system('arptables --flush')
        os.system('arptables -P INPUT DROP')
        os.system('arptables -A INPUT --source-mac ' + gatewayMac + ' -j ACCEPT')
