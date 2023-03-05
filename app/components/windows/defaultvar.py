import os

from PyQt5 import uic
from PyQt5.QtCore import QRegExp, Qt
from PyQt5.QtGui import QRegExpValidator, QCursor
from PyQt5.QtWidgets import QFrame, QPushButton, QLineEdit, QLabel, QGraphicsOpacityEffect

from app.components.abstract.qframelessmodal import QFramelessModal
from app.components.templateitem import TemplateItem
from app.components.variableinput import VariableInput
from app.src import utils, templatoron, dialog
from app.src.templatoron import TemplatoronObject


class DefaultVariableWindow(QFramelessModal):
    Content: QFrame
    TitleBar: QFrame
    BtnClose: QPushButton
    ExtLabel: QLabel

    VariableAreaContent: QFrame

    CreateBtn: QPushButton

    def __init__(self, template: TemplatoronObject, values: dict):
        super().__init__("default_vars_window.ui")
        self.BtnClose.clicked.connect(self.close)
        utils.apply_shadow(self.BtnClose, 50)
        for var in template.variables:
            varInput = VariableInput(var["id"], var["displayname"], template.is_var_used_in_file_system(var["id"]))
            self.VariableAreaContent.layout().addWidget(varInput)
            varInput.input.setText(values.get(var["id"], ""))
        self.CreateBtn.clicked.connect(self.process)
        self.__val = None

    def process(self):
        R = {}
        for var in self.get_variables():
            if var.get_value() != "":
                R[var.id] = var.get_value()
        self.__val = R
        self.close()

    def get_variables(self) -> list[VariableInput]:
        return [i for i in self.VariableAreaContent.children() if isinstance(i, VariableInput)]

    def exec(self) -> dict[str, str] | None:
        super().exec()
        return self.__val

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.process()
        elif event.key() == Qt.Key_Escape:
            self.close()
