import pandas as pd
import numpy as np
from pathlib import Path

data_dir = Path("data")
interim_dir = data_dir / "interim"
features_dir = data_dir / "features"

features_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(interim_dir / "race_driver_facts.csv")

df = df.sort_values(["driver_id", "season", "round"]).reset_index(drop=True)

df["normalized_gap"] = df["gap_to_leader_seconds"] / df["laps_completed"]
df.loc[df["laps_completed"] == 0, "normalized_gap"] = np.nan

df["driver_last_10_finish_mean"] = (
    df.groupby("driver_id")["finish_position"]
      .shift(1)
      .rolling(10, min_periods=1)
      .mean()
)

df["driver_gap_mean_last_10"] = (
    df.groupby("driver_id")["normalized_gap"]
      .shift(1)
      .rolling(10, min_periods=1)
      .mean()
)

df["driver_gap_trend_last_10"] = (
    df.groupby("driver_id")["normalized_gap"]
      .shift(1)
      .rolling(10, min_periods=3)
      .apply(lambda x: np.polyfit(range(len(x)), x, 1)[0], raw=False)
)

df["driver_consistency_index"] = (
    df.groupby("driver_id")["finish_position"]
      .shift(1)
      .rolling(10, min_periods=3)
      .std()
)

out = df[[
    "season",
    "round",
    "race_name",
    "driver_id",
    "driver_last_10_finish_mean",
    "driver_gap_mean_last_10",
    "driver_gap_trend_last_10",
    "driver_consistency_index"
]]

out.to_csv(features_dir / "driver_form.csv", index=False)
