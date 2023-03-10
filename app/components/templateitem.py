import base64
import os.path

from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QTreeWidgetItem

from app.src.templatoron import TemplatoronObject


class TemplateItem(QTreeWidgetItem):
    Template: TemplatoronObject

    def __init__(self, path: str):
        obj = TemplatoronObject.from_file(path)
        super().__init__([obj.name])
        self.Template = obj
        self.path = path

        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(self.Template.icon))
        self.setIcon(0, QIcon(pixmap))
        self.setToolTip(0, self.Template.name)

    def remove(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def save(self):
        if os.path.exists(self.path):
            self.Template.save(self.path)
