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

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget):
        if len(self.vertices) > 0:
            closePolygon = PolygonItem.closePolygon
            pen = QPen(QColor(0, 0, 0))
            pen.setWidth(0)
            pen.setStyle(Qt.DashDotLine)
            brush = QBrush(QColor(0, 0, 0), Qt.Dense7Pattern)
            painter.setPen(pen)
            painter.drawPolyline(QPolygonF(self.vertices))
            painter.fillRect(self.rect, brush)
            if closePolygon:
                painter.drawLine(self.vertices[-1], self.vertices[0])
