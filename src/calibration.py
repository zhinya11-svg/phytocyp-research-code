"""Calibration and y-scrambling.

Two questions that reviewers of QSAR and tool papers expect answered.

CALIBRATION: when the model says 0.80, do 80% of those molecules actually inhibit?
  Ranking quality (AUROC) and calibration are different things. A model can rank
  perfectly and still have every probability far too high. Ours over-calls weak
  inhibitors, so we need to measure that rather than describe it.

Y-SCRAMBLING: if we shuffle the labels and retrain, performance must collapse to
  chance. If a model still "works" on nonsense labels, it was memorising structure
  in the split rather than learning chemistry. This is one of the OECD validation
  principles for QSAR models and is cheap to run.

Nothing here retrains anything by itself - the caller supplies held-out predictions
so that the same scaffold split used everywhere else in the project is reused.
"""

import numpy as np
from sklearn.metrics import roc_auc_score

from cyp_pipeline import train_model


def reliability_curve(y_true, probability, n_bins=10):
    """Observed frequency vs mean predicted probability, per bin.

    Returns one dict per NON-EMPTY bin. Empty bins are dropped rather than reported
    as zero, which would otherwise draw a misleading line through the diagram.
    """
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    # np.digitize puts x == 1.0 in an extra bin; clip it back into the last one.
    index = np.clip(np.digitize(probability, edges[1:-1], right=False), 0, n_bins - 1)

    bins = []
    for b in range(n_bins):
        mask = index == b
        if not mask.any():
            continue
        bins.append({
            "bin_low": edges[b],
            "bin_high": edges[b + 1],
            "n": int(mask.sum()),
            "mean_predicted": float(probability[mask].mean()),
            "observed_frequency": float(y_true[mask].mean()),
        })
    return bins


def expected_calibration_error(y_true, probability, n_bins=10):
    """ECE: average gap between predicted probability and observed frequency,
    weighted by how many molecules fall in each bin. 0 is perfect; lower is better."""
    bins = reliability_curve(y_true, probability, n_bins)
    total = sum(b["n"] for b in bins)
    return sum(
        (b["n"] / total) * abs(b["observed_frequency"] - b["mean_predicted"])
        for b in bins
    )


def maximum_calibration_error(y_true, probability, n_bins=10):
    """MCE: the worst single bin. ECE can look fine while one region is badly off."""
    bins = reliability_curve(y_true, probability, n_bins)
    return max(abs(b["observed_frequency"] - b["mean_predicted"]) for b in bins)


def brier_score(y_true, probability):
    """Mean squared error of the probabilities. Combines calibration and sharpness."""
    return float(np.mean((probability - y_true) ** 2))


def calibration_summary(y_true, probability, n_bins=10):
    """Everything the paper needs for one enzyme, in one dict."""
    probability = np.asarray(probability, dtype=float)
    y_true = np.asarray(y_true, dtype=float)
    return {
        "ECE": expected_calibration_error(y_true, probability, n_bins),
        "MCE": maximum_calibration_error(y_true, probability, n_bins),
        "Brier": brier_score(y_true, probability),
        "Mean predicted": float(probability.mean()),
        "Observed rate": float(y_true.mean()),
        "Over-call gap": float(probability.mean() - y_true.mean()),
    }


def y_scramble(X, y, train_index, test_index, n_repeats=10, seed=42):
    """Retrain on shuffled labels and score on the real held-out labels.

    Only the TRAINING labels are permuted. The test labels stay real, which is what
    makes the comparison meaningful: we are asking whether a model built on noise can
    still predict the truth.

    Returns (real_auroc, [scrambled_auroc, ...]).
    """
    rng = np.random.default_rng(seed)

    real = train_model(X[train_index], y[train_index], seed=seed)
    real_auroc = roc_auc_score(y[test_index], real.predict_proba(X[test_index])[:, 1])

    scrambled = []
    for repeat in range(n_repeats):
        shuffled = rng.permutation(y[train_index])
        model = train_model(X[train_index], shuffled, seed=seed + repeat)
        scrambled.append(
            roc_auc_score(y[test_index], model.predict_proba(X[test_index])[:, 1])
        )
    return real_auroc, scrambled
