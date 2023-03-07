import os

from PyQt5 import uic
from PyQt5.QtCore import Qt, QEventLoop
from PyQt5.QtWidgets import QApplication
from qframelesswindow import FramelessWindow

from app.components.titlebar import TitleBar
from app.src import utils, pather
from app.src.templatoron import TemplatoronObject


class TemplatoronEditWindow(FramelessWindow):
    
    def __init__(self, template: TemplatoronObject):
        super().__init__()
        self.Template = template
        uic.loadUi(pather.design_file("edit_window.ui"), self)
        self.setTitleBar(TitleBar(self))
        self.setWindowModality(Qt.ApplicationModal)
        utils.center_widget(QApplication.instance(),self)
        self.__loop = QEventLoop()

    def exec(self):
        self.show()
        self.__loop.exec()
        return self.Template

    def closeEvent(self, a0) -> None:
        self.__loop.exit()

