import sys

from PyQt5.QtWidgets import QApplication

from app.window import Window
from app.assets import assets

if __name__ == '__main__':
    App = QApplication(sys.argv)
    assets.qInitResources()
    ui = Window(App)
    ui.show()
    sys.exit(App.exec())