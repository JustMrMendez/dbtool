#!/usr/bin/env python

import typer
from yaspin import yaspin
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
import os
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
    Choice(name="Remove Duplicates", value="remove"),
    Choice(name="Verify Emails", value="fix"),
    Choice(name="Sort by Date", value="sort"),
    Choice(name="Full Clean", value="full_clean"),
    Separator(),
    Choice(name="Save & Exit", value="exit"),
]

merge_menu = [
    Choice("Merge & Save", "merge"),
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
@yaspin(Spinners.bouncingBall,text='Loading...', color="magenta", on_color="on_cyan", attrs=["bold"])
def get_csv_files(paths):
    csv_files = []
    for path in paths:
        if os.path.isfile(path):
            print(f"{path} added")
            if path.endswith(".csv"):
                csv_files.append(path)
        elif os.path.isdir(path):
            for file in os.listdir(path):
                print(f' ✅ {os.path.basename(os.path.dirname(os.path.join(path, file)))}/{file} added')
                if file.endswith(".csv"):
                    csv_files.append(os.path.join(path, file))

    return csv_files

# run a while loop asking the user if they want to add more files or path
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

def clean_csv(files, action):
    if action == "remove":
        for file in files:
            df = pd.read_csv(file)
            df.drop_duplicates(subset="Email 1", keep="first", inplace=True)
    elif action == "fix":
        for file in files:
            df = pd.read_csv(file)
            # iterate through each row and check if the email if there is a email in the row
            for index, row in df.iterrows():
                if validate_email(str(row["Email 1"])):
                    pass
                elif not validate_email(str(row["Email 1"])) and validate_phone(row["Phone 1"]):
                    print(f"{row['Email 1']} Email Invalid but {row['Phone 1']} is a phone number")
                    df.at[index, "Email 1"] = row["Phone 1"]
                    pass
                else:
                    # print the row and remove the row
                    print(f"{row['Email 1']} Email &  {row['Phone 1']} Phone Invalid")
                    df.drop(index, inplace=True)
                    # print the index of the row removed
                    print(f"{index} row removed")


    elif action == "sort":
        for file in files:
            df = pd.read_csv(file)
            df.sort_values(by=['Date'], inplace=True)
    elif action == "clean":
        for file in files:
            df = pd.read_csv(file)
            df.drop_duplicates(inplace=True)
            df = df[df['Email 1'].apply(validate_email(verify=True))]
            df.sort_values(by=['Date'], inplace=True)

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
        selector = inquirer.select(
            message="What do you want to do?",
            choices=clean_menu,
            pointer="👉",
        ).execute()

        if selector == "remove":
            clean_csv(files, "remove")
        elif selector == "fix":
            clean_csv(files, "fix")
        elif selector == "sort":
            clean_csv(files, "sort")
        elif selector == "full_clean":
            clean_csv(files, "clean")
        elif selector == "exit":
            print("Exiting")


if __name__ == "__main__":
    app()
