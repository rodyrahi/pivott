import openai
openai.api_key = ''

def get_travel_advice():
    prompt = f"the dataset is a ticanic dataset wihich tells about the survival of the passenger , the dataset has the columns PassengerId(range from 1 to 891),Survived(range from 0 to 1),Pclass(range from 1 to 3),Name,Sex,Age(range from 0 to 80 , contains nan),SibSp,Parch,Ticket,Fare,Cabin(contains nan),Embarked(contains nan) : what data cleaning should be taken foreach column   "

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a data scientist"},
            {"role": "user", "content": f"{prompt}:Without any comment, return the result in the following JSON format {{column: from these setps select one or more also if imputing tell the strategy [dropna,impute:mean/median/most_frequent,encoding_categorical_data,drop_duplicaes,drop_column,outlier_removing  ]}}"  }
        ]
    )
    advice = response.choices[0].message.content
    print(advice)
    # return advice
get_travel_advice()