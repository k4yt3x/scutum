#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: SCUTUM ufw Class
Author: K4YT3X
Date Created: Sep 15, 2017
Last Modified: April 22, 2019

Description: This class controls TCP/UDP/ICMP traffic
using ufw.
"""
from avalon_framework import Avalon
from utilities import Utilities
import shutil


class Ufw:
    """
    UFW controller class

    This class handles UFW Firewall
    UFW has to be installed when an object of this class is created,
    otherwise the program will raise an exception
    """

    def __init__(self):
        """
        Keyword Arguments:
            log {object} -- object of logger (default: {False})

        Raises:
            FileNotFoundError -- raised when UFW not installed
        """

        if shutil.which('ufw') is None:  # Detect if ufw installed
            print(Avalon.FM.BD + Avalon.FG.R + '\nWe have detected that you don\'t have UFW installed!' + Avalon.FM.RST)
            print('UFW Firewall function requires UFW to run')
            if not Utilities.install_package('ufw'):
                Avalon.error('ufw is required for this function. Exiting...')
                raise FileNotFoundError('File: \"/usr/sbin/ufw\" not found')

    def initialize(self, purge=True):
        """
        Checks and adjusts the default rules of ufw which control outgoing data
        and incoming data.
        We drop all incoming data by default

        This will only be ran when scutum is being installed
        """
        if purge:
            Utilities.execute(['ufw', '--force', 'reset'])  # Reset ufw configurations
            Utilities.execute(['rm', '-f', '/etc/ufw/*.*.*'])  # Delete automatic backups

        coutparsed = Utilities.execute(['ufw', 'status', 'verbose'])
        for line in coutparsed:
            if 'Default:' in line:
                if not (line.split(' ')[1] + line.split(' ')[2] == 'deny(incoming),'):
                    print(line.split(' ')[1] + line.split(' ')[2])
                    Avalon.info('[UFW]: Adjusting default rule for incoming packages to drop\n')
                    Utilities.execute(['ufw', 'default', 'deny', 'incoming'])
                if not (line.split(' ')[3] + line.split(' ')[4] == 'allow(outgoing),'):
                    line.split(' ')[3] + line.split(' ')[4]
                    Avalon.info('[UFW]: Adjusting default rule for outgoing packages to allow\n')
                    Utilities.execute(['ufw', 'default', 'allow', 'outgoing'])
            if 'inactive' in line:
                Avalon.info('[UFW]: Enabling ufw\n')
                Utilities.execute(['ufw', 'enable'])

    def enable(self):
        Utilities.execute(['ufw', '--force', 'enable'])

    def disable(self):
        Utilities.execute(['ufw', '--force', 'disable'])

    def allow(self, port):
        """
        Accept all traffic from one address

        Arguments:
            port {int} -- Port number
        """
        Avalon.info(f'[UFW]: Allowing port {str(port)}\n\n')
        Utilities.execute(['ufw', 'allow', f'{str(port)}/tcp'])

    def expire(self, port):
        """
        Disallows all traffic from one address

        Arguments:
            port {int} -- Port number
        """
        Avalon.info(f'[UFW]: Expiring port {str(port)}\n\n')
        Utilities.execute(['ufw', '--force', 'delete', 'allow', f'{str(port)}/tcp'])
