#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: SCUTUM Logger Class
Author: K4YT3X
Date Created: Sep 15, 2017
Last Modified: Sep 28, 2017

Description: Handles all the logging actions

This class is migrated from Project: DefenseMatrix
"""
import datetime
import os


class Logger:

    def __init__(self, LOGPATH=False):
        self.LOGPATH = LOGPATH

    def writeLog(self, content):
        if self.LOGPATH:
            with open(self.LOGPATH, "a+") as log:
                log.write(str(datetime.datetime.now()) + " " + str(content) + "\n")
                log.close()

    def purge(self):
        os.remove(self.LOGPATH)
