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
Last Modified: April 17, 2018

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
from __future__ import print_function
from interface import Interface
from installer import Installer
from ufw import Ufw
import avalon_framework as avalon
import argparse
import configparser
import datetime
import os
import urllib.request
import traceback


LOGPATH = '/var/log/scutum.log'
CONFPATH = "/etc/scutum.conf"

# This is the master version number
VERSION = '2.7.0 alpha2'


# -------------------------------- Functions --------------------------------


def print_icon():
    """Print SCUTUM icon

    Credits goes to messletters.com
    """
    print(avalon.FM.BD + '     ___   __  _  _  ____  _  _  __  __' + avalon.FM.RST)
    print(avalon.FM.BD + '    / __) / _)( )( )(_  _)( )( )(  \/  )' + avalon.FM.RST)
    print(avalon.FM.BD + '    \__ \( (_  )()(   )(   )()(  )    (' + avalon.FM.RST)
    print(avalon.FM.BD + '    (___/ \__) \__/  (__)  \__/ (_/\/\_)' + avalon.FM.RST)
    print('\n               ARP Firewall')
    spaces = ((32 - len("Version " + VERSION)) // 2) * " "
    print(avalon.FM.BD + "\n" + spaces + '    Version ' + VERSION + '\n' + avalon.FM.RST)


def process_arguments():
    """This function parses all arguments

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
    control_group.add_argument("-i", "--interface", help="Run SCUTUM on specified interface", action="store", default=False)
    control_group.add_argument("--start", help="Enable SCUTUM once before shutdown", action="store_true", default=False)
    control_group.add_argument("--enable", help="Enable SCUTUM", action="store_true", default=False)
    control_group.add_argument("--disable", help="Disable SCUTUM", action="store_true", default=False)
    control_group.add_argument("--status", help="Show SCUTUM current status", action="store_true", default=False)
    control_group.add_argument("--enablegeneric", help="Enable SCUTUM generic firewall", action="store_true", default=False)
    control_group.add_argument("--disablegeneric", help="Disnable SCUTUM generic firewall", action="store_true", default=False)
    control_group.add_argument("--reset", help="Disable SCUTUM temporarily before the next connection", action="store_true", default=False)
    control_group.add_argument("--purgelog", help="Purge SCUTUM log file", action="store_true", default=False)
    inst_group = parser.add_argument_group('Installation')
    inst_group.add_argument("--install", help="Install Scutum Automatically", action="store_true", default=False)
    inst_group.add_argument("--uninstall", help="Uninstall Scutum Automatically", action="store_true", default=False)
    inst_group.add_argument("--upgrade", help="Check SCUTUM & AVALON Framework Updates", action="store_true", default=False)
    etc = parser.add_argument_group('Extra')
    etc.add_argument("--version", help="Show SCUTUM version and exit", action="store_true", default=False)
    return parser.parse_args()


def update_arptables(log):
    """operates arptables directly and
    locks gateway mac addresses

    This function creates an instance for each handled
    interface and updates it's corresponded gateway mac
    address into arptables.
    """

    # reset arptables, removing all rules and
    # accept all incoming packages
    os.system('arptables --flush')

    if args.interface:
        interface = Interface(args.interface, log)
        interface.update_gateway_addrs()
        log.write('ADAPTER={}\n'.format(interface.interface))
        log.write('GATEWAY_MAC={}\n'.format(interface.gateway_mac))
        log.write('SELF_IP={}\n'.format(interface.get_ip()))
        if interface.gateway_mac:
            os.system('arptables -P INPUT DROP')
            os.system('arptables -A INPUT --source-mac ' + interface.gateway_mac + ' -j ACCEPT')
    else:
        # Create one instance for each interface
        for interface in interfaces:
            interface = Interface(interface, log)
            ifaceobjs.append(interface)

        # make each interface update gateway mac address
        for interface in ifaceobjs:
            interface.update_gateway_addrs()
            if interface.gateway_mac or interface.get_ip():
                log.write('ADAPTER={}\n'.format(interface.interface))
                log.write('GATEWAY_MAC={}\n'.format(interface.gateway_mac))
                log.write('SELF_IP={}\n'.format(interface.get_ip()))

        for interface in ifaceobjs:
            if interface.gateway_mac:
                os.system('arptables -P INPUT DROP')
                os.system('arptables -A INPUT --source-mac ' + interface.gateway_mac + ' -j ACCEPT')


def initialize():
    """ Parses configuration
    This function parses the configuration file and
    load the configurations into the program

    TODO: Do something about KeyError
    """
    log.write('{}\n'.format(str(datetime.datetime.now())))
    if not os.path.isfile(CONFPATH):  # Configuration not found
        avalon.error('SCUTUM configuration file not found! Please re-install SCUTUM!')
        avalon.warning('Please run "scutum --install" before using it for the first time')
        raise FileNotFoundError(CONFPATH)

    # Initialize python confparser and read config
    config = configparser.ConfigParser()
    config.read(CONFPATH)

    # Read sections from the configuration file
    interfaces = config["Interfaces"]["interfaces"].split(",")
    network_controllers = config["NetworkControllers"]["controllers"]
    ufw_handled = bool(config["Ufw"]["handled"])
    return config, interfaces, network_controllers, ufw_handled


# -------------------------------- Execute --------------------------------

args = process_arguments()

if not (args.enable or args.disable):
    print_icon()

if args.version:  # prints program legal / dev / version info
    print("Current Version: " + VERSION)
    print("Author: K4YT3X")
    print("License: GNU GPL v3")
    print("Github Page: https://github.com/K4YT3X/SCUTUM")
    print("Contact: k4yt3x@protonmail.com\n")
    exit(0)
elif args.status:
    """
    Asks systemd-sysv-install if scutum is enabled
    by systemctl. May not apply to non-Debian distros
    """
    if os.system("/lib/systemd/systemd-sysv-install is-enabled scutum"):
        avalon.info("{}SCUTUM is {}{}{}\n".format(avalon.FM.RST, avalon.FG.R, "NOT ENABLED", avalon.FM.RST))
    else:
        avalon.info("{}SCUTUM is {}{}{}\n".format(avalon.FM.RST, avalon.FG.G, "ENABLED", avalon.FM.RST))
    exit(0)
elif os.getuid() != 0:  # Multiple components require root access
    avalon.error('SCUTUM must be run as root!')
    print(avalon.FG.LGR + 'It requires root privilege to operate the system' + avalon.FM.RST)
    exit(1)

exit_code = 0
log = open(LOGPATH, 'a+')
installer = Installer(CONFPATH, log=log)

if args.upgrade or args.install:
    try:
        installer.check_avalon()
        installer.check_version(VERSION)
    except urllib.error.URLError:
        pass
    if args.upgrade:
        exit(exit_code)

try:
    if not (args.purgelog or args.install or args.uninstall):
        # if program is doing normal operations, log everything
        # pointless if purging log, installing/removing
        config, interfaces, network_controllers, ufw_handled = initialize()

    if args.install:
        # Install scutum into system
        avalon.info('Starting installation procedure')
        installer.install()
        print('\n' + avalon.FM.BD, end='')
        avalon.info('Installation Complete!')
        avalon.info('SCUTUM service is now enabled on system startup')
        avalon.info('You can now control it with systemd')
        avalon.info("You can also control it manually with \"scutum\" command")
    elif args.uninstall:
        # Removes scutum completely from the system
        # Note that the configuration file will be removed too
        if avalon.ask('Removal Confirm: ', False):
            installer.remove_scutum()
        else:
            avalon.warning('Removal Canceled')
    elif args.reset:
        # resets the arptable, ufw and accept all incoming connections
        # This will expose the computer entirely on the network
        log.write('TIME={}\n'.format(str(datetime.datetime.now())))
        os.system('arptables -P INPUT ACCEPT')
        os.system('arptables --flush')
        if ufw_handled is True:
                ufwctrl = Ufw(log=log)
                ufwctrl.disable()
        avalon.info('RESETED')
        log.write('RESETED\n')
    elif args.purgelog:
        # Deletes the log file of scutum
        # TODO: delete rotated logs too
        os.system('rm {}'.format(LOGPATH))
        avalon.info('LOG PURGED')
    elif args.enable or args.disable:
        if args.enable:
            # Enable scutum will write scrips for wicd and network-manager
            # scutum will be started automatically
            if "wicd" in network_controllers.split(","):
                installer.install_wicd_scripts()
            if "NetworkManager" in network_controllers.split(","):
                installer.install_nm_scripts(config["NetworkControllers"]["controllers"].split(","))
            ifaceobjs = []  # a list to store internet controller objects
            os.system('arptables -P INPUT ACCEPT')  # Accept to get Gateway Cached

            update_arptables(log)

            if ufw_handled is True:
                # if ufw is handled by scutum, enable it
                ufwctrl = Ufw(log=log)
                ufwctrl.enable()
            avalon.info('ENABLED')
            log.write('ENABLED\n')
        elif args.disable:
            # This will disable scutum entirely and ufw too if it
            # is handled by scutum. scutum will not be started automatically
            # Firewalls will be reseted and expose the computer completely
            installer.remove_nm_scripts()
            installer.remove_wicd_scripts()
            os.system('arptables -P INPUT ACCEPT')
            os.system('arptables --flush')
            if ufw_handled is True:
                ufwctrl = Ufw(log=log)
                ufwctrl.disable()
            avalon.info('DISABLED')
            log.write('DISABLED\n')
    elif args.enablegeneric or args.disablegeneric:
        # you can choose to make scutum to handle ufw
        # after the installation
        ufwctrl = Ufw(log=log)
        if args.enablegeneric:
            ufwctrl.enable()
        elif args.disablegeneric:
            ufwctrl.disable()
    else:
        ifaceobjs = []  # a list to store internet controller objects
        os.system('arptables -P INPUT ACCEPT')  # Accept to get Gateway Cached

        update_arptables(log)

        if ufw_handled is True:
            ufwctrl = Ufw(log=log)
            ufwctrl.enable()
        avalon.info('OK')
except KeyboardInterrupt:
    avalon.warning('KeyboardInterrupt caught')
    avalon.warning('Exiting')
    exit_code = 1
    traceback.print_exc()
    traceback.print_exc(file=log)
except KeyError:
    avalon.error('The program configuration file is broken for some reason')
    avalon.error('You should reinstall SCUTUM to repair the configuration file\n')
    exit_code = 1
    traceback.print_exc()
    traceback.print_exc(file=log)
except Exception as e:
    avalon.error("SCUTUM has encountered an error")
    exit_code = 1
    traceback.print_exc()
    traceback.print_exc(file=log)
finally:
    log.write('\n')
    log.close()
    exit(exit_code)
