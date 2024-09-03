from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

import json
import os


from dataframeinfo import *
from dataframe_table import *
from dataframe_widget import *
from custom_widgets import *
from feature_widgets import *
from automation import *
from api import *


try:
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    config = None




global VERSION

code = 0.003

if config:
    VERSION = config['VERSION'] = code
    with open('config.json', 'w') as config_file:
        json.dump(config, config_file, indent=4)
else:
    VERSION = code





print("Version:", VERSION)



class MenuWidget(QMenuBar):
    def __init__(self, top_parent ,  parent=None ):
        super().__init__(top_parent)
        self.top_parent = top_parent
        self.parent = parent
        self.setup_menus()

    def setup_menus(self):
        # Add File menu
        file_menu = self.addMenu("File")
        self.add_file_actions(file_menu)

        # Add Edit menu
        edit_menu = self.addMenu("Edit")
        self.add_edit_actions(edit_menu)

        # Add Help menu
        help_menu = self.addMenu("Help")
        self.add_help_actions(help_menu)

    def add_file_actions(self, file_menu):
        new_action = QAction("New Project", self)
        open_action = QAction("Open Project", self)
        save_action = QAction("Save", self)
        exit_action = QAction("Exit", self)

        new_action.triggered.connect(self.parent.create_project)
        open_action.triggered.connect(self.parent.open_project)

        exit_action.triggered.connect(self.top_parent.close)

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

    def add_edit_actions(self, edit_menu):
        cut_action = QAction("Cut", self)
        copy_action = QAction("Copy", self)
        paste_action = QAction("Paste", self)

        edit_menu.addAction(cut_action)
        edit_menu.addAction(copy_action)
        edit_menu.addAction(paste_action)

    def add_help_actions(self, help_menu):
        about_action = QAction("About", self)
        help_menu.addAction(about_action)


