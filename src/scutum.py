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
import pathlib
import contextlib
import os

# third-party imports
from avalon_framework import Avalon

# local imports
from arp import Arp
from ufw import Ufw
from interface import Interface

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
    control_group.add_argument('-i', '--interface', help='update the specified interface', action='store')

    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument('-u', '--update', help='update ARP blocking rules', action='store_true')
    action_group.add_argument('-r', '--reset', help='discard ARP blocking rules', action='store_true')

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


def list_active_interfaces() -> list:
    active_interfaces = []

    # Linux virtual interface status files directory
    sys_class_net = pathlib.Path('/sys/class/net')

    for interface in sys_class_net.iterdir():
        operstate = open(interface / 'operstate', 'r').readlines()[0].strip('\n')
        interface_type = open(interface / 'type', 'r').readlines()[0].strip('\n')
        if interface_type == '1' and operstate == 'up':
            active_interfaces.append(interface.name)

    return active_interfaces


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

# check user privilege
if os.getuid() != 0:
    Avalon.error('Root privilege is required')
    raise PermissionError('insufficient privilege')

# initialize ARP controller
arp = Arp()

# initialize UFW controller
ufw = Ufw()


# if an interface name is specified
# perform action only on the specified interface
if args.interface:

    if args.update:
        interface_object = Interface(args.interface)
        gateway_mac = interface_object.get_gateway_mac()
        arp.allow_mac(gateway_mac, args.interface)
        ufw.enable()

    elif args.reset:
        arp.discard_interface_rules(args.interface)

# if no interface is specified
# perform action all interfaces
else:

    # if -u, --update
    if args.update:

        interfaces = list_active_interfaces()

        Avalon.debug_info(f'Active interfaces: {" ".join(interfaces)}')

        for interface in interfaces:
            interface_object = Interface(interface)
            gateway_mac = interface_object.get_gateway_mac()
            arp.allow_mac(gateway_mac, interface)

        ufw.enable()

    # if -r, --reset
    elif args.reset:
        arp.reset()
        ufw.disable()
