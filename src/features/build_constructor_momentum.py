import pandas as pd
import numpy as np
from pathlib import Path

data_dir = Path("data")
interim_dir = data_dir / "interim"
features_dir = data_dir / "features"

features_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(interim_dir / "race_driver_facts.csv")

df = df.sort_values(["constructor_id", "season", "round"]).reset_index(drop=True)

df["normalized_gap"] = df["gap_to_leader_seconds"] / df["laps_completed"]
df.loc[df["laps_completed"] == 0, "normalized_gap"] = np.nan

constructor_race = (
    df.groupby(["constructor_id", "season", "round"], as_index=False)
      .agg({"normalized_gap": "mean"})
      .sort_values(["constructor_id", "season", "round"])
)

constructor_race["constructor_gap_mean_last_10"] = (
    constructor_race.groupby("constructor_id")["normalized_gap"]
        .shift(1)
        .rolling(10, min_periods=1)
        .mean()
)

constructor_race["constructor_gap_delta_last_5"] = (
    constructor_race.groupby("constructor_id")["normalized_gap"]
        .shift(1)
        .rolling(5, min_periods=3)
        .apply(lambda x: x.iloc[-1] - x.iloc[0], raw=False)
)

constructor_race["constructor_trend_strength"] = (
    constructor_race.groupby("constructor_id")["normalized_gap"]
        .shift(1)
        .rolling(10, min_periods=3)
        .apply(lambda x: abs(np.polyfit(range(len(x)), x, 1)[0]), raw=False)
)

out = constructor_race[[
    "season",
    "round",
    "constructor_id",
    "constructor_gap_mean_last_10",
    "constructor_gap_delta_last_5",
    "constructor_trend_strength"
]]

out.to_csv(features_dir / "constructor_momentum.csv", index=False)
