#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : map_data.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-09-24
# Description   :
#


import copy
from PyQt5.QtCore import QObject


COMMAND_UNRESOLVED = '无法解析的命令'
COMMAND_UNFINISHED = '不完整的命令'
COMMAND_GRAMMAR_ERROR = '语法错误'
COMMAND_ID_NOT_FOUND = 'ID不存在'


class MapData(QObject):
    def __init__(self):
        super().__init__()
        self.polygons = []
        self.layers = []
        self.old_polygons = []
        self.old_layers = []
        self.child_dict = {}
        self.additional_dict = {}
        self.polygon_dict = {}
        self.command_history = []
        self.command_history_revert = []
        self.command_tree = {
            'add': {
                'shape': self.executeAddPolygon,
                'pt': self.executeAddPoint
            },
            'del': {
                'shape': self.executeRemovePolygon,
                'pt': None
            },
            'mov': {
                'shape': self.executeMovePolygon,
                'pt': self.executeMovePoint
            },
            'set': {
                'pt': self.executeSetPoint,
                'layer': None,
                'additional': None
            }
        }

    def set(self, polygons, layers):
        self.polygons = polygons
        self.layers = layers
        self.updateBackupData()
        # 更新信息
        self.invalidate()

    def get(self):
        return self.polygons, self.layers

    def getPolygons(self):
        return self.polygons

    def invalidate(self):
        # polygon 索引
        self.polygon_dict = {}
        for polygon in self.polygons:
            polygon_id = polygon[0]
            self.polygon_dict[polygon_id] = polygon
        # 其他索引
        self.child_dict = createChildDict(self.layers)
        self.additional_dict = createAdditionalDict(self.layers)

    def updateBackupData(self):
        # 用于 撤销/重做
        self.old_polygons = copy.deepcopy(self.polygons)
        self.old_layers = copy.deepcopy(self.layers)
        self.command_history.clear()

    def revertAll(self):
        self.polygons = copy.deepcopy(self.old_polygons)
        self.layers = copy.deepcopy(self.old_layers)
        self.command_history.clear()
        self.invalidate()

    def redoCommandHistory(self):
        command_history = copy.deepcopy(self.command_history)
        self.revertAll()
        for commands in command_history:
            self.execute(commands, is_redo=True)

    def undo(self):
        if len(self.command_history) > 0:
            self.command_history_revert.append(self.command_history.pop())
            self.redoCommandHistory()

    def redo(self):
        if len(self.command_history_revert) > 0:
            self.command_history.append(self.command_history_revert.pop())
            self.redoCommandHistory()

    def execute(self, commands, is_redo=False):
        try:
            if isinstance(commands, str):
                self.executeSingleCommand(commands)
            else:
                for command in commands:
                    self.executeSingleCommand(command)
        except Exception as e:
            if not is_redo:
                self.redoCommandHistory()
            else:
                raise Exception(repr(e) + '\n尝试恢复时出错')
            raise e
        else:
            self.command_history.append(commands)
            if not is_redo:
                self.command_history_revert.clear()

    def executeSingleCommand(self, command):
        commands = command.strip().split(' ')
        self.executeInTree(self.command_tree, commands)
        # notify
        self.invalidate()

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
                leaf(*[commands[1:]])
            # else it's the tree's problem
        else:
            raise Exception(COMMAND_UNRESOLVED)

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

    def getSpareId(self, _id):
        while _id in self.polygon_dict:
            _id += 1
        return _id

    def updatePolygon(self, _id, vertices):     # 更新某个多边形的数据
        for polygon in self.polygons:
            if polygon[0] == _id:
                polygon[2] = len(vertices)
                polygon[3] = vertices
                self.polygon_dict[_id] = polygon
                break

    def executeAddPolygon(self, commands):
        if len(commands) == 3:
            (_id, layer, additional) = (int(commands[0]), int(commands[1]), commands[2])
            parent_id = None
        elif len(commands) == 4:
            (_id, layer, additional, parent_id) = (int(commands[0]), int(commands[1]), int(commands[2]), int(commands[3]))
        else:
            raise Exception(COMMAND_GRAMMAR_ERROR)
        # add
        self.__addPolygon(_id, layer, additional, parent_id)

    def executeAddPoint(self, commands):
        if len(commands) != 3:
            raise Exception(COMMAND_GRAMMAR_ERROR)
        (_id, x, y) = (int(commands[0]), float(commands[1]), float(commands[2]))
        if _id in self.polygon_dict:
            self.__appendPoint(_id, x, y)
        else:
            raise Exception(COMMAND_ID_NOT_FOUND)

    def executeRemovePolygon(self, commands):
        if len(commands) != 1:
            raise Exception(COMMAND_GRAMMAR_ERROR)
        _id = int(commands[0])
        self.__removePolygon(_id)

    def executeSetPoint(self, commands):
        if len(commands) != 4:
            raise Exception(COMMAND_GRAMMAR_ERROR)
        (_id, pt_id, x, y) = (int(commands[0]), int(commands[1]), float(commands[2]), float(commands[3]))
        self.__setPoint(_id, pt_id, x, y)

    def executeMovePolygon(self, commands):
        if len(commands) != 3:
            raise Exception(COMMAND_GRAMMAR_ERROR)
        (_id, dx, dy) = (int(commands[0]), float(commands[1]), float(commands[2]))
        if _id in self.polygon_dict:
            self.__movePolygon(_id, dx, dy)
        else:
            raise Exception(COMMAND_ID_NOT_FOUND)

    def executeMovePoint(self, commands):
        pass

    def __addPolygon(self, polygon_id, layer, additional, parent_id):
        polygon = [polygon_id, layer, 0, []]
        self.polygons.append(polygon)
        self.polygons.sort(key=lambda p: polygon[0])
        # update self.layers, set parent info
        if layer >= 0:
            if len(self.layers[layer]) > 0:
                _id = max(record[0] for record in self.layers[layer]) + 1
            else:
                _id = 1
            if layer == 0:
                record = (_id, polygon_id, additional)
            else:
                record = (_id, polygon_id, additional, parent_id)
            self.layers[layer].append(record)

    def __appendPoint(self, polygon_id, x, y):
        polygon = self.polygon_dict[polygon_id]
        vertex_num = int(polygon[2])
        polygon[2] = vertex_num + 1
        polygon[3].append([x, y])

    def __removePolygon(self, _id):
        if _id in self.polygon_dict:
            # remove children
            if _id in self.child_dict:
                for child_id in self.child_dict[_id]:
                    self.__removePolygon(child_id)
            del self.polygon_dict[_id]
            self.polygons = [polygon for polygon in self.polygons if polygon[0] != _id]
            for i in range(0, len(self.layers)):
                self.layers[i] = [layer for layer in self.layers[i] if layer[1] != _id]

    def __setPoint(self, polygon_id, pt_id, x, y):
        polygon = self.polygon_dict[polygon_id]
        point = polygon[3][pt_id]
        point[0] = x
        point[1] = y

    def __movePolygon(self, polygon_id, dx, dy):
        polygon = self.polygon_dict[polygon_id]
        for point in polygon[3]:
            point[0] += dx
            point[1] += dy


def createChildDict(layers):   # 更新 self.child_dict
    child_dict = {}
    for layer in layers[1:]:
        for record in layer:
            (polygon_id, parent_id) = (record[1], record[3])
            setParentOfChild(child_dict, polygon_id, parent_id)
    return child_dict


def createAdditionalDict(layers):   # 更新 self.additional_dict
    additional_dict = {}
    for layer in layers:
        for record in layer:
            (polygon_id, additional) = (record[1], record[2])
            additional_dict[polygon_id] = additional
    return additional_dict


def setParentOfChild(child_dict, child_id, parent_id):
    if parent_id != child_id:
        if parent_id not in child_dict:
            child_dict[parent_id] = []
        child_dict[parent_id].append(child_id)

