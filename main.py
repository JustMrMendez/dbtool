#!/usr/bin/env python
# A CLI tool for interacting with CSV files.
# Cleans up CSV files by removing duplicate rows and sorting by column by date.
# Merges multiple CSV files into one.
# Searches CSV files for a specific value and prints the row that contains it.
# Menu driven interface, using PyInquirer, typerm and Yaspin.


from webbrowser import get
import typer
from yaspin import yaspin
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.prompts.expand import Choice
from InquirerPy.separator import Separator
from InquirerPy.validator import PathValidator
import os
import pandas as pd
from InquirerPy.utils import patched_print
from yaspin.spinners import Spinners

app = typer.Typer()

menu = [
    Choice(name="Clean CSV", value="clean"),
    Choice(name="Merge CSV", value="merge"),
    Choice(name="Search CSV", value="search"),
    Choice(name="Exit", value="exit"),
]

clean_menu = [
    Choice(name="Remove Duplicates", value="remove"),
    Choice(name="Fix Email endings", value="fix"),
    Choice(name="Sort by Date", value="sort"),
    Choice(name="Full Clean", value="full_clean"),
    Choice(name="Save & Exit", value="exit"),
]

merge_menu = [
    Choice("Pick files", "merge"),
    Choice("Save & Exit", "exit"),
]

search_menu = [
    Choice("Filter by tag", "filter"),
    Choice("Search by value", "search"),
    Choice("Exit", "exit"),
]



# check if path is a file or directory and return a list of o csv files
@yaspin(Spinners.bouncingBall,text='Loading...', color="magenta", on_color="on_cyan", attrs=["bold"])
def get_csv_files(paths):
    csv_files = []
    for path in paths:
        if os.path.isfile(path):
            patched_print(f"{path} added")
            if path.endswith(".csv"):
                csv_files.append(path)
        elif os.path.isdir(path):
            for file in os.listdir(path):
                patched_print(f' ✅ {os.path.basename(os.path.dirname(os.path.join(path, file)))}/{file} added')
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

        patched_print(f'{len(paths)} paths added to load')
        selector = inquirer.select(
            message="Will you like to add another file or path?",
            qmark="\n?",
            choices=[
                'yes',
                'no',
            ],
            pointer="👉",
        ).execute()
        # if selector == "no" break the loop one line code
        if selector == "no":
            get_csv_files(paths)
            break
    return paths


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
            print("Removing duplicates")
        elif selector == "fix":
            print("Fixing email endings")
        elif selector == "sort":
            print("Sorting by date")
        elif selector == "full_clean":
            print("Full clean")
        elif selector == "exit":
            print("Exiting")


if __name__ == "__main__":
    app()
