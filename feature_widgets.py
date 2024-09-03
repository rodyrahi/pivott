from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

import json
from custom_widgets import *
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder
import numpy as np
import pandas as pd


def inArray(parent , column):
    for l in parent:
        if str(l[0]) == column:
            return l
         
    return None


class featureWidget(QWidget):
    def __init__(self, df, parent):
        super().__init__()
        self.setAcceptDrops(True)
        self.df = df
        self.parent = parent
        self.feature_label = QLabel("feature")
        
        self.initUI()

    def initUI(self):
        
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setAcceptDrops(True)
        
        
        self.scroll_layout = QVBoxLayout(scroll_widget)
        # self.scroll_layout.addLayout(hbox)
        
            
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        self.main_layout = QVBoxLayout(self)
        
        
        self.main_layout.addWidget(self.feature_label)

        self.main_layout.addWidget(scroll_area)
        scroll_area.setAcceptDrops(True)
        # self.setMaximumSize(350, 300)
        # self.setMinimumSize(350, 200)
        self.setAcceptDrops(True)
        
        self.setLayout(self.main_layout)

    def read_json(self):
        with open(self.parent.projectpath, 'r') as file:
            return json.load(file)

    def Write_json(self , jsonfile):

        with open(self.parent.projectpath, 'w') as file:
                return json.dump(jsonfile, file ) 
          
        

    def dropduplicateUI(self):
        duplicatecol = feature("All" , self , self.drop_duplicate_all)
        duplicatecol.dropduplicate_col()
        self.parent.duplicate_checkboxes.append(duplicatecol)
        duplicate_cb = duplicatecol.checkbox
        duplicate_cb.stateChanged.connect(lambda state , col="All" , checkbox=duplicate_cb: self.drop_duplicate_all(state , checkbox ,col))
        self.scroll_layout.addLayout(duplicatecol.hbox)
    
    def imputeUI(self):
        
        all_na_cols = self.df.dataframe.columns[self.df.dataframe.isna().any()].tolist()
        for column in all_na_cols:
            imputecol = feature(column, self, self.impute_column)
            imputecol.impute_col()
            self.parent.impute_checkboxes.append(imputecol)
            impute_cb = imputecol.checkbox
            impute_cb.stateChanged.connect(lambda state, col=column, combo=imputecol.strategy_combo, checkbox=impute_cb: self.impute_column(state, column=col, checkbox=checkbox, strategy=combo.currentText()))
            
            self.scroll_layout.addLayout(imputecol.hbox)



        

    def dropnaUI(self):
        allcolumns = ["All"]+self.df.dataframe.columns[self.df.dataframe.isna().any()].tolist()
        for column in allcolumns:
            dropnacol = feature(column , self , self.drop_columnna )
            dropnacol.dropna_col()
            self.parent.dropna_checkboxes.append(dropnacol)


            dropnacol.checkbox.stateChanged.connect(lambda state , checkbox=dropnacol.checkbox, col=column : self.drop_columnna( state, checkbox , col))
            self.scroll_layout.addLayout(dropnacol.hbox)

    def encodeUI(self):
        allcolumns = self.df.dataframe.columns
        for column in allcolumns:
            encodecol = feature(column , self , self.encode_column)
            encodecol.encode_col()
            self.parent.encode_checkboxes.append(encodecol)

            encodecol.checkbox.stateChanged.connect(lambda state , checkbox=encodecol.checkbox, col=column : self.encode_column( state, checkbox , col))
            self.scroll_layout.addLayout(encodecol.hbox)
    
    def dropcolUI(self):
        allcolumns = self.df.dataframe.columns
        for column in allcolumns:

            dropcol = feature(column , self , self.drop_column)
            dropcol.drop_col()
            self.parent.dropcol_checkboxes.append(dropcol)

            dropcol.checkbox.stateChanged.connect(lambda state , checkbox=dropcol.checkbox, col=column : self.drop_column( state, checkbox , col))
            self.scroll_layout.addLayout(dropcol.hbox)

    def outlierUI(self):
        allcolumns = self.df.dataframe.columns
        for column in allcolumns:

            outliercol = feature(column , self , self.outlier_column)
            outliercol.outlier_col()
            self.parent.outlier_checkboxes.append(outliercol)

            outliercol.checkbox.stateChanged.connect(lambda state , checkbox=outliercol.checkbox,list = outliercol.method ,col=column : self.outlier_column( state, checkbox ,list.currentText() , col))
            self.scroll_layout.addLayout(outliercol.hbox)


    def impute_column(self , state , checkbox , column, strategy):
        
        if checkbox.isChecked():
            
            jsonfile = self.read_json()

            try:
                if not column in jsonfile["impute"]["col"] and not strategy in jsonfile["impute"]["strategy"]:
                    
                    jsonfile["impute"]["col"].append(column)
                    jsonfile["impute"]["strategy"].append(strategy)
            except:
            
                jsonfile["impute"] = {"col":[column], "strategy":[strategy]}


            self.Write_json(jsonfile)

            
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

                        

            
        else: 
            col = inArray(self.parent.unchecked, column+'impute')
            if col:
              
                self.df.dataframe[column] = col[1][column]
                self.parent.df.dataframe = self.df.dataframe
                self.parent.create_table()

                jsonfile = self.read_json()

                
                index = jsonfile["impute"]["col"].index(column)

                jsonfile["impute"]["col"].remove(column)
                del jsonfile["impute"]["strategy"][index]

                self.Write_json(jsonfile)

    def imputecol(self , imputer , column):
        
        imputer.fit(self.df.dataframe[[column]])
        self.df.dataframe[column] = imputer.transform(self.df.dataframe[[column]]).ravel() 


    def drop_columnna(self , state , checkbox ,column):

        if checkbox.isChecked():

            jsonfile = self.read_json()

            try:
                if not column in jsonfile["dropna"]["col"] :
                    
                    jsonfile["dropna"]["col"].append(column)
                    
            except:
            
                jsonfile["dropna"] = {"col":[column]}



            self.Write_json(jsonfile)    

            if column == "All":


                if checkbox.save_unchecked(self.parent , self.df , column , 'dropna'):
                    self.dropna_all()
                    self.parent.df.dataframe = self.df.dataframe
                    self.parent.create_table()

            else:
                if checkbox.save_unchecked(self.parent , self.df , column , 'dropna'):
                    self.dropna_col(column)

                    self.parent.df.dataframe = self.df.dataframe
                    self.parent.create_table()

        else:
            col = inArray(self.parent.unchecked, column+'dropna')
            if col:

                diff = col[1][~col[1].index.isin(self.df.dataframe.index )]
                print(diff) 
                self.df.dataframe = pd.concat( [self.df.dataframe, diff], ignore_index=True)

                self.parent.df.dataframe = self.df.dataframe
                self.parent.create_table()
            
                jsonfile = self.read_json()
                jsonfile["dropna"]["col"].remove(column)
                self.Write_json(jsonfile)




    def dropna_all(self):
        self.df.dataframe = self.df.dataframe.dropna()
    
    def dropna_col(self , col):
        print("test")
        self.df.dataframe = self.df.dataframe.dropna(subset=[col])

    def encode_column(self , state , checkbox ,column):

        if checkbox.isChecked():
                
                jsonfile = self.read_json()
                try:
                    if not column in jsonfile["enocde"]["col"]:
                        jsonfile["encode"]["col"].append(column)
                except:
                
                    jsonfile["encode"] = {"col":[column]}


                self.Write_json(jsonfile)






                if checkbox.save_unchecked(self.parent , self.df , column , 'encode'):
                    self.encode_col(column)

                    self.parent.df.dataframe[column] = self.df.dataframe[column]
                    self.parent.create_table()

        else:
            col = inArray(self.parent.unchecked, column+'encode')
            if col:
                
                self.df.dataframe[column] = col[1][column]
                self.parent.df.dataframe = self.df.dataframe
                self.parent.create_table()


                jsonfile = self.read_json()
                jsonfile["encode"]["col"].remove(column)
                self.Write_json(jsonfile)



    
    def encode_col(self , col):
        le = LabelEncoder()
        
        self.df.dataframe[col] = le.fit_transform(self.df.dataframe[col])

    def drop_column(self , state , checkbox ,column):

        if checkbox.isChecked():

            jsonfile = self.read_json()
            try:
                if not column in jsonfile["dropcol"]["col"]:
                    jsonfile["dropcol"]["col"].append(column)
            except:
                jsonfile["dropcol"] = {"col":[column]}
            self.Write_json(jsonfile)


            if checkbox.save_unchecked(self.parent , self.df , column , 'dropcol'):
                self.drop_col(column)

                self.parent.df.dataframe = self.df.dataframe
                self.parent.create_table()
        else:
            col = inArray(self.parent.unchecked, column+'dropcol')
            if col:

                self.df.dataframe[column] = col[1][column]
                self.parent.df.dataframe = self.df.dataframe
                self.parent.create_table()


                jsonfile = self.read_json()
                jsonfile["dropcol"]["col"].remove(column)
                self.Write_json(jsonfile)
    def drop_col(self , col):
        self.df.dataframe = self.df.dataframe.drop(col, axis=1)

    def outlier_column(self , state , checkbox ,list ,column):

        print(checkbox.isChecked())

        if checkbox.isChecked():

            jsonfile = self.read_json()
            try:
                if not column in jsonfile["outlier"]["col"]:
                    jsonfile["outlier"]["col"].append(column)
                    jsonfile["outlier"]["method"].append(list)
            except:
                jsonfile["outlier"] = {"col":[column], "method":[list]}
            self.Write_json(jsonfile)

            if list == "IQR":
                if checkbox.save_unchecked(self.parent , self.df , column , 'outlier'):
 
                    self.outlier_IQR(column)

                    # self.parent.df.dataframe = self.df.dataframe

                    self.parent.df.dataframe[column] = self.df.dataframe[column]
                    self.parent.create_table()
            
        else:
            
            col = inArray(self.parent.unchecked, column+'outlier')
            if col:
                
              
                diff = col[1][~col[1].index.isin(self.df.dataframe.index )]
                print(diff) 
                self.df.dataframe = pd.concat( [self.df.dataframe, diff], ignore_index=True)

                self.parent.df.dataframe = self.df.dataframe
                self.parent.create_table()





                jsonfile = self.read_json()
                
                index = jsonfile["outlier"]["col"].index(column)

                jsonfile["outlier"]["col"].remove(column)
                print(index)
                del jsonfile["outlier"]["method"][index]

                self.Write_json(jsonfile)

                
    def outlier_IQR(self , col):
        q1 = self.df.dataframe[col].quantile(0.25)
        q3 = self.df.dataframe[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)
        outliers = self.df.dataframe[(self.df.dataframe[col] < lower_bound) | (self.df.dataframe[col] > upper_bound)]
        print(outliers)
        self.df.dataframe = self.df.dataframe.drop(outliers.index)
    
    def drop_duplicate_all(self , state , checkbox ,column):


        if checkbox.isChecked():
            jsonfile = self.read_json()
            try:
                if not column in jsonfile["dropduplicates"]["col"]:
                    jsonfile["dropduplicates"]["col"].append(column)
            except:
                jsonfile["dropduplicates"] = {"col":[column]}
            self.Write_json(jsonfile)

            if checkbox.save_unchecked(self.parent , self.df , column , 'dropduplicates'):
        
                self.drop_duplicates()

                # self.parent.df.dataframe = self.df.dataframe
                self.parent.df.dataframe = self.df.dataframe
                self.parent.create_table()

        else:
            col = inArray(self.parent.unchecked, column+'dropduplicates')
            if col:

                self.df.dataframe= col[1]
                self.parent.df.dataframe = self.df.dataframe
                self.parent.create_table()


                jsonfile = self.read_json()
                jsonfile["dropduplicates"]["col"].remove(column)
                self.Write_json(jsonfile)

    
    def drop_duplicates(self):
        self.df.dataframe = self.parent.df.dataframe.drop_duplicates()
