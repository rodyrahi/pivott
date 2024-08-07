from PyQt5.QtWidgets import *
class Button(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("padding: 10px;")


class SQCheckBox(QCheckBox):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        


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