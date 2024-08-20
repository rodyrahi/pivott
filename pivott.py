import sys
import os
# from PySide2 import QtWidgets
import qdarkstyle
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import json
from dataframe_widget import *
from feature_widgets import *
from custom_widgets import *
from automation import *
from api import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn as sns 


global VERSION
VERSION = 0.001

print("Version :" ,VERSION)



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
            value_counts = self.dataframe[column_name].value_counts().sort_index()
            unique_values_str = '\n'.join(f"{value} :{count}" for value, count in value_counts.items())
            # Create a context menu
            context_menu = QMenu(self)

            # Create a QTextEdit for displaying unique values
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setText(unique_values_str)
            text_edit.setMaximumSize(400, 300)  # Set a maximum size for the text edit



            # Add distribution plot if the column is numeric
            if self.dataframe[column_name].dtype in ['int64', 'float64']:
                fig, ax = plt.subplots(figsize=(4, 3))
                self.dataframe[column_name].hist(ax=ax)
                ax.set_title(f'Distribution of {column_name}')
                ax.set_xlabel(column_name)
                ax.set_ylabel('Frequency')

                canvas = FigureCanvas(fig)
                canvas.setFixedSize(300, 200)

                plot_action = QWidgetAction(context_menu)
                plot_action.setDefaultWidget(canvas)
                context_menu.addAction(plot_action)

                # Add range information for numeric columns
                min_value = self.dataframe[column_name].min()
                max_value = self.dataframe[column_name].max()
                range_str = f"Range: {min_value} to {max_value}"
            else:
                # Create graph of count for non-numeric columns
                fig, ax = plt.subplots(figsize=(4, 3))
                value_counts = self.dataframe[column_name].value_counts()
                value_counts.plot(kind='bar', ax=ax)
                ax.set_title(f'Count of {column_name}')
                ax.set_xlabel(column_name)
                ax.set_ylabel('Count')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()

                canvas = FigureCanvas(fig)
                canvas.setFixedSize(300, 200)

                plot_action = QWidgetAction(context_menu)
                plot_action.setDefaultWidget(canvas)
                context_menu.addAction(plot_action)

                range_str = "Range: Not applicable for non-numeric data"
            range_action = context_menu.addAction(range_str)
            range_action.setEnabled(False)
            
            context_menu.addSeparator()

            # Create a QWidgetAction to hold the QTextEdit
            widget_action = QWidgetAction(context_menu)
            
            widget_action.setDefaultWidget(text_edit)
            context_menu.addAction("Unique Values")
            context_menu.addAction(widget_action)

            # Show the context menu at the cursor position
            context_menu.exec_(QCursor.pos())

