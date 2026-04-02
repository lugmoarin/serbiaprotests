# utils/data_processing_serbia.py
import pandas as pd


def load_weekly():
    df = pd.read_csv("data/weekly_serbia.csv")
    df["week"] = pd.to_datetime(df["week"])
    return df

def load_monthly():
    pass