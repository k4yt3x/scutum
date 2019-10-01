#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: scutum arp class
Author: K4YT3X
Date Created: September 23, 2019
Last Modified: September 23, 2019
"""

# local imports
from utils import Utils


class Arp():

    def __init__(self):
        pass

    def _create_arp_table(self):
        commands = []

        # create arp filter table
        commands.append(['nft', 'add', 'table', 'arp', 'filter'])

        # create input chain
        commands.append([['nft', 'add', 'chain', 'arp', 'filter', 'INPUT',
                          '{', 'type', 'filter', 'hook', 'input', 'priority', '0', ';', '}']])

        # create output chain
        commands.append([['nft', 'add', 'chain', 'arp', 'filter', 'OUTPUT',
                          '{', 'type', 'filter', 'hook', 'output', 'priority', '0', ';', '}']])

        # execute commands
        for command in commands:
            Utils.exec(command, check=True)

    def _arp_table_exists(self) -> bool:
        return_code = Utils.exec(['nft', 'list', 'ruleset', 'arp'])
        if return_code == 0:
            return True
        return False

    def reset(self):
        Utils.exec(['nft', 'flush', 'chain', 'arp', 'filter', 'INPUT'], check=True)
        Utils.exec(['nft', 'flush', 'chain', 'arp', 'filter', 'OUTPUT'], check=True)

    def allow_mac(self, mac: str):

        # if table arp filter if it doesn't exist
        # nftables sometimes doesn't come with all tables
        if not self._arp_table_exists():
            self._create_arp_table()

        command = [
            'nft', 'add', 'rule', 'arp', 'filter', 'INPUT',
            'ether', 'saddr', '!=', mac, 'drop'
        ]

        Utils.exec(command, check=True)
