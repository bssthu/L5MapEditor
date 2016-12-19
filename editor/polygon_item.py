#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : polygon_item.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-09-24
# Description   :
#


from PyQt5.QtCore import QRectF, QPointF
from PyQt5.QtGui import QPolygonF, QPen, QColor
from editor.polygon_base import PolygonBase, COLOR
from editor import polygon_base


class PolygonItem(PolygonBase):
    def __init__(self, polygon):
        """构造函数

        Args:
            polygon (DaoPolygon): 多边形对象
        """
        super().__init__()
        self.layer = polygon.layer
        self.points = polygon_base.get_qt_points(polygon.vertices)
        if len(self.points) > 0:
            self.rect = polygon_base.get_bounding_rect(self.points)
            self.top_left = self.rect.topLeft()
            self.bottom_right = self.rect.topLeft()
            self.rect.adjust(-self.MAR, -self.MAR, self.MAR, self.MAR)
        else:
            self.top_left = QPointF(float('Inf'), float('Inf'))
            self.bottom_right = QPointF(-float('Inf'), -float('Inf'))
            self.rect = QRectF()

    def paint(self, painter, option, widget=None):
        if len(self.points) > 1:
            # init graphics
            pen = QPen(COLOR[self.layer])
            pen.setWidth(0)
            painter.setPen(pen)
            # draw
            painter.drawPolyline(QPolygonF(self.points))
            if PolygonBase.close_polygon:
                painter.drawLine(self.points[-1], self.points[0])
            # easter
            if len(self.points) == 58:
                penLight = QPen(QColor(224, 224, 224))
                penLight.setWidth(0)
                painter.setPen(penLight)
                for i in range(1, 28):
                    painter.drawLine(self.points[i], self.points[-i-1])
