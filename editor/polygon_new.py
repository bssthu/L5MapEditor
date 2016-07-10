#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : polygon_new.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-09-28
# Description   :
#


from PyQt5.QtCore import QRectF, QPointF
from PyQt5.QtGui import QColor, QPolygonF, QPen
from editor.polygon_base import PolygonBase


L_SIZE = 20
S_SIZE = 10


class PolygonNew(PolygonBase):
    def __init__(self):
        super().__init__()
        self.mouse_point = None

    def paint(self, painter, option, widget):
        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(0)
        red_pen = QPen(QColor(255, 0, 0))
        red_pen.setWidth(0)
        scale = 1
        # lines
        painter.setPen(pen)
        if len(self.points) > 1:
            painter.drawPolyline(QPolygonF(self.points))
        # point mark
        painter.setPen(pen)
        if PolygonBase.mark_points:
            scale = painter.transform().m11()
            if len(self.points) > 0:
                scale = painter.transform().m11()
                painter.drawEllipse(self.points[0], L_SIZE / scale, L_SIZE / scale)
            for point in self.points:
                painter.drawEllipse(point, S_SIZE / scale, S_SIZE / scale)
        # pre add
        painter.setPen(red_pen)
        if self.mouse_point is not None:
            if len(self.points) > 0:
                painter.drawLine(self.points[-1], self.mouse_point)
            if PolygonBase.mark_points:
                painter.drawEllipse(self.mouse_point, S_SIZE / scale, S_SIZE / scale)

    def preAddPoint(self, pt):
        self.mouse_point = QPointF(pt)
        self.updateBoundingRect(pt)

    def addPoint(self, pt):
        self.mouse_point = None
        self.points.append(QPointF(pt))
        self.updateBoundingRect(pt)

    def removePoint(self):
        if len(self.points) > 0:
            self.points = self.points[:-1]
        self.mouse_point = None

