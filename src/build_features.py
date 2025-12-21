import pandas as pd
import numpy as np


"""Bayesian Rate"""
df=pd.read_csv("data/processed/base_race_table.csv")
k=20
filtered_df=df[df["status"]=="Finished" or ["status"]=="Lapped"]
total_races=filtered_df.groupby("constructor_id").size()
total_podiums=filtered_df.groupby("constructor_id")["is_podium"].sum()
global_total_podiums=filtered_df["is_podium"].sum()
global_race_entries=total_races.agg(sum)

global_podium_rate=global_total_podiums/global_race_entries
alpha=(k*global_podium_rate)
beta=k*(1-global_podium_rate)
bayesian_rate=(alpha+total_podiums)/(alpha+beta+total_podiums+(total_races-total_podiums))
print(bayesian_rate)

bayesian_rate = bayesian_rate.rename("constructor_bayesian_podium_rate").reset_index()

df = df.merge(bayesian_rate, on="constructor_id", how="left")
df.to_csv("data/processed/base_race_table.csv", index=False)




"""print(df.agg("sum",axis="columns"))"""





"""Mean Driver Grid Position over last 10 raecs"""
df=pd.read_csv("data/processed/base_race_table.csv")
last_10_races=df.tail(200)
print(last_10_races.groupby("driver_name")["grid_position"].mean())


""""Qualifying Position Percentile"""
quali_2025 = pd.read_csv("data/processed/quali_2025.csv")

quali_2025["qualifying_position_percentile"] = (
    quali_2025["qualifying_position"] /
    quali_2025.groupby("race_name")["qualifying_position"].transform("max")
)

quali_2025.to_csv("data/processed/quali_2025.csv", index=False)

"""Best Qualification Time"""
quali_2025 = pd.read_csv("data/processed/quali_2025.csv")

aus = quali_2025[quali_2025["race_name"] == "Australian Grand Prix"].copy()

aus["best_quali_time"] = aus["Q3"]
aus["best_quali_time"] = aus["best_quali_time"].fillna(aus["Q2"])
aus["best_quali_time"] = aus["best_quali_time"].fillna(aus["Q1"])
print(aus)
