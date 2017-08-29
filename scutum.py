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
Last Modified: Aug 29,2017

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
import datetime
import ipaddress
import os
import socket
import struct
import subprocess
import time
import urllib.request

try:
    import avalon_framework as avalon
except ImportError:
    while True:
        install = input('\033[31m\033[1mAVALON Framework not installed! Install now? [Y/n] \033[0m')
        if len(install) == 0 or install[0].upper() == 'Y':
            try:
                if os.path.isfile('/usr/bin/pip3'):
                    print('Installing using method 1')
                    os.system('pip3 install avalon_framework')
                elif os.path.isfile('/usr/bin/wget'):
                    print('Installing using method 2')
                    os.system('wget -O - https://bootstrap.pypa.io/get-pip.py | python3')
                    os.system('pip3 install avalon_framework')
                else:
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
        elif install[0].upper() == 'N':
            print('\033[31m\033[1mSCUTUMM requires avalon framework to run!\033[0m')
            print('\033[33mAborting..\033[0m')
            exit(0)
        else:
            print('\033[31m\033[1mInvalid Input!\033[0m')


LOGPATH = '/var/log/scutum.log'
VERSION = '2.5.1'


# -------------------------------- Classes --------------------------------

class interface_ctrl:

    def __init__(self, interface):
        self.interface = interface

    def getGateway(self):
        """Get Linux Default Gateway"""
        with open("/proc/net/route") as fh:
            for line in fh:
                if self.interface in line:
                    fields = line.strip().split()
                    if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                        continue
                    return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))
        return 0

    def getGatewayMac(self):
        """Get Gateway Mac Address"""
        with open('/proc/net/arp') as arpf:
            for line in arpf:
                if line.split(' ')[0] == interface_ctrl.getGateway(self) and self.interface in line:
                    for field in line.split(' '):
                        if len(field) == 17 and ':' in field:
                            return field
        return 0

    def getIP(self):
        """
        Returns the IP address for current machine
        More accurate than socket, but only works when there's only one interface
        Might be improved or removed in future
        """
        output = subprocess.Popen(["ifconfig"], stdout=subprocess.PIPE).communicate()[0]
        iface_splited = output.decode().split('\n\n')
        for line in iface_splited:
            if line.split(':')[0] == self.interface:
                for section in line.split('\n'):
                    if 'inet ' in section:
                        ipv4_address = section.split('inet ')[1].split(' ')[0]
                    """ In case needed in the future
                    if 'inet6 ' in section:
                        ipv6_address = section.split('inet6 ')[1].split(' ')[0]
                    if 'ether ' in section:
                        mac_address = section.split('ether ')[1].split(' ')[0]
                    """
                if ipv4_address:
                    return ipv4_address
        return False

    def updateIPTables(self):
        """
        Add router to iptables whitelist
        """
        if ipaddress.ip_address(interface_ctrl.getIP(self)).is_private:
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
            for address in dnsServers:  # Accept all DNS within /etc/resolv.conf
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

    def iptablesReset(self):
        """
        Flush everything in iptables completely
        This function will reset iptables and flush all custom settings
        """
        os.system('iptables -F && iptables -X')
        os.system('iptables -P INPUT ACCEPT')
        os.system('iptables -P FORWARD ACCEPT')
        os.system('iptables -P OUTPUT ACCEPT')

    def updateArpTables(self):
        """
        This function adds the gateway's mac address into
        arptable's whitelist
        """
        while True:  # Wait Until Gateway ARP is cached
            gatewayMac = str(interface_ctrl.getGatewayMac(self))
            # os.system('nslookup google.ca')  # Works as well as the following
            try:
                ac = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ac.settimeout(0)
                # Connect to gateway to cache gateway MAC
                ac.connect((interface_ctrl.getGateway(self), 0))
                ac.close()
            except Exception:
                pass
            # Check if it's a valid MAC Address
            if gatewayMac != '00:00:00:00:00:00' and len(gatewayMac) == 17:
                break
            time.sleep(0.5)  # Be nice to CPU
        log.write(str(datetime.datetime.now()) + '  MAC: ' + gatewayMac + '\n')
        log.write(str(datetime.datetime.now()) + '  IP: ' + str(interface_ctrl.getIP(self)) + '\n')
        os.system('arptables --flush')
        os.system('arptables -P INPUT DROP')
        os.system('arptables -A INPUT --source-mac ' + gatewayMac + ' -j ACCEPT')


