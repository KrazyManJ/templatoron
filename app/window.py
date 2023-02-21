import ctypes
import os.path

from PyQt5 import uic
from qframelesswindow import FramelessWindow

from app import utils
from app.components.titlebar import TitleBar


class Window(FramelessWindow):
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        uic.loadUi(os.path.join(__file__,os.path.pardir,"design","main_window.ui"), self)
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("me.KrazyManJ.Templatoron.1.0.0")
        self.setTitleBar(TitleBar(self))
        utils.center_widget(self.app,self)