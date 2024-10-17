from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import polars as pl
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class OptimizedTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self._columns = data.columns if hasattr(data, 'columns') else [f"Column {i+1}" for i in range(self._data.shape[1])]

    def rowCount(self, parent=QModelIndex()):
        return self._data.shape[0]

    def columnCount(self, parent=QModelIndex()):
        return self._data.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            # Use .row() and .column() methods to get the correct values
            return str(self._data[index.row(), index.column()])
        elif role == Qt.ItemDataRole.BackgroundRole:
            return QColor(Qt.GlobalColor.white)
        elif role == Qt.ItemDataRole.ForegroundRole:
            return QColor(Qt.GlobalColor.black)
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._columns[section])
            else:
                return f"{section + 1}"
        return None


class OptimizedTableWidget(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.setAlternatingRowColors(True)
        self.setWordWrap(False)
        self.horizontalHeader().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.horizontalHeader().customContextMenuRequested.connect(self.show_unique_values)
        self.dataframe = None

    def setData(self, data):
        self.dataframe = data
        model = OptimizedTableModel(data)
        self.setModel(model)

    def show_unique_values(self, pos):
        logical_index = self.horizontalHeader().logicalIndexAt(pos)
        column_name = self.dataframe.columns[logical_index]

        # Polars value_counts() returns a DataFrame where:
        # - The first column is the unique values
        # - The second column is the counts, but its name depends on the input column
        value_counts_df = self.dataframe[column_name].value_counts()

        # Extract the unique values and their counts
        value_col_name = value_counts_df.columns[0]  # Name of the unique values column
        count_col_name = value_counts_df.columns[1]  # Name of the counts column

        # Sort the value_counts DataFrame for further analysis
        value_counts_sorted = value_counts_df.sort(count_col_name, descending=True)

        # Create a context menu
        context_menu = QMenu(self)

        # Create a QTextEdit for displaying column info
        info_edit = QTextEdit()
        info_edit.setReadOnly(True)

        # Gather column info
        column_info = f"Column Name: {column_name}\n"
        column_info += f"Data Type: {self.dataframe[column_name].dtype}\n"
        column_info += f"Number of Null Values: {self.dataframe[column_name].null_count()}\n"
        column_info += f"Number of Unique Values: {self.dataframe[column_name].n_unique()}\n"

        if self.dataframe[column_name].dtype in [pl.Float64, pl.Int64]:
            column_info += f"Min Value: {self.dataframe[column_name].min()}\n"
            column_info += f"Max Value: {self.dataframe[column_name].max()}\n"
            column_info += f"Mean: {self.dataframe[column_name].mean():.2f}\n"
            column_info += f"Median: {self.dataframe[column_name].median()}\n"
            column_info += f"Standard Deviation: {self.dataframe[column_name].std():.2f}\n"
        else:
            most_common_value = value_counts_sorted.select(value_col_name)[0, 0]
            least_common_value = value_counts_sorted.select(value_col_name)[-1, 0]
            column_info += f"Most Common Value: {most_common_value}\n"
            column_info += f"Least Common Value: {least_common_value}\n"

        info_edit.setText(column_info)
        info_edit.setMaximumSize(300, 150)  # Set a maximum size for the info edit

        # Add distribution plot if the column is numeric
        if self.dataframe[column_name].dtype in [pl.Float64, pl.Int64]:
            fig, ax = plt.subplots(figsize=(4, 3))
            self.dataframe[column_name].to_pandas().hist(ax=ax)
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
        # for value, count in value_counts_df.iter_rows():
        #     checkbox = QCheckBox(f"{value} : {count}")
        #     checkbox.stateChanged.connect(lambda state, v=value: self.filter_table(column_name, v, state))
        #     unique_layout.addWidget(checkbox)

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
        # Implement the filtering logic here
        pass
