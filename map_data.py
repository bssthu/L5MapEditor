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
    updateChildrenList = pyqtSignal(list)

    def __init__(self):
        QObject.__init__(self)

    def set(self, polygons, l0, l1, l2, l3, l4):
        self.polygons = polygons
        self.levels = []
        self.levels.append(l0)
        self.levels.append(l1)
        self.levels.append(l2)
        self.levels.append(l3)
        self.levels.append(l4)
        # polygon 索引
        self.polygonsDict = {}
        for polygon in self.polygons:
            polygon_id = polygon[0]
            self.polygonsDict[polygon_id] = polygon
        # 把 child 单独整理出来
        self.childrenDict = {}
        for level in self.levels[1:]:
            for record in level:
                polygon_id = record[1]
                parent_id = record[2]
                if parent_id not in self.childrenDict:
                    self.childrenDict[parent_id] = []
                self.childrenDict[parent_id].append(polygon_id)
        # notify
        self.updatePolygonList.emit(self.polygons)

    def get(self):
        return (self.polygons, self.levels)

    def selectPolygon(self, polygon_id):
        children = []
        if polygon_id in self.childrenDict:
            for child_id in self.childrenDict[polygon_id]:
                children.append(self.polygonsDict[child_id])
        self.updateChildrenList.emit(children)
        return self.polygonsDict[polygon_id]

    def addPolygon(self, parent_id, type, verticesNum, vertices):
        polygon_id = parent_id
        while polygon_id in self.polygonsDict:
            polygon_id += 1
        # add polygon
        polygon = (polygon_id, type, verticesNum, vertices)
        self.polygons.append(polygon)
        self.polygonsDict[polygon_id] = polygon
        # set parent
        if type > 0:
            if len(self.levels[type]) > 0:
                id = max(record[0] for record in self.levels[type]) + 1
            else:
                id = 1
            record = (id, polygon_id, parent_id)
            self.levels[type].append(record)
            if parent_id not in self.childrenDict:
                self.childrenDict[parent_id] = []
            self.childrenDict[parent_id].append(polygon_id)
        # notify
        self.updatePolygonList.emit(self.polygons)

