#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: SCUTUM ufw Class
Author: K4YT3X
Date Created: Sep 15, 2017
Last Modified: April 25, 2018

Description: This class controls TCP/UDP/ICMP traffic
using ufw.

Version 1.4.1
"""

import avalon_framework as avalon
import datetime
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

        if not os.path.isfile('/usr/sbin/ufw'):  # Detect if ufw installed
            print(avalon.FM.BD + avalon.FG.R + '\nWe have detected that you don\'t have UFW installed!' + avalon.FM.RST)
            print('UFW Firewall function requires UFW to run')
            if not self.sysInstallPackage("ufw"):
                avalon.error("ufw is required for this function. Exiting...")
                raise FileNotFoundError("File: \"/usr/sbin/ufw\" not found")

    def sysInstallPackage(self, package):
        if avalon.ask('Install ' + package + '?', True):
            if os.path.isfile('/usr/bin/apt'):
                os.system('apt update && apt install ' + package + ' -y')  # install arptables with apt
                return True
            elif os.path.isfile('/usr/bin/yum'):
                os.system('yum install ' + package + ' -y')  # install arptables with yum
                return True
            elif os.path.isfile('/usr/bin/pacman'):
                os.system('pacman -S ' + package + ' --noconfirm')  # install arptables with pacman
                return True
            else:
                avalon.error('Sorry, we can\'t find a package manager that we currently support. Aborting..')
                print('Currently Supported: apt, yum, pacman')
                print('Please come to SCUTUM\'s github page and comment if you know how to add support to another package manager')
                return False
        else:
            return False

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
                    self.log.write("[UFW]: Adjusting default rule for incoming packages to drop\n")
                    os.system("ufw default deny incoming")
                if not (line.split(' ')[3] + line.split(' ')[4] == "allow(outgoing),"):
                    line.split(' ')[3] + line.split(' ')[4]
                    self.log.write("[UFW]: Adjusting default rule for outgoing packages to allow\n")
                    os.system("ufw default allow outgoing")
            if 'inactive' in line:
                self.log.write("[UFW]: Enabling ufw\n")
                os.system("ufw enable")

    def enable(self):
        os.system("ufw --force enable")

    def disable(self):
        os.system("ufw --force disable")

    def allow(self, port):
        """
        Accept all traffic from one address

        Arguments:
            port {int} -- Port number
        """
        self.log.write('{}\n'.format(str(datetime.datetime.now())))
        self.log.write("[UFW]: Allowing port {}\n\n".format(str(port)))
        os.system("ufw allow {}/tcp".format(str(port)))

    def expire(self, port):
        """
        Disallows all traffic from one address

        Arguments:
            port {int} -- Port number
        """
        self.log.write('{}\n'.format(str(datetime.datetime.now())))
        self.log.write("[UFW]: Expiring port {}\n\n".format(str(port)))
        os.system("ufw --force delete allow {}/tcp".format(str(port)))
