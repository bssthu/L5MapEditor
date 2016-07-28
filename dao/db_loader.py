#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : db_loader.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2016-07-28
# Description   :
#


from dao.dao_polygon import DaoPolygon


def create_dao_polygon_table(polygons, layers):
    """从来自数据库的数据 list 创建 Polygon 表

    Args:
        polygons: list of [polygon_id, layer, vertex_num, <str>vertices]
        layers: list of list of record

    Returns:
        polygon_table: {polygon_id: DaoPolygon}
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


def export_dao_polygon_table(polygon_table):
    pass

