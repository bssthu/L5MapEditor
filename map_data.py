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
        super().__init__()
        self.polygons = []
        self.levels = []
        self.child_dict = {}
        self.polygon_dict = {}

    def set(self, polygons, levels):
        self.polygons = polygons
        self.levels = levels
        # polygon 索引
        self.polygon_dict = {}
        for polygon in self.polygons:
            polygon_id = polygon[0]
            self.polygon_dict[polygon_id] = polygon
        # 把 child 单独整理出来
        self.__updateChildDict()
        # notify
        self.updatePolygonList.emit(self.polygons)

    def get(self):
        return self.polygons, self.levels

    def __updateChildDict(self):   # 更新 self.childDict
        self.child_dict = {}
        for level in self.levels[1:]:
            for record in level:
                polygon_id = record[1]
                parent_id = record[3]
                self.__addChild(parent_id, polygon_id)

    def __addChild(self, parent_id, child_id):
        if parent_id != child_id:
            if parent_id not in self.child_dict:
                self.child_dict[parent_id] = []
            self.child_dict[parent_id].append(child_id)

    def getPolygonChildList(self, polygon_id):
        # update children
        children = []
        if polygon_id in self.child_dict:
            children = [self.polygon_dict[child_id] for child_id in self.child_dict[polygon_id]]
        # get the polygon
        return children

    def getPolygon(self, polygon_id):
        # get the polygon
        if polygon_id in self.polygon_dict:
            return self.polygon_dict[polygon_id]
        else:
            return None

    def addPolygon(self, parent_id, layer, vertices_num, vertices):
        polygon_id = parent_id
        while polygon_id in self.polygon_dict:
            polygon_id += 1
        # add polygon
        polygon = [polygon_id, layer, vertices_num, vertices]
        self.polygons.append(polygon)
        self.polygons.sort(key=lambda p: polygon[0])
        self.polygon_dict[polygon_id] = polygon
        # set parent
        if layer > 0:
            if len(self.levels[layer]) > 0:
                _id = max(record[0] for record in self.levels[layer]) + 1
            else:
                _id = 1
            record = (_id, polygon_id, 0, parent_id)
            self.levels[layer].append(record)
            self.__addChild(parent_id, polygon_id)
        # notify
        self.updatePolygonList.emit(self.polygons)

    def updatePolygon(self, _id, vertices_num, vertices):     # 更新某个多边形的数据
        for polygon in self.polygons:
            if polygon[0] == _id:
                polygon[2] = vertices_num
                polygon[3] = vertices
                self.polygon_dict[_id] = polygon
                break
        # notify
        self.updatePolygonList.emit(self.polygons)

    def removePolygon(self, _id):
        self.__removePolygon(_id)
        self.__updateChildDict()
        # notify
        self.updatePolygonList.emit(self.polygons)

    def __removePolygon(self, _id):
        if _id in self.polygon_dict:
            # remove children
            if _id in self.child_dict:
                for child_id in self.child_dict[_id]:
                    self.__removePolygon(child_id)
            del self.polygon_dict[_id]
            self.polygons = [polygon for polygon in self.polygons if polygon[0] != _id]
            for i in range(0, len(self.levels)):
                self.levels[i] = [level for level in self.levels[i] if level[1] != _id]

