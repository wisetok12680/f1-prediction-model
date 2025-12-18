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

for championship_season in range(2022,2025):
    print(f"\nProcessing season {championship_season}")

    try:
        schedule=fastf1.get_event_schedule(championship_season)
    except Exception as e:
        print(f"⚠️ Failed to load schedule for {championship_season}: {e}")
        continue

    round_numbers=schedule["RoundNumber"].dropna().astype(int).unique()
    round_numbers=sorted(round_numbers)

    print(f"Found {len(round_numbers)} rounds")

    for current_round in round_numbers:
        try:
            print(f"  Loading round {current_round}")

            session=fastf1.get_session(
                championship_season,
                current_round,
                "R"
            )
            session.load()

            results=session.results.copy()
            results["season"]=championship_season
            results["round"]=current_round
            results["event_name"]=session.event["EventName"]
            results["session_type"]="R"

            all_results.append(results)

        except Exception as e:
            print(
                f"  ⚠️ Skipping season {championship_season}, "
                f"round {current_round}: {e}"
            )
            continue

df_main=pd.concat(all_results,ignore_index=True)

print("\nFinal dataset shape:",df_main.shape)
print(
    "Unique races:",
    df_main[["season","round"]].drop_duplicates().shape[0]
)

output_path=RAW_DIR/"race_results.csv"
df_main.to_csv(output_path,index=False)
print(f"\nSaved to {output_path}")
