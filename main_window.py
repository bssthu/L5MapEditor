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
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QGraphicsScene, QTableWidgetItem
from PyQt5.QtWidgets import QFileDialog, QInputDialog
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from ui_Form import Ui_MainWindow
from db_helper import DbHelper
from map_data import MapData


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
        # other signals/slots
        self.ui.polygonTableWidget.itemSelectionChanged.connect(self.polygonSelectionChanged)
        self.ui.scaleSlider.valueChanged.connect(self.scaleSliderChanged)
        self.ui.closePolygonCheckBox.stateChanged.connect(self.closePolygonStateChanged)
        self.ui.graphicsView.polygonCreated.connect(self.addPolygon)
        # open default database
        self.open('default.sqlite')

# slots
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
            self.ui.graphicsView.beginInsert()
        else:
            self.ui.graphicsView.endInsert()

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

    @pyqtSlot(int)
    def closePolygonStateChanged(self, state):
        self.ui.graphicsView.drawClosePolygon(self.ui.closePolygonCheckBox.isChecked())

    @pyqtSlot(int, str)
    def addPolygon(self, verticesNum, vertices):
        id = self.selectedId()
        type = self.ui.insertTypeComboBox.currentIndex()
        self.mapData.addPolygon(id, type, verticesNum, vertices)

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

    def open(self, path):
        if os.path.exists(path):
            try:
                (polygons, levels) = DbHelper.getTables(path)
                self.mapData.set(polygons, levels)
                self.path = path
            except sqlite3.Error as error:
                self.showMessage(repr(error))
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

