import gc
import json
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import os
import glob
import numpy as np
import pandas as pd
import polars as pl


from sklearn.calibration import LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OrdinalEncoder


from custom_widgets import smallButton
from file_functions import read_save_parquet , df_from_parquet , save_parquet_file, create_final_df , read_json_file , \
    update_remove_json_file


def set_df(df , main_interface):
    if not df is None:
        final_df = main_interface.current_df[0].replace("df.parquet" , "final_df.parquet")
        if os.path.exists(final_df):
            df = df_from_parquet(final_df)
    else:    
        df = df_from_parquet(main_interface.current_df[0])
    
    return df

def on_uncheck_checkbox(main_interface , name=None , strategy=None):
    
    print("not checked")

    for i in main_interface.current_df:
        
        if f"df_{name}.parquet" in i:
            main_interface.current_df.remove(i)
            if os.path.exists(i):
                os.remove(i)


    create_final_df(main_interface , main_interface.main_df)
    main_interface.update_table()

    
    update_remove_json_file(main_interface , name , strategy)



checkbox_map = {}



class featureWidget(QWidget):
    def __init__(self, main_interface):
        super().__init__()
        self.main_interface = main_interface
        self.columns = []



    def disable_checkbox(self, column_name, action_type):
        key = (action_type, column_name)
        if key in checkbox_map:
            checkbox = checkbox_map[key]
            checkbox.setEnabled(False)
        else:
            print(f"No checkbox found for action '{action_type}' on column: {column_name}")

    def enable_checkbox(self, column_name, action_type):
        key = (action_type, column_name)
        if key in checkbox_map:
            checkbox = checkbox_map[key]
            checkbox.setEnabled(True)
        else:
            print(f"No checkbox found for action '{action_type}' on column: {column_name}")


class imputeMissingWidget(featureWidget):
    def __init__(self, main_interface):
        super().__init__(main_interface)
      
    def initUI(self):
        layout = QVBoxLayout()
        print(self.main_interface.current_df)
        
       
        # final_df = self.main_interface.current_df[0].replace("df.parquet", "final_df.parquet")
        # if os.path.exists(final_df):
        #     final_df = df_from_parquet(final_df)
        # else:
        #     final_df = df_from_parquet(self.main_interface.current_df[0])
        

        final_df = self.main_interface.main_df
        columns = final_df.select(pl.all().is_null().any()).columns
        print(columns)

        for col in columns:
            row_layout = QHBoxLayout()
            
            col_label = QLabel(col[:20] + '...' if len(col) > 20 else col)
            row_layout.addWidget(col_label)
            
            strategy_combo = QComboBox()
            strategy_combo.addItems(["mean", "median", "most_frequent", "constant"])
            strategy_combo.setCurrentIndex(0) 
        
            checkbox = QCheckBox("Impute")
            checkbox.stateChanged.connect(lambda state, c=col, s=strategy_combo: self.impute_missing(state=state, cols=[c], strategy=s.currentText()))
            
            row_layout.addWidget(strategy_combo)
            row_layout.addWidget(checkbox)
            self.main_interface.impute_checkboxes.append((f"impute", checkbox))

            checkbox_map[("impute", col)] = checkbox  # Store the checkbox in the shared map
             
            layout.addLayout(row_layout)

        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)


    def impute_missing(self, state, df=None, cols=None, strategy=None, name="impute", checkbox=None):
        df = set_df(df, self.main_interface)
        

        if state == 2 or state == True:
            print("Imputing missing values")
        
            if checkbox:
                checkbox.blockSignals(True)
                checkbox.setChecked(True)
                checkbox.blockSignals(False)
    
            imputer = SimpleImputer(strategy=strategy)
            df[cols] = imputer.fit_transform(df[cols])

            modified_df = df[cols]
            save_parquet_file(modified_df, f"{name}", self.main_interface, strategy)
            self.main_interface.update_table()
            
            print(modified_df)
   
        else:
            on_uncheck_checkbox(self.main_interface, name=f"{name}-{cols[0]}", strategy=strategy)


