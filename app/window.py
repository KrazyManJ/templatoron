import ctypes
import os.path

from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import *
from qframelesswindow import FramelessWindow

from app import utils
from app.components.templateitem import TemplateItem
from app.components.titlebar import TitleBar


class Window(FramelessWindow):

    OutputPathButton: QPushButton
    CreateProjectBtn: QPushButton
    OutputPathInput: QLineEdit

    TemplateListView: QListWidget

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

        pths = os.path.join(__file__,os.path.pardir,os.path.pardir,"templatoron_template_files")
        for a in os.listdir(pths):
            self.TemplateListView.addItem(TemplateItem(os.path.abspath(os.path.join(pths,a))))
        self.TemplateListView.itemSelectionChanged.connect(self.handle_item_selection_changed)

    def is_something_selected(self):
        selected_items = self.TemplateListView.selectedItems()
        return selected_items is not None

    def handle_item_selection_changed(self):
        if not self.is_something_selected():
            return
        selected_item = self.TemplateListView.selectedItems()[0]
        if isinstance(selected_item, TemplateItem):
            print(selected_item.Template.variables)