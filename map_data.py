#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : map_data.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-09-24
# Description   :
#


from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSlot, pyqtSignal


class MapData(QObject):
    updatePolygonList = pyqtSignal(list)

    def __init__(self):
        QObject.__init__(self)

    def set(self, polygons, l0, l1, l2, l3, l4):
        self.polygons = polygons
        self.l0 = l0
        self.l1 = l1
        self.l2 = l2
        self.l3 = l3
        self.l4 = l4
        self.updatePolygonList.emit(self.polygons)

    @pyqtSlot(int)
    def selectPolygon(self, id):
        print(id)

