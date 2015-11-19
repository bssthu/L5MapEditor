#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : db_helper.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-09-24
# Description   :
#


import sqlite3


class DbHelper():
    def getTables(filepath):
        conn = sqlite3.connect(filepath)
        cur = conn.cursor()
        polygons = cur.execute('SELECT * FROM POLYGON').fetchall()
        polygons = [list(polygon) for polygon in polygons]
        levels = []
        for NAME in DbHelper.getLayerNames():
            levels.append(cur.execute('SELECT * FROM %s' % NAME).fetchall())
        conn.close()
        return (polygons, levels)

    def writeTables(filepath, polygons, levels):
        LAYER_NAMES = DbHelper.getLayerNames()
        conn = sqlite3.connect(filepath)
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

    def getLayerNames():
        return DbHelper.LAYER_NAMES

    def getLayerName(id):
        if id >= 0 and id < len(DbHelper.LAYER_NAMES):
            return DbHelper.LAYER_NAMES[id]
        else:
            return 'Unknown'

    def loadLayerNames():
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
            DbHelper.LAYER_NAMES = tuple(names)


DbHelper.LAYER_NAMES = ('L0', 'L1', 'L2', 'L3', 'L4')

