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
from sklearn.preprocessing import *


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
    def __init__(self, main_interface , steps_widget):
        super().__init__()
        self.main_interface = main_interface
        self.columns = []
        self.steps_widget = steps_widget



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


    def add_columns(self, col, state=False, strategy=None , columns = None ):
       

        print(columns)
        if state == 2 or state is True:
            if strategy:

                columns.append([col, strategy])
                print(f"Column {col} added for imputation using {strategy}")
            else:
                columns.append(col)
                print(f"Column {col} added for imputation")
        else:
            if strategy:
 
                
    
                columns.remove([col , strategy])
                print(f"Column {col} removed from imputation using {strategy}")
            else:
                columns.remove(col)
                print(f"Column {col} removed from imputation")

    def get_final_df(self):
        final_df_path = self.main_interface.current_df[0].replace("df.parquet", "final_df.parquet")
        if os.path.exists(final_df_path):
            return  pl.read_parquet(final_df_path)
        else:
            return self.main_interface.main_df




class imputeMissingWidget(featureWidget):
    def __init__(self, main_interface , steps_widget):
        super().__init__(main_interface , steps_widget)
        self.columns_to_impute = []

    def initUI(self):
        layout = QVBoxLayout()
        print(self.main_interface.current_df)

        final_df = self.main_interface.main_df
        columns = final_df.schema
        columns = [col for col in columns if final_df[col].is_null().any()]

        print("getting columns for imputing missing values")
        for col in columns:
            row_layout = QHBoxLayout()

            col_label = QLabel(col[:20] + '...' if len(col) > 20 else col)
            row_layout.addWidget(col_label)

            strategy_combo = QComboBox()
            strategy_combo.addItems(["mean", "median", "most_frequent", "constant"])
            
            impute_checkbox = QCheckBox("Impute")
            impute_checkbox.stateChanged.connect(
                lambda state, c=col, strategy_combo=strategy_combo , columns=self.columns_to_impute: self.add_columns(
                    col=c, state=state, strategy=strategy_combo.currentText() ,  columns=columns
                )
            )
            row_layout.addWidget(strategy_combo)
            row_layout.addWidget(impute_checkbox)
            self.main_interface.impute_checkboxes.append((f"impute-{col}", impute_checkbox))

            checkbox_map[("impute", col)] = impute_checkbox  # Store in shared checkbox map
            
            layout.addLayout(row_layout)

        button_layout = QHBoxLayout()

        apply_button = smallButton("Apply")
        apply_button.clicked.connect(lambda: self.impute_missing(state=True, cols=self.columns_to_impute))

        clear_all_button = smallButton("Clear All")
        clear_all_button.clicked.connect(self.clear_all)
        button_layout.addWidget(clear_all_button)
        button_layout.addWidget(apply_button)

        layout.addLayout(button_layout)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)



    def impute_missing(self, state, df=None, cols=None, name="impute", checkbox=None):
        
        
        
        
        
        df = self.get_final_df()

        if state == 2 or state is True:
            print(f"Imputing missing values in columns: {cols}")
            

           
            if cols:
                modified_df = df.clone()
                for col , strategy in cols:
                    if strategy == "mean":
                        fill_value = df[col].mean()
                        print(fill_value)
                    elif strategy == "median":
                        fill_value = df[col].median()
                    elif strategy == "mode":
                        fill_value = df[col].mode()[0]
                        print(fill_value)
                    elif strategy == "constant":
                        fill_value = 0  # You can change this to any constant value

                    modified_df = modified_df.with_columns(pl.col(col).fill_null(fill_value))
                cols_for_df = [col for col , method in cols]
                save_parquet_file(modified_df[cols_for_df], f"{name}", cols, self.main_interface, strategy=strategy)
                self.main_interface.update_table()

                print(f"Imputed missing values in column(s): {cols} using {strategy}")
      
            else:
                on_uncheck_checkbox(self.main_interface, name=f"{name}")

            
            self.steps_widget.update_steps()

    def clear_all(self):
        for name, checkbox in self.main_interface.impute_checkboxes:
            checkbox.setChecked(False)

