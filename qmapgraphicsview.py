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
from PyQt5.QtCore import QPointF
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt
from polygon_item import PolygonItem


class QMapGraphicsView(QGraphicsView):
    leftClick = pyqtSignal(QPointF)
    rightClick = pyqtSignal()
    polygonCreated = pyqtSignal(int, int, str)

    def __init__(self, centralwidget):
        QGraphicsView.__init__(self, centralwidget)
        self.newLevel = 0

# slots
    @pyqtSlot(QPointF)
    def addPoint(self, pt):
        self.newPolygon.addPoint(pt)
        pass

    @pyqtSlot()
    def removePoint(self):
        pass

    @pyqtSlot(int)
    def setNewLevel(self, level):
        self.newLevel = level

    def setPolygons(self, polygons):
        self.scene().clear()
        for polygon in polygons:
            self.scene().addItem(PolygonItem(polygon[1], polygon[3]))

    def drawClosePolygon(self, close=True):
        PolygonItem.closePolygon = close
        self.scene().invalidate()

    def beginInsert(self):
        # ui
        self.setCursor(QCursor(Qt.CrossCursor))
        # data
        self.newPolygon = PolygonItem(-1, '')
        self.scene().addItem(self.newPolygon)
        # signal
        self.leftClick.connect(self.addPoint)
        self.rightClick.connect(self.removePoint)

    def endInsert(self):
        # ui
        self.setCursor(QCursor(Qt.ArrowCursor))
        # 处理新多边形
        (verticesNum, verticesString) = self.newPolygon.getVertices()
        self.polygonCreated.emit(self.newLevel, verticesNum, verticesString)
        # data
        self.scene().removeItem(self.newPolygon)
        self.newPolygon = None
        # signal
        self.leftClick.disconnect(self.addPoint)
        self.rightClick.disconnect(self.removePoint)

    def mousePressEvent(self, event):
        button = event.button()
        pt = self.mapToScene(event.pos())
        if button == Qt.LeftButton:
            self.leftClick.emit(pt)
        elif button == Qt.RightButton:
            self.rightClick.emit()
        self.scene().invalidate()

