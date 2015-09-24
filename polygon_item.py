#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : polygon_item.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-09-24
# Description   :
#


import math
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsWidget
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtCore import QRectF, QPointF, QPoint


MAR = 50

class PolygonItem(QGraphicsWidget):
    def __init__(self, type, verticesString):
        QGraphicsWidget.__init__(self)
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
        maxY = min(ylist)
        self.rect = QRectF(minX - MAR, minY - MAR, maxX - minX + 2 * MAR, maxY - minY + 2 * MAR)

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget):
        if len(self.vertices) > 0:
            p0 = self.vertices[0]
            pprev = p0
            for point in self.vertices[1:]:
                painter.drawLine(pprev, point)
                pprev = point
            painter.drawLine(pprev, p0)

