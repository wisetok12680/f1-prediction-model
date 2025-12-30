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

        weather = session.weather_data

        if weather is None or weather.empty:
            continue

        rows.append({
            "season": season,
            "round": round_number,
            "race_name": race_name,
            "air_temperature": weather["AirTemp"].mean(),
            "track_temperature": weather["TrackTemp"].mean(),
            "humidity": weather["Humidity"].mean(),
            "wind_speed": weather["WindSpeed"].mean(),
            "rainfall_flag": int(weather["Rainfall"].max() > 0)
        })

df = pd.DataFrame(rows)
df = df.sort_values(["season", "round"]).reset_index(drop=True)
df.to_csv(interim_dir / "weather_race_level.csv", index=False)
