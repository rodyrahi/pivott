import json
import os
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

from custom_widgets import stepButton , Button
from operation_widgets import process_file
from file_functions import update_remove_json_file

from collapsable_widgets import CollapsableWidget
from operation_widgets import on_uncheck_checkbox

class StepsWidget(QWidget):
    def __init__(self , main_interface):
        super().__init__()
        self.main_interface = main_interface
        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout()
        
       
        print(self.main_interface.current_df)
        # step1_button = stepButton("Step 1")
        # step2_button = stepButton("Step 2")
        # step3_button = stepButton("Step 3")
        self.update_steps()
        

        # self.main_layout.addWidget(step1_button)
        # self.main_layout.addWidget(step2_button)
        # self.main_layout.addWidget(step3_button)
        
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.main_layout)
    
    def update_steps(self):
         
        
        # Remove all widgets from main_layout
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.deleteItemsOfLayout(item.layout())
        


        with open(self.main_interface.project_path, 'r') as file:
            data = json.load(file)
        

        step_label = QLabel("Operations")
        self.main_layout.addWidget(step_label)
        step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        operations = [(op , data[op]['col']) for op in data.keys() if isinstance(data[op], dict) and 'col' in data[op] and len(data[op]['col']) > 0]
        
        for op, col in operations:
            
            button_layout = QHBoxLayout()
            button_layout.addWidget(QLabel(f"{op}") , alignment=Qt.AlignmentFlag.AlignHCenter)
            close_button = QPushButton("×")
            close_button.setObjectName("closeButton")
            close_button.setFixedSize(30, 30)
            close_button.setStyleSheet("""
                QPushButton#closeButton {
                    background-color: transparent;
                    border: none;
                    color: #808080;
                    font-size: 20px;
                    font-weight: bold;
                }
                QPushButton#closeButton:hover {
                    color: white;
                }
            """)
            close_button.clicked.connect(lambda _, op=op: self.remove_step(op))
            button_layout.addWidget(close_button)
            self.main_layout.addLayout(button_layout)

    def remove_step(self , op):
        all_checkbox = [self.main_interface.impute_checkboxes,
        self.main_interface.drop_column_checkboxes ,
        self.main_interface.remove_outlier_checkboxes ,
        self.main_interface.encode_checkboxes ,
        self.main_interface.drop_na_checkboxes ,
        self.main_interface.scale_minmax_checkboxes ,
        self.main_interface.change_dtype_checkboxes ]

        for checkboxes in all_checkbox:
            for checkbox in checkboxes:
                if op in checkbox[0]:
                    checkbox[-1].setChecked(False)
                    for i in self.main_interface.current_df:
                        
    
                        if f"df_{op}.parquet" in i:
                            self.main_interface.current_df.remove(i)
                            if os.path.exists(i):
                                os.remove(i)

                    # on_uncheck_checkbox(self.main_interface , name=op , strategy=None)
        update_remove_json_file(self.main_interface , f"{op}-remove")
        process_file(self.main_interface , self)




    def deleteItemsOfLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.deleteItemsOfLayout(item.layout())
            layout.deleteLater()