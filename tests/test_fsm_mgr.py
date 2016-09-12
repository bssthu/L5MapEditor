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

    def test_change_fsm(self):
        self.assertEqual(str(self.fsm.get_current_state()), 'empty')

        result = self.fsm.change_fsm('empty', 'normal')
        self.assertTrue(result)
        self.assertEqual(str(self.fsm.get_current_state()), 'normal')

        result = self.fsm.change_fsm('normal', 'empty')
        self.assertTrue(result)
        self.assertEqual(str(self.fsm.get_current_state()), 'empty')

    def test_change_fsm_fail(self):
        # current name not equal
        result = self.fsm.change_fsm('normal', 'empty')
        self.assertFalse(result)
        self.assertEqual(str(self.fsm.get_current_state()), 'empty')

        # next name not valid
        result = self.fsm.change_fsm('empty', 'insert')
        self.assertFalse(result)
        self.assertEqual(str(self.fsm.get_current_state()), 'empty')
