from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from custom_widgets import stepButton
class StepsWidget(QWidget):
    def __init__(self , main_interface):
        super().__init__()
        self.main_interface = main_interface
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        step_label = QLabel("Steps:")
        print(self.main_interface.current_df)
        step1_button = stepButton("Step 1")
        step2_button = stepButton("Step 2")
        step3_button = stepButton("Step 3")
        
        layout.addWidget(step_label)
        layout.addWidget(step1_button)
        layout.addWidget(step2_button)
        layout.addWidget(step3_button)
        
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)
