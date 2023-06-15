import os

from PyQt5.QtCore import QRegExp, Qt
from PyQt5.QtGui import QRegExpValidator, QCursor
from PyQt5.QtWidgets import QPushButton, QLineEdit, QLabel, QGraphicsOpacityEffect

import app.src.graphiceffects
from app.components.abstract.qframelessmodal import QFramelessModal
from app.src import templatoron, dialog


class CreateTemplate(QFramelessModal):
    class ContentTyping(QFramelessModal):
        ExtLabel: QLabel
        NameInput: QLineEdit
        CreateBtn: QPushButton

    Content: ContentTyping

    def __init__(self):
        super().__init__("create_template_window.ui")

        app.src.graphiceffects.shadow(self.BtnClose, 50)
        self.Content.ExtLabel.setText(templatoron.EXT)
        self.__val = None
        regex = QRegExp(templatoron.ILLEGAL_CHARS)
        validator = QRegExpValidator(regex)
        self.Content.NameInput.setValidator(validator)
        self.Content.NameInput.setMaxLength(255)

        self.Content.CreateBtn.clicked.connect(self.process)
        self.Content.NameInput.textChanged.connect(self.checkButton)

        self.set_create_project_button_state(False)

    def process(self):
        if len(self.Content.NameInput.text()) == 0:
            return
        pth = os.path.join("templates", self.Content.NameInput.text() + templatoron.EXT)
        if os.path.exists(pth):
            dialog.Warn("This template file already Exists!")
            return
        templatoron.TemplatoronObject().save(pth)
        self.__val = pth
        self.close()

    def checkButton(self):
        self.set_create_project_button_state(len(self.Content.NameInput.text()) > 0)

    def set_create_project_button_state(self, state: bool):
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.5)
        self.Content.CreateBtn.setGraphicsEffect(None if state else opacity_effect)
        self.Content.CreateBtn.setCursor(QCursor(Qt.PointingHandCursor if state else Qt.ForbiddenCursor))
        self.Content.CreateBtn.setToolTip(None if state else "You need to enter all parameters before creation.")

    def exec(self) -> str | None:
        super().exec()
        return self.__val

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.process()
        elif event.key() == Qt.Key_Escape:
            self.close()
