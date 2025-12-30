import pandas as pd
import fastf1
from pathlib import Path

SEASON = 2025

data_dir = Path("data")
cache_dir = data_dir / "raw" / "cache"
eval_dir = data_dir / "evaluation"

cache_dir.mkdir(parents=True, exist_ok=True)
eval_dir.mkdir(parents=True, exist_ok=True)

fastf1.Cache.enable_cache(str(cache_dir))

rows = []

schedule = fastf1.get_event_schedule(SEASON, include_testing=False)

for _, event in schedule.iterrows():
    race_name = event["EventName"]
    round_number = event["RoundNumber"]

    try:
        session = fastf1.get_session(SEASON, race_name, "R")
        session.load()
    except Exception:
        continue

    results = session.results
    if results is None or results.empty:
        continue

    for _, r in results.iterrows():
        if pd.isna(r["Position"]):
            continue

        rows.append({
            "season": SEASON,
            "round": round_number,
            "race_name": race_name,
            "driver_id": r["DriverId"],
            "finish_position": int(r["Position"])
        })

df = pd.DataFrame(rows)
df.to_csv(eval_dir / "actual_2025_results.csv", index=False)
