#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : log.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2016-01-25
# Description   :
#


from PyQt5.QtCore import pyqtSignal, QObject


class Log(QObject):
    onLog = pyqtSignal(str)

    def __init__(self):
        super().__init__()


def debug(msg):
    msg = str(msg)
    logger.onLog.emit(msg)


def info(msg):
    msg = str(msg)
    logger.onLog.emit(msg)


def warning(msg):
    msg = str(msg)
    logger.onLog.emit(msg)


def error(msg):
    msg = str(msg)
    logger.onLog.emit(msg)


logger = Log()

