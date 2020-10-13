import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class Widget(QWidget):
    def __init__(self):
        super(Widget, self).__init__()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.black)
        painter.drawLine(10, 10, 100, 140)


def init():
    app = QApplication(sys.argv)
    cx = Widget()
    cx.resize(400, 280)
    cx.show()
    sys.exit(app.exec_())