class dropNaWidget(featureWidget):
    def __init__(self, main_interface, steps_widget):
        super().__init__(main_interface, steps_widget)
        self.columns_to_drop = []

    def initUI(self):
        layout = QVBoxLayout()
        print(self.main_interface.current_df)

        final_df = self.main_interface.main_df
        columns = final_df.schema
        columns = [col for col in columns if final_df[col].is_null().any()]

        print("getting columns for dropping NA values")
        for col in columns:
            row_layout = QHBoxLayout()

            col_label = QLabel(col[:20] + '...' if len(col) > 20 else col)
            row_layout.addWidget(col_label)

            drop_checkbox = QCheckBox("Drop NA")
            drop_checkbox.stateChanged.connect(
                lambda state, c=col, columns=self.columns_to_drop: self.add_columns(
                    col=c, state=state, columns=columns
                )
            )
            row_layout.addWidget(drop_checkbox)
            self.main_interface.drop_na_checkboxes.append((f"drop_na-{col}", drop_checkbox))

            checkbox_map[("drop_na", col)] = drop_checkbox  # Store in shared checkbox map
            
            layout.addLayout(row_layout)

        button_layout = QHBoxLayout()

        apply_button = smallButton("Apply")
        apply_button.clicked.connect(lambda: self.drop_na(state=True, cols=self.columns_to_drop))

        clear_all_button = smallButton("Clear All")
        clear_all_button.clicked.connect(self.clear_all)
        button_layout.addWidget(clear_all_button)
        button_layout.addWidget(apply_button)

        layout.addLayout(button_layout)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)

    def drop_na(self, state, df=None, cols=None, name="drop_na", checkbox=None):
    # Use the main dataframe from the interface if df is not provided
        df = self.get_final_df()

        if state == 2 or state is True:
            if cols:
                print(f"Dropping NA values in columns: {cols}")
                
                # Check for null values only in the specified columns
                null_condition = pl.fold(
                    acc=pl.lit(False),
                    function=lambda acc, col: acc | col.is_null(),
                    exprs=[pl.col(col) for col in cols]  # Use only the specified columns
                )
                
                
                null_rows = df.filter(null_condition)
                
             
                
                
                print("Rows with null values:", null_rows)
                
               
                save_parquet_file(null_rows, name, cols, self.main_interface)
                
               
                self.main_interface.update_table()

                print(f"Dropped NA values in column(s): {cols}")
            
            else:
                # Handle the case where no columns are selected (maybe uncheck the checkbox)
                on_uncheck_checkbox(self.main_interface, name=f"{name}")
            
            # Update the steps widget
            self.steps_widget.update_steps()

    def clear_all(self):
        for name, checkbox in self.main_interface.drop_na_checkboxes:
            checkbox.setChecked(False)

