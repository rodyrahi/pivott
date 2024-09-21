from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import os



from sklearn.impute import SimpleImputer



from file_functions import read_save_parquet , df_from_parquet , save_parquet_file, create_final_df


def set_df(df , main_interface):
    if not df is None:
        final_df = main_interface.current_df[0].replace("df.parquet" , "final_df.parquet")
        if os.path.exists(final_df):
            df = df_from_parquet(final_df)
    else:    
        df = df_from_parquet(main_interface.current_df[0])
    
    return df

def on_uncheck_checkbox(main_interface , name=None):
    
    print("not checked")

    for i in main_interface.current_df:
        print(i)
        if f"df_{name}.parquet" in i:
            main_interface.current_df.remove(i)
            os.remove(i)


    create_final_df(main_interface.current_df)
    main_interface.update_table()



class imputeMissingWidget(QWidget):
    def __init__(self , main_interface):
        super().__init__()
        self.main_interface = main_interface
        # self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        print(self.main_interface.current_df)
    
        
        final_df = self.main_interface.current_df[0].replace("df.parquet", "final_df.parquet")
        if os.path.exists(final_df):
            final_df = df_from_parquet(final_df)
        else:
            final_df = df_from_parquet(self.main_interface.current_df[0])
        
        columns = final_df.columns[final_df.isnull().any()].tolist()

        for col in columns:
            row_layout = QHBoxLayout()
            
            col_label = QLabel(col)
            row_layout.addWidget(col_label)
            
            strategy_combo = QComboBox()
            strategy_combo.addItems(["mean", "median", "most_frequent", "constant"])
            strategy_combo.setCurrentIndex(0) 
        
            checkbox = QCheckBox("Impute")
            checkbox.stateChanged.connect(lambda state, c=col, s=strategy_combo: self.impute_missing(state=state, cols=[c], strategy=s.currentText() ))
            

            row_layout.addWidget(strategy_combo)
            row_layout.addWidget(checkbox)
            self.main_interface.impute_checkboxes.append(( f"impute-{col}" , checkbox))

            layout.addLayout(row_layout)

        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)

    def impute_missing(self, state, df=None, cols=None, strategy=None, name="impute" , checkbox=None):
        df = set_df(df, self.main_interface)
        

        if state == 2 or state==True:
            print("impute missing")
        
            if checkbox:
                checkbox.blockSignals(True)
                checkbox.setChecked(True)
                checkbox.blockSignals(False)
    


            imputer = SimpleImputer(strategy=strategy)
            df[cols] = imputer.fit_transform(df[cols])

            self.main_interface.update_table(df)
            modified_df = df[cols]
            save_parquet_file(modified_df, f"{name}-{cols[0]}" , self.main_interface.current_df )
            
            print(modified_df)
                
        else:
            on_uncheck_checkbox(self.main_interface , name=f"{name}-{cols[0]}")

            # print("not checked")

            # for i in self.main_interface.current_df:
            #     print(i)
            #     if f"df_{name}-{cols[0]}.parquet" in i:
            #         self.main_interface.current_df.remove(i)
            #         os.remove(i)


            # create_final_df(self.main_interface.current_df)
            # self.main_interface.update_table()

class dropDuplicateWidget(QWidget):
    def __init__(self , main_interface):
        super().__init__()
        self.main_interface = main_interface
        self.initUI()

    def initUI(self):
        print(self.main_interface.current_df)
        self.checkbox = QCheckBox("Drop duplicates")
        layout = QVBoxLayout()
        layout.addWidget(self.checkbox)
        # self.checkbox.stateChanged.connect(lambda  :self.drop_duplicates(self.checkbox.isChecked()))
        self.checkbox.stateChanged.connect(lambda  :self.drop_na(self.checkbox.isChecked()))


        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)

    def drop_duplicates(self , state):
        
        if state:
            self.main_interface.current_df = self.main_interface.current_df.drop_duplicates()
            self.main_interface.update_table()



    def drop_na(self , state , df=None, cols=None ,  name = "dropna"):
        
        if not df:
            df = df_from_parquet(self.main_interface.current_df[-1])

        if state:
            
            # if cols:
                self.checkbox.setChecked(True)
                path = f"{self.main_interface.save_data_folder}/df_{name}.parquet"
                print(path)
                # if not os.path.exists(path) and not f"df_{name}.parquet" in self.main_interface.current_df:

                modified_df = df.dropna()
                self.main_interface.update_table(modified_df)
                dropped_rows = df[~df.index.isin(modified_df.index)]
                save_parquet_file(dropped_rows , name , self.main_interface.current_df )
                
                print(dropped_rows)
                
        else:
            print("not checked")
            # if f"df_{name}.parquet" in self.main_interface.current_df[-1]:

            for i in self.main_interface.current_df:
                print(i)
                if f"df_{name}.parquet" in i:
                    self.main_interface.current_df.remove(i)
                    os.remove(i)


            create_final_df(self.main_interface.current_df)
            self.main_interface.update_table()

            # if f"df_{name}.parquet" in self.main_interface.current_df[-1]:
                
            # modified_df = df.dropna()
            # dropped_rows = df[df.isna().any(axis=1)]

        # return dropped_rows






def process_file(main_interface , config=None):
    
    if config is None:
        config = {}

    # Step 1: Read and save the CSV as a Parquet file
    # read_save_file(csv_filepath, parquet_filepath)

    # Step 2: Apply operations based on the config
    impute = imputeMissingWidget(main_interface)


    for operation, details in config.items():

        df = df_from_parquet(main_interface.current_df[0])

        
        # if operation == "dropna":
        #     cols = details.get("col", None)
        #     df = drop_na(df, cols)
        #     save_parquet_file(df, "dropna")

        # elif operation == "dropcol":
        #     cols = details.get("col", [])
        #     df = drop_col(df, cols)
        #     save_parquet_file(df, "dropcol")
        
        if operation == "impute":
            cols = details.get("col", [])
            strategies = details.get("strategy", [])
            
            for col, strategy in zip(cols, strategies):
                for checkbox in main_interface.impute_checkboxes:
                    if checkbox[0] == f"impute-{col}":
                        df = impute.impute_missing(state=True, df = df ,cols=[col], strategy=strategy , checkbox=checkbox[1])
            
        # df.to_parquet(main_interface.current_df[0].replace("df.parquet" , "final_df.parquet"))    

        # print(f"Shape after {operation}: {df.shape}")
