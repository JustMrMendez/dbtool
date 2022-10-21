#!/usr/bin/env python

from operator import index
from unicodedata import name
import numpy as np
from yaspin import yaspin
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
import os, typer
import pandas as pd
from yaspin.spinners import Spinners
from validate_email_address import validate_email

app = typer.Typer()

menu = [
    Choice(name="Clean CSV", value="clean"),
    Choice(name="Merge CSV", value="merge"),
    Choice(name="Search CSV", value="search"),
    Separator(),
    Choice(name="Exit", value="exit"),
]

clean_menu = [
    Choice(name="Prepare File", value="prepare"),
    Choice(name="Split Data", value="split"),
    Choice(name="Sort by Date", value="sort"),
    Choice(name="Full Clean", value="full_clean"),
    Separator(),
    Choice(name="Save & Exit", value="exit"),
]

merge_menu = [
    Choice("merge", "Merge & Save"),
    Separator(),
    Choice("Exit", "exit"),
]

search_menu = [
    Choice("Filter by tag", "filter"),
    Choice("Search by value", "search"),
    Separator(),
    Choice("Exit", "exit"),
]


# check if path is a file or directory and return a list of o csv files
def get_csv_files(paths):
    csv_files = []
    for path in paths:
        if os.path.isfile(path):
            print(f"\n{path} added")
            if path.endswith(".csv"):
                csv_files.append(path)
        elif os.path.isdir(path):
            for file in os.listdir(path):
                print(
                    f" ✅ {os.path.basename(os.path.dirname(os.path.join(path, file)))}/{file} added"
                )
                if file.endswith(".csv"):
                    csv_files.append(os.path.join(path, file))

    return csv_files


# run a while loop asking the user if they want to add more files or path
def get_paths(path=os.getcwd()):
    paths = []
    selector = "yes"
    while True:
        home_path = path if os.name == "posix" else "C:\\"
        new_path = inquirer.filepath(
            message="Load CSV file or directory",
            qmark="\n📁",
            default=home_path+"/data",
        ).execute()
        # add new path to list of paths
        paths.append(new_path)

        print(f"\n{len(paths)} paths added to load\n")
        selector = inquirer.select(
            message="Will you like to add another file or path?",
            qmark="\n?",
            choices=[
                "yes",
                "no",
            ],
            default="no",
            pointer="👉",
        ).execute()
        if selector == "no":
            paths = get_csv_files(paths)
            break
    return paths


def validate_phone(phone):
    if phone.isdigit():
        return True
    else:
        return False


# clean up csv files by removing duplicate rows and sorting by column by date
# @yaspin(Spinners.bouncingBall,text='Loading...', color="magenta", on_color="on_cyan", attrs=["bold"])
def prepare(file):
    df = pd.read_csv(file)
    # create an array of the head() of the dataframen with the index as key and include the column names as the first row
    # head = np.array(df.head())
    # head = np.insert(head, 0, df.columns, axis=0)

    # ask user to select a row from the first 5 rows
    # header = inquirer.select(
    #     message="Select a row as the header",
    #     choices=head.tolist(),
    #     pointer="👉",
    # ).execute()

    # get the index of the selected row
    # header_index = np.where(head == header)[0][0]

    df = df.replace(r"\n", " ", regex=True)
    df = df.replace(r"\r", " ", regex=True)
    df = df.replace(r"\t", " ", regex=True)
    df = df.dropna(axis=1, how="all")
    df = df.dropna(axis=0, how="all")
    print("✅ Empty columns and rows removed")

    df = df.drop_duplicates()
    df = df.loc[:, ~df.columns.duplicated()]
    print("✅ Duplicate rows and columns removed")
    return df


def clean_csv(files):
    action = inquirer.select(
        message="What do you want to do?",
        choices=clean_menu,
        pointer="👉",
    ).execute()

    print("action: ", action)
    if action == "prepare":
        for file in files:
            prepare(file)
            # ask save or reopen the clean menu
            selector = inquirer.select(
                message="Save or clean more?",
                qmark="\n?",
                choices=[
                    "save",
                    "keep cleaning",
                ],
                pointer="👉",
            ).execute()
            if selector == "save":
                # save the cleaned csv file with the _prepared suffix
                df.to_csv(f"{os.path.splitext(file)[0]}_prepared.csv", index=False)
                print(f"✅ {os.path.basename(file)} saved")
                main()
            else:
                # save a temporary csv file
                df.to_csv(f"{os.path.splitext(file)[0]}_temp.csv", index=False)
                clean_menu[0].name = f"{clean_menu[0].name} ✔️"
                clean_csv(files=[f"{os.path.splitext(file)[0]}_temp.csv"])

    elif action == "split":
        for file in files:
            df = pd.read_csv(file)
            # ask user to select a select multiple columns
            columns = inquirer.checkbox(
                message="Select columns to split",
                choices=df.columns.tolist(),
                pointer="👉",
            ).execute()
        # create a dataframe copy containing only rows where the selected columns are empty
        df_empty = df[df[columns].isnull().all(axis=1)].copy()
        # create a dataframe copy containing only rows where the selected columns are not empty
        df_not_empty = df[~df[columns].isnull().all(axis=1)].copy()

        # ask save or reopen the clean menu
        selector = inquirer.select(
            message="Save or clean more?",
            qmark="\n?",
            choices=[
                "save",
                "keep cleaning",
            ],
            pointer="👉",
        ).execute()
        if selector == "save":
            # save both dataframes as csv files
            df_empty.to_csv(f"{os.path.splitext(file)[0]}_empty.csv", index=False)
            df_not_empty.to_csv(
                f"{os.path.splitext(file)[0]}_not_empty.csv", index=False
            )
            print(f"✅ {os.path.basename(file)} saved")
        else:
            # save both all 3 dataframes as temporary csv files
            df.to_csv(f"{os.path.splitext(file)[0]}_temp.csv", index=False)
            df_empty.to_csv(f"{os.path.splitext(file)[0]}_empty_temp.csv", index=False)
            df_not_empty.to_csv(
                f"{os.path.splitext(file)[0]}_not_empty_temp.csv", index=False
            )
            clean_menu[1].name = f"{clean_menu[1].name} ✔️"
            clean_csv(
                files=[
                    f"{os.path.splitext(file)[0]}_temp.csv",
                    f"{os.path.splitext(file)[0]}_empty_temp.csv",
                    f"{os.path.splitext(file)[0]}_not_empty_temp.csv",
                ]
            )

    elif action == "sort":
        for file in files:
            df = pd.read_csv(file)
            df.sort_values(by=["Date"], inplace=True)
    elif action == "clean":
        for file in files:
            df = pd.read_csv(file)
            df.drop_duplicates(inplace=True)
            df = df[df["Email 1"].apply(validate_email(verify=True))]
            df.sort_values(by=["Date"], inplace=True)
    else:
        print("Not able to prepare csv file")


