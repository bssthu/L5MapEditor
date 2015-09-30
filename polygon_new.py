#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : polygon_new.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-09-28
# Description   :
#


import math
from PyQt5.QtWidgets import QGraphicsWidget
from PyQt5.QtCore import QRectF, QPointF
from PyQt5.QtGui import QColor, QPolygonF, QPen
from polygon_item import PolygonItem


MAR = 50

class PolygonNew(QGraphicsWidget):
    def __init__(self):
        QGraphicsWidget.__init__(self)
        self.vertices = []
        self.topLeft = QPointF(float('Inf'), float('Inf'))
        self.bottomRight = QPointF(-float('Inf'), -float('Inf'))
        self.rect = QRectF()
        self.mousePoint = None

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget):
        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(0)
        redPen = QPen(QColor(255, 0, 0))
        redPen.setWidth(0)
        # lines
        painter.setPen(pen)
        if len(self.vertices) > 1:
            painter.drawPolyline(QPolygonF(self.vertices))
        # point mark
        painter.setPen(pen)
        if PolygonItem.markPoints:
            scale = painter.transform().m11()
            L_SIZE = 20
            S_SIZE = 10
            if len(self.vertices) > 0:
                scale = painter.transform().m11()
                painter.drawEllipse(self.vertices[0], L_SIZE / scale, L_SIZE / scale)
            for vertex in self.vertices:
                painter.drawEllipse(vertex, S_SIZE / scale, S_SIZE / scale)
        # pre add
        painter.setPen(redPen)
        if self.mousePoint is not None:
            if len(self.vertices) > 0:
                painter.drawLine(self.vertices[-1], self.mousePoint)
            if PolygonItem.markPoints:
                S_SIZE = 10
                painter.drawEllipse(self.mousePoint, S_SIZE / scale, S_SIZE / scale)

    def preAddPoint(self, pt):
        self.mousePoint = QPointF(pt)
        self.updateBoundingRect(pt)

    def addPoint(self, pt):
        self.mousePoint = None
        self.vertices.append(QPointF(pt))
        self.updateBoundingRect(pt)

    def updateBoundingRect(self, pt):
        self.topLeft = QPointF(min(self.topLeft.x(), pt.x()), min(self.topLeft.y(), pt.y()))
        self.bottomRight = QPointF(max(self.bottomRight.x(), pt.x()), max(self.bottomRight.y(), pt.y()))
        self.rect = QRectF(self.topLeft, self.bottomRight).adjusted(-MAR, -MAR, MAR, MAR)
        self.prepareGeometryChange()

    def removePoint(self):
        if len(self.vertices) > 0:
            self.vertices = self.vertices[:-1]

    def getVerticesForDb(self):
        verticesNum = len(self.vertices)
        verticesString = ';\n'.join('%f,%f' % (vertex.x(), vertex.y()) for vertex in self.vertices)
        return (verticesNum, verticesString)

