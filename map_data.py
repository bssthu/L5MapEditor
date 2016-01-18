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


COMMAND_UNRESOLVED = '无法解析的命令'
COMMAND_UNFINISHED = '不完整的命令'
COMMAND_GRAMMAR_ERROR = '语法错误'


class MapData(QObject):
    updatePolygonList = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.polygons = []
        self.levels = []
        self.child_dict = {}
        self.additional_dict = {}
        self.polygon_dict = {}
        self.command_tree = {
            'add': {
                'polygon': None,
                'point': None
            },
            'delete': {
                'polygon': self.executeRemovePolygon,
                'point': None
            }
        }

    def set(self, polygons, levels):
        self.polygons = polygons
        self.levels = levels
        # polygon 索引
        self.polygon_dict = {}
        for polygon in self.polygons:
            polygon_id = polygon[0]
            self.polygon_dict[polygon_id] = polygon
        # 更新信息
        self.invalidate()
        # notify
        self.updatePolygonList.emit(self.polygons)

    def get(self):
        return self.polygons, self.levels

    def execute(self, command):
        commands = command.strip().split(' ')
        self.executeInTree(self.command_tree, commands)

    def executeInTree(self, command_tree, commands):
        tree = command_tree
        if len(commands) == 0:
            raise Exception(COMMAND_UNFINISHED)
        command_name = commands[0].lower()
        if command_name in tree:
            leaf = command_tree[command_name]
            if isinstance(leaf, dict):
                self.executeInTree(leaf, commands[1:])
            elif callable(leaf):
                # call it
                leaf(*commands[1:])
            # else it's the tree's problem
        else:
            raise Exception(COMMAND_UNRESOLVED)

    def invalidate(self):
        self.child_dict = createChildDict(self.levels)
        self.additional_dict = createAdditionalDict(self.levels)

    def getChildListOfPolygon(self, polygon_id):
        # update children
        children = []
        if polygon_id in self.child_dict:
            children = [self.polygon_dict[child_id] for child_id in self.child_dict[polygon_id]]
        # get the polygon
        return children

    def getAdditionalOfPolygon(self, polygon_id):
        if polygon_id in self.additional_dict:
            return self.additional_dict[polygon_id]
        else:
            return None

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
            setParentOfChild(self.child_dict, polygon_id, parent_id)
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

    def executeRemovePolygon(self, commands):
        if len(commands) != 1:
            raise Exception(COMMAND_GRAMMAR_ERROR)
        _id = int(commands[0])
        self.__removePolygon(_id)
        self.invalidate()
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


def createChildDict(levels):   # 更新 self.child_dict
    child_dict = {}
    for level in levels[1:]:
        for record in level:
            (polygon_id, parent_id) = (record[1], record[3])
            setParentOfChild(child_dict, polygon_id, parent_id)
    return child_dict


def createAdditionalDict(levels):   # 更新 self.additional_dict
    additional_dict = {}
    for level in levels:
        for record in level:
            (polygon_id, additional) = (record[1], record[2])
            additional_dict[polygon_id] = additional
    return additional_dict


def setParentOfChild(child_dict, child_id, parent_id):
    if parent_id != child_id:
        if parent_id not in child_dict:
            child_dict[parent_id] = []
        child_dict[parent_id].append(child_id)

