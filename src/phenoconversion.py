"""Population phenoconversion: how inhibition changes CYP activity-score distributions.

Weights a predicted herb-enzyme inhibition by how much metabolic capacity a population
started with, using CPIC activity scores at diplotype level.

    R(herb, enzyme, population) = fraction of people who HAD capacity and are driven
                                  below the clinical impairment threshold

WHAT IS CPIC'S AND WHAT IS OURS
  CPIC's:  the per-allele activity scores; the inhibitor multipliers (strong x0,
           moderate x0.5, Crews 2021 PMID 33387367); the CYP2C9 poor-metaboliser
           boundary of AS <= 0.5 (Theken 2020).
  Ours:    the CYP2D6 impairment threshold of AS <= 0.5. CPIC's CYP2D6 PM is AS = 0
           exactly, which only a strong inhibitor can produce, so a strict reading
           makes the model degenerate. This threshold is an ASSUMPTION and the
           threshold sweep below is its justification, not a citation.
  Ours:    the mapping from our classifier's probability band to a CPIC multiplier.
           No herb is ever assigned the "strong" multiplier - our data cannot support
           that claim, and strong saturates every population anyway.

METHODOLOGICAL FINDING
  Under CPIC's multiplicative framework the relative effect of an inhibitor is
  population-invariant: every activity score is scaled by the same factor, so the
  proportional loss is identical in every population. Population pharmacogenomics
  therefore modulates ABSOLUTE post-inhibition capacity rather than RELATIVE risk.
  Apparent population differences in conversion rate are artefacts of threshold
  placement on a discrete activity-score grid.

  Consequence for this module: report distributions (activity_distribution) and
  cumulative curves (cumulative_below), NOT crossing counts. converted_fraction is
  kept only to demonstrate the instability.

SCOPE
  CYP2D6 and CYP2C9 only. CYP2C19 is excluded because CPIC publishes no activity score
  for it (verified: "activity score" appears zero times in the CPIC CYP2C19 guideline);
  it is reported descriptively elsewhere. CYP1A2 is not star-allele polymorphic and
  CYP3A5 is a different gene from the CYP3A4 our models predict.
"""

from collections import defaultdict

import pgx_convert as pgx

# Enzymes with a published CPIC activity score, and the threshold we score against.
# "cpic_threshold" records whether that threshold is CPIC's own or our assumption.
ENZYMES = {
    "CYP2D6": {"scores": pgx.CYP2D6_AS, "threshold": 0.5, "cpic_threshold": False},
    "CYP2C9": {"scores": pgx.CYP2C9_AS, "threshold": 0.5, "cpic_threshold": True},
}

# Our classifier band -> CPIC multiplier. The 0.70 cut matches the flagging threshold
# used for the pair tiers. Everything here is an assumption for sensitivity analysis.
BANDS = [
    (0.70, "likely inhibitor", 0.5),    # treated as a MODERATE inhibitor
    (0.40, "uncertain", 0.75),          # partial effect
    (0.00, "unlikely", 1.0),            # no effect
]

def activity_distribution(population, enzyme):
    """Hardy-Weinberg activity-score distribution: {activity score: frequency}.

    This is the whole point of working at diplotype level - we never collapse to the
    four phenotype categories, because that is what made the model degenerate.
    """
    scores = ENZYMES[enzyme]["scores"]
    frequencies = dict(pgx.SOURCES[population][enzyme])
    frequencies["*1"] = max(0.0, 1 - sum(frequencies.values()))

    distribution = defaultdict(float)
    for (a, b), probability in pgx._diplotypes(frequencies).items():
        distribution[round(scores[a] + scores[b], 3)] += probability
    return dict(sorted(distribution.items()))


def converted_fraction(distribution, multiplier, threshold, strict=True):
    """Fraction who had capacity (AS > 0) and are driven below the threshold.

    People already at AS 0 are excluded: they have nothing left to lose, and counting
    them would credit an inhibitor with harm that the genotype had already done.

    DO NOT USE THIS FUNCTION TO PRODUCE A HEADLINE NUMBER. See the module docstring:
    conversion counts are threshold artefacts. It is retained for the threshold sweep,
    which exists to DEMONSTRATE that instability, not to measure a population.

    With multiplier m and threshold t, only people with t < AS <= t/m can cross. For
    m=0.5, t=0.5 that window is two of eight grid points, and `strict` decides whether
    the large AS 1.0 group falls inside it. Between them, the two conventions move the
    Middle East / Europe ratio across more than an order of magnitude AND flip its
    direction. No ratio computed here is reportable.
    """
    def crossed(score):
        # Must have been ABOVE the threshold to begin with: R measures the change the
        # inhibitor causes, not how many people are impaired anyway. Without this,
        # a herb predicted NOT to inhibit still scores above zero, because the
        # genotypically impaired are already below the line.
        if score <= threshold:
            return False
        after = score * multiplier
        return after < threshold if strict else after <= threshold

    return sum(
        frequency for score, frequency in distribution.items()
        if score > 0 and crossed(score)
    )


def populations_for(enzyme):
    """Which populations we have published allele data for, for this enzyme."""
    return [name for name, enzymes in pgx.SOURCES.items() if enzyme in enzymes]


# --- Threshold-free reporting. These are the functions the paper should use. -------

def reserve(population, enzyme, top_score=2.0):
    """Fraction of the population at full activity score - the baseline reserve.

    Threshold-free and model-free: a direct reading of the published allele data.
    This is the most robust claim available, so it carries the headline.
    """
    return activity_distribution(population, enzyme).get(top_score, 0.0)


def shift_distribution(population, enzyme, multiplier):
    """The activity-score distribution after multiplying every score by `multiplier`.

    Threshold-free. Shows where a population ENDS UP, not how many crossed a line.
    """
    shifted = defaultdict(float)
    for score, frequency in activity_distribution(population, enzyme).items():
        shifted[round(score * multiplier, 4)] += frequency
    return dict(sorted(shifted.items()))


def cumulative_below(distribution, thresholds):
    """P(AS <= t) for each t - the cumulative curve.

    Reporting the whole curve, rather than its value at one chosen t, is what makes
    the comparison honest: the reader sees where the populations differ and where
    the curves cross.
    """
    return {t: sum(f for s, f in distribution.items() if s <= t) for t in thresholds}


def mean_activity(distribution):
    """Mean activity score. Scales exactly with the multiplier, which is the point:
    it demonstrates that the RELATIVE effect is population-invariant."""
    return sum(score * frequency for score, frequency in distribution.items())
