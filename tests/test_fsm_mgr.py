#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : test_fsm_mgr.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-09-30
# Description   :
#


import unittest
from editor import fsm_mgr


class TestFsmMgr(unittest.TestCase):
    def setUp(self):
        self.fsm = fsm_mgr.FsmMgr()

    def test_get_fsm(self):
        fsm_names = ('normal', 'empty', 'insert', 'move', 'move_point')
        for fsm_name in fsm_names:
            self.assertEqual(fsm_name, str(self.fsm.get_fsm(fsm_name)))
