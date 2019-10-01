#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: scutum firewall
Author: K4YT3X
Date of Creation: March 8, 2017
Last Modified: September 23, 2019

Licensed under the GNU General Public License Version 3 (GNU GPL v3),
    available at: https://www.gnu.org/licenses/gpl-3.0.txt

(C) 2016-2019 K4YT3X

scutum is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

scutum is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Description: scutum is a light-weight utility that can block all ARP packets
besides the ones coming from the gateway. It can also help you to setup
your netfilter/iptables firewall using UFW.
"""

# built-in imports
import argparse
import socket
import struct

# third-party imports
from avalon_framework import Avalon

# local imports
from arp import Arp
from ufw import Ufw

# master version number
VERSION = '3.0.0'


def process_arguments() -> argparse.Namespace:
    """ parse arguments

    Returns:
        argparse.Namespace -- namespace for parsed arguments
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # general firewall controls
    control_group = parser.add_argument_group('Firewall Controls')
    control_group.add_argument('-r', '--reset', help='allow all traffic', action='store_true')

    # miscellaneous arguments
    misc_group = parser.add_argument_group('Miscellaneous')
    misc_group.add_argument('-v', '--version', help='Show scutum version and exit', action='store_true')
    return parser.parse_args()


def print_icon():
    """ print scutum icon
    """
    scutum_icon = f'''{Avalon.FM.BD}
     ___   __  _  _  ____  _  _  __  __
    / __) / _)( )( )(_  _)( )( )(  \/  )
    \__ \( (_  )()(   )(   )()(  )    (
    (___/ \__) \__/  (__)  \__/ (_/\/\_){Avalon.FM.RST}\n'''

    print(scutum_icon)
    print(f'{"ARP Firewall":^44}')
    print(f'{Avalon.FM.BD}{f"Version {VERSION}":^44}{Avalon.FM.RST}\n')


def get_default_gateway() -> str:
    """ get Linux default gateway

    Returns:
        str -- IP address of default gateway
    """
    with open('/proc/net/route') as route_file:
        for line in route_file:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                continue
            return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))


def get_mac_by_ip(ip: str) -> str:
    """get MAC address by IP

    Arguments:
        ip {str} -- IP address to lookup

    Returns:
        str -- MAC address of IP
    """
    with open('/proc/net/arp') as arp_file:
        for line in [r for r in arp_file if r.split()[0] == ip]:
            for field in line.strip().split():
                if len(field) == 17 and ':' in field:
                    return field


# this is not a library
if __name__ != '__main__':
    raise ImportError('this file cannot be imported')

# print scutum icon
print_icon()

# process command line arguments
args = process_arguments()

# -v, --version
if args.version:  # prints program legal / dev / version info
    print(f'SCUTUM Version: {VERSION}')
    print('Author: K4YT3X')
    print('License: GNU GPL v3')
    print('Github Page: https://github.com/k4yt3x/scutum')
    print('Contact: k4yt3x@k4yt3x.com\n')
    exit(0)

# initialize ARP controller
arp = Arp()

# initialize UFW controller
ufw = Ufw()

# -r, --reset
if args.reset:
    arp.reset()
    ufw.disable()

# default action without arguments
else:
    default_gateway_ip = get_default_gateway()
    default_gateway_mac = get_mac_by_ip(default_gateway_ip)
    arp.allow_mac(default_gateway_mac)
    ufw.enable()
