from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

import polars as pl 


from select_file_widget import SelectFileWidget
from custom_widgets import MainButton , Button , CollapsibleButton
from mian_interface import MainInterface
from file_functions import create_json_file


class ProjectWidget(QWidget):
    def __init__(self , main_parent = None):
        super().__init__()
        self.main_parent = main_parent
        # Set window to be frameless (no title bar) and fixed size
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(800, 600)

        # Main layout for the window
        main_layout = QVBoxLayout()




 
        middle_layout = QVBoxLayout()

        # Spacer above the logo and text (reduced size to move content up)
        middle_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Placeholder for logo (temporary)
        logo_label = QLabel()
        logo_label.setPixmap(QPixmap("icon.png").scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo_label.setFixedSize(100, 100)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("padding: 5px;")
        middle_layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignCenter)

        software_title = QLabel("Pivot")
        software_title.setStyleSheet("font-size: 24px; font-weight: bold;")
        software_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Software version
        version_label = QLabel("Version 1.0.0")
        version_label.setStyleSheet("font-size: 14px; color: gray;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add title and version to the middle layout
        middle_layout.addWidget(software_title)
        middle_layout.addWidget(version_label)

        # Add project management buttons (New and Open Project)
        button_layout = QHBoxLayout()

        # Add stretches on both sides of the buttons to center them horizontally
        button_layout.addStretch(1)

        # New Project button
        new_project_button = MainButton("New Project")
        new_project_button.clicked.connect(self.new_project)
        button_layout.addWidget(new_project_button)

        # Open Project button
        open_project_button = MainButton("Open Project")
        open_project_button.clicked.connect(self.open_project)
        button_layout.addWidget(open_project_button)

        # Add another stretch after the buttons to center them
        button_layout.addStretch(1)

        # Add button layout to the middle layout
        middle_layout.addLayout(button_layout)

        # Spacer below the logo and text (increased size to push buttons down)
        middle_layout.addSpacerItem(QSpacerItem(20, 200, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Add middle layout to the main layout (centered)
        main_layout.addLayout(middle_layout)

        # Set the main layout to the window
        self.setLayout(main_layout)

 
    
    def new_project(self):

        file_dialog = QFileDialog()
        project_path , _ = file_dialog.getSaveFileName(self, "Create a Projec", "", "Project Files (*.json)")
        if project_path:
            create_json_file(project_path)

            # main_interface = MainInterface(project_path=project_path)
            self.main_parent.toggle_frame()
            select_file_widget = SelectFileWidget(project_path)

            self.parent().layout().addWidget(select_file_widget)

            self.parent().layout().removeWidget(self)
            self.deleteLater()


    def open_project(self):
        file_dialog = QFileDialog()
        project_path, _ = file_dialog.getOpenFileName(self, "Open a Project", "", "Project Files (*.json)")
        if project_path:
            

            # df = pl.read_csv(r"C:\Users\Raj\Downloads\202310-divvy-tripdata.csv")
            # df.write_parquet("test_data.parquet", compression="zstd")

            # df = pl.read_parquet("test_data.parquet")
            # print(df)
       

            self.main_parent.toggle_frame()
            
            main_interface = MainInterface(project_path=project_path)


            self.parent().layout().addWidget(main_interface)
            self.parent().layout().removeWidget(self)
            
            self.deleteLater()
           
            

        








# class ProjectWidget(QWidget):
#     def __init__(self , main_parent = None):
#         super().__init__()
#         self.initUI()

#     def initUI(self):
#         main_layout = QHBoxLayout()

#         self.button_layout = QVBoxLayout()
#         self.logo_layout = QVBoxLayout()

#         new_project_btn = MainButton('New Project')
#         new_project_btn.clicked.connect(self.new_project)
#         self.button_layout.addWidget(new_project_btn)

#         open_project_btn = MainButton('Open Project')
#         open_project_btn.clicked.connect(self.open_project)
#         self.button_layout.addWidget(open_project_btn)

#         self.button_layout.setSpacing(20) 
#         self.button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         main_layout.addLayout(self.button_layout)
#         main_layout.addLayout(self.logo_layout)

        

#         self.setLayout(main_layout)

#     def new_project(self):

#         file_dialog = QFileDialog()
#         project_path , _ = file_dialog.getSaveFileName(self, "Create a Projec", "", "Project Files (*.json)")
#         if project_path:
#             create_json_file(project_path)

#             # main_interface = MainInterface(project_path=project_path)
            
#             select_file_widget = SelectFileWidget(project_path)

#             self.parent().layout().addWidget(select_file_widget)

#             self.parent().layout().removeWidget(self)
#             self.deleteLater()


#     def open_project(self):
#         file_dialog = QFileDialog()
#         project_path, _ = file_dialog.getOpenFileName(self, "Open a Project", "", "Project Files (*.json)")
#         if project_path:
            

#             # df = pl.read_csv(r"C:\Users\Raj\Downloads\202310-divvy-tripdata.csv")
#             # df.write_parquet("test_data.parquet", compression="zstd")

#             # df = pl.read_parquet("test_data.parquet")
#             # print(df)
       

#             main_interface = MainInterface(project_path=project_path)

            

#             self.parent().layout().addWidget(main_interface)

#             self.parent().layout().removeWidget(self)
#             self.deleteLater()
            

        
