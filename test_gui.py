
import cProfile
import pstats
import json
import sys
from PyQt6.QtWidgets import *
import qdarkstyle
import pandas as pd
import glob
import os
from project_window import *
from custom_widgets import MainButton , Button
# from sklearn.impute import SimpleImputer




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.project_path = ""


        self.setWindowTitle('Two Column Main Window')
        self.setWindowIcon(QIcon('icon.png'))

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout for central widget
        self.main_layout = QHBoxLayout(central_widget)

        project_widget = ProjectWidget(main_parent = self)
        self.main_layout.addWidget(project_widget)

        self.header_layout = QHBoxLayout()

        # Add the close button to the top right
        close_button = QPushButton("×")
        close_button.setObjectName("closeButton")
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet("""
            QPushButton#closeButton {
                background-color: transparent;
                border: none;
                color: #808080;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton#closeButton:hover {
                color: white;
            }
        """)
        close_button.clicked.connect(self.close)

        self.header_layout.addStretch(1)  # Push close button to the right
        self.header_layout.addWidget(close_button)

        self.header_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # Add the header layout with close button at the top
        self.main_layout.addLayout(self.header_layout)
        


        # Set the window properties
        self.setWindowTitle('Pivot')
        self.setFixedSize(800, 600)

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint , True)
               # Make the window draggable
        self.drag_position = QPoint()

    # Function to enable dragging the frameless window
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.drag_position:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
    
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept() 


    def toggle_frame(self):

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, False)
        self.setFixedSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX)
        self.drag_position = None
        self.main_layout.removeItem(self.header_layout)
        
        self.showNormal() 



if __name__ == "__main__":
  
    with cProfile.Profile() as profile:  
        app = QApplication(sys.argv)
        
        window = MainWindow()
        window.show()
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt6())
        
        app.exec()
        
    results = pstats.Stats(profile).sort_stats(pstats.SortKey.TIME)
    results.dump_stats('profile_results.prof')