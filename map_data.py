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
    updateChildList = pyqtSignal(list)
    updatePointLis = pyqtSignal(list)

    def __init__(self):
        super().__init__()

    def set(self, polygons, levels):
        self.polygons = polygons
        self.levels = levels
        # polygon 索引
        self.polygonsDict = {}
        for polygon in self.polygons:
            polygon_id = polygon[0]
            self.polygonsDict[polygon_id] = polygon
        # 把 child 单独整理出来
        self.__listChildren()
        # notify
        self.updatePolygonList.emit(self.polygons)

    def __listChildren(self):   # 更新 self.childDict
        self.childDict = {}
        for level in self.levels[1:]:
            for record in level:
                polygon_id = record[1]
                parent_id = record[3]
                self.__addChild(parent_id, polygon_id)

    def __addChild(self, parent_id, child_id):
        if parent_id != child_id:
            if parent_id not in self.childDict:
                self.childDict[parent_id] = []
            self.childDict[parent_id].append(child_id)

    def get(self):
        return (self.polygons, self.levels)

    def selectPolygon(self, polygon_id):
        # update children
        children = []
        if polygon_id in self.childDict:
            children = [self.polygonsDict[child_id] for child_id in self.childDict[polygon_id]]
        self.updateChildList.emit(children)
        # get the polygon
        if polygon_id in self.polygonsDict:
            return self.polygonsDict[polygon_id]
        else:
            return None

    def getPolygon(self, polygon_id):
        # get the polygon
        if polygon_id in self.polygonsDict:
            return self.polygonsDict[polygon_id]
        else:
            return None

    def addPolygon(self, parent_id, layer, verticesNum, vertices):
        polygon_id = parent_id
        while polygon_id in self.polygonsDict:
            polygon_id += 1
        # add polygon
        polygon = [polygon_id, layer, verticesNum, vertices]
        self.polygons.append(polygon)
        self.polygons.sort(key=lambda polygon: polygon[0])
        self.polygonsDict[polygon_id] = polygon
        # set parent
        if layer > 0:
            if len(self.levels[layer]) > 0:
                id = max(record[0] for record in self.levels[layer]) + 1
            else:
                id = 1
            record = (id, polygon_id, 0, parent_id)
            self.levels[layer].append(record)
            self.__addChild(parent_id, polygon_id)
        # notify
        self.updatePolygonList.emit(self.polygons)

    def updatePolygon(self, id, verticesNum, vertices):     # 更新某个多边形的数据
        for i in range(0, len(self.polygons)):
            if self.polygons[i][0] == id:
                self.polygons[i][2] = verticesNum
                self.polygons[i][3] = vertices
                self.polygonsDict[id] = self.polygons[i]
                break
        # notify
        self.updatePolygonList.emit(self.polygons)

    def removePolygon(self, id):
        self.__removePolygon(id)
        self.__listChildren()
        # notify
        self.updatePolygonList.emit(self.polygons)

    def __removePolygon(self, id):
        if id in self.polygonsDict:
            # remove children
            if id in self.childDict:
                for child_id in self.childDict[id]:
                    self.__removePolygon(child_id)
            del self.polygonsDict[id]
            self.polygons = [polygon for polygon in self.polygons if polygon[0] != id]
            for i in range(0, len(self.levels)):
                self.levels[i] = [level for level in self.levels[i] if level[1] != id]

