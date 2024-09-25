import gc
import json
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import os
import glob
import numpy as np
import pandas as pd


from sklearn.calibration import LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OrdinalEncoder



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
        columns = final_df.columns[final_df.isnull().any()].tolist()

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


class dropColumnWidget(featureWidget):
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
        columns = final_df.columns.tolist()

        for col in columns:
            row_layout = QHBoxLayout()
            
            col_label = QLabel(col[:20] + '...' if len(col) > 20 else col)
            row_layout.addWidget(col_label)
            
        
            checkbox = QCheckBox("Drop Column")
            checkbox.stateChanged.connect(lambda state, c=col: self.drop_column(state=state, cols=[c]))
            

            row_layout.addWidget(checkbox)
            self.main_interface.drop_column_checkboxes.append((f"drop_column-{col}", checkbox))

            checkbox_map[("drop_column", col)] = checkbox  # Store the checkbox in the shared map
             

            
            layout.addLayout(row_layout)

        
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)


    def drop_column(self, state, df=None, cols=None, strategy=None, name="drop_column", checkbox=None):
        df = set_df(df, self.main_interface)

        if state == 2 or state == True:
            print("Dropping column(s)")
        
            if checkbox:
                checkbox.blockSignals(True)
                checkbox.setChecked(True)
                checkbox.blockSignals(False)

            if cols:
                dropped_columns = df[cols].copy()
                df = df.drop(columns=cols)

            save_parquet_file(dropped_columns, f"{name}-{cols[0]}", self.main_interface)
            self.main_interface.update_table()

            self.disable_checkbox(cols[0] , 'impute')
            self.disable_checkbox(cols[0] , 'iqr')    

            print(f"Dropped column(s): {cols}")
   
        else:
            on_uncheck_checkbox(self.main_interface, name=f"{name}-{cols[0]}")
            self.enable_checkbox(cols[0] , 'impute')
            self.enable_checkbox(cols[0] , 'iqr')    


class removeOutlierWidget(featureWidget):
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
        columns = final_df.columns.tolist()
        


        print("getting columns")
        for col in columns:
            if pd.api.types.is_numeric_dtype(final_df[col]):
                row_layout = QHBoxLayout()
                
                col_label = QLabel(col[:20] + '...' if len(col) > 20 else col)
                row_layout.addWidget(col_label)

                
                
                method_dropdown = QComboBox()
                method_dropdown.addItems(["IQR", "Z-Score"])
                
                remove_checkbox = QCheckBox("Remove Outliers")
                remove_checkbox.stateChanged.connect(lambda state, c=col , method = method_dropdown.currentText().lower() : self.remove_outlier(state=state, cols=[c], method=method))
                
                row_layout.addWidget(method_dropdown)
                row_layout.addWidget(remove_checkbox)

                if method_dropdown.currentText().lower() == "iqr":
                    self.main_interface.remove_outlier_checkboxes.append((f"remove_outlier-{col}-iqr", remove_checkbox))
                    checkbox_map[("remove_outlier-iqr", col)] = remove_checkbox

                elif method_dropdown.currentText().lower() == "z-score":
                    self.main_interface.remove_outlier_checkboxes.append((f"remove_outlier-{col}-zscore", remove_checkbox))
                    checkbox_map[("remove_outlier-zscore", col)] = remove_checkbox

                
                
                
                layout.addLayout(row_layout)
        
        print("layout added")
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)

    def remove_outlier(self, state, df=None, cols=None, method='iqr', name="remove_outlier", checkbox=None):
        df = set_df(df, self.main_interface)
        
        if state == 2 or state == True:
            print(f"Removing outliers using {method}")
        
            if checkbox:
                checkbox.blockSignals(True)
                checkbox.setChecked(True)
                checkbox.blockSignals(False)

            if cols:
                for col in cols:
                    if method == 'iqr':
                        Q1 = df[col].quantile(0.25)
                        Q3 = df[col].quantile(0.75)
                        IQR = Q3 - Q1
                        lower_bound = Q1 - 1.5 * IQR
                        upper_bound = Q3 + 1.5 * IQR
                        # df[col] = df[col].clip(lower_bound, upper_bound)

                        modified_df = df[(df[col] < lower_bound) | (df[col] > upper_bound)]

                    elif method == 'zscore':
                        z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                        df[col] = df[col].mask(z_scores > 3, df[col].mean())


            save_parquet_file(modified_df, f"{name}-{cols[0]}", self.main_interface , strategy=method)
            self.main_interface.update_table()

            print(f"Removed outliers from column(s): {cols} using {method}")
   
        else:
            on_uncheck_checkbox(self.main_interface, name=f"{name}-{cols[0]}" , strategy=method)