class encodingCategoryWidget(featureWidget):
    def __init__(self, main_interface , steps_widget):
        super().__init__(main_interface , steps_widget)
        self.columns_to_encode = []

    def initUI(self):
        layout = QVBoxLayout()
        print(self.main_interface.current_df)

        final_df = self.main_interface.main_df
        columns = final_df.schema
        columns = [col for col in columns if final_df[col].dtype == pl.Categorical or final_df[col].dtype == pl.Utf8]

        print("getting columns for encoding categorical values")
        for col in columns:
            row_layout = QHBoxLayout()

            col_label = QLabel(col[:20] + '...' if len(col) > 20 else col)
            row_layout.addWidget(col_label)

            strategy_combo = QComboBox()
            strategy_combo.addItems(["ordinal","label"])
            
            encode_checkbox = QCheckBox("Encode")
            encode_checkbox.stateChanged.connect(
                lambda state, c=col, strategy_combo=strategy_combo , columns =self.columns_to_encode: self.add_columns(
                    col=c, state=state, strategy=strategy_combo.currentText() , columns=columns
                )
            )
            row_layout.addWidget(strategy_combo)
            row_layout.addWidget(encode_checkbox)
            self.main_interface.encode_checkboxes.append((f"encode-{col}", encode_checkbox))

            checkbox_map[("encode", col)] = encode_checkbox  # Store in shared checkbox map
            
            layout.addLayout(row_layout)

        button_layout = QHBoxLayout()

        apply_button = smallButton("Apply")
        apply_button.clicked.connect(lambda: self.encode_category(state=True, cols=self.columns_to_encode))

        clear_all_button = smallButton("Clear All")
        clear_all_button.clicked.connect(self.clear_all)
        button_layout.addWidget(clear_all_button)
        button_layout.addWidget(apply_button)

        layout.addLayout(button_layout)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)


    def encode_category(self, state, df=None, cols=None, name="encode", checkbox=None , strategy=None):
        
        df = self.get_final_df()


        if state == 2 or state is True:
            print(f"Encoding categorical values in columns: {cols}")
            
            if cols:
                modified_df = df.clone()
                for col, strategy in cols:

                      if strategy == "one-hot":
                          encoded = pd.get_dummies(modified_df[col], prefix=col)
                          modified_df = pl.concat([modified_df, pl.DataFrame(encoded)], axis=1)
                          modified_df = modified_df.drop(col)
                      elif strategy == "label":
                          encoded = pd.factorize(modified_df[col])[0]
                          modified_df = modified_df.with_columns(pl.Series(name=f"{col}_encoded", values=encoded))
                      elif strategy == "ordinal":
                          categories = modified_df[col].unique().sort().to_list()
                          encoded = pd.Categorical(modified_df[col], categories=categories).codes
                          modified_df = modified_df.with_columns(pl.Series(name=col, values=encoded))
                          print(modified_df)
                cols_for_df = [col for col, method in cols]
                save_parquet_file(modified_df[cols_for_df], f"{name}", cols, self.main_interface, strategy=strategy)
                self.main_interface.update_table()

                print(f"Encoded categorical values in column(s): {cols} using {strategy}")
      
            else:
                
                on_uncheck_checkbox(self.main_interface, name=f"{name}")
            
            self.steps_widget.update_steps()

    def clear_all(self):
        for name, checkbox in self.main_interface.encode_checkboxes:
            checkbox.setChecked(False)


class dropColumnWidget(featureWidget):
    def __init__(self, main_interface , steps_widget):
        super().__init__(main_interface , steps_widget)
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
            checkbox.stateChanged.connect(
                lambda state , col=col , columns=self.columns_to_drop  : self.add_columns(col=col , state=state , columns=columns  ))

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

    
    
    # def add_columns(self , col , state=False):
    #     if state == 2 or state == True:
                
    #         self.columns_to_drop.append(col)
    #         print("col appended " , col)

    #         self.disable_checkbox(col , 'impute')
    #         self.disable_checkbox(col , 'iqr')    
    #     else:
    #         self.columns_to_drop.remove(col)
    #         print("col removed" , col)
    #         self.enable_checkbox(col , 'impute')
    #         self.enable_checkbox(col , 'iqr')    

    
    
    def drop_column(self, state, df=None, cols=None, strategy=None, name="drop_column", checkbox=None):
        
        df = self.get_final_df()

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
            
            self.steps_widget.update_steps()           
            
    def clear_all(self):
        for name, checkbox in self.main_interface.drop_column_checkboxes:
            checkbox.setChecked(False)


