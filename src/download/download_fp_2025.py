import pandas as pd
import fastf1
from fastf1.core import DataNotLoadedError
from pathlib import Path

SEASON = 2025

data_dir = Path("data")
cache_dir = data_dir / "raw" / "cache"
interim_dir = data_dir / "interim"

cache_dir.mkdir(parents=True, exist_ok=True)
interim_dir.mkdir(parents=True, exist_ok=True)

fastf1.Cache.enable_cache(str(cache_dir))

rows = []

schedule = fastf1.get_event_schedule(SEASON, include_testing=False, backend="ergast")

for _, event in schedule.iterrows():
    race_name = event["EventName"]
    round_number = event["RoundNumber"]

    for fp in ["FP1", "FP2", "FP3"]:
        try:
            session = fastf1.get_session(SEASON, race_name, fp)
            session.load(laps=True, telemetry=False)
        except Exception:
            continue

        try:
            laps = session.laps
        except DataNotLoadedError:
            continue

        if laps.empty:
            continue

        quicklaps = laps.pick_quicklaps()
        if quicklaps.empty:
            continue

        median_laps = quicklaps.groupby("Driver")["LapTime"].median()
        best_median = median_laps.min()

        for driver, lap in median_laps.items():
            rows.append({
                "season": SEASON,
                "round": round_number,
                "race_name": race_name,
                "driver_code": driver,
                "fp_session": fp,
                "fp_gap_to_best_seconds": (lap - best_median).total_seconds()
            })

df = pd.DataFrame(rows)
df = df.sort_values(["round", "driver_code", "fp_session"]).reset_index(drop=True)
df.to_csv(interim_dir / "fp_2025.csv", index=False)