class encodingCategoryWidget(featureWidget):
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
        columns = final_df.select_dtypes(include=['object', 'category']).columns.tolist()

        for col in columns:
            row_layout = QHBoxLayout()
            
            col_label = QLabel(col[:20] + '...' if len(col) > 20 else col)
            row_layout.addWidget(col_label)
            
            strategy_combo = QComboBox()
            strategy_combo.addItems(["ordinal", "label" ])
            strategy_combo.setCurrentIndex(0) 
        
            checkbox = QCheckBox("Encode")
            checkbox.stateChanged.connect(lambda state, c=col, s=strategy_combo: self.encode_category(state=state, cols=[c], strategy=s.currentText()))
            
            row_layout.addWidget(strategy_combo)
            row_layout.addWidget(checkbox)
            self.main_interface.encode_checkboxes.append((f"encode-{col}", checkbox))

            checkbox_map[("encode", col)] = checkbox  # Store the checkbox in the shared map
             
            layout.addLayout(row_layout)

        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)


    def encode_category(self, state, df=None, cols=None, strategy=None, name="encode", checkbox=None):
        df = set_df(df, self.main_interface)
        

        if state == 2 or state == True:
            print("Encoding categorical values")
        
            if checkbox:
                checkbox.blockSignals(True)
                checkbox.setChecked(True)
                checkbox.blockSignals(False)

            
            if strategy == "label":
                le = LabelEncoder()
                modified_df = pd.DataFrame(le.fit_transform(df[cols[0]]), columns=[cols[0]])
                save_parquet_file(modified_df, f"{name}-{cols[0]}", self.main_interface, strategy)
                self.main_interface.update_table()
                
            elif strategy == "ordinal":
                oe = OrdinalEncoder()
                modified_df = pd.DataFrame(oe.fit_transform(df[[cols[0]]]), columns=[cols[0]])

                save_parquet_file(modified_df, f"{name}-{cols[0]}", self.main_interface, strategy)
                self.main_interface.update_table()

        else:
            on_uncheck_checkbox(self.main_interface, name=f"{name}-{cols[0]}", strategy=strategy)

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
                        
                        df = drop_column.drop_column(state=True, df = df ,cols=[col] , checkbox=checkbox[1])
       
        if operation == "remove_outlier":
            
            cols = details.get("col", [])
            strategies = details.get("strategy", [])
            for col, strategy in zip(cols, strategies):
                
                for checkbox in main_interface.remove_outlier_checkboxes:
                    
                    if checkbox[0] == f"remove_outlier-{col}-{strategy}":
                        df = remove_outlier.remove_outlier(state=True, df = df ,cols=[col] ,  checkbox=checkbox[1] , method=strategy)

        if operation == "encode":
            cols = details.get("col", [])
            strategies = details.get("strategy", [])
            for col, strategy in zip(cols, strategies):
                for checkbox in main_interface.encode_checkboxes:
                   
                    if checkbox[0] == f"encode-{col}":
                        
                        df = encode.encode_category(state=True, df = df ,cols=[col] ,  checkbox=checkbox[1] , strategy=strategy)
