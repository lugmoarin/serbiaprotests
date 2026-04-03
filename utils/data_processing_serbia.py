# ── utils/data_processing_serbia.py ──────────────────────────────────────────
# All data loading functions for the Serbia Protests app.
# Uses relative paths that work both locally and on Streamlit Cloud.

import pandas as pd
import os

# ── Base path — works locally and on Streamlit Cloud ─────────────────────────
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _path(filename):
    return os.path.join(BASE, "data", filename)

# ── LOAD WEEKLY DATA (for line chart) ────────────────────────────────────────
def load_weekly():
    df = pd.read_csv(_path("weekly_serbia.csv"))
    df["week"] = pd.to_datetime(df["week"])
    return df

# ── LOAD PROTEST EVENTS (for map) ────────────────────────────────────────────
def load_protests():
    df = pd.read_csv(_path("protests_serbia.csv"))
    df["event_date"] = pd.to_datetime(df["event_date"])
    keywords = "student|university|fakultet|faculty|omladina|youth|young people"
    df["is_student"] = df["notes"].str.contains(keywords, case=False, na=False)
    return df

# ── LOAD UNIVERSITY DATA ──────────────────────────────────────────────────────
def load_universities():
    df = pd.read_csv(_path("uni_serbia.csv"), sep=";")
    df.columns = ["city", "public_unis", "private_unis", "n_universities", "n_students"]
    coords = {
        "Belgrade":   (44.8176, 20.4633),
        "Novi Sad":   (45.2671, 19.8335),
        "Niš":        (43.3209, 21.8954),
        "Kragujevac": (44.0165, 20.9114),
        "Novi Pazar": (43.1367, 20.5120),
    }
    df["lat"] = df["city"].map(lambda c: coords.get(c, (None, None))[0])
    df["lon"] = df["city"].map(lambda c: coords.get(c, (None, None))[1])
    return df

# ── PREPARE MAP JSON (legacy — kept for import compatibility) ─────────────────
# Returns a base dict with university data.
# Actual phase data is built directly in streamlit_app.py.
def prepare_map_json():
    unis = load_universities()
    uni_points = [
        {
            "lat": float(row.lat),
            "lon": float(row.lon),
            "city": row.city,
            "n_students": int(row.n_students),
            "n_universities": int(row.n_universities),
        }
        for row in unis.itertuples()
        if row.lat and row.lon
    ]
    return {"universities": uni_points}