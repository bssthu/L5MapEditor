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
        name: L0 名字
        additional: 类型
        parent: parent 指针
        children: list of child 指针
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

    def move(self, dx, dy, v_id=None):
        """整体平移或平移某点

        Args:
            dx: x 方向偏移
            dy: y 方向偏移
            v_id: 待移动点的索引, None 表示整体平移
        """
        if v_id is None:
            # 整体平移
            for vertex in self.vertices:
                vertex.move(dx, dy)
        else:
            # 移动某点
            self.vertices[v_id].move(dx, dy)

    def add_vertex(self, x, y, v_id=-1):
        """插入顶点

        Args:
            x: 新点 x 坐标
            y: 新点 x 坐标
            v_id: 新点插入位置，原 v_id 对应点后移。若 v_id 为负，则插入到最后。
        """
        if v_id >= 0:
            # 从中间插入点
            self.vertices[v_id:v_id] = DaoPoint(x, y)
        elif v_id < 0:
            # 从最后插入点
            self.vertices.append(DaoPoint(x, y))
        self.vertex_num = len(self.vertices)

    def remove_vertex(self, v_id):
        """删除顶点

        Args:
            v_id: 待删顶点索引，其后点前移
        """
        if 0 <= v_id < self.vertex_num:
            del self.vertices[v_id]
        self.vertex_num = len(self.vertices)

    def set_vertex(self, x, y, v_id):
        """设置顶点坐标

        Args:
            x: 新的 x 坐标
            y: 新的 x 坐标
            v_id: 顶点的索引
        """
        if 0 <= v_id < self.vertex_num:
            self.vertices[v_id].set(x, y)

    def traversal_post_order(self):
        """后续遍历递归

        可用于删除所有 children，以及自身

        Returns:
            list of 后续遍历得到的多边形索引
        """
        deleted_id = []
        for child in self.children:
            deleted_id.extend(child.traversal_post_order())
        deleted_id.append(self.polygon_id)
        return deleted_id


class DaoPoint:
    """Polygon 中的一个点"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def set(self, x, y):
        """移动

        Args:
            x: 新的 x 坐标
            y: 新的 y 坐标
        """
        self.x = x
        self.y = y

    def move(self, dx, dy):
        """移动

        Args:
            dx: x 方向偏移
            dy: y 方向偏移
        """
        self.x += dx
        self.y += dy
