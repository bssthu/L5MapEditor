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
        self.db = db_helper
        self.old_polygon_table = {}
        self.command_history = []
        self.command_history_revert = []
        self.command_tree = {
            'add': {
                'shape': self.execute_add_polygon,
                'pt': self.execute_add_point
            },
            'del': {
                'shape': self.execute_remove_polygon,
                'pt': None
            },
            'mov': {
                'shape': self.execute_move_polygon,
                'pt': self.execute_move_point
            },
            'set': {
                'pt': self.execute_set_point,
                'layer': None,
                'additional': None
            }
        }
        self.reset_backup_data()

    def invalidate(self):
        pass

    def reset_backup_data(self):
        """备份当前数据，用于 撤销/重做"""
        self.old_polygon_table = copy.deepcopy(self.db.polygon_table)
        self.command_history.clear()

    def revert_all(self):
        """还原到备份的数据，清空命令列表"""
        self.db.polygon_table = copy.deepcopy(self.old_polygon_table)
        self.command_history.clear()

    def redo_command_history(self):
        """按照 command_history 中的命令还原数据

        用于命令执行失败后的恢复。
        """
        command_history = copy.deepcopy(self.command_history)
        self.revert_all()
        for commands in command_history:
            self.execute(commands, is_redo=True)

    def undo(self):
        if len(self.command_history) > 0:
            self.command_history_revert.append(self.command_history.pop())
            self.redo_command_history()

    def redo(self):
        if len(self.command_history_revert) > 0:
            self.command_history.append(self.command_history_revert.pop())
            self.redo_command_history()

    def execute(self, commands, is_redo=False):
        try:
            if isinstance(commands, str):
                self.execute_single_command(commands)
            else:
                for command in commands:
                    self.execute_single_command(command)
        except Exception as e:
            if not is_redo:
                self.redo_command_history()
            else:
                raise Exception(repr(e) + '\n尝试恢复时出错')
            raise e
        else:
            self.command_history.append(commands)
            if not is_redo:
                self.command_history_revert.clear()

    def execute_single_command(self, command):
        commands = command.strip().split(' ')
        self.execute_tree(self.command_tree, commands)

    def execute_tree(self, command_tree, commands):
        tree = command_tree
        if len(commands) == 0:
            raise Exception(COMMAND_UNFINISHED)
        command_name = commands[0].lower()
        if command_name in tree:
            leaf = command_tree[command_name]
            if isinstance(leaf, dict):
                self.execute_tree(leaf, commands[1:])
            elif callable(leaf):
                # call it
                leaf(*[commands[1:]])
            # else it's the tree's problem
        else:
            raise Exception(COMMAND_UNRESOLVED)

    def get_spare_id(self, _id):
        while _id in self.db.polygon_table.keys():
            _id += 1
        return _id

    def execute_add_polygon(self, commands):
        check_commands_length(commands, (3, 4))
        if len(commands) == 3:
            # L0 层
            (_id, layer, name) = (int(commands[0]), int(commands[1]), commands[2])
            if layer != 0:
                raise Exception(COMMAND_GRAMMAR_ERROR)
            if _id not in self.db.polygon_table.keys():
                # 插入多边形
                self.db.add_l0_polygon(_id, name)
        elif len(commands) == 4:
            # 其他层
            (_id, layer, additional, parent_id) = \
                (int(commands[0]), int(commands[1]), int(commands[2]), int(commands[3]))
            if layer <= 0:
                raise Exception(COMMAND_GRAMMAR_ERROR)
            if _id not in self.db.polygon_table.keys():
                # 插入边形
                self.db.add_lp_polygon(_id, layer, additional, parent_id)
        else:
            raise Exception(COMMAND_GRAMMAR_ERROR)

    def execute_add_point(self, commands):
        check_commands_length(commands, 3)
        (_id, x, y) = (int(commands[0]), float(commands[1]), float(commands[2]))
        if _id in self.db.polygon_table.keys():
            self.db.polygon_table[_id].add_vertex(x, y)
        else:
            raise Exception(COMMAND_ID_NOT_FOUND)

    def execute_remove_polygon(self, commands):
        check_commands_length(commands, 1)
        _id = int(commands[0])
        if _id in self.db.polygon_table.keys():
            self.db.delete_by_id(_id)
        else:
            raise Exception(COMMAND_ID_NOT_FOUND)

    def execute_set_point(self, commands):
        check_commands_length(commands, 4)
        (_id, pt_id, x, y) = (int(commands[0]), int(commands[1]), float(commands[2]), float(commands[3]))
        if _id in self.db.polygon_table.keys():
            self.db.polygon_table[_id].set_vertex(x, y, pt_id)
        else:
            raise Exception(COMMAND_ID_NOT_FOUND)

    def execute_move_polygon(self, commands):
        check_commands_length(commands, 3)
        (_id, dx, dy) = (int(commands[0]), float(commands[1]), float(commands[2]))
        if _id in self.db.polygon_table.keys():
            self.db.polygon_table[_id].move(dx, dy)
        else:
            raise Exception(COMMAND_ID_NOT_FOUND)

    def execute_move_point(self, commands):
        check_commands_length(commands, 3)
        (_id, pt_id, dx, dy) = (int(commands[0]), int(commands[1]), float(commands[2]), float(commands[3]))
        if _id in self.db.polygon_table.keys():
            self.db.polygon_table[_id].move(dx, dy, pt_id)
        else:
            raise Exception(COMMAND_ID_NOT_FOUND)

    def __add_polygon(self, polygon_id, layer, additional, parent_id):
        polygon = DaoPolygon([polygon_id, layer, 0, ''])
        polygon.layer = layer
        polygon.additional = additional
        if parent_id is not None:
            polygon.set_parent(self.db.polygon_table[parent_id])
        # 更新多边形表
        self.db.polygon_table[polygon_id] = polygon


def check_commands_length(commands, expected_argc):
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


def set_parent_of_child(child_dict, child_id, parent_id):
    if parent_id != child_id:
        if parent_id not in child_dict:
            child_dict[parent_id] = []
        child_dict[parent_id].append(child_id)
