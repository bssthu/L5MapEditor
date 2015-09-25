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
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt
from polygon_item import PolygonItem


class QMapGraphicsView(QGraphicsView):
    leftClick = pyqtSignal()
    rightClick = pyqtSignal()

    def __init__(self, centralwidget):
        QGraphicsView.__init__(self, centralwidget)

# slots
    @pyqtSlot()
    def addPoint(self):
        pass

    @pyqtSlot()
    def removePoint(self):
        pass

    def setPolygons(self, polygons):
        self.scene().clear()
        for polygon in polygons:
            self.scene().addItem(PolygonItem(polygon[1], polygon[3]))

    def drawClosePolygon(self, close=True):
        PolygonItem.closePolygon = close
        self.scene().invalidate()

    def beginInsert(self):
        self.setCursor(QCursor(Qt.CrossCursor))
        self.leftClick.connect(self.addPoint)
        self.rightClick.connect(self.removePoint)

    def endInsert(self):
        self.setCursor(QCursor(Qt.ArrowCursor))
        self.leftClick.disconnect(self.addPoint)
        self.rightClick.disconnect(self.removePoint)

    def mousePressEvent(self, event):
        button = event.button()
        if button == Qt.LeftButton:
            self.leftClick.emit()
        elif button == Qt.RightButton:
            self.rightClick.emit()

