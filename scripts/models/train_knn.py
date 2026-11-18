"""KNN experiments for PathSnap candidate scoring.

Runs:
- knn: n_neighbors=15, weights='distance', max_train_rows=200_000
- knn_k5: n_neighbors=5, weights='distance', max_train_rows=200_000
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from pathsnap.evaluation import run_experiment

FAMILY = "instance_based"

EXPERIMENTS = [
    {
        "name": "knn",
        "config": {
            "n_neighbors": 15,
            "weights": "distance",
            "max_train_rows": 200_000,
            "n_jobs": -1,
        },
    },
    {
        "name": "knn_k5",
        "config": {
            "n_neighbors": 5,
            "weights": "distance",
            "max_train_rows": 200_000,
            "n_jobs": -1,
        },
    },
]


def build_estimator(config: dict):
    """Return a NEW unfitted estimator exposing fit / predict_proba."""
    return make_pipeline(
        StandardScaler(),
        KNeighborsClassifier(
            n_neighbors=config["n_neighbors"],
            weights=config["weights"],
            n_jobs=config.get("n_jobs", -1),
        ),
    )


def main() -> None:
    for exp in EXPERIMENTS:
        name = exp["name"]
        config = exp["config"]
        print(f"\n{'=' * 60}\nRunning experiment: {name}\n{'=' * 60}")
        run_experiment(
            name=name,
            family=FAMILY,
            config=config,
            estimator_factory=lambda cfg=config: build_estimator(cfg),
            seed=42,
            max_train_rows=config["max_train_rows"],
        )


if __name__ == "__main__":
    main()
