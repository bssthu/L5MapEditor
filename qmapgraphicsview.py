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
from polygon_base import PolygonBase
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
    pointsUpdated = pyqtSignal(list)

    def __init__(self, centralwidget):
        super().__init__(centralwidget)
        self.selectedPolygon = None

# slots
    @pyqtSlot(QPointF)
    def addPoint(self, pt):
        self.newPolygon.addPoint(pt)

    @pyqtSlot(QPointF)
    def preAddPoint(self, pt):      # 按住鼠标并移动到点
        self.newPolygon.preAddPoint(pt)
        self.scene().invalidate()

    @pyqtSlot()
    def removePoint(self):          # 右键移除最新添加的点
        self.newPolygon.removePoint()

    @pyqtSlot(QPointF)
    def setMoveMouseBasePoint(self, pt):    # 移动起点
        self.moveBase = pt

    @pyqtSlot(QPointF)
    def setMoveMouseToPoint(self, pt):  # 移动到的点，左键按住
        if self.selectedPolygon is not None:
            offset = pt - self.moveBase
            self.selectedPolygon.setOffset(offset)
            self.scene().invalidate()

    @pyqtSlot(QPointF)
    def finishMove(self, pt):       # 移动到的点，松开左键
        if self.selectedPolygon is not None:
            offset = pt - self.moveBase
            self.selectedPolygon.applyOffset(offset)
            self.pointsUpdated.emit(self.selectedPolygon.getVertices())

    @pyqtSlot(QPointF)
    def resetMove(self):
        if self.selectedPolygon is not None:
            self.selectedPolygon.resetOffset()
            self.pointsUpdated.emit(self.selectedPolygon.getVertices())

    def scale(self, sx, sy):
        super().scale(sx, sy)
        if self.selectedPolygon is not None:
            self.selectedPolygon.setScale(sx)
        self.scene().invalidate()

    def setPolygons(self, polygons, layerNum):
        self.scene().clear()
        for polygon in polygons:
            layer = polygon[1]
            vertices = polygon[3]
            if layer < layerNum:
                self.scene().addItem(PolygonItem(layer, vertices))
        self.scene().setSceneRect(self.scene().itemsBoundingRect())

    def selectPolygon(self, polygon):   # 绘制选中的多边形
        if self.selectedPolygon in self.scene().items():
            self.scene().removeItem(self.selectedPolygon)
        if polygon is not None:
            polygonItem = PolygonItem(polygon[1], polygon[3])
            self.selectedPolygon = PolygonSelect(polygonItem.getVertices(), polygonItem.boundingRect())
            self.selectedPolygon.setScale(self.transform().m11())
            self.scene().addItem(self.selectedPolygon)
        self.scene().invalidate()

    def movePoint(self, allow=True):
        PolygonBase.movePoint = allow

    def selectPoint(self, pointId):
        self.selectedPolygon.setPointId(pointId)
        self.scene().invalidate()

    def drawClosedPolygon(self, allow=True):
        PolygonBase.closePolygon = allow
        self.scene().invalidate()

    def highlightSelection(self, allow=True):
        PolygonBase.highlightSelection = allow
        self.scene().invalidate()

    def markPoints(self, allow=True):
        PolygonBase.markPoints = allow
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
        if event.buttons() == Qt.LeftButton:
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
        self.leftUp.connect(self.addPoint)
        self.leftClick.connect(self.preAddPoint)
        self.mouseMove.connect(self.preAddPoint)
        self.rightClick.connect(self.removePoint)

    def endInsert(self):
        # 处理新多边形
        (verticesNum, verticesString) = self.newPolygon.getVerticesForDb()
        self.scene().removeItem(self.newPolygon)
        self.newPolygon = None
        if verticesNum > 0:
            self.polygonCreated.emit(verticesNum, verticesString)
        # signal
        self.leftUp.disconnect(self.addPoint)
        self.leftClick.disconnect(self.preAddPoint)
        self.mouseMove.disconnect(self.preAddPoint)
        self.rightClick.disconnect(self.removePoint)

    def beginMove(self):
        # data
        self.pointsUpdated.emit(self.selectedPolygon.getVertices())
        # signal
        self.leftClick.connect(self.setMoveMouseBasePoint)
        self.mouseMove.connect(self.setMoveMouseToPoint)
        self.leftUp.connect(self.finishMove)
        self.rightClick.connect(self.resetMove)

    def endMove(self):
        # data
        if self.selectedPolygon is not None:
            self.selectedPolygon.confirmOffset()
            (verticesNum, verticesString) = self.selectedPolygon.getVerticesForDb()
            self.polygonUpdated.emit(verticesNum, verticesString)
        # signal
        self.leftClick.disconnect(self.setMoveMouseBasePoint)
        self.mouseMove.disconnect(self.setMoveMouseToPoint)
        self.leftUp.disconnect(self.finishMove)
        self.rightClick.disconnect(self.resetMove)

