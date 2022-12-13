from distutils.command.clean import clean
import os
from shutil import move
import time
import pandas as pd
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler


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


if __name__ == "__main__":

    def prepare(file):
        df = pd.DataFrame()
        if file.endswith(".csv"):
            df = read_csv(file)
            # ask user to select index column
            # selector = inquirer.select(
            #     message=f"Select header to use as index for {file}",
            #     qmark="\n📁",
            #     choices=[0, 1, 2, 3, 4],
            #     default=0,
            #     pointer="👉",
            # ).execute()

            # Remove empty columns or unnamed columns
            df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
            print("✅ Empty columns and rows removed")

            df = df.drop_duplicates()
            df = df.loc[:, ~df.columns.duplicated()]
            print("✅ Duplicate rows and columns removed")

            # drop any row that contains the word page and of in any column
            df = df[~df.astype(str).apply(lambda x: x.str.contains("page|of")).any(1)]

        elif file.endswith(".xlsx"):
            # selector = inquirer.select(
            #     message=f"Select header to use as index for {file}",
            #     qmark="\n📁",
            #     choices=[0, 1, 2, 3, 4],
            #     default=0,
            #     pointer="👉",
            # ).execute()
            df = pd.read_excel(file)
            # save the file as a csv in the same folder
            df.to_csv(
                os.path.join(
                    os.path.dirname(file), f"{os.path.basename(file).split('.')[0]}.csv"
                ),
                index=False,
            )
            # print(df.head())
            # df = df.replace(r"\n", " ", regex=True)
            # df = df.replace(r"\r", " ", regex=True)
            # df = df.replace(r"\t", " ", regex=True)

            # Remove empty columns or unnamed columns
            df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
            print("✅ Empty columns and rows removed")

            df = df.drop_duplicates()
            df = df.loc[:, ~df.columns.duplicated()]
            print("✅ Duplicate rows and columns removed")

            # drop any row that contains the word page and of in any column
            df = df[~df.astype(str).apply(lambda x: x.str.contains("page|of")).any(1)]

        return df

    # watch for a folder in the desktop called ReportCleaner
    # if folder is not found, create it
    # if folder is found, watch for files to be added
    # if file is added, run the prepare function
    # if file is not a csv or xlsx, skip it
    eventHandler = LoggingEventHandler()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # get user desktop path
    desktop = os.path.join(os.path.join(os.environ["USERPROFILE"]), "Desktop")

    path = os.path.join(desktop, "ReportCleaner")

    def clean(event):
        file = event.src_path
        print(f"📁 {file} added to ReportCleaner folder")
        df = prepare(file)
        clean_path = os.path.join(path, "cleaned")
        print(f"📁 {file} cleaned and saved to {clean_path}")
        # save the file to desktop
        df.to_csv(
            os.path.join(desktop, f"{time.strftime('%Y%m%d-%H%M%S')}.csv"), index=False
        )
        move(file, clean_path)
        print("✅ File cleaned")
        print("✅ File saved")
        print("👋 Goodbye")

    if not os.path.exists(path):
        os.makedirs(path)
        print("📁 ReportCleaner folder created on desktop")
    # elif a cleaned folder is not found, create it
    elif not os.path.exists(os.path.join(path, "cleaned")):
        os.makedirs(os.path.join(path, "cleaned"))
        print("📁 ReportCleaner/cleaned folder created on desktop")
    else:
        print("📁 ReportCleaner folder found on desktop")
        print("📁 ReportCleaner/cleaned folder found on desktop")
        observer = Observer()
        eventHandler.on_created = clean
        # eventHandler.on_modified = clean
        observer.schedule(eventHandler, path, recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
