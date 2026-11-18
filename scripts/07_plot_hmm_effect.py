"""Plot classifier-only vs classifier + HMM top-1 accuracy per student_test trip, one panel per model.

Reads results/hmm_<model>/student_test_per_trip.csv written by scripts/05_tune_hmm.py.
Usage: python scripts/07_plot_hmm_effect.py lightgbm mlp
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def main(models: list[str]) -> None:
    fig, axes = plt.subplots(1, len(models), figsize=(6.5 * len(models), 5), sharex=True)
    axes = [axes] if len(models) == 1 else list(axes)
    for ax, model in zip(axes, models):
        per_trip = pd.read_csv(ROOT / "results" / f"hmm_{model}" / "student_test_per_trip.csv", dtype={"trip_id": str})
        rows = range(len(per_trip))
        for row, (_, trip) in zip(rows, per_trip.iterrows()):
            ax.plot([trip.classifier_top1, trip.hmm_top1], [row, row],
                    color="#2e8b57" if trip.hmm_top1 >= trip.classifier_top1 else "#c0392b", lw=2, zorder=1)
        ax.scatter(per_trip.classifier_top1, rows, color="#e67e22", s=45, label="classifier only", zorder=2)
        ax.scatter(per_trip.hmm_top1, rows, color="#1f4e79", s=45, label="classifier + HMM", zorder=2)
        ax.set_yticks(list(rows))
        ax.set_yticklabels(per_trip.trip_id)
        ax.invert_yaxis()
        ax.grid(axis="x", alpha=0.3)
        ax.set_xlabel("observation top-1 accuracy (student_test)")
        ax.set_title(f"{model}: effect of HMM decoding per trip")
        ax.legend(loc="lower left", fontsize=8)
    fig.tight_layout()
    out = ROOT / "results" / "figures"
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / "hmm_effect.png", dpi=150)
    print("wrote", out / "hmm_effect.png")


if __name__ == "__main__":
    main(sys.argv[1:] or ["lightgbm", "mlp"])
