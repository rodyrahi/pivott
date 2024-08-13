from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import json
from custom_widgets import *
from sklearn.impute import SimpleImputer
import numpy as np
import pandas as pd


def inArray(parent , column):
    for l in parent:
        if str(l[0]) == column:
            return l
         
    return None


# class save_checkbox():
#     def __init__(self , checkbox , column , func , feature):





   


    



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
            
          
            imputecol = impute_col(column , self)
            self.parent.impute_checkboxes.append(imputecol)
            impute_cb = imputecol.impute_checkbox
            

            impute_cb.stateChanged.connect(lambda  state ,   col=column, combo=imputecol.strategy_combo , checkbox= impute_cb: self.impute_column( state , column=col , checkbox=checkbox, strategy= combo.currentText()))
            
            layout.addLayout(imputecol.hbox)        

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        main_layout = QVBoxLayout(self)
        

        main_layout.addWidget(scroll_area)
        scroll_area.setAcceptDrops(True)
        self.setMaximumSize(300, 300)
        self.setAcceptDrops(True)
        
        self.setLayout(main_layout)
        
        
 

    def impute_column(self , state , checkbox , column, strategy):
        
       
        
        print(column , "impute is ran")

        if checkbox.isChecked():
            
            with open(self.parent.projectpath, 'r') as file:
                jsonfile = json.load(file)

            try:
                if not column in jsonfile["impute"]["col"] and not strategy in jsonfile["impute"]["strategy"]:
                    
                    jsonfile["impute"]["col"].append(column)
                    jsonfile["impute"]["strategy"].append(strategy)
            except:
            
                jsonfile["impute"] = {"col":[column], "strategy":[strategy]}


            with open(self.parent.projectpath, 'w') as file:
                json.dump(jsonfile, file ) 

            
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

                        

            # column_found1 = checkbox.save_checked(self.parent , self.df , column , 'impute')
            # if column_found1:
            #     print("3")
            #     self.df.dataframe[column] = column_found1[1][column]
            #     self.parent.df.dataframe = self.df.dataframe
            #     self.parent.create_table()
            
        else: 
            col = inArray(self.parent.unchecked, column+'impute')
            if col:
              
                self.df.dataframe[column] = col[1][column]
                self.parent.df.dataframe = self.df.dataframe
                self.parent.create_table()

            with open(self.parent.projectpath, 'r') as file:
                jsonfile = json.load(file)
                
                index = jsonfile["impute"]["col"].index(column)

                jsonfile["impute"]["col"].remove(column)
                del jsonfile["impute"]["strategy"][index]

            with open(self.parent.projectpath, 'w') as file:
                json.dump(jsonfile, file ) 



    def imputecol(self , imputer , column):
        
        imputer.fit(self.df.dataframe[[column]])
        self.df.dataframe[column] = imputer.transform(self.df.dataframe[[column]]).ravel()        

        
                

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

           
            dropnacol = dropna_col(column , self)

            dropnacol.dropna_checkbox.stateChanged.connect(lambda state , checkbox=dropnacol.dropna_checkbox, col=column : self.drop_columnna( state, checkbox , col))
    
            layout.addLayout(dropnacol.hbox)        

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        scroll_area.setAcceptDrops(True)
        self.setMaximumSize(300, 300)
        self.setAcceptDrops(True)
        self.setLayout(main_layout)
        


    def drop_columnna(self , state , checkbox ,col):

        if checkbox.isChecked():
            if col == "All":
                # dropall = self.drop_all(" ")
                if checkbox.save_unchecked(self.parent , self.df , col , 'dropna'):
                    self.drop_all(" ")
                    self.parent.df.dataframe = self.df.dataframe
                    self.parent.create_table()


                # save_checkbox(self , checkbox , col , dropall , 'dropna')
            else:
                if checkbox.save_unchecked(self.parent , self.df , col , 'dropna'):
                    self.drop_col(col)
                    # difference = self.parent.df.dataframe != self.df.dataframe

                    self.parent.df.dataframe = self.df.dataframe
                    self.parent.create_table()

        else:
            col = inArray(self.parent.unchecked, col+'dropna')
            if col:

                # Identify rows in col[1] that are not in self.df.dataframe based on the index
                diff = col[1][~col[1].index.isin(self.df.dataframe.index )]
                print(diff) 

                # Concatenate the new rows to self.df.dataframe, ensuring indices are aligned
                self.df.dataframe = pd.concat([self.df.dataframe, diff], ignore_index=True)

                self.parent.df.dataframe = self.df.dataframe
                self.parent.create_table()


        # self.parent.df = self.df
        # self.parent.create_table()

    def drop_all(self , all):
        self.df.dataframe = self.df.dataframe.dropna()
    
    def drop_col(self , col):
        print("test")
        self.df.dataframe = self.df.dataframe.dropna(subset=[col])







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