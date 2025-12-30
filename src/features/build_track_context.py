import pandas as pd
from pathlib import Path

data_dir = Path("data")
interim_dir = data_dir / "interim"
features_dir = data_dir / "features"

features_dir.mkdir(parents=True, exist_ok=True)

tracks = pd.read_csv(interim_dir / "track_metadata.csv")

tracks["event_format"] = tracks["event_format"].astype(str)

tracks["is_sprint_weekend"] = tracks["is_sprint_weekend"].astype(int)

out = tracks[[
    "season",
    "round",
    "race_name",
    "circuit_name",
    "country",
    "is_sprint_weekend"
]]

out.to_csv(features_dir / "track_context.csv", index=False)
