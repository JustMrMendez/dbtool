import inquirer
import pandas as pd
import numpy as np
import os

# read xlsx file and convert to csv
def read_xlsx(file):
    df = pd.read_excel(file)
    df.to_csv(file.replace(".xlsx", ".csv"), index=False)
    return df


# read csv file
def read_csv(file, header=4):
    df = pd.read_csv(
        file,
        header=header,
        skip_blank_lines=True,
        usecols=lambda x: x not in ["Unnamed: 0"],
        encoding="utf-8",
        engine="c",
        skipinitialspace=True,
        on_bad_lines="warn",
    )
    df.columns = df.iloc[0].str.lower().str.replace(" ", "_")
    # remove all \n, \t, \r from column names
    df.columns = df.columns.str.replace("\n", "")
    df.columns = df.columns.str.replace("\t", "")
    df.columns = df.columns.str.replace("\r", "")
    df = df[2:]

    df = df.reset_index(col_level=0, drop=True)

    for i, column in enumerate(df.columns):
        if (not pd.isna(column)) & (
            round(df.iloc[:, i].isna().sum() / len(df), 2) > 0.80
        ):
            print(
                f'⚠️   #{i} → {column} is {"{:.0%}".format(df.iloc[:, i].isna().sum() / len(df))} empty with name'
            )

            if (pd.isna(df.columns[i + 1])) & (
                round(1 - df.iloc[:, i + 1].isna().sum() / len(df), 2) >= 0.80
            ):
                print(f"✅  #{i + 1} → {df.columns[i + 1]} renamed with {column}")
                df.rename(columns={df.columns[i + 1]: column}, inplace=True)
                print(df.columns)
        else:
            print(
                f"❌  #{i} → {column} {round(df.iloc[:, i].isna().sum() / len(df), 2)}"
            )

    print(df.head())
    return df

# ask user to enter file path
def get_file_path():
    file_path = input("Enter file path: ")
    if os.path.exists(file_path):
        return file_path
    else:
        print("File path does not exist")
        return get_file_path()

if __name__ == "__main__":
    file_path =  get_file_path()
    read_csv(file_path)