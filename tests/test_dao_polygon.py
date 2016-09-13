#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : test_dao_polygon.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2016-09-12
# Description   :
#


import unittest
from dao.dao_polygon import DaoPolygon, DaoPoint


class TestDaoPolygon(unittest.TestCase):
    def setUp(self):
        self.record_from_db_1 = [0, 0, 2, '1.0,2.0; 3.5,4.5']
        self.polygon1 = DaoPolygon(self.record_from_db_1)
        self.record_from_db_2 = [1, 2, 2, '6.0,7.0; 9.5,8.5']
        self.polygon2 = DaoPolygon(self.record_from_db_2)
        self.record_from_db_3 = [2, 2, 1, '4.0,5.5']
        self.polygon3 = DaoPolygon(self.record_from_db_3)

    def test_init_dao_polygon(self):
        self.assertIsNotNone(self.polygon1)
        self.assertIsNotNone(self.polygon2)

        polygon_id, layer, vertex_num, vertices = self.record_from_db_1
        # 测试空 vertices 字符串
        polygon4 = DaoPolygon([polygon_id, layer, vertex_num, ''])
        self.assertIsNotNone(polygon4)
        self.assertEqual(0, len(polygon4.vertices))
        # 测试错误的 vertex_num
        polygon5 = DaoPolygon([polygon_id, layer, 0, vertices])
        self.assertIsNotNone(polygon5)
        self.assertEqual(vertex_num, len(polygon5.vertices))

    def test_init_dao_point(self):
        point = DaoPoint(1, 2)
        self.assertEqual(1, point.x)
        self.assertEqual(2, point.y)

    def test_to_list(self):
        record_from_dao_polygon_a = self.polygon1.to_list()
        # 测试 list 的前3项是否相等
        self.assertEqual(record_from_dao_polygon_a[:3], self.record_from_db_1[:3])
        # 测试第四项转换成的 float 是否相等
        self.assertEqual(self.vertex_str_to_float(self.record_from_db_1[3]),
                         self.vertex_str_to_float(record_from_dao_polygon_a[3]))

        # 测试用 to_list 的结果再初始化 DaoPolygon
        polygon = DaoPolygon(record_from_dao_polygon_a)
        record_from_dao_polygon_b = polygon.to_list()
        self.assertEqual(record_from_dao_polygon_a, record_from_dao_polygon_b)
        self.assertEqual(self.vertex_str_to_float(record_from_dao_polygon_a[3]),
                         self.vertex_str_to_float(record_from_dao_polygon_b[3]))

    def test_add_child(self):
        # 测试 add_child 对 parent, children 的影响
        self.polygon1.add_child(self.polygon2)
        self.assertIs(self.polygon1.children[0], self.polygon2)
        self.assertIs(self.polygon2.parent, self.polygon1)

        # 测试修改 parent 的影响
        self.polygon2.set_parent(self.polygon3)
        self.assertIs(self.polygon3.children[0], self.polygon2)
        self.assertIs(self.polygon2.parent, self.polygon3)
        self.assertEqual(0, len(self.polygon1.children))

        self.polygon2.set_parent(None)
        self.assertIsNone(self.polygon2.parent, self.polygon3)
        self.assertEqual(0, len(self.polygon3.children))

    def test_move(self):
        self.assertEqual([[1.0, 2.0], [3.5, 4.5]],
                         self.vertex_str_to_float(self.polygon1.to_list()[3]))
        # 测试移动单点
        self.polygon1.move(1, 2, 1)
        self.assertEqual([[1.0, 2.0], [4.5, 6.5]],
                         self.vertex_str_to_float(self.polygon1.to_list()[3]))
        # 测试移动整体
        self.polygon1.move(3, 4, None)
        self.assertEqual([[4.0, 6.0], [7.5, 10.5]],
                         self.vertex_str_to_float(self.polygon1.to_list()[3]))

    def test_add_vertex(self):
        self.assertEqual([[1.0, 2.0], [3.5, 4.5]],
                         self.vertex_str_to_float(self.polygon1.to_list()[3]))
        # 在最前面添加
        self.polygon1.add_vertex(-1, -2, 0)
        self.assertEqual([[-1.0, -2.0], [1.0, 2.0], [3.5, 4.5]],
                         self.vertex_str_to_float(self.polygon1.to_list()[3]))
        # 在中间添加
        self.polygon1.add_vertex(-3, -4, 2)
        self.assertEqual([[-1.0, -2.0], [1.0, 2.0], [-3, -4], [3.5, 4.5]],
                         self.vertex_str_to_float(self.polygon1.to_list()[3]))
        # 在结尾添加
        self.polygon1.add_vertex(-5, -6, -1)
        self.assertEqual([[-1.0, -2.0], [1.0, 2.0], [-3, -4], [3.5, 4.5], [-5, -6]],
                         self.vertex_str_to_float(self.polygon1.to_list()[3]))

    def test_remove_vertex(self):
        self.assertEqual([[1.0, 2.0], [3.5, 4.5]],
                         self.vertex_str_to_float(self.polygon1.to_list()[3]))
        # 删除一个
        self.polygon1.remove_vertex(1)
        self.assertEqual([[1.0, 2.0]],
                         self.vertex_str_to_float(self.polygon1.to_list()[3]))
        # 删除失败
        self.polygon1.remove_vertex(1)
        self.assertEqual([[1.0, 2.0]],
                         self.vertex_str_to_float(self.polygon1.to_list()[3]))

    def test_set_vertex(self):
        self.assertEqual([[1.0, 2.0], [3.5, 4.5]],
                         self.vertex_str_to_float(self.polygon1.to_list()[3]))
        # 设置一个
        self.polygon1.set_vertex(-1, -2, 1)
        self.assertEqual([[1.0, 2.0], [-1, -2]],
                         self.vertex_str_to_float(self.polygon1.to_list()[3]))
        # 设置失败
        self.polygon1.set_vertex(-3, -4, -1)
        self.assertEqual([[1.0, 2.0], [-1, -2]],
                         self.vertex_str_to_float(self.polygon1.to_list()[3]))

    def test_traversal_post_order(self):
        self.assertEqual(0, self.polygon1.polygon_id)
        self.assertEqual(1, self.polygon2.polygon_id)
        self.assertEqual(2, self.polygon3.polygon_id)
        self.polygon1.add_child(self.polygon2)
        self.polygon1.add_child(self.polygon3)
        self.assertEqual([1, 2, 0],
                         self.polygon1.traversal_post_order())
        self.assertEqual([1],
                         self.polygon2.traversal_post_order())

    def test_get_com(self):
        self.assertEqual((2.25, 3.25), self.polygon1.get_com())
        self.assertEqual((7.75, 7.75), self.polygon2.get_com())
        self.assertEqual((4.0, 5.5), self.polygon3.get_com())
        # 异常的 DaoPolygon
        polygon4 = DaoPolygon([4, 3, 0, '1,2'])
        self.assertEqual((1.0, 2.0), polygon4.get_com())
        polygon5 = DaoPolygon([4, 3, 2, ''])
        self.assertEqual((0.0, 0.0), polygon5.get_com())

    @staticmethod
    def vertex_str_to_float(vertex_str_list):
        return [[float(v.strip()) for v in pt_str.strip().split(',')]
                for pt_str in vertex_str_list.strip().split(';')]
