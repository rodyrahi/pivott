import nbformat as nbf




# Create a new notebook
nb = nbf.v4.new_notebook()

# Create a code cell with the existing Python code

data = {
    "data_path": "F:/pivott/pivott/test_data.csv",
    "drop_column": {
        "col": ["raj"]
    },
    "dropna": {
        "col": []
    },
    "impute": {
        "col": ["city"],
        "strategy": ["mode"]
    },
    "remove_outlier": {
        "col": ["age"],
        "strategy": ["iqr"]
    },
    "encode": {
        "col": [],
        "strategy": []
    }
}

def import_libs():
    nb.cells.append(nbf.v4.new_code_cell(
        '''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
        '''))


def create_file(jsondata):
    import_libs()
    if jsondata["data_path"]:
        csv_file = jsondata["data_path"]
        nb.cells.append(nbf.v4.new_code_cell(f'''data_frame = pd.read_csv("{csv_file}")'''))
    if jsondata["drop_column"]["col"]:
        nb.cells.append(nbf.v4.new_code_cell(f'''data_frame = data_frame.drop(columns={jsondata["drop_column"]["col"]})'''))

    if jsondata["dropna"]["col"]:
        nb.cells.append(nbf.v4.new_code_cell(f'''data_frame = data_frame.dropna(subset={jsondata["dropna"]["col"]})'''))

    if jsondata["impute"]["col"]:
        nb.cells.append(nbf.v4.new_code_cell(f'''data_frame = data_frame.fillna(strategy={jsondata["impute"]["strategy"]})'''))


create_file(data)

with open('python_code_generation.ipynb', 'w') as f:
    nbf.write(nb, f)
