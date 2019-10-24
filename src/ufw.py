#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: scutum ufw class
Author: K4YT3X
Date Created: Sep 15, 2017
Last Modified: September 23, 2019
"""

# built-in imports
import shutil

# local imports
from utils import Utils


class Ufw:

    def __init__(self):

        # if ufw binary is not found in PATH
        if shutil.which('ufw') is None:
            raise FileNotFoundError('ufw binary not found')
        else:
            self.ufw_binary = shutil.which('ufw')

    def enable(self):
        """ enable ufw firewall
        """
        self._initialize_rules()
        Utils.exec([self.ufw_binary, '--force', 'enable'])

    def disable(self):
        """ disable ufw firewall
        """
        self._reset()
        Utils.exec([self.ufw_binary, '--force', 'disable'])

    def _initialize_rules(self):
        # reset current ufw rules
        self._reset()

        # set incoming to deny
        Utils.exec([self.ufw_binary, 'default', 'deny', 'incoming'])

        # set outgoing to allow
        Utils.exec([self.ufw_binary, 'default', 'allow', 'outgoing'])

    def _reset(self):
        # reset ufw configurations
        Utils.exec([self.ufw_binary, '--force', 'reset'])

        # delete automatic backups
        Utils.exec(['rm', '-f', '/etc/ufw/*.*.*'])
