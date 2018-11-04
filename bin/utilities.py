#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: K4YT3X Generic Utilities
Author: K4YT3X
Date Created: October 19, 2018
Last Modified: November 4, 2018

Description: This class contains some useful utilities.
"""
from avalon_framework import Avalon
import os
import shutil
import subprocess
import sys

VERSION = '1.0.2'


class Utilities:
    """ Useful utilities

    This class contains a number of utility tools.
    """

    def execute(command, std_in='', std_out=subprocess.PIPE, std_err=subprocess.PIPE):
        """ Execute a system command and return the output
        """
        if type(std_in) is str:
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=std_out, stderr=std_err)
            return process.communicate(input=std_in)[0].decode().split('\n')
        else:
            process = subprocess.Popen(command, stdin=sys.stdin, stdout=std_out, stderr=std_err)
            return process.communicate()[0].decode().split('\n')

    def install_packages(packages):
        """ Install a package using system package manager
        """
        Avalon.warning('If the installation is unsuccessful, you should consider updating the package manager cache', log=False)
        if Avalon.ask('Install {}?'.format(' '.join(packages)), True):
            if shutil.which('apt-get'):
                os.system('apt-get install {} -y'.format(' '.join(packages)))
                return True
            elif shutil.which('yum'):
                os.system('yum install {} -y'.format(' '.join(packages)))
                return True
            elif shutil.which('pacman'):
                os.system('pacman -S {} --noconfirm'.format(' '.join(packages)))
                return True
            else:
                Avalon.error('Sorry, we can\'t find a package manager that we currently support. Aborting..')
                Avalon.error('Currently Supported: apt, yum, pacman')
                return False
        else:
            return False
