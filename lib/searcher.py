# import numpy as np
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator


def search_dataframe(df, column_name):
    # Use inquirer to ask the user what they want to search for
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
        # Ask the user for the filter tag
        filter_tag = inquirer.text(
            message="Enter the filter tag:",
            input="filter"
        ).execute()

        # Filter the DataFrame by the specified tag
        filtered_df = df[df[column_name].str.contains(filter_tag, case=False)]
        return filtered_df
    elif search_type == "search":
        # Ask the user for the search value
        search_value = inquirer.text(
            message="Enter the search value:",
        ).execute()

        # Search the DataFrame for the specified value
        search_results = df[df[column_name].str.contains(search_value, case=False)]
        return search_results
    else:
        # Return the original DataFrame if the user chooses to exit
        return df
