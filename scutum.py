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
Date of Creation: March 8,2017
Last Modified: Mar 10, 2018

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
from adapter import Adapter
from installer import Installer
from iptables import Ufw
from logger import Logger
import argparse
import configparser
import datetime
import os
import traceback
import urllib.request

try:
    import avalon_framework as avalon
except ImportError:
    while True:
        install = input('\033[31m\033[1mAVALON Framework not installed! Install now? [Y/n] \033[0m')
        if len(install) == 0 or install[0].upper() == 'Y':
            try:
                if os.path.isfile('/usr/bin/pip3'):
                    # Try installing with installed pip
                    print('Installing using method 1')
                    os.system('pip3 install avalon_framework')
                elif os.path.isfile('/usr/bin/wget'):
                    # Try downloading pip from bootstrap and install avalon
                    # framework
                    print('Installing using method 2')
                    os.system('wget -O - https://bootstrap.pypa.io/get-pip.py | python3')
                    os.system('pip3 install avalon_framework')
                else:
                    # download script with urllib.request if wget is not present
                    print('Installing using method 3')
                    # import urllib.request
                    content = urllib.request.urlopen('https://bootstrap.pypa.io/get-pip.py')
                    with open('/tmp/get-pip.py', 'w') as getpip:
                        getpip.write(content.read().decode())
                        getpip.close()
                    os.system('python3 /tmp/get-pip.py')
                    os.system('pip3 install avalon_framework')
                    os.remove('/tmp/get-pip.py')
            except Exception as e:
                print('\033[31mInstallation failed!: ' + str(e))
                print('Please check your Internet connectivity')
                exit(0)
            print('\033[32mInstallation Succeed!\033[0m')
            print('\033[32mPlease restart the program\033[0m')
            exit(0)
        elif install[0].upper() == 'N':  # if the user choose not to install
            print('\033[31m\033[1mSCUTUMM requires avalon framework to run!\033[0m')
            print('\033[33mAborting..\033[0m')
            exit(0)
        else:
            print('\033[31m\033[1mInvalid Input!\033[0m')


LOGPATH = '/var/log/scutum.log'
CONFPATH = "/etc/scutum.conf"

# This is the master version number
VERSION = '2.6.6'


# -------------------------------- Functions --------------------------------


def printIcon():
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


def processArguments():
    """This function parses all arguments

    There are three groups of arguments.

    The first group is controls group which directly controls the
    firewall.

    The second group, Installation group, controls the installation,
    uninstallation and upgrading of scutum

    The last groups, Extra, contains only a version function
    for now.
    """
    global args
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
    args = parser.parse_args()


def update_arptables():
    """operates arptables directly and
    locks gateway mac addresses

    This function creates an instance for each handled
    adapter and updates it's corresponded gateway mac
    address into arptables.
    """

    # reset arptables, removing all rules and
    # accept all incoming packages
    os.system('arptables --flush')

    if args.interface:
        interface = Adapter(args.interface, log)
        interface.updateGatewayAddrs()
        if interface.gatewayMac:
            os.system('arptables -P INPUT DROP')
            os.system('arptables -A INPUT --source-mac ' + interface.gatewayMac + ' -j ACCEPT')
    else:
        # Create one instance for each adapter
        for interface in interfaces:
            interface = Adapter(interface, log)
            ifaceobjs.append(interface)

        # make each adapter update gateway mac address
        for interface in ifaceobjs:
            interface.updateGatewayAddrs()

        for interface in ifaceobjs:
            if interface.gatewayMac:
                os.system('arptables -P INPUT DROP')
                os.system('arptables -A INPUT --source-mac ' + interface.gatewayMac + ' -j ACCEPT')


# -------------------------------- Execute --------------------------------

processArguments()


if not (args.enable or args.disable):
    printIcon()

if args.version:  # prints program legal / dev / version info
    print("Current Version: " + VERSION)
    print("Author: K4YT3X")
    print("License: GNU GPL v3")
    print("Github Page: https://github.com/K4YT3X/SCUTUM")
    print("Contact: k4yt3x@protonmail.com")
    print()
    exit(0)

log = Logger(LOGPATH)
installer = Installer(CONFPATH)

if args.upgrade:
    installer.check_avalon()
    installer.check_version(VERSION)
    exit(0)

