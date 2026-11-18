# Tanish – models: LightGBM and MLP

Branch names: `model/lightgbm`, `model/mlp`.

## Do first
Setup steps are in `docs/PLAN.md`. Read the `src/pathsnap/evaluation.py` docstring and
`scripts/models/_template.py`. Do not edit `evaluation.py`; report problems to Shubhika.

## Model 5 – LightGBM (family: gradient boosting)
* File: `scripts/models/train_lightgbm.py`. Trees: no scaler needed.
* Start: `LGBMClassifier(n_estimators=300, learning_rate=0.05, num_leaves=63, subsample=0.8,
  subsample_freq=1, colsample_bytree=0.8, random_state=42, n_jobs=-1, verbose=-1)`. It handles all 3M rows,
  so leave `max_train_rows=None`.
* This is the most likely candidate for Bayesian tuning (stage 7), so also note the training time per fold.

## Model 6 – MLP (family: neural network)
* File: `scripts/models/train_mlp.py`. Pipeline: `StandardScaler` then
  `MLPClassifier(hidden_layer_sizes=(64, 32), alpha=1e-4, early_stopping=True, max_iter=100, random_state=42)`.
* Use `max_train_rows=1_000_000` and record it in `CONFIG`.
* The MLP is the one model that has an epoch-wise history. After the run, load `models/mlp.joblib`, read
  `named_steps[...].loss_curve_` and `validation_scores_` and save them to `results/curves/mlp_history.csv`
  with a script (`scripts/plots/mlp_curves.py`) that plots training loss vs validation score. Only real
  histories may be plotted; do not invent curves for the other models.

## What to produce
1. Harness outputs (`results/experiments/*.json`, `results/model_comparison.csv`).
2. `docs/model_notes/lightgbm.md` and `docs/model_notes/mlp.md` answering, from your own results:
   A1, A2, B5 (hyperparameters + initial values), B6 (log loss objective for both), C7-8 student-test top-1 /
   macro F1 / log loss, C9 over/underfitting with evidence.
3. Handover to stage 7: in `docs/model_notes/lightgbm.md`, list which hyperparameters you would search and the
   ranges, and why. Bayesian optimisation itself (Optuna TPE, group CV over train trips, recorded trials)
   starts only after Shubhika produces the comparison table.

## Commit plan (suggested)
`feat(models): add lightgbm experiment` -> `feat(models): add mlp experiment and history plot`
-> `docs(models): add lightgbm and mlp notes`.
