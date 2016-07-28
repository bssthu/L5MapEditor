#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : db_helper.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-09-24
# Description   :
#


import sqlite3

import dao.db_loader as db_loader
from editor import config_loader


class DbHelper:
    def __init__(self):
        self.polygon_table = {}

    def load_tables(self, file_path):
        """从文件载入 sqlite 数据库

        Args:
            file_path: 数据库路径
        """
        # clear
        self.clear()
        # load sqlite
        conn = sqlite3.connect(file_path)
        cur = conn.cursor()
        polygons = cur.execute('SELECT * FROM POLYGON').fetchall()
        polygons = [list(polygon) for polygon in polygons]
        layers = []
        for NAME in config_loader.getLayerNames():
            layer = cur.execute('SELECT * FROM %s' % NAME).fetchall()
            layer = [list(record) for record in layer]
            layers.append(layer)
        conn.close()
        # parse data
        self.polygon_table = db_loader.create_dao_polygon_table(polygons, layers)

    def write_to_file(self, file_path, polygons, layers):
        """将结果写入 sqlite 数据库

        Args:
            file_path: 数据库路径
        """
        LAYER_NAMES = config_loader.getLayerNames()
        conn = sqlite3.connect(file_path)
        cur = conn.cursor()
        # clear
        cur.execute('DELETE FROM POLYGON')
        for NAME in LAYER_NAMES:
            cur.execute('DELETE FROM %s' % NAME)
        # insert
        sql = 'INSERT INTO POLYGON (_id, layer, vertex_Num, vertices) VALUES (?,?,?,?)'
        for polygon in polygons:
            polygon_copy = polygon[0:3]
            vertex_str = ';\n'.join('%f,%f' % (vertex[0], vertex[1]) for vertex in polygon[3])
            polygon_copy.append(vertex_str)
            polygon_copy += polygon[4:]
            cur.execute(sql, polygon_copy)
        sql = 'INSERT INTO %s VALUES (?,?,?)' % LAYER_NAMES[0]
        for record in layers[0]:
            cur.execute(sql, record)
        for i in range(1, len(layers)):
            sql = 'INSERT INTO %s VALUES (?,?,?,?)' % LAYER_NAMES[i]
            for record in layers[i]:
                cur.execute(sql, record)
        conn.commit()
        conn.close()

    def get_polygon_by_id(self, polygon_id):
        """根据多边形 id 获取多边形

        Args:
            polygon_id: 多边形 id

        Returns:
            多边形对象 或 None
        """
        return self.polygon_table[polygon_id] if polygon_id in self.polygon_table.keys() else None

    def get_children_table_by_id(self, polygon_id):
        """根据多边形 id 获取 children dict

        Args:
            polygon_id: 多边形 id

        Returns:
            当前多边形的 children 多边形 dict ，若无此 polygon_id 则返回 None
        """
        return {child.polygon_id: child for child in self.polygon_table[polygon_id].children} \
            if polygon_id in self.polygon_table.keys() else None

    def clear(self):
        """清空数据，递归删除"""
        while len(self.polygon_table) > 0:
            self.delete_by_id(list(self.polygon_table.keys())[0])

    def delete_by_id(self, polygon_id):
        """根据多边形 id 删除多边形（及其 children）

        Args:
            polygon_id: 多边形 id
        """
        if polygon_id in self.polygon_table.keys():
            # delete recursive
            deleted_id_list = self.polygon_table[polygon_id].delete()
            # remove from dict
            for deleted_id in deleted_id_list:
                if deleted_id in self.polygon_table.keys():
                    del self.polygon_table[deleted_id]

