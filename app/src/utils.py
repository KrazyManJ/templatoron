import base64

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QWidget, QMessageBox


def apply_shadow(widget: QWidget, alpha: float, x: float = 0, y: float = 4, r: float = 8):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(r)
    shadow.setYOffset(y)
    shadow.setXOffset(x)
    shadow.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(shadow)


def center_widget(app, widget):
    frameGm = widget.frameGeometry()
    frameGm.moveCenter(app.desktop().screenGeometry(app.desktop().screenNumber(app.desktop().cursor().pos())).center())
    widget.move(frameGm.topLeft())


def image_to_base_bytes(path: str):
    """
    Used to create icons for templatoron files
    """
    with open(path, "rb") as f:
        image_bytes = f.read()
    return base64.b64encode(image_bytes).decode()
