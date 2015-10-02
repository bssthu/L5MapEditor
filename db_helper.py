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
        for NAME in DbHelper.getTypeNames():
            levels.append(cur.execute('SELECT * FROM %s' % NAME).fetchall())
        conn.close()
        return (polygons, levels)

    def writeTables(filepath, polygons, levels):
        TYPE_NAMES = DbHelper.getTypeNames()
        conn = sqlite3.connect(filepath)
        cur = conn.cursor()
        # clear
        cur.execute('DELETE FROM POLYGON')
        for NAME in TYPE_NAMES:
            cur.execute('DELETE FROM %s' % NAME)
        # insert
        sql = 'INSERT INTO POLYGON (_id, type, vertex_Num, vertices) VALUES (?,?,?,?)'
        for polygon in polygons:
            cur.execute(sql, polygon)
        sql = 'INSERT INTO %s (_id, polygon_id, type) VALUES (?,?,?)' % TYPE_NAMES[0]
        for record in levels[0]:
            cur.execute(sql, record)
        for i in range(1, len(levels)):
            sql = 'INSERT INTO %s (_id, polygon_id, type, parent_id) VALUES (?,?,?,?)' % TYPE_NAMES[i]
            for record in levels[i]:
                cur.execute(sql, record)
        conn.commit()
        conn.close()

    def getTypeNames():
        return DbHelper.TYPE_NAMES


DbHelper.TYPE_NAMES = ('L0', 'L1', 'L2', 'L3', 'L4')

