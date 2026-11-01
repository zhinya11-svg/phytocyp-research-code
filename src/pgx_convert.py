"""Convert published star-allele frequencies to CPIC metaboliser phenotype frequencies.

Several of the source papers publish allele frequencies but not a full
poor/intermediate/normal/ultrarapid breakdown, so we derive one here. Every
assumption is written down rather than buried, because the methods section has to
state exactly how these numbers were produced.

METHOD
  1. Assume Hardy-Weinberg equilibrium and independence between loci. Diplotype
     frequency = product of the two allele frequencies (doubled for heterozygotes).
  2. Score each diplotype with the CPIC activity-score rules below.
  3. Bin the activity score into PM / IM / NM / UM using CPIC's published cut-offs.

KNOWN LIMITATIONS (state these in the paper)
  - Hardy-Weinberg is an assumption, not a measurement. Consanguinity is common in
    several of these populations, which inflates homozygosity and would therefore
    push the true PM fraction ABOVE our estimate.
  - Gene duplications are not reported in the regional allele tables we could read,
    so CYP2D6 ultrarapid metabolisers CANNOT be estimated from them. The derived
    CYP2D6 UM fraction is structurally zero and must not be read as a finding.
  - Any allele not listed is folded into *1 (normal function), which biases the
    estimate towards normal metabolism.
"""

# --- CPIC activity scores per allele -------------------------------------------
# CYP2D6 and CYP2C19 values follow Koopmans et al. 2021 Table 1, which reproduces
# PharmVar/CPIC functional assignments (PMID 33627619).
CYP2D6_AS = {
    "*1": 1.0, "*2": 1.0, "*35": 1.0, "*45": 1.0,
    "*9": 0.5, "*17": 0.5, "*29": 0.5, "*41": 0.5,
    "*10": 0.25,
    "*3": 0.0, "*4": 0.0, "*5": 0.0, "*6": 0.0,
}

# CYP2C19 is handled by allele class, not an activity score, because CPIC assigns
# rapid/ultrarapid status from the increased-function *17 allele specifically.
CYP2C19_FUNCTION = {
    "*1": "normal", "*17": "increased",
    "*2": "none", "*3": "none", "*4": "none", "*5": "none",
    "*6": "none", "*7": "none", "*8": "none",
    "*9": "decreased", "*10": "decreased", "*16": "decreased",
}

CYP2C9_AS = {
    "*1": 1.0, "*9": 1.0,
    "*2": 0.5, "*5": 0.5, "*8": 0.5, "*11": 0.5,
    "*3": 0.0, "*6": 0.0, "*13": 0.0, "*33": 0.0,
}

CYP3A5_FUNCTION = {
    "*1": "normal",
    "*3": "none", "*6": "none", "*7": "none",
}


def _diplotypes(allele_freqs):
    """Every diplotype and its Hardy-Weinberg frequency.

    allele_freqs maps allele name -> frequency. Frequencies should sum to 1;
    whatever is missing is assigned to *1 by the callers below.
    """
    alleles = sorted(allele_freqs)
    out = {}
    for i, a in enumerate(alleles):
        for b in alleles[i:]:
            p = allele_freqs[a] * allele_freqs[b]
            out[(a, b)] = p if a == b else 2 * p
    return out


def _bin(freqs):
    """Round to one decimal place as a percentage and make the bins sum to 100."""
    pct = {k: round(100 * v, 1) for k, v in freqs.items()}
    drift = round(100 - sum(pct.values()), 1)
    if drift:                      # push any rounding residue into the largest bin
        biggest = max(pct, key=pct.get)
        pct[biggest] = round(pct[biggest] + drift, 1)
    return pct


def cyp2d6_phenotypes(allele_freqs):
    """CPIC CYP2D6 bins: PM 0, IM 0.25-1.0, NM 1.25-2.25, UM >2.25."""
    freqs = dict(allele_freqs)
    freqs["*1"] = max(0.0, 1 - sum(freqs.values()))
    out = {"PM": 0.0, "IM": 0.0, "NM": 0.0, "UM": 0.0}
    for (a, b), p in _diplotypes(freqs).items():
        score = CYP2D6_AS[a] + CYP2D6_AS[b]
        if score == 0:
            out["PM"] += p
        elif score <= 1.0:
            out["IM"] += p
        elif score <= 2.25:
            out["NM"] += p
        else:
            out["UM"] += p
    return _bin(out)


