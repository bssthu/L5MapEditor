#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : polygon_base.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-10-02
# Description   :
#


import math
from PyQt5.QtWidgets import QGraphicsWidget
from PyQt5.QtCore import QRectF, QPointF
from PyQt5.QtGui import QColor, QPolygonF, QPen


MAR = 50

class PolygonBase(QGraphicsWidget):
    def __init__(self):
        super().__init__()
        self.vertices = []
        self.topLeft = QPointF(float('Inf'), float('Inf'))
        self.bottomRight = QPointF(-float('Inf'), -float('Inf'))
        self.rect = QRectF()

    def boundingRect(self):
        return self.rect

    def updateBoundingRect(self, pt):
        self.topLeft = QPointF(min(self.topLeft.x(), pt.x()), min(self.topLeft.y(), pt.y()))
        self.bottomRight = QPointF(max(self.bottomRight.x(), pt.x()), max(self.bottomRight.y(), pt.y()))
        self.rect = QRectF(self.topLeft, self.bottomRight).adjusted(-MAR, -MAR, MAR, MAR)
        self.prepareGeometryChange()

    def moveBoundingRect(self, offset):
        self.topLeft = self.topLeft + offset
        self.bottomRight = self.bottomRight + offset
        self.rect.adjust(offset.x(), offset.y(), offset.x(), offset.y())
        self.prepareGeometryChange()

    def getVertices(self):
        return self.vertices

    def getVerticesForDb(self):
        verticesNum = len(self.vertices)
        verticesString = ';\n'.join('%f,%f' % (vertex.x(), vertex.y()) for vertex in self.vertices)
        return (verticesNum, verticesString)


PolygonBase.COLOR = (QColor(255, 0, 0), QColor(255, 0, 255), QColor(192, 192, 0),
        QColor(0, 200, 0), QColor(0, 150, 250))

PolygonBase.movePoint = False
PolygonBase.closePolygon = True
PolygonBase.drawDots = True
PolygonBase.drawGrid = False
PolygonBase.markPoints = True

