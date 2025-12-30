import pandas as pd
import xgboost as xgb
from pathlib import Path

data_dir = Path("data")
processed_dir = data_dir / "processed"
model_dir = Path("models")

model_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(processed_dir / "base_race_table.csv")

df = df.dropna(subset=["finish_position", "grid_position"])

df["delta_position"] = df["finish_position"] - df["grid_position"]

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

X = df[feature_cols].fillna(df[feature_cols].median())
y = df["delta_position"]

groups = (
    df.groupby(["season", "round"])
      .size()
      .to_numpy()
)

dtrain = xgb.DMatrix(X, label=y)
dtrain.set_group(groups)

params = {
    "objective": "rank:pairwise",
    "eval_metric": "ndcg",
    "learning_rate": 0.05,
    "max_depth": 6,
    "subsample": 0.9,
    "colsample_bytree": 0.9,
    "tree_method": "hist",
    "seed": 42
}

model = xgb.train(
    params=params,
    dtrain=dtrain,
    num_boost_round=500
)

model.save_model(model_dir / "xgb_delta_ranker.json")
