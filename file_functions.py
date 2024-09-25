import gc
import os
import json
import pandas as pd





def update_add_json_file(main_interface , suffix , strategy):

    col = suffix.split('-')[-1]
    feature = suffix.split('-')[0]
    print(col)
    data = read_json_file(main_interface.project_path)

   

    if col not in data[feature]['col']:
        data[feature]['col'].append(col)

    if strategy and not len(data[feature]['strategy']) == len(data[feature]['col']):
        data[feature]['strategy'].append(strategy)

    with open(main_interface.project_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Updated {feature} in JSON: {data[feature]}")

def update_remove_json_file(main_interface , suffix , strategy):

    col = suffix.split('-')[-1]
    feature = suffix.split('-')[0]
    print(col)
    data = read_json_file(main_interface.project_path)

    if col in data[feature]['col']:
        data[feature]['col'].remove(col)

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
        df = pd.read_csv(file)
        df.to_parquet(save_path , engine='pyarrow')
    except:
        df = pd.read_excel(file)
        df.to_parquet(save_path , engine='pyarrow')


def df_from_parquet(file):
    df = pd.read_parquet(file)
    return df


def save_parquet_file(df, suffix , main_interface , strategy = None):

    filepath = main_interface.current_df[0].replace(".parquet", f"_{suffix}.parquet")
    if os.path.exists(filepath):
        os.remove(filepath)

    df.to_parquet(filepath , engine='pyarrow')
    main_interface.current_df.append(filepath)
    print(f"File saved as {filepath}")

    print(main_interface.main_df.shape)
    create_final_df(main_interface , main_interface.main_df )
    
    update_add_json_file(main_interface , suffix , strategy)
    








def create_final_df(main_interface, main_df):
    final_path = main_interface.current_df[0].replace("df.parquet", "final_df.parquet")
    if os.path.exists(final_path):
        os.remove(final_path)

    main_df = main_df.copy()
    # main_df = df_from_parquet(current_df[0].replace("df.parquet", "final_df.parquet"))
    
    print(main_interface.current_df)
    for file_path in main_interface.current_df:

        file_df = df_from_parquet(file_path)

        if 'dropna' in file_path:
            main_df = main_df[~main_df.index.isin(file_df.index)]

        elif 'drop_column' in file_path:
            col = file_path.split('-')[-1].replace(".parquet", "")
            # print(col)
            main_df = main_df.drop(col, axis=1)

        elif 'remove_outlier' in file_path:
            col = file_path.split('-')[-1].replace(".parquet", "")
  
            main_df = main_df[~main_df.index.isin(file_df.index)]

        
        elif 'impute' in file_path or 'encode' in file_path:
            print("impute is called")
            col = file_path.split('-')[-1].replace(".parquet", "")
            main_df[col] = file_df
            


        
            
    print(main_df.isna().sum())
    if os.path.exists(final_path):
        os.remove(final_path)
    main_df.to_parquet(final_path , engine='pyarrow')
    print(f"Final DataFrame saved to {final_path}")


    

    





def read_json_file(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data
        
