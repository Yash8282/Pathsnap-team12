# Yashvantha – models: Random Forest and Extra Trees

Branch names: `model/random-forest`, `model/extra-trees`.

## Do first
Setup steps are in `docs/PLAN.md`. Read the `src/pathsnap/evaluation.py` docstring and
`scripts/models/_template.py`. Do not edit `evaluation.py`; report problems to Shubhika.

## Model 3 – Random Forest (family: tree ensemble, bagging)
* File: `scripts/models/train_random_forest.py`. No scaler needed for trees.
* Start: `RandomForestClassifier(n_estimators=200, max_depth=20, min_samples_leaf=5, n_jobs=-1,
  random_state=42)`. On about 3M rows fitting is slow: use `max_train_rows=800_000` first and record it in `CONFIG`.
* Probabilities from forests are vote fractions; check log loss and think about why it may be worse than
  boosting.

## Model 4 – Extra Trees (family: tree ensemble, randomised splits)
* File: `scripts/models/train_extra_trees.py`. Start: `ExtraTreesClassifier(n_estimators=200,
  min_samples_leaf=5, n_jobs=-1, random_state=42)`, same row cap as Random Forest so the comparison is fair.
* Compare with Random Forest: variance, speed, probability quality.

## What to produce
1. Harness outputs (`results/experiments/*.json`, `results/model_comparison.csv`).
2. `docs/model_notes/random_forest.md` and `docs/model_notes/extra_trees.md` answering, from your own results:
   A1 suitability, A2 strengths/limitations, B5 hyperparameters + initial values, B6 objective (Gini impurity
   or entropy, as used), C7-8 student-test top-1 / macro F1 / log loss, C9 over/underfitting with evidence.
   For overfitting: trees with unlimited depth will show train macro F1 far above CV; show it.
3. Feature importances (`feature_importances_` from the saved model) as a figure; code in `scripts/plots/`.
   This helps justify the feature choices in the report.

## Commit plan (suggested)
`feat(models): add random forest experiment` -> `feat(models): add extra trees experiment`
-> `docs(models): add tree ensemble notes and feature importance plot`.
