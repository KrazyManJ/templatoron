import os

from PyQt5 import uic
from PyQt5.QtCore import QRegExp, Qt
from PyQt5.QtGui import QRegExpValidator, QCursor
from PyQt5.QtWidgets import QFrame, QPushButton, QLineEdit, QLabel, QGraphicsOpacityEffect

from app.components.abstract.qframelessdialog import QFramelessDialog
from app.components.templateitem import TemplateItem
from app.src import utils, templatoron, dialog


class CreateTemplate(QFramelessDialog):
    Content: QFrame
    TitleBar: QFrame
    BtnClose: QPushButton
    ExtLabel: QLabel

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
        self.ExtLabel.setText(templatoron.EXT)

        regex = QRegExp(templatoron.ILLEGAL_CHARS)
        validator = QRegExpValidator(regex)
        self.NameInput.setValidator(validator)
        self.NameInput.setMaxLength(255)

        self.CreateBtn.clicked.connect(self.process)
        self.NameInput.textChanged.connect(self.checkButton)

        self.set_create_project_button_state(False)

    def process(self):
        if len(self.NameInput.text()) == 0:
            return
        pth = os.path.join("templates", self.NameInput.text() + templatoron.EXT)
        if os.path.exists(pth):
            dialog.Warn("This template file already Exists!")
            return
        templatoron.TemplatoronObject().save(pth)
        self.__val = pth
        self.close()

    def checkButton(self):
        self.set_create_project_button_state(len(self.NameInput.text()) > 0)


    def set_create_project_button_state(self, state: bool):
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.5)
        self.CreateBtn.setGraphicsEffect(None if state else opacity_effect)
        self.CreateBtn.setCursor(QCursor(Qt.PointingHandCursor if state else Qt.ForbiddenCursor))
        self.CreateBtn.setToolTip(None if state else "You need to enter all parameters before creation.")

    def exec(self) -> str | None:
        super().exec()
        return self.__val
