"""Evidence for the feature-engineering choices (train partition only).

Outputs:
  results/figures/feature_distributions.png   true vs non-true candidate distributions
  results/figures/feature_importance.png      LightGBM gain importance (exploratory; fit on a train subsample)
  results/feature_missingness.csv             explicit missingness / validity flags per feature
  results/feature_summary.csv                 per-feature mean for true vs non-true candidates
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from lightgbm import LGBMClassifier  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pathsnap.features import FEATURE_COLUMNS  # noqa: E402

SEED = 42
BLUE, ORANGE = "#1f4e79", "#e67e22"


def main() -> None:
    pairs = pd.read_parquet(ROOT / "data" / "features_train.parquet")
    obs = pd.read_parquet(ROOT / "data" / "obs_train.parquet")
    figures = ROOT / "results" / "figures"
    figures.mkdir(parents=True, exist_ok=True)

    # --- missingness / validity (no NaNs exist; uncertainty is carried by explicit flags)
    missing = pd.DataFrame({
        "check": ["NaN values in any feature", "heading unreliable (heading_valid == 0)",
                  "no valid neighbour context (ctx_valid_count == 0)",
                  "fewer than 4 valid context neighbours", "observations with no candidate arc"],
        "share_percent": [100 * float(pairs[FEATURE_COLUMNS].isna().any(axis=1).mean()),
                          100 * float((pairs.heading_valid == 0).mean()),
                          100 * float((pairs.ctx_valid_count == 0).mean()),
                          100 * float((pairs.ctx_valid_count < 4).mean()),
                          100 * float(1 - pairs.groupby(["trip_id", "obs_idx"]).ngroups / len(obs))],
    })
    missing.to_csv(ROOT / "results" / "feature_missingness.csv", index=False)
    print(missing.round(3).to_string(index=False))

    summary = pairs.groupby("y")[FEATURE_COLUMNS].mean().T.rename(columns={0: "mean_non_true", 1: "mean_true"})
    summary.to_csv(ROOT / "results" / "feature_summary.csv")

    # --- distributions, true vs non-true
    sample = pairs.sample(400_000, random_state=SEED)
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    panels = [("dist_m", "Distance point -> arc (m)", (0, 100)), ("ctx_dist_mean", "Mean distance over +/-6 s context (m)", (0, 100)),
              ("heading_cos", "cos(vehicle heading, arc direction), valid heading only", (-1, 1)),
              ("t_frac", "Position along arc (0 = start, 1 = end)", (0, 1)),
              ("speed_ms", "Speed (m/s)", (0, 40)), ("dist_minus_min", "Distance minus nearest candidate's (m)", (0, 60))]
    for ax, (column, title, limits) in zip(axes.ravel(), panels):
        data = sample[sample.heading_valid == 1] if column == "heading_cos" else sample
        for label, color, name in ((0, ORANGE, "not the reference arc"), (1, BLUE, "reference arc")):
            ax.hist(data.loc[data.y == label, column].clip(*limits), bins=50, range=limits, density=True,
                    alpha=0.6, color=color, label=name)
        ax.set_title(title, fontsize=10)
        ax.legend(fontsize=8)
    fig.suptitle("Feature distributions: reference arc vs other candidates (train, 400k sampled candidate pairs)")
    fig.tight_layout()
    fig.savefig(figures / "feature_distributions.png", dpi=150)
    plt.close(fig)

    # --- true-arc rate by distance rank
    rank_rate = pairs[pairs.dist_rank < 10].groupby("dist_rank").y.mean()
    print("share of candidates that are the reference arc, by distance rank:\n", rank_rate.round(3).to_string())

    # --- exploratory importance
    fit = pairs.sample(600_000, random_state=SEED)
    model = LGBMClassifier(n_estimators=200, learning_rate=0.05, num_leaves=63, subsample=0.8, subsample_freq=1,
                           colsample_bytree=0.8, importance_type="gain", random_state=SEED, n_jobs=-1, verbose=-1)
    model.fit(fit[FEATURE_COLUMNS], fit.y)
    importance = pd.Series(model.feature_importances_, index=FEATURE_COLUMNS)
    importance = (100 * importance / importance.sum()).sort_values()
    importance.sort_values(ascending=False).round(3).to_csv(ROOT / "results" / "feature_importance.csv", header=["gain_percent"])
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(importance.index, importance.values, color=BLUE)
    ax.set_xlabel("share of total split gain (%)")
    ax.set_title("LightGBM feature importance (exploratory fit, 600k train rows)")
    fig.tight_layout()
    fig.savefig(figures / "feature_importance.png", dpi=150)
    print("\ntop features by gain:\n", importance.sort_values(ascending=False).head(8).round(2).to_string())


if __name__ == "__main__":
    main()