class removeOutlierWidget(featureWidget):
    def __init__(self, main_interface , steps_widget):
        super().__init__(main_interface , steps_widget)
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
                    lambda state, c=col, method_dropdown=method_dropdown, columns =self.columns_to_remove_outliers: self.add_columns(
                        col=c, state=state, strategy=method_dropdown.currentText().lower() , columns= columns
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


    def remove_outlier(self, state, df=None, cols=None , methoh=None , name="remove_outlier", checkbox=None):
        df = self.get_final_df()

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
            self.steps_widget.update_steps()
    def clear_all(self):
        for name, checkbox in self.main_interface.remove_outlier_checkboxes:
            checkbox.setChecked(False)


class dropDuplicateWidget(featureWidget):
    def __init__(self , main_interface , steps_widget):
        super().__init__(main_interface , steps_widget)
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
        
        self.steps_widget.update_steps()

class scaleMinmaxWidget(featureWidget):
    def __init__(self, main_interface, steps_widget):
        super().__init__(main_interface, steps_widget)
        self.columns_to_scale = []

    def initUI(self):
        layout = QVBoxLayout()
        
        final_df = self.main_interface.main_df
        columns = final_df.columns
        dtypes = final_df.dtypes

        # Filter for numeric columns using Polars data types
        columns = [
            col for col, dtype in zip(columns, dtypes)
            if pl.Int64 == dtype or pl.Float64 == dtype
        ]

        print("Getting columns for MinMax scaling")

        # Use QGridLayout for a compact, structured layout
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)  # Reduce spacing to make it more compact

        for i, col in enumerate(columns):
            col_label = QLabel(col[:20] + '...' if len(col) > 20 else col)
            grid_layout.addWidget(col_label, i, 0)

            # Checkbox for scaling
            scale_checkbox = QCheckBox("Scale")
            grid_layout.addWidget(scale_checkbox, i, 1)

            # Min input with reduced width
            min_input = QLineEdit()
            min_input.setPlaceholderText("Min")
            min_input.setValidator(QDoubleValidator())  # Allow floating-point values only
            min_input.setFixedWidth(60)
            grid_layout.addWidget(min_input, i, 2)

            # Max input with reduced width
            max_input = QLineEdit()
            max_input.setPlaceholderText("Max")
            max_input.setValidator(QDoubleValidator())  # Allow floating-point values only
            max_input.setFixedWidth(60)
            grid_layout.addWidget(max_input, i, 3)

            # Connect the checkbox to the event handler
            scale_checkbox.stateChanged.connect(
                lambda state, c=col, columns=self.columns_to_scale, strategy=(min_input, max_input): self.add_columns(
                    col=c, state=state, strategy=[str(strategy[0].text()), str(strategy[-1].text())], columns=columns
                )
            )

            self.main_interface.scale_minmax_checkboxes.append((f"scale_minmax-{col}", scale_checkbox, min_input, max_input))
            checkbox_map[("scale_minmax", col)] = (scale_checkbox, min_input, max_input)

        # Add grid layout to the main layout
        layout.addLayout(grid_layout)

        # Button layout
        button_layout = QHBoxLayout()

        # Clear All Button
        clear_all_button = smallButton("Clear All")
        clear_all_button.setFixedWidth(80)
        button_layout.addWidget(clear_all_button, alignment=Qt.AlignmentFlag.AlignRight)
        clear_all_button.clicked.connect(self.clear_all)

        # Apply Button
        apply_button = smallButton("Apply")
        apply_button.setFixedWidth(80)
        button_layout.addWidget(apply_button, alignment=Qt.AlignmentFlag.AlignRight)
        apply_button.clicked.connect(self.apply_scale_minmax)

        # Add button layout to main layout
        layout.addLayout(button_layout)

        # Align layout to the top
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.setLayout(layout)


    def apply_scale_minmax(self):
        cols_to_scale = []
        min_max_values = {}
        for name, checkbox, min_input, max_input in self.main_interface.scale_minmax_checkboxes:
            if checkbox.isChecked():
                col = name.split('-')[1]
                cols_to_scale.append(col)
                try:
                    min_val = float(min_input.text())
                    max_val = float(max_input.text())
                    min_max_values[col] = (min_val, max_val)
                except ValueError:
                    print(f"Invalid min/max values for column {col}. Using default min/max.")
        
        self.scale_minmax(state=True, cols=self.columns_to_scale, min_max_values=min_max_values)

    def scale_minmax(self, state, df=None, cols=None, min_max_values=None, name="scale_minmax", checkbox=None):
        from sklearn.preprocessing import MinMaxScaler
        import numpy as np
        
        df = self.get_final_df()

        if state == 2 or state is True:
            if cols:
                print(f"Applying MinMax scaling to columns: {cols}")
                
                scaler = MinMaxScaler()
                
                scaled_df = df.clone()
                for col , strategy in cols:
                    print(strategy)
                    if min_max_values and col in min_max_values:
                        feature_range = min_max_values[col]
                        scaler = MinMaxScaler(feature_range=feature_range)
                    else:
                        scaler = MinMaxScaler()
                    
                    scaled_values = scaler.fit_transform(np.array(df[col]).reshape(-1, 1)).flatten()
                    scaled_df = scaled_df.with_columns(pl.Series(name=col, values=scaled_values))
                
                cols_to_save= [col for col , strategy in cols]
                save_parquet_file(scaled_df[cols_to_save], name, cols, self.main_interface , )
                
                self.main_interface.update_table()

                print(f"Applied MinMax scaling to column(s): {cols}")
            
            else:
                on_uncheck_checkbox(self.main_interface, name=f"{name}")
            
            self.steps_widget.update_steps()

    def clear_all(self):
        for name, checkbox, min_input, max_input in self.main_interface.scale_minmax_checkboxes:
            checkbox.setChecked(False)
            min_input.clear()
            max_input.clear()

