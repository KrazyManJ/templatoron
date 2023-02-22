import base64

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon, QCursor
from PyQt5.QtWidgets import QListWidgetItem

from templatoron import TemplatoronObject


class TemplateItem(QListWidgetItem):

    Template: TemplatoronObject

    def __init__(self, path):
        obj = TemplatoronObject.from_file(path)
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(obj.icon))
        super().__init__(QIcon(pixmap),obj.name)
        self.Template = obj
