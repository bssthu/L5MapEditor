#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : qmapgraphicsview.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-09-25
# Description   :
#


from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtCore import QPointF
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt
from editor.polygon_base import PolygonBase
from editor.polygon_item import PolygonItem
from editor.polygon_new import PolygonNew
from editor.polygon_select import PolygonSelect


class QMapGraphicsView(QGraphicsView):
    leftClick = pyqtSignal(QPointF)
    rightClick = pyqtSignal()
    mouseMove = pyqtSignal(QPointF)
    leftUp = pyqtSignal(QPointF)
    polygonCreated = pyqtSignal(list)
    polygonUpdated = pyqtSignal(list)
    pointsUpdated = pyqtSignal(list)

    def __init__(self, parent):
        super().__init__(parent)
        self.selected_polygon = None
        self.move_base = QPointF()
        self.new_polygon = None

# slots
    @pyqtSlot(QPointF)
    def addPoint(self, pt):
        self.new_polygon.addPoint(pt)

    @pyqtSlot(QPointF)
    def preAddPoint(self, pt):      # 按住鼠标并移动到点
        self.new_polygon.preAddPoint(pt)
        self.scene().invalidate()

    @pyqtSlot()
    def removePoint(self):          # 右键移除最新添加的点
        self.new_polygon.removePoint()

    @pyqtSlot(QPointF)
    def setMoveMouseBasePoint(self, pt):    # 移动起点
        self.move_base = pt

    @pyqtSlot(QPointF)
    def setMoveMouseToPoint(self, pt):  # 移动到的点，左键按住
        if self.selected_polygon is not None:
            offset = pt - self.move_base
            self.selected_polygon.setOffset(offset)
            self.scene().invalidate()

    @pyqtSlot(QPointF)
    def finishMove(self, pt):       # 移动到的点，松开左键
        if self.selected_polygon is not None:
            offset = pt - self.move_base
            self.selected_polygon.applyOffset(offset)
            self.pointsUpdated.emit(self.selected_polygon.getPoints())

    @pyqtSlot(QPointF)
    def resetMove(self):
        if self.selected_polygon is not None:
            self.selected_polygon.resetOffset()
            self.pointsUpdated.emit(self.selected_polygon.getPoints())

    def scale(self, sx, sy):
        super().scale(sx, sy)
        if self.selected_polygon is not None:
            self.selected_polygon.setScale(sx)
        self.scene().invalidate()

    def setPolygons(self, polygons, layer_num):
        self.scene().clear()
        for polygon in polygons:
            layer = polygon[1]
            if layer < layer_num:
                self.scene().addItem(PolygonItem(polygon))
        self.scene().setSceneRect(self.scene().itemsBoundingRect())

    def setSelectedPolygon(self, polygon):   # 绘制选中的多边形
        if self.selected_polygon in self.scene().items():
            self.scene().removeItem(self.selected_polygon)
        if polygon is not None:
            self.selected_polygon = PolygonSelect(polygon)
            self.selected_polygon.setScale(self.transform().m11())
            self.scene().addItem(self.selected_polygon)
        self.scene().invalidate()

    def movePoint(self, allow=True):
        PolygonBase.move_point = allow

    def selectPoint(self, point_id):
        self.selected_polygon.setPointId(point_id)
        self.scene().invalidate()

    def drawClosedPolygon(self, allow=True):
        PolygonBase.close_polygon = allow
        self.scene().invalidate()

    def highlightSelection(self, allow=True):
        PolygonBase.highlight_selection = allow
        self.scene().invalidate()

    def markPoints(self, allow=True):
        PolygonBase.mark_points = allow
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
        self.new_polygon = PolygonNew()
        self.scene().addItem(self.new_polygon)
        # signal
        self.leftUp.connect(self.addPoint)
        self.leftClick.connect(self.preAddPoint)
        self.mouseMove.connect(self.preAddPoint)
        self.rightClick.connect(self.removePoint)

    def endInsert(self):
        # 处理新多边形
        vertices = self.new_polygon.getVertices()
        self.scene().removeItem(self.new_polygon)
        self.new_polygon = None
        if len(vertices) > 0:
            self.polygonCreated.emit(vertices)
        # signal
        self.leftUp.disconnect(self.addPoint)
        self.leftClick.disconnect(self.preAddPoint)
        self.mouseMove.disconnect(self.preAddPoint)
        self.rightClick.disconnect(self.removePoint)

    def beginMove(self):
        # data
        self.pointsUpdated.emit(self.selected_polygon.getPoints())
        # signal
        self.leftClick.connect(self.setMoveMouseBasePoint)
        self.mouseMove.connect(self.setMoveMouseToPoint)
        self.leftUp.connect(self.finishMove)
        self.rightClick.connect(self.resetMove)

    def endMove(self):
        # data
        if self.selected_polygon is not None:
            self.selected_polygon.confirmOffset()
            vertices = self.selected_polygon.getVertices()
            self.polygonUpdated.emit(vertices)
        # signal
        self.leftClick.disconnect(self.setMoveMouseBasePoint)
        self.mouseMove.disconnect(self.setMoveMouseToPoint)
        self.leftUp.disconnect(self.finishMove)
        self.rightClick.disconnect(self.resetMove)

