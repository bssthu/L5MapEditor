#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : log.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2016-01-25
# Description   :
#


from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt


class Log(QObject):
    onLog = pyqtSignal(str, QColor)

    def __init__(self):
        super().__init__()


def debug(msg):
    msg = str(msg)
    logger.onLog.emit(msg, QColor(Qt.black))


def info(msg):
    msg = str(msg)
    logger.onLog.emit(msg, QColor(Qt.blue))


def warning(msg):
    msg = str(msg)
    logger.onLog.emit(msg, QColor(Qt.darkRed))


def error(msg):
    msg = str(msg)
    logger.onLog.emit(msg, QColor(Qt.red))


logger = Log()
