from PyQt5.QtWidgets import *
from custom_widgets import *

class imputeWidget(QWidget):
    def __init__(self , df):
        super().__init__()
        self.df = df
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        for column in self.df.columns:
            hbox = QHBoxLayout()

            


            hbox.addWidget(QLabel(column))
            hbox.addWidget(Button("Impute"))
            
            layout.addLayout(hbox)        
          
        self.setLayout(layout)