class dropColumnWidget(featureWidget):
    def __init__(self, main_interface):
        super().__init__(main_interface)
        self.columns_to_drop = []

    def initUI(self):
        layout = QVBoxLayout()
        print(self.main_interface.current_df)

        
        final_df = self.main_interface.main_df
        columns = final_df.columns

        for col in columns:
            row_layout = QHBoxLayout()
            
            col_label = QLabel(col[:20] + '...' if len(col) > 20 else col)
            row_layout.addWidget(col_label)
            
        
            checkbox = QCheckBox("Drop Column")
            checkbox.stateChanged.connect(lambda state , col=col : self.add_columns(col=col , state=state  ))

            row_layout.addWidget(checkbox)
            self.main_interface.drop_column_checkboxes.append((f"drop_column-{col}", checkbox))

            checkbox_map[("drop_column", col)] = checkbox  # Store the checkbox in the shared map
             

            
            layout.addLayout(row_layout)

        
  
        button_layout = QHBoxLayout()
        
        apply_button = smallButton("Apply")
        apply_button.clicked.connect(lambda: self.drop_column(state=True , cols=self.columns_to_drop))
      
        
        clear_all_button = smallButton("Clear All")

        clear_all_button.clicked.connect(self.clear_all)
        button_layout.addWidget(clear_all_button)
        button_layout.addWidget(apply_button)


        layout.addLayout(button_layout)
        

        
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)

    
    
    def add_columns(self , col , state=False):
        if state == 2 or state == True:
                
            self.columns_to_drop.append(col)
            print("col appended " , col)

            self.disable_checkbox(col , 'impute')
            self.disable_checkbox(col , 'iqr')    
        else:
            self.columns_to_drop.remove(col)
            print("col removed" , col)
            self.enable_checkbox(col , 'impute')
            self.enable_checkbox(col , 'iqr')    

    def drop_column(self, state, df=None, cols=None, strategy=None, name="drop_column", checkbox=None):
        
        df = self.main_interface.main_df

        if state == 2 or state == True :
            print("Dropping column(s)")
        
            if checkbox:
                checkbox.blockSignals(True)
                checkbox.setChecked(True)
                checkbox.blockSignals(False)
            

            if cols:
                
                cols = [col for col in cols if col in df.columns]
              
                print(df.columns)
                dropped_columns = df.select(cols)
                

                save_parquet_file(dropped_columns, f"{name}",cols , self.main_interface)
                self.main_interface.update_table()

               

                print(f"Dropped column(s): {cols}")
   
            else:
                print("uncecked")
                on_uncheck_checkbox(self.main_interface, name=f"{name}", strategy=strategy)
           
            
    def clear_all(self):
        for name, checkbox in self.main_interface.drop_column_checkboxes:
            checkbox.setChecked(False)


