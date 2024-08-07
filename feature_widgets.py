from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from PyQt5.QtWidgets import *
from custom_widgets import Button
from sklearn.impute import SimpleImputer
import numpy as np

class imputeWidget(QWidget):
    def __init__(self, df, parent):
        super().__init__()
        self.setAcceptDrops(True)
        self.df = df
        self.parent = parent
        self.initUI()
    
    def initUI(self):
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.acceptDrops = True
        layout = QVBoxLayout(scroll_widget)
        for column in self.df.dataframe.columns:
            hbox = QHBoxLayout()

            hbox.addWidget(QLabel(column))
    
            strategy_combo = QComboBox()
            strategy_combo.addItems(['mean', 'median', 'most_frequent', 'constant'])
            strategy_combo.setEditable(True)
            hbox.addWidget(strategy_combo)
    
            impute_button = Button("Impute")
            hbox.addWidget(impute_button)
            impute_button.clicked.connect(lambda checked, col=column, combo=strategy_combo: self.impute_column(col, combo.currentText()))
    
            layout.addLayout(hbox)        

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        self.setMaximumSize(300, 300)
        self.setAcceptDrops(True)
        self.setLayout(main_layout)
        


    def impute_column(self, column, strategy):

        if strategy == 'constant':
            fill_value = 0  # You can modify this to allow user input
            imputer = SimpleImputer(missing_values=np.nan, strategy=strategy, fill_value=fill_value)
        elif strategy in ['mean','median','most_frequent']:
            imputer = SimpleImputer(missing_values=np.nan, strategy=strategy)
        else:
            imputer = SimpleImputer(missing_values=np.nan, strategy='constant', fill_value=strategy)
        
        imputer.fit(self.df.dataframe[[column]])
        self.df.dataframe[column] = imputer.transform(self.df.dataframe[[column]]).ravel()        
      
        self.parent.df = self.df
        self.parent.create_table()
        
        print(f"Column '{column}' imputed using {strategy} strategy.")


