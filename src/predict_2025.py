import pandas as pd
import numpy as np
import xgboost as xgb
from pathlib import Path

data_dir = Path("data")
interim_dir = data_dir / "interim"
features_dir = data_dir / "features"
processed_dir = data_dir / "processed"
model_dir = Path("models")

qualifying_2025 = pd.read_csv(interim_dir / "qualifying_2025.csv")
fp_2025 = pd.read_csv(interim_dir / "fp_2025.csv")

driver_form = pd.read_csv(features_dir / "driver_form.csv")
constructor_momentum = pd.read_csv(features_dir / "constructor_momentum.csv")
track_context = pd.read_csv(features_dir / "track_context.csv")
driver_track = pd.read_csv(features_dir / "driver_track_dominance.csv")
driver_weather = pd.read_csv(features_dir / "driver_weather_traits.csv")

model = xgb.Booster()
model.load_model(model_dir / "xgb_ranker.json")

last_known_form = (
    driver_form.sort_values(["season", "round"])
    .groupby("driver_id")
    .tail(1)
)

last_constructor_form = (
    constructor_momentum.sort_values(["season", "round"])
    .groupby("constructor_id")
    .tail(1)
)

df = qualifying_2025.copy()

df["grid_position"] = df["qualifying_position"]

df = df.merge(
    last_known_form.drop(columns=["season", "round", "race_name"]),
    on="driver_id",
    how="left"
)

df = df.merge(
    last_constructor_form.drop(columns=["season", "round"]),
    on="constructor_id",
    how="left"
)

df = df.merge(
    track_context,
    on=["season", "round", "race_name"],
    how="left"
)

df = df.merge(
    driver_track.groupby(["driver_id", "race_name"])
        .tail(1)
        .drop(columns=["season", "round"]),
    on=["driver_id", "race_name"],
    how="left"
)

df = df.merge(
    driver_weather.groupby("driver_id")
        .tail(1)
        .drop(columns=["season", "round", "race_name"]),
    on="driver_id",
    how="left"
)

fp_summary = (
    fp_2025.groupby(["round", "driver_code"])["fp_gap_to_best_seconds"]
    .mean()
    .reset_index()
)

df = df.merge(
    fp_summary,
    on=["round", "driver_code"],
    how="left"
)

rookie_mask = df["driver_last_10_finish_mean"].isna()

df.loc[rookie_mask, "driver_gap_mean_last_10"] = (
    0.6 * df.loc[rookie_mask, "fp_gap_to_best_seconds"]
    + 0.4 * df.loc[rookie_mask, "constructor_gap_mean_last_10"]
)

df.loc[rookie_mask, "driver_last_10_finish_mean"] = df.loc[
    rookie_mask, "qualifying_position"
]

feature_cols = [
    "grid_position",
    "qualifying_position",
    "best_quali_time_seconds",
    "quali_gap_to_pole_seconds",
    "driver_last_10_finish_mean",
    "driver_gap_mean_last_10",
    "driver_gap_trend_last_10",
    "driver_consistency_index",
    "constructor_gap_mean_last_10",
    "constructor_gap_delta_last_5",
    "constructor_trend_strength",
    "driver_track_gap_mean",
    "driver_track_finish_mean",
    "driver_track_experience_count",
    "driver_rain_skill",
    "wet_race_experience",
    "is_sprint_weekend"
]

X = df[feature_cols].astype(float)
X = X.fillna(X.median())

groups = df.groupby("round").size().to_numpy()

dtest = xgb.DMatrix(X)
dtest.set_group(groups)

df["predicted_score"] = model.predict(dtest)

df = df.sort_values(["round", "predicted_score"], ascending=[True, False])

df.to_csv(processed_dir / "predicted_2025_race_order.csv", index=False)
