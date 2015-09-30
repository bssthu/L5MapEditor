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
from db_helper import DbHelper
from map_data import MapData
from fsm_mgr import FsmMgr


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self)
        # ui
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.graphicsView.setScene(QGraphicsScene())
        self.view = self.ui.graphicsView
        self.scene = self.ui.graphicsView.scene()
        self.ui.polygonTableWidget.setColumnCount(2)
        self.ui.polygonTableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.ui.polygonTableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ui.polygonTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.ui.childrenTableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ui.childrenTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.ui.insertTypeComboBox.addItems(DbHelper.getTypeNames())
        self.ui.graphicsView.scale(1, -1)   # invert y
        # data
        self.mapData = MapData()
        self.mapData.updatePolygonList.connect(self.updatePolygonList)
        self.mapData.updateChildrenList.connect(self.updateChildrenList)
        self.path = None
        # fsm
        self.__initFsm()
        # other signals/slots
        self.ui.polygonTableWidget.itemSelectionChanged.connect(self.polygonSelectionChanged)
        self.ui.scaleSlider.valueChanged.connect(self.scaleSliderChanged)
        self.ui.graphicsView.polygonCreated.connect(self.addPolygon)
        self.ui.graphicsView.polygonUpdated.connect(self.updatePolygon)
        # open default database
        self.open('default.sqlite', True)

    def __initFsm(self):
        self.fsm_mgr = FsmMgr()
        self.fsm_mgr.change_state.connect(self.changeState)
        self.fsm_mgr.getFsm('insert').enter_state.connect(self.ui.graphicsView.beginInsert)
        self.fsm_mgr.getFsm('insert').exit_state.connect(self.ui.graphicsView.endInsert)
        self.fsm_mgr.getFsm('move').enter_state.connect(self.ui.graphicsView.beginMove)
        self.fsm_mgr.getFsm('move').exit_state.connect(self.ui.graphicsView.endMove)

