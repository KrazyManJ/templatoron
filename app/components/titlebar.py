import os
import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from qframelesswindow.utils import startSystemMove

class TitleBar(QWidget):

    BtnClose: QPushButton

    def __init__(self, parent):
        super().__init__(parent)  # type: ignore
        uic.loadUi(os.path.join(__file__, os.path.pardir, os.path.pardir, "design", "titlebar.ui"), self)

        BTN_MAP = [
            (self.BtnClose, self.window().close),
           # (self.BtnMin, self.window().showMinimized),
           # (self.BtnMax, self.__toggleMaxState)
        ]
        for widg, fct in BTN_MAP:
            widg.clicked.connect(fct)

        self.window().installEventFilter(self)

    def mouseDoubleClickEvent(self, event):
        if event.button() != Qt.LeftButton: return
        self.__toggleMaxState()

    def mouseMoveEvent(self, e):
        if sys.platform != "win32" or not self._isDragRegion(e.pos()): return
        startSystemMove(self.window(), e.globalPos())

    def mousePressEvent(self, e):
        if sys.platform == "win32" or e.button() != Qt.LeftButton or not self._isDragRegion(e.pos()): return
        startSystemMove(self.window(), e.globalPos())

    def __toggleMaxState(self):
        if self.window().isMaximized():
            self.window().showNormal()
        else:
            self.window().showMaximized()

    def _isDragRegion(self, pos):
        return 0 < pos.x() < self.width() - 46 * 3