class changeDtypeWidget(featureWidget):
    def __init__(self, main_interface, steps_widget):
        super().__init__(main_interface, steps_widget)
        self.columns_to_change = []

    def initUI(self):
        layout = QVBoxLayout()
        
        final_df = self.main_interface.main_df
        columns = final_df.columns

        print("Getting columns for dtype change")
        
        for col in columns:
            row_layout = QHBoxLayout()

            # Label for column name
            col_label = QLabel(col[:20] + '...' if len(col) > 20 else col)
            row_layout.addWidget(col_label)

            # Combo box for selecting dtype
            dtype_combo = QComboBox()
            dtype_combo.addItems(["Int64", "Float64", "String", "Boolean", "Datetime"])
            dtype_combo.setFixedWidth(100)  # Adjusted width for better appearance
            row_layout.addWidget(dtype_combo, alignment=Qt.AlignmentFlag.AlignRight)

            # Checkbox for applying dtype change
            change_checkbox = QCheckBox("Change")
            row_layout.addWidget(change_checkbox )

            # Connect checkbox to state change handler
            change_checkbox.stateChanged.connect(
                lambda state, c=col, columns=self.columns_to_change, dtype_combo=dtype_combo: self.add_columns(
                    col=c, state=state, strategy=dtype_combo.currentText(), columns=columns
                )
            )

            # Store the checkbox and combo box
            self.main_interface.change_dtype_checkboxes.append((f"change_dtype-{col}", change_checkbox, dtype_combo))
            checkbox_map[("change_dtype", col)] = (change_checkbox, dtype_combo)

            # Add row layout to main layout
            layout.addLayout(row_layout)

        # Layout for buttons
        button_layout = QHBoxLayout()
        
        # Clear All Button
        clear_all_button = smallButton("Clear All")
        clear_all_button.setFixedWidth(100)
        button_layout.addWidget(clear_all_button, alignment=Qt.AlignmentFlag.AlignLeft)
        clear_all_button.clicked.connect(self.clear_all)

        # Apply Button
        apply_button = smallButton("Apply")
        apply_button.setFixedWidth(100)
        button_layout.addWidget(apply_button, alignment=Qt.AlignmentFlag.AlignLeft)
        apply_button.clicked.connect(self.apply_change_dtype)

        # Add button layout to main layout
        layout.addLayout(button_layout)
        
        # Ensure main layout is aligned at the top
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.setLayout(layout)    
    def apply_change_dtype(self):
        cols_to_change = []
        dtype_changes = {}
        for name, checkbox, dtype_combo in self.main_interface.change_dtype_checkboxes:
            if checkbox.isChecked():
                col = name.split('-')[1]
                cols_to_change.append(col)
                dtype_changes[col] = dtype_combo.currentText()
        
        self.change_dtype(state=True, cols=self.columns_to_change, dtype_changes=dtype_changes)

    def change_dtype(self, state, df=None, cols=None, dtype_changes=None, name="change_dtype", checkbox=None):
        df = self.get_final_df()

        if state == 2 or state is True:
            if cols:
                print(f"Changing data types for columns: {cols}")
                
                changed_df = df.clone()
                for col, new_dtype in cols:
                    print(f"Changing {col} to {new_dtype}")
                    if new_dtype == "Int64":
                        changed_df = changed_df.with_columns(pl.col(col).cast(pl.Int64))
                    elif new_dtype == "Float64":
                        changed_df = changed_df.with_columns(pl.col(col).cast(pl.Float64))
                    elif new_dtype == "String":
                        changed_df = changed_df.with_columns(pl.col(col).cast(pl.Utf8))
                    elif new_dtype == "Boolean":
                        changed_df = changed_df.with_columns(pl.col(col).cast(pl.Boolean))
                    elif new_dtype == "Datetime":
                        changed_df = changed_df.with_columns(pl.col(col).cast(pl.Datetime))
                
                cols_to_save = [col for col, _ in cols]
                save_parquet_file(changed_df[cols_to_save], name, cols, self.main_interface)
                
                self.main_interface.update_table()

                print(f"Changed data types for column(s): {cols}")
            
            else:
                on_uncheck_checkbox(self.main_interface, name=f"{name}")
            
            self.steps_widget.update_steps()

    def clear_all(self):
        for name, checkbox, dtype_combo in self.main_interface.change_dtype_checkboxes:
            checkbox.setChecked(False)
            dtype_combo.setCurrentIndex(0)




