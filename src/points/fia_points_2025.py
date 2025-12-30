import pandas as pd
from pathlib import Path

data_dir = Path("data")
processed_dir = data_dir / "processed"

df = pd.read_csv(processed_dir / "predicted_2025_race_order.csv")

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

df = (
    df.sort_values(["round", "predicted_score"], ascending=[True, False])
      .reset_index(drop=True)
)

df["predicted_finish_position"] = (
    df.groupby("round")
      .cumcount()
      .add(1)
)

df["fia_points"] = (
    df["predicted_finish_position"]
    .map(points_map)
    .fillna(0)
    .astype(int)
)

driver_standings = (
    df.groupby(["driver_id", "driver_name"], as_index=False)["fia_points"]
      .sum()
      .sort_values("fia_points", ascending=False)
      .reset_index(drop=True)
)

driver_standings.to_csv(
    processed_dir / "predicted_2025_driver_standings.csv",
    index=False
)
