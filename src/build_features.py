import pandas as pd
import numpy as np

df = pd.read_csv("data/processed/base_race_table.csv")

# CONSTRUCTOR BAYESIAN PODIUM RATE

k = 20

filtered_df = df[df["status"].isin(["Finished", "Lapped"])]

total_races = filtered_df.groupby("constructor_id").size()
total_podiums = filtered_df.groupby("constructor_id")["is_podium"].sum()

global_podium_rate = total_podiums.sum() / total_races.sum()

alpha = k * global_podium_rate
beta = k * (1 - global_podium_rate)

constructor_bayes = (
    (alpha + total_podiums)
    / (alpha + beta + total_races)
).rename("constructor_bayesian_podium_rate")

df = df.merge(
    constructor_bayes.reset_index(),
    on="constructor_id",
    how="left"
)

# DRIVER LAST 10 RACES — GRID POSITION MEAN

df = df.sort_values(["driver_id", "race_date"])

df["driver_last_10_grid_mean"] = (
    df.groupby("driver_id")["grid_position"]
      .transform(lambda x: x.shift(1).rolling(10, min_periods=1).mean())
)

# DRIVER LAST 10 RACES — FINISH POSITION MEAN

df["last_10_places_mean"] = (
    df.groupby("driver_id")["position"]
      .transform(lambda x: x.shift(1).rolling(10, min_periods=1).mean())
)
# DRIVER EXPERIENCE (NUMBER OF PRIOR RACES)

df["driver_experience"] = (
    df.groupby("driver_id").cumcount()
)

# SAVE BASE TABLE

df.to_csv("data/processed/base_race_table.csv", index=False)

# LOAD QUALIFYING DATA

quali = pd.read_csv("data/processed/quali_2025.csv")

# QUALIFYING POSITION PERCENTILE

quali["qualifying_position_percentile"] = (
    quali["qualifying_position"]
    / quali.groupby("race_name")["qualifying_position"].transform("max")
)

# BEST QUALIFYING TIME (Q3 > Q2 > Q1)

quali["best_quali_time"] = quali["Q3"]
quali["best_quali_time"] = quali["best_quali_time"].fillna(quali["Q2"])
quali["best_quali_time"] = quali["best_quali_time"].fillna(quali["Q1"])

# SAVE QUALIFYING DATA

quali.to_csv("data/processed/quali_2025.csv", index=False)

# EXAMPLE: AUSTRALIAN GP CHECK

