from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QWidget

from app.src import utils


class QFramelessDialog(QDialog):

    clickPos = None

    def __init__(self):
        super().__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        #utils.apply_shadow(contentWidget, 50, y=0, r=20)

    def setDraggable(self, widget: QWidget):
        widget.mousePressEvent = self.draggableClick
        widget.mouseMoveEvent = self.draggableMove
        widget.mouseReleaseEvent = self.draggableRelease

    def shadow(self, contentWidget):
        utils.apply_shadow(contentWidget, 50, y=0, r=20)

    def draggableClick(self, ev):
        self.clickPos = ev.pos()

    def draggableMove(self, ev):
        if self.clickPos is not None and ev.buttons() == Qt.LeftButton:
            self.move(self.pos() + ev.pos() - self.clickPos)

    def draggableRelease(self, ev):
        self.clickPos = None
        