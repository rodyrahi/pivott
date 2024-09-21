import json
import os

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

from custom_widgets import MainButton , Button
from dataframe_table import tableWidget
from table_widget import OptimizedTableWidget
from dataframeinfo import dataframeinfo
from collapsable_widgets import CollapsableWidget
from operation_widgets import dropDuplicateWidget , imputeMissingWidget , process_file



from file_functions import create_folder , read_save_parquet , df_from_parquet , read_json_file


class MainInterface(QWidget):
    
    def __init__(self , project_path):
        super().__init__()
        self.project_path =project_path

        self.file_path = ""
        self.project_data = ""
        self.save_data_folder  = ""
        self.current_df = []
        self.dataframe_columns = []
        self.main_df = None

        self.impute_checkboxes = []


        self.prepare_project()
        self.initUI()
    
    def prepare_project(self):
        
        with open(self.project_path, 'r') as f:
            self.project_data = json.load(f)

        self.file_path = self.project_data["data_path"]
        self.save_data_folder = f"{self.project_path.split('.')[0]}/save_data"
        print(self.save_data_folder)
        create_folder(self.save_data_folder)
        read_save_parquet(self.file_path, f"{self.save_data_folder}/df.parquet")
        self.current_df = [f"{self.save_data_folder}/df.parquet"]
        print(self.current_df)

            
    def initUI(self):
        main_layout = QHBoxLayout()

        self.table_layout = QVBoxLayout()
        self.properties_layout = QVBoxLayout()
        self.table_bottom_layout = QVBoxLayout()

        # df = df_from_parquet(self.current_df[-1])
        self.table_widget = OptimizedTableWidget()
        self.main_df = df_from_parquet(self.current_df[0])
        self.update_table(self.main_df)

        # self.table_widget.setData(df)
        self.dataframe_columns = self.main_df.columns.to_list()
        print(self.dataframe_columns)


        self.table_layout.addWidget(self.table_widget)
    
        self.table_layout.addLayout(self.table_bottom_layout)

        # self.dataframe_info = dataframeinfo(df , parent=self)

    
        features = [
            ("Drop Duplicates" , dropDuplicateWidget),
            ("Impute Missing", imputeMissingWidget ),
        ]

        for feature_name, feature_widget in features:
            collapsible = CollapsableWidget(feature_name)
            collapsible.setWidgets(feature_widget , self)
            self.properties_layout.addWidget(collapsible)

    
        
    
        self.table_layout.setSpacing(20) 
        self.properties_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.addLayout(self.table_layout, 75)
        main_layout.addLayout(self.properties_layout, 25)

    

        self.setLayout(main_layout)

        process_file(self , read_json_file(self.project_path) )





    # def new_project(self):
    #     # TODO: Implement new project functionality
    #     pass

    # def open_project(self):
    #     self.dataframe_info.show()



    def update_table(self , df = None):

        if df is not None:
            self.table_widget.setData(df)
            return
        
        if os.path.exists(self.current_df[0].replace("df.parquet", "final_df.parquet")):
            df = df_from_parquet(self.current_df[0].replace("df.parquet", "final_df.parquet"))
            self.table_widget.setData(df)

        else:    
            df = self.main_df
            self.table_widget.setData(df)

    