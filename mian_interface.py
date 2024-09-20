import json
import os
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

from custom_widgets import MainButton , Button
from dataframe_table import tableWidget
from file_functions import create_folder


class MainInterface(QWidget):
    def __init__(self , project_path):
        super().__init__()
        self.project_path =project_path

        self.file_path = ""
        self.project_data = ""
        self.save_data_folder  = ""

        self.prepare_project()
        self.initUI()
    
    def prepare_project(self):
        
        with open(self.project_path, 'r') as f:
            self.project_data = json.load(f)

        self.file_path = self.project_data["data_path"]
        self.save_data_folder = f"{self.project_path.split('.')[0]}/save_data"
        print(self.save_data_folder)
        create_folder(self.save_data_folder)
       

            
    def initUI(self):
        main_layout = QHBoxLayout()

        self.table_layout = QHBoxLayout()
        self.properties_layout = QHBoxLayout()
        # table = tableWidget(df)

        # self.table_layout.addWidget(tableWidget(table))
        new_project_btn = Button('Table')
        new_project_btn.clicked.connect(self.new_project)
        self.table_layout.addWidget(new_project_btn)
        
        open_project_btn = Button('Options')
        open_project_btn.clicked.connect(self.open_project)
        self.properties_layout.addWidget(open_project_btn)

        self.table_layout.setSpacing(20) 
        self.properties_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(self.table_layout)
        main_layout.addLayout(self.properties_layout)

        

        self.setLayout(main_layout)



    



    def new_project(self):
        # TODO: Implement new project functionality
        pass

    def open_project(self):
        pass