#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : db_helper.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-09-24
# Description   :
#


import dao.db_loader as db_loader
from dao.dao_polygon import DaoPolygon


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
        # parse data
        new_polygon_table = db_loader.load_from_sqlite(file_path)
        self.polygon_table.clear()
        for k, v in new_polygon_table.items():
            self.polygon_table[k] = v

    def write_to_file(self, file_path):
        """将结果写入 sqlite 数据库

        Args:
            file_path: 数据库路径
        """
        db_loader.write_to_sqlite(file_path, self.polygon_table)

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
            deleted_id_list = self.polygon_table[polygon_id].traversal_post_order()
            # remove from dict
            for deleted_id in deleted_id_list:
                if deleted_id in self.polygon_table.keys():
                    del self.polygon_table[deleted_id]

    def add_l0_polygon(self, polygon_id, name):
        """插入新的空多边形，L0层

        Args:
            polygon_id: 多边形 id
            name: L0 名字
        """
        if polygon_id not in self.polygon_table.keys():
            polygon = DaoPolygon([polygon_id, 0, 0, ''])
            polygon.layer = 0
            polygon.name = name
            self.polygon_table[polygon_id] = polygon

    def add_lp_polygon(self, polygon_id, layer, additional, parent_id):
        """插入新的空多边形，其他层

        Args:
            polygon_id: 多边形 id
            layer: 层号
            additional: 类型
            parent_id: parent 编号
        """
        if polygon_id not in self.polygon_table.keys():
            polygon = DaoPolygon([polygon_id, layer, 0, ''])
            polygon.layer = layer
            polygon.additional = additional
            self.polygon_table[polygon_id] = polygon
            if parent_id in self.polygon_table.keys():
                polygon.set_parent(self.polygon_table[parent_id])
