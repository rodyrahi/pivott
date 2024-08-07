import sys
from PySide2 import QtWidgets
import qdarkstyle
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from dataframe_widget import *
from feature_widgets import *
from custom_widgets import *




class dragableListWidget(QListWidget):
    def __init__(self , df):
        super().__init__()
        self.setAcceptDrops(True)
        self.df = df
        self.initUI()
        

    def initUI(self):
        self.setStyleSheet("max-width: 150px;")
        for column in self.df.dataframe.columns:
            item = QListWidgetItem(column)
            
            self.setDragDropMode(QAbstractItemView.InternalMove)
            
            self.addItem(item)

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
        self.mainLayout = QHBoxLayout()
        self.column0Layout = QVBoxLayout()
        self.column1Layout = QVBoxLayout()
        self.column2Layout = QVBoxLayout()
        self.df_widget = None
        self.imputewidget = None

        self.initUI()

    def initUI(self):
        # Create the main layout

        
        
        select_button = Button('Select File')
        select_button.clicked.connect(self.set_df)
        self.column1Layout.addWidget(select_button)

       
        self.column1Layout.addWidget(QCheckBox('Drop Duplicates'))
      
        impute_checkbox = QCheckBox('Impute Missing Values')
        self.column1Layout.addWidget(impute_checkbox)
        impute_checkbox.stateChanged.connect(lambda:self.impute_dataframe(impute_checkbox))


        # Create an empty QTableWidget
        self.empty_table = QTableWidget()
        self.empty_table.setRowCount(0)
        self.empty_table.setColumnCount(0)
        
        
        # Add the empty table to column2Layout
        self.column2Layout.addWidget(self.empty_table)

     
       
        
        self.column1Layout.setAlignment(Qt.AlignTop)


        # Add columns to the main layout
        self.mainLayout.addLayout(self.column0Layout)
        self.mainLayout.addLayout(self.column1Layout)
        self.mainLayout.addLayout(self.column2Layout)
        

        # Set the main layout for the window
        self.setLayout(self.mainLayout)

        # Set the window properties
        self.setWindowTitle('Pivot')
        self.setGeometry(300, 100, 1000, 600)
    
    def create_impute_widget(self):
        if self.df is None:
            return None
        self.column1Layout.removeWidget(self.imputewidget)
        
        self.imputewidget = imputeWidget(self.df , parent=self)
        self.imputewidget.hide()
        self.column1Layout.addWidget(self.imputewidget)
    def create_list(self):
        if self.df is None:
            return None
        self.column0Layout.removeWidget(dragableListWidget(self.df))
        self.column0Layout.addWidget(dragableListWidget(self.df))

    def set_df(self):
        file_path, _ = QFileDialog().getOpenFileName()
        self.df = dataframe(file_path)

        
        self.create_table()
        self.create_impute_widget()
        self.create_list()

    
    def create_table(self):
        if self.df is None:
            return None
        
        while self.column2Layout.count():
            child = self.column2Layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.df_widget = tableWidget(self.df.dataframe)
        self.column2Layout.addWidget(self.df_widget)
    
    def impute_dataframe(self , checkbox):

        if self.df is None:
            return None
        if checkbox.isChecked():
            self.imputewidget.show()
        else:
            self.imputewidget.hide()
        

            


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TwoColumnWindow()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window.show()
    sys.exit(app.exec_())
