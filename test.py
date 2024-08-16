import pandas as pd
import numpy as np

# Sample dataframe
df = pd.DataFrame({
    'A': [1, 2, np.nan, 4],
    'B': ['a', 'b', 'c', 'd'],
    'C': [5, 6, 7, np.nan]
})

# Identify the column with NaN values (e.g., column 'A')
column_name = 'A'
column_data = df[column_name].copy()
column_position = df.columns.get_loc(column_name)

# Drop the column with NaN values
df = df.drop(columns=[column_name])

# Reinsert the column back at its original position
df.insert(column_position, column_name, column_data)

print(df)
