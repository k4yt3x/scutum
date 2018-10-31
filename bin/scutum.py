#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    ╬##################╬
    ##       ##       ##
    ##  #    ##    #  ##
    ##  #    ##    #  ##
    ##  #    ##    #  ##
    ##   #   ##   #   ##
    ##    ## ## ##    ##     ___   __  _  _  ____  _  _  __  __
    ##      ####      ##    / __) / _)( )( )(_  _)( )( )(  \/  )
    ####################    \__ \( (_  )()(   )(   )()(  )    (
    ##      ####      ##    (___/ \__) \__/  (__)  \__/ (_/\/\_)
    ##    ## ## ##    ##
    ##   #   ##   #   ##               ARP Firewall
    ##  #    ##    #  ##
    ##  #    ##    #  ##
    ##  #    ##    #  ##
    ##       ##       ##
    ╬##################╬


Name: SCUTUM Firewall
Author: K4YT3X
Date of Creation: March 8, 2017
Last Modified: October 31, 2018

Licensed under the GNU General Public License Version 3 (GNU GPL v3),
    available at: https://www.gnu.org/licenses/gpl-3.0.txt

(C) 2016 - 2018 K4YT3X

Description: SCUTUM is a firewall designed for personal computers that mainly
focuses on ARP defensing

For WICD and Network-Manager

For tutorial please look at the Github Page: https://github.com/K4YT3X/SCUTUM


KNOWN ISSUES:
1. If the service is started manually when connecting to
a network, the command will hang until the Internet is connected
(when an IP address is assigned, when gateway address is defined)

