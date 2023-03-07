from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect, QGraphicsOpacityEffect


def shadow(widget: QWidget, alpha: float, x: float = 0, y: float = 4, r: float = 8):
    effect = QGraphicsDropShadowEffect()
    effect.setBlurRadius(r)
    effect.setYOffset(y)
    effect.setXOffset(x)
    effect.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(effect)


def opacity(widget: QWidget, value: float):
    opacity_effect = QGraphicsOpacityEffect()
    opacity_effect.setOpacity(value)
    widget.setGraphicsEffect(opacity_effect)

def clear(widget: QWidget):
    widget.setGraphicsEffect(None)