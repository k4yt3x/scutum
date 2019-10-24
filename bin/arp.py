#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: scutum arp class
Author: K4YT3X
Date Created: September 23, 2019
Last Modified: October 1, 2019
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
        commands.append(['nft', 'add', 'chain', 'arp', 'filter', 'INPUT',
                         '{', 'type', 'filter', 'hook', 'input', 'priority', '0', ';', '}'])

        # create output chain
        commands.append(['nft', 'add', 'chain', 'arp', 'filter', 'OUTPUT',
                         '{', 'type', 'filter', 'hook', 'output', 'priority', '0', ';', '}'])

        # execute commands
        for command in commands:
            Utils.exec(command, check=True)

    def _arp_table_exists(self) -> bool:
        arp_rules = Utils.get_exec_output(['nft', 'list', 'ruleset', 'arp'])
        if arp_rules == '':
            return False
        return True

    def set_chain_default_policy(self, chain: ['INPUT', 'OUTPUT'], policy: ['accept', 'drop']):
        command = [
            'nft', 'chain', 'arp', 'filter', chain, '{', 'policy', policy, ';' '}'
        ]

        Utils.exec(command, check=True)

    def reset(self):
        Utils.exec(['nft', 'flush', 'chain', 'arp', 'filter', 'INPUT'], check=True)
        Utils.exec(['nft', 'flush', 'chain', 'arp', 'filter', 'OUTPUT'], check=True)

    def allow_mac(self, mac: str, interface: str):

        # if table arp filter if it doesn't exist
        # nftables sometimes doesn't come with all tables
        if not self._arp_table_exists():
            self._create_arp_table()

        command = ['nft', 'add', 'rule', 'arp', 'filter', 'INPUT',
                   'iif', interface,
                   'ether', 'saddr', '==', mac, 'accept'
                   ]

        Utils.exec(command, check=True)

    def discard_interface_rules(self, interface):
        Utils.get_exec_output(['nft', 'list', ''])
