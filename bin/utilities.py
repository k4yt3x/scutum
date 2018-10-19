#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: SCUTUM Utilities
Author: K4YT3X
Date Created: October 19, 2018
Last Modified: October 19, 2018

Description: This class contains some useful utilities.

Version 1.0.0
"""
from avalon_framework import Avalon
import shutil
import subprocess
import sys


class Utilities:
    """ Useful utilities

    This class contains a number of utility tools.
    """

    def execute(command, input_value=''):
        """ Execute a system command and return the output
        """
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=sys.stdout)
        return process.communicate(input=input_value)[0].decode().split('\n')

    def install_package(package):
        """ Install a package using system package manager
        """
        if Avalon.ask('Install {}?'.format(package), True):
            if shutil.which('/usr/bin/apt') is not None:
                Utilities.execute(['apt', 'update', '&&', 'apt', 'install', package, '-y'])  # install arptables with apt
                return True
            elif shutil.which('/usr/bin/yum') is not None:
                Utilities.execute(['yum', 'install', package, '-y'])  # install arptables with yum
                return True
            elif shutil.which('/usr/bin/pacman') is not None:
                Utilities.execute(['pacman', '-S', package, '--noconfirm'])  # install arptables with pacman
                return True
            else:
                Avalon.error('Sorry, we can\'t find a package manager that we currently support. Aborting..')
                Avalon.error('Currently Supported: apt, yum, pacman')
                Avalon.error('Please come to SCUTUM\'s github page and comment if you know how to add support to another package manager')
                return False
        else:
            return False
