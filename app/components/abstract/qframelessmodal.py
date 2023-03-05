import os

from PyQt5 import uic
from PyQt5.QtCore import Qt, QEventLoop
from PyQt5.QtWidgets import QWidget

from app.src import utils


class QFramelessModal(QWidget):
    Content: QWidget
    TitleBar: QWidget

    clickPos = None

    def __init__(self, uiFileName: str):
        super().__init__()
        uic.loadUi(os.path.join(__file__, os.path.pardir, os.path.pardir, os.path.pardir, "design", uiFileName), self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowModality(Qt.ApplicationModal)
        utils.apply_shadow(self.Content, 50, y=0, r=20)
        self.TitleBar.mousePressEvent = self.draggableClick
        self.TitleBar.mouseMoveEvent = self.draggableMove
        self.TitleBar.mouseReleaseEvent = self.draggableRelease
        self.__loop = QEventLoop()

    def draggableClick(self, ev):
        self.clickPos = ev.pos()

    def draggableMove(self, ev):
        if self.clickPos is not None and ev.buttons() == Qt.LeftButton:
            self.move(self.pos() + ev.pos() - self.clickPos)

    def draggableRelease(self, ev):
        self.clickPos = None

    def exec(self):
        self.show()
        self.__loop.exec()

    def close(self) -> bool:
        self.__loop.exit()
        return super().close()

    def closeEvent(self, a0) -> None:
        self.__loop.exit()
