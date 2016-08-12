#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : main.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-09-24
# Description   :
#


import math
import os
import sqlite3

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, Qt, QObject
from PyQt5.QtGui import QCursor, QColor
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMessageBox

from dao.db_helper import DbHelper
from editor import config_loader
from editor import log
from editor.fsm_mgr import FsmMgr
from editor.map_command import MapCommand
from editor.ui_Form import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        config_loader.load_all()
        # ui
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.graphics_view.setScene(QGraphicsScene())
        self.view = self.ui.graphics_view
        self.scene = self.ui.graphics_view.scene()
        self.ui.polygon_table_widget.setColumnCount(2)
        self.ui.polygon_table_widget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.ui.polygon_table_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ui.polygon_table_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.ui.second_table_widget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.ui.second_table_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ui.second_table_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.ui.insert_layer_combo_box.addItems(config_loader.get_layer_names())
        self.ui.graphics_view.scale(1, -1)   # invert y
        # data
        self.db = DbHelper()
        self.command_handler = MapCommand(self.db)
        self.path = None
        # fsm
        self.__init_fsm()
        # other signals/slots
        self.ui.polygon_table_widget.itemSelectionChanged.connect(self.polygon_selection_changed)
        self.ui.second_table_widget.itemSelectionChanged.connect(self.second_selection_changed)
        self.ui.scale_slider.valueChanged.connect(self.scale_slider_changed)
        self.ui.graphics_view.polygonCreated.connect(self.add_polygon)
        self.ui.graphics_view.polygonUpdated.connect(self.update_polygon)
        self.ui.graphics_view.pointsUpdated.connect(self.update_points)
        log.logger.onLog.connect(self.print_to_output)
        # open default database
        self.setAcceptDrops(True)
        self.open('default.sqlite', True)

    def __init_fsm(self):
        """初始化 UI 状态机"""
        self.fsm_mgr = FsmMgr()
        self.fsm_mgr.changeState.connect(self.change_state)
        self.fsm_mgr.get_fsm('insert').enterState.connect(self.ui.graphics_view.begin_insert)
        self.fsm_mgr.get_fsm('insert').exitState.connect(self.ui.graphics_view.end_insert)
        self.fsm_mgr.get_fsm('normal').transferToState.connect(
                lambda name: self.ui.graphics_view.begin_move() if (name == 'move') else None)
        self.fsm_mgr.get_fsm('normal').transferToState.connect(
                lambda name: self.ui.graphics_view.begin_move() if (name == 'move_point') else None)
        self.fsm_mgr.get_fsm('move').transferToState.connect(
                lambda name: self.ui.graphics_view.end_move() if (name == 'normal') else None)
        self.fsm_mgr.get_fsm('move_point').transferToState.connect(
                lambda name: self.ui.graphics_view.end_move() if (name == 'normal') else None)
        self.change_state(self.fsm_mgr.get_current_state())

