#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: SCUTUM Firewall
Author: K4YT3X
Date of Creation: March 8, 2017
Last Modified: May 5, 2019

Licensed under the GNU General Public License Version 3 (GNU GPL v3),
    available at: https://www.gnu.org/licenses/gpl-3.0.txt

(C) 2016-2019 K4YT3X

SCUTUM is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

SCUTUM is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Description: SCUTUM is a firewall designed for personal computers that
integrates with WICD and NetworkManager.
For tutorial please look at the GitHub Page: https://github.com/K4YT3X/scutum.
"""
from arpcontroller import ArpController
from avalon_framework import Avalon
from installer import Installer
from interface import Interface
from ufw import Ufw
import argparse
import json
import os
import subprocess
import sys
import syslog
import traceback

# master version number
VERSION = '2.10.2'


def process_arguments():
    """ This function parses all arguments

    There are three groups of arguments.

    The first group is controls group which directly controls the
    firewall.

    The second group, Installation group, controls the installation,
    uninstallation and upgrading of scutum

    The last groups, Extra, contains only a version function
    for now.
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # general firewall controls
    control_group = parser.add_argument_group('Controls')
    control_group.add_argument('-i', '--interface', help='run SCUTUM on specified interface', action='store')
    control_group.add_argument('-s', '--start', help='enable SCUTUM once before shutdown', action='store_true')
    control_group.add_argument('-r', '--reset', help='disable SCUTUM temporarily before the next connection', action='store_true')
    control_group.add_argument('-e', '--enable', help='enable SCUTUM', action='store_true')
    control_group.add_argument('-d', '--disable', help='Disable SCUTUM', action='store_true')
    control_group.add_argument('-c', '--config', help='specify config file location', action='store', default='/etc/scutum.json')
    control_group.add_argument('--status', help='show SCUTUM current status', action='store_true')
    control_group.add_argument('--enableufw', help='enable SCUTUM generic firewall', action='store_true')
    control_group.add_argument('--disableufw', help='disable SCUTUM generic firewall', action='store_true')

    # installation controls
    install_group = parser.add_argument_group('Installation')
    install_group.add_argument('--install', help='Install SCUTUM', action='store_true')
    install_group.add_argument('--uninstall', help='Uninstall SCUTUM', action='store_true')

    # extra arguments
    etc = parser.add_argument_group('Extra')
    etc.add_argument('-v', '--version', help='Show SCUTUM version and exit', action='store_true')
    return parser.parse_args()


