import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import pandas as pd

class dataframeinfo(QWidget):
    def __init__(self, df , parent=None):
        super().__init__()
        self.df = df
        self.info = {}
        self.initui()
  

    def initui(self):
        self.get_info()
        
        layout = QVBoxLayout()
        tab_widget = QTabWidget()
        
        main_tab = self.create_tab(["columns", "shape", "dtypes", "missing_values", "unique_values"])
        samples_tab = self.create_tab(["head", "tail", "sample"])
        describe_tab = self.create_tab(["describe"])
        
        tab_widget.addTab(main_tab, "Main Info")
        tab_widget.addTab(samples_tab, "Dataframe")
        tab_widget.addTab(describe_tab, "Describe")
        
        layout.addWidget(tab_widget)
        self.setLayout(layout)
        
        self.setWindowTitle("DataFrame Info")
        self.setGeometry(100, 100, 800, 600)
        # Remove the self.show() call from here

    def get_info(self):
        self.info = {
            'columns': self.df.columns.tolist(),
            'shape': self.df.shape,
            'dtypes': self.df.dtypes.to_dict(),
            'missing_values': self.df.isnull().sum().to_dict(),
            'unique_values': self.df.nunique().to_dict(),
            'describe': self.df.describe(include='all').to_dict(),
            'head': self.df.head().to_dict(),
            'tail': self.df.tail().to_dict(),
            'sample': self.df.sample(n=5).to_dict()
        }

    def create_tab(self, keys):
        tab = QWidget()
        tab_layout = QVBoxLayout()

        print(keys)
        
        for key in keys:
            group_box = QGroupBox(key.capitalize())
            layout = QVBoxLayout()
            
            if key == "describe":
                describe_data = self.info[key]
                table = QTableWidget()
                table.setColumnCount(len(describe_data))
                table.setRowCount(len(next(iter(describe_data.values()))))
                table.setHorizontalHeaderLabels(describe_data.keys())
                table.setVerticalHeaderLabels(next(iter(describe_data.values())).keys())
                for col, col_data in enumerate(describe_data.values()):
                    for row, value in enumerate(col_data.values()):
                        table.setItem(row, col, QTableWidgetItem(str(value)))
                layout.addWidget(table)

            elif key in ["head", "tail", "sample"]:
                data = self.info[key]
                table = QTableWidget()
                table.setColumnCount(len(data))
                table.setRowCount(len(next(iter(data.values()))))
                table.setHorizontalHeaderLabels(data.keys())
                for col, col_data in enumerate(data.values()):
                    for row, value in enumerate(col_data.values()):
                        table.setItem(row, col, QTableWidgetItem(str(value)))
                layout.addWidget(table)

            elif key == "shape":
                label = QLabel(f"Rows: {self.info[key][0]}, Columns: {self.info[key][1]}")
                layout.addWidget(label)

            elif key in ["dtypes", "missing_values", "unique_values"]:
                data = self.info[key]
                table = QTableWidget()
                table.setColumnCount(2)
                table.setRowCount(len(data))
                table.setHorizontalHeaderLabels(["Column", "Value"])
                for row, (col_name, value) in enumerate(data.items()):
                    table.setItem(row, 0, QTableWidgetItem(str(col_name)))
                    table.setItem(row, 1, QTableWidgetItem(str(value)))
                layout.addWidget(table)

            elif isinstance(self.info[key], dict):
                for sub_key, sub_value in self.info[key].items():
                    label = QLabel(f"{sub_key}: {sub_value}")
                    layout.addWidget(label)
            else:
                label = QLabel(str(self.info[key]))
                layout.addWidget(label)
            
            group_box.setLayout(layout)
            tab_layout.addWidget(group_box)
        
        tab.setLayout(tab_layout)
        return tab# if __name__ == '__main__':
#     app = QApplication(sys.argv)



#     window = dataframeinfo(pd.read_csv('test.csv'))
#     app.setStyleSheet(qdarkstyle.load_stylesheet_PyQt6())
#     window.show()
#     sys.exit(app.exec_())