class removeOutlierWidget(featureWidget):
    def __init__(self, main_interface):
        super().__init__(main_interface)
        self.columns_to_remove_outliers = []

    def initUI(self):
        layout = QVBoxLayout()
        print(self.main_interface.current_df)

        final_df = self.main_interface.main_df
        columns = final_df.columns

        print("getting columns for removing outliers")
        for col in columns:
            if pl.Series(final_df[col]).dtype.is_numeric():
                row_layout = QHBoxLayout()

                col_label = QLabel(col[:20] + '...' if len(col) > 20 else col)
                row_layout.addWidget(col_label)

                method_dropdown = QComboBox()
                method_dropdown.addItems(["IQR", "Z-Score"])
                
                remove_checkbox = QCheckBox("Remove Outliers")
                remove_checkbox.stateChanged.connect(
                    lambda state, c=col, method_dropdown=method_dropdown: self.add_columns(
                        col=c, state=state, method=method_dropdown.currentText().lower()
                    )
                )
                row_layout.addWidget(method_dropdown)
                row_layout.addWidget(remove_checkbox)
                self.main_interface.remove_outlier_checkboxes.append((f"remove_outlier-{col}", remove_checkbox))

                checkbox_map[("remove_outlier", col)] = remove_checkbox  # Store in shared checkbox map
                
                layout.addLayout(row_layout)

        button_layout = QHBoxLayout()

        apply_button = smallButton("Apply")
        apply_button.clicked.connect(lambda: self.remove_outlier(state=True, cols=self.columns_to_remove_outliers))

        clear_all_button = smallButton("Clear All")
        clear_all_button.clicked.connect(self.clear_all)
        button_layout.addWidget(clear_all_button)
        button_layout.addWidget(apply_button)

        layout.addLayout(button_layout)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)

    def add_columns(self, col, state=False, method="iqr"):
        if state == 2 or state is True:
            self.columns_to_remove_outliers.append((col, method))
            print(f"Column {col} added for outlier removal using {method}")
            self.disable_checkbox(col, 'drop_column')  # Disable conflicting operations
        else:
            self.columns_to_remove_outliers = [(c, m) for c, m in self.columns_to_remove_outliers if c != col]
            print(f"Column {col} removed from outlier removal")
            self.enable_checkbox(col, 'drop_column')

    def remove_outlier(self, state, df=None, cols=None , methoh=None , name="remove_outlier", checkbox=None):
        df = self.main_interface.main_df

        if state == 2 or state is True:
            print(f"Removing outliers from columns: {cols}")
            
            if cols:
                for col, method in cols:
                    if method == 'iqr':
                        # Calculate IQR
                        Q1 = df.select(pl.col(col).quantile(0.25)).item()
                        Q3 = df.select(pl.col(col).quantile(0.75)).item()
                        IQR = Q3 - Q1
                        lower_bound = Q1 - 1.5 * IQR
                        upper_bound = Q3 + 1.5 * IQR

                        # Filter rows using Polars' .filter() method
                        modified_df = df.filter((pl.col(col) >= lower_bound) & (pl.col(col) <= upper_bound))
                    
                    elif method == 'zscore':
                        # Calculate Z-Score
                        mean = df.select(pl.col(col).mean()).item()
                        std_dev = df.select(pl.col(col).std()).item()
                        z_scores = df.with_column(((pl.col(col) - mean) / std_dev).abs().alias("z_score"))
                        
                        # Filter rows where z_score is <= 3
                        modified_df = z_scores.filter(pl.col("z_score") <= 3).drop("z_score")

                
                save_parquet_file(modified_df, f"{name}", cols ,self.main_interface, strategy=method)
                self.main_interface.update_table()

                print(f"Removed outliers from column(s): {cols} using {method}")
      
            else:
            
                on_uncheck_checkbox(self.main_interface, name=f"{name}")

    def clear_all(self):
        for name, checkbox in self.main_interface.remove_outlier_checkboxes:
            checkbox.setChecked(False)


