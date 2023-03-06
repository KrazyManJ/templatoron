import sys

from PyQt5.QtGui import QIcon, QFontDatabase
from PyQt5.QtWidgets import QApplication


from app.mainwindow import TemplatoronMainWindow
from app.assets import assets # type: ignore
from app.src import pather

if __name__ == '__main__':
    App = QApplication(sys.argv)
    App.setWindowIcon(QIcon(":/icon/icon.svg"))
    for font in pather.listdirfullpath(pather.FONTS_FOLDER):

        QFontDatabase.addApplicationFont(font)
    ui = TemplatoronMainWindow(App)
    ui.show()
    sys.exit(App.exec())