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

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget):
        if len(self.vertices) > 1:
            pen = QPen(QColor(0, 0, 0))
            pen.setWidth(0)
            painter.setPen(pen)
            painter.drawPolyline(QPolygonF(self.vertices))
        if PolygonItem.markPoints:
            scale = painter.transform().m11()
            L_SIZE = 20
            S_SIZE = 10
            if len(self.vertices) > 0:
                scale = painter.transform().m11()
                painter.drawEllipse(self.vertices[0], L_SIZE / scale, L_SIZE / scale)
            for vertex in self.vertices:
                painter.drawEllipse(vertex, S_SIZE / scale, S_SIZE / scale)

    def addPoint(self, pt):
        self.vertices.append(QPointF(pt))
        self.topLeft = QPointF(min(self.topLeft.x(), pt.x()), min(self.topLeft.y(), pt.y()))
        self.bottomRight = QPointF(max(self.bottomRight.x(), pt.x()), max(self.bottomRight.y(), pt.y()))
        self.rect = QRectF(self.topLeft, self.bottomRight).adjusted(-MAR, -MAR, MAR, MAR)

    def removePoint(self):
        if len(self.vertices) > 0:
            self.vertices = self.vertices[:-1]

    def getVertices(self):
        verticesNum = len(self.vertices)
        verticesString = ';\n'.join('%f,%f' % (vertex.x(), vertex.y()) for vertex in self.vertices)
        return (verticesNum, verticesString)

