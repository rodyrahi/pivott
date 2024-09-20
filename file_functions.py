import os
import json



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



