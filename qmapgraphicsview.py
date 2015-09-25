#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : qmapgraphicsview.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-09-25
# Description   :
#


import sqlite3
from PyQt5.QtWidgets import QGraphicsView
from polygon_item import PolygonItem


class QMapGraphicsView(QGraphicsView):
    def __init__(self, centralwidget):
        QGraphicsView.__init__(self, centralwidget)

    def setPolygons(self, polygons):
        self.scene().clear()
        for polygon in polygons:
            self.scene().addItem(PolygonItem(polygon[1], polygon[3]))

    def drawClosePolygon(self, close=True):
        PolygonItem.closePolygon = close
        self.scene().invalidate()
