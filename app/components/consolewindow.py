import os

from PyQt5 import uic
from PyQt5.QtCore import QProcess, Qt
from PyQt5.QtWidgets import *

from app.src import systemsupport, dialog, utils


class ConsoleWindow(QDialog):

    clickPos = None

    TitleBar: QFrame
    Content: QFrame
    Console: QPlainTextEdit

    def __init__(self, commands: list[str], working_directory = None):
        super().__init__()
        uic.loadUi(os.path.join(__file__, os.path.pardir, os.path.pardir, "design", "console_window.ui"), self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        utils.apply_shadow(self.Content,50,y=0,r=20)

        self.commands = commands
        self.curCommand = ""

        self.TitleBar.mousePressEvent = self.TitleBarClick
        self.TitleBar.mouseMoveEvent = self.TitleBarMove
        self.TitleBar.mouseReleaseEvent = self.TitleBarRelease

        self.process = QProcess()
        self.process.finished.connect(self.__finished)
        self.process.readyReadStandardOutput.connect(self.__outputReady)
        self.process.readyReadStandardError.connect(self.__errorReady)
        if working_directory is not None:
            self.process.setWorkingDirectory(working_directory)

        self.__run()

    def consoleText(self):
        return self.Console.toPlainText()

    def __run(self):
        if len(self.commands) > 0:
            self.Console.appendPlainText(f"> {self.commands[0]}\n")
            self.process.start(systemsupport.terminal_command(self.commands[0]))
            self.curCommand = self.commands.pop(0)
        else:
            self.close()

    def __outputReady(self):
        self.Console.insertPlainText(self.process.readAllStandardOutput().data().decode())

    def __errorReady(self):
        self.Console.insertPlainText(self.process.readAllStandardError().data().decode())

    def __finished(self, exitCode, exitStatus):
        if exitCode == 1:
            dialog.Warn(f'There was a problem while executing command "{self.curCommand}"!')
        self.__run()

    def TitleBarClick(self, ev):
        self.clickPos = ev.pos()

    def TitleBarMove(self, event):
        if self.clickPos is not None and event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.clickPos)

    def TitleBarRelease(self, ev):
        self.clickPos = None