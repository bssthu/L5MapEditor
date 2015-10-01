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
from polygon_base import PolygonBase


MAR = 50

class PolygonItem(PolygonBase):
    def __init__(self, type, verticesString):
        super().__init__()
        self.type = type
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

    def paint(self, painter, option, widget):
        if len(self.vertices) > 1:
            # init graphics
            pen = QPen(PolygonItem.COLOR[self.type])
            pen.setWidth(0)
            painter.setPen(pen)
            # draw
            painter.drawPolyline(QPolygonF(self.vertices))
            if PolygonItem.closePolygon:
                painter.drawLine(self.vertices[-1], self.vertices[0])

