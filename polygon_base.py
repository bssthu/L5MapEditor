#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : polygon_base.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-10-02
# Description   :
#


from PyQt5.QtWidgets import QGraphicsWidget
from PyQt5.QtCore import QRectF, QPointF
from PyQt5.QtGui import QColor


COLOR = (QColor(255, 0, 0), QColor(255, 0, 255), QColor(192, 192, 0), QColor(0, 200, 0), QColor(0, 150, 250))


class PolygonBase(QGraphicsWidget):
    def __init__(self):
        super().__init__()
        self.MAR = 50
        self.points = []
        self.top_left = QPointF(float('Inf'), float('Inf'))
        self.bottom_right = QPointF(-float('Inf'), -float('Inf'))
        self.rect = QRectF()

    def boundingRect(self):
        return self.rect

    def updateBoundingRect(self, pt):
        self.top_left = QPointF(min(self.top_left.x(), pt.x()), min(self.top_left.y(), pt.y()))
        self.bottom_right = QPointF(max(self.bottom_right.x(), pt.x()), max(self.bottom_right.y(), pt.y()))
        self.rect = QRectF(self.top_left, self.bottom_right).adjusted(-self.MAR, -self.MAR, self.MAR, self.MAR)
        self.prepareGeometryChange()

    def moveBoundingRect(self, offset):
        self.top_left += offset
        self.bottom_right += offset
        self.rect.adjust(offset.x(), offset.y(), offset.x(), offset.y())
        self.prepareGeometryChange()

    def getPoints(self):
        return self.points

    def getVertices(self):
        vertices = [[vertex.x(), vertex.y()] for vertex in self.points]
        return vertices


PolygonBase.move_point = False
PolygonBase.close_polygon = True
PolygonBase.highlight_selection = True
PolygonBase.draw_grid = False
PolygonBase.mark_points = True


def getQtPoints(vertices):
    return [QPointF(vertex[0], vertex[1]) for vertex in vertices]


def getBoundingRect(points):
    if len(points) > 0:
        x_list = [point.x() for point in points]
        y_list = [point.y() for point in points]
        top_left = QPointF(min(x_list), min(y_list))
        bottom_right = QPointF(max(x_list), max(y_list))
        return QRectF(top_left, bottom_right)
    else:
        return QRectF()

