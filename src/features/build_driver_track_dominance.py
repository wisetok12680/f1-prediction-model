import pandas as pd
import numpy as np
from pathlib import Path

data_dir = Path("data")
interim_dir = data_dir / "interim"
features_dir = data_dir / "features"

features_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(interim_dir / "race_driver_facts.csv")

df = df.sort_values(["driver_id", "race_name", "season", "round"]).reset_index(drop=True)

df["normalized_gap"] = df["gap_to_leader_seconds"] / df["laps_completed"]
df.loc[df["laps_completed"] == 0, "normalized_gap"] = np.nan

df["driver_track_gap_mean"] = (
    df.groupby(["driver_id", "race_name"])["normalized_gap"]
      .shift(1)
      .expanding()
      .mean()
)

df["driver_track_finish_mean"] = (
    df.groupby(["driver_id", "race_name"])["finish_position"]
      .shift(1)
      .expanding()
      .mean()
)

df["driver_track_experience_count"] = (
    df.groupby(["driver_id", "race_name"])
      .cumcount()
)

out = df[[
    "season",
    "round",
    "race_name",
    "driver_id",
    "driver_track_gap_mean",
    "driver_track_finish_mean",
    "driver_track_experience_count"
]]

out.to_csv(features_dir / "driver_track_dominance.csv", index=False)
