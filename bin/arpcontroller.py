#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: SCUTUM ARP Controller
Author: K4YT3X
Date Created: October 31, 2018
Last Modified: October 31, 2018

Description: This class controls all ARP
related operations.

Version 1.0.1
"""
from avalon_framework import Avalon
from utilities import Utilities


class ArpController():
    """ ARP Controller for SCUTUM

    This class controls all the operations that are
    related to ARP, such as blocking and allowing.
    """

    def __init__(self, driver='nftables'):

        self.driver = driver

        if self.driver != 'nftables' and self.driver != 'arptables':
            Avalon.warning('Unrecognized ARP controller driver {}'.format(self.driver))
            Avalon.warning('Falling back to nftables')
            self.driver = 'nftables'

    def append_allowed_mac(self, mac_address, interface=False):
        """ Allow the traffic from this MAC address

        This will drop all traffic that is not from this address.
        """
        if self.driver == 'arptables':
            # Allow only this MAC address globally
            Utilities.execute(['arptables', '-P', 'INPUT', 'DROP'])
            Utilities.execute(['arptables', '-A', 'INPUT', '--source-mac', mac_address, '-j', 'ACCEPT'])
        elif interface:
            # If an interface is provided, limit rule to interface
            Utilities.execute(['nft', 'add', 'rule', 'inet', 'filter', 'input', 'iif', interface, 'ether', 'saddr', '!=', mac_address, 'drop'])
        else:
            # If no interface specified, allow only this MAC globally
            Utilities.execute(['nft', 'add', 'rule', 'inet', 'filter', 'input', 'ether', 'saddr', '!=', mac_address, 'drop'])

    def flush_all(self):
        """ Accept all incoming connections

        Accept all incoming connections by flushing the
        inet input chain. This will allow any address to
        talk to our host.
        """
        if self.driver == 'arptables':
            Utilities.execute(['arptables', '-P', 'INPUT', 'ACCEPT'])
            Utilities.execute(['arptables', '--flush'])
        else:
            Utilities.execute(['nft', 'flush', 'chain', 'inet', 'filter', 'input'])
