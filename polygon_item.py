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
from PyQt5.QtCore import QRectF, QPoint
from PyQt5.QtGui import QColor, QPolygon, QPen


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
                self.vertices.append(QPoint(vertexF[0], vertexF[1]))
                xlist.append(vertexF[0])
                ylist.append(vertexF[1])
        minX = min(xlist)
        minY = min(ylist)
        maxX = max(xlist)
        maxY = max(ylist)
        self.rect = QRectF(minX - MAR, minY - MAR, maxX - minX + 2 * MAR, maxY - minY + 2 * MAR)

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget):
        if len(self.vertices) > 1:
            pen = QPen(PolygonItem.COLOR[self.type])
            pen.setWidth(0)
            painter.setPen(pen)
            painter.drawPolyline(QPolygon(self.vertices))
            if PolygonItem.closePolygon:
                painter.drawLine(self.vertices[-1], self.vertices[0])


PolygonItem.COLOR = (QColor(255, 0, 0), QColor(255, 0, 255), QColor(255, 127, 0),
        QColor(0, 200, 0), QColor(0, 150, 250))

PolygonItem.closePolygon = True

