from PyQt5.QtWidgets import *
class Button(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("padding: 10px;")