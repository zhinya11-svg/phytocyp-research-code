"""Herb-level scoring from constituent predictions.

A herb is a mixture. Our model scores individual constituents, so something has to
turn n constituent probabilities into one herb-level number.

WHAT THE LITERATURE SUPPORTS, AND WHAT IT DOES NOT

  The maximum rule has precedent. Brantley SJ, Graf TN, Oberlies NH, Paine MF.
  Drug Metab Dispos. 2013;41(9):1662-70 (PMID 23801821) reports "the maximum predicted
  increases in midazolam area under the curve" for milk thistle - a maximum across the
  constituents tested, which is the rule used here.

  No framework specifies a combining rule. The NaPDI Center's recommended approach
  (Cox EJ, et al. Pharmacol Rev. 2021;73(2):847-859, PMID 33712517) applies its
  criteria per constituent and specifies no method for combining several inhibitory
  constituents. Brantley SJ, et al. Drug Metab Dispos. 2014;42(3):301-17
  (PMID 24335390) states that "a standard system for interaction prediction and
  evaluation is nonexistent".

  Additive combination was tested on a botanical and under-predicted. Brantley 2013
  found whole silymarin inhibited CYP3A more than additivity over its flavonolignans
  predicted, suggesting synergy.

WHY WE DO NOT WEIGHT BY ABUNDANCE
  We have none. data/herb_constituents.csv records structures and citations, not
  concentrations. Plant content is also not exposure at the enzyme, so an
  abundance-weighted score would imply a pharmacokinetic claim we cannot support.

WHAT THIS MODULE REPORTS
  The maximum as the primary score, the count of flagged constituents as a second
  axis, and alternative rules for sensitivity analysis only. The alternatives exist to
  show whether the ranking depends on the choice - not to be used as the headline.
"""

import numpy as np

FLAG_THRESHOLD = 0.70        # the paper-level "flagged call" threshold (the 25 flagged
                             # constituent-enzyme calls) and the strong-signal pair tier.
                             # NOTE: pairs are admitted from 0.50, so a
                             # pair can be in the pair table with nothing at 0.70.


def herb_score(probabilities, threshold=FLAG_THRESHOLD):
    """Summarise one herb's constituent probabilities for one enzyme.

    `probabilities` is an iterable that may contain NaN for constituents outside the
    applicability domain; those are dropped, and `n_assessable` records how many
    remained. A herb with nothing assessable returns None rather than zero: we cannot
    distinguish "no risk" from "cannot say".
    """
    values = np.asarray([p for p in probabilities if p is not None and not np.isnan(p)],
                        dtype=float)
    if values.size == 0:
        return None

    return {
        # Primary score. Brantley 2013 precedent.
        "max": float(values.max()),
        # Second axis: how many constituents independently clear the threshold.
        # Distinguishes a herb with four flagged constituents from one with a single
        # flagged constituent and nothing else near it.
        "n_flagged": int((values >= threshold).sum()),
        "n_assessable": int(values.size),
        # Sensitivity only - never the headline.
        "mean": float(values.mean()),
        "top2": float(np.sort(values)[-2:].mean()),
        # Reported so a reader can see how isolated the maximum is.
        "second": float(np.sort(values)[-2]) if values.size > 1 else None,
    }


def margin(score):
    """How far the maximum sits above the next constituent.

    A large margin means the herb-level score rests on one compound, so any change of
    combining rule - or one bad prediction - moves it. This is the number that tells
    you how fragile a herb-level finding is.
    """
    if score is None or score["second"] is None:
        return None
    return round(score["max"] - score["second"], 3)


def single_constituent(score, threshold=FLAG_THRESHOLD):
    """True when exactly one constituent carries the herb above the threshold."""
    if score is None:
        return False
    return score["n_flagged"] == 1 and score["max"] >= threshold


# Rules compared in the sensitivity analysis. "noisy_or" is deliberately absent:
# 1 - prod(1 - p) saturates towards 1.0 for any herb with several moderate
# constituents, which in our data sends three herbs to exactly 1.000. It is not a
# usable alternative and is excluded rather than reported.
SENSITIVITY_RULES = ("max", "mean", "top2")
