import openai
openai.api_key = ''

def automate( user_promt , parent):

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

