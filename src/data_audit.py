import pandas as pd
import numpy as np
from pathlib import Path

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

RACE_FILE = RAW_DIR / "race_results.csv"
QUALI_FILE = RAW_DIR / "qualifying_results.csv"
OUT_FILE = OUT_DIR / "base_race_table.csv"


def time_to_ms(t):
    if pd.isna(t):
        return np.nan
    try:
        mins, rest = t.split(":")
        secs, ms = rest.split(".")
        return (int(mins) * 60 + int(secs)) * 1000 + int(ms)
    except:
        return np.nan


def main():
    race = pd.read_csv(RACE_FILE)
    quali = pd.read_csv(QUALI_FILE)

    race = race[race["session_type"].str.lower().str.startswith("r")].copy()
    quali = quali[quali["session_type"].str.lower().str.startswith("q")].copy()


    race = race.rename(
        columns={
            "DriverId": "driver_id",
            "FullName": "driver_name",
            "TeamName": "constructor",
            "GridPosition": "grid_position",
            "Position": "finish_position",
            "event_name": "race_name",
            "Status": "status",
            "Points": "points",
        }
    )

    race = race[
        [
            "season",
            "round",
            "race_name",
            "driver_id",
            "driver_name",
            "constructor",
            "grid_position",
            "finish_position",
            "status",
            "points",
        ]
    ]

    quali = quali.rename(
        columns={
            "DriverId": "driver_id",
            "Position": "qualifying_position",
            "Q1": "q1",
            "Q2": "q2",
            "Q3": "q3",
        }
    )

    for col in ["q1", "q2", "q3"]:
        quali[f"{col}_ms"] = quali[col].apply(time_to_ms)

    quali["qualifying_time_ms"] = quali[["q1_ms", "q2_ms", "q3_ms"]].min(axis=1)

    quali = quali[
        [
            "season",
            "round",
            "driver_id",
            "qualifying_position",
            "qualifying_time_ms",
        ]
    ]

    base = race.merge(
        quali,
        on=["season", "round", "driver_id"],
        how="left",
        validate="1:1",
    )

    base["is_winner"] = (base["finish_position"] == 1).astype(int)
    base["is_podium"] = (base["finish_position"] <= 3).astype(int)

    base = base.sort_values(
        ["season", "round", "finish_position"]
    ).reset_index(drop=True)

    assert base.groupby(["season", "round"])["is_winner"].sum().eq(1).all()

    base.to_csv(OUT_FILE, index=False)
    print(len(base))


if __name__ == "__main__":
    main()