class TwoColumnWindow(QWidget):
    def __init__(self , parent):
        super().__init__()
        self.parent = parent
        self.setWindowIcon(QIcon('icon.png'))
        
        self.version = VERSION

        self.df = None
        self.filepath = None
        self.projectpath = None

        self.checked = []
        self.unchecked = []

        self.mainLayout = QHBoxLayout()
        self.column0Layout = QVBoxLayout()
        self.column1Layout = QVBoxLayout()



        self.filecolumnLayout = QVBoxLayout()
        self.featurescolumnLayout = QVBoxLayout()

        
        self.column2Layout = QVBoxLayout()

       

        self.df_widget = None
        self.imputewidget = None
        self.drop_nanwidget = None

        self.impute_checkboxes = []
        self.encode_checkboxes = []
        self.dropna_checkboxes = []
        self.dropcol_checkboxes = []
        self.outlier_checkboxes = []
        self.duplicate_checkboxes = []

        self.initUI()

    def initUI(self):
        # Create the main layout

        
        self.open_project_btn = MainButton('Open Project')
        self.open_project_btn.clicked.connect(self.open_project)
        self.column2Layout.addWidget(self.open_project_btn)
        

        self.new_project_button = MainButton('New Project')
        self.new_project_button.clicked.connect(self.create_project)

        self.column2Layout.addWidget(self.new_project_button)




        

        image = QLabel(pixmap=QPixmap('logo.png'))
        self.filecolumnLayout.addWidget(image)

        version_label = QLabel(f"Version: {self.version}")
        self.filecolumnLayout.addWidget(version_label)

        self.column1Layout.setSpacing(20)   
        
        image.setFixedSize(500 , 500)
        
        self.filecolumnLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
       
        self.column1Layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.column0Layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.column2Layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        
        
        
        self.mainLayout.addLayout(self.column2Layout)
        
       

        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_widget.setLayout(self.column1Layout)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        self.mainLayout.addWidget(self.scroll_area)
        
        self.scroll_area.setMaximumSize(380, 1000)
        self.scroll_area.hide()
        
         # Add columns to the main layout
        self.mainLayout.addLayout(self.column0Layout)
        

        
        self.column0Layout.addLayout(self.filecolumnLayout)
        self.column0Layout.addLayout(self.featurescolumnLayout)
        self.featurescolumnLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        

        # Set the main layout for the window
        self.setLayout(self.mainLayout)


    
 

    def create_project(self):
        save_location, _ = QFileDialog.getSaveFileName(self, "Save Project", "", "JSON Files (*.json)")
        if save_location:
            self.projectpath = save_location
            project_name = os.path.splitext(os.path.basename(save_location))[0]
            with open(save_location, 'w') as f:
                json.dump({"data_path":"" , "impute": {"col": [], "strategy": []}, "encode": {"col": []}, "dropna": {"col": []} ,"dropcol": {"col": []} , "outlier": {"col": [] , "method": []}  } , f)
            



            
            

            self.select_button = MainButton('Select .Csv or .xlsx File')
            self.select_button.clicked.connect(self.set_df)


            self.column2Layout.addWidget(self.select_button)


            # project_label = QLabel(f"Project Selected: {project_name}")
            # self.column2Layout.addWidget(project_label)

            self.open_project_btn.hide()
            self.new_project_button.hide()                        

    def open_project(self):
        project_path, _ = QFileDialog().getOpenFileName(self, "Open Project", "", "JSON Files (*.json)")
        if project_path:
            with open(project_path, 'r') as file:
                jsonfile = json.load(file)
        

            self.projectpath = project_path
            self.select_source(jsonfile)


    def select_source(self , jsonfile):
        print(jsonfile)
        data_path = jsonfile["data_path"]
        self.df = dataframe(data_path)

        self.create_df_widgets()
        self.create_table()
        
        for i in jsonfile.items():

            if i[0] == 'impute':
                list_col = list(i[1]["col"])
                list_strategy = list(i[1]["strategy"])

                for k in self.impute_checkboxes:
                    
                    for index,col in enumerate(list_col):
                        if k.label.text() == col:
                            k.checked()
                            k.func( state = True, checkbox=k.checkbox , column=col , strategy=list_strategy[index])
            
            if i[0] == 'encode':
                list_col = list(i[1]["col"])

                for k in self.encode_checkboxes:
                    for col in list_col:
                        if k.label.text() ==col:
                            k.checked()
                            k.func( state = True, checkbox=k.checkbox , column=col)

            if i[0] == 'dropna':
                list_col = list(i[1]["col"])

                for k in self.dropna_checkboxes:
                    for col in list_col:
                        if k.label.text() ==col:
                            k.checked()
                            k.func( state = True, checkbox=k.checkbox , column=col)
            
            if i[0] == 'dropcol':
                list_col = list(i[1]["col"])

                for k in self.dropcol_checkboxes:
                    for col in list_col:
                        if k.label.text() ==col:
                            k.checked()
                            k.func( state = True, checkbox=k.checkbox , column=col)

            if i[0] == 'outlier':
                
                    list_col = list(i[1]["col"])
                    list_method = list(i[1]["method"])

                    for k in self.outlier_checkboxes:
                        
                        for index,col in enumerate(list_col):
                            if k.label.text() == col:
                                k.checked()
                                # state , checkbox=outliercol.checkbox,list = outliercol.method ,col=column 
                                print(index)
                                k.func( state = True, checkbox=k.checkbox , list=list_method[index] , column=col )


    # def select_source(self, jsonfile):
    #     print(jsonfile)
    #     data_path = jsonfile["data_path"]
    #     self.df = dataframe(data_path)

    #     self.create_df_widgets()
    #     self.create_table()

    #     # Mapping action keys to corresponding checkbox attributes
    #     action_mapping = {
    #         'impute': ('impute_checkboxes', 'strategy'),
    #         'encode': ('encode_checkboxes', None),
    #         'dropna': ('dropna_checkboxes', None),
    #         'dropcol': ('dropcol_checkboxes', None),
    #         'outlier': ('outlier_checkboxes', 'method')
    #     }

    #     for action, params in jsonfile.items():
    #         if action in action_mapping:
    #             checkbox_attr, strategy_key = action_mapping[action]
    #             list_col = list(params["col"])
    #             list_strategy = list(params[strategy_key]) if strategy_key else None

    #             for k in getattr(self, checkbox_attr):
    #                 for index, col in enumerate(list_col):
    #                     if k.label.text() == col:
    #                         k.checked()
    #                         kwargs = {
    #                             "state": True,
    #                             "checkbox": k.checkbox,
    #                             "column": col
    #                         }
    #                         if list_strategy:
    #                             kwargs[strategy_key] = list_strategy[index]
    #                         k.func(**kwargs)

            
        
    # def create_df_widgets(self):
    #     self.scroll_area.show()
    #     # self.remove_all_widgets(self.column0Layout)
    #     self.remove_all_widgets(self.featurescolumnLayout)
    #     self.remove_all_widgets(self.filecolumnLayout)

    #     popup_button = Button('Dataframe Info')
    #     infodf = dataframeinfo(self.df.dataframe , parent=self)
    #     popup_button.clicked.connect(lambda: infodf.show())
    #     self.featurescolumnLayout.addWidget(popup_button)



    #     select_button = Button('Select Source')
    #     select_button.clicked.connect(self.set_df)
    #     self.featurescolumnLayout.addWidget(select_button)


       

    #     self.drop_duplicate_checkbox = popCheckBox('Drop Duplicates' , parent=self , widget=featureWidget  )
    #     self.drop_duplicate_checkbox.widget.dropduplicateUI()
    #     self.featurescolumnLayout.addWidget(self.drop_duplicate_checkbox.cb)
    #     self.drop_duplicate_checkbox.cb.stateChanged.connect(lambda:self.drop_duplicate_checkbox.visbility())


    #     self.drop_nan_checkbox = popCheckBox('Drop Missing Values' , parent=self , widget=featureWidget  )
    #     self.drop_nan_checkbox.widget.dropnaUI()
    #     self.featurescolumnLayout.addWidget(self.drop_nan_checkbox.cb)
    #     self.drop_nan_checkbox.cb.stateChanged.connect(lambda:self.drop_nan_checkbox.visbility())

        
        
       
    #     self.impute_checkbox = popCheckBox('Impute Missing Values' , parent=self , widget=featureWidget)
    #     self.impute_checkbox.widget.imputeUI()
    #     self.featurescolumnLayout.addWidget(self.impute_checkbox.cb)
    #     self.impute_checkbox.cb.stateChanged.connect(lambda:self.impute_checkbox.visbility())



    #     self.outlier_checkbox = popCheckBox('Outlier Removing' , parent=self , widget=featureWidget )
    #     self.outlier_checkbox.widget.outlierUI()
    #     self.featurescolumnLayout.addWidget(self.outlier_checkbox.cb)
    #     self.outlier_checkbox.cb.stateChanged.connect(lambda:self.outlier_checkbox.visbility())

        
    #     encoding_checkbox = popCheckBox('Encoding Categorical' , parent=self , widget=featureWidget )
    #     encoding_checkbox.widget.encodeUI()
    #     self.featurescolumnLayout.addWidget(encoding_checkbox.cb)
    #     encoding_checkbox.cb.stateChanged.connect(lambda:encoding_checkbox.visbility())

    #     dropcol_checkbox = popCheckBox('Drop Columns' , parent=self , widget=featureWidget )
    #     dropcol_checkbox.widget.dropcolUI()
    #     self.featurescolumnLayout.addWidget(dropcol_checkbox.cb)
    #     dropcol_checkbox.cb.stateChanged.connect(lambda:dropcol_checkbox.visbility())


    #     # Create an empty QTableWidget
    #     self.empty_table = QTableWidget()
    #     self.empty_table.setRowCount(0)
    #     self.empty_table.setColumnCount(0)
        
        
    #     # Add the empty table to column2Layout
    #     self.column2Layout.addWidget(self.empty_table)
    #     auto_button = Button('Automate with AI')
    #     auto_button.clicked.connect(self.automate_with_ai)
    #     self.column0Layout.addWidget(auto_button)

        
    def create_df_widgets(self):

        self.parent.setMenuBar(MenuWidget(self.parent , self))
        self.scroll_area.show()
        self.remove_all_widgets(self.featurescolumnLayout)
        self.remove_all_widgets(self.filecolumnLayout)

        # Create and add the "Dataframe Info" button
        popup_button = Button('Dataframe Info')
        infodf = dataframeinfo(self.df.dataframe, parent=self)
        popup_button.clicked.connect(lambda: infodf.show())
        self.featurescolumnLayout.addWidget(popup_button)

        # Create and add the "Select Source" button
        select_button = Button('Select Source')
        select_button.clicked.connect(self.set_df)
        self.featurescolumnLayout.addWidget(select_button)

        # List of checkbox configurations (label, UI method, max size, min size)
        checkbox_configs = [
            ('Drop Duplicates', 'dropduplicateUI', QSize(350, 95), QSize(200, 95)),
            ('Drop Missing Values', 'dropnaUI', QSize(350, 300), QSize(200, 300)),
            ('Impute Missing Values', 'imputeUI', QSize(350, 300), QSize(200, 300)),
            ('Outlier Removing', 'outlierUI', QSize(350, 700), QSize(200, 300)),
            ('Encoding Categorical', 'encodeUI', QSize(350, 300), QSize(200, 300)),
            ('Drop Columns', 'dropcolUI', QSize(350, 300), QSize(200, 300)),
        ]

        # Create checkboxes dynamically based on the configurations
        for label, ui_method, max_size, min_size in checkbox_configs:
            checkbox = popCheckBox(label, parent=self, widget=featureWidget)
            getattr(checkbox.widget, ui_method)()  # Call the UI method dynamically
            checkbox.widget.setMaximumSize(max_size)  # Set maximum size dynamically
            checkbox.widget.setMinimumSize(min_size)  # Set minimum size dynamically
            self.featurescolumnLayout.addWidget(checkbox.cb)
            checkbox.cb.stateChanged.connect(lambda _, cb=checkbox: cb.visbility())
        # Create and add an empty QTableWidget
        self.empty_table = QTableWidget(0, 0)
        self.column2Layout.addWidget(self.empty_table)

        # Create and add the "Automate with AI" button
        auto_button = Button('Automate with AI')
        auto_button.clicked.connect(self.automate_with_ai)
        self.column0Layout.addWidget(auto_button)


        


    def automate_with_ai(self):
        # Create a new window
        self.ai_window = QWidget()
        self.ai_window.setWindowTitle("AI Automation")
        self.ai_window.setGeometry(100, 100, 400, 300)

        # Create a layout for the new window
        layout = QVBoxLayout()

        # Create a text area

        self.ai_text_area = QTextEdit()
               
        self.ai_text_area.setPlaceholderText("Write a small description of the dataset")        
        layout.addWidget(self.ai_text_area)

        # Create a button
        ai_button = Button("Run AI Automation")

        ai_button.clicked.connect(lambda:auto_clean(self.ai_text_area,self))
        layout.addWidget(ai_button)
        layout.setAlignment(Qt.AlignCenter)

        # Set the layout for the new window
        self.ai_window.setLayout(layout)

        # Show the new window
        self.ai_window.show()

        


    def set_df(self):
        file_path, _ = QFileDialog().getOpenFileName(filter="Excel or CSV Files (*.xlsx *.csv)")
        
        if file_path:
            self.filepath = file_path
            
            with open(self.projectpath, 'r') as file:
                jsonfile = json.load(file)

            
            jsonfile["data_path"] = file_path
            with open(self.projectpath, 'w') as file:
                json.dump(jsonfile, file, indent=4) 
            
            
            if not jsonfile["data_path"] == "":
                self.select_source(jsonfile)
            else:
                self.df = dataframe(file_path)

                self.create_df_widgets()
                self.create_table()
        
        
        

    
    def create_table(self):
        if self.df is None:
            return None
        

        self.remove_all_widgets(self.column2Layout)

        self.df_widget = tableWidget(self.df.dataframe)
        export_button = Button('Export to CSV')

        self.column2Layout.addWidget(self.df_widget)
        self.column2Layout.addWidget(export_button)
        export_button.clicked.connect(self.export_to_csv)
    
    def export_to_csv(self):
        file_path, _ = QFileDialog().getSaveFileName()
        print(file_path)
        if file_path:
            self.df.dataframe.to_csv(file_path + ".csv", index=False)
    def remove_all_widgets(self , layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    