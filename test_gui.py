
import json
import sys
from PyQt6.QtWidgets import *
import qdarkstyle
import pandas as pd
import glob
import os
from data_cleaning import *
from project_window import *
from custom_widgets import MainButton , Button
# from sklearn.impute import SimpleImputer









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
        # try:
            df = pd.read_csv(csv_filepath)
            print("Loading CSV...")

            # Remove the existing parquet file if it exists
            if os.path.exists(parquet_filepath):
                os.remove(parquet_filepath)

            df.to_parquet(parquet_filepath)
            print("CSV loaded and saved as Parquet.")
            self.label.setText(f"File loaded: {csv_filepath}")
            self.data_cleaning = DataCleaningWidget()
            self.parent().layout().addWidget(self.data_cleaning)
            
            with open('test_project.json') as f:
                csv_data = json.load(f)
                print(csv_data)

            self.data_cleaning.process_file(csv_filepath=csv_data)

            # self.data_cleaning.drop_na(state=True)


        # except Exception as e:
        #     print(f"Error loading file: {str(e)}")
        #     self.label.setText("Error loading file")
    





class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.project_path = ""


        self.setWindowTitle('Two Column Main Window')
        self.setWindowIcon(QIcon('icon.png'))

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout for central widget
        main_layout = QHBoxLayout(central_widget)

        project_widget = ProjectWidget()
        main_layout.addWidget(project_widget)

    
        
        # Set the window properties
        self.setWindowTitle('Pivot')
        self.setGeometry(300, 100, 1000, 600)
        




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt6())

    sys.exit(app.exec())
