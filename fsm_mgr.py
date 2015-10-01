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
    change_state = pyqtSignal(QObject)

    def __init__(self):
        QObject.__init__(self)
        self.__fsms = {}
        self.__fsms['normal'] = self.FsmNormal()
        self.__fsms['empty'] = self.FsmEmpty()
        self.__fsms['insert'] = self.FsmInsert()
        self.__fsms['move'] = self.FsmMove()
        self.__fsms['move_point'] = self.FsmMovePoint()
        self.state = self.__fsms['empty']

    def getCurrentState(self):
        return self.state

    def getFsm(self, name):
        return self.__fsms[name.lower()]

    def changeFsm(self, currName, newName):
        if self.getFsm(currName) != self.state:
            return False
        newName = newName.lower()
        newState = self.getFsm(newName)
        if self.state == self.getFsm('empty'):
            if newState == self.getFsm('normal'):  # empty => normal
                self.__setFsm(newState)
                return True
        # normal => empty / insert / move / move_point
        elif self.state == self.getFsm('normal'):
            if newState == self.getFsm('insert'):  # normal => insert
                self.__setFsm(newState)
                return True
            elif newState == self.getFsm('move'):  # normal => move
                self.__setFsm(newState)
                return True
            elif newState == self.getFsm('move_point'):  # normal => move_point
                self.__setFsm(newState)
                return True
        # insert => normal
        elif self.state == self.getFsm('insert'):
            if newState == self.getFsm('normal'):  # insert => normal
                self.__setFsm(newState)
                return True
        # move => normal / move_point
        elif self.state == self.getFsm('move'):
            if newState == self.getFsm('normal'):  # move => normal
                self.__setFsm(newState)
                return True
            elif newState == self.getFsm('move_point'):  # move => move_point
                self.__setFsm(newState)
                return True
        # move_point => normal / move
        elif self.state == self.getFsm('move_point'):
            if newState == self.getFsm('normal'):  # move_point => normal
                self.__setFsm(newState)
                return True
            elif newState == self.getFsm('move'):  # move_point => move
                self.__setFsm(newState)
                return True
        return False

    def __setFsm(self, newState):
        self.state.exitState.emit()
        newState.enterState.emit()
        self.state = newState
        self.change_state.emit(newState)

    class BaseFsm(QObject):
        enterState = pyqtSignal()
        exitState = pyqtSignal()

    class FsmEmpty(BaseFsm):
        pass

    class FsmNormal(BaseFsm):
        pass

    class FsmInsert(BaseFsm):
        pass

    class FsmMove(BaseFsm):
        pass

    class FsmMovePoint(BaseFsm):
        pass

