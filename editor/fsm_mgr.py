#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : fsm_mgr.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-09-30
# Description   : UI 状态转移
#


from PyQt5.QtCore import pyqtSignal, QObject


# 可能的 state 转移路线, key 为原 state, value 为可能的目标 state 集合
possible_state_transfer = {
    'empty': ['normal'],
    'normal': ['empty', 'insert', 'move', 'move_point'],
    'insert': ['normal'],
    'move': ['normal', 'move_point'],
    'move_point': ['normal', 'move']
}


class FsmMgr(QObject):
    changeState = pyqtSignal(QObject)

    def __init__(self):
        super().__init__()
        self.__fsm_map = {
            'normal': self.FsmNormal(),
            'empty': self.FsmEmpty(),
            'insert': self.FsmInsert(),
            'move': self.FsmMove(),
            'move_point': self.FsmMovePoint()
        }
        self.state = self.__fsm_map['empty']

    def get_current_state(self):
        return self.state

    def get_fsm(self, name):
        return self.__fsm_map[name.lower()]

    def change_fsm(self, curr_name, new_name):
        """如果可以，转移状态

        Args:
            curr_name: 当前 state 名称
            new_name: 请求转移到的 state 名称
        """
        if self.get_fsm(curr_name) != self.state:
            return False
        new_name = new_name.lower()
        if new_name in possible_state_transfer[curr_name]:
            new_state = self.get_fsm(new_name)
            self.__set_fsm(new_state)
            return True
        return False

    def __set_fsm(self, new_state):
        self.state.exitState.emit()
        new_state.enterState.emit()
        self.state.transferToState.emit(str(new_state))
        self.state = new_state
        self.changeState.emit(new_state)

    class BaseFsm(QObject):
        enterState = pyqtSignal()
        exitState = pyqtSignal()
        transferToState = pyqtSignal(str)

    class FsmEmpty(BaseFsm):
        def __str__(self):
            return 'empty'

    class FsmNormal(BaseFsm):
        def __str__(self):
            return 'normal'

    class FsmInsert(BaseFsm):
        def __str__(self):
            return 'insert'

    class FsmMove(BaseFsm):
        def __str__(self):
            return 'move'

    class FsmMovePoint(BaseFsm):
        def __str__(self):
            return 'move_point'
