
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import numpy as np

class OptimizedTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = np.array(data)
        self._columns = data.columns if hasattr(data, 'columns') else [f"Column {i+1}" for i in range(self._data.shape[1])]

    def rowCount(self, parent=QModelIndex()):
        return self._data.shape[0]

    def columnCount(self, parent=QModelIndex()):
        return self._data.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
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
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.setWordWrap(False)

    def setData(self, data):
        model = OptimizedTableModel(data)
        self.setModel(model)
        self.resizeColumnsToContents()


