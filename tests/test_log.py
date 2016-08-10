#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : test_log.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2016-01-26
# Description   :
#


import unittest
from editor import log


class TestLog(unittest.TestCase):
    def test_init(self):
        logger = log.Log()

    def test_log(self):
        log.debug('debug')
        log.info('info')
        log.warning('warning')
        log.error('error')
