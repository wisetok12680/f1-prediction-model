import pandas as pd
import fastf1
from pathlib import Path

SEASONS = [2022, 2023, 2024]

data_dir = Path("data")
cache_dir = data_dir / "raw" / "cache"
interim_dir = data_dir / "interim"

cache_dir.mkdir(parents=True, exist_ok=True)
interim_dir.mkdir(parents=True, exist_ok=True)

fastf1.Cache.enable_cache(str(cache_dir))

rows = []

for season in SEASONS:
    schedule = fastf1.get_event_schedule(season, include_testing=False, backend="ergast")

    for _, event in schedule.iterrows():
        race_name = event["EventName"]
        round_number = event["RoundNumber"]

        try:
            session = fastf1.get_session(season, race_name, "R")
            session.load()
        except Exception:
            continue

        results = session.results
        leader_time = results["Time"].min()

        for _, r in results.iterrows():
            gap = None
            if pd.notna(r["Time"]) and pd.notna(leader_time):
                gap = (r["Time"] - leader_time).total_seconds()

            rows.append({
                "season": season,
                "round": round_number,
                "race_name": race_name,
                "race_date": session.date,
                "driver_id": r["DriverId"],
                "driver_code": r["Abbreviation"],
                "driver_name": r["FullName"],
                "constructor_id": r["TeamId"],
                "constructor_name": r["TeamName"],
                "grid_position": r["GridPosition"],
                "finish_position": r["Position"],
                "status": r["Status"],
                "laps_completed": r["Laps"],
                "points": r["Points"],
                "gap_to_leader_seconds": gap
            })

df = pd.DataFrame(rows)
df = df.sort_values(["season", "round", "finish_position"]).reset_index(drop=True)
df.to_csv(interim_dir / "race_driver_facts.csv", index=False)
