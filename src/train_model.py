import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
df = pd.read_csv("data/processed/base_race_table.csv")
df = df[df["season"].between(2022, 2024)].copy()
FEATURES = [
    "qualifying_position",
    "constructor_bayesian_podium_rate",
    "last_10_races_mean",
]
X = df[FEATURES]
y = df["is_winner"]
imputer = SimpleImputer(strategy="median")
X_imp = imputer.fit_transform(X)
model = LogisticRegression(
    class_weight="balanced",
    max_iter=1000
)
model.fit(X_imp, y)
coef = pd.Series(model.coef_[0], index=FEATURES)
print(coef.sort_values())
train_probs = model.predict_proba(X_imp)[:, 1]
print(train_probs.min(), train_probs.max())
quali_2025 = pd.read_csv("data/processed/quali_2025.csv")
aus = quali_2025[quali_2025["race_name"] == "Australian Grand Prix"].copy()
constructor_feat = (
    df[["constructor_id", "constructor_bayesian_podium_rate"]]
    .drop_duplicates()
)
driver_feat = (
    df[["driver_id", "last_10_races_mean"]]
    .drop_duplicates()
)
aus = aus.merge(constructor_feat, on="constructor_id", how="left")
aus = aus.merge(driver_feat, on="driver_id", how="left")
X_aus = aus[FEATURES]
X_aus_imp = imputer.transform(X_aus)
aus["win_probability"] = model.predict_proba(X_aus_imp)[:, 1]
aus = aus.sort_values("win_probability", ascending=False)
print(aus[["driver_name", "win_probability"]])
