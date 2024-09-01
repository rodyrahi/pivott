import pandas as pd
from sklearn.impute import SimpleImputer

class dataframe(pd.DataFrame):
    def __init__(self, file):
        super().__init__()
        self.file = file
        self.dataframe = self.file_to_dataframe()
        
    def file_to_dataframe(self):

        try:
            return pd.read_csv(self.file)
        except:
            return pd.read_excel(self.file)

    
        
    
    