"""
from arpcontroller import ArpController
from avalon_framework import Avalon
from installer import Installer
from interface import Interface
from ufw import Ufw
from utilities import Utilities
import argparse
import json
import os
import sys
import syslog
import traceback

CONFPATH = '/etc/scutum.json'

# This is the master version number
VERSION = '2.10.0'


# -------------------------------- Functions

def print_icon():
    """ Print SCUTUM icon

    Credits goes to messletters.com
    """
    print(Avalon.FM.BD + '     ___   __  _  _  ____  _  _  __  __' + Avalon.FM.RST)
    print(Avalon.FM.BD + '    / __) / _)( )( )(_  _)( )( )(  \/  )' + Avalon.FM.RST)
    print(Avalon.FM.BD + '    \__ \( (_  )()(   )(   )()(  )    (' + Avalon.FM.RST)
    print(Avalon.FM.BD + '    (___/ \__) \__/  (__)  \__/ (_/\/\_)' + Avalon.FM.RST)
    print('\n               ARP Firewall')
    spaces = ((32 - len('Version ' + VERSION)) // 2) * ' '
    print(Avalon.FM.BD + '\n' + spaces + '    Version ' + VERSION + '\n' + Avalon.FM.RST)


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
    parser = argparse.ArgumentParser()
    control_group = parser.add_argument_group('Controls')
    control_group.add_argument('-i', '--interface', help='Run SCUTUM on specified interface', action='store', default=False)
    control_group.add_argument('--start', help='Enable SCUTUM once before shutdown', action='store_true', default=False)
    control_group.add_argument('--enable', help='Enable SCUTUM', action='store_true', default=False)
    control_group.add_argument('--disable', help='Disable SCUTUM', action='store_true', default=False)
    control_group.add_argument('--status', help='Show SCUTUM current status', action='store_true', default=False)
    control_group.add_argument('--enableufw', help='Enable SCUTUM generic firewall', action='store_true', default=False)
    control_group.add_argument('--disableufw', help='Disnable SCUTUM generic firewall', action='store_true', default=False)
    control_group.add_argument('--reset', help='Disable SCUTUM temporarily before the next connection', action='store_true', default=False)
    inst_group = parser.add_argument_group('Installation')
    inst_group.add_argument('--install', help='Install Scutum Automatically', action='store_true', default=False)
    inst_group.add_argument('--uninstall', help='Uninstall Scutum Automatically', action='store_true', default=False)
    etc = parser.add_argument_group('Extra')
    etc.add_argument('--version', help='Show SCUTUM version and exit', action='store_true', default=False)
    return parser.parse_args()


def update_arp():
    """ Operates arptables directly and
    locks gateway mac addresses

    This function creates an instance for each handled
    interface and updates it's corresponded gateway mac
    address into arptables.
    """

    # reset arptables, removing all rules and
    # accept all incoming packages
    ac.flush_all()

    if args.interface:
        interface = Interface(args.interface)
        interface.update_gateway_addrs()
        Avalon.info('ADAPTER={}'.format(interface.interface), log=True)
        Avalon.info('GATEWAY_MAC={}'.format(interface.gateway_mac), log=True)
        Avalon.info('SELF_IP={}'.format(interface.get_ip()), log=True)
        if interface.gateway_mac:
            ac.block(interface.gateway_mac)
    else:
        # Create one instance for each interface
        for interface in interfaces:
            interface = Interface(interface)
            ifaceobjs.append(interface)

        # make each interface update gateway mac address
        for interface in ifaceobjs:
            interface.update_gateway_addrs()
            if interface.gateway_mac or interface.get_ip():
                Avalon.info('ADAPTER={}'.format(interface.interface), log=True)
                Avalon.info('GATEWAY_MAC={}'.format(interface.gateway_mac), log=True)
                Avalon.info('SELF_IP={}'.format(interface.get_ip()), log=True)

        for interface in ifaceobjs:
            if interface.gateway_mac:
                ac.append_allowed_mac(interface.gateway_mac)


def read_config():
    """ Parses configuration
    This function parses the configuration file and
    load the configurations into the program

    TODO: Do something about KeyError
    """
    if not os.path.isfile(CONFPATH):  # Configuration not found
        Avalon.error('SCUTUM configuration file not found! Please re-install SCUTUM!')
        Avalon.warning('Please run \"scutum --install\" before using it for the first time')
        raise FileNotFoundError(CONFPATH)

    # Initialize python confparser and read config
    with open(CONFPATH, 'r') as raw_config:
        config = json.load(raw_config)

    # Get controlled interfaces
    interfaces = []
    for interface in config['Interfaces']['interfaces']:
        if os.path.isdir('/sys/class/net/{}'.format(interface)):
            # Check if interface is connected
            interfaces.append(interface)

    # Get controlled network controllers
    network_controllers = config['NetworkControllers']['controllers']

    # Check if we should handle ufw
    ufw_handled = bool(config['Ufw']['handled'])

    # Get ARP Controller driver
    arp_driver = config['ArpController']['driver']

    return interfaces, network_controllers, ufw_handled, arp_driver


# -------------------------------- Execute

args = process_arguments()

if not (args.enable or args.disable):
    print_icon()

# Unprivileged Section
if args.version:  # prints program legal / dev / version info
    print('Current Version: {}'.format(VERSION))
    print('Author: K4YT3X')
    print('License: GNU GPL v3')
    print('Github Page: https://github.com/K4YT3X/scutum')
    print('Contact: k4yt3x@k4yt3x.com\n')
    exit(0)
elif args.status:
    # Asks systemd-sysv-install if scutum is enabled
    # by systemctl. May not apply to non-Debian distros
    if Utilities.execute(['/lib/systemd/systemd-sysv-install', 'is-enabled', 'scutum']):
        Avalon.info('{}SCUTUM is {}{}{}\n'.format(Avalon.FM.RST, Avalon.FG.R, 'NOT ENABLED', Avalon.FM.RST))
    else:
        Avalon.info('{}SCUTUM is {}{}{}\n'.format(Avalon.FM.RST, Avalon.FG.G, 'ENABLED', Avalon.FM.RST))
    exit(0)
elif os.getuid() != 0:
    # Multiple components require root access
    Avalon.error('SCUTUM must be run as root')
    Avalon.error('Exiting')
    exit(1)

# Set an exit code
exit_code = 0

# Privileged Section
try:
    if not (args.install or args.uninstall):
        # if program is doing normal operations, log everything
        # pointless if purging log, installing/removing
        interfaces, network_controllers, ufw_handled, arp_driver = read_config()

        # Initialize objects
        installer = Installer(CONFPATH)
        ac = ArpController()
        if ufw_handled:
            ufwctrl = Ufw()

    if args.install:
        # Install scutum into system
        Avalon.info('Starting installation procedure')
        installer.install()
        print('\n' + Avalon.FM.BD, end='')
        Avalon.info('Installation completed')
        Avalon.info('SCUTUM service is now enabled on system startup')
        Avalon.info('You can now control it with systemd')
        Avalon.info('You can also control it manually with \"scutum\" command')
    elif args.uninstall:
        # Removes scutum completely from the system
        # Note that the configuration file will be removed too
        if Avalon.ask('Removal confirmation: ', False):
            installer.uninstall()
        else:
            Avalon.warning('Removal canceled')
    elif args.reset:
        # resets the arptable, ufw and accept all incoming connections
        # This will expose the computer entirely on the network
        ac.flush_all()
        if ufw_handled is True:
            ufwctrl.disable()
        Avalon.info('RESETED')
    elif args.enable or args.disable:
        if args.enable:
            # Enable scutum will write scrips for wicd and network-manager
            # scutum will be started automatically
            if 'wicd' in network_controllers:
                installer.install_wicd_scripts()
            if 'NetworkManager' in network_controllers:
                installer.install_nm_scripts(network_controllers)
            ifaceobjs = []  # a list to store internet controller objects
            ac.flush_all()  # Accept to get Gateway Cached

            if ufw_handled:
                # if ufw is handled by scutum, enable it
                ufwctrl.enable()
            Avalon.info('ENABLED')
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
    elif args.enableufw or args.disableufw:
        # you can choose to make scutum to handle ufw
        # after the installation
        if args.enableufw:
            ufwctrl.enable()
        elif args.disableufw:
            ufwctrl.disable()
    else:
        ifaceobjs = []  # a list to store internet controller objects
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
    Avalon.error('The program configuration file is broken for some reason')
    Avalon.error('You should reinstall SCUTUM to repair the configuration file\n')
    exit_code = 1
    error_string = traceback.format_exc()
    print(error_string, file=sys.stderr)
    syslog.syslog(syslog.LOG_ERR, error_string)
except Exception as e:
    Avalon.error('SCUTUM has encountered an error')
    exit_code = 1
    error_string = traceback.format_exc()
    print(error_string, file=sys.stderr)
    syslog.syslog(syslog.LOG_ERR, error_string)
finally:
    exit(exit_code)
