from PyQt5.QtWidgets import QMessageBox


def Info(message: str):
    box = QMessageBox()
    box.setIcon(QMessageBox.Information)
    box.setWindowTitle("Templatoron - Success")
    box.setText(message)
    box.exec()


def Warn(message: str):
    box = QMessageBox()
    box.setIcon(QMessageBox.Critical)
    box.setWindowTitle("Templatoron - Error")
    box.setText(message)
    box.exec()

def Confirm(message):
    box = QMessageBox()
    box.setIcon(QMessageBox.Warning)
    box.setWindowTitle("Templatoron - Confirm")
    box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    box.setText(message)
    return box.exec() == QMessageBox.Ok