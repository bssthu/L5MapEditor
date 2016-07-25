#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : dao_polygon.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2016-07-25
# Description   :
#


from editor import log


def create_dao_polygon_table(polygons):
    """从来自数据库的数据 list 创建 Polygon 表

    Args:
        polygons: list of [polygon_id, layer, vertex_num, <str>vertices]

    Returns:
        polygon_table: {polygon_id, DaoPolygon}
    """
    polygon_table = {}
    for polygon in polygons:
        dao_polygon = DaoPolygon(polygon)
        polygon_table[dao_polygon.polygon_id] = dao_polygon
    return polygon_table


class DaoPolygon:
    """一个 Polygon

    Attributes:
        polygon_id: 多边形的 id
        layer: 多边形所属层
        vertex_num: 该多边形的顶点数量

    """
    def __init__(self, polygon):
        """构造函数

        Args:
            polygon: [polygon_id, layer, vertex_num, <str>vertices]
        """
        self.polygon_id = polygon[0]
        self.layer = polygon[1]
        vertex_str_list = polygon[3].strip().strip(';')
        if vertex_str_list == '':
            self.vertices = []
            self.vertex_num = 0
        else:
            # vertex_list: [[float, float], [float, float], ...]
            vertex_list = [[float(v.strip()) for v in pt_str.strip().split(',')]
                           for pt_str in vertex_str_list.strip().split(';')]
            # self.vertices: [DaoPoint, DaoPoint, ...]
            self.vertices = [DaoPoint(x, y) for x, y in vertex_list]
            self.vertex_num = len(self.vertices)
        if self.vertex_num != polygon[2]:
            log.debug('polygon %d: expect %d vertices, find %d.' % (self.polygon_id, polygon[2], self.vertex_num))

    def to_list(self):
        """转换为 list, 准备写回数据库

        Returns:
            [polygon_id, layer, vertex_num, <str>vertices]
        """
        vertex_str = ';'.join(('%f,%f' % (pt.x, pt.y) for pt in self.vertices))
        return [self.polygon_id, self.layer, self.vertex_num, vertex_str]


class DaoPoint:
    """Polygon 中的一个点"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

