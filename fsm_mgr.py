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
        self.__fsms['insert'] = self.FsmInsert()
        self.__fsms['move'] = self.FsmMove()
        self.state = self.__fsms['normal']

    def getFsm(self, name):
        return self.__fsms[name.lower()]

    def changeFsm(self, curr_name, new_name):
        if self.getFsm(curr_name) != self.state:
            return False
        new_name = new_name.lower()
        new_state = self.getFsm(new_name)
        if self.state == self.getFsm('normal'):
            if new_state == self.getFsm('insert'):  # normal => insert
                self.__setFsm(new_state)
                self.change_state.emit(new_state)
                return True
            elif new_state == self.getFsm('move'):  # normal => move
                self.__setFsm(new_state)
                self.change_state.emit(new_state)
                return True
        elif self.state == self.getFsm('insert'):
            if new_state == self.getFsm('normal'):  # insert => normal
                self.__setFsm(new_state)
                self.change_state.emit(new_state)
                return True
        elif self.state == self.getFsm('move'):
            if new_state == self.getFsm('normal'):  # move => normal
                self.__setFsm(new_state)
                self.change_state.emit(new_state)
                return True
        return False

    def __setFsm(self, new_state):
        self.state.exit_state.emit()
        new_state.enter_state.emit()
        self.state = new_state

    class FsmNormal(QObject):
        enter_state = pyqtSignal()
        exit_state = pyqtSignal()

    class FsmInsert(QObject):
        enter_state = pyqtSignal()
        exit_state = pyqtSignal()

    class FsmMove(QObject):
        enter_state = pyqtSignal()
        exit_state = pyqtSignal()

