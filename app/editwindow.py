from PyQt5 import uic
from PyQt5.QtCore import Qt, QEventLoop
from PyQt5.QtWidgets import QApplication, QPushButton, QFileDialog
from qframelesswindow import FramelessWindow

from app.components.titlebar import TitleBar
from app.src import utils, pather, dialog, systemsupport
from app.src.templatoron import TemplatoronObject


class TemplatoronEditWindow(FramelessWindow):

    CreateTemplateProjectButton: QPushButton

    def __init__(self, template: TemplatoronObject):
        super().__init__()
        self.Template = template
        uic.loadUi(pather.design_file("edit_window.ui"), self)
        self.setTitleBar(TitleBar(self))
        self.setWindowModality(Qt.ApplicationModal)
        utils.center_widget(QApplication.instance(),self)
        self.__loop = QEventLoop()
        self.__done = True
        self.CreateTemplateProjectButton.clicked.connect(self.create_project_template)

    def exec(self) -> TemplatoronObject | None:
        self.show()
        self.__loop.exec()
        return self.Template

    def closeEvent(self, a0) -> None:
        if not self.__done:
            response = dialog.ConfirmCancel("Do you want to save all changes before closing edit window?")
            if response == dialog.CANCEL:
                a0.ignore()
                return
            if response == dialog.NO:
                self.Template = None
        self.__loop.exit()

    def create_project_template(self):
        a = QFileDialog.getExistingDirectory(self, "Select Directory", systemsupport.desktop_path())
        if a != "":
            self.Template.create_template_project(a)