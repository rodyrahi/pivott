import json
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from custom_widgets import stepButton
class StepsWidget(QWidget):
    def __init__(self , main_interface):
        super().__init__()
        self.main_interface = main_interface
        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout()
        
        step_label = QLabel("Steps:")
        print(self.main_interface.current_df)
        # step1_button = stepButton("Step 1")
        # step2_button = stepButton("Step 2")
        # step3_button = stepButton("Step 3")
        self.update_steps()
        
        self.main_layout.addWidget(step_label)
        # self.main_layout.addWidget(step1_button)
        # self.main_layout.addWidget(step2_button)
        # self.main_layout.addWidget(step3_button)
        
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.main_layout)
    
    def update_steps(self):
        

        # Remove all widgets from main_layout
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        with open(self.main_interface.project_path, 'r') as file:
            data = json.load(file)
        

        

        operations = [(op , data[op]['col']) for op in data.keys() if isinstance(data[op], dict) and 'col' in data[op] and len(data[op]['col']) > 0]
        
        for op , col in operations:
            step_button = stepButton(op)
            self.main_layout.addWidget(step_button)

