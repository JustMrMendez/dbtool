import os
import pandas as pd
from InquirerPy import inquirer



def fix_whitespace(filenames):
    # ask the user for a column name
    df = pd.read_csv(filenames[0])
    column = inquirer.select(
        message="Select a column to fix whitespace",
        choices=df.columns.tolist(),
        pointer="👉",
    ).execute()

    # iterate through each CSV file
    for filename in filenames:
        # read the CSV file using pandas
        df = pd.read_csv(filename)

        # apply the fix to the selected column in the DataFrame
        df[column] = df[column].apply(lambda x: " ".join(x.split()))

        # create the output directory if it doesn't exist
        dirname = os.path.dirname(filename)
        output_dir = os.path.join(dirname, "whitespace")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # save the fixed DataFrame to a new CSV file in the output directory
        fixed_filename = os.path.join(output_dir, os.path.basename(filename))
        df.to_csv(fixed_filename, index=False)