def process_file(main_interface , steps_widget = None):
    
    
    # if config is None:
    config = read_json_file(main_interface.project_path)


    impute = imputeMissingWidget(main_interface , steps_widget )
    drop_column = dropColumnWidget(main_interface, steps_widget)
    remove_outlier = removeOutlierWidget(main_interface, steps_widget)
    encode = encodingCategoryWidget(main_interface, steps_widget)
    drop_na = dropNaWidget(main_interface, steps_widget)
    scale_minmax = scaleMinmaxWidget(main_interface, steps_widget)


    for operation, details in config.items():

        df = main_interface.main_df
        # df = df_from_parquet(main_interface.current_df[0])
 
        
        if operation == "impute":

            cols = details.get("col", [])

            for col in cols:
                for checkbox in main_interface.impute_checkboxes:
                   
                    print(col)
                    if checkbox[0] == f"impute-{col[0]}":
                        print("Encoding")
                        checkbox[1].blockSignals(True)
                        checkbox[1].setChecked(True)
                        checkbox[1].blockSignals(False)
                        checkbox[1].parent().columns_to_impute.append((col[0] , col[-1]))

                        df = impute.impute_missing(state=True, df=df, cols=[(col[0] , col[-1])], checkbox=checkbox[1])




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
        
        
        
        if operation == "encode":
           
            cols = details.get("col", [])

            for col in cols:
                for checkbox in main_interface.encode_checkboxes:
                   
                    print(col)
                    if checkbox[0] == f"encode-{col[0]}":
                        print("Encoding")
                        checkbox[1].blockSignals(True)
                        checkbox[1].setChecked(True)
                        checkbox[1].blockSignals(False)
                        checkbox[1].parent().columns_to_encode.append([col[0] , col[-1]])

                        df = encode.encode_category(state=True, df=df, cols=[(col[0] , col[-1])], strategy=col[-1], checkbox=checkbox[1])



        if operation == "drop_na":
            cols = details.get("col", [])
    
            for col in cols:
                for checkbox in main_interface.drop_na_checkboxes:
                    if checkbox[0] == f"drop_na-{col}":

                        checkbox[1].blockSignals(True)
                        checkbox[1].setChecked(True)
                        checkbox[1].blockSignals(False)
                        checkbox[1].parent().columns_to_drop.append(col)


            df = drop_na.drop_na(state=True, df=df, cols=cols)

                

        if operation == "scale_minmax":
           
            cols = details.get("col", [])

            for col in cols:
                for checkbox in main_interface.scale_minmax_checkboxes:
                   
                    
                    
                    if checkbox[0] == f"scale_minmax-{col[0]}":
                        print("Scaling MinMax")
                        checkbox[1].blockSignals(True)
                        checkbox[1].setChecked(True)
                        checkbox[1].blockSignals(False)
                        checkbox[1].parent().columns_to_scale.append(col)
                        checkbox[-1].setText( col[-1][-1])
                        checkbox[-2].setText( col[-1][0])
                        df = scale_minmax.scale_minmax(state=True, df=df, cols=[(col[0] , col[-1])], checkbox=checkbox[1])
            
            # df = encode.encode_category(state=True, df = df ,cols=cols  , strategy=strategies)



