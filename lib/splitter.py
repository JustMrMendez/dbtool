import os
import pandas as pd
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

from lib.cleaner import expclean_csv


def split_df(file, clean=False):
    if clean:
        df = expclean_csv(file)
        print(df.head())
    else:
        print("just read the file")
        # read the csv file ignoring blank lines and unneeded columns
        df = pd.read_csv(file)

    column = inquirer.select(
        message="Select a column to search",
        choices=df.columns.tolist(),
        pointer="👉",
    ).execute()

    values = df[column].unique()

    split_by_all = inquirer.confirm(
        message="Do you want to split by all values?",
        default=False
    ).execute()

    if split_by_all:
        values_to_split = values
    else:
        values_to_split = inquirer.checkbox(
            message="Select the values to split by",
            choices=values.tolist(),
            pointer="👉",
        ).execute()

    for value in values_to_split:
        value_df = df[df[column] == value]

        file_name = os.path.splitext(file)[0]

        new_file_name = f"{file_name}_{value}.csv"

        value_df.to_csv(new_file_name, index=False)
