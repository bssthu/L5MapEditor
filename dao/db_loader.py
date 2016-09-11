#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : db_loader.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2016-07-28
# Description   :
#


import sqlite3

from dao.dao_polygon import DaoPolygon
from editor import config_loader


def load_from_sqlite(file_path):
    """从文件载入 sqlite 数据库

    Args:
        file_path (str): 数据库路径
    """
    # open sqlite
    conn = sqlite3.connect(file_path)
    cur = conn.cursor()
    # load polygons
    polygons = cur.execute('SELECT * FROM POLYGON').fetchall()
    polygons = [list(polygon) for polygon in polygons]
    # load layers
    layers = []
    for NAME in config_loader.get_layer_names():
        layer = cur.execute('SELECT * FROM %s' % NAME).fetchall()
        layer = [list(record) for record in layer]
        layers.append(layer)
    conn.close()
    return create_dao_polygon_table(polygons, layers)


def create_dao_polygon_table(polygons, layers):
    """从来自数据库的数据 list 创建 Polygon 表

    Args:
        polygons (list): list of [polygon_id, layer, vertex_num, <str>vertices]
        layers (list[list]): list of list of record

    Returns:
        polygon_table (dict[int, DaoPolygon]): {polygon_id: DaoPolygon}
    """

    # create table
    polygon_table = {}
    for polygon in polygons:
        dao_polygon = DaoPolygon(polygon)
        polygon_table[dao_polygon.polygon_id] = dao_polygon

    # set info from layer
    keys = polygon_table.keys()

    if len(layers) > 0:
        layer0_table = layers[0]
        for _id, polygon_id, name in layer0_table:
            if polygon_id in keys:
                polygon_table[polygon_id].name = name

    for current_layer_table in layers[1:]:
        for _id, polygon_id, additional, parent_id in current_layer_table:
            if polygon_id not in keys or parent_id not in keys:
                raise Exception('多边形 %d 的 layer 信息错误' % polygon_id)
            polygon = polygon_table[polygon_id]
            parent = polygon_table[parent_id]
            if polygon.layer <= parent.layer:
                raise Exception('多边形 %d 或 %d 的 layer 信息错误' % (polygon_id, parent_id))
            polygon.additional = additional
            polygon.parent_id = parent_id
            polygon.parent = parent
            parent.children.append(polygon)

    return polygon_table


def write_to_sqlite(file_path, polygon_table):
    """将结果写入 sqlite 数据库

    Args:
        file_path (str): 数据库路径
        polygon_table (dict[int, DaoPolygon]): {polygon_id: DaoPolygon}
    """
    LAYER_NAMES = config_loader.get_layer_names()
    conn = sqlite3.connect(file_path)
    cur = conn.cursor()
    # clear
    cur.execute('DELETE FROM POLYGON')
    for NAME in LAYER_NAMES:
        cur.execute('DELETE FROM %s' % NAME)
    # insert polygon table
    sql = 'INSERT INTO POLYGON (_id, layer, vertex_Num, vertices) VALUES (?,?,?,?)'
    for polygon in polygon_table.values():
        cur.execute(sql, polygon.to_list())
    # insert layer table
    layer_id = [0] * len(LAYER_NAMES)
    for polygon in polygon_table.values():
        layer = polygon.layer
        if layer < len(LAYER_NAMES):
            layer_id[layer] += 1
            if layer == 0:
                sql = 'INSERT INTO %s VALUES (?,?,?)' % LAYER_NAMES[0]
                record = (layer_id[layer], polygon.polygon_id, polygon.name)
                cur.execute(sql, record)
            else:
                sql = 'INSERT INTO %s VALUES (?,?,?,?)' % LAYER_NAMES[layer]
                record = (layer_id[layer], polygon.polygon_id, polygon.additional, polygon.parent.polygon_id)
                cur.execute(sql, record)
    conn.commit()
    conn.close()
