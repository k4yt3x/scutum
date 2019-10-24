#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: scutum utils class
Author: K4YT3X
Date Created: September 23, 2019
Last Modified: September 23, 2019
"""

# built-in imports
import subprocess

# third-party imports
from avalon_framework import Avalon


class Utils:

    @staticmethod
    def exec(command: list, **kwargs):
        Avalon.debug_info(f'Executing: {" ".join(command)}')
        return subprocess.run(command, **kwargs).returncode

    @staticmethod
    def get_exec_output(command: list, **kwargs):
        Avalon.debug_info(f'Executing: {" ".join(command)}')
        return subprocess.check_output(command, **kwargs).decode()
