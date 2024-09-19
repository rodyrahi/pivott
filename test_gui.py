
import sys
from PyQt6.QtWidgets import *

import pandas as pd
import glob
import os

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
        self.dropna_checkbox.stateChanged.connect(lambda  :self.drop_na(df , self.dropna_checkbox.isChecked()))
        


        self.dropcol_checkbox = QCheckBox("Drop columns")
        layout.addWidget(self.dropcol_checkbox)
        
        self.impute_checkbox = QCheckBox("Impute missing values")
        layout.addWidget(self.impute_checkbox)


    def drop_na(self , df, state , cols=None ):

        if state:
            
            if cols:
                modified_df = df.dropna(subset=cols)
            else:
                modified_df = df.dropna()

            self.save_parquet_file(df, "dropna")
            return modified_df
        else:
            self.current_df[:-1]


    def drop_col( self ,  df, cols):
        return df.drop(columns=cols)

    def impute_mising(df, cols, strategy):
        imputer = SimpleImputer(strategy=strategy)
        df[cols] = imputer.fit_transform(df[cols])
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



class FileLoaderWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.label = QLabel("No file loaded")
        layout.addWidget(self.label)
        
        load_button = QPushButton("Load File")
        load_button.clicked.connect(self.load_file)
        layout.addWidget(load_button)
    
    def load_file(self):
        file_dialog = QFileDialog()
        csv_filepath, _ = file_dialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if csv_filepath:
            self.read_save_file(csv_filepath)
    
    def read_save_file(self, csv_filepath, parquet_filepath="./test_files/df.parquet"):
        try:
            df = pd.read_csv(csv_filepath)
            print("Loading CSV...")

            # Remove the existing parquet file if it exists
            if os.path.exists(parquet_filepath):
                os.remove(parquet_filepath)

            df.to_parquet(parquet_filepath)
            print("CSV loaded and saved as Parquet.")
            self.label.setText(f"File loaded: {csv_filepath}")
            data_cleaning = DataCleaningWidget()
            self.parent().layout().addWidget(data_cleaning)

        except Exception as e:
            print(f"Error loading file: {str(e)}")
            self.label.setText("Error loading file")





class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 GUI")
        self.setGeometry(100, 100, 300, 200)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        label = QLabel("Welcome to PyQt6 GUI!")
        layout.addWidget(label)


        file_loader = FileLoaderWidget()
        layout.addWidget(file_loader)
        
        # data_cleaning = DataCleaningWidget()
        # layout.addWidget(data_cleaning)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
