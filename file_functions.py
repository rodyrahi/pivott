import gc
import os
import json
import pandas as pd
import polars as pl
from functools import cache







def update_add_json_file(main_interface , suffix , strategy , parquet_file , cols):

    # col = suffix.split('-')[-1]
    feature = suffix.split('-')[0]
    # print(col)
    data = read_json_file(main_interface.project_path)

   
    
    data[feature]['file'] = parquet_file
    if cols not in data[feature]['col']:
        data[feature]['col'] = cols

    # if strategy and not len(data[feature]['strategy']) == len(data[feature]['col']):
    #     data[feature]['strategy'].append(strategy)

    with open(main_interface.project_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Updated {feature} in JSON: {data[feature]}")

def update_remove_json_file(main_interface , suffix ,strategy=None):

    col = suffix.split('-')[-1]
    feature = suffix.split('-')[0]
    # print(col)
    data = read_json_file(main_interface.project_path)

    if data[feature]['col']:
        data[feature]['col'] = []

    # if strategy and strategy in data[feature]['strategy']:
    #     data[feature]['strategy'].remove(strategy)

    with open(main_interface.project_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    # print(f"Updated {feature} in JSON: {data[feature]}")



def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def create_json_file(file_path, data=None):

    data = {

            "data_path": "",
            "drop_column": {
                    "col": []
                },
            "dropna": {
                "col": []
            },
            "impute": {
                "col": [
                    
                ],
              
            },
            "remove_outlier": {
                "col": [
                   
                ],
                
            },
            "encode":{
                "col": [

                ],
                
            },
            "drop_na": {
                "col": [],
              
                "file": ""
                }

        }

    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)



def read_save_parquet(file , save_path):
    try:
        df = pl.read_csv(file)
        df.write_parquet(save_path )
    except:
        df = pl.read_excel(file)
        df.write_parquet(save_path )


def df_from_parquet(file , engine = 'pandas'):
    if engine == 'pandas':
        df = pl.read_parquet(file)
    else:
        df = pl.read_parquet(file)
    return df


def save_parquet_file(df, suffix , cols , main_interface , strategy = None):

    print("save_parquet_file called")

    filepath = main_interface.current_df[0].replace(".parquet", f"_{suffix}.parquet")
    if os.path.exists(filepath):
        os.remove(filepath)

    print(df)
    df.write_parquet(filepath , compression="zstd")

    main_interface.current_df.append(filepath)
    print(f"File saved as {filepath}")

    update_add_json_file(main_interface , suffix , strategy , filepath , cols)

    
    
    create_final_df(main_interface , main_interface.main_df )
    
    








def create_final_df(main_interface, main_df):
    final_path = main_interface.current_df[0].replace("df.parquet", "final_df.parquet")
    if os.path.exists(final_path):
        os.remove(final_path)

    
    main_df = main_df.clone()
    # main_df = df_from_parquet(current_df[0].replace("df.parquet", "final_df.parquet"))
    
   
    data = read_json_file(main_interface.project_path)

   


    for file_path in main_interface.current_df:



            
        if 'drop_column' in file_path:
            
            cols = data['drop_column']['col']
            cols = [col for col in cols if col in main_df.columns]
            print(cols , "create final df")
            main_df = main_df.drop(cols)

            
     


        elif 'remove_outlier' in file_path:

            file_df = df_from_parquet(file_path)

            main_df = main_df.with_columns(pl.concat_str(main_df.columns).alias("concat_all"))
            file_df = file_df.with_columns(pl.concat_str(file_df.columns).alias("concat_all"))

            main_df_filtered = main_df.join(file_df, how="anti", on="concat_all")
            main_df = main_df_filtered.drop("concat_all")

        
        elif 'impute' in file_path:

            cols = data['impute']['col']
            file_df = df_from_parquet(file_path)
            cols = [col for col, method in cols]
            
            # Ensure we only use columns that exist in both dataframes
            common_cols = [col for col in cols if col in main_df.columns and col in file_df.columns]
            
            # Replace columns in main_df with columns from file_df
            main_df = main_df.with_columns(
                file_df.select(common_cols)
            )
        




        elif 'drop_na' in file_path:
            file_df = df_from_parquet(file_path)
            main_df = main_df.with_columns(pl.arange(0, pl.count()).alias("temp_index"))
            file_df = file_df.with_columns(pl.arange(0, pl.count()).alias("temp_index"))

            # Perform an anti-join based on the temporary index
            main_df = main_df.join(file_df, on="temp_index", how="anti").drop("temp_index")
            print(main_df)

        
        
        elif 'encode' in file_path:
            cols = data['encode']['col']
           
            file_df = df_from_parquet(file_path)
            cols = [col for col, method in cols]
            
            # Ensure we only use columns that exist in both dataframes
            common_cols = [col for col in cols if col in main_df.columns and col in file_df.columns]
            

            

            # Replace columns in main_df with columns from file_df
            main_df = main_df.with_columns(
                file_df.select(common_cols)
            )

        
            


        elif 'scale_minmax' in file_path:
            
            cols = data['scale_minmax']['col']
           
            file_df = df_from_parquet(file_path)
            # cols = [col for col in cols]
            
            # Get all common columns from file_df and main_df
            common_cols = [col for col in file_df.columns if col in main_df.columns]
            
            # Replace main_df columns with file_df columns
            main_df = main_df.with_columns(
                file_df.select(common_cols)
            )
            print(main_df) 

    
        
    
    if os.path.exists(final_path):
        os.remove(final_path)
    
    main_df.write_parquet(final_path , compression="zstd")
    print(f"Final DataFrame saved to {final_path}")


    

    





def read_json_file(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data
        
