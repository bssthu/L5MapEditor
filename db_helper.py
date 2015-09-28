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
        l0 = cur.execute('SELECT * FROM L0').fetchall()
        l1 = cur.execute('SELECT * FROM L1').fetchall()
        l2 = cur.execute('SELECT * FROM L2').fetchall()
        l3 = cur.execute('SELECT * FROM L3').fetchall()
        l4 = cur.execute('SELECT * FROM L4').fetchall()
        conn.close()
        return (polygons, l0, l1, l2, l3, l4)

    def writeTables(filepath, polygons, levels):
        conn = sqlite3.connect(filepath)
        cur = conn.cursor()
        # clear
        cur.execute('DELETE FROM POLYGON')
        cur.execute('DELETE FROM L0')
        cur.execute('DELETE FROM L1')
        cur.execute('DELETE FROM L2')
        cur.execute('DELETE FROM L3')
        cur.execute('DELETE FROM L4')
        # insert
        sql = 'INSERT INTO POLYGON (_id, type, vertex_Num, vertices) VALUES (?,?,?,?)'
        for polygon in polygons:
            cur.execute(sql, polygon)
        LEVEL_NAME = ('L0', 'L1', 'L2', 'L3', 'L4')
        sql = 'INSERT INTO %s (_id, polygon_id) VALUES (?,?)' % LEVEL_NAME[0]
        for record in levels[0]:
            cur.execute(sql, record)
        for i in range(1, len(levels)):
            sql = 'INSERT INTO %s (_id, polygon_id, parent_id) VALUES (?,?,?)' % LEVEL_NAME[i]
            for record in levels[i]:
                cur.execute(sql, record)
        conn.commit()
        conn.close()

