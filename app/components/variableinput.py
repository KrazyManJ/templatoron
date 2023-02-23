from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QFrame, QLineEdit, QLabel, QVBoxLayout, QSizePolicy

from typing import TYPE_CHECKING

from app.src import templatoron

if TYPE_CHECKING:
    from app.window import TemplatoronWindow


class VariableInput(QFrame):
    def __init__(self,window:"TemplatoronWindow",var_id,label,file_mask=False):
        super().__init__()
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.id = var_id

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.label = QLabel(self)
        self.label.setText(label)
        self.label.setIndent(10)
        self.main_layout.addWidget(self.label)
        self.input_frame = QFrame(self)
        self.input_frame.setStyleSheet("""
    QFrame {
        background: #141414;
        max-height: 40px;
        min-height: 40px;
        border-radius: 10px;
        border: 1px solid #555;
    }
    QLineEdit {
        background: transparent;
        border: none;
        font: 10pt "Fira Code";
        color: #ccc;
    }
                """)
        self.main_layout.addWidget(self.input_frame)
        self.input_layout = QVBoxLayout(self.input_frame)
        self.input = QLineEdit(self.input_frame)
        self.input_layout.addWidget(self.input)
        self.input.textEdited.connect(window.variableChange)
        if file_mask:
            regex = QRegExp(templatoron.ILLEGAL_CHARS)
            validator = QRegExpValidator(regex)
            self.input.setValidator(validator)

    def get_id(self):
        return self.id

    def get_value(self):
        return self.input.text()

    def is_empty(self):
        return self.input.text() == ""