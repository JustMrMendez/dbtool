#!/usr/bin/env python

from audioop import add
from operator import index
from select import select
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
import re

from lib.cleaner import expclean_csv

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
    Choice("join", "Join 2 files"),
    Choice("compare", "Compare"),
    Separator(),
    Choice("Exit", "exit"),
]

search_menu = [
    Choice("Filter by tag", "filter"),
    Choice("Search by value", "search"),
    Separator(),
    Choice("Exit", "exit"),
]


def get_csv_files(paths):
    csv_files = []
    for path in paths:
        if os.path.isfile(path):
            print(f"\n{path} added")
            if path.endswith(".csv"):
                csv_files.append(path)
            elif path.endswith(".xlsx"):
                df = pd.read_excel(path)
                csv_path = path.replace(".xlsx", ".csv")
                df.to_csv(csv_path, index=False)
                csv_files.append(csv_path)
                print(f"\n{path} converted to {csv_path}")
                os.rename(path, f"old_{path}")
        elif os.path.isdir(path):
            for file in os.listdir(path):
                print(
                    f" ✅ {os.path.basename(os.path.dirname(os.path.join(path, file)))}/{file} added"
                )
                if file.endswith(".csv") or file.endswith(".xlsx"):
                    csv_files.append(os.path.join(path, file))

    return csv_files


def get_paths(path=os.getcwd()):
    paths = []
    selector = "yes"
    while True:
        home_path = path if os.name == "posix" else "data"
        new_path = inquirer.filepath(
            message="Load CSV file or directory",
            qmark="\n📁",
            default=home_path,
        ).execute()
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


def prepare(file):
    if file.endswith(".csv"):
        df = pd.read_csv(file)
        print(df.head())

    elif file.endswith(".xlsx"):
        df = pd.read_excel(file)
        print(df.head())
    df = df.replace(r"\n", " ", regex=True)
    df = df.replace(r"\r", " ", regex=True)
    df = df.replace(r"\t", " ", regex=True)

    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    print("✅ Empty columns and rows removed")

    df = df.drop_duplicates()
    df = df.loc[:, ~df.columns.duplicated()]
    print("✅ Duplicate rows and columns removed")

    df = df[~df.astype(str).apply(lambda x: x.str.contains("page|of")).any(1)]

    return df


def clean_csv(files):
    action = inquirer.select(
        message="What do you want to do?",
        choices=clean_menu,
        pointer="👉",
    ).execute()

    if action == "prepare":
        file = inquirer.select(
            message="Select file to clean",
            qmark="\n📁",
            choices=files,
            default=0,
            pointer="👉",
        ).execute()
        df = expclean_csv(file)
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
            df.to_csv(f"{os.path.splitext(file)[0]}_prepared.csv", index=False)
            print(f"✅ {os.path.basename(file)} saved")
            main()
        else:
            df.to_csv(f"{os.path.splitext(file)[0]}_temp.csv", index=False)
            clean_menu[0].name = f"{clean_menu[0].name} ✔️"
            clean_csv(files=[f"{os.path.splitext(file)[0]}_temp.csv"])

    elif action == "split":
        for file in files:
            df = pd.read_csv(file)
            columns = inquirer.checkbox(
                message="Select columns to split",
                choices=df.columns.tolist(),
                pointer="👉",
            ).execute()
        df_empty = df[df[columns].isnull().all(axis=1)].copy()
        df_not_empty = df[~df[columns].isnull().all(axis=1)].copy()

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
            df_empty.to_csv(f"{os.path.splitext(file)[0]}_empty.csv", index=False)
            df_not_empty.to_csv(
                f"{os.path.splitext(file)[0]}_not_empty.csv", index=False
            )
            print(f"✅ {os.path.basename(file)} saved")
        else:
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
    file_two = inquirer.select(
        message="Select a file to merge",
        choices=files,
        pointer="👉",
    ).execute()
    df_one = prepare(file_one)
    df_two = prepare(file_two)

    condition_one = inquirer.select(
        message="Select a column to check as a condition",
        choices=df_one.columns.tolist(),
        pointer="👉",
    ).execute()

    condition_two = inquirer.select(
        message="Select a column to check as a condition",
        choices=df_two.columns.tolist(),
        pointer="👉",
    ).execute()

    df_one[condition_one] = df_one[condition_one].astype(df_two[condition_two].dtype)

    # df_merged = pd.concat([df_one[~df_one[condition_one].apply(lambda x: df_two[condition_two].str.contains(str(x)).any())], df_two], axis=0, join='inner')
    # df_merged = df_one[
    #     ~df_one[condition_one].apply(
    #         lambda x: df_two[condition_two].str.contains(str(x)).any()
    #     )
    # ]

    # df_4 = merge using the condition: df_one[condition_one].apply(lambda x: df_two[condition_two].str.contains(str(x)).any())
    # and leave only the rows from df_two that didn't match with df_one

    df_two["match"] = df_one[condition_one].apply(
        lambda x: df_two[condition_two].str.contains(str(x)).any()
    )
    
    df_merged = pd.concat(
        [
            df_two[df_two["match"] == True],
            df_one[
                ~df_one[condition_one].apply(
                    lambda x: df_two[condition_two].str.contains(str(x)).any()
                )
            ],
        ],
        axis=0,
        join="inner",
    )
    
    print("🚀 ~ file: main.py:265 ~ df_4", df_merged)

    selector = inquirer.select(
        message="Save or clean more?",
        qmark="\n?",
        choices=[
            "save",
            "keep merging",
        ],
        pointer="👉",
    ).execute()
    if selector == "save":
        df_merged.to_csv(f"{os.path.splitext(file_one)[0]}_merged.csv", index=False)
    else:
        df_one.to_csv(f"{os.path.splitext(file_one)[0]}_merged_temp.csv", index=False)
        merge_menu[0].name = f"{merge_menu[0].name} ✔️"
        merge_csv(files=[f"{os.path.splitext(file_one)[0]}_merged_temp.csv"])


