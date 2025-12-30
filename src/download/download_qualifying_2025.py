import pandas as pd
import fastf1
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

    try:
        session = fastf1.get_session(SEASON, race_name, "Q")
        session.load()
    except Exception:
        continue

    results = session.results
    pole_time = results[["Q1", "Q2", "Q3"]].min(axis=1).min()

    for _, r in results.iterrows():
        times = [r["Q3"], r["Q2"], r["Q1"]]
        times = [t for t in times if pd.notna(t)]
        best_time = min(times) if times else None

        gap_to_pole = None
        if best_time is not None and pd.notna(pole_time):
            gap_to_pole = (best_time - pole_time).total_seconds()

        rows.append({
            "season": SEASON,
            "round": round_number,
            "race_name": race_name,
            "driver_id": r["DriverId"],
            "driver_code": r["Abbreviation"],
            "driver_name": r["FullName"],
            "constructor_id": r["TeamId"],
            "constructor_name": r["TeamName"],
            "qualifying_position": r["Position"],
            "best_quali_time_seconds": best_time.total_seconds() if best_time is not None else None,
            "quali_gap_to_pole_seconds": gap_to_pole
        })

df = pd.DataFrame(rows)
df = df.sort_values(["round", "qualifying_position"]).reset_index(drop=True)
df.to_csv(interim_dir / "qualifying_2025.csv", index=False)
