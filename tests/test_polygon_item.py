#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : test_polygon_item.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2016-09-13
# Description   :
#


import unittest
from unittest import mock
from PyQt5.QtCore import QPointF
from dao.dao_polygon import DaoPolygon
from editor.polygon_base import PolygonBase
from editor.polygon_item import PolygonItem
from editor.polygon_new import PolygonNew
from editor.polygon_select import PolygonSelect


class TestPolygonItem(unittest.TestCase):
    def setUp(self):
        pass

    def test_polygon_base(self):
        polygon = PolygonBase()
        polygon.MAR = 100
        self.assertTrue(polygon.boundingRect().isNull())

        # test update_bounding_rect
        polygon.update_bounding_rect(QPointF(3, 4))
        self.assertFalse(polygon.boundingRect().isNull())
        self.assertEqual(-100 + 3, polygon.boundingRect().x())
        self.assertEqual(-100 + 4, polygon.boundingRect().y())
        self.assertEqual(200, polygon.boundingRect().width())
        self.assertEqual(200, polygon.boundingRect().height())

        polygon.update_bounding_rect(QPointF(-3, 4))
        self.assertEqual(-100 - 3, polygon.boundingRect().x())
        self.assertEqual(-100 + 4, polygon.boundingRect().y())
        self.assertEqual(206, polygon.boundingRect().width())
        self.assertEqual(200, polygon.boundingRect().height())

        # test move_bounding_rect
        polygon.move_bounding_rect(QPointF(10, 20))
        self.assertEqual(-100 - 3 + 10, polygon.boundingRect().x())
        self.assertEqual(-100 + 4 + 20, polygon.boundingRect().y())
        self.assertEqual(206, polygon.boundingRect().width())
        self.assertEqual(200, polygon.boundingRect().height())

    def test_polygon_item(self):
        polygon1 = PolygonItem(DaoPolygon([0, 0, 2, '1.0,2.0; 3.5,5.5']))
        self.assertEqual([[1.0, 2.0], [3.5, 5.5]], polygon1.get_vertices())

        self.assertEqual(50, polygon1.MAR)
        self.assertEqual(-50 + 1, polygon1.boundingRect().x())
        self.assertEqual(-50 + 2, polygon1.boundingRect().y())
        self.assertEqual(102.5, polygon1.boundingRect().width())
        self.assertEqual(103.5, polygon1.boundingRect().height())

        polygon2 = PolygonItem(DaoPolygon([0, 0, 2, '']))
        self.assertEqual([], polygon2.get_vertices())
        self.assertTrue(polygon2.boundingRect().isNull())

        painter = mock.MagicMock()
        polygon1.paint(painter, None)

    def test_polygon_new(self):
        polygon = PolygonNew()
        self.assertEqual(0, len(polygon.points))

        polygon.pre_add_point(QPointF(2, 3))
        self.assertEqual(0, len(polygon.points))

        painter = mock.MagicMock()
        polygon.paint(painter, None)

        polygon.add_point(QPointF(4, 5))
        self.assertEqual(1, len(polygon.points))

        painter = mock.MagicMock()
        polygon.paint(painter, None)

        polygon.remove_point()
        self.assertEqual(0, len(polygon.points))
        polygon.remove_point()
        self.assertEqual(0, len(polygon.points))

        painter = mock.MagicMock()
        polygon.paint(painter, None)

    def test_polygon_select(self):
        polygon = PolygonSelect(DaoPolygon([0, 0, 2, '1.0,2.0; 3.5,5.5']))

        # 暂时不随着图形移动，编辑操作完成后直接重建 PolygonSelect
        polygon.setScale(1)
        self.assertEqual(20, polygon.MAR)
        self.assertEqual(-polygon.MAR + 1, polygon.dots_rect.x())
        self.assertEqual(-polygon.MAR + 2, polygon.dots_rect.y())
        self.assertEqual(polygon.MAR * 2 + 2.5, polygon.dots_rect.width())
        self.assertEqual(polygon.MAR * 2 + 3.5, polygon.dots_rect.height())
        polygon.setScale(2)
        self.assertEqual(10, polygon.MAR)
        self.assertEqual(-polygon.MAR + 1, polygon.dots_rect.x())
        self.assertEqual(-polygon.MAR + 2, polygon.dots_rect.y())
        self.assertEqual(polygon.MAR * 2 + 2.5, polygon.dots_rect.width())
        self.assertEqual(polygon.MAR * 2 + 3.5, polygon.dots_rect.height())

        polygon.set_offset(QPointF(1, 2))
        self.assertEqual([[1.0, 2.0], [3.5, 5.5]], polygon.get_vertices())

        polygon.apply_offset(QPointF(5, 6))
        self.assertEqual([[6.0, 8.0], [8.5, 11.5]], polygon.get_vertices())

        polygon.reset_offset()
        self.assertEqual([[1.0, 2.0], [3.5, 5.5]], polygon.get_vertices())

        PolygonBase.move_point = True
        polygon.set_point_id(1)
        polygon.apply_offset(QPointF(10, 20))
        self.assertEqual([[1.0, 2.0], [13.5, 25.5]], polygon.get_vertices())

        polygon.confirm_offset()
        polygon.reset_offset()
        self.assertEqual([[1.0, 2.0], [13.5, 25.5]], polygon.get_vertices())

        painter = mock.MagicMock()
        polygon.paint(painter, None)

