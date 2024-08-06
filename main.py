import sys
from PySide2 import QtWidgets
import qdarkstyle
from PyQt5.QtWidgets import *
from dataframe_widget import *
from impute_widget import *
from custom_widgets import *

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

        layout.addWidget(self.tableWidget)
        self.setLayout(layout)
        self.setWindowTitle('DataFrame Viewer')




class TwoColumnWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.df = None
        self.mainLayout = QHBoxLayout()
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

     
       
        
        

        # Add columns to the main layout
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
        
        self.imputewidget = imputeWidget(self.df.dataframe)
        self.imputewidget.hide()
        self.column1Layout.addWidget(self.imputewidget)


    def set_df(self):
        file_path, _ = QFileDialog().getOpenFileName()
        self.df = dataframe(file_path)
        self.create_table()
        self.create_impute_widget()

    
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

    # app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
   
    window.show()
    sys.exit(app.exec_())
