#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : main.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-09-24
# Description   :
#


import os
import math
import sqlite3
from PyQt5 import QtWidgets
from PyQt5.QtGui import QCursor, QColor
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QGraphicsScene, QTableWidgetItem
from PyQt5.QtWidgets import QFileDialog, QInputDialog
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QObject
from editor.ui_Form import Ui_MainWindow
from editor import config_loader
from editor import db_helper
from editor.map_data import MapData
from editor.fsm_mgr import FsmMgr
from editor import log


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        config_loader.loadAll()
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
        self.ui.second_table_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ui.second_table_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.ui.insert_layer_combo_box.addItems(config_loader.getLayerNames())
        self.ui.graphics_view.scale(1, -1)   # invert y
        # data
        self.map_data = MapData()
        self.path = None
        # fsm
        self.__initFsm()
        # other signals/slots
        self.ui.polygon_table_widget.itemSelectionChanged.connect(self.polygonSelectionChanged)
        self.ui.second_table_widget.itemSelectionChanged.connect(self.secondSelectionChanged)
        self.ui.scale_slider.valueChanged.connect(self.scaleSliderChanged)
        self.ui.graphics_view.polygonCreated.connect(self.addPolygon)
        self.ui.graphics_view.polygonUpdated.connect(self.updatePolygon)
        self.ui.graphics_view.pointsUpdated.connect(self.updatePoints)
        log.logger.onLog.connect(self.printToOutput)
        # open default database
        self.setAcceptDrops(True)
        self.open('default.sqlite', True)

    def __initFsm(self):
        """初始化 UI 状态机"""
        self.fsm_mgr = FsmMgr()
        self.fsm_mgr.changeState.connect(self.changeState)
        self.fsm_mgr.getFsm('insert').enterState.connect(self.ui.graphics_view.beginInsert)
        self.fsm_mgr.getFsm('insert').exitState.connect(self.ui.graphics_view.endInsert)
        self.fsm_mgr.getFsm('normal').transferToState.connect(
                lambda name: self.ui.graphics_view.beginMove() if (name == 'move') else None)
        self.fsm_mgr.getFsm('normal').transferToState.connect(
                lambda name: self.ui.graphics_view.beginMove() if (name == 'move_point') else None)
        self.fsm_mgr.getFsm('move').transferToState.connect(
                lambda name: self.ui.graphics_view.endMove() if (name == 'normal') else None)
        self.fsm_mgr.getFsm('move_point').transferToState.connect(
                lambda name: self.ui.graphics_view.endMove() if (name == 'normal') else None)
        self.changeState(self.fsm_mgr.getCurrentState())

