import polars as pl 
import time 


# df = pl.read_csv(r"C:\Users\Raj\Downloads\202310-divvy-tripdata.csv")
# df.write_parquet("test_data.parquet", compression="zstd")

# df.drop_nulls()

# new_df = pl.read_parquet("test_data.parquet").to_pandas()

def do():
    
    start = time.time()
    for i in range(10):
        new_df = pl.read_parquet("test_data.parquet")
    end = time.time()

    print(end - start)

do()
# import pandas as pl 

# df = pl.read_csv(r"C:\Users\Raj\Downloads\202310-divvy-tripdata.csv")
# df.to_parquet("test_data.parquet")
# new_df = pl.read_parquet("test_data.parquet")
# df.dropna()