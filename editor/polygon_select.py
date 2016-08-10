#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : polygon_select.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-09-24
# Description   :
#


from PyQt5.QtCore import QRectF, QPointF
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPolygonF, QPen, QBrush
from editor import polygon_base
from editor.polygon_base import PolygonBase


L_SIZE = 20
S_SIZE = 10
M_SIZE = 15


class PolygonSelect(PolygonBase):
    def __init__(self, polygon):
        super().__init__()
        self.MAR = 50
        self.points = polygon_base.get_qt_points(polygon.vertices)
        self.rect = polygon_base.get_bounding_rect(self.points)
        self.top_left = self.rect.topLeft()
        self.bottom_right = self.rect.bottomRight()
        self.dots_rect = self.rect
        self.offset = QPointF(0, 0)
        self.old_points = self.points
        self.point_id = -1

    def paint(self, painter, option, widget=None):
        # init graphics
        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(0)
        pen.setStyle(Qt.DashDotLine)
        redPen = QPen(QColor(255, 0, 0))
        redPen.setWidth(0)
        # current points
        points = self.__apply_offset(self.points, self.offset)
        if len(points) > 0:
            # draw
            painter.setPen(pen)
            painter.drawPolyline(QPolygonF(points))
            if PolygonBase.highlight_selection:
                brush = QBrush(QColor(0, 0, 0, 64))
                painter.fillRect(self.dots_rect, brush)
            if PolygonBase.close_polygon:
                painter.drawLine(points[-1], points[0])
        scale = painter.transform().m11()
        if PolygonBase.mark_points:
            if len(points) > 0:
                painter.drawEllipse(points[0], L_SIZE / scale, L_SIZE / scale)
            for point in points:
                painter.drawEllipse(point, S_SIZE / scale, S_SIZE / scale)
        if self.point_id >= 0:
            painter.setPen(redPen)
            if len(points) > 0:
                painter.drawEllipse(points[self.point_id], M_SIZE / scale, M_SIZE / scale)

    def setScale(self, scale):
        self.MAR = 20 / scale
        self.dots_rect = QRectF(self.top_left, self.bottom_right).adjusted(-self.MAR, -self.MAR, self.MAR, self.MAR)

    def set_point_id(self, point_id):
        self.point_id = point_id

    def set_offset(self, offset):
        self.offset = offset

    def apply_offset(self, offset):  # 移动到某处释放鼠标
        self.points = self.__apply_offset(self.points, offset)
        if not PolygonBase.move_point:
            self.move_bounding_rect(offset)
        self.offset = QPointF(0, 0)

    def __apply_offset(self, points, offset):
        points = points[:]
        if PolygonBase.move_point:
            if self.point_id >= 0:
                points[self.point_id] = points[self.point_id] + offset
                self.update_bounding_rect(points[self.point_id])
        else:
            points = [point + offset for point in points]
        return points

    def confirm_offset(self):        # 退出移动状态，保存
        self.old_points = self.points

    def reset_offset(self):
        self.offset = QPointF(0, 0)
        self.points = self.old_points

    def get_offset(self):
        return self.offset
