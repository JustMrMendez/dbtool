import pandas as pd
# import numpy as np

def expclean_csv(file_path, head=3):
    if file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path, skiprows=head-1, skipfooter=4, dtype=str)
    elif file_path.endswith('.csv'):
        df = pd.read_csv(file_path, skiprows=head-1, skipfooter=4, engine='python', dtype=str)
    else:
        raise ValueError('Unsupported file type')

    df = df.dropna(axis=1, how='all')
    df = df.dropna(axis=0, how='all')
    df = df.drop_duplicates()
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.columns = df.columns.str.replace('\n', '')
    df = df.dropna(thresh=len(df.columns) * 0.3, axis=0)
    df = df.reset_index(drop=True)
    
    return df

