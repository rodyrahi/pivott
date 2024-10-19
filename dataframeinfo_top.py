import sys
import polars as pl
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QTableWidget, QTableWidgetItem, QTabWidget
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import seaborn as sns



class DataFrameInfoWidget(QWidget):
    def __init__(self, df: pl.DataFrame):
        super().__init__()
        self.df = df

        # Create Tab Widget to hold different sections of DataFrame info
        self.tab_widget = QTabWidget(self)

        # Add tabs for various DataFrame information
        self.add_general_info_tab()
        self.add_column_statistics_tab()
        self.add_graphs_tab()

        # Set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

        # Limit the height of the entire widget
        self.setMaximumHeight(150)  # Set a maximum height to the widget (adjust as needed)

    def add_general_info_tab(self):
        """Add a general information tab for DataFrame summary."""
        general_info_widget = QWidget()
        layout = QVBoxLayout()

        # Display general DataFrame info
        num_rows = self.df.shape[0]
        num_cols = self.df.shape[1]
        column_names_and_dtypes = ', '.join([f"(<b>{col}</b>,{dtype})" for col, dtype in zip(self.df.columns, self.df.dtypes)])

        info_text = (
            f"<b>Shape: ({num_rows} , {num_cols} )</b><br>"
            f"Column Names <br> {column_names_and_dtypes}"
            # f"Data Types: {dtypes}"
        )
        label = QLabel(info_text)
        label.setWordWrap(True)

        layout.addWidget(label)
        general_info_widget.setLayout(layout)
        self.tab_widget.addTab(general_info_widget, "General Info")

    def add_column_statistics_tab(self):
        """Add a tab to display basic column statistics in a table."""
        stats_widget = QWidget()
        layout = QVBoxLayout()

        # Get statistics for numeric columns
        numeric_columns = [col for col, dtype in zip(self.df.columns, self.df.dtypes) if dtype in [pl.Float64, pl.Int64]]
        
        if numeric_columns:
            # Calculate statistics for numeric columns
            stats_df = self.df.select(numeric_columns).describe().to_pandas()

            # Create a QTableWidget to display the statistics
            stats_table = QTableWidget(self)
            stats_table.setRowCount(len(stats_df))
            stats_table.setColumnCount(len(stats_df.columns))

            # Set column headers to be the column names of the statistics DataFrame
            stats_table.setHorizontalHeaderLabels([str(col) for col in stats_df.columns])

            # Set row headers to show which statistic each row represents
            stats_table.setVerticalHeaderLabels([str(idx) for idx in stats_df.index])

            # Populate the QTableWidget with the statistics
            for row_idx, row_data in stats_df.iterrows():
                for col_idx, value in enumerate(row_data):
                    stats_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

            # Adjust the table to fit contents
            stats_table.resizeColumnsToContents()
            stats_table.resizeRowsToContents()

            # Limit the height of the stats table
            stats_table.setMaximumHeight(200)  # Set a maximum height for the table (adjust as needed)

            # Add the table to the layout
            layout.addWidget(stats_table)
        
        else:
            no_data_label = QLabel("No numeric columns available for statistics.")
            layout.addWidget(no_data_label)

        stats_widget.setLayout(layout)
        self.tab_widget.addTab(stats_widget, "Statistics Table")

    def add_graphs_tab(self):
        """Add a tab to display various graphs based on DataFrame."""
        graph_widget = QWidget()
        graph_layout = QHBoxLayout()  # Changed to QHBoxLayout to display graphs side by side

        # Graph for missing values
        missing_values = self.df.select([
            pl.col(col).is_null().sum().alias(col) for col in self.df.columns
        ]).to_pandas()

        fig, axs = plt.subplots(1, 2, figsize=(12, 4))  # Set up 1 row and 2 columns for side-by-side graphs

        # 1. Missing Values Bar Chart
        axs[0].bar(missing_values.columns, missing_values.iloc[0], color='skyblue')
        axs[0].set_title('Missing Values per Column')
        axs[0].set_ylabel('Count')
        axs[0].set_xlabel('Columns')
        
        # 2. Histogram for Numeric Columns
        numeric_columns = [col for col, dtype in zip(self.df.columns, self.df.dtypes) if dtype in [pl.Float64, pl.Int64]]
        if numeric_columns:
            numeric_data = self.df.select(numeric_columns).to_pandas()
            for col in numeric_columns:
                axs[1].hist(numeric_data[col], bins=20, alpha=0.7, label=col)
            axs[1].set_title('Histogram of Numeric Columns')
            axs[1].set_ylabel('Frequency')
            axs[1].set_xlabel('Values')
            axs[1].legend(loc='upper right')

        plt.tight_layout()

        # Create a Matplotlib canvas and add it to the layout
        canvas = FigureCanvas(fig)
        graph_layout.addWidget(canvas)

        graph_widget.setLayout(graph_layout)
        self.tab_widget.addTab(graph_widget, "Graphs")
        graph_widget.setMaximumHeight(300)  # Limit the height of the graphs tab
