# PathSnap – Team 12 project plan

Goal: map-match noisy GPS to a road network. Pipeline:
GPS point -> candidate arcs -> classifier scores each (point, arc) pair -> HMM/Viterbi picks a connected route
-> FastAPI (Laptop 1) -> UI (Laptop 2).

**First evaluation covers: 5+ models, Bayesian tuning, and HMM/Viterbi.** API, UI and report follow.

## Status

| # | Stage | Owner | Status |
|---|-------|-------|--------|
| 1 | Setup, dataset inventory (EDA) | Shubhika | done (`scripts/01_eda.py`) |
| 2 | Reference labels + candidate generation | Shubhika | done |
| 3 | Feature engineering + dataset build | Shubhika | done |
| 4 | Shared evaluation harness | Shubhika | done (`src/pathsnap/evaluation.py`) |
| 5 | Train 6 models (2 each) | Atharva, Yashvantha, Tanish | **to do** |
| 6 | Model comparison table + plots | Shubhika | after 5 |
| 7 | Bayesian optimisation (Optuna) of best model | Tanish (proposed) | after 6 |
| 8 | HMM + Viterbi route reconstruction | Shubhika + Yashvantha (proposed) | after 6 (can start on OOF probabilities from any finished model) |
| 9 | FastAPI backend | Atharva (proposed) | can start now with a stub model |
| 10 | Evaluator UI (Laptop 2) | Yashvantha (proposed) | can start now against the stub API |
| 11 | Folium maps, report PDF | everyone writes their own model sections; Shubhika assembles | last |

Owners for 7-11 are proposals – change them freely, but write the real owner here.

## Design decisions already made (and why) – keep consistent

* **Per-trip local projection** (azimuthal equidistant, metres). Every trip is a different city, so there is
  no shared map; absolute lon/lat and arc ids are never features.
* **Reference labels**: `.route` has no timestamps, so each GPS point is aligned to a route position with a
  monotone DP (`src/pathsnap/labels.py`). Median alignment distance is about 4.5 m on good trips. The derived
  labels are reference labels, not verified ground truth (state this in the report).
* **Excluded trips** (`results/excluded_trips.csv`): train trips 00000033 and 00000054 – their reference
  route covers only part of the GPS track (59% and 89% of points are >50 m from it).
  Rule: exclude a trip if more than 20% of points are >50 m from their aligned arc.
* **Candidates**: all arcs within 100 m, nearest 30 kept. Radius study (`results/radius_study.csv`):
  100 m gives 0.16% candidate miss rate at about 15 candidates per point. Chosen over 75 m (0.41% / 11.4) and
  150 m (0.05% / 21.2; 40% more pairs for little gain).
* **Splits**: 5-fold GroupKFold by trip on the train trips; student_test (10 trips) for development comparison.
  Never random row splits. Evaluator trips are never touched.
* **Metrics** (defined in the `evaluation.py` docstring): pair-level macro F1 and log loss, observation-level
  top-1 accuracy (candidate misses count as wrong), route continuity (reference value is also reported).

## Known data issues (put in the report's data-quality section)

* Large time gaps: train 00000090 (153,064 s max gap, 224 gaps in 536 points), 00000078 (52,810 s),
  00000069, 00000021, 00000011, 00000042. The HMM needs a gap policy.
* Trip lengths range 262 to 19,313 points; long trips dominate row counts.
* Road graphs have up to 421 connected components; arcs are directed (about 90% have a reverse twin).
* Some route arcs repeat within a route (the vehicle revisits a road), so alignment runs over route
  positions, not arc ids.

## Working agreement (history is audited)

* Everyone commits under their **own** git identity. No shared accounts, no copy-pasted code between teams.
* One branch per task: `model/<name>`, `feat/hmm`, `feat/api`, `feat/ui`. Open a PR into `main`; do not
  commit straight to `main`. Small commits, conventional messages: `feat(models): add random forest baseline`,
  `fix(...)`, `docs(...)`, `test(...)`.
* Do not commit `data/`, `.venv/`, secrets, or large model files (`models/*.joblib` is gitignored; ask before
  committing a final model).
* Every number in the report must come from a file in `results/` produced by committed code.
* Every teammate must be able to explain every part in the viva. Disclose any AI assistance as the event requires.

## Setup (each person, once)

```bash
git clone <repo-url> && cd pathsnap
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
export PATHSNAP_DATA="/path/to/Student folder"      # folder containing train/ and student_test/
.venv/bin/python scripts/01_eda.py                  # ~10 s
.venv/bin/python scripts/03_build_dataset.py        # ~40 s, writes data/*.parquet (not committed)
```

## Shared timeline (relative; fix real clock times with the organisers)

1. Now: model training (stage 5) in parallel; API/UI skeletons in parallel.
2. Comparison table, pick best model, Bayesian tuning (stages 6-7).
3. HMM/Viterbi, classifier-only vs +HMM comparison (stage 8). **Needed for first evaluation.**
4. Integrate API + UI, test all student_test trips through the API as stand-ins for the evaluator trips.
5. Folium maps, report, README, final push.

## Open questions for the organisers

* What exactly is expected at the "first phase evaluation before lunch"?
* How will the 10 evaluator trips be delivered to Laptop 1 (same file format as `student_test`, with `.route`)?
