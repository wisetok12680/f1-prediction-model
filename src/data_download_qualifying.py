import fastf1
import pandas as pd
from pathlib import Path
DATA_DIR=Path("data")
CACHE_DIR=DATA_DIR/"cache"
RAW_DIR=DATA_DIR/"raw"
CACHE_DIR.mkdir(parents=True,exist_ok=True)
RAW_DIR.mkdir(parents=True,exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))
all_results=[]
for championship_season in range(2022,2026):
    try:
        schedule=fastf1.get_event_schedule(championship_season)
    except Exception:
        continue
    round_numbers=schedule["RoundNumber"].dropna().astype(int).unique()
    round_numbers=sorted(round_numbers)
    for current_round in round_numbers:
        try:
            session=fastf1.get_session(championship_season,current_round,"Q")
            session.load()
            results=session.results.copy()
            results["season"]=championship_season
            results["round"]=current_round
            results["event_name"]=session.event["EventName"]
            results["session_type"]="Q"
            all_results.append(results)
        except Exception:
            continue
df_main=pd.concat(all_results,ignore_index=True)
df_main.to_csv(RAW_DIR/"qualifying_results.csv",index=False)