# slots
    @pyqtSlot(QObject)
    def changeState(self, new_state):
        if new_state == self.fsm_mgr.getFsm('normal'):
            self.ui.insertAction.setEnabled(True)
            self.ui.deleteAction.setEnabled(True)
            self.ui.moveAction.setEnabled(True)
            self.ui.graphicsView.setCursor(QCursor(Qt.ArrowCursor))
            self.ui.polygonTableWidget.setEnabled(True)
        elif new_state == self.fsm_mgr.getFsm('insert'):
            self.ui.insertAction.setEnabled(True)
            self.ui.deleteAction.setEnabled(False)
            self.ui.moveAction.setEnabled(False)
            self.ui.graphicsView.setCursor(QCursor(Qt.CrossCursor))
            self.ui.polygonTableWidget.setEnabled(True)
        elif new_state == self.fsm_mgr.getFsm('move'):
            self.ui.insertAction.setEnabled(False)
            self.ui.deleteAction.setEnabled(False)
            self.ui.moveAction.setEnabled(True)
            self.ui.graphicsView.setCursor(QCursor(Qt.DragMoveCursor))
            self.ui.polygonTableWidget.setEnabled(False)

    @pyqtSlot()
    def on_openAction_triggered(self):
        path = QFileDialog.getOpenFileName(self, '载入数据', '.', '数据库文档(*.sqlite)')[0]
        if path:
            self.open(path)

    @pyqtSlot()
    def on_saveAction_triggered(self):
        if self.path is not None:
            self.save(self.path)

    @pyqtSlot()
    def on_insertAction_triggered(self):
        if self.ui.insertAction.isChecked():
            if not self.fsm_mgr.changeFsm('normal', 'insert'):
                self.ui.insertAction.setChecked(False)
        else:
            if not self.fsm_mgr.changeFsm('insert', 'normal'):
                self.ui.insertAction.setChecked(True)

    @pyqtSlot()
    def on_deleteAction_triggered(self):
        id = self.selectedId()
        if id >= 0:
            row = self.ui.polygonTableWidget.currentRow()
            self.mapData.removePolygon(id)
            self.ui.polygonTableWidget.setCurrentCell(row, 0)

    @pyqtSlot()
    def on_aboutAction_triggered(self):
        info = 'L5MapEditor by bssthu\n\n'   \
                'https://github.com/bssthu/L5MapEditor'
        QMessageBox.about(self, '关于', info);

    @pyqtSlot()
    def on_exitAction_triggered(self):
        exit()

    @pyqtSlot()
    def on_moveAction_triggered(self):
        if self.ui.moveAction.isChecked():
            if not self.fsm_mgr.changeFsm('normal', 'move'):
                self.ui.moveAction.setChecked(False)
        else:
            if not self.fsm_mgr.changeFsm('move', 'normal'):
                self.ui.moveAction.setChecked(True)

    @pyqtSlot()
    def on_closedPolygonAction_triggered(self):
        self.ui.graphicsView.drawClosedPolygon(self.ui.closedPolygonAction.isChecked())

    @pyqtSlot()
    def on_dotsAction_triggered(self):
        self.ui.graphicsView.drawSelectionDots(self.ui.dotsAction.isChecked())

    @pyqtSlot()
    def on_gridAction_triggered(self):
        pass

    @pyqtSlot()
    def on_dotAction_triggered(self):
        pass

    @pyqtSlot()
    def on_markPointsAction_triggered(self):
        self.ui.graphicsView.markPoints(self.ui.markPointsAction.isChecked())

    def lockUI(self):
        self.ui.toolBar.setEnabled(False)

    @pyqtSlot()
    def unlockUI(self):
        self.ui.toolBar.setEnabled(True)
        self.ui.graphicsView.scene().update()

    @pyqtSlot(list)
    def updatePolygonList(self, polygons):
        id = self.selectedId()
        self.fillTableWithPolygons(self.ui.polygonTableWidget, polygons)
        self.ui.graphicsView.setPolygons(polygons)
        if len(polygons) > 0:
            if not self.selecteRowById(self.ui.polygonTableWidget, id):
                self.ui.polygonTableWidget.setCurrentCell(0, 0)

    @pyqtSlot(list)
    def updateChildrenList(self, polygons):
        self.fillTableWithPolygons(self.ui.childrenTableWidget, polygons)

    @pyqtSlot()
    def polygonSelectionChanged(self):
        id = self.selectedId()
        if id >= 0:
            polygon = self.mapData.selectPolygon(id)
            self.ui.graphicsView.selectPolygon(polygon)

    @pyqtSlot()
    def scaleSliderChanged(self):
        scale = math.exp(self.ui.scaleSlider.value() / 10)
        self.ui.graphicsView.resetTransform()
        self.ui.graphicsView.scale(scale, -scale)

    @pyqtSlot(int, str)
    def addPolygon(self, verticesNum, vertices):
        id = self.selectedId()
        type = self.ui.insertTypeComboBox.currentIndex()
        self.mapData.addPolygon(id, type, verticesNum, vertices)

    @pyqtSlot(int, str)
    def updatePolygon(self, verticesNum, vertices):
        id = self.selectedId()
        self.mapData.updatePolygon(id, verticesNum, vertices)

    def fillTableWithPolygons(self, tableWidget, polygons):
        tableWidget.clear()
        tableWidget.setRowCount(0)
        tableWidget.setColumnCount(2)
        tableWidget.setHorizontalHeaderLabels(('id', 'type'))
        if len(polygons) > 0:
            TYPE_NAMES = DbHelper.getTypeNames()
            for rowPos in range(0, len(polygons)):
                tableWidget.insertRow(rowPos)
                tableWidget.setItem(rowPos, 0, QTableWidgetItem(str(polygons[rowPos][0]))) # id
                type_id = polygons[rowPos][1]
                tableWidget.setItem(rowPos, 1, QTableWidgetItem(TYPE_NAMES[type_id])) # type
        tableWidget.resizeColumnsToContents()

    def open(self, path, quiet=False):
        if os.path.exists(path):
            try:
                (polygons, levels) = DbHelper.getTables(path)
                self.mapData.set(polygons, levels)
                self.path = path
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
            (polygons, levels) = self.mapData.get()
            DbHelper.writeTables(path, polygons, levels)
        except sqlite3.Error as error:
            self.showMessage(repr(error))

    def selectedId(self):
        row = self.ui.polygonTableWidget.currentRow()
        item = self.ui.polygonTableWidget.item(row, 0)
        if item is not None:
            return int(item.text())
        else:
            return -1

    def selecteRowById(self, tableWidget, polygonId):
        for row in range(0, tableWidget.rowCount()):
            if tableWidget.item(row, 0).text() == str(polygonId):
                tableWidget.setCurrentCell(row, 0)
                return True
        return False

    def showMessage(self, msg, title='L5MapEditor'):
        QMessageBox.information(self, title, msg);


if __name__ == '__main__':
    import sys
    #QApplication.addLibraryPath('./plugins')
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