# -------------------------------- Functions --------------------------------

def printIcon():
    print(avalon.FM.BD + '     ___   __  _  _  ____  _  _  __  __' + avalon.FM.RST)
    print(avalon.FM.BD + '    / __) / _)( )( )(_  _)( )( )(  \/  )' + avalon.FM.RST)
    print(avalon.FM.BD + '    \__ \( (_  )()(   )(   )()(  )    (' + avalon.FM.RST)
    print(avalon.FM.BD + '    (___/ \__) \__/  (__)  \__/ (_/\/\_)' + avalon.FM.RST)
    print('\n               ARP Firewall')
    print(avalon.FM.BD + '\n              Version ' + VERSION + '\n' + avalon.FM.RST)


def processArguments():
    """
    This function takes care of all arguments
    """
    global args
    parser = argparse.ArgumentParser()
    control_group = parser.add_argument_group('Controls')
    control_group.add_argument("--start", help="Start SCUTUM once even if disabled", action="store_true", default=False)
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
    args = parser.parse_args()


def removeScutum():
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

    if not os.path.isfile('/usr/bin/arptables') and not os.path.isfile('/sbin/arptables'):  # Detect if arptables installed
        print(avalon.FM.BD + avalon.FG.R + '\nWe have detected that you don\'t have arptables installed!' + avalon.FM.RST)
        print('SCUTUM requires arptables to run')
        if avalon.ask('Install arptables?', True):
            if os.path.isfile('/usr/bin/apt'):
                os.system('apt update && apt install arptables -y')  # install arptables with apt
            elif os.path.isfile('/usr/bin/yum'):
                os.system('yum install arptables -y')  # install arptables with yum
            elif os.path.isfile('/usr/bin/pacman'):
                os.system('pacman -S arptables --noconfirm')  # install arptables with pacman
            else:
                avalon.error('Sorry, we can\'t find a package manager that we currently support. Aborting..')
                print('Currently Supported: apt, yum, pacman')
                print('Please come to SCUTUM\'s github page and comment if you know how to add support to another package manager')
                exit(0)
        else:
            avalon.error('arptables not installed. Unable to proceed. Aborting..')
            exit(0)

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
        selection = avalon.gets('Please select (index number): ')

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

        selection = avalon.gets('Please select: (index number): ')

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
            scutum_config.write('interfaces=' + ','.join(ifacesSelected) + '\n')
            scutum_config.write('enabled=true\n')
            scutum_config.close()
    else:
        with open('/etc/scutum.conf', 'w') as scutum_config:
            scutum_config.write('[SCUTUM CONFIG]\n')
            scutum_config.write('firewall=false\n')
            scutum_config.write('interfaces=' + ','.join(ifacesSelected) + '\n')
            scutum_config.write('enabled=true\n')
            scutum_config.close()


# -------------------------------- Execute --------------------------------

processArguments()
if not (args.enable or args.disable):
        printIcon()

