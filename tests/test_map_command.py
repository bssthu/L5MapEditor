#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : test_map_command.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2016-09-13
# Description   :
#


import unittest
from unittest.mock import patch
from editor.map_command import MapCommand, CommandNotValidException
from dao.db_loader import create_dao_polygon_table
from dao.db_helper import DbHelper


class TestMapCommand(unittest.TestCase):
    def setUp(self):
        polygons = [
            [1, 2, 1, '1,2'],
        ]
        layers = [
            [[1, 6, 'desc'], ],
        ]
        polygon_table = create_dao_polygon_table(polygons, layers)

        self.helper = DbHelper()
        self.helper.polygon_table = polygon_table
        self.cmd = MapCommand(self.helper)

    def test_execute_exception(self):
        self.assertRaises(CommandNotValidException, self.cmd.execute, 'goto')
        self.assertRaises(CommandNotValidException, self.cmd.execute, 'goto shape 1 1')
        self.assertRaises(CommandNotValidException, self.cmd.execute, 'goto shap 1')
        self.assertRaises(CommandNotValidException, self.cmd.execute, 'del shape -1')

    def test_undo_redo(self):
        with patch.object(MapCommand, 'execute', wraps=self.cmd.execute) as fake_execute:
            with patch.object(MapCommand, 'execute_commands', wraps=self.cmd.execute_commands) as fake_commands:
                with patch.object(MapCommand, 'execute_single_command', wraps=self.cmd.execute_single_command) \
                        as fake_single:
                    self.assertEqual(0, fake_execute.call_count)
                    self.assertEqual(0, fake_commands.call_count)
                    self.assertEqual(0, fake_single.call_count)
                    self.cmd.execute('goto shape 1')
                    self.assertEqual(1, fake_execute.call_count)
                    self.assertEqual(1, fake_commands.call_count)
                    self.assertEqual(1, fake_single.call_count)
                    self.cmd.execute(['goto shape 1', 'goto shape 1'])
                    self.assertEqual(2, fake_execute.call_count)
                    self.assertEqual(2, fake_commands.call_count)
                    self.assertEqual(3, fake_single.call_count)
                    self.assertEqual(2, len(self.cmd.command_history))

                    # 撤销后的次数
                    self.cmd.undo()
                    self.assertEqual(1, len(self.cmd.command_history))
                    self.cmd.redo()
                    self.assertEqual(2, len(self.cmd.command_history))
                    self.cmd.redo()
                    self.assertEqual(2, len(self.cmd.command_history))

                    self.cmd.undo()
                    self.assertEqual(1, len(self.cmd.command_history))
                    self.cmd.undo()
                    self.assertEqual(0, len(self.cmd.command_history))
                    self.cmd.undo()
                    self.assertEqual(0, len(self.cmd.command_history))
                    self.cmd.redo()
                    self.assertEqual(1, len(self.cmd.command_history))

    def test_get_spare_id(self):
        self.assertEqual(2, self.cmd.get_spare_id(1))
        self.assertEqual(3, self.cmd.get_spare_id(3))

    def test_add_shape(self):
        with patch.object(MapCommand, 'execute_add_polygon', wraps=self.cmd.execute_add_polygon) as fake_add:
            self.cmd.command_tree = self.cmd.init_command_tree()
            self.assertEqual(0, fake_add.call_count)
            self.cmd.execute('add shape 2 1 0 1')
            self.assertEqual(1, fake_add.call_count)
            self.cmd.execute('add shape 3 0 name')
            self.assertEqual(2, fake_add.call_count)
            self.assertEqual([2, 1], self.helper.polygon_table[1].traversal_post_order())
            self.assertEqual([3,], self.helper.polygon_table[3].traversal_post_order())

    def test_add_point(self):
        with patch.object(MapCommand, 'execute_add_point', wraps=self.cmd.execute_add_point) as fake_add:
            self.cmd.command_tree = self.cmd.init_command_tree()
            self.assertEqual(0, fake_add.call_count)
            self.cmd.execute('add pt 1 0.0 0.5')
            self.assertEqual(1, fake_add.call_count)
            vertices = [[v.x, v.y] for v in self.helper.polygon_table[1].vertices]
            self.assertEqual([[1, 2], [0.0, 0.5]], vertices)
            self.assertRaises(CommandNotValidException, self.cmd.execute, 'add pt 2 0.0 0.5')

    def test_delete_shape(self):
        with patch.object(MapCommand, 'execute_remove_polygon', wraps=self.cmd.execute_remove_polygon) as fake_rm:
            self.cmd.command_tree = self.cmd.init_command_tree()
            self.assertEqual(0, fake_rm.call_count)
            self.cmd.execute('del shape 1')
            self.assertEqual(1, fake_rm.call_count)
            self.assertEqual(0, len(self.helper.polygon_table))
            self.assertRaises(CommandNotValidException, self.cmd.execute, 'del shape 2')

    def test_move_point(self):
        with patch.object(MapCommand, 'execute_move_point', wraps=self.cmd.execute_move_point) as fake_move:
            self.cmd.command_tree = self.cmd.init_command_tree()
            self.assertEqual(0, fake_move.call_count)
            self.cmd.execute('mov pt 1 0 1.0 1.5')
            self.assertEqual(1, fake_move.call_count)
            vertices = [[v.x, v.y] for v in self.helper.polygon_table[1].vertices]
            self.assertEqual([[2.0, 3.5], ], vertices)
            self.assertRaises(CommandNotValidException, self.cmd.execute, 'mov pt 2 4 1.0 1.5')

    def test_move_shape(self):
        with patch.object(MapCommand, 'execute_move_polygon', wraps=self.cmd.execute_move_polygon) as fake_move:
            self.cmd.command_tree = self.cmd.init_command_tree()
            self.assertEqual(0, fake_move.call_count)
            self.cmd.execute('mov shape 1 1.0 1.5')
            self.assertEqual(1, fake_move.call_count)
            vertices = [[v.x, v.y] for v in self.helper.polygon_table[1].vertices]
            self.assertEqual([[2.0, 3.5], ], vertices)
            self.assertRaises(CommandNotValidException, self.cmd.execute, 'mov shape 2 1.0 1.5')

    def test_set_point(self):
        with patch.object(MapCommand, 'execute_set_point', wraps=self.cmd.execute_set_point) as fake_set:
            self.cmd.command_tree = self.cmd.init_command_tree()
            self.assertEqual(0, fake_set.call_count)
            self.cmd.execute('set pt 1 0 1.0 1.5')
            self.assertEqual(1, fake_set.call_count)
            vertices = [[v.x, v.y] for v in self.helper.polygon_table[1].vertices]
            self.assertEqual([[1.0, 1.5], ], vertices)
            self.assertRaises(CommandNotValidException, self.cmd.execute, 'set pt 2 0 1.0 1.5')
