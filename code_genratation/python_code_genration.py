import json
import os

def create_jupyter_notebook(data, file_name):
    notebook = {
        "cells": [],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 4
    }

    def add_code_cell(source):
        notebook["cells"].append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": source
        })

    # Import libraries
    add_code_cell(
        "import pandas as pd\n"
        "import numpy as np\n"
        "import matplotlib.pyplot as plt\n"
        "import seaborn as sns"
    )

    # Load data
    if data["data_path"]:
        add_code_cell(f'data_frame = pd.read_csv("{data["data_path"]}")')

    # Drop columns
    if data["drop_column"]["col"]:
        add_code_cell(f'data_frame = data_frame.drop(columns={data["drop_column"]["col"]})')

    # Drop NA
    if data["dropna"]["col"]:
        add_code_cell(f'data_frame = data_frame.dropna(subset={data["dropna"]["col"]})')

    # Impute
    if data["impute"]["col"]:
        cols = data["impute"]["col"]
        add_code_cell(f'data_frame[{cols}].fillna(data_frame[{cols}].mean(), inplace=True)')

    # Remove outliers
    if data["remove_outlier"]["col"]:
        add_code_cell(
            f'data_frame = data_frame.drop(index=data_frame[data_frame[{data["remove_outlier"]["col"]}] > '
            f'data_frame[{data["remove_outlier"]["col"]}].quantile(0.75) + 1.5 * '
            f'(data_frame[{data["remove_outlier"]["col"]}].quantile(0.75) - '
            f'data_frame[{data["remove_outlier"]["col"]}].quantile(0.25))].index)'
        )

    # Encode
    if data["encode"]["col"]:
        add_code_cell(f'data_frame = data_frame.drop(columns={data["encode"]["col"]})')

    # Write notebook to file
    with open(f'{file_name}.ipynb', 'w') as f:
        json.dump(notebook, f)

# Example usage
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

create_jupyter_notebook(data, "output_notebook")
