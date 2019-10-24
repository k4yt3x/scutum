#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: scutum interface class
Author: K4YT3X
Date Created: September 26, 2017
Last Modified: October 1, 2019
"""

# built-in imports
import re
import socket
import struct


class Interface:

    def __init__(self, interface: str):
        self.interface = interface

    def _get_default_gateway(self) -> str:
        """ get Linux default gateway

        Returns:
            str -- IP address of default gateway
        """
        with open('/proc/net/route') as route_file:
            for line in route_file:
                fields = line.strip().split()
                if fields[0] == self.interface:
                    if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                        continue
                    return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))

    def get_gateway_mac(self) -> str:
        """get MAC address by IP

        Arguments:
            ip {str} -- IP address to lookup

        Returns:
            str -- MAC address of IP
        """
        with open('/proc/net/arp') as arp_file:
            for line in [r for r in arp_file if r.split()[0] == self._get_default_gateway()]:
                fields = line.strip().split()
                # ip = fields[0]
                hw_address = fields[3]
                device = fields[5]

                # if the device is the one we are working on
                if device == self.interface:

                    # check if MAC address is valid
                    if re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', hw_address) is not None:
                        return hw_address
