#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : test_db_helper.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2016-09-12
# Description   :
#


import unittest
from dao.db_loader import *
from dao.db_helper import DbHelper


class TestDbHelper(unittest.TestCase):
    def setUp(self):
        self.polygons = [
            [1, 2, 1, '1,2'],
            [2, 2, 1, '3,4'],
            [4, 1, 1, '5,6'],
            [5, 1, 1, '5,6'],
            [6, 0, 1, '5,6'],
        ]
        self.layers = [
            [[1, 6, 'desc'], ],
            [[1, 4, 0, 6], [2, 5, 0, 6]],
            [[1, 1, 0, 4], [2, 2, 0, 5]],
            [],
        ]
        self.polygon_table = create_dao_polygon_table(self.polygons, self.layers)
        self.helper = DbHelper()
        self.helper.polygon_table = self.polygon_table

    def test_create_dao_polygon_table(self):
        # 测试能否从来自数据库的数据 list 创建 Polygon 表
        self.assertEqual(5, len(self.polygon_table))
        self.assertEqual([1, 4, 2, 5, 6], self.polygon_table[6].traversal_post_order())
        self.assertEqual(1, self.polygon_table[1].polygon_id)
        self.assertEqual(2, self.polygon_table[2].polygon_id)
        self.assertEqual(4, self.polygon_table[4].polygon_id)
        self.assertEqual(5, self.polygon_table[5].polygon_id)
        self.assertEqual(6, self.polygon_table[6].polygon_id)

    def test_get_polygon_by_id(self):
        self.assertEqual(4, self.helper.get_polygon_by_id(4).polygon_id)
        self.assertIsNone(self.helper.get_polygon_by_id(3))

    def test_get_children_table_by_id(self):
        self.assertEqual([4, 5], list(self.helper.get_children_table_by_id(6).keys()))
        self.assertEqual([2], list(self.helper.get_children_table_by_id(5).keys()))
        self.assertDictEqual({}, self.helper.get_children_table_by_id(2))
        self.assertIsNone(self.helper.get_children_table_by_id(8))

    def test_clear(self):
        self.helper.clear()
        self.assertDictEqual({}, self.helper.polygon_table)

    def test_delete_by_id(self):
        self.helper.delete_by_id(1)
        self.assertEqual([4, 2, 5, 6], self.polygon_table[6].traversal_post_order())
        self.helper.delete_by_id(5)
        self.assertEqual([4, 6], self.polygon_table[6].traversal_post_order())

    def test_add_polygon(self):
        self.assertEqual(5, len(self.helper.polygon_table))
        # L0
        self.helper.add_l0_polygon(9, 'new')
        self.assertEqual(6, len(self.helper.polygon_table))
        self.assertEqual(9, self.polygon_table[9].polygon_id)
        # Other
        self.helper.add_lp_polygon(10, 2, 0, 9)
        self.assertEqual(7, len(self.helper.polygon_table))
        self.assertEqual(10, self.polygon_table[10].polygon_id)
        self.assertEqual([10, 9], self.polygon_table[9].traversal_post_order())
