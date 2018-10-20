#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: SCUTUM Installer Class
Author: K4YT3X
Date Created: September 26, 2017
Last Modified: October 19, 2018

Description: Handles the installation, removal, configuring and
upgrading for SCUTUM
"""
from avalon_framework import Avalon
from ufw import Ufw
from utilities import Utilities
import configparser
import os
import shutil
import subprocess
import urllib.request

VERSION = '1.9.6'


class Installer():

    def __init__(self, CONFPATH='/etc/scutum.conf', INSTALL_DIR='/usr/share/scutum'):
        self.SCUTUM_BIN_FILE = '/usr/bin/scutum'
        self.CONFPATH = CONFPATH
        self.INSTALL_DIR = INSTALL_DIR
        self.INSTALLER_DIR = os.path.dirname(os.path.realpath(__file__)).replace('/bin', '')

    def install_service(self):
        if os.path.isdir('/etc/init.d/'):
            """
            This is for debian-based systems. On debian, only an executable
            script/file is needed. This file is usually in /etc/inid.d/ and
            registered with update-rc.d. The service (unit) files will be
            created automagically.
            """
            shutil.copyfile(self.INSTALL_DIR + '/bin/scutum', '/etc/init.d/scutum')
            Utilities.execute(['chmod', '755', '/etc/init.d/scutum'])
            Utilities.execute(['update-rc.d', 'scutum', 'defaults'])
            # runlevels are now defined in the executable files in newer versions
            # of systemd. Keeping this line for older systems
            Utilities.execute(['update-rc.d', 'scutum', 'start', '10', '2', '3', '4', '5', '.', 'stop', '90', '0', '1', '6', '.'])
        elif os.path.isdir('/usr/lib/systemd'):
            """
            This is for the old-fashion systemds. In old (maybe I'm wrong)
            systemds, unit files are created manually. They are stored in
            /usr/lib/systemd/system/ folder. systemctl command will look
            for service files in that folder.
            """
            shutil.copyfile(self.INSTALL_DIR + '/res/scutum.service', '/usr/lib/systemd/system/scutum.service')
            if os.path.islink('/etc/systemd/system/multi-user.target.wants/scutum.service'):
                # Let's just remove it in case of program structure update.
                os.remove('/etc/systemd/system/multi-user.target.wants/scutum.service')
            Utilities.execute(['ln', '-s', '/usr/lib/systemd/system/scutum.service', '/etc/systemd/system/multi-user.target.wants/scutum.service'])

    def check_version(self, VERSION):
        """
        Arguments:
            VERSION {string} -- version number

        Returns:
            string -- server version number
        """
        Avalon.info(Avalon.FM.RST + 'Checking SCUTUM Version...')
        with urllib.request.urlopen('https://raw.githubusercontent.com/K4YT3X/scutum/master/bin/scutum.py') as response:
            html = response.read().decode().split('\n')
            for line in html:
                if 'VERSION = ' in line:
                    server_version = line.split(' ')[-1].replace('\'', '')
                    break
            Avalon.debug_info('Server version: ' + server_version)
            if server_version > VERSION:
                Avalon.info('There\'s a newer version of SCUTUM!')
                if Avalon.ask('Update to the newest version?'):
                    script_url = 'https://raw.githubusercontent.com/K4YT3X/scutum/master/bin/quickinstall.sh'
                    if shutil.which('curl'):
                        Utilities.execute(['sudo', 'sh', '-c', '\"$(curl -fsSL {})\"'.format(script_url)])
                    elif shutil.which('wget'):
                        Utilities.execute(['sudo', 'sh', '-c', '\"$(wget {} -O -)\"'.format(script_url)])
                    else:
                        urllib.request.urlretrieve(script_url, '/tmp/quickinstall.sh')
                        Utilities.execute(['sudo', 'bash', '/tmp/quickinstall.sh'])
                else:
                    Avalon.warning('Ignoring update')
            else:
                Avalon.info('SCUTUM is already on the newest version')
        return server_version

    def check_avalon(self):
        """
        Check avalon version and update avalon_framework
        if necessary
        """
        Avalon.info(Avalon.FM.RST + 'Checking AVALON Framework Version...')
        if shutil.which('pip3') is None:
            Avalon.warning('pip3 not found, aborting version check')
            return
        avalon_version_check = subprocess.Popen(['pip3', 'freeze'], stdout=subprocess.PIPE).communicate()[0]
        pipOutput = avalon_version_check.decode().split('\n')
        for line in pipOutput:
            if 'avalon-framework' in line:
                local_version = line.split('==')[-1]

        with urllib.request.urlopen('https://raw.githubusercontent.com/K4YT3X/AVALON/master/__init__.py') as response:
            html = response.read().decode().split('\n')
            for line in html:
                if 'VERSION = ' in line:
                    server_version = line.split(' ')[-1].replace('\'', '')
                    break

        if server_version > local_version:
            Avalon.info('Here\'s a newer version of AVALON Framework: {}'.format(server_version))
            if Avalon.ask('Update to the newest version?', True):
                Utilities.execute(['pip3', 'install', '--upgrade', 'avalon_framework'])
            else:
                Avalon.warning('Ignoring update')
        else:
            Avalon.debug_info('Current version: ' + local_version)
            Avalon.info('AVALON Framework is already on the newest version')

    def install_wicd_scripts(self):
        """
        Write scutum scripts for WICD
        """
        print(Avalon.FG.G + '[+] INFO: Installing for WICD' + Avalon.FM.RST + '.....', end='')
        if not os.path.isdir('/etc/wicd/'):
            print(Avalon.FG.G + Avalon.FM.BD + 'ERROR' + Avalon.FM.RST)
            Avalon.warning('WICD folder not found! WICD does not appear to be installed!')
            if Avalon.ask('Continue anyway? (Create Directories)', False):
                Utilities.execute(['mkdir', '-p', '/etc/wicd/scripts/postconnect/'])
                Utilities.execute(['mkdir', '-p', '/etc/wicd/scripts/postdisconnect/'])
            else:
                Avalon.warning('Aborting installation for WICD')
                return False
        with open('/etc/wicd/scripts/postconnect/scutum_connect', 'w') as postconnect:
            postconnect.write('#!/bin/bash\n')
            postconnect.write('scutum')
            postconnect.close()
        with open('/etc/wicd/scripts/postdisconnect/scutum_disconnect', 'w') as postdisconnect:
            postdisconnect.write('#!/bin/bash\n')
            postdisconnect.write('scutum --reset')
            postdisconnect.close()
        Utilities.execute(['chown', 'root:', '/etc/wicd/scripts/postconnect/scutum_connect'])
        Utilities.execute(['chmod', '755', '/etc/wicd/scripts/postconnect/scutum_connect'])
        Utilities.execute(['chown', 'root:', '/etc/wicd/scripts/postdisconnect/scutum_disconnect'])
        Utilities.execute(['chmod', '755', '/etc/wicd/scripts/postdisconnect/scutum_disconnect'])
        print(Avalon.FG.G + Avalon.FM.BD + 'SUCCEED' + Avalon.FM.RST)
        return True

    def install_nm_scripts(self, interfaces):
        """
        Write scutum scripts for Network Manager
        """
        print(Avalon.FG.G + '[+] INFO: Installing for NetworkManager' + Avalon.FM.RST + '.....', end='')
        if not os.path.isdir('/etc/NetworkManager/dispatcher.d/'):
            print(Avalon.FG.G + Avalon.FM.BD + 'ERROR' + Avalon.FM.RST)
            Avalon.warning('NetworkManager folders not found! NetworkManager does not appear to be installed!')
            if Avalon.ask('Continue anyway? (Create Directories)', False):
                Utilities.execute(['mkdir', '-p', '/etc/NetworkManager/dispatcher.d/'])
            else:
                Avalon.warning('Aborting installation for NetworkManager')
                return False
        with open('/etc/NetworkManager/dispatcher.d/scutum', 'w') as nmScript:
            nmScript.write('#!/usr/bin/env python3\n')
            nmScript.write('\n')
            nmScript.write('import sys\n')
            nmScript.write('import os\n')
            nmScript.write('\n')
            nmScript.write('try:\n')
            nmScript.write('    interface = sys.argv[1]\n')
            nmScript.write('    status = sys.argv[2]\n')
            nmScript.write('except IndexError:\n')
            nmScript.write('    exit(0)\n')
            nmScript.write('\n')
            nmScript.write('if status == \"down\":\n')
            nmScript.write('    os.system(\"scutum --reset\")\n')
            nmScript.write('    exit(0)\n')
            nmScript.write('\n')
            nmScript.write('if status == \"up\":\n')
            nmScript.write('    os.system(\"scutum\")\n')
            nmScript.write('    exit(0)\n')
            nmScript.close()

        Utilities.execute(['chown', 'root:', '/etc/NetworkManager/dispatcher.d/scutum'])
        Utilities.execute(['chmod', '755', '/etc/NetworkManager/dispatcher.d/scutum'])
        print(Avalon.FG.G + Avalon.FM.BD + 'SUCCEED' + Avalon.FM.RST)
        return True

    def remove_wicd_scripts(self):
        try:
            os.remove('/etc/wicd/scripts/postconnect/scutum_connect')
            os.remove('/etc/wicd/scripts/postdisconnect/scutum_disconnect')
        except FileNotFoundError:
            pass

    def remove_nm_scripts(self):
        try:
            os.remove('/etc/NetworkManager/dispatcher.d/scutum')
        except FileNotFoundError:
            pass

    def remove_scutum(self):
        self.remove_wicd_scripts()
        self.remove_nm_scripts()
        Utilities.execute(['ufw', '--force', 'reset'])  # Reset ufw configurations
        Utilities.execute(['rm', '-f', '/etc/ufw/*.*.*'])  # Delete automatic backups

        RMLIST = ['/usr/bin/scutum', self.INSTALL_DIR, self.CONFPATH, '/var/log/scutum.log',
                  '/usr/lib/systemd/system/scutum.service', '/etc/init.d/scutum',
                  '/etc/systemd/system/multi-user.target.wants/scutum.service']

        for path in RMLIST:
            if os.path.isfile(path) or os.path.islink(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)

        Avalon.info('SCUTUM successfully removed!')
        exit(0)

    def install_scutum_gui(self):
        DESKTOP_FILE = '/usr/share/applications/scutum-gui.desktop'
        if os.path.islink(DESKTOP_FILE) or os.path.isfile(DESKTOP_FILE):
            os.remove(DESKTOP_FILE)
        Utilities.execute(['ln', '-s', '{}/res/scutum-gui.desktop'.format(self.INSTALL_DIR), DESKTOP_FILE])

    def install(self):
        """
        This is the main function for installer
        """
        config = configparser.ConfigParser()
        config['Interfaces'] = {}
        config['NetworkControllers'] = {}
        config['Ufw'] = {}

        print(Avalon.FM.BD + 'Choose Installation Directory (Enter for default)' + Avalon.FM.RST)
        installation_dir = Avalon.gets('Choose Installation Path (\"/usr/share/scutum\"):')
        if installation_dir.strip(' ') != '' and installation_dir[-1] == '/':
            self.INSTALL_DIR = installation_dir[0:-1]  # strip last '/' if exists. breaks program path format
            Avalon.info('Changed installation directory to: {}{}{}'.format(Avalon.FM.BD, self.INSTALL_DIR, Avalon.FM.RST))
        elif installation_dir.strip(' ') != '':
            self.INSTALL_DIR = installation_dir
            Avalon.info('Changed installation directory to: {}{}{}'.format(Avalon.FM.BD, self.INSTALL_DIR, Avalon.FM.RST))
        else:
            Avalon.info('Using default installation directory: {}{}{}'.format(Avalon.FM.BD, self.INSTALL_DIR, Avalon.FM.RST))

        if self.INSTALLER_DIR != self.INSTALL_DIR:
            if os.path.isdir(self.INSTALL_DIR):
                shutil.rmtree(self.INSTALL_DIR)  # delete existing old scutum files
            shutil.copytree(self.INSTALLER_DIR, self.INSTALL_DIR)

        if os.path.islink(self.SCUTUM_BIN_FILE) or os.path.isfile(self.SCUTUM_BIN_FILE):
            os.remove(self.SCUTUM_BIN_FILE)  # Remove old file or symbolic links

        Utilities.execute(['ln', '-s', '{}/bin/scutum.py'.format(self.INSTALL_DIR), self.SCUTUM_BIN_FILE])

        self.install_service()  # install and register service files
        Utilities.execute(['systemctl', 'enable', 'scutum'])  # enable service
        Utilities.execute(['systemctl', 'start', 'scutum'])  # start service

        if not os.path.isfile('/usr/bin/arptables') and not os.path.isfile('/sbin/arptables'):  # Detect if arptables installed
            print(Avalon.FM.BD + Avalon.FG.R + '\nWe have detected that you don\'t have arptables installed!' + Avalon.FM.RST)
            print('SCUTUM requires arptables to run')
            if not Utilities.install_package('arptables'):
                Avalon.error('arptables is required for scutum. Exiting...')
                exit(1)

        ifaces_selected = []
        ifaces = []
        with open('/proc/net/dev', 'r') as dev:
            for line in dev:
                try:
                    if line.split(':')[1]:
                        ifaces.append(line.split(':')[0])
                except IndexError:
                    pass
        while True:
            print(Avalon.FM.BD + '\nWhich interface do you want scutum to control?' + Avalon.FM.RST)
            if not len(ifaces) == 0:
                idx = 0
                for iface in ifaces:
                    if iface.replace(' ', '') not in ifaces_selected:
                        print('{}. {}'.format(str(idx), iface.replace(' ', '')))
                    idx += 1
            print('x. Manually Enter')
            print(Avalon.FM.BD + 'Press [ENTER] when complete' + Avalon.FM.RST)
            selection = Avalon.gets('Please select (index number): ')

            try:
                if selection == 'x':
                    manif = Avalon.gets('Interface: ')
                    if manif not in ifaces_selected:
                        ifaces_selected.append(manif)
                elif selection == '':
                    if len(ifaces_selected) != 0:
                        break
                    else:
                        Avalon.error('You have not selected any interfaces yet')
                elif int(selection) >= len(ifaces):
                    Avalon.error('Selected interface doesn\'t exist!')
                else:
                    ifaces_selected.append(ifaces[int(selection)].replace(' ', ''))

            except ValueError:
                Avalon.error('Invalid Input!')
                Avalon.error('Please enter the index number!')

        config['Interfaces']['interfaces'] = ','.join(ifaces_selected)

        while True:
            print(Avalon.FM.BD + '\nWhich network controller do you want to install for?' + Avalon.FM.RST)
            print('1. WICD')
            print('2. Network-Manager')
            print('3. Both')

            selection = Avalon.gets('Please select: (index number): ')

            if selection == '1':
                if self.install_wicd_scripts() is not True:
                    Avalon.error('SCUTUM Script for WICD has failed to install!')
                    Avalon.error('Aborting Installation...')
                    exit(1)
                config['NetworkControllers']['controllers'] = 'wicd'
                break
            elif selection == '2':
                if self.install_nm_scripts(ifaces_selected) is not True:
                    Avalon.error('SCUTUM Script for NetworkManager has failed to install!')
                    Avalon.error('Aborting Installation...')
                    exit(1)
                config['NetworkControllers']['controllers'] = 'NetworkManager'
                break
            elif selection == '3':
                ifaces = ['wicd', 'NetworkManager']
                if self.install_wicd_scripts() is not True:
                    Avalon.warning('Deselected WICD from installation')
                    ifaces.remove('wicd')
                if self.install_nm_scripts(ifaces_selected) is not True:
                    Avalon.warning('Deselected NetworkManager from installation')
                    ifaces.remove('NetworkManager')
                if len(ifaces) == 0:
                    Avalon.error('All SCUTUM Scripts have failed to install!')
                    Avalon.error('Aborting Installation...')
                    exit(1)
                config['NetworkControllers']['controllers'] = ','.join(ifaces)
                break
            else:
                Avalon.error('Invalid Input!')

        print(Avalon.FM.BD + '\nEnable UFW firewall?' + Avalon.FM.RST)
        print('Do you want SCUTUM to help configuring and enabling UFW firewall?')
        print('This will prevent a lot of scanning and attacks')
        if Avalon.ask('Enable?', True):
            ufwctrl = Ufw()
            print('UFW can configure UFW Firewall for you')
            print('However this will reset your current UFW configurations')
            print('It is recommended to do so the first time you install SCUTUM')
            if Avalon.ask('Let SCUTUM configure UFW for you?', True):
                ufwctrl.initialize(True)
            else:
                Avalon.info('Okay. Then we will simply enable it for you')
                ufwctrl.enable()

            print('If you let SCUTUM handle UFW, then UFW will be activated and deactivated with SCUTUM')
            if Avalon.ask('Let SCUTUM handle UFW?', True):
                config['Ufw']['handled'] = 'true'
            else:
                config['Ufw']['handled'] = 'false'
        else:
            config['Ufw']['handled'] = 'false'
            Avalon.info('You can turn it on whenever you change your mind')

        print(Avalon.FM.BD + '\nInstall SCUTUM GUI?' + Avalon.FM.RST)
        print('SCUTUM GUI is convenient for GUI Interfaces')
        print('ex. KDE, GNOME, XFCE, etc.')
        print('However, there\'s not point to install GUI on servers')
        if Avalon.ask('Install SCUTUM GUI?', True):
            self.install_scutum_gui()

        with open(self.CONFPATH, 'w') as configfile:
            config.write(configfile)  # Writes configurations
