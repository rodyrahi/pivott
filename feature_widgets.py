from PyQt5.QtCore import *
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
        
        all_na_cols = self.df.dataframe.columns[self.df.dataframe.isna().any()].tolist()
      

        for column in all_na_cols:
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
            hbox.setAlignment(Qt.AlignTop)
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
            
            
            
            
          
           
            column_found = next((l for l in self.parent.unchecked if str(l[0]) == column), None)
            if column_found is None:
                self.parent.unchecked.append((column, self.df.dataframe.copy()))

                imputer.fit(self.df.dataframe[[column]])
                self.df.dataframe[column] = imputer.transform(self.df.dataframe[[column]]).ravel()        

                self.parent.df = self.df
                self.parent.create_table()

                

            

            column_found1 = next((i for i in self.parent.checked if str(i[0]) == column), None)
            if column_found1 is None:
                self.parent.checked.append((column, self.df.dataframe.copy()))
            else:
               
                self.df.dataframe = column_found1[1]
                self.parent.df.dataframe = self.df.dataframe
                self.parent.create_table()
               
            
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

        allcolumns = ["All"]+self.df.dataframe.columns[self.df.dataframe.isna().any()].tolist()
      
        for column in allcolumns:

           
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


