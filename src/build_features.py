import pandas as pd
import numpy as np

df=pd.read_csv("data/processed/base_race_table.csv")
k=20
filtered_df=df[df["status"]=="Finished"]
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