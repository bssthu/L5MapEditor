#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : map_command.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-09-24
# Description   :
#


import copy
from PyQt5.QtCore import QObject, pyqtSignal
from dao.db_helper import DbHelper


COMMAND_UNRESOLVED = '无法解析的命令'
COMMAND_UNFINISHED = '不完整的命令'
COMMAND_GRAMMAR_ERROR = '语法错误'
COMMAND_ID_NOT_FOUND = 'ID不存在'


class MapCommand(QObject):
    """命令管理器"""

    gotoPolygon = pyqtSignal('PyQt_PyObject')   # int, 但类型不能写 int, 转换到 c++ 后不够长

    def __init__(self, db_helper):
        """构造函数

        Args:
            db_helper (DbHelper): DbHelper
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
            },
            'goto': {
                'shape': self.execute_goto_polygon
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
        """执行命令

        Args:
            commands (str | list[str]): 命令或命令列表
            is_redo (bool): 是否是在重试，重试时出异常就不再恢复并重试
        """
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
                raise CommandNotValidException(repr(e) + '\n尝试恢复时出错')
            raise e
        else:
            self.command_history.append(commands)
            if not is_redo:
                self.command_history_revert.clear()

    def execute_single_command(self, command):
        """执行一条命令

        Args:
            command (str): 命令
        """
        commands = command.strip().split(' ')
        self.execute_tree(self.command_tree, commands)

    def execute_tree(self, command_tree, commands):
        """执行一条命令

        Args:
            command_tree (dict): 函数指针
            commands (list[str]): 分词后的命令
        """
        tree = command_tree
        if len(commands) == 0:
            raise CommandNotValidException(COMMAND_UNFINISHED)
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
            raise CommandNotValidException(COMMAND_UNRESOLVED)

    def get_spare_id(self, _id):
        """获得一个还没有被用的 id

        Args:
            _id (int): 当前 id

        Returns:
            new_id (int): 新的没有在使用的 id
        """
        while _id in self.db.polygon_table.keys():
            _id += 1
        return _id

    def execute_add_polygon(self, commands):
        """添加多边形命令

        Args:
            commands (list[str]): [_id, layer, name] 或 [_id, layer, additional, parent_id]
        """
        check_commands_length(commands, (3, 4))
        if len(commands) == 3:
            # L0 层
            (_id, layer, name) = (int(commands[0]), int(commands[1]), commands[2])
            if layer != 0:
                raise CommandNotValidException(COMMAND_GRAMMAR_ERROR)
            if _id not in self.db.polygon_table.keys():
                # 插入多边形
                self.db.add_l0_polygon(_id, name)
        elif len(commands) == 4:
            # 其他层
            (_id, layer, additional, parent_id) = \
                (int(commands[0]), int(commands[1]), int(commands[2]), int(commands[3]))
            if layer <= 0:
                raise CommandNotValidException(COMMAND_GRAMMAR_ERROR)
            if _id not in self.db.polygon_table.keys():
                # 插入边形
                self.db.add_lp_polygon(_id, layer, additional, parent_id)
        else:
            raise CommandNotValidException(COMMAND_GRAMMAR_ERROR)

    def execute_add_point(self, commands):
        """添加顶点命令

        新顶点作为多边形的最后一个顶点

        Args:
            commands (list[str]): [_id, x, y]
        """
        check_commands_length(commands, 3)
        (_id, x, y) = (int(commands[0]), float(commands[1]), float(commands[2]))
        if _id in self.db.polygon_table.keys():
            self.db.polygon_table[_id].add_vertex(x, y)
        else:
            raise CommandNotValidException(COMMAND_ID_NOT_FOUND)

    def execute_remove_polygon(self, commands):
        """删除多边形命令

        Args:
            commands (list[str]): [_id]
        """
        check_commands_length(commands, 1)
        _id = int(commands[0])
        if _id in self.db.polygon_table.keys():
            self.db.delete_by_id(_id)
        else:
            raise CommandNotValidException(COMMAND_ID_NOT_FOUND)

    def execute_set_point(self, commands):
        """修改顶点命令

        Args:
            commands (list[str]): [_id, pt_id, x, y]
        """
        check_commands_length(commands, 4)
        (_id, pt_id, x, y) = (int(commands[0]), int(commands[1]), float(commands[2]), float(commands[3]))
        if _id in self.db.polygon_table.keys():
            self.db.polygon_table[_id].set_vertex(x, y, pt_id)
        else:
            raise CommandNotValidException(COMMAND_ID_NOT_FOUND)

    def execute_move_polygon(self, commands):
        """移动多边形命令

        Args:
            commands (list[str]): [_id, dx, dy]
        """
        check_commands_length(commands, 3)
        (_id, dx, dy) = (int(commands[0]), float(commands[1]), float(commands[2]))
        if _id in self.db.polygon_table.keys():
            self.db.polygon_table[_id].move(dx, dy)
        else:
            raise CommandNotValidException(COMMAND_ID_NOT_FOUND)

    def execute_move_point(self, commands):
        """移动顶点命令

        Args:
            commands (list[str]): [_id, pt_id, dx, dy]
        """
        check_commands_length(commands, 4)
        (_id, pt_id, dx, dy) = (int(commands[0]), int(commands[1]), float(commands[2]), float(commands[3]))
        if _id in self.db.polygon_table.keys():
            self.db.polygon_table[_id].move(dx, dy, pt_id)
        else:
            raise CommandNotValidException(COMMAND_ID_NOT_FOUND)

    def execute_goto_polygon(self, commands):
        """视角跳转到多边形命令

        Args:
            commands (list[str]): [_id]
        """
        check_commands_length(commands, 1)
        _id = int(commands[0])
        self.gotoPolygon.emit(_id)


def check_commands_length(commands, expected_argc):
    """检查命令语法（参数个数）

    Args:
        commands (list[str]): 命令拆分得到的 list
        expected_argc (list[int] | tuple[int] | int): 正确的参数个数

    Raises:
        CommandNotValidException: 命令检查不通过
    """
    if isinstance(expected_argc, list) or isinstance(expected_argc, tuple):
        if len(commands) not in expected_argc:
            raise CommandNotValidException(COMMAND_GRAMMAR_ERROR)
    elif len(commands) != expected_argc:
        raise CommandNotValidException(COMMAND_GRAMMAR_ERROR)


class CommandNotValidException(Exception):
    pass
