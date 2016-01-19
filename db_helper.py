#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : db_helper.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-09-24
# Description   :
#


import sqlite3
import config_loader


def getTables(file_path):
    conn = sqlite3.connect(file_path)
    cur = conn.cursor()
    polygons = cur.execute('SELECT * FROM POLYGON').fetchall()
    polygons = [list(polygon) for polygon in polygons]
    for polygon in polygons:
        vertex_str = polygon[3].strip().strip(';')
        if vertex_str == '':
            polygon[3] = []
            polygon[2] = 0
        else:
            polygon[3] = [[float(v.strip()) for v in pt_str.strip().split(',')] for pt_str in vertex_str.split(';')]
            polygon[2] = len(polygon[3])
    levels = []
    for NAME in config_loader.getLayerNames():
        print(NAME)
        levels.append(cur.execute('SELECT * FROM %s' % NAME).fetchall())
    conn.close()
    return polygons, levels


def writeTables(file_path, polygons, levels):
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
    for record in levels[0]:
        cur.execute(sql, record)
    for i in range(1, len(levels)):
        sql = 'INSERT INTO %s VALUES (?,?,?,?)' % LAYER_NAMES[i]
        for record in levels[i]:
            cur.execute(sql, record)
    conn.commit()
    conn.close()
