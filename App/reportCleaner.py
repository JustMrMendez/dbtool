from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.core.window import Window
import os
import pandas as pd
from kivy.config import Config

def on_drop_file(filename):
    # read the file
    df = pd.DataFrame()
    # convert binary to string
    filename = filename.decode("utf-8")
    print("✔️", filename)
    if  filename.endswith(".csv"):
        df = pd.read_csv(filename)
        print(df.head())
        df = df.replace(r"\n", " ", regex=True)
        df = df.replace(r"\r", " ", regex=True)
        df = df.replace(r"\t", " ", regex=True)

        # Remove empty columns or unnamed columns
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
        print("✅ Empty columns and rows removed")

        df = df.drop_duplicates()
        df = df.loc[:, ~df.columns.duplicated()]
        print("✅ Duplicate rows and columns removed")

        # drop any row that contains the word page and of in any column
        df = df[~df.astype(str).apply(lambda x: x.str.contains("page|of")).any(1)]

    elif filename.endswith(".xlsx"):
        df = pd.read_excel(filename)
        print(df.head())
        df = df.replace(r"\n", " ", regex=True)
        df = df.replace(r"\r", " ", regex=True)
        df = df.replace(r"\t", " ", regex=True)

        # Remove empty columns or unnamed columns
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
        print("✅ Empty columns and rows removed")

        df = df.drop_duplicates()
        df = df.loc[:, ~df.columns.duplicated()]
        print("✅ Duplicate rows and columns removed")

        # drop any row that contains the word page and of in any column
        df = df[~df.astype(str).apply(lambda x: x.str.contains("page|of")).any(1)]
    # save the file to the desktop
    df.to_csv(os.path.join(os.path.expanduser('~'), 'Desktop', 'cleaned.csv'), index=False)

class ReportCleaner(Widget):
    pass

class ReportCleanerApp(App):
    def build(self):
        Config.set('graphics', 'width', '200')
        Config.set('graphics', 'height', '200')
        Config.set('graphics', 'resizable', False)
        Config.write()
        Window.bind(on_drop_file=on_drop_file)
        return ReportCleaner()

if __name__ == "__main__":
    try:
        ReportCleanerApp().run()
    except Exception as e:
        print(e)
        input("Press enter.")