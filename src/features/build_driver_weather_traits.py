import pandas as pd
import numpy as np
from pathlib import Path

data_dir = Path("data")
interim_dir = data_dir / "interim"
features_dir = data_dir / "features"

features_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(interim_dir / "race_driver_facts.csv")
weather = pd.read_csv(interim_dir / "weather_race_level.csv")

df = df.merge(
    weather[["season", "round", "rainfall_flag"]],
    on=["season", "round"],
    how="left"
)

df = df.sort_values(["driver_id", "season", "round"]).reset_index(drop=True)

df["normalized_gap"] = df["gap_to_leader_seconds"] / df["laps_completed"]
df.loc[df["laps_completed"] == 0, "normalized_gap"] = np.nan

wet = df[df["rainfall_flag"] == 1].copy()

wet["driver_wet_gap_mean"] = (
    wet.groupby("driver_id")["normalized_gap"]
       .shift(1)
       .expanding()
       .mean()
)

wet["wet_race_experience"] = (
    wet.groupby("driver_id")
       .cumcount()
)

overall = (
    df.groupby("driver_id")["normalized_gap"]
      .shift(1)
      .expanding()
      .mean()
)

wet = wet.merge(
    overall.rename("driver_overall_gap_mean"),
    left_index=True,
    right_index=True,
    how="left"
)

wet["driver_rain_skill"] = wet["driver_wet_gap_mean"] - wet["driver_overall_gap_mean"]

out = wet[[
    "season",
    "round",
    "race_name",
    "driver_id",
    "driver_rain_skill",
    "wet_race_experience"
]]

out.to_csv(features_dir / "driver_weather_traits.csv", index=False)
