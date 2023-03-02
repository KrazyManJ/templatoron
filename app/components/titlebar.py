import os
import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from qframelesswindow.utils import startSystemMove

from app.src import utils


class TitleBar(QWidget):

    BtnClose: QPushButton
    BtnMin: QPushButton
    BtnMax: QPushButton

    def __init__(self, parent):
        super().__init__(parent)  # type: ignore
        uic.loadUi(os.path.join(__file__, os.path.pardir, os.path.pardir, "design", "titlebar.ui"), self)

        BTN_MAP = [
            (self.BtnClose, self.window().close),
            (self.BtnMin, self.window().showMinimized),
            (self.BtnMax, self.__toggleMaxState)
        ]
        for widg, fct in BTN_MAP:
            widg.clicked.connect(fct)
            utils.apply_shadow(widg,50)
        self.__updateIcon()
        self.window().installEventFilter(self)

    def mouseDoubleClickEvent(self, event):
        if event.button() != Qt.LeftButton: return
        self.__updateIcon()
        self.__toggleMaxState()

    def mouseMoveEvent(self, e):
        if sys.platform != "win32" or not self._isDragRegion(e.pos()): return
        self.__updateIcon()
        startSystemMove(self.window(), e.globalPos())

    def mousePressEvent(self, e):
        if sys.platform == "win32" or e.button() != Qt.LeftButton or not self._isDragRegion(e.pos()): return
        self.__updateIcon()
        startSystemMove(self.window(), e.globalPos())

    def __toggleMaxState(self):
        if self.window().isMaximized():
            self.window().showNormal()
        else:
            self.window().showMaximized()
        self.__updateIcon()

    def _isDragRegion(self, pos):
        return 0 < pos.x() < self.width() - 46 * 3

    def __updateIcon(self):
        if self.window().isMaximized():
            self.BtnMax.setStyleSheet("")
        else:
            self.BtnMax.setStyleSheet("""
            #BtnMax {
                border-image: url(:/titlebar/titlebar/normalize.svg);
            }
            """)
