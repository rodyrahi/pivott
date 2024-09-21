
import cProfile
import pstats
import json
import sys
from PyQt6.QtWidgets import *
import qdarkstyle
import pandas as pd
import glob
import os
from data_cleaning import *
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
        main_layout = QHBoxLayout(central_widget)

        project_widget = ProjectWidget()
        main_layout.addWidget(project_widget)

    
        
        # Set the window properties
        self.setWindowTitle('Pivot')
        self.setGeometry(300, 100, 1000, 600)
        






if __name__ == "__main__":
  
    with cProfile.Profile() as profile:  
        app = QApplication(sys.argv)
        
        window = MainWindow()
        window.show()
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt6())

        app.exec()
        
    results = pstats.Stats(profile).sort_stats(pstats.SortKey.TIME)
    results.dump_stats('profile_results.prof')