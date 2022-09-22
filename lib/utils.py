from InquirerPy import inquirer
from InquirerPy.separator import Separator
from InquirerPy.base import Choice
import os, numpy as np, pandas as pd

def get_paths(path = os.getcwd()):
    paths = []
    selector = 'yes'
    while True:
        home_path = path if os.name == "posix" else "C:\\"
        new_path = inquirer.filepath(
            message="Load CSV file or directory",
            qmark="\n📁",
            default=home_path,
        ).execute()
        # add new path to list of paths
        paths.append(new_path)

        print(f'{len(paths)} paths added to load')
        selector = inquirer.select(
            message="Will you like to add another file or path?",
            qmark="\n?",
            choices=[
                'yes',
                'no',
            ],
            pointer="👉",
        ).execute()
        if selector == "no":
            # paths = get_csv_files(paths)
            break
    return paths

# get csv and xlsx files from paths
def get_files(paths):
    files = []
    for path in paths:
        if os.path.isfile(path):
            if path.endswith(".csv") or path.endswith(".xlsx"):
                files.append(path)
                print(f"{path} added")
        elif os.path.isdir(path):
            for file in os.listdir(path):
                if file.endswith(".csv") or file.endswith(".xlsx"):
                    files.append(os.path.join(path, file))
                    print(f' \n✅ {os.path.basename(os.path.dirname(os.path.join(path, file)))}/{file} added')
    return files

def get_dataframes(files):
    dataframes = []
    for file in files:
        if file.endswith(".csv"):
            dataframes.append(pd.read_csv(file))
        elif file.endswith(".xlsx"):
            dataframes.append(pd.read_excel(file))
    return dataframes

def clean_dataframes(dataframes):
    cleaned_dfs = []
    for df in dataframes:
        df= df.rename(columns=str.lower)
        df = df.fillna('')
        keep_cols = [
            'first name' 'last name' 'email 1' 'phone 1' 'phone 2' 'phone 3'
            'address 1 - street' 'address 1 - city' 'address 1 - country'
            'address 2 - city' 'address 2 - country' 'address 3 - street'
            'address 3 - city' 'address 3 - country' 'labels' 'created at'
            'subscription status' 'total purchases' 'total spent' 'last activity'
            'last activity date' 'source' 'language']
        print(keep_cols)

        # add all data frame columns to list of columns to keep
        select_cols = inquirer.select(
                message="Select the columns you want to keep",
                qmark="\n?",
                choices=[
                    Choice(keep_cols[0], keep_cols[1]),
                    Separator(),
                    'all',
                ],
                multiselect=True,
                pointer="👉",
            ).execute()
        if select_cols == 'all':
            keep_columns = df.columns
        else:
            keep_columns = select_cols
        # drop all columns not in keep_columns
        print(df.filter(regex='|'.join(keep_columns)).columns)
        cleaned_dfs.append(df)
    return cleaned_dfs

        

paths = get_paths()
files = get_files(paths)
dataframes = get_dataframes(files)
cleaned_dfs = clean_dataframes(dataframes)
# # for df in cleaned_dfs:
# #     print(df.head())
# #     print(df.columns)
