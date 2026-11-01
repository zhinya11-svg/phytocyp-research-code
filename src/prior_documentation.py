"""Prior documentation: is a herb-drug pair already named in the Memorial Sloan Kettering herb guide?

One matcher, used for the 29 priority pairs (review sheet) and for all 423 pairs (pair table), so the two
cannot drift apart. It reads one row of data/c3_mskcc_lookup.csv (the herb's page in the guide).

A pair is MENTIONED if the herb's page names the pair's enzyme (in the Herb-Drug Interactions
section, or in an Adverse Reactions case report) or names the pair's drug by name. A drug CLASS does
not count. Otherwise it is NOT MENTIONED. A herb with no page at all gets the basis "no monograph".
"""

import re

MENTIONED = "Mentioned"
NOT_MENTIONED = "Not mentioned"

BASES = ("enzyme named - Herb-Drug Interactions", "enzyme named - case report only", "drug named",
         "drug class named (loose rule only)", "enzyme not named", "no monograph")

# Rule 3 only: which pair drugs a drug CLASS heading would cover. This is a pharmacological
# classification (warfarin is an anticoagulant) - the only class that touches the six study drugs.
CLASS_MEMBERS = {"anticoagul": {"warfarin"}}


def parts(cell):
    return [p.strip() for p in str(cell).split(";") if p.strip()]


def code_of(enzyme):                      # "CYP1A2" / "CYP 2C9" -> "1A2" / "2C9"
    return re.sub(r"(?i)^cyp\s*", "", enzyme.strip()).upper()


def norm_drug(drug):
    """'S-warfarin' -> 'warfarin' (a page names warfarin, not one enantiomer). A leading R-/S- is dropped."""
    return re.sub(r"(?i)^[rs]-", "", drug.strip()).lower()


def token_in(text, code):
    """True if enzyme `code` (e.g. '2C9') appears in `text` as that enzyme - as 'CYP2C9', 'CYP 2C9',
    'cytochrome 2C9' or a bare '2C9' in a list ('CYP450 1A2, 2D6, and 3A4') - and NOT as part of
    another enzyme such as 'CYP2C19' or 'CYP11A2'."""
    return re.search(rf"(?:(?<![A-Za-z0-9])|(?<=[Cc][Yy][Pp])){re.escape(code)}(?![A-Za-z0-9])", text) is not None


def self_test_token_in():
    """The matcher must accept every real form and reject look-alikes (the negative tests)."""
    assert token_in("inhibits CYP1A2, CYP2C9, and CYP3A4", "1A2") and token_in("inhibits CYP1A2, CYP2C9", "2C9")
    assert token_in("potential CYP 2C9 and 3A4 inhibition", "2C9") and token_in("Curcumin inhibits cytochrome 1A2", "1A2")
    assert token_in("the CYP450 1A2, 2D6, and 3A4 enzymes", "3A4") and token_in("the CYP450 1A2, 2D6, and 3A4 enzymes", "1A2")
    assert not token_in("inhibits CYP2C19", "2C9") and not token_in("CYP11A2", "1A2") and not token_in("CYP1A22", "1A2")
    assert not token_in("inhibits CYP3A4 only", "1A2")
    assert not token_in("inhibits CYP2C9", "2C19")                       # and the other way round
    assert norm_drug("S-warfarin") == "warfarin" and norm_drug("R-venlafaxine") == "venlafaxine"


def basis(rec, drug, enzyme, rule=1, drug_column="Drugs_named_among_study_drugs"):
    """Why a pair is (or is not) mentioned. `rec` is one row of the lookup. rule 1 = default, 2 = strict
    (ignores enzymes named only in a case report), 3 = loose (a drug class names its members).
    `drug_column`: the 29 priority pairs use the study-drugs column; all other pairs need
    "Drugs_named_all" (identical for the six study drugs; the review-sheet section asserts that)."""
    if rec["In_MSKCC"] == "No":
        return "no monograph"
    code = code_of(enzyme)
    named = {code_of(e) for e in parts(rec["Enzymes_named"])}
    case_only = {code_of(e) for e in parts(rec["Enzymes_case_report_only"])}
    if code in named - case_only:
        return "enzyme named - Herb-Drug Interactions"
    if code in case_only and rule != 2:
        return "enzyme named - case report only"
    if norm_drug(drug) in {norm_drug(d) for d in parts(rec[drug_column])}:
        return "drug named"
    if rule == 3:
        for cls in parts(rec["Classes_named"]):
            if any(key in cls.lower() and norm_drug(drug) in members for key, members in CLASS_MEMBERS.items()):
                return "drug class named (loose rule only)"
    return "enzyme not named"


def is_mentioned(a_basis):
    return a_basis not in ("enzyme not named", "no monograph")


# The three labels a reader sees (the tier rule itself still uses the two-way Mentioned / Not mentioned above).
LABEL_NAMES = "The guide names this enzyme or drug for this herb"
LABEL_NO_MATCH = "The guide's page for this herb does not name this enzyme or this drug"
LABEL_NO_PAGE = "The guide has no page for this herb"
DISPLAY_LABELS = (LABEL_NAMES, LABEL_NO_MATCH, LABEL_NO_PAGE)


def display_label(a_basis):
    """The displayed Prior documentation label for a basis returned by basis()."""
    if a_basis == "no monograph":
        return LABEL_NO_PAGE
    return LABEL_NAMES if is_mentioned(a_basis) else LABEL_NO_MATCH
