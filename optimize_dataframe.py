import pandas as pd
import numpy as np
def optimize_dataframe(df):
    # 1. Detect data types
    def detect_data_types(df):
        type_mapping = {
            pd.api.types.is_integer_dtype: 'Integer',
            pd.api.types.is_float_dtype: 'Float',
            pd.api.types.is_string_dtype: 'String',
            pd.api.types.is_bool_dtype: 'Boolean',
            pd.api.types.is_datetime64_any_dtype: 'Datetime',
            pd.api.types.is_timedelta64_dtype: 'Timedelta'
        }

        print("Automatically detected data types (grouped):\n")
        for column in df.columns:
            detected_type = 'Other'
            for type_check, type_name in type_mapping.items():
                if type_check(df[column]):
                    detected_type = type_name
                    break
            print(f"{column}: {detected_type}")
        print()

    # 2. Optimize integer columns
    def optimize_integer_columns(df):
        int_columns = df.select_dtypes(include=['int64']).columns
        int_types = {
            (-128, 127): 'int8',
            (-32768, 32767): 'int16',
            (-2147483648, 2147483647): 'int32'
        }

        for col in int_columns:
            col_min, col_max = df[col].min(), df[col].max()
            for (type_min, type_max), dtype in int_types.items():
                if type_min <= col_min and col_max <= type_max:
                    df[col] = df[col].astype(dtype)
                    break
            else:
                df[col] = df[col].astype('int64')

        print("Integer columns have been optimized.")
        return df

    # 3. Optimize float columns
    def optimize_float_columns(df):
        float_columns = df.select_dtypes(include=['float64']).columns

        for col in float_columns:
            col_min, col_max = df[col].min(), df[col].max()

            if np.finfo(np.float16).min < col_min and col_max < np.finfo(np.float16).max:
                df[col] = df[col].astype(np.float16)
            elif np.finfo(np.float32).min < col_min and col_max < np.finfo(np.float32).max:
                df[col] = df[col].astype(np.float32)
            else:
                df[col] = df[col].astype('float64')

        print("Float columns have been optimized.")
        return df

    # 4. Find min and max values for numeric columns
    def find_min_max(df):
        # Handle numeric columns (int and float)
        for column in df.select_dtypes(include=['number']).columns:
            min_value = df[column].min()
            max_value = df[column].max()
            print(f"{column}:\n  Min: {min_value}\n  Max: {max_value}\n")

        # Handle non-numeric columns (object, category, etc.)
        for column in df.select_dtypes(exclude=['number']).columns:
            print(f"{column}: Not a numeric column, skipping min/max calculation\n")

    # Execute all steps
    print("Step 1: Detecting data types:")
    detect_data_types(df)

    print("Step 2: Optimizing integer columns:")
    df = optimize_integer_columns(df)

    print("Step 3: Optimizing float columns:")
    df = optimize_float_columns(df)

    print("Step 4: Finding min and max values:")
    find_min_max(df)

    print("Your data has been optimized.")  # Final print statement to indicate completion

    return df



# df = pd.read_csv(r"test.csv")
# print(df.info())
# optimize_dataframe(df)

# print(df.info())