import base64

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QListWidgetItem, QTreeWidgetItem, QMenu, QAction

from app.src.templatoron import TemplatoronObject


class TemplateItem(QTreeWidgetItem):

    Template: TemplatoronObject

    def __init__(self, path: str):
        obj = TemplatoronObject.from_file(path)
        super().__init__([obj.name])
        self.path = path

        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(obj.icon))
        self.setIcon(0,QIcon(pixmap))
        self.setToolTip(0,obj.name)
        self.Template = obj
