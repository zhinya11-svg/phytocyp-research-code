"""Supplementary validation analyses (DOME reporting): baseline model, confidence intervals, train versus test.

Nothing here changes a model or a setting used elsewhere. The folds, features, XGBoost settings and metrics are
those of cyp_pipeline (scaffold-grouped 5-fold cross-validation, threshold 0.5); the baseline is the logistic
regression of section 3.1.
"""

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import cyp_pipeline as cp

METRICS = ["AUROC", "AUPRC", "Sensitivity", "Specificity", "Balanced accuracy"]
MODELS = ["Logistic regression", "XGBoost"]


def make_logreg(seed=42):
    """The baseline of section 3.1: standardised features, logistic regression."""
    return make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, random_state=seed))


def make_model(name, seed=42):
    if name == "XGBoost":
        return cp.XGBClassifier(random_state=seed, **cp.XGB_SETTINGS)
    return make_logreg(seed)


def cross_validate_both(X, y, scaffolds, n_splits=5, seed=42):
    """Same folds as cp.cross_validate. Returns per-fold train and test scores for both models, and the
    pooled out-of-fold test probabilities (one value per compound, from the fold in which it was held out)."""
    groups = pd.factorize(pd.Series(scaffolds))[0]
    rows = []
    oof = {m: np.full(len(y), np.nan) for m in MODELS}
    for fold, (train_i, test_i) in enumerate(GroupKFold(n_splits=n_splits).split(X, y, groups=groups), start=1):
        for name in MODELS:
            model = make_model(name, seed)
            model.fit(X[train_i], y[train_i])
            for part, idx in (("train", train_i), ("test", test_i)):
                p = model.predict_proba(X[idx])[:, 1]
                if part == "test":
                    oof[name][idx] = p
                rows.append({"Model": name, "Fold": fold, "Part": part, "n": int(len(idx)),
                             **cp.score(y[idx], p)})
    assert not any(np.isnan(v).any() for v in oof.values()), "a compound was never held out"
    return pd.DataFrame(rows), oof


def t_interval(values, level=0.95):
    """Mean and t-based interval across folds: mean +/- t(0.975, k-1) * sd / sqrt(k), sd with ddof=1."""
    v = np.asarray(values, dtype=float)
    k = len(v)
    mean, sd = v.mean(), v.std(ddof=1)
    half = stats.t.ppf(0.5 + level / 2, k - 1) * sd / np.sqrt(k)
    return mean, sd, mean - half, mean + half


def bootstrap_interval(y, p, n_boot=1000, seed=42, level=0.95):
    """Percentile bootstrap of the five metrics on the pooled out-of-fold predictions (compounds resampled)."""
    rng = np.random.default_rng(seed)
    y = np.asarray(y)
    n = len(y)
    draws = {m: [] for m in METRICS}
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        s = cp.score(y[idx], p[idx])
        for m in METRICS:
            draws[m].append(s[m])
    lo, hi = (1 - level) / 2 * 100, (1 + level) / 2 * 100
    return {m: (float(np.percentile(draws[m], lo)), float(np.percentile(draws[m], hi))) for m in METRICS}


def paired_comparison(folds, enzyme):
    """XGBoost minus logistic regression on the fold-wise test scores, one row per metric.
    Plain paired t-test, and the Nadeau-Bengio corrected t-test, which allows for the overlap of the training
    sets (variance factor 1/k + n_test/n_train)."""
    test = folds[folds["Part"] == "test"]
    train = folds[folds["Part"] == "train"]
    x = test[test["Model"] == "XGBoost"].sort_values("Fold")
    b = test[test["Model"] == "Logistic regression"].sort_values("Fold")
    ratio = float(np.mean(x["n"].to_numpy() /
                          train[train["Model"] == "XGBoost"].sort_values("Fold")["n"].to_numpy()))
    k = len(x)
    out = []
    for m in METRICS:
        d = x[m].to_numpy() - b[m].to_numpy()
        mean, sd = d.mean(), d.std(ddof=1)
        half = stats.t.ppf(0.975, k - 1) * sd / np.sqrt(k)
        t_plain = mean / (sd / np.sqrt(k)) if sd > 0 else np.inf
        t_corr = mean / np.sqrt((1 / k + ratio) * sd ** 2) if sd > 0 else np.inf
        out.append({"Enzyme": enzyme, "Metric": m, "Folds": k,
                    "Mean difference (XGBoost - LogReg)": mean,
                    "95% t-interval low": mean - half, "95% t-interval high": mean + half,
                    "Folds where XGBoost is better": int((d > 0).sum()),
                    "Paired t-test p": float(2 * stats.t.sf(abs(t_plain), k - 1)),
                    "Corrected (Nadeau-Bengio) p": float(2 * stats.t.sf(abs(t_corr), k - 1))})
    return out
