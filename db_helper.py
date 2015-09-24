#! D:/Python33/ python
# -*- coding: utf-8 -*-
# Module        : db_helper.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-09-24
# Description   :
#


import sqlite3


class dbHelper():
    def getTables(filepath):
        conn = sqlite3.connect(filepath)
        cur = conn.cursor()
        polygon = cur.execute('SELECT * FROM POLYGON').fetchall()
        l0 = cur.execute('SELECT * FROM L0').fetchall()
        l1 = cur.execute('SELECT * FROM L1').fetchall()
        l2 = cur.execute('SELECT * FROM L2').fetchall()
        l3 = cur.execute('SELECT * FROM L3').fetchall()
        l4 = cur.execute('SELECT * FROM L4').fetchall()
        conn.close()
        return (polygon, l0, l1, l2, l3, l4)