def join_csv(files):
    file_one = inquirer.select(
        message="Select a file 1",
        choices=files,
        pointer="👉",
    ).execute()
    file_two = inquirer.select(
        message="Select a file 2 join",
        choices=files,
        pointer="👉",
    ).execute()
    df_one = prepare(file_one)
    df_two = prepare(file_two)

    df_one = df_one.append(df_two, ignore_index=True)

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
        df_one.to_csv(f"{os.path.splitext(file_one)[0]}_joined.csv", index=False)
        print(f"✅ {os.path.basename(file_one)} saved")
    else:
        df_one.to_csv(f"{os.path.splitext(file_one)[0]}_joined_temp.csv", index=False)
        merge_menu[1].name = f"{merge_menu[1].name} ✔️"
        join_csv(files=[f"{os.path.splitext(file_one)[0]}_joined_temp.csv"])


def compare_csv(files):
    main = inquirer.select(
        message="Select a file 1",
        choices=files,
        pointer="👉",
    ).execute()
    to_merge = inquirer.select(
        message="Select a file 2 join",
        choices=files,
        pointer="👉",
    ).execute()
    df_one = prepare(main)
    df_two = prepare(to_merge)

    column = inquirer.select(
        message="Select a column to compare",
        choices=df_one.columns.tolist(),
        pointer="👉",
    ).execute()
    column_two = inquirer.select(
        message="Select a column to compare",
        choices=df_two.columns.tolist(),
        pointer="👉",
    ).execute()
    df_one = df_one.append(
        df_two[~df_two[column_two].isin(df_one[column])], ignore_index=True
    )

    selector = inquirer.select(
        message="Save or compare more?",
        qmark="\n?",
        choices=[
            "save",
            "keep cleaning",
        ],
        pointer="👉",
    ).execute()
    if selector == "save":
        df_one.to_csv(f"{os.path.splitext(main)[0]}_joined.csv", index=False)
        print(f"✅ {os.path.basename(main)} saved")
    else:
        df_one.to_csv(f"{os.path.splitext(main)[0]}_joined_temp.csv", index=False)
        merge_menu[1].name = f"{merge_menu[1].name} ✔️"
        join_csv(files=[f"{os.path.splitext(main)[0]}_joined_temp.csv"])


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
        elif selector == "join":
            print("Joining")
            join_csv(files)
        elif selector == "compare":
            print("Comparing")
            compare_csv(files)

        elif selector == "exit":
            print("Exiting")


if __name__ == "__main__":
    app()
