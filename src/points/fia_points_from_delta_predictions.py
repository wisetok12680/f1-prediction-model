import pandas as pd
from pathlib import Path

data_dir = Path("data")
processed_dir = data_dir / "processed"

df = pd.read_csv(processed_dir / "predicted_2025_race_results_delta.csv")

points_map = {
    1: 25,
    2: 18,
    3: 15,
    4: 12,
    5: 10,
    6: 8,
    7: 6,
    8: 4,
    9: 2,
    10: 1
}

df["fia_points"] = (
    df["predicted_finish_position"]
      .map(points_map)
      .fillna(0)
      .astype(int)
)

driver_standings = (
    df.groupby("driver_id", as_index=False)
      .agg({
          "driver_name": "last",
          "fia_points": "sum"
      })
      .sort_values("fia_points", ascending=False)
      .reset_index(drop=True)
)

constructor_standings = (
    df.groupby("constructor_id", as_index=False)
      .agg({
          "constructor_name": "last",
          "fia_points": "sum"
      })
      .sort_values("fia_points", ascending=False)
      .reset_index(drop=True)
)

driver_standings.to_csv(
    processed_dir / "predicted_2025_driver_standings_delta.csv",
    index=False
)

constructor_standings.to_csv(
    processed_dir / "predicted_2025_constructor_standings_delta.csv",
    index=False
)
