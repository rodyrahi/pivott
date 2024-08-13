from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
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
        self.parent.column1Layout.addWidget(self.widget)


    def visbility(self):
        if self.parent.df is None:
            return None
        if self.cb.isChecked():
            print(self.widget)
            self.widget.show()
        else:
            self.widget.hide()

class impute_col(QWidget):
    def __init__(self, column , top):
        super().__init__()
        self.column = column
        self.impute_checkbox = None
        self.top = top
        self.initUI()

    def initUI(self):
            self.hbox = QHBoxLayout()
            self.label = QLabel(self.column)
            self.impute_checkbox = SQCheckBox("Impute")


            self.hbox.addWidget(self.label)
            self.strategy_combo = QComboBox()
            self.strategy_combo.addItems(['mean', 'median', 'most_frequent', 'constant'])
            self.strategy_combo.setEditable(True)
            self.hbox.addWidget(self.strategy_combo)
            self.hbox.addWidget(self.impute_checkbox)
            self.hbox.setAlignment(Qt.AlignTop)
    
    def checked(self):
        self.impute_checkbox.stateChanged.disconnect()
        self.impute_checkbox.setChecked(True)
        self.impute_checkbox.stateChanged.connect(lambda state=True , checkbox= self.impute_checkbox,  col= self.column, strategy= self.strategy_combo: self.top.impute_column(state,checkbox , col, strategy.currentText()))


class dropna_col(QWidget):
    def __init__(self, column , top):
        super().__init__()
        self.column = column
        self.dropna_checkbox = None
        self.top = top
        self.initUI()

    def initUI(self):
            self.hbox = QHBoxLayout()
            self.label = QLabel(self.column)
            self.dropna_checkbox = SQCheckBox("Dropna")


            self.hbox.addWidget(self.label)
            self.hbox.addWidget(self.dropna_checkbox)
            self.hbox.setAlignment(Qt.AlignTop)
    
    def checked(self):
        self.dropna_checkbox.stateChanged.disconnect()
        self.dropna_checkbox.setChecked(True)
        self.dropna_checkbox.stateChanged.connect(lambda state=True , checkbox= self.dropna_checkbox,  col= self.column: self.top.dropna_column(state,checkbox , col))