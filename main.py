import sys
import os
from PySide2 import QtWidgets
import qdarkstyle
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import json
from dataframe_widget import *
from feature_widgets import *
from custom_widgets import *






# class dragableListWidget(QListWidget):
#     def __init__(self , df):
#         super().__init__()
#         self.setAcceptDrops(True)
#         self.df = df
#         self.initUI()
        

#     def initUI(self):
#         self.setStyleSheet("max-width: 150px;")
#         for column in self.df.dataframe.columns:
#             item = QListWidgetItem(column)
            
#             self.setDragDropMode(QAbstractItemView.InternalMove)
            
#             self.addItem(item)

class tableWidget(QWidget):
        def __init__(self, dataframe):
            super().__init__()

            self.dataframe = dataframe
            self.initUI()

        def initUI(self):
            layout = QVBoxLayout()

            # Create QTableWidget
            self.tableWidget = QTableWidget()
            self.tableWidget.setRowCount(self.dataframe.shape[0])
            self.tableWidget.setColumnCount(self.dataframe.shape[1])
            self.tableWidget.setHorizontalHeaderLabels(self.dataframe.columns)

            # Fill QTableWidget with DataFrame data
            for row in range(self.dataframe.shape[0]):
                for col in range(self.dataframe.shape[1]):
                    item = QTableWidgetItem(str(self.dataframe.iat[row, col]))
                    self.tableWidget.setItem(row, col, item)

            # Connect header right-click event to show unique values
            self.tableWidget.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
            self.tableWidget.horizontalHeader().customContextMenuRequested.connect(self.show_unique_values)

            layout.addWidget(self.tableWidget)
            self.setLayout(layout)
            self.setWindowTitle('DataFrame Viewer')


        def show_unique_values(self, pos):
            logical_index = self.tableWidget.horizontalHeader().logicalIndexAt(pos)
            column_name = self.dataframe.columns[logical_index]
            unique_values = self.dataframe[column_name].unique().tolist()
            unique_values_str = '\n'.join(map(str, unique_values))

            # Create a context menu
            context_menu = QMenu(self)

            # Create a QTextEdit for displaying unique values
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setText(unique_values_str)

            # Set a maximum size for the text edit
            text_edit.setMaximumSize(400, 300)

            # Create a QWidgetAction to hold the QTextEdit
            widget_action = QWidgetAction(context_menu)
            widget_action.setDefaultWidget(text_edit)

            # Add the widget action to the context menu
            context_menu.addAction('Unique Values')
            context_menu.addAction(widget_action)

            # Show the context menu at the cursor position
            context_menu.exec_(QCursor.pos())

class TwoColumnWindow(QWidget):
    def __init__(self):
        super().__init__()
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

        self.initUI()

    def initUI(self):
        # Create the main layout


        
        open_project = Button('Open Project')
        open_project.clicked.connect(self.open_project)
        self.filecolumnLayout.addWidget(open_project)
        

        new_project_button = Button('New Project')
        new_project_button.clicked.connect(self.create_project)

        self.filecolumnLayout.addWidget(new_project_button)


        select_button = Button('Select Source')
        select_button.clicked.connect(self.set_df)
        self.filecolumnLayout.addWidget(select_button)

        

        image = QLabel(pixmap=QPixmap('logo.png'))
        self.column0Layout.addWidget(image)


        
       
        
        self.column1Layout.setAlignment(Qt.AlignTop)

        
        # Add columns to the main layout
        self.mainLayout.addLayout(self.column1Layout)
        self.mainLayout.addLayout(self.column2Layout)
        self.mainLayout.addLayout(self.column0Layout)


        self.column1Layout.addLayout(self.filecolumnLayout)
        self.column1Layout.addLayout(self.featurescolumnLayout)
        

        # Set the main layout for the window
        self.setLayout(self.mainLayout)

        # Set the window properties
        self.setWindowTitle('Pivot')
        self.setGeometry(300, 100, 1000, 600)
    
 
    # def create_list(self):
    #     if self.df is None:
    #         return None
    #     self.column0Layout.removeWidget(dragableListWidget(self.df))
    #     self.column0Layout.addWidget(dragableListWidget(self.df))

    def create_project(self):
        save_location, _ = QFileDialog.getSaveFileName(self, "Save Project", "", "JSON Files (*.json)")
        if save_location:
            self.projectpath = save_location
            project_name = os.path.splitext(os.path.basename(save_location))[0]
            with open(save_location, 'w') as f:
                json.dump({}, f)
                        

    def open_project(self):
        project_path, _ = QFileDialog().getOpenFileName()
        if project_path:
            with open(project_path, 'r') as file:
                jsonfile = json.load(file)
        

            self.projectpath = project_path
            self.select_source(jsonfile)

            # data_path = jsonfile["data_path"]
            # self.df = dataframe(data_path)

            # self.create_df_widgets()
            # self.create_table()
            
            # for i in jsonfile.items():
            #     if i[0] == 'impute':
            #         list_col = list(i[1]["col"])
            #         list_strategy = list(i[1]["strategy"])

            #         for k in self.impute_checkboxes:
                        
            #             for index,col in enumerate(list_col):
            #                 if k.label.text() == col:
            #                     k.checked()
            #                     k.top.impute_column( state = True, checkbox=k.impute_checkbox , column=col , strategy=list_strategy[index])
    
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

            
        
    def create_df_widgets(self):

        self.remove_all_widgets(self.column0Layout)
        self.remove_all_widgets(self.featurescolumnLayout)


      
        

        self.featurescolumnLayout.addWidget(QCheckBox('Drop Duplicates'))


        dropwidget = featureWidget
        drop_nan_checkbox = popCheckBox('Drop Missing Values' , parent=self , widget=dropwidget  )
        drop_nan_checkbox.widget.dropnaUI()
        self.featurescolumnLayout.addWidget(drop_nan_checkbox.cb)
        drop_nan_checkbox.cb.stateChanged.connect(lambda:drop_nan_checkbox.visbility())

        
        
        imputewidget = featureWidget
        self.impute_checkbox = popCheckBox('Impute Missing Values' , parent=self , widget=imputewidget)
        self.impute_checkbox.widget.imputeUI()
        self.featurescolumnLayout.addWidget(self.impute_checkbox.cb)
        self.impute_checkbox.cb.stateChanged.connect(lambda:self.impute_checkbox.visbility())



        outlier_checkbox = popCheckBox('Outlier Removing' , parent=self , widget=featureWidget )
        self.featurescolumnLayout.addWidget(outlier_checkbox.cb)
        outlier_checkbox.cb.stateChanged.connect(lambda:outlier_checkbox.visbility())

        
        encoding_checkbox = popCheckBox('Encoding Categorical' , parent=self , widget=featureWidget )
        encoding_checkbox.widget.encodeUI()
        self.featurescolumnLayout.addWidget(encoding_checkbox.cb)
        encoding_checkbox.cb.stateChanged.connect(lambda:encoding_checkbox.visbility())


        # Create an empty QTableWidget
        self.empty_table = QTableWidget()
        self.empty_table.setRowCount(0)
        self.empty_table.setColumnCount(0)
        
        
        # Add the empty table to column2Layout
        self.column2Layout.addWidget(self.empty_table)

    def set_df(self):
        file_path, _ = QFileDialog().getOpenFileName()
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
        self.column2Layout.addWidget(self.df_widget)
    

    def remove_all_widgets(self , layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        

            


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TwoColumnWindow()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window.show()
    sys.exit(app.exec_())
