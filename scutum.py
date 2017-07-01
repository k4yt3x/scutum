#!/usr/bin/python3
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
Author: K4T
Date of Creation: March 8,2017
Last Modified: June 16,2017

Licensed under the GNU General Public License Version 3 (GNU GPL v3),
    available at: https://www.gnu.org/licenses/gpl-3.0.txt

(C) 2017 K4YT3X

Description: SCUTUM is a firewall designed for personal computers that mainly
focuses on ARP defensing

For WICD and Network-Manager

For tutorial please look at the Github Page: https://github.com/K4YT3X/SCUTUM

"""
from __future__ import print_function
import argparse
import avalon_framework as avalon
import datetime
import ipaddress
import os
import socket
import struct
import subprocess
import time

LOGPATH = '/var/log/scutum.log'
VERSION = '2.3 Alpha'


# -------------------------------- Classes --------------------------------

class NotRoot(Exception):
    """
    The Exception raised when run with insufficient privilege
    """
    pass


# -------------------------------- Functions --------------------------------


def printIcon():
    print(avalon.FM.BD + '     ___   __  _  _  ____  _  _  __  __' + avalon.FM.RST)
    print(avalon.FM.BD + '    / __) / _)( )( )(_  _)( )( )(  \/  )' + avalon.FM.RST)
    print(avalon.FM.BD + '    \__ \( (_  )()(   )(   )()(  )    (' + avalon.FM.RST)
    print(avalon.FM.BD + '    (___/ \__) \__/  (__)  \__/ (_/\/\_)' + avalon.FM.RST)
    print('\n               ARP Firewall')
    print(avalon.FM.BD + '\n              Version ' + VERSION + '\n' + avalon.FM.RST)


def getGateway():
    """Get Linux Default Gateway"""
    with open("/proc/net/route") as fh:
        for line in fh:
            for iface in interfaces:
                if iface in line:
                    fields = line.strip().split()
                    if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                        continue
                    return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))
    return 0


def getGatewayMac():
    """Get Gateway Mac Address"""
    with open('/proc/net/arp') as arpf:
        for line in arpf:
            if line.split(' ')[0] == getGateway():
                for field in line.split(' '):
                    if len(field) == 17 and ':' in field:
                        return field
    return 0


def getIP():
    """
    Returns the IP address for current machine
    More accurate than socket, but only works when there's only one interface
    Might be improved or removed in future
    """
    output = subprocess.Popen(["ifconfig"], stdout=subprocess.PIPE).communicate()[0]
    output = output.decode().split('\n')
    ips = []
    for line in output:
        if 'inet' in line:
            ips.append(line[8:].split(' ')[1])
    for ip in ips:
        if ip != '127.0.0.1' and not ipaddress.ip_address(ip).is_loopback:
            return ip
    return False


def allowRouter():
    if ipaddress.ip_address(getIP()).is_private:
        os.system('iptables -P INPUT DROP')
        os.system('iptables -P FORWARD DROP')
        os.system('iptables -P OUTPUT ACCEPT')
        os.system('iptables -A INPUT -p tcp --match multiport --dports 1025:65535 -j ACCEPT')
        with open('/etc/resolv.conf', 'r') as resolv:
            dnsServers = []
            for line in resolv:
                if 'nameserver' in line:
                    for element in line.replace('\n', '').split(' '):
                        try:
                            if ipaddress.ip_address(element):
                                dnsServers.append(element)
                        except ValueError:
                            pass
        for address in dnsServers:
            os.system('iptables -A INPUT -p udp -s ' + address + ' -j ACCEPT')
        # os.system('iptables -A INPUT -p udp -s 208.67.222.222 -j ACCEPT')
        # os.system('iptables -A INPUT -p udp -s 208.67.220.220 -j ACCEPT')
        os.system('iptables -A INPUT -m iprange --src-range 10.0.0.0-10.255.255.255 -j DROP')
        os.system('iptables -A INPUT -m iprange --src-range 172.16.0.0-172.31.255.255 -j DROP')
        os.system('iptables -A INPUT -m iprange --src-range 192.168.0.0-192.168.255.255 -j DROP')
    """  # this part adds gateway into iptables whitelist, might not be necessary
    while True:  # Just keep trying forever until the router is found
        if getGateway() != 0:
            avalon.subLevelTimeInfo('Accepting Traffic from ' + getGateway())
            os.system('iptables -A INPUT -s ' + getGateway() + ' -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT')
            break
    """


def iptablesReset():
    os.system('iptables -F && iptables -X')
    os.system('iptables -P INPUT ACCEPT')
    os.system('iptables -P FORWARD ACCEPT')
    os.system('iptables -P OUTPUT ACCEPT')


def updateArpTables():
    """Update Arptables"""
    while True:  # Wait Until Gateway ARP is cached
        gatewayMac = str(getGatewayMac())
        # os.system('nslookup google.ca')  # Works as well as the following
        try:
            ac = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ac.settimeout(0)
            ac.connect((getGateway(), 0))  # Connect to gateway to cache gateway MAC
            ac.close()
        except Exception:
            pass
        if gatewayMac != '00:00:00:00:00:00' and len(gatewayMac) == 17:  # Check if it's a valid MAC Address
            break
        time.sleep(0.5)  # Be nice to CPU
    log.write(str(datetime.datetime.now()) + '  MAC: ' + gatewayMac + '\n')
    log.write(str(datetime.datetime.now()) + '  IP: ' + str(getIP()) + '\n')
    os.system('arptables --flush')
    os.system('arptables -P INPUT DROP')
    os.system('arptables -A INPUT --source-mac ' + gatewayMac + ' -j ACCEPT')


def processArguments():
    """
    This function takes care of all arguments
    """
    global args
    parser = argparse.ArgumentParser()
    action_group = parser.add_argument_group('ACTIONS')
    action_group.add_argument("-r", "--reset", help="Allow all ARP packets", action="store_true", default=False)
    action_group.add_argument("-p", "--purgelog", help="Purge Log File", action="store_true", default=False)
    action_group.add_argument("--install", help="Install Scutum Automatically", action="store_true", default=False)
    action_group.add_argument("--uninstall", help="Uninstall Scutum Automatically", action="store_true", default=False)
    args = parser.parse_args()


def installScutum():
    def install4WICD():
        """
        Write scutum scripts for WICD
        """
        print(avalon.FG.G + '[+] INFO: Installing for WICD' + avalon.FM.RST + '.....', end='')
        if not os.path.isdir('/etc/wicd/'):
            print(avalon.FG.G + avalon.FM.BD + 'ERROR' + avalon.FM.RST)
            avalon.warning('WICD folder not found! WICD does not appear to be installed!')
            if avalon.ask('Continue anyway?', False):
                os.system('mkdir /etc/wicd/')
                os.system('mkdir /etc/wicd/scripts/')
                os.system('mkdir /etc/wicd/scripts/postconnect/')
                os.system('mkdir /etc/wicd/scripts/postdisconnect/')
            else:
                avalon.warning('Aborting installation for WICD')
                return 0
        with open('/etc/wicd/scripts/postconnect/scutum_connect', 'w') as postconnect:
            postconnect.write('#!/bin/bash\n')
            postconnect.write('scutum')
            postconnect.close()
        with open('/etc/wicd/scripts/postdisconnect/scutum_disconnect', 'w') as postdisconnect:
            postdisconnect.write('#!/bin/bash\n')
            postdisconnect.write('scutum --reset')
            postdisconnect.close()
        os.system('chown root: /etc/wicd/scripts/postconnect/scutum_connect')
        os.system('chmod 755 /etc/wicd/scripts/postconnect/scutum_connect')
        os.system('chown root: /etc/wicd/scripts/postdisconnect/scutum_disconnect')
        os.system('chmod 755 /etc/wicd/scripts/postdisconnect/scutum_disconnect')
        print(avalon.FG.G + avalon.FM.BD + 'SUCCEED' + avalon.FM.RST)

    def install4NM():
        """
        Write scutum scripts for Network Manager
        """
        print(avalon.FG.G + '[+] INFO: Installing for NetworkManager' + avalon.FM.RST + '.....', end='')
        if not os.path.isdir('/etc/NetworkManager/dispatcher.d/'):
            print(avalon.FG.G + avalon.FM.BD + 'ERROR' + avalon.FM.RST)
            avalon.warning('NetworkManager folders not found! NetworkManager does not appear to be installed!')
            if avalon.ask('Continue anyway?', False):
                os.system('mkdir /etc/NetworkManager/')
                os.system('mkdir /etc/NetworkManager/dispatcher.d/')
            else:
                avalon.warning('Aborting installation for NetworkManager')
                return 0
        with open('/etc/NetworkManager/dispatcher.d/scutum', 'w') as nmScript:
            nmScript.write("#!/bin/bash\n")
            nmScript.write(" \n")
            nmScript.write("IF=$1\n")
            nmScript.write("STATUS=$2\n")
            nmScript.write(" \n")
            for iface in ifacesSelected:
                nmScript.write("if [ \"$IF\" == \"" + iface + "\" ]\n")
                nmScript.write("then\n")
                nmScript.write("    case \"$2\" in\n")
                nmScript.write("        up)\n")
                nmScript.write("        scutum\n")
                nmScript.write("        ;;\n")
                nmScript.write("        down)\n")
                nmScript.write("        scutum --reset\n")
                nmScript.write("        ;;\n")
                nmScript.write("        *)\n")
                nmScript.write("        ;;\n")
                nmScript.write("    esac\n")
                nmScript.write("fi\n")
            nmScript.close()

        os.system('chown root: /etc/NetworkManager/dispatcher.d/scutum')
        os.system('chmod 755 /etc/NetworkManager/dispatcher.d/scutum')
        print(avalon.FG.G + avalon.FM.BD + 'SUCCEED' + avalon.FM.RST)

    ifacesSelected = []
    while True:
        print(avalon.FM.BD + '\nWhich interface do you wish to install for?' + avalon.FM.RST)
        ifaces = []
        with open('/proc/net/dev', 'r') as dev:
            for line in dev:
                try:
                    if line.split(':')[1]:
                        ifaces.append(line.split(':')[0])
                except IndexError:
                    pass
        if not len(ifaces) == 0:
            idx = 0
            for iface in ifaces:
                print(str(idx) + '. ' + iface.replace(' ', ''))
                idx += 1
        print('99. Manually Enter')
        selection = avalon.gets('Please select (index number):')

        try:
            if selection == '99':
                manif = avalon.gets('Interface: ')
                if manif not in ifacesSelected:
                    ifacesSelected.append(manif)
                if avalon.ask('Add more interfaces?', False):
                    pass
                else:
                    break
            elif int(selection) >= len(ifaces):
                avalon.error('Selected interface doesn\'t exist!')
            else:
                ifacesSelected.append(ifaces[int(selection)].replace(' ', ''))
                if avalon.ask('Add more interfaces?', False):
                    pass
                else:
                    break
        except ValueError:
            avalon.error('Invalid Input!')
            avalon.error('Please enter the index number!')

    while True:
        print(avalon.FM.BD + '\nWhich network controller do you want to install for?' + avalon.FM.RST)
        print('1. WICD')
        print('2. Network-Manager')
        print('3. Both')

        selection = avalon.gets('Please select: (index number)')

        if selection == '1':
            install4WICD()
            break
        elif selection == '2':
            install4NM()
            break
        elif selection == '3':
            install4WICD()
            install4NM()
            break
        else:
            avalon.error('Invalid Input!')

    print(avalon.FM.BD + '\nEnable SCUTUM iptables firewall?' + avalon.FM.RST)
    print('This firewall uses linux iptables to establish a relatively secure environment')
    print('However, professional firewall softwares like ufw is recommended')
    print('Enable this only if you don\'t have a firewall already')
    avalon.warning('This feature will erase all existing iptables settings!')
    if avalon.ask('Enable?', False):
        with open('/etc/scutum.conf', 'w') as scutum_config:  # A very simple config system
            scutum_config.write('[SCUTUM CONFIG]\n')
            scutum_config.write('firewall=true\n')
            scutum_config.write('interfaces=' + ','.join(ifacesSelected))
            scutum_config.close()
    else:
        with open('/etc/scutum.conf', 'w') as scutum_config:
            scutum_config.write('[SCUTUM CONFIG]\n')
            scutum_config.write('firewall=false\n')
            scutum_config.write('interfaces=' + ','.join(ifacesSelected))
            scutum_config.close()


# -------------------------------- Execute --------------------------------

printIcon()
processArguments()

try:
    if os.getuid() != 0:  # Arptables requires root
        avalon.error('SCUTUM must be run as root!')
        raise NotRoot(str(datetime.datetime.now()) + ' Not Root')
    if not (args.purgelog or args.install or args.uninstall):
        log = open(LOGPATH, 'a+')  # Just for debugging
        log.write(str(datetime.datetime.now()) + ' ---- START ----\n')
        log.write(str(datetime.datetime.now()) + '  UID: ' + str(os.getuid()) + '\n')
        if not os.path.isfile('/etc/scutum.conf'):
            avalon.error('SCUTUM Config file not found! Please re-install SCUTUM!')
            avalon.warning('Please run "scutum --install" before using it for the first time')
            exit()
        with open('/etc/scutum.conf', 'r') as scutum_config:
            for line in scutum_config:
                if 'firewall' in line and 'true' in line:
                    iptablesEnabled = True
                elif 'firewall' in line and 'false' in line:
                    iptablesEnabled = False
                if 'interfaces' in line:
                    interfaces = line.split('=')[1].split(',')
    if args.install:
        avalon.info('Start Installing Scutum...')
        os.rename(os.path.abspath(__file__), '/usr/bin/scutum')
        os.system('chown root: /usr/bin/scutum')
        os.system('chmod 755 /usr/bin/scutum')
        installScutum()
        print('\n' + avalon.FM.BD, end='')
        avalon.info('Installation Complete!')
        exit(0)
    elif args.uninstall:
        confirmed = avalon.ask('Removal Confirm: ', False)
        if confirmed:
            os.remove('/usr/bin/scutum')
            try:
                os.remove('/etc/wicd/scripts/postconnect/scutum_connect')
                os.remove('/etc/wicd/scripts/postdisconnect/scutum_disconnect')
            except FileNotFoundError:
                pass
            try:
                os.remove('/etc/NetworkManager/dispatcher.d/scutum')
            except FileNotFoundError:
                pass
            avalon.info('Scutum sucessfully removed!')
            exit(0)
        else:
            avalon.warning('Removal Canceled')
            exit(0)
    elif args.reset:
        log.write(str(datetime.datetime.now()) + ' ---- START ----\n')
        os.system('arptables -P INPUT ACCEPT')
        os.system('arptables --flush')
        avalon.info('RST OK')
        log.write(str(datetime.datetime.now()) + ' RESET OK\n')
    elif args.purgelog:
        os.remove(LOGPATH)
        avalon.info('LOG PURGE OK')
        exit(0)
    else:
        os.system('arptables -P INPUT ACCEPT')  # Accept to get Gateway Cached
        updateArpTables()

        if iptablesEnabled:
            iptablesReset()
            allowRouter()
        avalon.info('OK')
except KeyboardInterrupt:
    print('\n')
    avalon.warning('^C Pressed! Exiting...')
    exit(0)
except Exception as er:
    avalon.error(str(er))
    if not (args.purgelog or args.install or args.uninstall):
        log.write(str(datetime.datetime.now()) + ' -!-! ERROR !-!-\n')
        log.write(str(er) + '\n')
finally:
    if not (args.purgelog or args.install or args.uninstall):
        log.write(str(datetime.datetime.now()) + ' ---- FINISH ----\n\n')
        log.close()
