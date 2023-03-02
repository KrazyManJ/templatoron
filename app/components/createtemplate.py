import os

from PyQt5 import uic
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QFrame, QPushButton, QLineEdit

from app.components.abstract.qframelessdialog import QFramelessDialog
from app.components.templateitem import TemplateItem
from app.src import utils, templatoron, dialog


class CreateTemplate(QFramelessDialog):
    Content: QFrame
    TitleBar: QFrame
    BtnClose: QPushButton

    NameInput: QLineEdit
    CreateBtn: QPushButton

    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(__file__, os.path.pardir, os.path.pardir, "design", "create_template_window.ui"), self)
        self.setDraggable(self.TitleBar)
        self.BtnClose.clicked.connect(self.close)
        self.shadow(self.Content)
        utils.apply_shadow(self.BtnClose, 50)
        self.__val = None

        regex = QRegExp(templatoron.ILLEGAL_CHARS)
        validator = QRegExpValidator(regex)
        self.NameInput.setValidator(validator)
        self.NameInput.setMaxLength(255)

        self.CreateBtn.clicked.connect(self.process)

    def process(self):
        pth = os.path.join("templates", self.NameInput.text() + templatoron.EXT)
        if os.path.exists(pth):
            dialog.Warn("This template file already Exists!")
            return
        templatoron.TemplatoronObject().save(pth)
        self.__val = TemplateItem(pth)
        self.close()

    def exec(self) -> TemplateItem | None:
        super().exec()
        return self.__val
