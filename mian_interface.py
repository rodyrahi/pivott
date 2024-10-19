import glob
import json
import os

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

import polars as pl
import numpy as np

from custom_widgets import MainButton , Button , aiButton
# from dataframe_table import tableWidget
from table_widget import OptimizedTableWidget

from dataframeinfo_top import DataFrameInfoWidget

from collapsable_widgets import CollapsableWidget
from operation_widgets import dropDuplicateWidget ,\
    imputeMissingWidget , dropColumnWidget , removeOutlierWidget, process_file \
    , encodingCategoryWidget , dropNaWidget , scaleMinmaxWidget , changeDtypeWidget, changeTextCaseWidget
    
from steps_widget import StepsWidget
from code_genratation.python_code_genration import create_jupyter_notebook


from file_functions import create_folder , read_save_parquet , df_from_parquet\
      , read_json_file


class MainInterface(QWidget):
    
    def __init__(self , project_path):
        super().__init__()

        self.project_path = project_path

        self.file_path = ""
        self.project_data = ""
        self.save_data_folder  = ""
        self.current_df = []
        self.dataframe_columns = []
        self.main_df = None
        self.final_df = None

        self.impute_checkboxes = []
        self.drop_column_checkboxes = []
        self.remove_outlier_checkboxes = []
        self.encode_checkboxes =[]
        self.drop_na_checkboxes = []
        self.scale_minmax_checkboxes = []
        self.change_dtype_checkboxes = []
        self.change_text_case_checkboxes = []

        self.prepare_project()
        self.initUI()

    def prepare_project(self):

        print("preparing project")

        self.project_data = read_json_file(self.project_path)
        self.file_path = self.project_data["data_path"]


        self.save_data_folder = f"{os.path.splitext(self.project_path)[0]}/save_data"
        
        print(self.save_data_folder)
        create_folder(self.save_data_folder)

        self.cache_remove_files()

        parquet_path = f"{self.save_data_folder}/df.parquet"

        read_save_parquet(self.file_path, parquet_path)
        self.current_df = [parquet_path]

        print(self.current_df)

        self.main_df = df_from_parquet(self.current_df[0])

        print("project prepared")

        
    def initUI(self):

        
        main_layout = QHBoxLayout()
        self.table_top_layout = QVBoxLayout()
        self.table_layout = QVBoxLayout()
        self.properties_layout = QVBoxLayout()
        self.steps_layout = QVBoxLayout()
        self.table_bottom_layout = QVBoxLayout()

        self.table_widget = OptimizedTableWidget()
    
        self.update_table(self.main_df)

        self.dataframe_columns = self.main_df.columns
        print(self.dataframe_columns)

        self.table_layout.addWidget(self.table_widget)
        self.table_layout.addLayout(self.table_top_layout)

        self.table_layout.addLayout(self.table_bottom_layout)
        
        steps_widget = StepsWidget(main_interface=self)
        self.steps_layout.addWidget(steps_widget)

        features = [
            # ("Drop Duplicates" , dropDuplicateWidget),
            ("Drop Columns", dropColumnWidget ),
            ("Drop Missing" , dropNaWidget),
            ("Impute Missing", imputeMissingWidget ),
            ("Remove Outliers", removeOutlierWidget),
            ("Encode Categorical", encodingCategoryWidget ),
            ("Scale MinMax", scaleMinmaxWidget),
            ("Change Dtype", changeDtypeWidget),
            ("Change Text Case", changeTextCaseWidget)

        ]

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
    
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        

        for feature_name, feature_widget in features:
            
            collapsible = CollapsableWidget(feature_name , steps_widget)
            # collapsible.setWidgets(feature_widget , self)
            collapsible.feature_widgets = feature_widget
            collapsible.main_interface =  self
            
            collapsible.setWidgets()
            scroll_layout.addWidget(collapsible)
        


        scroll_area.setWidget(scroll_widget)
        self.properties_layout.addWidget(scroll_area)

        # self.table_layout.setSpacing(20) 
      
        self.properties_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.addLayout(self.table_layout, 65)
        main_layout.addLayout(self.properties_layout, 35)
        main_layout.addLayout(self.steps_layout, 10)

        export_button = Button("Exoprt ipynb")
        self.table_bottom_layout.addWidget(export_button)
        export_button.clicked.connect(lambda: create_jupyter_notebook(read_json_file(self.project_path) , "test_python" ))


  

        df_info = DataFrameInfoWidget(self.main_df)
        self.table_top_layout.addWidget(df_info)

        self.properties_layout.addWidget(aiButton("Clean With AI ✨"))
        self.setLayout(main_layout)

       

        process_file(self  , steps_widget=steps_widget )
 
       


    def cache_remove_files(self):
        parquet_files = glob.glob(os.path.join(self.save_data_folder, "*.parquet"))
        for file in parquet_files:
            os.remove(file)

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