try:
    if os.getuid() != 0:  # Arptables requires root
        avalon.error('SCUTUM must be run as root!')
        exit(0)
    if not (args.purgelog or args.install or args.uninstall or args.enable or args.disable):
        log = open(LOGPATH, 'a+')  # Just for debugging
        log.write(str(datetime.datetime.now()) + ' ---- START ----\n')
        log.write(str(datetime.datetime.now()) + '  UID: ' + str(os.getuid()) + '\n')
        if not os.path.isfile('/etc/scutum.conf'):
            avalon.error('SCUTUM Config file not found! Please re-install SCUTUM!')
            avalon.warning('Please run "scutum --install" before using it for the first time')
            exit()

        configIntegrity = []
        required = ['firewall', 'enabled', 'interfaces']

        with open('/etc/scutum.conf', 'r') as scutum_config:
            for line in scutum_config:
                if 'firewall' in line and 'true' in line:
                    configIntegrity.append('firewall')
                    iptablesEnabled = True
                elif 'firewall' in line and 'false' in line:
                    configIntegrity.append('firewall')
                    iptablesEnabled = False

                if 'enabled' in line and 'true' in line:
                    configIntegrity.append('enabled')
                    enabled = True
                elif 'enabled' in line and 'false' in line:
                    configIntegrity.append('enabled')
                    enabled = False

                if 'interfaces' in line:
                    configIntegrity.append('interfaces')
                    interfaces = line.replace('\n', '').split('=')[1].split(',')

        for item in required:
            if item not in configIntegrity:
                avalon.error('The program configuration file is broken for some reason')
                avalon.error('You should reinstall SCUTUM to repair the configuration file')
                exit(0)

    if args.install:
        avalon.info('Start Installing Scutum...')
        os.system('cp ' + os.path.abspath(__file__) + ' /usr/bin/scutum')  # os.rename throws an error when /tmp is in a separate partition
        os.system('chown root: /usr/bin/scutum')
        os.system('chmod 755 /usr/bin/scutum')
        installScutum()
        os.system('cp scutum-gui /usr/bin/scutum-gui')
        os.system('chown root: /usr/bin/scutum-gui')
        os.system('chmod 755 /usr/bin/scutum-gui')
        os.system('cp scutum-gui.desktop /usr/share/applications/scutum-gui.desktop')
        os.system('chown root: /usr/share/applications/scutum-gui.desktop')
        os.system('chmod 755 /usr/share/applications/scutum-gui.desktop')
        os.system('cp scutum-gui.png /usr/share/icons/scutum-gui.png')
        print('\n' + avalon.FM.BD, end='')
        avalon.info('Installation Complete!')
        if avalon.ask('Do you want to remove the installer?', True):
            avalon.info('Removing ' + os.path.abspath(__file__))
            os.remove(os.path.abspath(__file__))
        avalon.info('Now SCUTUM will start automatically on connection')
        avalon.info('You can now manually call the program with command "scutum"')
        exit(0)
    elif args.uninstall:
        confirmed = avalon.ask('Removal Confirm: ', False)
        if confirmed:
            removeScutum()
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
    elif args.status:
        with open('/etc/scutum.conf', 'r') as scutum_config:
            for line in scutum_config:
                if 'enable' in line and 'true' in line:
                    print('SCUTUM is ' + avalon.FG.G + 'ENABLED' + avalon.FM.RST)
                elif 'enable' in line and 'false' in line:
                    print('SCUTUM is ' + avalon.FG.R + 'DISABLED' + avalon.FM.RST)
    elif args.enable or args.disable:
        with open('/etc/scutum.conf', 'r') as conf_old:
            with open('/tmp/scutum.conf', 'w') as conf_new:
                for line in conf_old:
                    if 'enabled' in line:
                        pass
                    else:
                        conf_new.write(line)
                if args.enable:
                    conf_new.write('enabled=true\n')
                    os.system('scutum --start')
                    avalon.info('SCUTUM Enabled')
                elif args.disable:
                    conf_new.write('enabled=false\n')
                    os.system('scutum --reset')
                    avalon.info('SCUTUM Disabled')
                conf_new.close()
            conf_old.close()
        os.system('mv /tmp/scutum.conf /etc/scutum.conf')  # os.rename throws an error when /tmp is in a separate partition
        exit(0)
    else:
        if enabled or args.start:
            ifaceobjs = []  # a list to store internet controller objects
            os.system('arptables -P INPUT ACCEPT')  # Accept to get Gateway Cached

            for interface in interfaces:
                interface = interface_ctrl(interface)
                ifaceobjs.append(interface)

            for interface in ifaceobjs:
                interface.updateArpTables()
                if iptablesEnabled:
                    interface.iptablesReset()
                    interface.updateIPTables()
            avalon.info('OK')
        else:
            log.write('SCUTUM Disabled, taking no actions')
            avalon.warning('SCUTUM Disabled, taking no actions')
except KeyboardInterrupt:
    print('\n')
    avalon.warning('^C Pressed! Exiting...')
    exit(0)
except Exception as er:
    avalon.error(str(er))
    if not (args.purgelog or args.install or args.uninstall or args.enable or args.disable or os.getuid() != 0):
        log.write(str(datetime.datetime.now()) + ' -!-! ERROR !-!-\n')
        log.write(str(er) + '\n')
finally:
    if not (args.purgelog or args.install or args.uninstall or args.enable or args.disable or os.getuid() != 0):
        log.write(str(datetime.datetime.now()) + ' ---- FINISH ----\n\n')
        log.close()
