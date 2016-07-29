#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : map_command.py
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


class MapCommand(QObject):
    """命令管理器"""

    def __init__(self, db_helper):
        """构造函数

        Args:
            db_helper: DbHelper
        """
        super().__init__()
        self.db_helper = db_helper
        self.polygon_dict = db_helper.polygon_table
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
        checkCommandsLength(commands, (3, 4))
        if len(commands) == 3:
            # L0 层
            (_id, layer, name) = (int(commands[0]), int(commands[1]), commands[2])
            if layer != 0:
                raise Exception(COMMAND_GRAMMAR_ERROR)
            if _id not in self.polygon_dict.keys():
                # 插入多边形
                self.db_helper.add_l0_polygon(_id, name)
        elif len(commands) == 4:
            # 其他层
            (_id, layer, additional, parent_id) = \
                (int(commands[0]), int(commands[1]), int(commands[2]), int(commands[3]))
            if layer <= 0:
                raise Exception(COMMAND_GRAMMAR_ERROR)
            if _id not in self.polygon_dict.keys():
                # 插入边形
                self.db_helper.add_lp_polygon(_id, layer, additional, parent_id)
        else:
            raise Exception(COMMAND_GRAMMAR_ERROR)

    def executeAddPoint(self, commands):
        checkCommandsLength(commands, 3)
        (_id, x, y) = (int(commands[0]), float(commands[1]), float(commands[2]))
        if _id in self.polygon_dict.keys():
            self.polygon_dict[_id].add_vertex(x, y)
        else:
            raise Exception(COMMAND_ID_NOT_FOUND)

    def executeRemovePolygon(self, commands):
        checkCommandsLength(commands, 1)
        _id = int(commands[0])
        if _id in self.polygon_dict.keys():
            self.db_helper.delete_by_id(_id)
        else:
            raise Exception(COMMAND_ID_NOT_FOUND)

    def executeSetPoint(self, commands):
        checkCommandsLength(commands, 4)
        (_id, pt_id, x, y) = (int(commands[0]), int(commands[1]), float(commands[2]), float(commands[3]))
        if _id in self.polygon_dict.keys():
            self.polygon_dict[_id].set_vertex(x, y, pt_id)
        else:
            raise Exception(COMMAND_ID_NOT_FOUND)

    def executeMovePolygon(self, commands):
        checkCommandsLength(commands, 3)
        (_id, dx, dy) = (int(commands[0]), float(commands[1]), float(commands[2]))
        if _id in self.polygon_dict.keys():
            self.polygon_dict[_id].move(dx, dy)
        else:
            raise Exception(COMMAND_ID_NOT_FOUND)

    def executeMovePoint(self, commands):
        checkCommandsLength(commands, 3)
        (_id, pt_id, dx, dy) = (int(commands[0]), int(commands[1]), float(commands[2]), float(commands[3]))
        if _id in self.polygon_dict.keys():
            self.polygon_dict[_id].move(dx, dy, pt_id)
        else:
            raise Exception(COMMAND_ID_NOT_FOUND)

    def __addPolygon(self, polygon_id, layer, additional, parent_id):
        polygon = DaoPolygon([polygon_id, layer, 0, ''])
        polygon.layer = layer
        polygon.additional = additional
        if parent_id is not None:
            polygon.set_parent(self.polygon_dict[parent_id])
        # 更新多边形表
        self.polygon_dict[polygon_id] = polygon


def checkCommandsLength(commands, expected_argc):
    """检查命令语法（参数个数）

    Args:
        commands: 命令拆分得到的 list
        expected_argc: 正确的参数个数
    """
    if isinstance(expected_argc, list) or isinstance(expected_argc, tuple):
        if len(commands) not in expected_argc:
            raise Exception(COMMAND_GRAMMAR_ERROR)
    elif len(commands) != expected_argc:
        raise Exception(COMMAND_GRAMMAR_ERROR)


def setParentOfChild(child_dict, child_id, parent_id):
    if parent_id != child_id:
        if parent_id not in child_dict:
            child_dict[parent_id] = []
        child_dict[parent_id].append(child_id)

