import ctypes
import os.path

import pyvscode
from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import *
from qframelesswindow import FramelessWindow

from app import utils
from app.components.titlebar import TitleBar


class Window(FramelessWindow):

    OutputPathButton: QPushButton
    CreateProjectBtn: QPushButton
    OutputPathInput: QLineEdit

    def change_path(self):
        a = QFileDialog.getExistingDirectory(self, "Select Directory", self.OutputPathInput.text())
        if a != "":
            self.OutputPathInput.setText(os.path.abspath(a))

    def create_project(self):
        #implement
        pass

    def __init__(self, app):
        super().__init__()
        self.app = app
        uic.loadUi(os.path.join(__file__,os.path.pardir,"design","main_window.ui"), self)
        for font in ["inter.ttf","firacode.ttf"]:
            QtGui.QFontDatabase.addApplicationFont(os.path.join(__file__,os.path.pardir,"fonts",font))
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("me.KrazyManJ.Templatoron.1.0.0")
        self.setTitleBar(TitleBar(self))
        self.OutputPathButton.clicked.connect(self.change_path)
        self.CreateProjectBtn.clicked.connect(self.create_project)
        utils.center_widget(self.app,self)
        self.OutputPathInput.setText(os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop'))