class encodingCategoryWidget(featureWidget):
    def __init__(self, main_interface):
        super().__init__(main_interface)
        self.columns_to_encode = []
      
    def initUI(self):
        layout = QVBoxLayout()
        print(self.main_interface.current_df)
    
        # final_df = self.main_interface.current_df[0].replace("df.parquet", "final_df.parquet")
        # if os.path.exists(final_df):
        #     final_df = df_from_parquet(final_df)
        # else:
        #     final_df = df_from_parquet(self.main_interface.current_df[0])
        
        final_df = self.main_interface.main_df
        columns = final_df.schema
        columns = [col for col, dtype in columns.items() if dtype in [pl.Utf8, pl.Categorical]]

        for col in columns:
            row_layout = QHBoxLayout()
            
            col_label = QLabel(col[:20] + '...' if len(col) > 20 else col)
            row_layout.addWidget(col_label)
            
            strategy_combo = QComboBox()
            strategy_combo.addItems(["ordinal", "label" ])
            strategy_combo.setCurrentIndex(0) 
        
            checkbox = QCheckBox("Encode")
            checkbox.stateChanged.connect(lambda state, col=col, s=strategy_combo: self.add_columns(state=state, col=col , method=s.currentText().lower()))
            
            row_layout.addWidget(strategy_combo)
            row_layout.addWidget(checkbox)
            self.main_interface.encode_checkboxes.append((f"encode-{col}", checkbox))

            checkbox_map[("encode", col)] = checkbox  # Store the checkbox in the shared map
             
            layout.addLayout(row_layout)

        button_layout = QHBoxLayout()
        
        apply_button = smallButton("Apply")
        apply_button.clicked.connect(lambda: self.encode_category(state=True , cols=self.columns_to_encode , strategy=strategy_combo.currentText().lower()))
      
        
        clear_all_button = smallButton("Clear All")

        clear_all_button.clicked.connect(self.clear_all)
        button_layout.addWidget(clear_all_button)
        button_layout.addWidget(apply_button)


        layout.addLayout(button_layout)
        

        
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)

        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)


    def encode_category(self, state, df=None, cols=None, strategy=None, name="encode", checkbox=None):
        df = set_df(df, self.main_interface)
        

        if state == 2 or state == True:
            
        
            if checkbox:
                checkbox.blockSignals(True)
                checkbox.setChecked(True)
                checkbox.blockSignals(False)


            cols = [col for col, method in cols]
            if  cols:

                if strategy == "label":
                    le = LabelEncoder()
                    modified_df = pd.DataFrame(le.fit_transform(df[cols[0]]), columns=[cols[0]])
                    save_parquet_file(modified_df, f"{name}-{cols[0]}", self.main_interface, strategy)
                    self.main_interface.update_table()
                    
                elif strategy == "ordinal":
                    oe = OrdinalEncoder()
                    print(cols)
                    numpy_array = df[cols].to_numpy()

                    # Apply OrdinalEncoder and transform the column
                    encoded_array = oe.fit_transform(numpy_array)

                    # Convert the encoded result back to a Polars DataFrame
                    modified_df = pl.DataFrame({cols[0]: encoded_array.flatten()})

                    print("Encoding categorical values")
                    save_parquet_file(modified_df, f"{name}" , cols, self.main_interface, strategy)
                    self.main_interface.update_table()

            else:
                print("uncecked")
                on_uncheck_checkbox(self.main_interface, name=f"{name}")
       

    def add_columns(self, col, state=False, method=None):
        if state == 2 or state is True:
            self.columns_to_encode.append((col, method))
            print(f"Column {col} added for outlier removal using {method}")
            self.disable_checkbox(col, 'drop_column')  # Disable conflicting operations
        else:
            self.columns_to_encode = [(c, m) for c, m in self.columns_to_encode if c != col]
            print(f"Column {col} removed from outlier removal")
            self.enable_checkbox(col, 'drop_column')

    def clear_all(self):
        for name, checkbox in self.main_interface.encode_checkboxes:
            checkbox.setChecked(False)




