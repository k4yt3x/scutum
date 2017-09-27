#!/usr/bin/python3
# -*- coding: utf-8 -*-
import avalon_framework as avalon
import os
import shutil
import subprocess
import urllib.response
import configparser


class Installer():

    def __init__(self, CONFPATH):
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
                return 0
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

    def install(self):
        """
        This is the main function for installer
        """
        global ifacesSelected

        config = configparser.ConfigParser()
        config["Interfaces"] = {}
        config["Iptables"] = {}
        config["networkControllers"] = {}

        if os.path.isdir(self.INSTALL_DIR):
            shutil.rmtree(self.INSTALL_DIR)  # remove old scutum files

        if os.path.isfile("/usr/bin/git"):
            os.system("git clone https://github.com/K4YT3X/SCUTUM.git " + self.INSTALL_DIR)
            os.system("chown -R root: " + self.INSTALL_DIR)
            os.system("chmod -R 755 " + self.INSTALL_DIR)
        else:
            avalon.error("Command: \"git\" not found. Please install git.")
            exit(0)

        if os.path.islink(self.SCUTUM_BIN_FILE) or os.path.isfile(self.SCUTUM_BIN_FILE):
            os.remove(self.SCUTUM_BIN_FILE)  # Remove old file or symbolic links

        os.system("ln -s " + self.INSTALL_DIR + "/scutum.py " + self.SCUTUM_BIN_FILE)

        self.install_service()  # install and register service files
        os.system("systemctl enable scutum")  # enable service
        os.system("systemctl start scutum")  # start service

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

        config["Interfaces"]["interfaces"] = ",".join(ifacesSelected)

        while True:
            print(avalon.FM.BD + '\nWhich network controller do you want to install for?' + avalon.FM.RST)
            print('1. WICD')
            print('2. Network-Manager')
            print('3. Both')

            selection = avalon.gets('Please select: (index number): ')

            if selection == '1':
                self.installWicdScripts()
                config["networkControllers"]["controllers"] = "wicd"
                break
            elif selection == '2':
                self.installNMScripts(ifacesSelected)
                config["networkControllers"]["controllers"] = "NetworkManager"
                break
            elif selection == '3':
                self.installWicdScripts()
                self.installNMScripts(ifacesSelected)
                config["networkControllers"]["controllers"] = "wicd,NetworkManager"
                break
            else:
                avalon.error('Invalid Input!')

        print(avalon.FM.BD + '\nEnable SCUTUM iptables firewall?' + avalon.FM.RST)
        print('This firewall uses linux iptables to establish a relatively secure environment')
        print('However, professional firewall softwares like ufw is recommended')
        print('Enable this only if you don\'t have a firewall already')
        avalon.warning('This feature will erase all existing iptables settings!')
        if avalon.ask('Enable?', False):
            config["Iptables"]["enabled"] = "true"
        else:
            config["Iptables"]["enabled"] = "false"
        with open(self.CONFPATH, 'w') as configfile:
            config.write(configfile)  # Writes configurations
