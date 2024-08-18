# import openai

import json
from api import get_update


# openai.api_key = ''





def openai_api( user_promt , parent):
    print(user_promt)
    columns = parent.df.dataframe.columns.tolist()

    # Get column ranges and check for NaN values
    column_info = {}
    for column in columns:
        column_data = parent.df.dataframe[column]
        if column_data.dtype.kind in 'biufc':  # Check if numeric
            column_info[column] = {
                'range': (column_data.min(), column_data.max()),
                'has_nan': column_data.isna().any()
            }
        else:
            column_info[column] = {
                'range': None,
                'has_nan': column_data.isna().any()
            }

    prompt = f"{user_promt}. The dataset has the following columns and their properties:\n\n"
    for column, info in column_info.items():
        range_info = f"range: {info['range']}" if info['range'] else "non-numeric"
        nan_info = "contains NaN" if info['has_nan'] else "no NaN"
        prompt += f"- {column}: {range_info}, {nan_info}\n"
    


    prompt += "\nWhat data cleaning steps should be taken for each column?"
    # response = openai.chat.completions.create(
    #     model="gpt-4o",
    #     messages=[
    #         {"role": "system", "content": "You are an expert data scientist."},
    #         {"role": "user", "content": """{prompt}:Without any comment, return the result in the following JSON format 
    #          {{column: look every single column very carefully and from these steps select one or more (try to select more steps if possible ) also if imputing tell the strategy [dropna,impute:mean/median/most_frequent,encoding_categorical_data,drop_duplicates,drop_column,outlier_removing]}}"""  }
    #     ]
    # )


    # advice = response.choices[0].message.content
    return get_update(parent.version).get_data({'prompt': prompt})



def auto_clean( text_area ,parent):
    # print(text_area.toPlainText())
        # new_json = openai_api(text_area.toPlainText() , parent)
        # print(new_json)
        
        # new_json = new_json["result"].replace('json' , '')
        # new_json = new_json.replace('```' , '')
        # print(new_json , type(new_json))

        new_json = '''
            {
            "PassengerId": ["drop_duplicates"],
            "Survived": [],
            "Pclass": ["drop_duplicates", "encoding_categorical_data"],
            "Name": ["drop_duplicates"],
            "Sex": ["encoding_categorical_data"],
            "Age": ["impute:mean", "drop_duplicates", "outlier_removing"],
            "SibSp": ["drop_duplicates"],
            "Parch": [],
            "Ticket": ["drop_duplicates"],
            "Fare": ["impute:mean", "drop_duplicates", "outlier_removing"],
            "Cabin": ["dropna"],
            "Embarked": ["encoding_categorical_data"]
            }
            '''

        test = json.loads(new_json)

        # Load the jsonfile once, outside the loop
        with open(parent.projectpath) as file:
            jsonfile = json.load(file)

        for column, actions in test.items():
            if not actions:
                continue
            
            print(column, actions)
            
            for action in actions:
                if 'impute' in action:
                    strategy = action.split(':')[1]
                    if column not in jsonfile["impute"]["col"]:
                        jsonfile["impute"]["col"].append(column)
                    if strategy not in jsonfile["impute"]["strategy"]:
                        jsonfile["impute"]["strategy"].append(strategy)

                elif 'drop_column' in action:
                    if column not in jsonfile["dropcol"]["col"]:
                        jsonfile["dropcol"]["col"].append(column)

                elif 'dropna' in action:
                    if column not in jsonfile["dropna"]["col"]:
                        jsonfile["dropna"]["col"].append(column)

                elif 'encoding_categorical_data' in action:
                    if column not in jsonfile["encode"]["col"]:
                        jsonfile["encode"]["col"].append(column)

                elif 'outlier_removing' in action:
                    if column not in jsonfile["outlier"]["col"]:
                        jsonfile["outlier"]["col"].append(column)
                        jsonfile["outlier"]["method"].append("IQR")

        # Save the updated jsonfile once, after processing all columns
        with open(parent.projectpath, 'w') as file:
            json.dump(jsonfile, file, indent=4)

        parent.select_source(jsonfile)    



