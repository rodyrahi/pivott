import pandas as pd
import glob
import os

from sklearn.impute import SimpleImputer


# global current_df 

current_df = ["./test_files/df.parquet"]



def save_parquet_file(df, suffix, base_path="./test_files/df.parquet"):


    filepath = base_path.replace(".parquet", f"_{suffix}.parquet")

    # Remove the file if it exists
    if os.path.exists(filepath):
        os.remove(filepath)

    df.to_parquet(filepath)


    # global current_df
    current_df.append(filepath)

    print(f"File saved as {filepath}")

def read_save_file(csv_filepath, parquet_filepath="./test_files/df.parquet"):
    
    df = pd.read_csv(csv_filepath)
    print("Loading CSV...")

    # Remove the existing parquet file if it exists
    if os.path.exists(parquet_filepath):
        os.remove(parquet_filepath)

    df.to_parquet(parquet_filepath)
    print("CSV loaded and saved as Parquet.")




def drop_na(df, cols=None):
    if cols:
        modified_df = df.dropna(subset=cols)
    else:
        modified_df = df.dropna()

    return modified_df

def drop_col(df, cols):
    return df.drop(columns=cols)

def impute_mising(df, cols, strategy):
    imputer = SimpleImputer(strategy=strategy)
    df[cols] = imputer.fit_transform(df[cols])
    return df

def process_file(csv_filepath, parquet_filepath="./test_files/df.parquet", config=None):
    
    if config is None:
        config = {}

    # Step 1: Read and save the CSV as a Parquet file
    read_save_file(csv_filepath, parquet_filepath)

    # Step 2: Apply operations based on the config
    for operation, details in config.items():
        df = pd.read_parquet(current_df[-1])  # Read the parquet file at each step
        
        if operation == "dropna":
            cols = details.get("col", None)
            df = drop_na(df, cols)
            save_parquet_file(df, "dropna")

        elif operation == "dropcol":
            cols = details.get("col", [])
            df = drop_col(df, cols)
            save_parquet_file(df, "dropcol")
        
        elif operation == "impute":
            cols = details.get("col", [])
            strategy = details.get("strategy", "mean")
            df = impute_mising(df, cols, strategy)
            save_parquet_file(df, f"impute_{strategy}")

        print(f"Shape after {operation}: {df.shape}")




def concat_parquet_files(output_path="./test_files/df.parquet"):

    if os.path.exists(output_path):
        os.remove(output_path)

   
    parquet_files = glob.glob("./test_files/*.parquet")
    
    dfs = [pd.read_parquet(file) for file in parquet_files if not file.endswith("df.parquet")]
    print(f"Number of Parquet files to concatenate: {len(dfs)}")

    if dfs:
        # Concatenate all dataframes
        combined_df = pd.concat(dfs , ignore_index=True)

 
   
        combined_df.to_parquet(output_path)
        combined_df.to_csv("combined_data.csv")
        print(f"All .parquet files have been concatenated and saved to {output_path}")
        print(combined_df)  




# Example JSON configuration
jsonfile = {
    "data_path": "test_data.csv",
    "dropcol": {
        "col": ["City"]
    },

    "dropna": {
        "col": []  
    },
    "impute": {
        "col": ["Legislative District"],
        "strategy": "mean"
    }

}



process_file(jsonfile["data_path"], config=jsonfile)
concat_parquet_files()

print(current_df)