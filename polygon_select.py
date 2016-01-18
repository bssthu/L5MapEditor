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
from polygon_base import PolygonBase


L_SIZE = 20
S_SIZE = 10
M_SIZE = 15


class PolygonSelect(PolygonBase):
    def __init__(self, vertices, rect):
        super().__init__()
        self.MAR = 50
        self.vertices = vertices
        self.rect = rect
        self.top_left = rect.topLeft() + QPointF(self.MAR, self.MAR)
        self.bottom_right = rect.bottomRight() - QPointF(self.MAR, self.MAR)
        self.dots_rect = self.rect
        self.offset = QPointF(0, 0)
        self.old_vertices = vertices
        self.point_id = -1

    def paint(self, painter, option, widget):
        # init graphics
        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(0)
        pen.setStyle(Qt.DashDotLine)
        redPen = QPen(QColor(255, 0, 0))
        redPen.setWidth(0)
        # current vertices
        vertices = self.__applyOffset(self.vertices, self.offset)
        if len(vertices) > 0:
            # draw
            painter.setPen(pen)
            painter.drawPolyline(QPolygonF(vertices))
            if PolygonBase.highlight_selection:
                brush = QBrush(QColor(0, 0, 0, 64))
                painter.fillRect(self.dots_rect, brush)
            if PolygonBase.close_polygon:
                painter.drawLine(vertices[-1], vertices[0])
        scale = painter.transform().m11()
        if PolygonBase.mark_points:
            if len(vertices) > 0:
                painter.drawEllipse(vertices[0], L_SIZE / scale, L_SIZE / scale)
            for vertex in vertices:
                painter.drawEllipse(vertex, S_SIZE / scale, S_SIZE / scale)
        if self.point_id >= 0:
            painter.setPen(redPen)
            if len(vertices) > 0:
                painter.drawEllipse(vertices[self.point_id], M_SIZE / scale, M_SIZE / scale)

    def setScale(self, scale):
        self.MAR = 20 / scale
        self.dots_rect = QRectF(self.top_left, self.bottom_right).adjusted(-self.MAR, -self.MAR, self.MAR, self.MAR)

    def setPointId(self, point_id):
        self.point_id = point_id

    def setOffset(self, offset):
        self.offset = offset

    def applyOffset(self, offset):  # 移动到某处释放鼠标
        self.vertices = self.__applyOffset(self.vertices, offset)
        if not PolygonBase.move_point:
            self.moveBoundingRect(offset)
        self.offset = QPointF(0, 0)

    def __applyOffset(self, vertices, offset):
        vertices = vertices[:]
        if PolygonBase.move_point:
            if self.point_id >= 0:
                vertices[self.point_id] = vertices[self.point_id] + offset
                self.updateBoundingRect(vertices[self.point_id])
        else:
            vertices = [vertex + offset for vertex in vertices]
        return vertices

    def confirmOffset(self):        # 退出移动状态，保存
        self.old_vertices = self.vertices

    def resetOffset(self):
        self.offset = QPointF(0, 0)
        self.vertices = self.old_vertices

    def getOffset(self):
        return self.offset

