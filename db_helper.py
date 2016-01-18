#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : db_helper.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-09-24
# Description   :
#


import sqlite3


LAYER_NAMES = ('L0', 'L1', 'L2', 'L3', 'L4')


def getLayerNames():
    return LAYER_NAMES


def getLayerName(_id):
    if 0 <= _id < len(LAYER_NAMES):
        return LAYER_NAMES[_id]
    else:
        return 'Unknown'


def loadLayerNames():
    global LAYER_NAMES
    names = []
    try:
        fp = open('PolygonLayer.cfg')
        for line in fp.readlines():
            if line.strip() != '':
                names.append(line.strip())
        fp.close()
    except Exception as e:
        print(repr(e))
    else:
        LAYER_NAMES = tuple(names)


def getTables(file_path):
    conn = sqlite3.connect(file_path)
    cur = conn.cursor()
    polygons = cur.execute('SELECT * FROM POLYGON').fetchall()
    polygons = [list(polygon) for polygon in polygons]
    levels = []
    for NAME in getLayerNames():
        levels.append(cur.execute('SELECT * FROM %s' % NAME).fetchall())
    conn.close()
    return polygons, levels


def writeTables(file_path, polygons, levels):
    LAYER_NAMES = getLayerNames()
    conn = sqlite3.connect(file_path)
    cur = conn.cursor()
    # clear
    cur.execute('DELETE FROM POLYGON')
    for NAME in LAYER_NAMES:
        cur.execute('DELETE FROM %s' % NAME)
    # insert
    sql = 'INSERT INTO POLYGON (_id, layer, vertex_Num, vertices) VALUES (?,?,?,?)'
    for polygon in polygons:
        cur.execute(sql, polygon)
    sql = 'INSERT INTO %s VALUES (?,?,?)' % LAYER_NAMES[0]
    for record in levels[0]:
        cur.execute(sql, record)
    for i in range(1, len(levels)):
        sql = 'INSERT INTO %s VALUES (?,?,?,?)' % LAYER_NAMES[i]
        for record in levels[i]:
            cur.execute(sql, record)
    conn.commit()
    conn.close()
