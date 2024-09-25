from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

from select_file_widget import SelectFileWidget
from custom_widgets import MainButton , Button , CollapsibleButton
from mian_interface import MainInterface
from file_functions import create_json_file

class ProjectWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()

        self.button_layout = QVBoxLayout()
        self.logo_layout = QVBoxLayout()

        new_project_btn = MainButton('New Project')
        new_project_btn.clicked.connect(self.new_project)
        self.button_layout.addWidget(new_project_btn)

        open_project_btn = MainButton('Open Project')
        open_project_btn.clicked.connect(self.open_project)
        self.button_layout.addWidget(open_project_btn)

        self.button_layout.setSpacing(20) 
        self.button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(self.button_layout)
        main_layout.addLayout(self.logo_layout)

        

        self.setLayout(main_layout)

    def new_project(self):

        file_dialog = QFileDialog()
        project_path , _ = file_dialog.getSaveFileName(self, "Create a Projec", "", "Project Files (*.json)")
        if project_path:
            create_json_file(project_path)

            # main_interface = MainInterface(project_path=project_path)
            
            select_file_widget = SelectFileWidget(project_path)

            self.parent().layout().addWidget(select_file_widget)

            self.parent().layout().removeWidget(self)
            self.deleteLater()


    def open_project(self):
        file_dialog = QFileDialog()
        project_path, _ = file_dialog.getOpenFileName(self, "Open a Project", "", "Project Files (*.json)")
        if project_path:
            main_interface = MainInterface(project_path=project_path)

            

            self.parent().layout().addWidget(main_interface)

            self.parent().layout().removeWidget(self)
            self.deleteLater()
            

        
