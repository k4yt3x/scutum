#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: SCUTUM Installer Class
Author: K4YT3X
Date Created: September 26, 2017
Last Modified: November 4, 2018

Description: Handles the installation, removal, configuring and
upgrading for SCUTUM
"""
from avalon_framework import Avalon
from ufw import Ufw
from utilities import Utilities
import json
import os
import shutil

VERSION = '1.10.1'


class Installer():
    """ SCUTUM Installer

    This is the installer for SCUTUM. It handles
    all the installations, file installation and
    removal.
    """

    def __init__(self, CONFPATH='/etc/scutum.conf', INSTALL_DIR='/usr/share/scutum'):

        # Initialize constants
        self.SCUTUM_BIN_FILE = '/usr/bin/scutum'
        self.CONFPATH = CONFPATH
        self.INSTALL_DIR = INSTALL_DIR
        self.INSTALLER_DIR = os.path.dirname(os.path.realpath(__file__)).replace('/bin', '')
        self.DESKTOP_FILE = '/usr/share/applications/scutum-gui.desktop'

    def install_wicd_scripts(self):
        """ Write scutum scripts for WICD
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
        """ Write scutum scripts for Network Manager
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
        """ Remove WICD SCUTUM scripts
        """
        try:
            os.remove('/etc/wicd/scripts/postconnect/scutum_connect')
            os.remove('/etc/wicd/scripts/postdisconnect/scutum_disconnect')
        except FileNotFoundError:
            pass

    def remove_nm_scripts(self):
        """ Remove Network Manager SCUTUM scripts
        """
        try:
            os.remove('/etc/NetworkManager/dispatcher.d/scutum')
        except FileNotFoundError:
            pass

    def _install_scutum_files(self):
        """ Install all SCUTUM files into system
        """
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

        # If files are not already in place
        if self.INSTALLER_DIR != self.INSTALL_DIR:
            if os.path.isdir(self.INSTALL_DIR):
                shutil.rmtree(self.INSTALL_DIR)  # delete existing old scutum files
            shutil.copytree(self.INSTALLER_DIR, self.INSTALL_DIR)

        # Remove executable in PATH if exists
        if os.path.islink(self.SCUTUM_BIN_FILE) or os.path.isfile(self.SCUTUM_BIN_FILE):
            os.remove(self.SCUTUM_BIN_FILE)  # Remove old file or symbolic links

        # Link scutum main executable to PATH
        # This will allow user to use the "scutum" command
        Utilities.execute(['ln', '-s', '{}/bin/scutum.py'.format(self.INSTALL_DIR), self.SCUTUM_BIN_FILE])

    def _install_service(self):
        """ Install SCUTUM service
        """
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

        # Enable service
        Utilities.execute(['systemctl', 'enable', 'scutum'])
        Utilities.execute(['systemctl', 'start', 'scutum'])

    def _get_arp_controller_driver(self):
        """ Choose ARP controller driver
        """
        print(Avalon.FM.BD + '\nConfigure ARP Controller Driver' + Avalon.FM.RST)

        # Inform the user which driver is active on current system
        if shutil.which('nft'):
            Avalon.info('nftables is available')

        if shutil.which('arptables'):
            Avalon.info('arptables is available')

        while True:
            driver = Avalon.gets('Please choose an ARP controller driver (nftables/arptables): ')
            if driver == 'nftables' or driver == 'arptables':
                self.config['ArpController']['driver'] = driver
                break
            else:
                Avalon.error('Invalid ARP controller driver chosen')

    def _install_arp_controller_driver(self):
        """ Install the CLI tool if not installed
        """
        if self.config['ArpController']['driver'] == 'nftables':
            binary = 'nft'
        elif self.config['ArpController']['driver'] == 'arptables':
            binary = 'arptables'

        if shutil.which(binary) is None:
            Avalon.warning('ARP controller driver is not installed')
            if Avalon.ask('Install {} ?'.format(self.config['ArpController']['driver']), True):
                Utilities.install_packages(self.config['ArpController']['driver'])
            else:
                Avalon.error('ARP controller driver not installed')
                Avalon.error('SCUTUM relies on the driver to run')
                Avalon.error('Aborting installation')
                exit(1)

    def _get_controlled_interfaces(self):
        """ Get interfaces to be controlled by SCUTUM
        """

        # Get controlled interfaces
        ifaces_selected = []
        ifaces = []

        # List all available interfaces
        with open('/proc/net/dev', 'r') as dev:
            for line in dev:
                try:
                    if line.split(':')[1]:
                        ifaces.append(line.split(':')[0])
                except IndexError:
                    pass

        # Enroll controlled interfaces
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

        # Put controlled interfaces into configuraion
        self.config['Interfaces']['interfaces'] = ifaces_selected

    def _get_controlled_nm(self):
        """ Ask which network controller to hook to
        """
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
                self.config['NetworkControllers']['controllers'] = 'wicd'
                break
            elif selection == '2':
                if self.install_nm_scripts(self.config['Interfaces']['interfaces']) is not True:
                    Avalon.error('SCUTUM Script for NetworkManager has failed to install!')
                    Avalon.error('Aborting Installation...')
                    exit(1)
                self.config['NetworkControllers']['controllers'] = 'NetworkManager'
                break
            elif selection == '3':
                ifaces = ['wicd', 'NetworkManager']
                if self.install_wicd_scripts() is not True:
                    Avalon.warning('Deselected WICD from installation')
                    ifaces.remove('wicd')
                if self.install_nm_scripts(self.config['Interfaces']['interfaces']) is not True:
                    Avalon.warning('Deselected NetworkManager from installation')
                    ifaces.remove('NetworkManager')
                if len(ifaces) == 0:
                    Avalon.error('All SCUTUM Scripts have failed to install!')
                    Avalon.error('Aborting Installation...')
                    exit(1)
                self.config['NetworkControllers']['controllers'] = ifaces
                break
            else:
                Avalon.error('Invalid Input!')

    def _setup_ufw(self):
        """ Enable UFW to controll the firewall
        """
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
                self.config['Ufw']['handled'] = 'true'
            else:
                self.config['Ufw']['handled'] = 'false'
        else:
            self.config['Ufw']['handled'] = 'false'
            Avalon.info('You can turn it on whenever you change your mind')

    def _install_scutum_gui(self):
        """ Install SCUTUM GUI
        """
        print(Avalon.FM.BD + '\nInstall SCUTUM GUI?' + Avalon.FM.RST)
        print('SCUTUM GUI is convenient for GUI Interfaces')
        print('ex. KDE, GNOME, XFCE, etc.')
        print('However, there\'s not point to install GUI on servers')
        if Avalon.ask('Install SCUTUM GUI?', True):
            if os.path.islink(self.DESKTOP_FILE) or os.path.isfile(self.DESKTOP_FILE):
                os.remove(self.DESKTOP_FILE)
            Utilities.execute(['ln', '-s', '{}/res/scutum-gui.desktop'.format(self.INSTALL_DIR), self.DESKTOP_FILE])

    def install(self):
        """ Install SCUTUM

        This method will install all SCUTUM files and components
        """

        # Initialize configuration containers
        self.config = {}
        self.config['Interfaces'] = {}
        self.config['NetworkControllers'] = {}
        self.config['Ufw'] = {}
        self.config['ArpController'] = {}

        self._install_scutum_files()
        self._install_service()
        self._get_arp_controller_driver()
        self._install_arp_controller_driver()
        self._get_controlled_interfaces()
        self._get_controlled_nm()
        self._setup_ufw()
        self._install_scutum_gui()

        # Export the configuration into configuration file
        with open(self.CONFPATH, 'w') as configfile:
            json.dump(self.config, configfile, indent=2)
            configfile.close()

    def uninstall(self):
        """ Remove SCUTUM completely

        This method will remove all SCUTUM files from
        the system. It is yet to be tested completely.
        """
        self.remove_wicd_scripts()
        self.remove_nm_scripts()
        Utilities.execute(['ufw', '--force', 'reset'])  # Reset ufw configurations
        Utilities.execute(['rm', '-f', '/etc/ufw/*.*.*'])  # Delete automatic backups

        # A list of files, directories and links to remove
        rmlist = ['/usr/bin/scutum',
                  self.INSTALL_DIR,
                  self.CONFPATH,
                  '/var/log/scutum.log',
                  '/usr/lib/systemd/system/scutum.service', '/etc/init.d/scutum',
                  '/etc/systemd/system/multi-user.target.wants/scutum.service'
                  ]

        # Remove all files in rmlist
        for path in rmlist:
            if os.path.isfile(path) or os.path.islink(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)

        Avalon.info('SCUTUM removed successfully!')
        exit(0)
