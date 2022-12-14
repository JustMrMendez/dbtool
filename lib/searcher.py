# import numpy as np
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
import pandas as pd


def search_dataframe(df, column_name):
    filtered_df = pd.DataFrame()
    while True:
        search_menu = [
            Choice("filter", "Filter by tag"),
            Choice("search", "Search by value"),
            Separator(),
            Choice("Exit", "exit"),
        ]
        search_type = inquirer.select(
            message="What do you want to search for?",
            choices=search_menu,
            pointer="🔎",
        ).execute()

        if search_type == "filter":
            filter_tag = inquirer.text(
                message="Enter the filter tag:", input="filter"
            ).execute()

            filtered_df = df[df[column_name].str.contains(filter_tag, case=False)]
            df = filtered_df
        elif search_type == "search":
            search_value = inquirer.text(
                message="Enter the search value:",
            ).execute()

            search_results = df[df[column_name].str.contains(search_value, case=False)]
            # us pandas concat to add the search results to the filtered df
            filtered_df = pd.concat([filtered_df, search_results])
        else:
            return filtered_df
