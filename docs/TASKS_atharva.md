# Atharva – models: Logistic Regression and KNN

Branch names: `model/logreg`, `model/knn`. One branch, one PR each.

## Do first
Setup steps are in `docs/PLAN.md`. Then read `src/pathsnap/evaluation.py` (top docstring) and
`scripts/models/_template.py`. Do not edit `evaluation.py`; if you think it is wrong, tell Shubhika.

## Model 1 – Logistic Regression (family: linear / probabilistic)
* File: `scripts/models/train_logreg.py` (copy the template).
* Pipeline: `StandardScaler` then `LogisticRegression`. Start with `C=1.0, max_iter=200` and log them.
* Try at least one variant (e.g. `C=0.1`, `class_weight="balanced"`) as a separate run name
  (`logreg_c0p1`); keep both runs, not just the best.
* Why it matters: gives calibrated probabilities and a fast baseline; check whether its log loss is good
  for the HMM.

## Model 2 – KNN (family: instance based)
* File: `scripts/models/train_knn.py`. Pipeline: `StandardScaler` then `KNeighborsClassifier(n_neighbors=15,
  weights="distance", n_jobs=-1)`.
* KNN is slow at prediction time on about 3M rows. Use `max_train_rows=200_000` and **write that in `CONFIG`**
  so it appears in the log. Expect minutes per fold. If too slow, lower the cap and say so.
* Note: KNN probabilities are coarse (multiples of 1/k), so log loss will look bad. Report it, explain it.

## What to produce
1. `results/experiments/<name>.json` and a row in `results/model_comparison.csv` (the harness writes both).
2. One notes file per model: `docs/model_notes/logreg.md`, `docs/model_notes/knn.md`, answering **in your
   own words, from your own results** the report questions (Deliverables 3.2):
   A1 why suitable for PathSnap, A2 strengths and limitations,
   B5 key hyperparameters and initial values, B6 loss / objective,
   C7-8 student-test top-1, macro F1, log loss, C9 over/underfitting and the evidence
   (compare `train_macro_f1` with `cv_macro_f1` and `test_macro_f1` in the CSV).
3. Optional but useful for the report: a confusion-matrix figure from the saved JSON
   (`student_test.confusion_matrix`). Put plotting code in `scripts/plots/`.

## Commit plan (suggested)
`feat(models): add logistic regression experiment` -> `feat(models): add knn experiment`
-> `docs(models): add logreg and knn notes with results`.
