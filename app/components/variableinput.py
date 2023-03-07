from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QFrame, QLineEdit, QLabel, QVBoxLayout, QSizePolicy

from app.design.__constants__ import StyleConstants
from app.src import templatoron


class VariableInput(QFrame):
    def __init__(self, var_id, label, file_mask=False):
        super().__init__()
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.id = var_id

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.label = QLabel(self)
        self.label.setText(label)
        self.label.setIndent(10)
        self.main_layout.addWidget(self.label)
        self.input_frame = QFrame(self)
        self.input_frame.setStyleSheet(StyleConstants.VAR_INPUT)
        self.main_layout.addWidget(self.input_frame)
        self.input_layout = QVBoxLayout(self.input_frame)
        self.input = QLineEdit(self.input_frame)
        self.input_layout.addWidget(self.input)
        if file_mask:
            regex = QRegExp(templatoron.ILLEGAL_CHARS)
            validator = QRegExpValidator(regex)
            self.input.setValidator(validator)
            self.input.setMaxLength(255)

    def set_value(self, value):
        self.input.setText(value)

    def get_id(self):
        return self.id

    def get_value(self):
        return self.input.text()

    def is_empty(self):
        return self.input.text() == ""
