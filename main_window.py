#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : mainWindow.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-09-24
# Description   :
#


import os
import math
import sqlite3
from PyQt5 import QtWidgets
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QGraphicsScene, QTableWidgetItem
from PyQt5.QtWidgets import QFileDialog, QInputDialog
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QObject
from ui_Form import Ui_MainWindow
import db_helper
from map_data import MapData
from fsm_mgr import FsmMgr


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        db_helper.loadLayerNames()
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
        self.ui.insert_layer_combo_box.addItems(db_helper.getLayerNames())
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
        # open default database
        self.setAcceptDrops(True)
        self.open('default.sqlite', True)

    def __initFsm(self):
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
        if new_state == self.fsm_mgr.getFsm('empty'):
            self.ui.save_action.setEnabled(False)
            self.ui.insert_action.setEnabled(False)
            self.ui.delete_action.setEnabled(False)
            self.ui.move_action.setEnabled(False)
            self.ui.graphics_view.setCursor(QCursor(Qt.ForbiddenCursor))
            self.ui.polygon_table_widget.setEnabled(False)
            self.ui.list2_type_label.setText('')
        if new_state == self.fsm_mgr.getFsm('normal'):
            self.ui.save_action.setEnabled(True)
            self.ui.insert_action.setEnabled(True)
            self.ui.delete_action.setEnabled(True)
            self.ui.move_action.setEnabled(True)
            self.ui.graphics_view.setCursor(QCursor(Qt.ArrowCursor))
            self.ui.polygon_table_widget.setEnabled(True)
            self.ui.list2_type_label.setText('children')
            self.ui.second_table_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        elif new_state == self.fsm_mgr.getFsm('insert'):
            self.ui.insert_action.setEnabled(True)
            self.ui.delete_action.setEnabled(False)
            self.ui.move_action.setEnabled(False)
            self.ui.graphics_view.setCursor(QCursor(Qt.CrossCursor))
            self.ui.polygon_table_widget.setEnabled(True)
            self.ui.list2_type_label.setText('children')
        elif new_state == self.fsm_mgr.getFsm('move'):
            self.ui.insert_action.setEnabled(False)
            self.ui.delete_action.setEnabled(False)
            self.ui.move_action.setEnabled(True)
            self.ui.graphics_view.setCursor(QCursor(Qt.DragMoveCursor))
            self.ui.polygon_table_widget.setEnabled(False)
            self.ui.list2_type_label.setText('points')
            self.ui.second_table_widget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        elif new_state == self.fsm_mgr.getFsm('move_point'):
            self.ui.insert_action.setEnabled(False)
            self.ui.delete_action.setEnabled(False)
            self.ui.move_action.setEnabled(True)
            self.ui.graphics_view.setCursor(QCursor(Qt.DragMoveCursor))
            self.ui.polygon_table_widget.setEnabled(False)
            self.ui.list2_type_label.setText('points')

    @pyqtSlot()
    def on_open_action_triggered(self):
        path = QFileDialog.getOpenFileName(self, '载入数据', '.', '数据库文档(*.sqlite)')[0]
        if path:
            self.open(path)

    @pyqtSlot()
    def on_save_action_triggered(self):
        if self.path is not None:
            self.save(self.path)

    @pyqtSlot()
    def on_insert_action_triggered(self):
        if self.ui.insert_action.isChecked():
            if not self.fsm_mgr.changeFsm('normal', 'insert'):
                self.ui.insert_action.setChecked(False)
        else:
            if not self.fsm_mgr.changeFsm('insert', 'normal'):
                self.ui.insert_action.setChecked(True)

    @pyqtSlot()
    def on_delete_action_triggered(self):
        _id = self.selectedId()
        if _id >= 0:
            row = self.ui.polygon_table_widget.currentRow()
            self.execute('del shape %d' % _id)
            self.ui.polygon_table_widget.setCurrentCell(row, 0)

    @pyqtSlot()
    def on_about_action_triggered(self):
        info = 'L5MapEditor by bssthu\n\n'   \
                'https://github.com/bssthu/L5MapEditor'
        QMessageBox.about(self, '关于', info)

    @pyqtSlot()
    def on_exit_action_triggered(self):
        exit()

    @pyqtSlot()
    def on_move_action_triggered(self):
        state_name = 'move' if not self.ui.move_point_action.isChecked() else 'move_point'
        if self.ui.move_action.isChecked():
            if not self.fsm_mgr.changeFsm('normal', state_name):
                self.ui.move_action.setChecked(False)
        else:
            if not self.fsm_mgr.changeFsm(state_name, 'normal'):
                self.ui.move_action.setChecked(True)

    @pyqtSlot()
    def on_move_point_action_triggered(self):
        self.ui.graphics_view.movePoint(self.ui.move_point_action.isChecked())
        if self.ui.move_point_action.isChecked():
            self.fsm_mgr.changeFsm('move', 'move_point')
        else:
            self.fsm_mgr.changeFsm('move_point', 'move')

    @pyqtSlot()
    def on_closed_polygon_action_triggered(self):
        self.ui.graphics_view.drawClosedPolygon(self.ui.closed_polygon_action.isChecked())

    @pyqtSlot()
    def on_highlight_action_triggered(self):
        self.ui.graphics_view.highlightSelection(self.ui.highlight_action.isChecked())

    @pyqtSlot()
    def on_grid_action_triggered(self):
        pass

    @pyqtSlot()
    def on_mark_points_action_triggered(self):
        self.ui.graphics_view.markPoints(self.ui.mark_points_action.isChecked())

    def lockUI(self):
        self.ui.tool_bar.setEnabled(False)

    @pyqtSlot()
    def unlockUI(self):
        self.ui.tool_bar.setEnabled(True)
        self.ui.graphics_view.scene().update()

    @pyqtSlot(list)
    def updateChildList(self, polygons):
        self.fillTableWithPolygons(self.ui.second_table_widget, polygons)

    @pyqtSlot()
    def polygonSelectionChanged(self):
        _id = self.selectedId()
        if _id >= 0:
            # draw polygon
            polygon = self.map_data.getPolygon(_id)
            self.ui.graphics_view.setSelectedPolygon(polygon)
            # list children
            child_list = self.map_data.getChildListOfPolygon(_id)
            self.updateChildList(child_list)

    @pyqtSlot()
    def secondSelectionChanged(self):
        if self.ui.move_action.isChecked():
            self.ui.graphics_view.selectPoint(self.ui.second_table_widget.currentRow())

    @pyqtSlot()
    def scaleSliderChanged(self):
        scale = math.exp(self.ui.scale_slider.value() / 10)
        self.ui.graphics_view.resetTransform()
        self.ui.graphics_view.scale(scale, -scale)

    @pyqtSlot(list)
    def addPolygon(self, vertices):
        parent_id = self.selectedId()
        _id = self.map_data.getSpareId(parent_id)
        layer = self.ui.insert_layer_combo_box.currentIndex()
        additional = 0
        self.execute('add shape %d %d %s %d' % (_id, layer, str(additional), parent_id))
        for vertex in vertices:
            self.execute('add pt %d %f %f' % (_id, vertex[0], vertex[1]))

    @pyqtSlot(list)
    def updatePolygon(self, vertices):
        _id = self.selectedId()
        self.map_data.updatePolygon(_id, vertices)

    @pyqtSlot(list)
    def updatePoints(self, points):
        row = self.ui.second_table_widget.currentRow()
        self.fillTableWithPoints(self.ui.second_table_widget, points)
        row_count = self.ui.second_table_widget.rowCount()
        if row_count > 0:
            row = min(row_count - 1, max(0, row))
            self.ui.second_table_widget.setCurrentCell(row, 0)

    def execute(self, command):
        try:
            self.map_data.execute(command)
            self.updatePolygonList(self.map_data.getPolygons())
        except Exception as e:
            self.showMessage(repr(e), '执行命令出错')
            return False
        else:
            return True

    def updatePolygonList(self, polygons):
        _id = self.selectedId()
        self.fillTableWithPolygons(self.ui.polygon_table_widget, polygons)
        self.ui.graphics_view.setPolygons(polygons, len(db_helper.getLayerNames()))
        if len(polygons) > 0:
            if not self.selectRowById(self.ui.polygon_table_widget, _id):
                self.ui.polygon_table_widget.setCurrentCell(0, 0)

    def fillTableWithPolygons(self, table_widget, polygons):
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
                layer_name = db_helper.getLayerName(layer_id)
                table_widget.setItem(row, 1, QTableWidgetItem(layer_name))
                # type
                type = self.map_data.getAdditionalOfPolygon(_id)
                table_widget.setItem(row, 2, QTableWidgetItem(str(type)))
        table_widget.resizeColumnsToContents()

    def fillTableWithPoints(self, table_widget, points):
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
        if os.path.exists(path):
            try:
                (polygons, levels) = db_helper.getTables(path)
                self.map_data.set(polygons, levels)
                self.updatePolygonList(self.map_data.getPolygons())
                self.path = path
                self.fsm_mgr.changeFsm('empty', 'normal')
            except sqlite3.Error as error:
                if quiet:
                    print(repr(error))
                else:
                    self.showMessage(repr(error))
        else:
            if quiet:
                print('File %s not exists.' % path)
            else:
                self.showMessage('File %s not exists.' % path)

    def save(self, path):
        try:
            (polygons, levels) = self.map_data.get()
            db_helper.writeTables(path, polygons, levels)
        except sqlite3.Error as error:
            self.showMessage(repr(error))

    def selectedId(self):
        row = self.ui.polygon_table_widget.currentRow()
        item = self.ui.polygon_table_widget.item(row, 0)
        if item is not None:
            return int(item.text())
        else:
            return -1

    def selectRowById(self, table_widget, polygon_id):
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


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

