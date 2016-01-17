#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : polygon_select.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-09-24
# Description   :
#


from PyQt5.QtCore import QRectF, QPointF
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPolygonF, QPen, QBrush
from polygon_base import PolygonBase


class PolygonSelect(PolygonBase):
    def __init__(self, vertices, rect):
        super().__init__()
        self.MAR = 50
        self.vertices = vertices
        self.rect = rect
        self.topLeft = rect.topLeft() + QPointF(self.MAR, self.MAR)
        self.bottomRight = rect.bottomRight() - QPointF(self.MAR, self.MAR)
        self.dotsRect = self.rect
        self.offset = QPointF(0, 0)
        self.oldVertices = vertices
        self.pointId = -1

    def paint(self, painter, option, widget):
        # init graphics
        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(0)
        pen.setStyle(Qt.DashDotLine)
        redPen = QPen(QColor(255, 0, 0))
        redPen.setWidth(0)
        # current vertices
        vertices = self.__applyOffset(self.vertices, self.offset)
        if len(vertices) > 0:
            # draw
            painter.setPen(pen)
            painter.drawPolyline(QPolygonF(vertices))
            if PolygonBase.highlightSelection:
                brush = QBrush(QColor(0, 0, 0, 64))
                painter.fillRect(self.dotsRect, brush)
            if PolygonBase.closePolygon:
                painter.drawLine(vertices[-1], vertices[0])
        scale = painter.transform().m11()
        if PolygonBase.markPoints:
            L_SIZE = 20
            S_SIZE = 10
            if len(vertices) > 0:
                painter.drawEllipse(vertices[0], L_SIZE / scale, L_SIZE / scale)
            for vertex in vertices:
                painter.drawEllipse(vertex, S_SIZE / scale, S_SIZE / scale)
        if self.pointId >= 0:
            M_SIZE = 15
            painter.setPen(redPen)
            if len(vertices) > 0:
                painter.drawEllipse(vertices[self.pointId], M_SIZE / scale, M_SIZE / scale)

    def setScale(self, scale):
        self.MAR = 20 / scale
        self.dotsRect = QRectF(self.topLeft, self.bottomRight).adjusted(-self.MAR, -self.MAR, self.MAR, self.MAR)

    def setPointId(self, pointId):
        self.pointId = pointId

    def setOffset(self, offset):
        self.offset = offset

    def applyOffset(self, offset):  # 移动到某处释放鼠标
        self.vertices = self.__applyOffset(self.vertices, offset)
        if not PolygonBase.movePoint:
            self.moveBoundingRect(offset)
        self.offset = QPointF(0, 0)

    def __applyOffset(self, vertices, offset):
        vertices = vertices[:]
        if PolygonBase.movePoint:
            if self.pointId >= 0:
                vertices[self.pointId] = vertices[self.pointId] + offset
                self.updateBoundingRect(vertices[self.pointId])
        else:
            vertices = [vertex + offset for vertex in vertices]
        return vertices

    def confirmOffset(self):        # 退出移动状态，保存
        self.oldVertices = self.vertices

    def resetOffset(self):
        self.offset = QPointF(0, 0)
        self.vertices = self.oldVertices

    def getOffset(self):
        return self.offset

