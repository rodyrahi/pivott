from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *





class MainButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("padding: 20px 40px; font-size:15px")

class Button(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("padding: 10px;")
        self.setFixedWidth(150)


class aiButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                color: #FFFFFF;
                background-color: #4CAF50;
                border: none;
                border-radius: 5px;

            }
            QPushButton:hover {
                background-color: #45a049;
            }

        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(50)


class stepButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("padding: 10px; border-radius: 0px; border: 2px solid White;")
        self.setFixedWidth(150)

class smallButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("padding: 5px; font-size:12px")
        self.setFixedWidth(100)

class CollapsibleButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background-color: None;
                color: white;
                border: 2px solid #6572a3;
                border-radius: 0px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #161717;
            }
            QPushButton:pressed {
                background-color: #000000;
            }
        """)

        # self.setFixedWidth(200)
       
        self.setCheckable(True)
        self.toggled.connect(self.toggle_collapse)
        self.collapsed = False
        self.indicator = QLabel(self)
        self.indicator.setFixedSize(20, 20)
        self.indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_indicator()

    def toggle_collapse(self, checked):
        self.collapsed = checked
        if self.collapsed:
            self.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background-color: None;
                color: white;
                border: 2px solid #6572a3;
                border-radius: 0px;
                text-align: left;
            }
            """)
        else:
            self.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background-color: None;
                color: white;
                border: 2px solid #6572a3;
                border-radius: 0px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #161717;
            }
            QPushButton:pressed {
                background-color: #000000;
            }
        """)
            # self.setFixedHeight(self.sizeHint().height())
        self.update_indicator()

    def update_indicator(self):
        if self.collapsed:
            self.indicator.setText("▲")
        else:
            self.indicator.setText("▼")
        self.indicator.move(self.width() - 25, (self.height() - self.indicator.height()) // 2)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_indicator()

    def enterEvent(self, event):
        if not self.collapsed:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        super().enterEvent(event)

  
