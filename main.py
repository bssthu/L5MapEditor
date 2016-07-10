#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : main.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2016-07-10
# Description   :
#


from PyQt5.QtWidgets import QApplication
from editor.main_window import MainWindow


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

