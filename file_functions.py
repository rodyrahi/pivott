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

    if strategy and not len(data[feature]['strategy']) == len(data[feature]['col']):
        data[feature]['strategy'].append(strategy)

    with open(main_interface.project_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Updated {feature} in JSON: {data[feature]}")

def update_remove_json_file(main_interface , suffix ,strategy):

    col = suffix.split('-')[-1]
    feature = suffix.split('-')[0]
    # print(col)
    data = read_json_file(main_interface.project_path)

    if data[feature]['col']:
        data[feature]['col'] = []

    if strategy and strategy in data[feature]['strategy']:
        data[feature]['strategy'].remove(strategy)

    with open(main_interface.project_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Updated {feature} in JSON: {data[feature]}")



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
                "strategy": [
                   
                ]
            },
            "remove_outlier": {
                "col": [
                   
                ],
                "strategy": [
                   
                ]
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

        if 'dropna' in file_path:
            file_df = df_from_parquet(file_path)
            main_df = main_df[~main_df.index.isin(file_df.index)]

        elif 'drop_column' in file_path:
            
            cols = data['drop_column']['col']
            cols = [col for col in cols if col in main_df.columns]
            print(cols , "create final df")
            main_df = main_df.drop(cols)
     


        elif 'remove_outlier' in file_path:
            file_df = df_from_parquet(file_path)
            col = file_path.split('-')[-1].replace(".parquet", "")
  
            main_df = main_df[~main_df.index.isin(file_df.index)]

        
        elif 'impute' in file_path or 'encode' in file_path:

            cols = data['encode']['col']
            # cols = [col for col in cols if col in main_df.columns]
            file_df = df_from_parquet(file_path )
            print(cols)
            main_df[cols] = file_df
        
            


        
            
    
    if os.path.exists(final_path):
        os.remove(final_path)

    main_df.write_parquet(final_path , compression="zstd")
    print(f"Final DataFrame saved to {final_path}")


    

    





def read_json_file(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data
        
