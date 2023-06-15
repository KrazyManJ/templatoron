import traceback

from PyQt5 import uic
from PyQt5.QtCore import Qt, QEventLoop
from PyQt5.QtWidgets import QApplication, QPushButton, QFileDialog, QLineEdit
from qframelesswindow import FramelessWindow

from app.components.titlebar import TitleBar
from app.components.windows.scan import ScanWindow
from app.src import utils, pather, dialog, systemsupport
from app.src.templatoron import TemplatoronObject


class TemplatoronEditWindow(FramelessWindow):

    CreateTemplateProjectButton: QPushButton
    ScanFolderButton: QPushButton
    TemplateNameEdit: QLineEdit
    SetIconButton: QPushButton

    def __init__(self, template: TemplatoronObject):
        super().__init__()
        self.Template = template.copy()
        uic.loadUi(pather.design_file("edit_window.ui"), self)
        self.setTitleBar(TitleBar(self))
        self.setWindowModality(Qt.ApplicationModal)
        utils.center_widget(QApplication.instance(),self)
        self.__loop = QEventLoop()
        self.__done = True
        self.TemplateNameEdit.setText(self.Template.name)
        self.TemplateNameEdit.textEdited.connect(self.editName)
        self.CreateTemplateProjectButton.clicked.connect(self.create_project_template)
        self.ScanFolderButton.clicked.connect(self.scan_folder)
        self.SetIconButton.clicked.connect(self.set_icon)

    def exec(self) -> TemplatoronObject | None:
        self.show()
        self.__loop.exec()
        return self.Template

    def editName(self):
        self.Template.name = self.TemplateNameEdit.text()
        self.__done = False

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

    def scan_folder(self):
        srcpath, include_folder = ScanWindow().exec()
        if srcpath is not None:
            self.Template.scan(srcpath, include_folder)
            self.__done = False

    def set_icon(self):
        pth,icoType = QFileDialog.getOpenFileName(self,"Select Icon","","Image (*.png)")
        if pth != "":
            try:
                self.Template.icon = utils.image_to_base_bytes(pth)
            except Exception as e:
                traceback.print_exc()