import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from app.mainwindow import TemplatoronMainWindow
from app.assets import assets # type: ignore

if __name__ == '__main__':
    App = QApplication(sys.argv)
    App.setWindowIcon(QIcon(":/icon/icon.svg"))
    ui = TemplatoronMainWindow(App)
    ui.show()
    sys.exit(App.exec())