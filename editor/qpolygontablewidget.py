#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : qpolygontablewidget.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2016-07-29
# Description   :
#


from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from editor import config_loader


class QPolygonTableWidget(QTableWidget):

    def __init__(self, parent):
        super().__init__(parent)

    def fillWithPolygons(self, polygon_table):
        """在控件中显示多边形

        Args:
            polygon_table: 多边形表
        """
        self.clear()
        self.setRowCount(0)
        self.setColumnCount(3)
        if polygon_table is not None:
            self.setHorizontalHeaderLabels(('id', 'layer', 'type'))
            if len(polygon_table.items()) > 0:
                row = 0
                for polygon_id in sorted(polygon_table.keys()):
                    polygon = polygon_table[polygon_id]
                    self.insertRow(row)
                    # id
                    _id = polygon.polygon_id
                    self.setItem(row, 0, QTableWidgetItem(str(_id)))
                    # layer
                    layer_id = polygon.layer
                    layer_name = config_loader.getLayerName(layer_id)
                    self.setItem(row, 1, QTableWidgetItem(layer_name))
                    # additional
                    additional = polygon.additional
                    self.setItem(row, 2, QTableWidgetItem(str(additional)))
                    row += 1
        self.resizeColumnsToContents()

    def fillWithPoints(self, points):
        """在控件中显示点

        Args:
            points: qpoint list
        """
        self.clear()
        self.setRowCount(0)
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(('x', 'y'))
        for row in range(0, len(points)):
            self.insertRow(row)
            self.setItem(row, 0, QTableWidgetItem(str(points[row].x())))
            self.setItem(row, 1, QTableWidgetItem(str(points[row].y())))
        self.resizeColumnsToContents()

    def getSelectedId(self):
        """当前选中的多边形"""
        row = self.currentRow()
        item = self.item(row, 0)
        if item is not None:
            return int(item.text())
        else:
            return -1

    def selectId(self, polygon_id):
        """根据多边形 id 选中一列

        Args:
            polygon_id: 多边形 id
        """
        for row in range(0, self.rowCount()):
            if self.item(row, 0).text() == str(polygon_id):
                self.setCurrentCell(row, 0)
                return True
        self.setCurrentCell(-1, -1)
        return False

