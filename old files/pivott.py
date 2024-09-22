import sys
import os
# from PySide2 import QtWidgets
import qdarkstyle
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *


import json

from feature_widgets import *
from custom_widgets import *
from automation import *
from maincolumns import *
from api import *





class UpdateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Software Update")
        self.setFixedSize(300, 150)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        message_label = QLabel("A new update is available!")
        message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(message_label)

        version_label = QLabel(f"Version: {VERSION}")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)

        update_button = Button("Update Now")
        update_button.clicked.connect(self.perform_update)
        layout.addWidget(update_button)

        close_button = Button("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def perform_update(self):
        
        import webbrowser
        webbrowser.open("https://pivott.click")
        QMessageBox.information(self, "Update", "Update page opened in your browser.")
    def show_update_message(self):
        self.exec_()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Two Column Main Window')
        self.setWindowIcon(QIcon('icon.png'))

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout for central widget
        main_layout = QHBoxLayout(central_widget)

        main_layout.addWidget(TwoColumnWindow(parent=self))

    
        
        # Set the window properties
        self.setWindowTitle('Pivot')
        self.setGeometry(300, 100, 1000, 600)




if __name__ == '__main__':
    app = QApplication(sys.argv)


    # window = TwoColumnWindow()
    isupdate = get_update(version=VERSION).update()
    print(isupdate)
    if get_update(version={"version":VERSION}).update()["update"] == "yes":


        window = UpdateDialog()
    else:
        window = MainWindow()

    
    
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt6())
    window.show()
    sys.exit(app.exec_())

