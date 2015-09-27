#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : polygon_item.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-09-24
# Description   :
#


import math
from PyQt5.QtWidgets import QGraphicsWidget
from PyQt5.QtCore import QRectF, QPointF
from PyQt5.QtGui import QColor, QPolygonF, QPen


MAR = 50

class PolygonItem(QGraphicsWidget):
    def __init__(self, type, verticesString):
        QGraphicsWidget.__init__(self)
        self.type = type
        self.vertices = []
        xlist = []
        ylist = []
        for vertexString in verticesString.split(';'):
            vertexString = vertexString.strip()
            if vertexString != '':
                vertex = vertexString.split(',')
                vertexF = [ float(vertex[0]), float(vertex[1]) ]
                self.vertices.append(QPointF(vertexF[0], vertexF[1]))
                xlist.append(vertexF[0])
                ylist.append(vertexF[1])
        if len(self.vertices) > 0:
            self.topLeft = QPointF(min(xlist), min(ylist))
            self.bottomRight = QPointF(max(xlist), max(ylist))
            self.rect = QRectF(self.topLeft, self.bottomRight).adjusted(-MAR, -MAR, MAR, MAR)
        else:
            self.topLeft = QPointF(float('Inf'), float('Inf'))
            self.bottomRight = QPointF(-float('Inf'), -float('Inf'))
            self.rect = QRectF()

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget):
        if len(self.vertices) > 1:
            if self.type >= 0:
                pen = QPen(PolygonItem.COLOR[self.type])
                closePolygon = PolygonItem.closePolygon
            else:
                pen = QPen(QColor(0, 0, 0))
                closePolygon = False
            pen.setWidth(0)
            painter.setPen(pen)
            painter.drawPolyline(QPolygonF(self.vertices))
            if closePolygon:
                painter.drawLine(self.vertices[-1], self.vertices[0])

    def addPoint(self, pt):
        self.vertices.append(QPointF(pt))
        self.topLeft = QPointF(min(self.topLeft.x(), pt.x()), min(self.topLeft.y(), pt.y()))
        self.bottomRight = QPointF(max(self.bottomRight.x(), pt.x()), max(self.bottomRight.y(), pt.y()))
        self.rect = QRectF(self.topLeft, self.bottomRight).adjusted(-MAR, -MAR, MAR, MAR)

    def getVertices(self):
        verticesNum = len(self.vertices)
        verticesString = ';\n'.join('%f,%f' % (vertex.x(), vertex.y()) for vertex in self.vertices)
        return (verticesNum, verticesString)


PolygonItem.COLOR = (QColor(255, 0, 0), QColor(255, 0, 255), QColor(255, 127, 0),
        QColor(0, 200, 0), QColor(0, 150, 250))

PolygonItem.closePolygon = True

