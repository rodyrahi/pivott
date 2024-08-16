import openai

import json
openai.api_key = ''

def openai_api( user_promt , parent):

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

    prompt = f"The dataset is a Titanic dataset which tells about the survival of passengers. The dataset has the following columns and their properties:\n\n"
    for column, info in column_info.items():
        range_info = f"range: {info['range']}" if info['range'] else "non-numeric"
        nan_info = "contains NaN" if info['has_nan'] else "no NaN"
        prompt += f"- {column}: {range_info}, {nan_info}\n"
    


    # prompt += "\nWhat data cleaning steps should be taken for each column?"
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a data scientist"},
            {"role": "user", "content": f"{prompt}:Without any comment, return the result in the following JSON format {{column: look every single column very carefully and from these steps select one or more (try to select more steps if possible ) also if imputing tell the strategy [dropna,impute:mean/median/most_frequent,encoding_categorical_data,drop_duplicates,drop_column,outlier_removing]}}"  }
        ]
    )
    advice = response.choices[0].message.content
    return advice


def auto_clean( user_promt ,parent):
        new_json = openai_api(user_promt , parent)
        
        new_json = new_json.replace('json' , '')
        new_json = new_json.replace('```' , '')
        print(new_json , type(new_json))
        test = json.loads(new_json)

        # test = {'PassengerId': [], 'Survived': [], 'Pclass': [], 'Name': [], 'Sex': ['encoding_categorical_data'], 'Age': ['impute:mean'], 'SibSp': [], 'Parch': [], 'Ticket': [], 'Fare': ['outlier_removing'], 'Cabin': ['drop_column'], 'Embarked': ['impute:most_frequent', 'encoding_categorical_data']}
        for i in test:
            if len(test[i]) > 0:
                jsonfile = json.load(open(parent.projectpath))
                # jsonfile[i] = test[i]

                print(i , test[i])
                for j in test[i]:


                    if 'impute' in j :
                        print(j)
                        strategy = j.split(':')[1]
                        if j not in  jsonfile["impute"]["col"] and strategy not in jsonfile['impute']['strategy']:
                            jsonfile['impute']['col'].append(i)
                            jsonfile['impute']['strategy'].append(strategy)
                    
                    
                    if 'drop_column' in j :
                        if j not in  jsonfile["dropcol"]["col"] :
                            jsonfile['dropcol']['col'].append(i)


                    if 'dropna' in j :

                        if j not in  jsonfile["dropna"]["col"] :
                            jsonfile['dropna']['col'].append(i)
                    
                    if 'encoding_categorical_data' in j :
                    
                        if j not in  jsonfile["encode"]["col"] :
                            jsonfile['encode']['col'].append(i)

                    if 'outlier_removing' in j :
                        print(j)
                        if j not in  jsonfile["outlier"]["col"] :
                            jsonfile['outlier']['col'].append(i)
                            jsonfile['outlier']['method'].append("IQR") 
                        
                        

                    with open(parent.projectpath, 'w') as file:
                        json.dump(jsonfile, file, indent=4)
    



