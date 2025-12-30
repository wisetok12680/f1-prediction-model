import pandas as pd
from pathlib import Path

data_dir = Path("data")
interim_dir = data_dir / "interim"
features_dir = data_dir / "features"
processed_dir = data_dir / "processed"

processed_dir.mkdir(parents=True, exist_ok=True)

facts = pd.read_csv(interim_dir / "race_driver_facts.csv")
qualifying = pd.read_csv(interim_dir / "qualifying_results.csv")

driver_form = pd.read_csv(features_dir / "driver_form.csv")
constructor_momentum = pd.read_csv(features_dir / "constructor_momentum.csv")
track_context = pd.read_csv(features_dir / "track_context.csv")
driver_track = pd.read_csv(features_dir / "driver_track_dominance.csv")
driver_weather = pd.read_csv(features_dir / "driver_weather_traits.csv")

df = facts.merge(
    qualifying,
    on=["season", "round", "race_name", "driver_id", "constructor_id"],
    how="left"
)

df = df.merge(
    driver_form,
    on=["season", "round", "race_name", "driver_id"],
    how="left"
)

df = df.merge(
    constructor_momentum,
    on=["season", "round", "constructor_id"],
    how="left"
)

df = df.merge(
    track_context,
    on=["season", "round", "race_name"],
    how="left"
)

df = df.merge(
    driver_track,
    on=["season", "round", "race_name", "driver_id"],
    how="left"
)

df = df.merge(
    driver_weather,
    on=["season", "round", "race_name", "driver_id"],
    how="left"
)

df = df.sort_values(["season", "round", "finish_position"]).reset_index(drop=True)

df.to_csv(processed_dir / "base_race_table.csv", index=False)
