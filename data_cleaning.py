
import json
import sys
from PyQt6.QtWidgets import *

import pandas as pd
import glob
import os
from maincolumns import *
from sklearn.impute import SimpleImputer



class DataCleaningWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        self.current_df = ["./test_files/df.parquet"]
        self.initui()



    def initui(self):

        df = pd.read_parquet(self.current_df[-1])
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.dropna_checkbox = QCheckBox("Drop NA values")
        layout.addWidget(self.dropna_checkbox)
        self.dropna_checkbox.stateChanged.connect(lambda  :self.drop_na(self.dropna_checkbox.isChecked()))
        
      

        self.dropcol_checkbox = QCheckBox("Drop columns")
        layout.addWidget(self.dropcol_checkbox)
        
        self.impute_checkbox = QCheckBox("Impute missing values")
        layout.addWidget(self.impute_checkbox)
        self.impute_checkbox.stateChanged.connect(lambda  :self.impute_mising( state= self.impute_checkbox.isChecked(), cols= ["Legislative District"] , strategy= "mean"))



    def drop_na(self , state , cols=None , name = "dropna" ):
        df = pd.read_parquet(self.current_df[-1])
        
        if state:
            self.dropna_checkbox.setChecked(True)
            if not os.path.exists(f"df_{name}.parquet") and f"df_{name}.parquet" not in self.current_df[-1]:
                
                if cols:
                    modified_df = df.dropna(subset=cols)
                else:
                    modified_df = df.dropna()

                self.save_parquet_file(df, name)
                print(self.current_df)
                return modified_df
            
        else:
            if  f"df_{name}.parquet" in self.current_df[-1] :
                self.current_df.remove(self.current_df[-1])
                os.remove(f"./test_files/df_{name}.parquet")
                print(self.current_df)
                return self.current_df[-1]
            
            else:
                for i in self.current_df:
                    if i.endswith(f"_{name}.parquet"):
                        self.current_df.remove(i)
        return df

    def drop_col( self ,  df, cols):
        return df.drop(columns=cols)

    def impute_mising(self , state ,cols, strategy , name = "impute"):
        # pass
        df = pd.read_parquet(self.current_df[-1])
        
        
        if state:
            
            self.impute_checkbox.setChecked(True)

            if not os.path.exists(f"df_{name}.parquet") and f"df_{name}.parquet" not in self.current_df[-1]:
                
                imputer = SimpleImputer(strategy=strategy)
                df[cols] = imputer.fit_transform(df[cols])
                
                self.save_parquet_file(df, name)
                print(self.current_df)
                return df
        else:
            if  f"df_{name}.parquet" in self.current_df[-1] :
                self.current_df.remove(self.current_df[-1])
                os.remove(f"./test_files/df_{name}.parquet")
                print(self.current_df)
                return self.current_df[-1]

        return df
    def save_parquet_file(self , df, suffix, base_path="./test_files/df.parquet"):


        filepath = base_path.replace(".parquet", f"_{suffix}.parquet")

        # Remove the file if it exists
        if os.path.exists(filepath):
            os.remove(filepath)

        df.to_parquet(filepath)


        # global current_df
        self.current_df.append(filepath)

        print(f"File saved as {filepath}")

    def process_file( self ,csv_filepath, parquet_filepath="./test_files/df.parquet", config=None):
        
        
        config = csv_filepath

        # Step 1: Read and save the CSV as a Parquet file
        # self.read_save_file(csv_filepath, parquet_filepath)

        # Step 2: Apply operations based on the config
        for operation, details in config.items():
            
            df = pd.read_parquet(self.current_df[-1])  # Read the parquet file at each step
            
            if operation == "dropna":
                cols = details.get("col", None)
                df = self.drop_na(cols)

                # self.save_parquet_file(df, "dropna")

            elif operation == "dropcol":
                cols = details.get("col", [])
                df = self.drop_col(df, cols)
                # self.save_parquet_file(df, "dropcol")
            
            elif operation == "impute":
                cols = details.get("col", [])
                strategy = details.get("strategy", "mean")
                df = self.impute_mising(state=True, cols=cols, strategy=strategy)
                # self.save_parquet_file(df, f"impute_{strategy}")

            print(f"Shape after {operation}: {df.shape}")
        
