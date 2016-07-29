#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : dao_polygon.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2016-07-25
# Description   :
#


from editor import log


class DaoPolygon:
    """一个 Polygon

    Attributes:
        polygon_id: 多边形的 id
        layer: 多边形所属层
        vertex_num: 该多边形的顶点数量
        vertices: 顶点
    """
    def __init__(self, polygon):
        """构造函数

        Args:
            polygon: [polygon_id, layer, vertex_num, <str>vertices]
        """

        self.polygon_id = int(polygon[0])
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

        # other attr
        self.name = ''
        self.additional = 0
        self.parent = None
        self.children = []

    def set_parent(self, parent):
        """设置 parent, 同时更新 parent 的 children 表

        Args:
            parent: parent DaoPolygon
        """
        # goodbye to old parent
        if (self.parent is not None) and (self in self.parent.children):
            self.parent.children.remove(self)
        # write new parent
        self.parent = parent
        # tell new parent
        if parent and self not in parent.children:
            parent.children.append(self)

    def add_child(self, child):
        """添加 child, 同时更新 child 的 parent 表

        不检查 child

        Args:
            child: child DaoPolygon
        """
        if child not in self.children:
            child.set_parent(self)

    def to_list(self):
        """转换为 list, 准备写回数据库

        Returns:
            [polygon_id, layer, vertex_num, <str>vertices]
        """
        vertex_str = ';'.join(('%f,%f' % (pt.x, pt.y) for pt in self.vertices))
        return [self.polygon_id, self.layer, self.vertex_num, vertex_str]

    def delete(self):
        """递归删除所有 children，以及自身"""
        deleted_id = []
        for child in self.children:
            deleted_id.extend(child.delete())
        deleted_id.extend(self.polygon_id)
        return deleted_id


class DaoPoint:
    """Polygon 中的一个点"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