# slots
    @pyqtSlot(QObject)
    def change_state(self, new_state):
        """UI 状态转移"""
        if new_state == self.fsm_mgr.get_fsm('empty'):
            self.ui.save_action.setEnabled(False)
            self.ui.undo_action.setEnabled(False)
            self.ui.redo_action.setEnabled(False)
            self.ui.insert_action.setEnabled(False)
            self.ui.delete_action.setEnabled(False)
            self.ui.move_action.setEnabled(False)
            self.ui.graphics_view.setCursor(QCursor(Qt.ForbiddenCursor))
            self.ui.polygon_table_widget.setEnabled(False)
            self.ui.list2_type_label.setText('')
        if new_state == self.fsm_mgr.get_fsm('normal'):
            self.ui.save_action.setEnabled(True)
            self.ui.undo_action.setEnabled(True)
            self.ui.redo_action.setEnabled(True)
            self.ui.insert_action.setEnabled(True)
            self.ui.delete_action.setEnabled(True)
            self.ui.move_action.setEnabled(True)
            self.ui.graphics_view.setCursor(QCursor(Qt.ArrowCursor))
            self.ui.polygon_table_widget.setEnabled(True)
            self.ui.list2_type_label.setText('children')
        elif new_state == self.fsm_mgr.get_fsm('insert'):
            self.ui.undo_action.setEnabled(False)
            self.ui.redo_action.setEnabled(False)
            self.ui.insert_action.setEnabled(True)
            self.ui.delete_action.setEnabled(False)
            self.ui.move_action.setEnabled(False)
            self.ui.graphics_view.setCursor(QCursor(Qt.CrossCursor))
            self.ui.polygon_table_widget.setEnabled(True)
            self.ui.list2_type_label.setText('children')
        elif new_state == self.fsm_mgr.get_fsm('move'):
            self.ui.undo_action.setEnabled(False)
            self.ui.redo_action.setEnabled(False)
            self.ui.insert_action.setEnabled(False)
            self.ui.delete_action.setEnabled(False)
            self.ui.move_action.setEnabled(True)
            self.ui.graphics_view.setCursor(QCursor(Qt.DragMoveCursor))
            self.ui.polygon_table_widget.setEnabled(False)
            self.ui.list2_type_label.setText('points')
        elif new_state == self.fsm_mgr.get_fsm('move_point'):
            self.ui.undo_action.setEnabled(False)
            self.ui.redo_action.setEnabled(False)
            self.ui.insert_action.setEnabled(False)
            self.ui.delete_action.setEnabled(False)
            self.ui.move_action.setEnabled(True)
            self.ui.graphics_view.setCursor(QCursor(Qt.DragMoveCursor))
            self.ui.polygon_table_widget.setEnabled(False)
            self.ui.list2_type_label.setText('points')

    @pyqtSlot()
    def on_open_action_triggered(self):
        """点击“打开”按钮"""
        path = QFileDialog.getOpenFileName(self, '载入数据', '.', '数据库文档(*.sqlite)')[0]
        if path:
            self.open(path)

    @pyqtSlot()
    def on_save_action_triggered(self):
        """点击“保存”按钮"""
        if self.path is not None:
            self.save(self.path)

    @pyqtSlot()
    def on_undo_action_triggered(self):
        """点击“撤销”按钮"""
        try:
            self.command_handler.undo()
            self.update_polygon_list()
        except Exception as e:
            log.error('撤销操作出错: %s' % repr(e))
            return False
        else:
            return True

    @pyqtSlot()
    def on_redo_action_triggered(self):
        """点击“重做”按钮"""
        try:
            self.command_handler.redo()
            self.update_polygon_list()
        except Exception as e:
            log.error('重做操作出错: %s' % repr(e))
            return False
        else:
            return True

    @pyqtSlot()
    def on_insert_action_triggered(self):
        """点击“插入”按钮"""
        if self.ui.insert_action.isChecked():
            if not self.fsm_mgr.change_fsm('normal', 'insert'):
                self.ui.insert_action.setChecked(False)
        else:
            if not self.fsm_mgr.change_fsm('insert', 'normal'):
                self.ui.insert_action.setChecked(True)

    @pyqtSlot()
    def on_delete_action_triggered(self):
        """点击“删除”按钮"""
        _id = self.selected_id()
        if _id >= 0:
            row = self.ui.polygon_table_widget.currentRow()
            self.execute('del shape %d' % _id)
            self.ui.polygon_table_widget.setCurrentCell(row, 0)

    @pyqtSlot()
    def on_about_action_triggered(self):
        """点击“关于”按钮"""
        info = 'L5MapEditor by bssthu\n\n' \
               'https://github.com/bssthu/L5MapEditor'
        QMessageBox.about(self, '关于', info)

    @pyqtSlot()
    def on_exit_action_triggered(self):
        """点击“退出”按钮"""
        exit()

    @pyqtSlot()
    def on_move_action_triggered(self):
        """点击“移动”按钮"""
        state_name = 'move' if not self.ui.move_point_action.isChecked() else 'move_point'
        if self.ui.move_action.isChecked():
            if not self.fsm_mgr.change_fsm('normal', state_name):
                self.ui.move_action.setChecked(False)
        else:
            if not self.fsm_mgr.change_fsm(state_name, 'normal'):
                self.ui.move_action.setChecked(True)

    @pyqtSlot()
    def on_move_point_action_triggered(self):
        """点击“拾取点”按钮"""
        self.ui.graphics_view.move_point(self.ui.move_point_action.isChecked())
        if self.ui.move_point_action.isChecked():
            self.fsm_mgr.change_fsm('move', 'move_point')
        else:
            self.fsm_mgr.change_fsm('move_point', 'move')

    @pyqtSlot()
    def on_closed_polygon_action_triggered(self):
        """点击“绘制封闭多边形”按钮"""
        self.ui.graphics_view.draw_closed_polygon(self.ui.closed_polygon_action.isChecked())

    @pyqtSlot()
    def on_highlight_action_triggered(self):
        """点击“突出显示图形”按钮"""
        self.ui.graphics_view.highlight_selection(self.ui.highlight_action.isChecked())

    @pyqtSlot()
    def on_grid_action_triggered(self):
        """点击“显示网格”按钮"""
        pass

    @pyqtSlot()
    def on_mark_points_action_triggered(self):
        """点击“标出点”按钮"""
        self.ui.graphics_view.mark_points(self.ui.mark_points_action.isChecked())

    @pyqtSlot()
    def on_command_edit_return_pressed(self):
        """输入命令后按下回车"""
        commands = self.ui.command_edit.text().strip()
        if commands != '':
            # 执行命令
            self.execute(commands)
        self.ui.command_edit.setText('')

    def lock_ui(self):
        """锁定 UI"""
        self.ui.tool_bar.setEnabled(False)

    @pyqtSlot()
    def unlock_ui(self):
        """解锁 UI"""
        self.ui.tool_bar.setEnabled(True)
        self.ui.graphics_view.scene().update()

    @pyqtSlot(list)
    def update_child_list(self, polygon_table):
        """更新 children 列表

        Args:
            polygon_table: 多边形表
        """
        self.ui.second_table_widget.fill_with_polygons(polygon_table)

    @pyqtSlot()
    def polygon_selection_changed(self):
        """在多边形列表中选择了多边形"""
        _id = self.selected_id()
        if _id >= 0:
            # draw polygon
            polygon = self.db.get_polygon_by_id(_id)
            # list children
            child_list = self.db.get_children_table_by_id(_id)
        else:
            # 选中了非法的多边形
            polygon = None
            child_list = {}
        self.ui.graphics_view.set_selected_polygon(polygon)
        self.update_child_list(child_list)
        return

    @pyqtSlot()
    def second_selection_changed(self):
        """在第二列选中"""
        if self.ui.move_action.isChecked():
            self.ui.graphics_view.select_point(self.ui.second_table_widget.currentRow())

    @pyqtSlot()
    def scale_slider_changed(self):
        """修改地图缩放比例"""
        scale = math.exp(self.ui.scale_slider.value() / 10)
        self.ui.graphics_view.resetTransform()
        self.ui.graphics_view.scale(scale, -scale)

    @pyqtSlot(list)
    def add_polygon(self, vertices):
        """插入多边形

        Args:
            vertices: 多边形顶点 list, [[x1,y1], [x2,y2], ..., [xn,yn]]
        """
        parent_id = self.selected_id()
        _id = self.command_handler.get_spare_id(parent_id)
        layer = self.ui.insert_layer_combo_box.currentIndex()
        additional = 0
        if layer == 0:
            commands = ['add shape %d %d %s' % (_id, layer, str(additional))]
        else:
            commands = ['add shape %d %d %s %d' % (_id, layer, str(additional), parent_id)]
        for vertex in vertices:
            commands.append('add pt %d %f %f' % (_id, vertex[0], vertex[1]))
        self.execute(commands)

    @pyqtSlot(list)
    def update_polygon(self, vertices):
        """修改当前选中的多边形的顶点坐标

        Args:
            vertices: 多边形顶点 list, [[x1,y1], [x2,y2], ..., [xn,yn]]
        """
        _id = self.selected_id()
        commands = []
        for pt_id in range(0, len(vertices)):
            x = vertices[pt_id][0]
            y = vertices[pt_id][1]
            commands.append('set pt %d %d %f %f' % (_id, pt_id, x, y))
        self.execute(commands)

    @pyqtSlot(list)
    def update_points(self, points):
        """更新第二列显示的点

        编辑模式下，第二列显示当前图形的点的坐标。本方法用于更新第二列的显示。

        Args:
            points: 多边形顶点 list, [qpoint1, qpoint2, ..., qpointn]
        """
        row = self.ui.second_table_widget.currentRow()
        self.ui.second_table_widget.fill_with_points(points)
        row_count = self.ui.second_table_widget.rowCount()
        if row_count > 0:
            row = min(row_count - 1, max(0, row))
            self.ui.second_table_widget.setCurrentCell(row, 0)

    @pyqtSlot(str, QColor)
    def print_to_output(self, msg, color):
        """打印到输出窗口

        Args:
            msg: 输出内容
            color: 输出颜色, QColor
        """
        print(msg)
        self.ui.output_browser.setTextColor(color)
        self.ui.output_browser.append(msg)

    def execute(self, commands):
        """执行命令

        Args:
            commands: 待执行命令
        """
        log.debug(commands)
        try:
            self.command_handler.execute(commands)
            self.update_polygon_list()
        except Exception as e:
            log.error('执行命令出错: %s' % repr(e))
            return False
        else:
            return True

    def update_polygon_list(self):
        """更新多边形列表"""
        polygon_table = self.db.polygon_table
        _id = self.selected_id()
        self.ui.polygon_table_widget.fill_with_polygons(polygon_table)
        self.ui.graphics_view.set_polygons(polygon_table, len(config_loader.get_layer_names()))
        if len(polygon_table) > 0:
            if not self.select_row_by_id(_id):
                self.ui.polygon_table_widget.setCurrentCell(0, 0)

    def open(self, path, quiet=False):
        """打开 sqlite 数据库文件

        Args:
            path: 文件路径
            quiet: 报错不弹框
        """
        if os.path.exists(path):
            try:
                self.db.load_tables(path)
                self.command_handler.reset_backup_data()
                self.update_polygon_list()
                self.path = path
                self.fsm_mgr.change_fsm('empty', 'normal')
                log.debug('Open "%s".' % path)
            except sqlite3.Error as error:
                log.error('Failed to open "%s".' % path)
                log.error(repr(error))
                if not quiet:
                    self.show_message(repr(error))
        else:
            log.error('File %s not exists.' % path)
            if not quiet:
                self.show_message('File %s not exists.' % path)

    def save(self, path):
        """保存 sqlite 数据库文件

        Args:
            path: 文件路径
        """
        try:
            self.db.write_to_file(path)
            self.command_handler.reset_backup_data()
            log.debug('Save "%s".' % path)
        except sqlite3.Error as error:
            log.error('Failed to save "%s".' % path)
            log.error(repr(error))
            self.show_message(repr(error))

    def selected_id(self):
        """选中的多边形的 id"""
        return self.ui.polygon_table_widget.get_selected_id()

    def select_row_by_id(self, polygon_id):
        """根据多边形的 id 选中行

        Args:
            polygon_id: 多边形 id
        """
        return self.ui.polygon_table_widget.select_id(polygon_id)

    def show_message(self, msg, title='L5MapEditor'):
        QMessageBox.information(self, title, msg)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        url = event.mimeData().urls()[0]
        if url.isLocalFile():
            path = url.toLocalFile()
            if os.path.isfile(path):
                self.open(path)