try:
    if os.getuid() != 0:  # Arptables requires root
        avalon.error('SCUTUM must be run as root!')
        print(avalon.FG.LGR + 'It needs to control the system firewall so..' + avalon.FM.RST)
        exit(0)
    if not (args.purgelog or args.install or args.uninstall):
        # if program is doing normal operations, log everything
        # pointless if purging log, installing/removing
        log.writeLog(str(datetime.datetime.now()) + ' ---- START ----')
        log.writeLog(str(datetime.datetime.now()) + '  UID: ' + str(os.getuid()))
        if not os.path.isfile(CONFPATH):  # Configuration not found
            avalon.error('SCUTUM configuration file not found! Please re-install SCUTUM!')
            avalon.warning('Please run "scutum --install" before using it for the first time')
            exit(1)

        # Initialize python confparser and read config
        config = configparser.ConfigParser()
        config.read(CONFPATH)
        config.sections()

        # Read sections from the configuration file
        interfaces = config["Interfaces"]["interfaces"].split(",")
        NetworkControllers = config["NetworkControllers"]["controllers"]
        ufwHandled = config["Ufw"]["handled"]

    if args.install:
        # Install scutum into system
        avalon.info('Start Installing SCUTUM...')
        installer.install()
        print('\n' + avalon.FM.BD, end='')
        avalon.info('Installation Complete!')
        avalon.info('SCUTUM service is now enabled on system startup')
        avalon.info('You can now control it with systemd')
        avalon.info("You can also control it manually with \"scutum\" command")
        exit(0)
    elif args.uninstall:
        # Removes scutum completely from the system
        # Note that the configuration file will be removed too
        if avalon.ask('Removal Confirm: ', False):
            installer.removeScutum()
        else:
            avalon.warning('Removal Canceled')
            exit(0)
    elif args.reset:
        # resets the arptable, ufw and accept all incoming connections
        # This will expose the computer entirely on the network
        log.writeLog(str(datetime.datetime.now()) + ' ---- START ----')
        os.system('arptables -P INPUT ACCEPT')
        os.system('arptables --flush')
        if ufwHandled.lower() == "true":
                ufwctrl = Ufw(log)
                ufwctrl.disable()
        avalon.info('RST OK')
        log.writeLog(str(datetime.datetime.now()) + ' RESET OK')
    elif args.purgelog:
        # Deletes the log file of scutum
        # TODO: delete rotated logs too
        log.purge()
        avalon.info('LOG PURGE OK')
        exit(0)
    elif args.enable or args.disable:
        if args.enable:
            # Enable scutum will write scrips for wicd and network-manager
            # scutum will be started automatically
            log.writeLog(str(datetime.datetime.now()) + " SCUTUM ENABLED")
            if "wicd" in NetworkControllers.split(","):
                installer.installWicdScripts()
            if "NetworkManager" in NetworkControllers.split(","):
                installer.installNMScripts(config["NetworkControllers"]["controllers"].split(","))
            ifaceobjs = []  # a list to store internet controller objects
            os.system('arptables -P INPUT ACCEPT')  # Accept to get Gateway Cached

            update_arptables()

            if ufwHandled.lower() == "true":
                # if ufw is handled by scutum, enable it
                ufwctrl = Ufw(log)
                ufwctrl.enable()
            avalon.info('OK')
        elif args.disable:
            # This will disable scutum entirely and ufw too if it
            # is handled by scutum. scutum will not be started automatically
            # Firewalls will be reseted and expose the computer completely
            log.writeLog(str(datetime.datetime.now()) + " SCUTUM DISABLED")
            installer.removeNMScripts()
            installer.removeWicdScripts()
            os.system('arptables -P INPUT ACCEPT')
            os.system('arptables --flush')
            if ufwHandled.lower() == "true":
                ufwctrl = Ufw(log)
                ufwctrl.disable()
            avalon.info('RST OK')
    elif args.enablegeneric or args.disablegeneric:
        # you can choose to make scutum to handle ufw
        # after the installation
        ufwctrl = Ufw(log)
        if args.enablegeneric:
            ufwctrl.enable()
        elif args.disablegeneric:
            ufwctrl.disable()
    else:
        ifaceobjs = []  # a list to store internet controller objects
        os.system('arptables -P INPUT ACCEPT')  # Accept to get Gateway Cached

        update_arptables()

        if ufwHandled.lower() == "true":
                ufwctrl = Ufw(log)
                ufwctrl.enable()
        avalon.info('OK')
except KeyboardInterrupt:
    print('\n')
    avalon.warning('^C Pressed! Exiting...')
except KeyError:  # configuration section(s) missing
    avalon.error('The program configuration file is broken for some reason')
    avalon.error('You should reinstall SCUTUM to repair the configuration file')
    traceback.print_exc()
except Exception as e:
    print()
    avalon.error("SCUTUM has encountered an error:")
    traceback.print_exc()  # TODO: write this into the log
    if os.getuid() == 0:
        log.writeLog(str(datetime.datetime.now()) + ' -!-! ERROR !-!-')
        log.writeLog(str(e) + '\n')
finally:
    # write and close the log before exiting
    if not (args.purgelog or args.install or args.uninstall or os.getuid() != 0):
        log.writeLog(str(datetime.datetime.now()) + ' ---- FINISH ----\n')
    exit(0)