def print_icon():
    """ print SCUTUM icon

    icon generated using messletters.com
    """
    print(f'{Avalon.FM.BD}     ___   __  _  _  ____  _  _  __  __{Avalon.FM.RST}')
    print(f'{Avalon.FM.BD}    / __) / _)( )( )(_  _)( )( )(  \/  ){Avalon.FM.RST}')
    print(f'{Avalon.FM.BD}    \__ \( (_  )()(   )(   )()(  )    ({Avalon.FM.RST}')
    print(f'{Avalon.FM.BD}    (___/ \__) \__/  (__)  \__/ (_/\/\_){Avalon.FM.RST}')
    print('\n               ARP Firewall')
    spaces = ((32 - len(f'Version {VERSION}')) // 2) * ' '
    print(f'{Avalon.FM.BD}\n{spaces}    Version {VERSION}\n{Avalon.FM.RST}')


def update_arp():
    """ Update gateway MAC address

    This function creates an instance for each handled
    interface and locks it's corresponded gateway mac
    address into nftables or arptables.
    """

    # reset arptables, removing all rules and
    # accept all incoming packages
    ac.flush_all()

    if args.interface:
        interface = Interface(args.interface)
        interface.update_gateway_addrs()
        Avalon.info(f'ADAPTER={interface.interface}', log=True)
        Avalon.info(f'GATEWAY_MAC={interface.gateway_mac}', log=True)
        Avalon.info(f'SELF_IP={interface.get_ip()}', log=True)
        if interface.gateway_mac:
            ac.block(interface.gateway_mac)
    else:
        # Create one instance for each interface
        for interface in interfaces:
            interface = Interface(interface)
            interface_objects.append(interface)

        # make each interface update gateway mac address
        for interface in interface_objects:
            interface.update_gateway_addrs()
            if interface.gateway_mac or interface.get_ip():
                Avalon.info(f'ADAPTER={interface.interface}', log=True)
                Avalon.info(f'GATEWAY_MAC={interface.gateway_mac}', log=True)
                Avalon.info(f'SELF_IP={interface.get_ip()}', log=True)

        for interface in interface_objects:
            if interface.gateway_mac:
                ac.append_allowed_mac(interface.gateway_mac)


def read_config():
    """ Parses configuration
    This function parses the configuration file and
    load the configurations into the program

    TODO: Do something about KeyError
    """
    if not os.path.isfile(args.config):  # Configuration not found
        Avalon.error('SCUTUM configuration file not found! Please re-install SCUTUM!')
        Avalon.warning('Please run \"scutum --install\" before using it for the first time')
        raise FileNotFoundError(args.config)

    # Initialize python confparser and read config
    with open(args.config, 'r') as raw_config:
        config = json.load(raw_config)

    # Get controlled interfaces
    interfaces = []
    for interface in config['Interfaces']['interfaces']:
        if os.path.isdir(f'/sys/class/net/{interface}'):
            # Check if interface is connected
            interfaces.append(interface)

    # Get controlled network controllers
    network_controllers = config['NetworkControllers']['controllers']

    # Check if we should handle ufw
    ufw_handled = config['Ufw']['handled']

    # Get ARP Controller driver
    arp_driver = config['ArpController']['driver']

    return interfaces, network_controllers, ufw_handled, arp_driver


args = process_arguments()

if not (args.enable or args.disable):
    print_icon()

# unprivileged section

# if '--version'
if args.version:  # prints program legal / dev / version info
    print(f'SCUTUM Version: {VERSION}')
    print('Author: K4YT3X')
    print('License: GNU GPL v3')
    print('Github Page: https://github.com/k4yt3x/scutum')
    print('Contact: k4yt3x@k4yt3x.com\n')
    exit(0)

# if '--status'
elif args.status:
    # asks systemd-sysv-install if scutum is enabled
    # by systemctl. May not apply to non-Debian distros
    if subprocess.run(['/lib/systemd/systemd-sysv-install', 'is-enabled', 'scutum']).returncode:
        Avalon.info(f'{Avalon.FM.RST}SCUTUM is {Avalon.FG.R}NOT ENABLED{Avalon.FM.RST}\n')
    else:
        Avalon.info(f'{Avalon.FM.RST}SCUTUM is {Avalon.FG.G}ENABLED{Avalon.FM.RST}\n')
    exit(0)

# if user not root (UID != 0)
elif os.getuid() != 0:
    # multiple components require root access
    Avalon.error('SCUTUM must be run as root')
    Avalon.error('Exiting')
    exit(1)


# privileged section

# set an exit code
exit_code = 0

try:
    # initialize installer
    installer = Installer(args.config)

    if not (args.install or args.uninstall):
        # Some objects don't need to be initialized during
        # installation or uninstallation
        interfaces, network_controllers, ufw_handled, arp_driver = read_config()

        # Initialize objects
        ac = ArpController()
        if ufw_handled:
            ufwctrl = Ufw()

    # If '--install'
    if args.install:
        # Install scutum into system
        installer.install()

    # If '--uninstall'
    elif args.uninstall:
        # Removes scutum completely from the system
        # Note that the configuration file will be removed too
        if Avalon.ask('Removal confirmation: ', False):
            installer.uninstall()
        else:
            Avalon.warning('Removal canceled')

    # If '--reset'
    elif args.reset:
        # resets the arptable, ufw and accept all incoming connections
        # This will expose the computer entirely on the network
        ac.flush_all()
        if ufw_handled is True:
            ufwctrl.disable()
        Avalon.info('RESETED')

    # If '--enable'
    elif args.enable:
        # Enable scutum will write scrips for wicd and network-manager
        # scutum will be started automatically
        if 'wicd' in network_controllers:
            installer.install_wicd_scripts()
        if 'NetworkManager' in network_controllers:
            installer.install_nm_scripts(network_controllers)

        # Lock gateway MAC on current networks
        interface_objects = []
        update_arp()

        if ufw_handled:
            ufwctrl.enable()
        Avalon.info('ENABLED')

    # If '--disable'
    elif args.disable:
        # This will disable scutum entirely and ufw too if it
        # is handled by scutum. scutum will not be started automatically
        # Firewalls will be reseted and expose the computer completely
        installer.remove_nm_scripts()
        installer.remove_wicd_scripts()
        ac.flush_all()
        if ufw_handled:
            ufwctrl.disable()
        Avalon.info('DISABLED')

    # If '--enableufw'
    elif args.enableufw:
        ufwctrl.enable()

    # If '--disableufw'
    elif args.disableufw:
        ufwctrl.disable()

    # If no arguments given
    # updates firewall status by default
    else:
        interface_objects = []  # a list to store internet controller objects
        update_arp()

        if ufw_handled:
            ufwctrl.enable()
        Avalon.info('OK')

except KeyboardInterrupt:
    Avalon.warning('KeyboardInterrupt caught')
    Avalon.warning('Exiting')
    exit_code = 1
    error_string = traceback.format_exc()
    print(error_string, file=sys.stderr)
    syslog.syslog(syslog.LOG_ERR, error_string)

except KeyError:
    Avalon.error('The configuration file is broken')
    Avalon.error('Try reinstalling SCUTUM to repair the configuration file')
    exit_code = 1
    error_string = traceback.format_exc()
    print(error_string, file=sys.stderr)
    syslog.syslog(syslog.LOG_ERR, error_string)

except Exception:
    Avalon.error('SCUTUM has encountered an error')
    exit_code = 1
    error_string = traceback.format_exc()
    print(error_string, file=sys.stderr)
    syslog.syslog(syslog.LOG_ERR, error_string)

finally:
    exit(exit_code)
