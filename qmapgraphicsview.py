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
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt
from polygon_item import PolygonItem
from polygon_new import PolygonNew
from polygon_select import PolygonSelect


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
        self.fsg_mgr = self.FsgMgr()
        self.fsg_mgr.getFsm('normal').enter_state.connect(lambda: self.setCursor(QCursor(Qt.ArrowCursor)))
        self.fsg_mgr.getFsm('insert').enter_state.connect(lambda: self.setCursor(QCursor(Qt.CrossCursor)))
        self.fsg_mgr.getFsm('insert').enter_state.connect(self.__beginInsert)
        self.fsg_mgr.getFsm('insert').exit_state.connect(self.__endInsert)
        self.fsg_mgr.getFsm('move').enter_state.connect(lambda: self.setCursor(QCursor(Qt.DragMoveCursor)))
        self.fsg_mgr.getFsm('move').enter_state.connect(self.__beginMove)
        self.fsg_mgr.getFsm('move').exit_state.connect(self.__endMove)

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
        return self.fsg_mgr.changeFsm('normal', 'insert')

    def endInsert(self):
        return self.fsg_mgr.changeFsm('insert', 'normal')

    def beginMove(self):
        return self.fsg_mgr.changeFsm('normal', 'move')

    def endMove(self):
        return self.fsg_mgr.changeFsm('move', 'normal')

    def __beginInsert(self):
        # data
        self.newPolygon = PolygonNew()
        self.scene().addItem(self.newPolygon)
        # signal
        self.leftClick.connect(self.addPoint)
        self.rightClick.connect(self.removePoint)

    def __endInsert(self):
        # 处理新多边形
        (verticesNum, verticesString) = self.newPolygon.getVerticesForDb()
        self.scene().removeItem(self.newPolygon)
        self.newPolygon = None
        if verticesNum > 0:
            self.polygonCreated.emit(verticesNum, verticesString)
        # signal
        self.leftClick.disconnect(self.addPoint)
        self.rightClick.disconnect(self.removePoint)

    def __beginMove(self):
        # signal
        self.leftClick.connect(self.setMoveBasePoint)
        self.mouseMove.connect(self.movingToPoint)
        self.leftUp.connect(self.finishMove)
        self.rightClick.connect(self.resetMove)

    def __endMove(self):
        # data
        if self.selectedPolygon is not None:
            (verticesNum, verticesString) = self.selectedPolygon.getVerticesForDb()
            self.polygonUpdated.emit(verticesNum, verticesString)
        # signal
        self.leftClick.disconnect(self.setMoveBasePoint)
        self.mouseMove.disconnect(self.movingToPoint)
        self.leftUp.disconnect(self.finishMove)
        self.rightClick.disconnect(self.resetMove)


# State
    class FsgMgr:
        def __init__(self):
            self.__fsms = {}
            self.__fsms['normal'] = self.FsmNormal()
            self.__fsms['insert'] = self.FsmInsert()
            self.__fsms['move'] = self.FsmMove()
            self.state = self.__fsms['normal']

        def getFsm(self, name):
            return self.__fsms[name.lower()]

        def changeFsm(self, curr_name, new_name):
            if self.getFsm(curr_name) != self.state:
                return False
            new_state = self.getFsm(new_name)
            if self.state == self.getFsm('normal'):
                if new_state == self.getFsm('insert'):  # normal => insert
                    self.__setFsm(new_state)
                    return True
                elif new_state == self.getFsm('move'):  # normal => move
                    self.__setFsm(new_state)
                    return True
            elif self.state == self.getFsm('insert'):
                if new_state == self.getFsm('normal'):  # insert => normal
                    self.__setFsm(new_state)
                    return True
            elif self.state == self.getFsm('move'):
                if new_state == self.getFsm('normal'):  # move => normal
                    self.__setFsm(new_state)
                    return True
            return False

        def __setFsm(self, new_state):
            self.state.exit_state.emit()
            new_state.enter_state.emit()
            self.state = new_state

        class FsmNormal(QObject):
            enter_state = pyqtSignal()
            exit_state = pyqtSignal()

        class FsmInsert(QObject):
            enter_state = pyqtSignal()
            exit_state = pyqtSignal()

        class FsmMove(QObject):
            enter_state = pyqtSignal()
            exit_state = pyqtSignal()

