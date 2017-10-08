#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: SCUTUM Installer Class
Author: K4YT3X
Date Created: Sep 26, 2017
Last Modified: Sep 30, 2017

Description: Handles the installation, removal, configuring and
upgrading for SCUTUM
"""
from iptables import Ufw
import avalon_framework as avalon
import configparser
import os
import shutil
import subprocess
import urllib.response


class Installer():

    def __init__(self, CONFPATH="/etc/scutum.conf"):
        self.SCUTUM_BIN_FILE = "/usr/bin/scutum"
        self.INSTALL_DIR = "/usr/share/scutum"
        self.CONFPATH = CONFPATH

    def install_service(self):
        shutil.copyfile("/usr/share/scutum/scutum", "/etc/init.d/scutum")
        os.system("chmod 755 /etc/init.d/scutum")
        os.system("update-rc.d scutum defaults")
        os.system("update-rc.d scutum start 10 2 3 4 5 . stop 90 0 1 6 .")

    def check_version(self, VERSION):
        avalon.info(avalon.FM.RST + 'Checking SCUTUM Version...')
        with urllib.request.urlopen('https://raw.githubusercontent.com/K4YT3X/SCUTUM/master/scutum.py') as response:
            html = response.read().decode().split('\n')
            for line in html:
                if 'VERSION = ' in line:
                    server_version = line.split(' ')[-1].replace('\'', '')
                    break
            avalon.subLevelTimeInfo('Server version: ' + server_version)
            if server_version > VERSION:
                avalon.info('Here\'s a newer version of SCUTUM!')
                if avalon.ask('Update to the newest version?'):
                    self.install()
                else:
                    avalon.warning('Ignoring update')
            else:
                avalon.info('SCUTUM is already on the newest version')
        return server_version

    def check_avalon(self):
        avalon.info(avalon.FM.RST + 'Checking AVALON Framework Version...')
        avalonVersionCheck = subprocess.Popen(["pip3", "freeze"], stdout=subprocess.PIPE).communicate()[0]
        pipOutput = avalonVersionCheck.decode().split('\n')
        for line in pipOutput:
            if 'avalon-framework' in line:
                localVersion = line.split('==')[-1]

        with urllib.request.urlopen('https://raw.githubusercontent.com/K4YT3X/AVALON/master/__init__.py') as response:
            html = response.read().decode().split('\n')
            for line in html:
                if 'VERSION = ' in line:
                    serverVersion = line.split(' ')[-1].replace('\'', '')
                    break

        if serverVersion > localVersion:
            avalon.info('Here\'s a newer version of AVALON Framework: ' + serverVersion)
            if avalon.ask('Update to the newest version?', True):
                os.system('pip3 install --upgrade avalon_framework')
            else:
                avalon.warning('Ignoring update')
        else:
            avalon.subLevelTimeInfo('Current version: ' + localVersion)
            avalon.info('AVALON Framework is already on the newest version')

    def sysInstallPackage(self, package):
        if avalon.ask('Install ' + package + '?', True):
            if os.path.isfile('/usr/bin/apt'):
                os.system('apt update && apt install ' + package + ' -y')  # install arptables with apt
                return True
            elif os.path.isfile('/usr/bin/yum'):
                os.system('yum install ' + package + ' -y')  # install arptables with yum
                return True
            elif os.path.isfile('/usr/bin/pacman'):
                os.system('pacman -S ' + package + ' --noconfirm')  # install arptables with pacman
                return True
            else:
                avalon.error('Sorry, we can\'t find a package manager that we currently support. Aborting..')
                print('Currently Supported: apt, yum, pacman')
                print('Please come to SCUTUM\'s github page and comment if you know how to add support to another package manager')
                return False
        else:
            return False

    def installWicdScripts(self):
        """
        Write scutum scripts for WICD
        """
        print(avalon.FG.G + '[+] INFO: Installing for WICD' + avalon.FM.RST + '.....', end='')
        if not os.path.isdir('/etc/wicd/'):
            print(avalon.FG.G + avalon.FM.BD + 'ERROR' + avalon.FM.RST)
            avalon.warning('WICD folder not found! WICD does not appear to be installed!')
            if avalon.ask('Continue anyway? (Create Directories)', False):
                os.system('mkdir /etc/wicd/')
                os.system('mkdir /etc/wicd/scripts/')
                os.system('mkdir /etc/wicd/scripts/postconnect/')
                os.system('mkdir /etc/wicd/scripts/postdisconnect/')
            else:
                avalon.warning('Aborting installation for WICD')
                return False
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
        return True

    def installNMScripts(self, interfaces):
        """
        Write scutum scripts for Network Manager
        """
        print(avalon.FG.G + '[+] INFO: Installing for NetworkManager' + avalon.FM.RST + '.....', end='')
        if not os.path.isdir('/etc/NetworkManager/dispatcher.d/'):
            print(avalon.FG.G + avalon.FM.BD + 'ERROR' + avalon.FM.RST)
            avalon.warning('NetworkManager folders not found! NetworkManager does not appear to be installed!')
            if avalon.ask('Continue anyway? (Create Directories)', False):
                os.system('mkdir /etc/NetworkManager/')
                os.system('mkdir /etc/NetworkManager/dispatcher.d/')
            else:
                avalon.warning('Aborting installation for NetworkManager')
                return False
        with open('/etc/NetworkManager/dispatcher.d/scutum', 'w') as nmScript:
            nmScript.write("#!/bin/bash\n")
            nmScript.write(" \n")
            nmScript.write("IF=$1\n")
            nmScript.write("STATUS=$2\n")
            nmScript.write(" \n")
            for iface in interfaces:
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
        return True

    def removeWicdScripts(self):
        try:
            os.remove('/etc/wicd/scripts/postconnect/scutum_connect')
            os.remove('/etc/wicd/scripts/postdisconnect/scutum_disconnect')
        except FileNotFoundError:
            pass

    def removeNMScripts(self):
        try:
            os.remove('/etc/NetworkManager/dispatcher.d/scutum')
        except FileNotFoundError:
            pass

    def removeScutum(self):
        os.remove('/usr/bin/scutum')

        self.removeWicdScripts()
        self.removeNMScripts()

        try:
            shutil.rmtree("/usr/share/scutum")
        except FileNotFoundError:
            pass
        avalon.info('SCUTUM successfully removed!')
        exit(0)

    def install_easytcp_controllers(self):
        if os.path.islink("/usr/bin/openport"):
            os.remove("/usr/bin/openport")
        if os.path.islink("/usr/bin/closeport"):
            os.remove("/usr/bin/closeport")
        os.system('ln -s {}/openport.py /usr/bin/openport'.format(self.INSTALL_DIR))
        os.system("chmod 755 {}/openport.py".format(self.INSTALL_DIR))
        os.system('ln -s {}/closeport.py /usr/bin/closeport'.format(self.INSTALL_DIR))
        os.system("chmod 755 {}/closeport.py".format(self.INSTALL_DIR))

    def install_scutum_gui(self):
        DESKTOP_FILE = "/usr/share/applications/scutum-gui.desktop"
        if os.path.islink(DESKTOP_FILE) or os.path.isfile(DESKTOP_FILE):
            os.remove(DESKTOP_FILE)
        os.system('ln -s {}/scutum-gui.desktop {}'.format(self.INSTALL_DIR, DESKTOP_FILE))
        os.system("chmod 755 {}/scutum-gui.desktop".format(self.INSTALL_DIR))

    def install(self):
        """
        This is the main function for installer
        """
        global ifacesSelected

        config = configparser.ConfigParser()
        config["Interfaces"] = {}
        config["NetworkControllers"] = {}
        config["Ufw"] = {}

        if os.path.islink(self.SCUTUM_BIN_FILE) or os.path.isfile(self.SCUTUM_BIN_FILE):
            os.remove(self.SCUTUM_BIN_FILE)  # Remove old file or symbolic links

        os.system("ln -s " + self.INSTALL_DIR + "/scutum.py " + self.SCUTUM_BIN_FILE)

        self.install_service()  # install and register service files
        os.system("systemctl enable scutum")  # enable service
        os.system("systemctl start scutum")  # start service

        if not os.path.isfile('/usr/bin/arptables') and not os.path.isfile('/sbin/arptables'):  # Detect if arptables installed
            print(avalon.FM.BD + avalon.FG.R + '\nWe have detected that you don\'t have arptables installed!' + avalon.FM.RST)
            print('SCUTUM requires arptables to run')
            if not self.sysInstallPackage("arptables"):
                avalon.error("arptables is required for scutum. Exiting...")
                exit(1)

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

        config["Interfaces"]["interfaces"] = ",".join(ifacesSelected)

        while True:
            print(avalon.FM.BD + '\nWhich network controller do you want to install for?' + avalon.FM.RST)
            print('1. WICD')
            print('2. Network-Manager')
            print('3. Both')

            selection = avalon.gets('Please select: (index number): ')

            if selection == '1':
                if self.installWicdScripts() is not True:
                    avalon.error("SCUTUM Script for WICD has failed to install!")
                    avalon.error("Aborting Installation...")
                    exit(1)
                config["NetworkControllers"]["controllers"] = "wicd"
                break
            elif selection == '2':
                if self.installNMScripts(ifacesSelected) is not True:
                    avalon.error("SCUTUM Script for NetworkManager has failed to install!")
                    avalon.error("Aborting Installation...")
                    exit(1)
                config["NetworkControllers"]["controllers"] = "NetworkManager"
                break
            elif selection == '3':
                ifaces = ["wicd", "NetworkManager"]
                if self.installWicdScripts() is not True:
                    avalon.warning("Deselected WICD from installation")
                    ifaces.remove("wicd")
                if self.installNMScripts(ifacesSelected) is not True:
                    avalon.warning("Deselected NetworkManager from installation")
                    ifaces.remove("NetworkManager")
                if len(ifaces) == 0:
                    avalon.error("All SCUTUM Scripts have failed to install!")
                    avalon.error("Aborting Installation...")
                    exit(1)
                config["NetworkControllers"]["controllers"] = ",".join(ifaces)
                break
            else:
                avalon.error('Invalid Input!')

        print(avalon.FM.BD + '\nEnable UFW firewall?' + avalon.FM.RST)
        print("Do you want SCUTUM to help configuring and enabling UFW firewall?")
        print("This will prevent a lot of scanning and attacks")
        if avalon.ask('Enable?', True):
            ufwctrl = Ufw(False)
            print("UFW can configure UFW Firewall for you")
            print("However this will reset your current UFW configurations")
            print("It is recommended to do so the first time you install SCUTUM")
            if avalon.ask("Let SCUTUM configure UFW for you?", True):
                ufwctrl.initialize(True)
            else:
                avalon.info("Okay. Then we will simply enable it for you")
                ufwctrl.enable()

            print("If you let SCUTUM handle UFW, then UFW will be activated and deactivated with SCUTUM")
            if avalon.ask("Let SCUTUM handle UFW?", True):
                config["Ufw"]["handled"] = "true"
            else:
                config["Ufw"]["handled"] = "false"
        else:
            avalon.info("You can turn it on whenever you change your mind")


        print(avalon.FM.BD + '\nInstall Easy TCP controllers?' + avalon.FM.RST)
        print("Easy tcp controller helps you open/close ports quickly")
        print("ex. \"openport 80\" opens port 80")
        print("ex. \"closeport 80\" closes port 80")
        print("ex. \"openport 80 443\" opens port 80 and 443")
        print("ex. \"closeport 80 443\" closes port 80 and 443")
        if avalon.ask("Install Easy TCP conrollers?", True):
            self.install_easytcp_controllers()

        print(avalon.FM.BD + '\nInstall SCUTUM GUI?' + avalon.FM.RST)
        print("SCUTUM GUI is convenient for GUI Interfaces")
        print("ex. KDE, GNOME, XFCE, etc.")
        print("However, there\'s not point to install GUI on servers")
        if avalon.ask("Install SCUTUM GUI?", True):
            self.install_scutum_gui()

        with open(self.CONFPATH, 'w') as configfile:
            config.write(configfile)  # Writes configurations