def merge_csv(files):
    file_one = inquirer.select(
        message="Select a file to merge",
        choices=files,
        pointer="👉",
    ).execute()
    print("file_one: ", file_one)
    file_two = inquirer.select(
        message="Select a file to merge",
        choices=files,
        pointer="👉",
    ).execute()
    print("file_two: ", file_two)
    # read and prepare the selected csv files
    df_one = prepare(file_one)
    df_two = prepare(file_two)

    # let user select which columns to replace
    replace = inquirer.select(
        message="Select columns to replace",
        choices=df_one.columns.tolist(),
        pointer="👉",
    ).execute()
    # let user select which column to check as a condition
    condition_one = inquirer.select(
        message="Select a column to check as a condition",
        choices=df_one.columns.tolist(),
        pointer="👉",
    ).execute()
    # let user select which column to replace_with
    replace_with = inquirer.select(
        message="Select a column to replace with",
        choices=df_two.columns.tolist(),
        pointer="👉",
    ).execute()
    # let user select which column to check as a condition
    condition_two = inquirer.select(
        message="Select a column to check as a condition",
        choices=df_two.columns.tolist(),
        pointer="👉",
    ).execute()

    # add empty rows until the two dataframes have the same number of rows
    if len(df_one) > len(df_two):
        df_two = df_two.append(
            [pd.Series() for _ in range(len(df_one) - len(df_two))], ignore_index=True
        )
    elif len(df_one) < len(df_two):
        df_one = df_one.append(
            [pd.Series() for _ in range(len(df_two) - len(df_one))], ignore_index=True
        )
    else:
        pass

    @yaspin(
        Spinners.bouncingBall,
        text="Loading...",
        color="magenta",
        on_color="on_cyan",
        attrs=["bold"],
    )
    def replace_values(condition_one, condition_two, replace, replace_with):
        #if the last 4 characters of condition_one are equal to the last 4 characters of condition_two ignore the row that contains the colmns
        # replace the value of replace with the value of replace_with
        for index, row in df_one.iterrows():
            if pd.isnull(row[condition_one]):
                break
            else:
                for index_two, row_two in df_two.iterrows():
                    if (str(df_one.loc[index, condition_one])[-4:] == str(df_two.loc[index_two, condition_two])[-4:]):
                        df_one.loc[index, replace] = df_two.loc[index_two, replace_with]
                        print(f'row {row[condition_one]} and row {row_two[condition_two]} are equal')
                        break
                    else:
                        continue
                    break
        return df_one


    # run the replace_values function
    df_one = replace_values(condition_one, condition_two, replace, replace_with)


    # apply the replace_values function to each row of the dataframe

    # df_one[replace] = np.where(
    #     df_one[condition_one].str[-4:].isin(df_two[condition_two].str[-4:]),
    #     df_two[replace_with],
    #     df_one[replace],
    # )            
    # ask save or reopen the clean menu
    selector = inquirer.select(
        message="Save or clean more?",
        qmark="\n?",
        choices=[
            "save",
            "keep cleaning",
        ],
        pointer="👉",
    ).execute()
    if selector == "save":
        # save the merged csv file with the _merged suffix
        df_one.to_csv(f"{os.path.splitext(file_one)[0]}_merged.csv", index=False)
        print(f"✅ {os.path.basename(file_one)} saved")
    else:
        # save the merged csv file as a temporary csv file
        df_one.to_csv(f"{os.path.splitext(file_one)[0]}_merged_temp.csv", index=False)
        merge_menu[0].name = f"{merge_menu[0].name} ✔️"
        merge_csv(files=[f"{os.path.splitext(file_one)[0]}_merged_temp.csv"])


@app.command()
def main():

    selector = inquirer.select(
        message="What do you want to do?",
        choices=menu,
        pointer="👉",
        qmark="\n?",
    ).execute()

    if selector == "clean":
        files = get_paths()
        clean_csv(files)
    elif selector == "merge":
        files = get_paths()
        selector = inquirer.select(
            message="What do you want to do?",
            choices=merge_menu,
            pointer="👉",
        ).execute()
        print("files")
        if selector == "merge":
            print("Merging")
            merge_csv(files)
            
        elif selector == "exit":
            print("Exiting")


if __name__ == "__main__":
    app()
