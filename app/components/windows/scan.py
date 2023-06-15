from PyQt5.QtWidgets import QLineEdit, QPushButton, QCheckBox, QFileDialog

from app.components.abstract.qframelessmodal import QFramelessModal


class ScanWindow(QFramelessModal):
    class ContentTyping(QFramelessModal):
        PathInput: QLineEdit
        ScanButton: QPushButton
        IncludeFolderCheck: QCheckBox
        OpenFileDialog: QPushButton

    Content: ContentTyping

    def __init__(self):
        super().__init__("scan_window.ui")
        self.__scan = False
        self.Content.OpenFileDialog.clicked.connect(self.change_path)
        self.Content.ScanButton.setDisabled(True)
        self.Content.ScanButton.clicked.connect(self.scan)

    def scan(self):
        self.__scan = True
        self.close()

    def exec(self) -> (str | None, bool | None):
        super().exec()
        if not self.__scan:
            return None, None
        return self.Content.PathInput.text(),self.Content.IncludeFolderCheck.checkState()

    def change_path(self):
        a = QFileDialog.getExistingDirectory(self, "Select Directory")
        if a != "":
            self.Content.PathInput.setText(a)
            self.Content.ScanButton.setDisabled(False)