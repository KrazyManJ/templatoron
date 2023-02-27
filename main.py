import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from app.window import TemplatoronWindow
from app.assets import assets

if __name__ == '__main__':
    App = QApplication(sys.argv)
    assets.qInitResources()
    App.setWindowIcon(QIcon(":/icon/icon.svg"))
    ui = TemplatoronWindow(App)
    ui.show()
    sys.exit(App.exec())