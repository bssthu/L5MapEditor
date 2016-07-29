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
from dao.dao_polygon import DaoPolygon, DaoPoint


COMMAND_UNRESOLVED = '无法解析的命令'
COMMAND_UNFINISHED = '不完整的命令'
COMMAND_GRAMMAR_ERROR = '语法错误'
COMMAND_ID_NOT_FOUND = 'ID不存在'


class MapData(QObject):
    """命令管理器"""

    def __init__(self, polygon_table):
        """构造函数

        Args:
            polygon_table: {polygon_id: DaoPolygon}
        """
        super().__init__()
        self.polygon_dict = polygon_table
        self.old_polygons = []
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

    def invalidate(self):
        pass

    def updateBackupData(self):
        # 用于 撤销/重做
        pass
        # self.old_polygons = copy.deepcopy(self.polygons)
        # self.old_layers = copy.deepcopy(self.layers)
        self.command_history.clear()

    def revertAll(self):
        pass
        # self.polygons = copy.deepcopy(self.old_polygons)
        # self.layers = copy.deepcopy(self.old_layers)
        self.command_history.clear()
        self.invalidate()

    def redoCommandHistory(self):
        pass
        # command_history = copy.deepcopy(self.command_history)
        # self.revertAll()
        # for commands in command_history:
        #     self.execute(commands, is_redo=True)

    def undo(self):
        pass
        # if len(self.command_history) > 0:
        #     self.command_history_revert.append(self.command_history.pop())
        #     self.redoCommandHistory()

    def redo(self):
        pass
        # if len(self.command_history_revert) > 0:
        #     self.command_history.append(self.command_history_revert.pop())
        #     self.redoCommandHistory()

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

    def getSpareId(self, _id):
        while _id in self.polygon_dict.keys():
            _id += 1
        return _id

    def executeAddPolygon(self, commands):
        if len(commands) == 3:
            (_id, layer, additional) = (int(commands[0]), int(commands[1]), commands[2])
            parent_id = None
        elif len(commands) == 4:
            (_id, layer, additional, parent_id) = \
                (int(commands[0]), int(commands[1]), int(commands[2]), int(commands[3]))
        else:
            raise Exception(COMMAND_GRAMMAR_ERROR)
        # add
        self.__addPolygon(_id, layer, additional, parent_id)

    def executeAddPoint(self, commands):
        if len(commands) != 3:
            raise Exception(COMMAND_GRAMMAR_ERROR)
        (_id, x, y) = (int(commands[0]), float(commands[1]), float(commands[2]))
        if _id in self.polygon_dict.keys():
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
        polygon = DaoPolygon([polygon_id, layer, 0, ''])
        polygon.layer = layer
        polygon.additional = additional
        if parent_id is not None:
            polygon.set_parent(self.polygon_dict[parent_id])
        # 更新多边形表
        self.polygon_dict[polygon_id] = polygon

    def __appendPoint(self, polygon_id, x, y):
        polygon = self.polygon_dict[polygon_id]
        polygon.vertices.append(DaoPoint(x, y))
        polygon.vertex_num += 1

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


def setParentOfChild(child_dict, child_id, parent_id):
    if parent_id != child_id:
        if parent_id not in child_dict:
            child_dict[parent_id] = []
        child_dict[parent_id].append(child_id)