# slots
    @pyqtSlot(QObject)
    def changeState(self, new_state):
        """UI 状态转移"""
        if new_state == self.fsm_mgr.getFsm('empty'):
            self.ui.save_action.setEnabled(False)
            self.ui.undo_action.setEnabled(False)
            self.ui.redo_action.setEnabled(False)
            self.ui.insert_action.setEnabled(False)
            self.ui.delete_action.setEnabled(False)
            self.ui.move_action.setEnabled(False)
            self.ui.graphics_view.setCursor(QCursor(Qt.ForbiddenCursor))
            self.ui.polygon_table_widget.setEnabled(False)
            self.ui.list2_type_label.setText('')
        if new_state == self.fsm_mgr.getFsm('normal'):
            self.ui.save_action.setEnabled(True)
            self.ui.undo_action.setEnabled(True)
            self.ui.redo_action.setEnabled(True)
            self.ui.insert_action.setEnabled(True)
            self.ui.delete_action.setEnabled(True)
            self.ui.move_action.setEnabled(True)
            self.ui.graphics_view.setCursor(QCursor(Qt.ArrowCursor))
            self.ui.polygon_table_widget.setEnabled(True)
            self.ui.list2_type_label.setText('children')
            self.ui.second_table_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        elif new_state == self.fsm_mgr.getFsm('insert'):
            self.ui.undo_action.setEnabled(False)
            self.ui.redo_action.setEnabled(False)
            self.ui.insert_action.setEnabled(True)
            self.ui.delete_action.setEnabled(False)
            self.ui.move_action.setEnabled(False)
            self.ui.graphics_view.setCursor(QCursor(Qt.CrossCursor))
            self.ui.polygon_table_widget.setEnabled(True)
            self.ui.list2_type_label.setText('children')
        elif new_state == self.fsm_mgr.getFsm('move'):
            self.ui.undo_action.setEnabled(False)
            self.ui.redo_action.setEnabled(False)
            self.ui.insert_action.setEnabled(False)
            self.ui.delete_action.setEnabled(False)
            self.ui.move_action.setEnabled(True)
            self.ui.graphics_view.setCursor(QCursor(Qt.DragMoveCursor))
            self.ui.polygon_table_widget.setEnabled(False)
            self.ui.list2_type_label.setText('points')
            self.ui.second_table_widget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        elif new_state == self.fsm_mgr.getFsm('move_point'):
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
            self.map_data.undo()
            self.updatePolygonList(self.map_data.getPolygons())
        except Exception as e:
            log.error('撤销操作出错: %s' % repr(e))
            return False
        else:
            return True

    @pyqtSlot()
    def on_redo_action_triggered(self):
        """点击“重做”按钮"""
        try:
            self.map_data.redo()
            self.updatePolygonList(self.map_data.getPolygons())
        except Exception as e:
            log.error('重做操作出错: %s' % repr(e))
            return False
        else:
            return True

    @pyqtSlot()
    def on_insert_action_triggered(self):
        """点击“插入”按钮"""
        if self.ui.insert_action.isChecked():
            if not self.fsm_mgr.changeFsm('normal', 'insert'):
                self.ui.insert_action.setChecked(False)
        else:
            if not self.fsm_mgr.changeFsm('insert', 'normal'):
                self.ui.insert_action.setChecked(True)

    @pyqtSlot()
    def on_delete_action_triggered(self):
        """点击“删除”按钮"""
        _id = self.selectedId()
        if _id >= 0:
            row = self.ui.polygon_table_widget.currentRow()
            self.execute('del shape %d' % _id)
            self.ui.polygon_table_widget.setCurrentCell(row, 0)

    @pyqtSlot()
    def on_about_action_triggered(self):
        """点击“关于”按钮"""
        info = 'L5MapEditor by bssthu\n\n'   \
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
            if not self.fsm_mgr.changeFsm('normal', state_name):
                self.ui.move_action.setChecked(False)
        else:
            if not self.fsm_mgr.changeFsm(state_name, 'normal'):
                self.ui.move_action.setChecked(True)

    @pyqtSlot()
    def on_move_point_action_triggered(self):
        """点击“拾取点”按钮"""
        self.ui.graphics_view.movePoint(self.ui.move_point_action.isChecked())
        if self.ui.move_point_action.isChecked():
            self.fsm_mgr.changeFsm('move', 'move_point')
        else:
            self.fsm_mgr.changeFsm('move_point', 'move')

    @pyqtSlot()
    def on_closed_polygon_action_triggered(self):
        """点击“绘制封闭多边形”按钮"""
        self.ui.graphics_view.drawClosedPolygon(self.ui.closed_polygon_action.isChecked())

    @pyqtSlot()
    def on_highlight_action_triggered(self):
        """点击“突出显示图形”按钮"""
        self.ui.graphics_view.highlightSelection(self.ui.highlight_action.isChecked())

    @pyqtSlot()
    def on_grid_action_triggered(self):
        """点击“显示网格”按钮"""
        pass

    @pyqtSlot()
    def on_mark_points_action_triggered(self):
        """点击“标出点”按钮"""
        self.ui.graphics_view.markPoints(self.ui.mark_points_action.isChecked())

    @pyqtSlot()
    def on_command_edit_returnPressed(self):
        """输入命令后按下回车"""
        commands = self.ui.command_edit.text().strip()
        if commands != '':
            # 执行命令
            self.execute(commands)
        self.ui.command_edit.setText('')

    def lockUI(self):
        """锁定 UI"""
        self.ui.tool_bar.setEnabled(False)

    @pyqtSlot()
    def unlockUI(self):
        """解锁 UI"""
        self.ui.tool_bar.setEnabled(True)
        self.ui.graphics_view.scene().update()

    @pyqtSlot(list)
    def updateChildList(self, polygons):
        """更新 children 列表

        Args:
            polygons: 多边形 list
        """
        self.fillTableWithPolygons(self.ui.second_table_widget, polygons)

    @pyqtSlot()
    def polygonSelectionChanged(self):
        """在多边形列表中选择了多边形"""
        _id = self.selectedId()
        if _id >= 0:
            # draw polygon
            polygon = self.map_data.getPolygon(_id)
            # list children
            child_list = self.map_data.getChildListOfPolygon(_id)
        else:
            # 选中了非法的多边形
            polygon = None
            child_list = []
        self.ui.graphics_view.setSelectedPolygon(polygon)
        self.updateChildList(child_list)

    @pyqtSlot()
    def secondSelectionChanged(self):
        """在第二列选中"""
        if self.ui.move_action.isChecked():
            self.ui.graphics_view.selectPoint(self.ui.second_table_widget.currentRow())

    @pyqtSlot()
    def scaleSliderChanged(self):
        """修改地图缩放比例"""
        scale = math.exp(self.ui.scale_slider.value() / 10)
        self.ui.graphics_view.resetTransform()
        self.ui.graphics_view.scale(scale, -scale)

    @pyqtSlot(list)
    def addPolygon(self, vertices):
        """插入多边形

        Args:
            vertices: 多边形顶点 list, [[x1,y1], [x2,y2], ..., [xn,yn]]
        """
        parent_id = self.selectedId()
        _id = self.map_data.getSpareId(parent_id)
        layer = self.ui.insert_layer_combo_box.currentIndex()
        additional = 0
        commands = ['add shape %d %d %s %d' % (_id, layer, str(additional), parent_id)]
        for vertex in vertices:
            commands.append('add pt %d %f %f' % (_id, vertex[0], vertex[1]))
        self.execute(commands)

    @pyqtSlot(list)
    def updatePolygon(self, vertices):
        """修改当前选中的多边形的顶点坐标

        Args:
            vertices: 多边形顶点 list, [[x1,y1], [x2,y2], ..., [xn,yn]]
        """
        _id = self.selectedId()
        commands = []
        for pt_id in range(0, len(vertices)):
            x = vertices[pt_id][0]
            y = vertices[pt_id][1]
            commands.append('set pt %d %d %f %f' % (_id, pt_id, x, y))
        self.execute(commands)

    @pyqtSlot(list)
    def updatePoints(self, points):
        """更新第二列显示的点

        编辑模式下，第二列显示当前图形的点的坐标。本方法用于更新第二列的显示。

        Args:
            points: 多边形顶点 list, [qpoint1, qpoint2, ..., qpointn]
        """
        row = self.ui.second_table_widget.currentRow()
        self.fillTableWithPoints(self.ui.second_table_widget, points)
        row_count = self.ui.second_table_widget.rowCount()
        if row_count > 0:
            row = min(row_count - 1, max(0, row))
            self.ui.second_table_widget.setCurrentCell(row, 0)

    @pyqtSlot(str, QColor)
    def printToOutput(self, msg, color):
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
            self.map_data.execute(commands)
            self.updatePolygonList(self.map_data.getPolygons())
        except Exception as e:
            log.error('执行命令出错: %s' % repr(e))
            return False
        else:
            return True

    def updatePolygonList(self, polygons):
        """更新多边形列表

        Args:
            polygons: 多边形 list
        """
        _id = self.selectedId()
        self.fillTableWithPolygons(self.ui.polygon_table_widget, polygons)
        self.ui.graphics_view.setPolygons(polygons, len(config_loader.getLayerNames()))
        if len(polygons) > 0:
            if not self.selectRowById(self.ui.polygon_table_widget, _id):
                self.ui.polygon_table_widget.setCurrentCell(0, 0)

    def fillTableWithPolygons(self, table_widget, polygons):
        """在控件中显示多边形

        Args:
            table_widget: 目标控件
            polygons: 多边形 list
        """
        table_widget.clear()
        table_widget.setRowCount(0)
        table_widget.setColumnCount(3)
        table_widget.setHorizontalHeaderLabels(('id', 'layer', 'type'))
        if len(polygons) > 0:
            for row in range(0, len(polygons)):
                table_widget.insertRow(row)
                # id
                _id = polygons[row][0]
                table_widget.setItem(row, 0, QTableWidgetItem(str(_id)))
                # layer
                layer_id = polygons[row][1]
                layer_name = config_loader.getLayerName(layer_id)
                table_widget.setItem(row, 1, QTableWidgetItem(layer_name))
                # type
                type = self.map_data.getAdditionalOfPolygon(_id)
                table_widget.setItem(row, 2, QTableWidgetItem(str(type)))
        table_widget.resizeColumnsToContents()

    def fillTableWithPoints(self, table_widget, points):
        """在控件中显示点

        Args:
            table_widget: 目标控件
            points: qpoint list
        """
        table_widget.clear()
        table_widget.setRowCount(0)
        table_widget.setColumnCount(2)
        table_widget.setHorizontalHeaderLabels(('x', 'y'))
        for row in range(0, len(points)):
            table_widget.insertRow(row)
            table_widget.setItem(row, 0, QTableWidgetItem(str(points[row].x())))
            table_widget.setItem(row, 1, QTableWidgetItem(str(points[row].y())))
        table_widget.resizeColumnsToContents()

    def open(self, path, quiet=False):
        """打开 sqlite 数据库文件

        Args:
            path: 文件路径
            quiet: 报错不弹框
        """
        if os.path.exists(path):
            try:
                (polygons, layers) = db_helper.getTables(path)
                self.map_data.set(polygons, layers)
                self.updatePolygonList(self.map_data.getPolygons())
                self.path = path
                self.fsm_mgr.changeFsm('empty', 'normal')
                log.debug('Open "%s".' % path)
            except sqlite3.Error as error:
                log.error('Failed to open "%s".' % path)
                log.error(repr(error))
                if not quiet:
                    self.showMessage(repr(error))
        else:
            log.error('File %s not exists.' % path)
            if not quiet:
                self.showMessage('File %s not exists.' % path)

    def save(self, path):
        """保存 sqlite 数据库文件

        Args:
            path: 文件路径
        """
        try:
            (polygons, layers) = self.map_data.get()
            db_helper.writeTables(path, polygons, layers)
            self.map_data.updateBackupData()
            log.debug('Save "%s".' % path)
        except sqlite3.Error as error:
            log.error('Failed to save "%s".' % path)
            log.error(repr(error))
            self.showMessage(repr(error))

    def selectedId(self):
        """选中的多边形的 id"""
        row = self.ui.polygon_table_widget.currentRow()
        item = self.ui.polygon_table_widget.item(row, 0)
        if item is not None:
            return int(item.text())
        else:
            return -1

    def selectRowById(self, table_widget, polygon_id):
        """根据多边形的 id 选中行

        Args:
            table_widget: 目标控件
            polygon_id: 多边形 id
        """
        for row in range(0, table_widget.rowCount()):
            if table_widget.item(row, 0).text() == str(polygon_id):
                table_widget.setCurrentCell(row, 0)
                return True
        return False

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

    def showMessage(self, msg, title='L5MapEditor'):
        QMessageBox.information(self, title, msg)

