#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : polygon_select.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-09-24
# Description   :
#


import math
from PyQt5.QtWidgets import QGraphicsWidget
from PyQt5.QtCore import QRectF, QPointF
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPolygonF, QPen, QBrush
from polygon_item import PolygonItem


class PolygonSelect(QGraphicsWidget):
    def __init__(self, vertices, rect):
        QGraphicsWidget.__init__(self)
        self.vertices = vertices
        self.rect = rect
        self.offset = QPointF(0, 0)
        self.oldVertices = vertices
        self.pointId = -1

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget):
        # init graphics
        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(0)
        pen.setStyle(Qt.DashDotLine)
        redPen = QPen(QColor(255, 0, 0))
        redPen.setWidth(0)
        brush = QBrush(QColor(0, 0, 0), Qt.Dense7Pattern)
        # current vertices
        vertices = self.__applyOffset(self.vertices, self.offset)
        if len(vertices) > 0:
            # draw
            painter.setPen(pen)
            painter.drawPolyline(QPolygonF(vertices))
            if PolygonItem.drawDots:
                painter.fillRect(self.rect, brush)
            if PolygonItem.closePolygon:
                painter.drawLine(vertices[-1], vertices[0])
        scale = painter.transform().m11()
        if PolygonItem.markPoints:
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

    def setPointId(self, pointId):
        self.pointId = pointId

    def setOffset(self, offset):
        self.offset = offset

    def applyOffset(self, offset):  # 移动到某处释放鼠标
        self.vertices = self.__applyOffset(self.vertices, offset)
        self.offset = QPointF(0, 0)

    def __applyOffset(self, vertices, offset):
        vertices = vertices[:]
        if PolygonItem.movePoint:
            if self.pointId >= 0:
                vertices[self.pointId] = vertices[self.pointId] + offset
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

    def getVertices(self):
        return self.vertices

    def getVerticesForDb(self):
        verticesNum = len(self.vertices)
        verticesString = ';\n'.join('%f,%f' % (vertex.x(), vertex.y()) for vertex in self.vertices)
        return (verticesNum, verticesString)

