from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class MainButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("padding: 20px 40px; font-size:15px")
class Button(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("padding: 10px;")


class SQCheckBox(QCheckBox):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)

    
    def save_unchecked(self , parent , df , column , method):
        column_found = self.inArray(parent.unchecked, column)
        if column_found is None:
            parent.unchecked.append((column+method, df.dataframe.copy()))
            print("unchecked added")
            return True
        return False
    
    def save_checked(self , parent , df , column , method):
        column_found = self.inArray(parent.checked, column)
        if column_found is None:
            parent.checked.append((column+method, df.dataframe.copy()))
            print("checked added")
            return False
        return column_found


    def inArray(self ,parent , column):
        for l in parent:
            if str(l[0]) == column:
                return l
           
        return None



class popCheckBox(QWidget):
    def __init__(self, text , parent , widget ):
        super().__init__()
        self.text = text
        self.parent = parent
        self.df = parent.df
        self.widget = widget
        self.initUI()

    def initUI(self):
        self.cb = QCheckBox(self.text)

        if self.df is None:
            return None
        
        try:
            self.parent.column1Layout.removeWidget(self.widget)
        except:
            pass

        
        self.widget = self.widget(self.df , parent=self.parent)
        self.widget.hide()
        self.widget.feature_label.setText(self.text)
        self.parent.column1Layout.addWidget(self.widget)


    def visbility(self):
        if self.parent.df is None:
            return None
        if self.cb.isChecked():
            print(self.widget)
            self.widget.show()
        else:
            self.widget.hide()


class feature(QWidget):
    def __init__(self, column , top , func):
        super().__init__()
        self.column = column
        self.func = func
        self.connect_func = None
        
        
    def dropna_col(self):
        self.hbox = QHBoxLayout()
        
        self.label = QLabel(self.column)
        self.checkbox = SQCheckBox("Dropna")


        self.hbox.addWidget(self.label)
        self.hbox.addWidget(self.checkbox)
        self.hbox.setAlignment(Qt.AlignTop)
        self.connect_func = self.dropna_connect


    def impute_col(self):
        self.hbox = QHBoxLayout()
        self.hbox.setSpacing(5)
        self.label = QLabel(self.column)
        self.checkbox = SQCheckBox("Impute")


        self.hbox.addWidget(self.label)
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems(['mean', 'median', 'most_frequent', 'constant'])
        self.strategy_combo.setEditable(True)
        self.hbox.addWidget(self.strategy_combo)
        self.hbox.addWidget(self.checkbox)
        self.hbox.setAlignment(Qt.AlignTop)

        self.connect_func = self.impute_connect
    
    def encode_col(self):
        self.hbox = QHBoxLayout()
        self.label = QLabel(self.column)
        self.checkbox = SQCheckBox("Encode")


        self.hbox.addWidget(self.label)
        self.hbox.addWidget(self.checkbox)
        self.hbox.setAlignment(Qt.AlignTop)
        self.connect_func = self.encode_connect


    def checked(self):
        self.checkbox.stateChanged.disconnect()
        self.checkbox.setChecked(True)
        self.connect_func()
    
    def dropna_connect(self):
        self.checkbox.stateChanged.connect(lambda state=True , checkbox= self.checkbox,  col= self.column: self.func(state,checkbox , col))

    def impute_connect(self):
        self.checkbox.stateChanged.connect(lambda state=True , checkbox= self.checkbox,  col= self.column, strategy= self.strategy_combo: self.func(state,checkbox , col, strategy.currentText()))
           
    def encode_connect(self):
        self.checkbox.stateChanged.connect(lambda state=True , checkbox= self.checkbox,  col= self.column: self.func(state,checkbox , col))
    