def cyp2c19_phenotypes(allele_freqs):
    """CPIC CYP2C19: PM two no-function; IM one no-function; RM *1/*17; UM *17/*17."""
    freqs = dict(allele_freqs)
    freqs["*1"] = max(0.0, 1 - sum(freqs.values()))
    out = {"PM": 0.0, "IM": 0.0, "NM": 0.0, "RM": 0.0, "UM": 0.0}
    for (a, b), p in _diplotypes(freqs).items():
        fa, fb = CYP2C19_FUNCTION[a], CYP2C19_FUNCTION[b]
        pair = {fa, fb}
        if fa == fb == "none":
            out["PM"] += p
        elif "none" in pair and "increased" in pair:
            out["IM"] += p          # CPIC calls *2/*17 an intermediate metaboliser
        elif "none" in pair:
            out["IM"] += p
        elif fa == fb == "increased":
            out["UM"] += p
        elif "increased" in pair:
            out["RM"] += p
        else:
            out["NM"] += p
    return _bin(out)


def cyp2c9_phenotypes(allele_freqs):
    """CPIC CYP2C9: AS 2 NM, 1.5 IM, 1.0 IM, 0.5 PM, 0 PM."""
    freqs = dict(allele_freqs)
    freqs["*1"] = max(0.0, 1 - sum(freqs.values()))
    out = {"PM": 0.0, "IM": 0.0, "NM": 0.0}
    for (a, b), p in _diplotypes(freqs).items():
        score = CYP2C9_AS[a] + CYP2C9_AS[b]
        if score <= 0.5:
            out["PM"] += p
        elif score <= 1.5:
            out["IM"] += p
        else:
            out["NM"] += p
    return _bin(out)


def cyp3a5_phenotypes(allele_freqs):
    """CPIC CYP3A5: two no-function alleles = poor metaboliser (non-expresser)."""
    freqs = dict(allele_freqs)
    freqs["*1"] = max(0.0, 1 - sum(freqs.values()))
    out = {"PM": 0.0, "IM": 0.0, "NM": 0.0}
    for (a, b), p in _diplotypes(freqs).items():
        none = sum(CYP3A5_FUNCTION[x] == "none" for x in (a, b))
        out[["NM", "IM", "PM"][none]] += p
    return _bin(out)


# --- Published allele frequencies, transcribed from the source papers ----------
# Each dict is quoted directly from the cited table. Nothing here is from memory.

SOURCES = {
    # Goljan E, et al. PLoS One 2022;17(1):e0263137. PMID 35089958. Table 1.
    # 11,889 unrelated Saudi nationals, NGS.
    "Saudi (Goljan 2022)": {
        "CYP2C9": {"*2": 0.134, "*3": 0.053, "*5": 0.002, "*6": 0.001,
                   "*8": 0.005, "*9": 0.007, "*11": 0.006, "*33": 0.003},
        "CYP2C19": {"*2": 0.096, "*3": 0.001, "*8": 0.001, "*9": 0.002,
                    "*17": 0.259},
        "CYP3A5": {"*3": 0.845, "*6": 0.024, "*7": 0.004},
    },
    # Koopmans AB, et al. Transl Psychiatry 2021;11(1):141. PMID 33627619. Table 2.
    "Middle East (Koopmans 2021)": {
        "CYP2D6": {"*2": 0.29, "*4": 0.09, "*5": 0.02, "*10": 0.14,
                   "*17": 0.03, "*29": 0.02, "*41": 0.25},
        "CYP2C19": {"*2": 0.15, "*3": 0.02, "*17": 0.25},
    },
    "Europe (Koopmans 2021)": {
        "CYP2D6": {"*2": 0.36, "*4": 0.18, "*5": 0.03, "*10": 0.02,
                   "*17": 0.00, "*29": 0.00, "*35": 0.06, "*41": 0.08},
        "CYP2C19": {"*2": 0.15, "*3": 0.00, "*17": 0.23},
    },
    "East Asia (Koopmans 2021)": {
        "CYP2D6": {"*2": 0.13, "*4": 0.00, "*5": 0.05, "*10": 0.49,
                   "*17": 0.00, "*29": 0.00, "*35": 0.00, "*41": 0.02},
        "CYP2C19": {"*2": 0.30, "*3": 0.07, "*17": 0.02},
    },
    # Aynacioglu AS, et al. Clin Pharmacol Ther 1999;66(2):185-92. PMID 10460072.
    # 404 unrelated Turkish individuals.
    "Turkish (Aynacioglu 1999)": {
        "CYP2D6": {"*2": 0.35, "*4": 0.11, "*5": 0.01, "*10": 0.06, "*17": 0.01},
        "CYP2C19": {"*2": 0.12, "*3": 0.004},
    },
}

CONVERTERS = {
    "CYP2C9": cyp2c9_phenotypes,
    "CYP2C19": cyp2c19_phenotypes,
    "CYP2D6": cyp2d6_phenotypes,
    "CYP3A5": cyp3a5_phenotypes,
}


def derive_all():
    """Every population x enzyme we can convert, as a list of plain dicts."""
    rows = []
    for population, enzymes in SOURCES.items():
        for enzyme, alleles in enzymes.items():
            rows.append({
                "population": population,
                "enzyme": enzyme,
                "phenotypes": CONVERTERS[enzyme](alleles),
            })
    return rows

