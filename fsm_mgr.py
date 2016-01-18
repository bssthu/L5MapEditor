#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : fsm_mgr.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-09-30
# Description   :
#


from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject


class FsmMgr(QObject):
    changeState = pyqtSignal(QObject)

    def __init__(self):
        super().__init__()
        self.__fsms = {
            'normal': self.FsmNormal(),
            'empty': self.FsmEmpty(),
            'insert': self.FsmInsert(),
            'move': self.FsmMove(),
            'move_point': self.FsmMovePoint()
        }
        self.state = self.__fsms['empty']

    def getCurrentState(self):
        return self.state

    def getFsm(self, name):
        return self.__fsms[name.lower()]

    def changeFsm(self, curr_name, new_name):
        if self.getFsm(curr_name) != self.state:
            return False
        new_name = new_name.lower()
        new_state = self.getFsm(new_name)
        if self.state == self.getFsm('empty'):
            if new_state == self.getFsm('normal'):  # empty => normal
                self.__setFsm(new_state)
                return True
        # normal => empty / insert / move / move_point
        elif self.state == self.getFsm('normal'):
            if new_state == self.getFsm('insert'):  # normal => insert
                self.__setFsm(new_state)
                return True
            elif new_state == self.getFsm('move'):  # normal => move
                self.__setFsm(new_state)
                return True
            elif new_state == self.getFsm('move_point'):  # normal => move_point
                self.__setFsm(new_state)
                return True
        # insert => normal
        elif self.state == self.getFsm('insert'):
            if new_state == self.getFsm('normal'):  # insert => normal
                self.__setFsm(new_state)
                return True
        # move => normal / move_point
        elif self.state == self.getFsm('move'):
            if new_state == self.getFsm('normal'):  # move => normal
                self.__setFsm(new_state)
                return True
            elif new_state == self.getFsm('move_point'):  # move => move_point
                self.__setFsm(new_state)
                return True
        # move_point => normal / move
        elif self.state == self.getFsm('move_point'):
            if new_state == self.getFsm('normal'):  # move_point => normal
                self.__setFsm(new_state)
                return True
            elif new_state == self.getFsm('move'):  # move_point => move
                self.__setFsm(new_state)
                return True
        return False

    def __setFsm(self, new_state):
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

