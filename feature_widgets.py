from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import json
from custom_widgets import *
from sklearn.impute import SimpleImputer
import numpy as np


def inArray(parent , column):
    for l in parent:
        if str(l[0]) == column:
            return l
         
    return None


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
            
            # hbox = QHBoxLayout()
            # label = QLabel(column)
            # impute_checkbox = SQCheckBox("Impute")


            # hbox.addWidget(label)
            # strategy_combo = QComboBox()
            # strategy_combo.addItems(['mean', 'median', 'most_frequent', 'constant'])
            # strategy_combo.setEditable(True)
            # hbox.addWidget(strategy_combo)
            

                
            # self.parent.impute_checkboxes.append()
            # hbox.addWidget(impute_checkbox)

            imputecol = impute_col(column , self)
            self.parent.impute_checkboxes.append(imputecol)
            impute_cb = imputecol.impute_checkbox
            

            impute_cb.stateChanged.connect(lambda  state ,   col=column, combo=imputecol.strategy_combo , checkbox= impute_cb: self.impute_column( state , checkbox ,col, combo.currentText()))
            
            layout.addLayout(imputecol.hbox)        

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        main_layout = QVBoxLayout(self)
        

        main_layout.addWidget(scroll_area)
        scroll_area.setAcceptDrops(True)
        self.setMaximumSize(300, 300)
        self.setAcceptDrops(True)
        
        self.setLayout(main_layout)
        
        
 

    def impute_column(self , state , checkbox ,column, strategy):
        
        with open(self.parent.projectpath, 'r') as file:
            jsonfile = json.load(file)

        try:
            if not column in jsonfile["impute"]["col"] and not strategy in jsonfile["impute"]["strategy"]:
                
                jsonfile["impute"]["col"].append(column)
                jsonfile["impute"]["strategy"].append(strategy)
        except:
        
            jsonfile["impute"] = {"col":[column], "strategy":[strategy]}


        # elif not column in jsonfile["impute"]["col"]:
        #     jsonfile["impute"]["col"].append(column)
        #     jsonfile["impute"]["strategy"].append(strategy)

        # if not jsonfile["impute"]["col"]:
        #     jsonfile["impute"] = {"col":[column], "strategy":[strategy]}
        # else:

        #     jsonfile["impute"]["col"].append(column)
        #     jsonfile["impute"]["strategy"].append(strategy)

        with open(self.parent.projectpath, 'w') as file:
            json.dump(jsonfile, file ) 

        if checkbox.isChecked():
            
            if strategy == 'constant':
                fill_value = 0  # You can modify this to allow user input
                imputer = SimpleImputer(missing_values=np.nan, strategy=strategy, fill_value=fill_value)
            elif strategy in ['mean','median','most_frequent']:
                imputer = SimpleImputer(missing_values=np.nan, strategy=strategy)
            else:
                imputer = SimpleImputer(missing_values=np.nan, strategy='constant', fill_value=strategy)
            
            
            
            
          
           
            
            if checkbox.save_unchecked(self.parent , self.df , column , 'impute'):

                imputer.fit(self.df.dataframe[[column]])
                self.df.dataframe[column] = imputer.transform(self.df.dataframe[[column]]).ravel()        

                self.parent.df.dataframe[column] = self.df.dataframe[column]
                self.parent.create_table()

                

            column_found1 = checkbox.save_checked(self.parent , self.df , column , 'impute')
            print(column_found1)
            if column_found1:

                self.df.dataframe[column] = column_found1[1][column]
                self.parent.df.dataframe = self.df.dataframe
                self.parent.create_table()
               
            
        else: 
            col = inArray(self.parent.unchecked, column+'impute')
            if col:

                self.df.dataframe[column] = col[1][column]
                self.parent.df.dataframe = self.df.dataframe
                self.parent.create_table()
                

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


class outlierWidget(QWidget):
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
        
        cols = self.df.dataframe.columns
      
        print(cols)
        for column in cols:
            current_df = self.df
            hbox = QHBoxLayout()

            hbox.addWidget(QLabel(column))
    
            strategy_combo = QComboBox()
            strategy_combo.addItems(['IQR', 'Z-Score'])
            strategy_combo.setEditable(True)
            hbox.addWidget(strategy_combo)
            
            cap_checkbox = SQCheckBox("cap")
                
            
           
                

            hbox.addWidget(cap_checkbox)
            cap_checkbox.stateChanged.connect(lambda  checkbox= cap_checkbox,  col=column, combo=strategy_combo: self.cap_column( checkbox ,col, combo.currentText()))
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
        
        


    def cap_column(self  , checkbox ,column, strategy):
        
       
        
         
        if checkbox.isChecked():
            
            if strategy == 'IQR':
                fill_value = 0  
                imputer = SimpleImputer(missing_values=np.nan, strategy=strategy, fill_value=fill_value)
            elif strategy == 'Z-Score':
                imputer = SimpleImputer(missing_values=np.nan, strategy=strategy)
            else:
                imputer = SimpleImputer(missing_values=np.nan, strategy='constant', fill_value=strategy)
            
            
            
            
          
           
            
            if checkbox.save_unchecked(self.parent , self.df , column , 'impute'):

                imputer.fit(self.df.dataframe[[column]])
                self.df.dataframe[column] = imputer.transform(self.df.dataframe[[column]]).ravel()        

                self.parent.df.dataframe[column] = self.df.dataframe[column]
                self.parent.create_table()

                

            column_found1 = checkbox.save_checked(self.parent , self.df , column , 'impute')
            print(column_found1)
            if column_found1:

                self.df.dataframe[column] = column_found1[1][column]
                self.parent.df.dataframe = self.df.dataframe
                self.parent.create_table()
               
            
        else: 
            col = inArray(self.parent.unchecked, column+'impute')
            if col:

                self.df.dataframe[column] = col[1][column]
                self.parent.df.dataframe = self.df.dataframe
                self.parent.create_table()