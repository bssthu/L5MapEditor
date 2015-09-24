#! D:/Python33/ python
# -*- coding: utf-8 -*-
# Module        : mainWindow.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2015-09-24
# Description   :
#


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtWidgets import QFileDialog, QInputDialog
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from ui_Form import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self, parent = None):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.graphicsView.setScene(QGraphicsScene())

# slots
    @pyqtSlot()
    def on_openAction_triggered(self):
        path = QFileDialog.getOpenFileName(self, '载入数据', '.',
                '数据库文档(*.sqlite)')[0];
        if path:
            print(path)

    @pyqtSlot()
    def on_saveAction_triggered(self):
        path = QFileDialog.getSaveFileName(self, '保存数据', '.',
                '数据库文档(*.sqlite)')[0];
        if path:
            self.skiplist.save(path)

    @pyqtSlot()
    def on_insertAction_triggered(self):
        pass

    @pyqtSlot()
    def on_deleteAction_triggered(self):
        pass

    @pyqtSlot()
    def on_aboutAction_triggered(self):
        info = 'L5MapEditor by bssthu\n\n'   \
                'https://github.com/bssthu/L5MapEditor'
        QMessageBox.about(self, '关于', info);

    @pyqtSlot()
    def on_exitAction_triggered(self):
        exit()

    def lockUI(self):
        self.ui.toolBar.setEnabled(False)

    @pyqtSlot()
    def unlockUI(self):
        self.ui.toolBar.setEnabled(True)
        self.ui.graphicsView.scene().update()


if __name__ == '__main__':
    import sys
    #QApplication.addLibraryPath('./plugins')
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

