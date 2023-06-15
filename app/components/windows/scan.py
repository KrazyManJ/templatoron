from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QLineEdit, QPushButton, QCheckBox, QFileDialog

from app.components.abstract.qframelessmodal import QFramelessModal
from app.src import graphiceffects


class ScanWindow(QFramelessModal):
    class ContentTyping(QFramelessModal):
        InputPath: QLineEdit
        ScanButton: QPushButton
        IncludeFolderCheck: QCheckBox
        InputPathButton: QPushButton

    Content: ContentTyping

    def __init__(self):
        super().__init__("scan_window.ui")
        self.__scan = False
        self.__btndisabled = True
        self.Content.InputPathButton.clicked.connect(self.change_path)
        self.set_button_state(False)
        self.Content.ScanButton.clicked.connect(self.scan)

    def scan(self):
        if self.__btndisabled:
            return
        self.__scan = True
        self.close()

    def exec(self) -> (str | None, bool | None):
        super().exec()
        if not self.__scan:
            return None, None
        return self.Content.InputPath.text(),self.Content.IncludeFolderCheck.checkState()

    def change_path(self):
        a = QFileDialog.getExistingDirectory(self, "Select Directory")
        if a != "":
            self.Content.InputPath.setText(a)
            self.set_button_state(True)

    def set_button_state(self, state):
        if state:
            graphiceffects.clear(self.Content.ScanButton)
        else:
            graphiceffects.opacity(self.Content.ScanButton, 0.5)
        self.Content.ScanButton.setCursor(QCursor(Qt.ArrowCursor if state else Qt.ForbiddenCursor))
        self.__btndisabled = not state
