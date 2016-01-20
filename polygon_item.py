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
import polygon_base


class PolygonItem(PolygonBase):
    def __init__(self, polygon):
        super().__init__()
        self.layer = polygon[1]
        vertices = polygon[3]
        self.points = polygon_base.getQtPoints(vertices)
        if len(self.points) > 0:
            self.rect = polygon_base.getBoundingRect(self.points)
            self.top_left = self.rect.topLeft()
            self.bottom_right = self.rect.topLeft()
            self.rect.adjust(-self.MAR, -self.MAR, self.MAR, self.MAR)
        else:
            self.top_left = QPointF(float('Inf'), float('Inf'))
            self.bottom_right = QPointF(-float('Inf'), -float('Inf'))
            self.rect = QRectF()

    def paint(self, painter, option, widget):
        if len(self.points) > 1:
            # init graphics
            pen = QPen(COLOR[self.layer])
            pen.setWidth(0)
            painter.setPen(pen)
            # draw
            painter.drawPolyline(QPolygonF(self.points))
            if PolygonBase.close_polygon:
                painter.drawLine(self.points[-1], self.points[0])

