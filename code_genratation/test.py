# import polars as pl 

# df = pl.read_csv(r"C:\Users\Raj\Downloads\202310-divvy-tripdata.csv")
# df.write_parquet("test_data.parquet", compression="zstd")

# df.drop_nulls()

# new_df = pl.read_parquet("test_data.parquet").to_pandas()




# import pandas as pl 

# df = pl.read_csv(r"C:\Users\Raj\Downloads\202310-divvy-tripdata.csv")
# df.to_parquet("test_data.parquet")
# new_df = pl.read_parquet("test_data.parquet")
# df.dropna()