class TwoColumnWindow(QWidget):
    def __init__(self):
        super().__init__()
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

        
        
        open_project = MainButton('Open Project')
        open_project.clicked.connect(self.open_project)
        self.filecolumnLayout.addWidget(open_project)
        

        new_project_button = MainButton('New Project')
        new_project_button.clicked.connect(self.create_project)

        self.filecolumnLayout.addWidget(new_project_button)


        select_button = MainButton('Select Source')
        select_button.clicked.connect(self.set_df)
        self.filecolumnLayout.addWidget(select_button)

        

        image = QLabel(pixmap=QPixmap('logo.png'))
        self.column2Layout.addWidget(image)

        self.column1Layout.setSpacing(20)   
        
        image.setFixedSize(500 , 500)
        
        self.filecolumnLayout.setAlignment(Qt.AlignCenter)
        self.column0Layout.setAlignment(Qt.AlignRight)
        self.column1Layout.setAlignment(Qt.AlignTop)
        self.column2Layout.setAlignment(Qt.AlignLeft)


        
        # Add columns to the main layout
        self.mainLayout.addLayout(self.column0Layout)

        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_widget.setLayout(self.column1Layout)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        self.mainLayout.addWidget(self.scroll_area)
        
        self.scroll_area.setMaximumSize(380, 1000)
        self.scroll_area.hide()
        
        self.mainLayout.addLayout(self.column2Layout)
        

        
        self.column0Layout.addLayout(self.filecolumnLayout)
        self.column0Layout.addLayout(self.featurescolumnLayout)
        self.featurescolumnLayout.setAlignment(Qt.AlignTop)

        

        # Set the main layout for the window
        self.setLayout(self.mainLayout)

        # Set the window properties
        self.setWindowTitle('Pivot')
        self.setGeometry(300, 100, 1000, 600)
    
 

    def create_project(self):
        save_location, _ = QFileDialog.getSaveFileName(self, "Save Project", "", "JSON Files (*.json)")
        if save_location:
            self.projectpath = save_location
            project_name = os.path.splitext(os.path.basename(save_location))[0]
            with open(save_location, 'w') as f:
                json.dump({"data_path":"" , "impute": {"col": [], "strategy": []}, "encode": {"col": []}, "dropna": {"col": []} ,"dropcol": {"col": []} , "outlier": {"col": [] , "method": []}  } , f)
                        

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
                                k.func( state = True, checkbox=k.checkbox , list=list_method[index] , column=col )



            
        
    def create_df_widgets(self):
        self.scroll_area.show()
        # self.remove_all_widgets(self.column0Layout)
        self.remove_all_widgets(self.featurescolumnLayout)
        self.remove_all_widgets(self.filecolumnLayout)


        select_button = Button('Select Source')
        select_button.clicked.connect(self.set_df)
        self.featurescolumnLayout.addWidget(select_button)

        # self.featurescolumnLayout.addWidget(QCheckBox('Drop Duplicates'))

        self.drop_duplicate_checkbox = popCheckBox('Drop Duplicates' , parent=self , widget=featureWidget  )
        self.drop_duplicate_checkbox.widget.dropduplicateUI()
        self.featurescolumnLayout.addWidget(self.drop_duplicate_checkbox.cb)
        self.drop_duplicate_checkbox.cb.stateChanged.connect(lambda:self.drop_duplicate_checkbox.visbility())


        self.drop_nan_checkbox = popCheckBox('Drop Missing Values' , parent=self , widget=featureWidget  )
        self.drop_nan_checkbox.widget.dropnaUI()
        self.featurescolumnLayout.addWidget(self.drop_nan_checkbox.cb)
        self.drop_nan_checkbox.cb.stateChanged.connect(lambda:self.drop_nan_checkbox.visbility())

        
        
       
        self.impute_checkbox = popCheckBox('Impute Missing Values' , parent=self , widget=featureWidget)
        self.impute_checkbox.widget.imputeUI()
        self.featurescolumnLayout.addWidget(self.impute_checkbox.cb)
        self.impute_checkbox.cb.stateChanged.connect(lambda:self.impute_checkbox.visbility())



        self.outlier_checkbox = popCheckBox('Outlier Removing' , parent=self , widget=featureWidget )
        self.outlier_checkbox.widget.outlierUI()
        self.featurescolumnLayout.addWidget(self.outlier_checkbox.cb)
        self.outlier_checkbox.cb.stateChanged.connect(lambda:self.outlier_checkbox.visbility())

        
        encoding_checkbox = popCheckBox('Encoding Categorical' , parent=self , widget=featureWidget )
        encoding_checkbox.widget.encodeUI()
        self.featurescolumnLayout.addWidget(encoding_checkbox.cb)
        encoding_checkbox.cb.stateChanged.connect(lambda:encoding_checkbox.visbility())

        dropcol_checkbox = popCheckBox('Drop Columns' , parent=self , widget=featureWidget )
        dropcol_checkbox.widget.dropcolUI()
        self.featurescolumnLayout.addWidget(dropcol_checkbox.cb)
        dropcol_checkbox.cb.stateChanged.connect(lambda:dropcol_checkbox.visbility())


        # Create an empty QTableWidget
        self.empty_table = QTableWidget()
        self.empty_table.setRowCount(0)
        self.empty_table.setColumnCount(0)
        
        
        # Add the empty table to column2Layout
        self.column2Layout.addWidget(self.empty_table)
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
        file_path, _ = QFileDialog().getOpenFileName()
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
        # QMessageBox.information(self, "Update", "Update page opened in your browser.")
    def show_update_message(self):
        self.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)


    window = TwoColumnWindow()
    # isupdate = get_update(version=VERSION).update()
    # print(isupdate)
    # if get_update(version={"version":VERSION}).update()["update"] == "yes":


    #     window = UpdateDialog()
    # else:
    #     window = TwoColumnWindow()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window.show()
    sys.exit(app.exec_())




# def get_travel_advice():
#     prompt = f"the dataset is a ticanic dataset wihich tells about the survival of the passenger , the dataset has the columns PassengerId(range from 1 to 891),Survived(range from 0 to 1),Pclass(range from 1 to 3),Name,Sex,Age(range from 0 to 80 , contains nan),SibSp,Parch,Ticket,Fare,Cabin(contains nan),Embarked(contains nan) : what data cleaning should be taken foreach column   "

#     response = openai.chat.completions.create(
#         model="gpt-4o",
#         messages=[
#             {"role": "system", "content": "You are a data scientist"},
#             {"role": "user", "content": f"{prompt}:Without any comment, return the result in the following JSON format {{column: from these setps select one or more also if imputing tell the strategy [dropna,impute:mean/median/most_frequent,encoding_categorical_data,drop_duplicaes,drop_column,outlier_removing  ]}}"  }
#         ]
#     )
#     advice = response.choices[0].message.content
#     print(advice)
#     # return advice
# get_travel_advice()