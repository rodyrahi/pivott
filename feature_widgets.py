from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from PyQt5.QtWidgets import *
from custom_widgets import *
from sklearn.impute import SimpleImputer
import numpy as np

class imputeWidget(QWidget):
    def __init__(self, df, parent):
        super().__init__()
        self.setAcceptDrops(True)
        self.df = df
        self.parent = parent
        self.initUI()
    
    def initUI(self):
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.acceptDrops = True
        layout = QVBoxLayout(scroll_widget)
        for column in self.df.dataframe.columns:
            current_df = self.df
            hbox = QHBoxLayout()

            hbox.addWidget(QLabel(column))
    
            strategy_combo = QComboBox()
            strategy_combo.addItems(['mean', 'median', 'most_frequent', 'constant'])
            strategy_combo.setEditable(True)
            hbox.addWidget(strategy_combo)
            
            impute_checkbox = SQCheckBox("Impute")
            
            
           
                

            hbox.addWidget(impute_checkbox)
            impute_checkbox.stateChanged.connect(lambda current_df=current_df,  checkbox= impute_checkbox,  col=column, combo=strategy_combo: self.impute_column( checkbox ,col, combo.currentText()))
    
            layout.addLayout(hbox)        

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        scroll_area.setAcceptDrops(True)
        self.setMaximumSize(300, 300)
        self.setAcceptDrops(True)
        self.setLayout(main_layout)
        
        


    def impute_column(self  , checkbox ,column, strategy):
        
       

         
        if checkbox.isChecked():
            
            if strategy == 'constant':
                fill_value = 0  # You can modify this to allow user input
                imputer = SimpleImputer(missing_values=np.nan, strategy=strategy, fill_value=fill_value)
            elif strategy in ['mean','median','most_frequent']:
                imputer = SimpleImputer(missing_values=np.nan, strategy=strategy)
            else:
                imputer = SimpleImputer(missing_values=np.nan, strategy='constant', fill_value=strategy)
            
            
            
            
            # if (column , self.df.dataframe.copy()) not in self.parent.unchecked:
            #     self.parent.unchecked.append((column, self.df.dataframe.copy()))
           
            column_found = next((l for l in self.parent.unchecked if str(l[0]) == column), None)
            if column_found is None:
                self.parent.unchecked.append((column, self.df.dataframe.copy()))

            print(self.parent.unchecked)            

            imputer.fit(self.df.dataframe[[column]])
            self.df.dataframe[column] = imputer.transform(self.df.dataframe[[column]]).ravel()        

            self.parent.df = self.df
            self.parent.create_table()

            column_found = next((i for i in self.parent.checked if str(i[0]) == column), None)
            if not column_found:
                self.parent.checked.append((column, self.df.dataframe.copy()))
            
        else: 
            for i in self.parent.unchecked:
                if str(i[0]) == column:
                    self.df.dataframe = i[1]
                    self.parent.df.dataframe = self.df.dataframe
                    self.parent.create_table()
                    break
        


class dropnaWidget(QWidget):
    def __init__(self, df, parent):
        super().__init__()
        self.setAcceptDrops(True)
        self.df = df
        self.parent = parent
        self.initUI()
    
    def initUI(self):
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.acceptDrops = True
        layout = QVBoxLayout(scroll_widget)

        allcolumns = ["All"]+self.df.dataframe.columns.tolist()

        for column in allcolumns:

            columnname = column
            hbox = QHBoxLayout()

            hbox.addWidget(QLabel(column))
    
    
            impute_button = Button("Dropna Rows")
            hbox.addWidget(impute_button)

            impute_button.clicked.connect(lambda checked, col=column : self.drop_columnna(col))
    
            layout.addLayout(hbox)        

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        scroll_area.setAcceptDrops(True)
        self.setMaximumSize(300, 300)
        self.setAcceptDrops(True)
        self.setLayout(main_layout)
        


    def drop_columnna(self ,col):

        if col == "All":
            self.df.dataframe = self.df.dataframe.dropna()
        else:
            self.df.dataframe = self.df.dataframe.dropna(subset=[col])
        self.parent.df = self.df
        self.parent.create_table()


