import pandas as pd
from scipy.stats import spearmanr
from pathlib import Path

data_dir = Path("data")
processed_dir = data_dir / "processed"
eval_dir = data_dir / "evaluation"

pred = pd.read_csv(processed_dir / "predicted_2025_race_results_delta.csv")
actual = pd.read_csv(eval_dir / "actual_2025_results.csv")

df = pred.merge(
    actual,
    on=["season", "round", "driver_id"],
    how="inner"
)

assert len(df) > 0

df["exact_match"] = (
    df["predicted_finish_position"] == df["finish_position"]
)

df["within_1"] = (
    (df["predicted_finish_position"] - df["finish_position"]).abs() <= 1
)

points_map = {
    1: 25, 2: 18, 3: 15, 4: 12, 5: 10,
    6: 8, 7: 6, 8: 4, 9: 2, 10: 1
}

df["actual_points"] = df["finish_position"].map(points_map).fillna(0)
df["predicted_points"] = df["predicted_finish_position"].map(points_map).fillna(0)

exact_acc = df["exact_match"].mean()
within1_acc = df["within_1"].mean()
points_mae = (df["actual_points"] - df["predicted_points"]).abs().mean()

corrs = []
for rnd, g in df.groupby("round"):
    corr, _ = spearmanr(
        g["finish_position"],
        g["predicted_finish_position"]
    )
    corrs.append(corr)

mean_spearman = sum(corrs) / len(corrs)

print("Races evaluated:", df["round"].nunique())
print("Exact position accuracy:", round(exact_acc, 3))
print("Within ±1 accuracy:", round(within1_acc, 3))
print("Mean points MAE:", round(points_mae, 2))
print("Mean Spearman correlation:", round(mean_spearman, 3))
