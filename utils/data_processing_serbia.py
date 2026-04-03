# ── utils/data_processing_serbia.py ──────────────────────────────────────────
# Data loading and processing functions for the Serbia Protests app.
# Keeps all data logic separate from the Streamlit display code.

import pandas as pd
import json

# ── LOAD WEEKLY DATA (for line chart) ────────────────────────────────────────
def load_weekly():
    df = pd.read_csv("data/weekly_serbia.csv")
    df["week"] = pd.to_datetime(df["week"])
    return df

# ── LOAD PROTEST EVENTS (for map) ────────────────────────────────────────────
def load_protests():
    df = pd.read_csv("data/protests_serbia.csv")
    df["event_date"] = pd.to_datetime(df["event_date"])

    # Flag student protests using same keywords as R script
    keywords = "student|university|fakultet|faculty|omladina|youth|young people"
    df["is_student"] = df["notes"].str.contains(keywords, case=False, na=False)

    # Keep only needed columns for map
    df = df[[
        "event_date", "latitude", "longitude",
        "location", "admin1", "sub_event_type",
        "is_student", "notes"
    ]].dropna(subset=["latitude", "longitude"])

    return df

# ── LOAD UNIVERSITY DATA ──────────────────────────────────────────────────────
def load_universities():
    df = pd.read_csv("data/uni_serbia.csv", sep=";")
    df.columns = ["city", "public_unis", "private_unis", "n_universities", "n_students"]

    # Manual coordinates for each university city
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

# ── PREPARE MAP DATA AS JSON (for HTML component) ────────────────────────────
def prepare_map_json():
    protests = load_protests()
    unis = load_universities()

    # Phase definitions
    phase_filters = {
        "phase1": protests[protests["event_date"] < "2024-11-01"],
        "phase2": protests[
            (protests["event_date"] >= "2024-11-01") &
            (protests["event_date"] <  "2024-12-01")
        ],
        "phase3": protests[
            (protests["event_date"] >= "2024-11-01") &
            (protests["event_date"] <  "2025-03-01")
        ],
        "phase4": protests[
            (protests["event_date"] >= "2024-11-01") &
            (protests["event_date"] <  "2025-03-01")
        ],
        "phase5": protests[protests["event_date"] >= "2025-03-01"],
    }

    def df_to_points(df):
        return [
            {
                "lat": row.latitude,
                "lon": row.longitude,
                "student": bool(row.is_student),
                "location": row.location,
                "date": str(row.event_date.date()),
            }
            for row in df.itertuples()
        ]

    uni_points = [
        {
            "lat": row.lat,
            "lon": row.lon,
            "city": row.city,
            "n_students": int(row.n_students),
            "n_universities": int(row.n_universities),
        }
        for row in unis.itertuples()
        if row.lat and row.lon
    ]

    return {
        "phase1": df_to_points(phase_filters["phase1"]),
        "phase2": df_to_points(phase_filters["phase2"]),
        "phase3": df_to_points(phase_filters["phase3"]),
        "phase4": df_to_points(phase_filters["phase4"]),
        "phase5": df_to_points(phase_filters["phase5"]),
        "universities": uni_points,
    }