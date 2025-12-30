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
        rows.append({
            "season": season,
            "round": event["RoundNumber"],
            "race_name": event["EventName"],
            "circuit_name": event["Location"],
            "country": event["Country"],
            "event_format": event["EventFormat"],
            "is_sprint_weekend": int(event["EventFormat"] != "conventional")
        })

df = pd.DataFrame(rows)
df = df.sort_values(["season", "round"]).reset_index(drop=True)
df.to_csv(interim_dir / "track_metadata.csv", index=False)
