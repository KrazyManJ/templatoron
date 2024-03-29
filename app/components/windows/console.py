from PyQt5.QtCore import QProcess
from PyQt5.QtWidgets import *

from app.components.abstract.qframelessmodal import QFramelessModal
from app.src import systemsupport, dialog


class ConsoleWindow(QFramelessModal):
    class ContentTyping(QFramelessModal):
        Console: QPlainTextEdit

    Content: ContentTyping

    def __init__(self, commands: list[str], working_directory=None):
        super().__init__("console_window.ui")
        self.disableClosing()

        self.commands = commands
        self.curCommand = ""

        self.process = QProcess()
        self.process.finished.connect(self.__finished)  # type: ignore
        self.process.readyReadStandardOutput.connect(self.__outputReady)  # type: ignore
        self.process.readyReadStandardError.connect(self.__errorReady)  # type: ignore
        if working_directory is not None:
            self.process.setWorkingDirectory(working_directory)

    def exec(self):
        self.__run()
        super().exec()

    def closeEvent(self, event) -> None:
        if event.spontaneous():
            event.ignore()
        else:
            super().closeEvent(event)

    def consoleText(self):
        return self.Content.Console.toPlainText()

    def addText(self, text):
        self.Content.Console.appendPlainText(text)

    def __run(self):
        if len(self.commands) > 0:
            self.addText(f"> {self.commands[0]}\n")
            self.process.start(systemsupport.terminal_command(self.commands[0]))
            self.curCommand = self.commands.pop(0)
        else:
            self.close()

    def __outputReady(self):
        self.addText(self.process.readAllStandardOutput().data().decode())

    def __errorReady(self):
        self.addText(self.process.readAllStandardError().data().decode())

    def __finished(self, exitCode, exitStatus):
        if exitCode == 1:
            dialog.Warn(f'There was a problem while executing command "{self.curCommand}"!')
        self.__run()
