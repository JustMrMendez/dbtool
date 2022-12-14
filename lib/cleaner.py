import pandas as pd
import numpy as np

def expclean_csv(csv_file, head=3):
    df = pd.read_csv(csv_file, skiprows=head-1, skipfooter=4, engine='python')
    df = df.dropna(axis=1, how='all')
    df = df.dropna(axis=0, how='all')
    df = df.drop_duplicates()
    # drop unnamed columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    # remove /n from column names
    df.columns = df.columns.str.replace('\n', '')
    df = df.dropna(thresh=len(df.columns) * 0.5, axis=0)
    df = df.reset_index(drop=False)
    return df


