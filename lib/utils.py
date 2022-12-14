import pandas as pd
import numpy as np

# i've a dataframe with a column that has values like this:
# Property
# 10915MBH	
# 10915MBH	
# 10915MBH	
# 109-25	
# 10915MBH	
# 10915MBH	
# 109-25	
# 109-25	

def unique_values(df, col):
    return df[col].unique()

def edit_values(df, col, old_value, new_value):
    df[col] = df[col].replace(old_value, new_value)
    return df