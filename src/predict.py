import pandas as pd

df=pd.read_csv("data/processed/base_race_table.csv")
df=df.rename(columns={"grid_position_x": "grid_position"})
df=df.rename(columns={"grid_position_y": "last_10_races_driver_mean"})
df.to_csv("data/processed/base_race_table.csv", index=False)

