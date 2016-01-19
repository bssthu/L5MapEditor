#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : polygon_item.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-09-24
# Description   :
#


from PyQt5.QtCore import QRectF, QPointF
from PyQt5.QtGui import QPolygonF, QPen
from polygon_base import PolygonBase, COLOR


class PolygonItem(PolygonBase):
    def __init__(self, layer, vertices):
        super().__init__()
        self.layer = layer
        x_list = []
        y_list = []
        for vertex in vertices:
            self.vertices.append(QPointF(vertex[0], vertex[1]))
            x_list.append(vertex[0])
            y_list.append(vertex[1])
        if len(self.vertices) > 0:
            self.top_left = QPointF(min(x_list), min(y_list))
            self.bottom_right = QPointF(max(x_list), max(y_list))
            self.generateMarginBoundingRectByTopLeftBottomRight()
        else:
            self.top_left = QPointF(float('Inf'), float('Inf'))
            self.bottom_right = QPointF(-float('Inf'), -float('Inf'))
            self.rect = QRectF()

    def paint(self, painter, option, widget):
        if len(self.vertices) > 1:
            # init graphics
            pen = QPen(COLOR[self.layer])
            pen.setWidth(0)
            painter.setPen(pen)
            # draw
            painter.drawPolyline(QPolygonF(self.vertices))
            if PolygonBase.close_polygon:
                painter.drawLine(self.vertices[-1], self.vertices[0])

