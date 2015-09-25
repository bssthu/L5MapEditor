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
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QGraphicsScene, QTableWidgetItem
from PyQt5.QtWidgets import QFileDialog, QInputDialog
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt
from ui_Form import Ui_MainWindow
from db_helper import DbHelper
from map_data import MapData
from polygon_item import PolygonItem


class MainWindow(QMainWindow):
    selectPolygon = pyqtSignal(int)

    def __init__(self, parent = None):
        QMainWindow.__init__(self)
        # ui
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.graphicsView.setScene(QGraphicsScene())
        self.ui.polygonTableWidget.setColumnCount(2)
        self.ui.polygonTableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.ui.polygonTableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ui.polygonTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.ui.polygonTableWidget.itemSelectionChanged.connect(self.PolygonSelectionChanged)
        self.ui.childrenTableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.ui.childrenTableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ui.childrenTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.ui.scaleSlider.valueChanged.connect(self.ScaleSliderChanged)
        self.ui.closePolygonCheckBox.stateChanged.connect(self.ClosePolygonStateChanged)
        self.ui.insertTypeComboBox.addItems(('L0', 'L1', 'L2', 'L3', 'L4'))
        # data
        self.mapData = MapData()
        self.mapData.updatePolygonList.connect(self.updatePolygonList)
        self.mapData.updateChildrenList.connect(self.updateChildrenList)
        self.selectPolygon.connect(self.mapData.selectPolygon)
        self.open('default.sqlite')   # open default database

# slots
    @pyqtSlot()
    def on_openAction_triggered(self):
        path = QFileDialog.getOpenFileName(self, '载入数据', '.',
                '数据库文档(*.sqlite)')[0];
        if path:
            self.open(path)

    @pyqtSlot()
    def on_saveAction_triggered(self):
        path = QFileDialog.getSaveFileName(self, '保存数据', '.',
                '数据库文档(*.sqlite)')[0];
        if path:
            pass

    @pyqtSlot()
    def on_insertAction_triggered(self):
        if self.ui.insertAction.isChecked():
            self.ui.graphicsView.setCursor(QCursor(Qt.CrossCursor))
        else:
            self.ui.graphicsView.setCursor(QCursor(Qt.ArrowCursor))

    @pyqtSlot()
    def on_deleteAction_triggered(self):
        pass

    @pyqtSlot()
    def on_aboutAction_triggered(self):
        info = 'L5MapEditor by bssthu\n\n'   \
                'https://github.com/bssthu/L5MapEditor'
        QMessageBox.about(self, '关于', info);

    @pyqtSlot()
    def on_exitAction_triggered(self):
        exit()

    def lockUI(self):
        self.ui.toolBar.setEnabled(False)

    @pyqtSlot()
    def unlockUI(self):
        self.ui.toolBar.setEnabled(True)
        self.ui.graphicsView.scene().update()

    @pyqtSlot(list)
    def updatePolygonList(self, polygons):
        self.fillTableWithPolygons(self.ui.polygonTableWidget, polygons)
        self.ui.graphicsView.setPolygons(polygons)
        if len(polygons) > 0:
            self.ui.polygonTableWidget.setCurrentCell(0, 0)

    @pyqtSlot(list)
    def updateChildrenList(self, polygons):
        self.fillTableWithPolygons(self.ui.childrenTableWidget, polygons)

    @pyqtSlot()
    def PolygonSelectionChanged(self):
        self.selectPolygon.emit(self.ui.polygonTableWidget.currentRow())

    @pyqtSlot()
    def ScaleSliderChanged(self):
        scale = math.exp(self.ui.scaleSlider.value() / 10)
        self.ui.graphicsView.resetTransform()
        self.ui.graphicsView.scale(scale, scale)

    @pyqtSlot(int)
    def ClosePolygonStateChanged(self, state):
        self.ui.graphicsView.drawClosePolygon(self.ui.closePolygonCheckBox.isChecked())

    def fillTableWithPolygons(self, tableWidget, polygons):
        tableWidget.clear()
        tableWidget.setRowCount(0)
        tableWidget.setColumnCount(2)
        tableWidget.setHorizontalHeaderLabels(('id', 'type'))
        if len(polygons) > 0:
            for rowPos in range(0, len(polygons)):
                tableWidget.insertRow(rowPos)
                tableWidget.setItem(rowPos, 0, QTableWidgetItem(str(polygons[rowPos][0]))) # id
                TYPE_NAME = ('L0', 'L1', 'L2', 'L3', 'L4')
                tableWidget.setItem(rowPos, 1, QTableWidgetItem(TYPE_NAME[polygons[rowPos][1]])) # type
        tableWidget.resizeColumnsToContents()

    def open(self, path):
        if os.path.exists(path):
            try:
                (polygons, l0, l1, l2, l3, l4) = DbHelper.getTables(path)
                self.mapData.set(polygons, l0, l1, l2, l3, l4)
            except Exception as e:
                self.showMessage(str(e))
        else:
            self.showMessage('File %s not exists.' % path)

    def showMessage(self, msg, title='L5MapEditor'):
        QMessageBox.information(self, title, msg);


if __name__ == '__main__':
    import sys
    #QApplication.addLibraryPath('./plugins')
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

