"""Reusable pipeline for CYP inhibition modelling.

Standardisation -> featurisation -> training -> scaffold-aware validation.
"""

from collections import defaultdict

import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import Descriptors, rdFingerprintGenerator
from rdkit.Chem.MolStandardize import rdMolStandardize
from rdkit.Chem.Scaffolds import MurckoScaffold
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import GroupKFold
from xgboost import XGBClassifier

RDLogger.DisableLog("rdApp.*")

# The five enzymes, with their TDC dataset names.
ENZYMES = {
    "CYP1A2": "CYP1A2_Veith",
    "CYP2C9": "CYP2C9_Veith",
    "CYP2C19": "CYP2C19_Veith",
    "CYP2D6": "CYP2D6_Veith",
    "CYP3A4": "CYP3A4_Veith",
}

DESCRIPTOR_NAMES = [
    "MolWt", "MolLogP", "TPSA", "NumHDonors", "NumHAcceptors",
    "NumRotatableBonds", "NumAromaticRings", "RingCount",
    "FractionCSP3", "HeavyAtomCount",
]

XGB_SETTINGS = dict(
    n_estimators=400, max_depth=6, learning_rate=0.1,
    subsample=0.8, colsample_bytree=0.8, eval_metric="logloss", n_jobs=-1,
)

_largest_fragment = rdMolStandardize.LargestFragmentChooser()
_uncharger = rdMolStandardize.Uncharger()
_morgan_gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
_descriptor_fns = {n: f for n, f in Descriptors.descList if n in DESCRIPTOR_NAMES}
_descriptor_fns = {n: _descriptor_fns[n] for n in DESCRIPTOR_NAMES}


def standardise(smiles):
    """Strip salts, neutralise charges, return an RDKit molecule (or None)."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return _uncharger.uncharge(_largest_fragment.choose(mol))


def clean_dataset(df, smiles_column="Drug", label_column="Y"):
    """Standardise structures, drop label conflicts and duplicates.

    Returns the cleaned frame plus a dict of what happened, for the methods section.
    """
    out = df.copy()
    out["SMILES_std"] = [
        Chem.MolToSmiles(m) if (m := standardise(s)) is not None else None
        for s in out[smiles_column]
    ]

    report = {"starting_rows": len(out), "unparseable": int(out["SMILES_std"].isna().sum())}
    out = out.dropna(subset=["SMILES_std"])

    labels_per_structure = out.groupby("SMILES_std")[label_column].nunique()
    conflicting = labels_per_structure[labels_per_structure > 1].index
    report["label_conflicts"] = len(conflicting)
    out = out[~out["SMILES_std"].isin(conflicting)]

    report["duplicates"] = int(len(out) - out["SMILES_std"].nunique())
    out = out.drop_duplicates(subset="SMILES_std").reset_index(drop=True)

    report["final_rows"] = len(out)
    report["inhibitor_fraction"] = float(out[label_column].mean())
    return out, report


def featurise(smiles_list):
    """2048 Morgan bits (radius 2) + 10 descriptors, as one float32 table."""
    molecules = [standardise(s) for s in smiles_list]
    fingerprints = np.array(
        [_morgan_gen.GetFingerprintAsNumPy(m) for m in molecules], dtype=np.float32
    )
    descriptors = np.array(
        [[f(m) for f in _descriptor_fns.values()] for m in molecules], dtype=np.float32
    )
    return np.hstack([fingerprints, descriptors])


def scaffolds_of(smiles_list):
    """Murcko scaffold SMILES for each molecule; '' means no rings."""
    return [
        MurckoScaffold.MurckoScaffoldSmiles(smiles=s, includeChirality=False)
        for s in smiles_list
    ]


def scaffold_split(scaffolds, train_fraction=0.8):
    """Common scaffolds to training, rare leftovers to testing. The hard split."""
    groups = defaultdict(list)
    for index, scaffold in enumerate(scaffolds):
        groups[scaffold].append(index)

    target = int(train_fraction * len(scaffolds))
    train, test = [], []
    for group in sorted(groups.values(), key=len, reverse=True):
        (train if len(train) + len(group) <= target else test).extend(group)
    return np.array(train), np.array(test)


def score(y_true, probability, threshold=0.5):
    """The five metrics the paper reports."""
    prediction = (probability >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, prediction).ravel()
    return {
        "AUROC": roc_auc_score(y_true, probability),
        "AUPRC": average_precision_score(y_true, probability),
        "Sensitivity": tp / (tp + fn),
        "Specificity": tn / (tn + fp),
        "Balanced accuracy": balanced_accuracy_score(y_true, prediction),
    }


def train_model(X, y, seed=42):
    model = XGBClassifier(random_state=seed, **XGB_SETTINGS)
    model.fit(X, y)
    return model


def cross_validate(X, y, scaffolds, n_splits=5, seed=42):
    """Scaffold-grouped k-fold: no scaffold ever spans a fold."""
    groups = pd.factorize(pd.Series(scaffolds))[0]
    folds = []
    for train_i, test_i in GroupKFold(n_splits=n_splits).split(X, y, groups=groups):
        model = train_model(X[train_i], y[train_i], seed=seed)
        folds.append(score(y[test_i], model.predict_proba(X[test_i])[:, 1]))
    return pd.DataFrame(folds)
