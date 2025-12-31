# Formula 1 Delta-Based Race Prediction Model

This repository contains an end-to-end machine learning system for predicting
Formula 1 race outcomes using **FastF1 only**.

The system predicts **race-by-race finishing order**, then derives championship
standings by applying FIA points — championships are **not modeled directly**.

---

## Core Idea: Delta Modeling

Instead of predicting absolute finishing positions, the model predicts:

delta_position = finish_position − grid_position

Final prediction:
predicted_finish = grid_position + predicted_delta

This avoids the common motorsport ML failure mode where models simply learn
qualifying order.

---

## Data & Scope

- **Training data:** 2022–2024 seasons
- **Inference target:** 2025 races
- **Granularity:** One row per driver per race
- **Library:** FastF1 (no Ergast)

Strict leakage controls are enforced:
- All rolling features use shift(1)
- Only pre-race information is used at inference

---

## Models

- **Primary:** XGBoost Ranker (`rank:pairwise`)
- **Auxiliary:** Logistic Regression (probability sanity anchor)
- **Experimental:** Random Forest (non-production)

Models are trained once and frozen for inference.

---

## Features

### Qualifying
- grid_position
- qualifying_position
- quali_gap_to_pole_seconds

### Driver Form (leakage-safe)
- driver_last_10_finish_mean
- driver_gap_mean_last_10
- driver_gap_trend_last_10
- driver_consistency_index

### Constructor Momentum
- constructor_gap_mean_last_10
- constructor_gap_delta_last_5
- constructor_trend_strength

### Track & Context
- driver_track_gap_mean
- driver_track_finish_mean
- driver_track_experience_count
- is_sprint_weekend

### Weather
- driver_rain_skill
- wet_race_experience

---

## Rookie Handling

Rookies are detected implicitly when rolling race features are NaN.

For rookies:
driver_gap_mean_last_10 =
0.6 × fp_gap_to_best_seconds
+ 0.4 × constructor_gap_mean_last_10

Rookie logic automatically disables after the driver completes one race.

No hardcoded rookie flags are used.

---

## Evaluation (2025 Races Only)

- Exact position accuracy: ~16%
- ±1 position accuracy: ~37%
- Mean FIA points MAE: ~2.36
- Mean Spearman correlation: ~0.65

All metrics outperform grid-only baselines.

---


## Status

v1.0 — Stable delta model with validated inference pipeline.
