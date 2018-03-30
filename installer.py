#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: SCUTUM Installer Class
Author: K4YT3X
Date Created: Sep 26, 2017
Last Modified: Mar 30, 2018

Description: Handles the installation, removal, configuring and
upgrading for SCUTUM

Version 1.8
"""
from iptables import Ufw
import avalon_framework as avalon
import configparser
import os
import shutil
import subprocess
import urllib.response


class Installer():

    def __init__(self, CONFPATH="/etc/scutum.conf", INSTALL_DIR="/usr/share/scutum"):
        self.SCUTUM_BIN_FILE = "/usr/bin/scutum"
        self.CONFPATH = CONFPATH
        self.INSTALL_DIR = INSTALL_DIR
        self.INSTALLER_DIR = os.path.dirname(os.path.realpath(__file__))

    def install_service(self):
        if os.path.isdir("/etc/init.d/"):
            """
            This is for debian-based systems. On debian, only an executable
            script/file is needed. This file is usually in /etc/inid.d/ and
            registered with update-rc.d. The service (unit) files will be
            created automagically.
            """
            shutil.copyfile(self.INSTALL_DIR + "/scutum", "/etc/init.d/scutum")
            os.system("chmod 755 /etc/init.d/scutum")
            os.system("update-rc.d scutum defaults")
            # runlevels are now defined in the executable files in newer versions
            # of systemd. Keeping this line for older systems
            os.system("update-rc.d scutum start 10 2 3 4 5 . stop 90 0 1 6 .")
        elif os.path.isdir("/usr/lib/systemd"):
            """
            This is for the old-fashion systemds. In old (maybe I'm wrong)
            systemds, unit files are created manually. They are stored in
            /usr/lib/systemd/system/ folder. systemctl command will look
            for service files in that folder.
            """
            shutil.copyfile(self.INSTALL_DIR + "/scutum.service", "/usr/lib/systemd/system/scutum.service")
            if os.path.islink("/etc/systemd/system/multi-user.target.wants/scutum.service"):
                # Let's just remove it in case of program structure update.
                os.remove("/etc/systemd/system/multi-user.target.wants/scutum.service")
            os.system("ln -s /usr/lib/systemd/system/scutum.service /etc/systemd/system/multi-user.target.wants/scutum.service")

    def check_version(self, VERSION):
        """
        Arguments:
            VERSION {string} -- version number

        Returns:
            string -- server version number
        """
        avalon.info(avalon.FM.RST + 'Checking SCUTUM Version...')
        with urllib.request.urlopen('https://raw.githubusercontent.com/K4YT3X/SCUTUM/master/scutum.py') as response:
            html = response.read().decode().split('\n')
            for line in html:
                if 'VERSION = ' in line:
                    server_version = line.split(' ')[-1].replace('\'', '')
                    break
            avalon.subLevelTimeInfo('Server version: ' + server_version)
            if server_version > VERSION:
                avalon.info('There\'s a newer version of SCUTUM!')
                if avalon.ask('Update to the newest version?'):
                    script_url = 'https://raw.githubusercontent.com/K4YT3X/SCUTUM/master/quickinstall.sh'
                    if not os.system("which curl"):
                        os.system("sudo sh -c \"$(curl -fsSL {})\"".format(script_url))
                    elif not os.system("which wget"):
                        os.system("sudo sh -c \"$(wget {} -O -)\"".format(script_url))
                    else:
                        urllib.request.urlretrieve(script_url, '/tmp/quickinstall.sh')
                        os.system('sudo bash /tmp/quickinstall.sh')
                else:
                    avalon.warning('Ignoring update')
            else:
                avalon.info('SCUTUM is already on the newest version')
        return server_version

    def check_avalon(self):
        """
        Check avalon version and update avalon_framework
        if necessary
        """
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
        """Install a package using the system package manager

        This method will look for available system package managers
        and install the package using package manager.

        Arguments:
            package {string} -- the name of the package to install

        Returns:
            bool -- true if installed successfully
        """
        if avalon.ask('Install ' + package + '?', True):
            if os.path.isfile('/usr/bin/apt'):
                os.system('apt update && apt install ' + package + ' -y')  # install the package with apt
                return True
            elif os.path.isfile('/usr/bin/yum'):
                os.system('yum install ' + package + ' -y')  # install the package with yum
                return True
            elif os.path.isfile('/usr/bin/pacman'):
                os.system('pacman -S ' + package + ' --noconfirm')  # install the package with pacman
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
            nmScript.write("#!/usr/bin/env python3\n")
            nmScript.write("\n")
            nmScript.write("import sys\n")
            nmScript.write("import os\n")
            nmScript.write("\n")
            nmScript.write("try:\n")
            nmScript.write("    interface = sys.argv[1]\n")
            nmScript.write("    status = sys.argv[2]\n")
            nmScript.write("except IndexError:\n")
            nmScript.write("    exit(0)\n")
            nmScript.write("\n")
            nmScript.write("if status == \"down\":\n")
            nmScript.write("    os.system(\"scutum --reset\")\n")
            nmScript.write("    exit(0)\n")
            nmScript.write("\n")
            nmScript.write("if status == \"up\":\n")
            nmScript.write("    os.system(\"scutum\")\n")
            nmScript.write("    exit(0)\n")
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
        self.removeWicdScripts()
        self.removeNMScripts()
        os.system("ufw --force reset")  # Reset ufw configurations
        os.system("rm -f /etc/ufw/*.*.*")  # Delete automatic backups

        RMLIST = ['/usr/bin/scutum', self.INSTALL_DIR, self.CONFPATH, '/var/log/scutum.log',
                  '/usr/lib/systemd/system/scutum.service', '/etc/init.d/scutum',
                  '/etc/systemd/system/multi-user.target.wants/scutum.service']

        for path in RMLIST:
            if os.path.isfile(path) or os.path.islink(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)

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

        print(avalon.FM.BD + "Choose Installation Directory (Enter for default)" + avalon.FM.RST)
        installation_dir = avalon.gets("Choose Installation Path (\"/usr/share/scutum\"):")
        if installation_dir.strip(" ") != "" and installation_dir[-1] == "/":
            self.INSTALL_DIR = installation_dir[0:-1]  # strip last "/" if exists. breaks program path format
            avalon.info("Changed installation directory to: {}{}{}".format(avalon.FM.BD, self.INSTALL_DIR, avalon.FM.RST))
        elif installation_dir.strip(" ") != "":
            self.INSTALL_DIR = installation_dir
            avalon.info("Changed installation directory to: {}{}{}".format(avalon.FM.BD, self.INSTALL_DIR, avalon.FM.RST))
        else:
            avalon.info("Using default installation directory: {}{}{}".format(avalon.FM.BD, self.INSTALL_DIR, avalon.FM.RST))

        if self.INSTALLER_DIR != self.INSTALL_DIR:
            if os.path.isdir(self.INSTALL_DIR):
                shutil.rmtree(self.INSTALL_DIR)  # delete existing old scutum files
            shutil.copytree(self.INSTALLER_DIR, self.INSTALL_DIR)

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
            config["Ufw"]["handled"] = "false"
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
