import os
import json
import pandas as pd



def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def create_json_file(file_path, data=None):

    data = {

            "data_path": "",
            "dropna": {
                "col": []
            },
            "impute": {
                "col": [],
                "strategy": ""
            }

        }

    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)



def read_save_parquet(file , save_path):
    try:
        df = pd.read_csv(file)
        df.to_parquet(save_path)
    except:
        df = pd.read_excel(file)
        df.to_parquet(save_path)


def df_from_parquet(file):
    df = pd.read_parquet(file)
    return df


def save_parquet_file(df, suffix , current_df):

    filepath = current_df[0].replace(".parquet", f"_{suffix}.parquet")
    if os.path.exists(filepath):
        os.remove(filepath)

    df.to_parquet(filepath)
    current_df.append(filepath)
    print(f"File saved as {filepath}")
    create_final_df(current_df)




def create_final_df(current_df ):

    final_path = current_df[0].replace("df.parquet", "final_df.parquet")
    if os.path.exists(final_path):
        os.remove(final_path)

    main_df = df_from_parquet(current_df[0])
    for index , i in enumerate(current_df):
        if 'dropna' in i:
            # main_df = df_from_parquet(current_df[0])
            file_df = df_from_parquet(i)

            main_df = main_df[~main_df.index.isin(file_df.index)]
            main_df.to_parquet(final_path)
            print(main_df)
        elif 'impute' in i:
            
            col = i.split('-')[-1].replace(".parquet", "")
            file_df = df_from_parquet(i)[col]
            main_df[col] = file_df
            main_df.to_parquet(final_path)
        else:
            # main_df = df_from_parquet(current_df[0])
            main_df.to_parquet(final_path)




def read_json_file(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data
        

