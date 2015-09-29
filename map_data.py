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

    def __listChildren(self):
        self.childrenDict = {}
        for level in self.levels[1:]:
            for record in level:
                polygon_id = record[1]
                parent_id = record[2]
                self.__addChild(parent_id, polygon_id)

    def __addChild(self, parent_id, child_id):
        if parent_id != child_id:
            if parent_id not in self.childrenDict:
                self.childrenDict[parent_id] = []
            self.childrenDict[parent_id].append(child_id)

    def get(self):
        return (self.polygons, self.levels)

    def selectPolygon(self, polygon_id):
        # update children
        children = []
        if polygon_id in self.childrenDict:
            children = [self.polygonsDict[child_id] for child_id in self.childrenDict[polygon_id]]
        self.updateChildrenList.emit(children)
        # get the polygon
        if polygon_id in self.polygonsDict:
            return self.polygonsDict[polygon_id]
        else:
            return None

    def addPolygon(self, parent_id, type, verticesNum, vertices):
        polygon_id = parent_id
        while polygon_id in self.polygonsDict:
            polygon_id += 1
        # add polygon
        polygon = [polygon_id, type, verticesNum, vertices]
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
            self.__addChild(parent_id, polygon_id)
        # notify
        self.updatePolygonList.emit(self.polygons)

    def updatePolygon(self, id, verticesNum, vertices):
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
            if id in self.childrenDict:
                for child_id in self.childrenDict[id]:
                    self.__removePolygon(child_id)
            del self.polygonsDict[id]
            self.polygons = [polygon for polygon in self.polygons if polygon[0] != id]
            for i in range(0, len(self.levels)):
                self.levels[i] = [level for level in self.levels[i] if level[1] != id]

