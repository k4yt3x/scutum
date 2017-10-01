#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: SCUTUM iptables Class
Author: K4YT3X
Date Created: Sep 15, 2017
Last Modified: Sep 30, 2017

Description: This class controls TCP/UDP/ICMP traffic
using ufw and iptables.

This class is migrated from Project: DefenseMatrix
"""

from installer import Installer
import avalon_framework as avalon
import ipaddress
import os
import subprocess


class Ufw:
    """
    UFW controller class

    This class handles UFW Firewall
    UFW has to be installed when an object of this class is created,
    otherwise the program will raise an exception
    """

    def __init__(self, log=False):
        """
        Keyword Arguments:
            log {object} -- object of logger (default: {False})

        Raises:
            FileNotFoundError -- raised when UFW not installed
        """
        self.log = log
        installer = Installer()
        if not os.path.isfile('/usr/sbin/ufw'):  # Detect if ufw installed
            print(avalon.FM.BD + avalon.FG.R + '\nWe have detected that you don\'t have UFW installed!' + avalon.FM.RST)
            print('UFW Firewall function requires UFW to run')
            if not installer.sysInstallPackage("ufw"):
                avalon.error("ufw is required for this function. Exiting...")
                raise FileNotFoundError("File: \"/usr/sbin/ufw\" not found")

    def initialize(self, purge=True):
        """
        Checks and adjusts the default rules of ufw which control outgoing data
        and incoming data.
        We drop all incoming data by default

        This will only be ran when scutum is being installed
        """
        if purge:
            os.system("ufw --force reset")  # Reset ufw configurations
            os.system("rm -f /etc/ufw/*.*.*")  # Delete automatic backups
        cout = subprocess.Popen(["ufw", "status", "verbose"], stdout=subprocess.PIPE).communicate()[0]
        coutparsed = cout.decode().split('\n')
        for line in coutparsed:
            if "Default:" in line:
                if not (line.split(' ')[1] + line.split(' ')[2] == "deny(incoming),"):
                    print(line.split(' ')[1] + line.split(' ')[2])
                    self.log.writeLog("Adjusting default rule for incoming packages to drop")
                    os.system("ufw default deny incoming")
                if not (line.split(' ')[3] + line.split(' ')[4] == "allow(outgoing),"):
                    line.split(' ')[3] + line.split(' ')[4]
                    self.log.writeLog("Adjusting default rule for outgoing packages to allow")
                    os.system("ufw default allow outgoing")
            if 'inactive' in line:
                self.log.writeLog("Enabling ufw")
                os.system("ufw enable")

    def enable(self):
        os.system("ufw enable")

    def disable(self):
        os.system("ufw disable")

    def allow(self, port):
        """
        Accept all traffic from one address

        Arguments:
            port {int} -- Port number
        """
        self.log.writeLog("Allowing port " + str(port))
        os.system("ufw allow " + str(port) + "/tcp")

    def expire(self, port):
        """
        Disallows all traffic from one address

        Arguments:
            port {int} -- Port number
        """
        self.log.writeLog("Expiring port " + str(port))
        os.system("ufw --force delete allow " + str(port) + "/tcp")


class Iptables:
    """
    This is the classic simple iptables firewall
    It is hard to configure/use
    """

    def __init__(self, log):
        self.log = log
        from adapter import Adapter
        self.Adapter = Adapter

    def updateIPTables(self):
        """
        Add router to iptables whitelist
        """
        if ipaddress.ip_address(self.Adapter.getIP(self)).is_private:
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
