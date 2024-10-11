import polars as pl

def remove_null_rows(df: pl.DataFrame) -> tuple[pl.DataFrame, pl.DataFrame]:
    # Identify rows with any null values using pl.fold to apply the condition across all columns
    null_condition = pl.fold(
        acc=pl.lit(False),
        function=lambda acc, col: acc | col.is_null(),
        exprs=[pl.col(col) for col in df.columns]
    )
    
    # Remove rows with null values from the original dataframe
    cleaned_df = df.filter(~null_condition)
    
    # Get the removed rows (those with nulls)
    null_rows = df.filter(null_condition)
    
    return cleaned_df, null_rows

# Example usage
data = {
    "col1": [1, 2, None, 4],
    "col2": [None, 2, 3, 4]
}

df = pl.DataFrame(data)
cleaned_df, removed_rows = remove_null_rows(df)

print("Cleaned DataFrame:")
print(cleaned_df)
print("Removed Rows:")
print(removed_rows)
