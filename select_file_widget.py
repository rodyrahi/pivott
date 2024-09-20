import json

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

from mian_interface import MainInterface

class SelectFileWidget(QWidget):
    def __init__(self , project_path):
        super().__init__()

        self.project_path = project_path
        
        self.initUI()




    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.dropArea = QLabel("Drag and drop .csv or .xlsx files here\nor click to select")
        self.dropArea.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dropArea.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                padding: 20px;
            }
        """)
        layout.addWidget(self.dropArea)

        self.setAcceptDrops(True)
        self.dropArea.mousePressEvent = self.openFileDialog

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        for f in files:
            if f.lower().endswith(('.csv', '.xlsx')):
                print(f"File dropped: {f}")
                self.update_json(f)
                self.open_new_project()
                # Here you can add code to handle the dropped file
            else:
                print(f"Unsupported file type: {f}")

    def openFileDialog(self, event):
        file, _ = QFileDialog.getOpenFileName(self, "Select File", "", "CSV Files (*.csv);;Excel Files (*.xlsx)")
        if file:
            print(f"File selected: {file}")
            self.update_json(file)
            self.open_new_project()

    def update_json(self, file_path):
        
        with open(self.project_path, 'r') as json_file:
            data = json.load(json_file)

        data["data_path"] = file_path

        with open(self.project_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)


        


    def open_new_project(self):
        main_interface = MainInterface(project_path=self.project_path)
        self.parent().layout().addWidget(main_interface)
        self.parent().layout().removeWidget(self)
        self.deleteLater()
