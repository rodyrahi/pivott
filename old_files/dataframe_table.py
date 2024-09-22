
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn as sns 

class tableWidget(QWidget):
    def __init__(self, dataframe):
        super().__init__()

        self.dataframe = dataframe
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Create QTableWidget
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(self.dataframe.shape[0])
        self.tableWidget.setColumnCount(self.dataframe.shape[1])
        self.tableWidget.setHorizontalHeaderLabels(self.dataframe.columns)

        # Fill QTableWidget with DataFrame data
        for row in range(self.dataframe.shape[0]):
            for col in range(self.dataframe.shape[1]):
                item = QTableWidgetItem(str(self.dataframe.iat[row, col]))
                self.tableWidget.setItem(row, col, item)

        # Connect header right-click event to show unique values
        self.tableWidget.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableWidget.horizontalHeader().customContextMenuRequested.connect(self.show_unique_values)

        layout.addWidget(self.tableWidget)
        self.setLayout(layout)
        self.setWindowTitle('DataFrame Viewer')


    def show_unique_values(self, pos):
        logical_index = self.tableWidget.horizontalHeader().logicalIndexAt(pos)
        column_name = self.dataframe.columns[logical_index]
        value_counts = self.dataframe[column_name].value_counts().sort_index()

        # Create a context menu
        context_menu = QMenu(self)

        # Create a QTextEdit for displaying column info
        info_edit = QTextEdit()
        info_edit.setReadOnly(True)

        # Gather column info
        column_info = f"Column Name: {column_name}\n"
        column_info += f"Data Type: {self.dataframe[column_name].dtype}\n"
        column_info += f"Number of Null Values: {self.dataframe[column_name].isnull().sum()}\n"
        column_info += f"Number of Unique Values: {self.dataframe[column_name].nunique()}\n"

        if self.dataframe[column_name].dtype in ['int64', 'float64']:
            column_info += f"Min Value: {self.dataframe[column_name].min()}\n"
            column_info += f"Max Value: {self.dataframe[column_name].max()}\n"
            column_info += f"Mean: {self.dataframe[column_name].mean():.2f}\n"
            column_info += f"Median: {self.dataframe[column_name].median()}\n"
            column_info += f"Standard Deviation: {self.dataframe[column_name].std():.2f}\n"
        else:
            column_info += f"Most Common Value: {self.dataframe[column_name].mode().iloc[0]}\n"
            column_info += f"Least Common Value: {value_counts.index[-1]}\n"

        info_edit.setText(column_info)
        info_edit.setMaximumSize(300, 150)  # Set a maximum size for the info edit

        # Add distribution plot if the column is numeric
        if self.dataframe[column_name].dtype in ['int64', 'float64']:
            fig, ax = plt.subplots(figsize=(4, 3))
            self.dataframe[column_name].hist(ax=ax)
            ax.set_title(f'Distribution of {column_name}')
            ax.set_xlabel(column_name)
            ax.set_ylabel('Frequency')

            canvas = FigureCanvas(fig)
            canvas.setFixedSize(300, 200)

            plot_action = QWidgetAction(context_menu)
            plot_action.setDefaultWidget(canvas)
            context_menu.addAction(plot_action)

        context_menu.addSeparator()

        # Create a scroll area for unique values
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumSize(300, 200)

        unique_widget = QWidget()
        unique_layout = QVBoxLayout(unique_widget)

        # Add checkboxes for unique values
        for value, count in value_counts.items():
            checkbox = QCheckBox(f"{value} : {count}")
            checkbox.stateChanged.connect(lambda state, v=value: self.filter_table(column_name, v, state))
            unique_layout.addWidget(checkbox)

        scroll_area.setWidget(unique_widget)

        # Create QWidgetActions to hold the widgets
        info_action = QWidgetAction(context_menu)
        info_action.setDefaultWidget(info_edit)

        unique_action = QWidgetAction(context_menu)
        unique_action.setDefaultWidget(scroll_area)

        context_menu.addAction("Column Info")
        context_menu.addAction(info_action)
        context_menu.addAction("Unique Values")
        context_menu.addAction(unique_action)

        # Show the context menu at the cursor position
        context_menu.exec(QCursor.pos())

    def filter_table(self, column_name, value, state):
        for row in range(self.tableWidget.rowCount()):
            item = self.tableWidget.item(row, self.dataframe.columns.get_loc(column_name))
            if state == Qt.Checked:
                self.tableWidget.setRowHidden(row, item.text() != str(value))
            else:
                self.tableWidget.setRowHidden(row, False)