class dropDuplicateWidget(featureWidget):
    def __init__(self , main_interface):
        super().__init__(main_interface)
        self.main_interface = main_interface
        # self.initUI()

    def initUI(self):

        layout = QVBoxLayout()
        print(self.main_interface.current_df)
        
       
           
        

        columns = self.main_interface.main_df.columns.tolist()
    
        for col in columns:
            row_layout = QHBoxLayout()
            
            # col_label = QLabel(col[:20] + '...' if len(col) > 20 else col)
            # row_layout.addWidget(col_label)
            
            strategy_combo = QComboBox()
            strategy_combo.addItems(["mean", "median", "most_frequent", "constant"])
            strategy_combo.setCurrentIndex(0) 
        
            checkbox = QCheckBox("Impute")
            checkbox.stateChanged.connect(lambda state, c=col, s=strategy_combo: self.impute_missing(state=state, cols=[c], strategy=s.currentText()))
            
            row_layout.addWidget(strategy_combo)
            row_layout.addWidget(checkbox)
            self.main_interface.impute_checkboxes.append((f"impute-{col}", checkbox))

            checkbox_map[("impute", col)] = checkbox  # Store the checkbox in the shared map
             
            layout.addLayout(row_layout)

        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)


    def impute_missing(self, state, df=None, cols=None, strategy=None, name="impute", checkbox=None):
        df = set_df(df, self.main_interface)
        

        if state == 2 or state == True:
            print("Imputing missing values")
        
            if checkbox:
                checkbox.blockSignals(True)
                checkbox.setChecked(True)
                checkbox.blockSignals(False)
    
            imputer = SimpleImputer(strategy=strategy)
            df[cols] = imputer.fit_transform(df[cols])

            modified_df = df[cols]
            save_parquet_file(modified_df, f"{name}-{cols[0]}", self.main_interface, strategy)
            self.main_interface.update_table()
            
            print(modified_df)
   
        else:
            on_uncheck_checkbox(self.main_interface, name=f"{name}-{cols[0]}", strategy=strategy)






def process_file(main_interface , config=None):
    
    
    if config is None:
        config = {}


    impute = imputeMissingWidget(main_interface)
    drop_column = dropColumnWidget(main_interface)
    remove_outlier = removeOutlierWidget(main_interface)
    encode = encodingCategoryWidget(main_interface)


    for operation, details in config.items():

        df = main_interface.main_df
        # df = df_from_parquet(main_interface.current_df[0])
 
        
        if operation == "impute":
            cols = details.get("col", [])
            strategies = details.get("strategy", [])
            
            for col, strategy in zip(cols, strategies):
                for checkbox in main_interface.impute_checkboxes:
                    if checkbox[0] == f"impute-{col}":
                        df = impute.impute_missing(state=True, df = df ,cols=[col], strategy=strategy , checkbox=checkbox[1])

        if operation == "drop_column":
            cols = details.get("col", [])
                     
            for col in cols:
                for checkbox in main_interface.drop_column_checkboxes:
                    if checkbox[0] == f"drop_column-{col}":

                        checkbox[1].blockSignals(True)
                        checkbox[1].setChecked(True)
                        checkbox[1].blockSignals(False)
                        checkbox[1].parent().columns_to_drop.append(col)

            
            df = drop_column.drop_column(state=True, df = df ,cols= cols)
           

          


        if operation == "remove_outlier":
            
            cols = details.get("col", [])
            strategies = details.get("strategy", [])
            for col, strategy in zip(cols, strategies):
                
                for checkbox in main_interface.remove_outlier_checkboxes:
                    
                    if checkbox[0] == f"remove_outlier-{col}-{strategy}":
                        df = remove_outlier.remove_outlier(state=True, df = df ,cols=[col] ,  checkbox=checkbox[1] , method=strategy)

        
        # if operation == "drop_column":
        #     cols = details.get("col", [])
                     
        #     for col in cols:
        #         for checkbox in main_interface.drop_column_checkboxes:
        #             if checkbox[0] == f"drop_column-{col}":

        #                 checkbox[1].blockSignals(True)
        #                 checkbox[1].setChecked(True)
        #                 checkbox[1].blockSignals(False)
        #                 checkbox[1].parent().columns_to_drop.append(col)

            
        #     df = drop_column.drop_column(state=True, df = df ,cols= cols)
        if operation == "encode":
            cols = details.get("col", [])
            strategies = details.get("strategy", [])
            for col, strategy in zip(cols, strategies):
                for checkbox in main_interface.encode_checkboxes:
                   
                    if checkbox[0] == f"encode-{col}":
                        checkbox[1].blockSignals(True)
                        checkbox[1].setChecked(True)
                        checkbox[1].blockSignals(False)
                        checkbox[1].parent().columns_to_encode.append(col)

            df = encode.encode_category(state=True, df = df ,cols=cols  , strategy=strategies)
