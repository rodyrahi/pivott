import pandas as pd
from sklearn.impute import SimpleImputer

class dataframe(pd.DataFrame):
    def __init__(self, file):
        super().__init__()
        self.file = file
        self.dataframe = self.file_to_dataframe()
        
    def file_to_dataframe(self):
        return pd.read_csv(self.file)
    
    def drop_duplicates(self):
        return self.dataframe.drop_duplicates()
     
        
    
    

