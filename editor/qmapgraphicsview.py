#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : qmapgraphicsview.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-09-25
# Description   :
#


from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtCore import QPointF
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt
from editor.polygon_base import PolygonBase
from editor.polygon_item import PolygonItem
from editor.polygon_new import PolygonNew
from editor.polygon_select import PolygonSelect
from dao.dao_polygon import DaoPolygon


class QMapGraphicsView(QGraphicsView):
    leftClick = pyqtSignal(QPointF)
    rightClick = pyqtSignal()
    mouseMove = pyqtSignal(QPointF)
    leftUp = pyqtSignal(QPointF)
    polygonCreated = pyqtSignal(list)
    polygonUpdated = pyqtSignal(list)
    pointsUpdated = pyqtSignal(list)

    def __init__(self, parent):
        super().__init__(parent)
        self.selected_polygon = None
        self.move_base = QPointF()
        self.new_polygon = None

# slots
    @pyqtSlot(QPointF)
    def add_point(self, pt):
        self.new_polygon.add_point(pt)

    @pyqtSlot(QPointF)
    def pre_add_point(self, pt):      # 按住鼠标并移动到点
        self.new_polygon.pre_add_point(pt)
        self.scene().invalidate()

    @pyqtSlot()
    def remove_point(self):          # 右键移除最新添加的点
        self.new_polygon.remove_point()

    @pyqtSlot(QPointF)
    def set_move_mouse_base_point(self, pt):    # 移动起点
        self.move_base = pt

    @pyqtSlot(QPointF)
    def set_move_mouse_to_point(self, pt):  # 移动到的点，左键按住
        if self.selected_polygon is not None:
            offset = pt - self.move_base
            self.selected_polygon.set_offset(offset)
            self.scene().invalidate()

    @pyqtSlot(QPointF)
    def finish_move(self, pt):       # 移动到的点，松开左键
        if self.selected_polygon is not None:
            offset = pt - self.move_base
            self.selected_polygon.apply_offset(offset)
            self.pointsUpdated.emit(self.selected_polygon.get_points())

    @pyqtSlot(QPointF)
    def reset_move(self):
        if self.selected_polygon is not None:
            self.selected_polygon.reset_offset()
            self.pointsUpdated.emit(self.selected_polygon.get_points())

    def scale(self, sx, sy):
        super().scale(sx, sy)
        if self.selected_polygon is not None:
            self.selected_polygon.setScale(sx)
        self.scene().invalidate()

    def set_polygons(self, polygon_table, layer_num):
        """设置多边形

        Args:
            polygon_table (dict[int, DaoPolygon]): 多边形表
            layer_num (int): layer 总数
        """
        self.scene().clear()
        for polygon in polygon_table.values():
            if polygon.layer < layer_num:
                self.scene().addItem(PolygonItem(polygon))
        self.scene().setSceneRect(self.scene().itemsBoundingRect())

    def set_selected_polygon(self, polygon):
        """绘制选中的多边形

        Args:
            polygon (DaoPolygon): 列表中选中的多边形
        """
        if self.selected_polygon in self.scene().items():
            self.scene().removeItem(self.selected_polygon)
        if polygon is not None:
            self.selected_polygon = PolygonSelect(polygon)
            self.selected_polygon.setScale(self.transform().m11())
            self.scene().addItem(self.selected_polygon)
        self.scene().invalidate()

    def move_point(self, allow=True):
        """开始或停止移动点

        Args:
            allow (bool): 是否移动
        """
        PolygonBase.move_point = allow

    def select_point(self, point_id):
        """选中一个点

        Args:
            point_id (int): 选中的点的 id
        """
        self.selected_polygon.set_point_id(point_id)
        self.scene().invalidate()

    def draw_closed_polygon(self, allow=True):
        """是否画封闭的多边形

        即最后一个点是否连到第一个点

        Args:
            allow (bool): 是否封闭
        """
        PolygonBase.close_polygon = allow
        self.scene().invalidate()

    def highlight_selection(self, allow=True):
        """是否突出显示选中的多边形（阴影覆盖）

        Args:
            allow (bool): 是否突出显示
        """
        PolygonBase.highlight_selection = allow
        self.scene().invalidate()

    def mark_points(self, allow=True):
        """是否突出显示选中的点

        Args:
            allow (bool): 是否突出显示
        """
        PolygonBase.mark_points = allow
        self.scene().invalidate()

    def begin_insert(self):
        """开始插入多边形流程"""
        # data
        self.new_polygon = PolygonNew()
        self.scene().addItem(self.new_polygon)
        # signal
        self.leftUp.connect(self.add_point)
        self.leftClick.connect(self.pre_add_point)
        self.mouseMove.connect(self.pre_add_point)
        self.rightClick.connect(self.remove_point)

    def end_insert(self):
        """结束插入多边形流程"""
        # 处理新多边形
        vertices = self.new_polygon.get_vertices()
        self.scene().removeItem(self.new_polygon)
        self.new_polygon = None
        if len(vertices) > 0:
            self.polygonCreated.emit(vertices)
        # signal
        self.leftUp.disconnect(self.add_point)
        self.leftClick.disconnect(self.pre_add_point)
        self.mouseMove.disconnect(self.pre_add_point)
        self.rightClick.disconnect(self.remove_point)

    def center_on_polygon(self, polygon):
        """视野中心移到多边形重心

        Args:
            polygon (DaoPolygon): 目标多边形
        """
        if polygon is not None:
            ax, ay = polygon.get_com()
            center_of_mass = QPointF(ax, ay)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.centerOn(center_of_mass)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    def begin_move(self):
        """开始移动流程"""
        # data
        self.pointsUpdated.emit(self.selected_polygon.get_points())
        # signal
        self.leftClick.connect(self.set_move_mouse_base_point)
        self.mouseMove.connect(self.set_move_mouse_to_point)
        self.leftUp.connect(self.finish_move)
        self.rightClick.connect(self.reset_move)

    def end_move(self):
        """结束移动流程"""
        # data
        if self.selected_polygon is not None:
            self.selected_polygon.confirm_offset()
            vertices = self.selected_polygon.get_vertices()
            self.polygonUpdated.emit(vertices)
        # signal
        self.leftClick.disconnect(self.set_move_mouse_base_point)
        self.mouseMove.disconnect(self.set_move_mouse_to_point)
        self.leftUp.disconnect(self.finish_move)
        self.rightClick.disconnect(self.reset_move)

    def mousePressEvent(self, event):       # 鼠标按下
        button = event.button()
        pt = self.mapToScene(event.pos())
        if button == Qt.LeftButton:
            self.leftClick.emit(pt)
        elif button == Qt.RightButton:
            self.rightClick.emit()
        self.scene().invalidate()

    def mouseMoveEvent(self, event):        # 鼠标移动
        pt = self.mapToScene(event.pos())
        if event.buttons() == Qt.LeftButton:
            self.mouseMove.emit(pt)

    def mouseReleaseEvent(self, event):     # 鼠标释放
        button = event.button()
        pt = self.mapToScene(event.pos())
        if button == Qt.LeftButton:
            self.leftUp.emit(pt)
