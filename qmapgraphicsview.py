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
from PyQt5.QtCore import QPointF
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt
from polygon_item import PolygonItem
from polygon_new import PolygonNew
from polygon_select import PolygonSelect
from fsm_mgr import FsmMgr


class QMapGraphicsView(QGraphicsView):
    leftClick = pyqtSignal(QPointF)
    rightClick = pyqtSignal()
    mouseMove = pyqtSignal(QPointF)
    leftUp = pyqtSignal(QPointF)
    polygonCreated = pyqtSignal(int, str)
    polygonUpdated = pyqtSignal(int, str)

    def __init__(self, centralwidget):
        QGraphicsView.__init__(self, centralwidget)
        self.selectedPolygon = None

# slots
    @pyqtSlot(QPointF)
    def addPoint(self, pt):
        self.newPolygon.addPoint(pt)

    @pyqtSlot()
    def removePoint(self):
        self.newPolygon.removePoint()

    @pyqtSlot(QPointF)
    def setMoveBasePoint(self, pt):
        self.moveBase = pt

    @pyqtSlot(QPointF)
    def movingToPoint(self, pt):
        if self.selectedPolygon is not None:
            offset = pt - self.moveBase
            self.selectedPolygon.setOffset(offset)
            self.scene().invalidate()

    @pyqtSlot(QPointF)
    def finishMove(self, pt):
        if self.selectedPolygon is not None:
            offset = pt - self.moveBase
            self.selectedPolygon.applyOffset(offset)

    @pyqtSlot(QPointF)
    def resetMove(self):
        if self.selectedPolygon is not None:
            self.selectedPolygon.resetOffset()

    def setPolygons(self, polygons):
        self.scene().clear()
        for polygon in polygons:
            self.scene().addItem(PolygonItem(polygon[1], polygon[3]))

    def selectPolygon(self, polygon):
        if self.selectedPolygon in self.scene().items():
            self.scene().removeItem(self.selectedPolygon)
        if polygon is not None:
            polygonItem = PolygonItem(polygon[1], polygon[3])
            self.selectedPolygon = PolygonSelect(polygonItem.getVertices(), polygonItem.boundingRect())
            self.scene().addItem(self.selectedPolygon)
        self.scene().invalidate()

    def drawClosedPolygon(self, close=True):
        PolygonItem.closePolygon = close
        self.scene().invalidate()

    def drawSelectionDots(self, draw=True):
        PolygonItem.drawDots = draw
        self.scene().invalidate()

    def markPoints(self, mark=True):
        PolygonItem.markPoints = mark
        self.scene().invalidate()

    def mousePressEvent(self, event):
        button = event.button()
        pt = self.mapToScene(event.pos())
        if button == Qt.LeftButton:
            self.leftClick.emit(pt)
        elif button == Qt.RightButton:
            self.rightClick.emit()
        self.scene().invalidate()

    def mouseMoveEvent(self, event):
        pt = self.mapToScene(event.pos())
        self.mouseMove.emit(pt)

    def mouseReleaseEvent(self, event):
        button = event.button()
        pt = self.mapToScene(event.pos())
        if button == Qt.LeftButton:
            self.leftUp.emit(pt)

    def beginInsert(self):
        # data
        self.newPolygon = PolygonNew()
        self.scene().addItem(self.newPolygon)
        # signal
        self.leftClick.connect(self.addPoint)
        self.rightClick.connect(self.removePoint)

    def endInsert(self):
        # 处理新多边形
        (verticesNum, verticesString) = self.newPolygon.getVerticesForDb()
        self.scene().removeItem(self.newPolygon)
        self.newPolygon = None
        if verticesNum > 0:
            self.polygonCreated.emit(verticesNum, verticesString)
        # signal
        self.leftClick.disconnect(self.addPoint)
        self.rightClick.disconnect(self.removePoint)

    def beginMove(self):
        # signal
        self.leftClick.connect(self.setMoveBasePoint)
        self.mouseMove.connect(self.movingToPoint)
        self.leftUp.connect(self.finishMove)
        self.rightClick.connect(self.resetMove)

    def endMove(self):
        # data
        if self.selectedPolygon is not None:
            (verticesNum, verticesString) = self.selectedPolygon.getVerticesForDb()
            self.polygonUpdated.emit(verticesNum, verticesString)
        # signal
        self.leftClick.disconnect(self.setMoveBasePoint)
        self.mouseMove.disconnect(self.movingToPoint)
        self.leftUp.disconnect(self.finishMove)
        self.rightClick.disconnect(self.resetMove)

