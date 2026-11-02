"""Pure functions that turn a herb-drug lookup into card content for PhytoCYP Tracker.

No Streamlit calls live here, so everything can be unit-tested (app/test_render.py). Every string that comes from the data is passed through
html.escape before it goes into HTML. Colours come from theme.py only; this file contains no hex value.
"""

import html
import json
import re
from pathlib import Path

import altair as alt
import pandas as pd

import theme

ENZYMES = ["CYP1A2", "CYP2C9", "CYP2C19", "CYP2D6", "CYP3A4"]
APP_NAME = "PhytoCYP Tracker"
NOTICE = ("PhytoCYP Tracker is a research prototype and a research screening aid built from a machine-learning model and published data. "
          "It is not clinical advice and does not replace pharmacist or physician judgement. Its results have not been validated in patients.")
SUBTITLE = "Herb and cytochrome P450 screening"
BANNED = re.compile(r"\b(?:safe|safely|avoid|dose|dosing|dangerous|harmless|recommend|should)\b", re.I)
RAN = re.compile(r"^The model assessed \d+ compounds? of this herb")
NOT_RAN = re.compile(r"^No compound of this herb could be assessed")

NOTE_SUBSTRATE_SENSITIVE = "The drug’s blood level rises 5-fold or more when this enzyme is blocked."
NOTE_SUBSTRATE_MODERATE = "The drug’s blood level rises 2- to 5-fold when this enzyme is blocked."
NOTE_NTI = "Narrow means a small change in blood level can cause treatment failure or serious harm."
NOTE_NO_PAGE = "This reflects coverage of the guide, not a negative finding."
PRIOR_SOURCE = "Memorial Sloan Kettering herb guide."
NOTE_UNTESTED = "No published lab test found for this herb compound and enzyme."
NOTE_PREDICTED_WEAKER = "The model predicted inhibition, but the lab value was weaker than 10 µM."
NOTE_PREDICTED_STRONGER = "The model predicted inhibition, and the lab value was 10 µM or stronger."
LEAD_NAMES = "Source quote (the guide’s own words):"
LEAD_CLOSEST = "Closest text recorded from the guide’s page for this herb. It is shown for context and does not match this pair:"
NOTE_HIGHEST = "The probability is the highest value among the herb’s compounds; combined effects of several compounds are putative and not modelled."
NOTE_NO_INTERACTION = "This does not mean the combination has no interaction."
LEGEND = "Darker blue means a higher model probability."
MARK = "†"      # a plain marker beside a driver compound that was also in the training data for that enzyme
MARK_HTML = f' <span data-field="insample" role="img" aria-label="also in the training data" title="Also in the training data for this enzyme">{MARK}</span>'
NOTE_IN_TRAINING = "Also in the training data for this enzyme, so this probability is not an independent test."
OVERVIEW_NOTE = "Bars below the line mean the model did not flag the herb for that enzyme. This does not mean no interaction."
OVERVIEW_DARKER = "Darker bars reached the 0.5 threshold."
OVERVIEW_BRIGHTER = "Brighter bars reached the 0.5 threshold."      # dark theme: the flagged bars are the lighter ones, so "darker" would be untrue there

esc = html.escape


# ---------------------------------------------------------------- data
def load_data(data_dir):
    """Read the app's data files (written by notebook 18) into plain structures."""
    d = Path(data_dir)
    pairs = pd.read_csv(d / "dashboard_pairs.csv", keep_default_na=False)
    missing = pd.read_csv(d / "dashboard_missing_combinations.csv", keep_default_na=False)
    overview = pd.read_csv(d / "herb_enzyme_overview.csv", keep_default_na=False)
    sens = pd.read_csv(d / "enzyme_sensitivity.csv")
    facts = json.loads((d / "data_facts.json").read_text(encoding="utf-8"))
    combos = pd.concat([pairs[["Herb", "Drug", "Enzyme"]], missing[["Herb", "Drug", "Enzyme"]]])
    drugs = [dict(drug=name, enzymes=sorted(g["Enzyme"].unique())) for name, g in sorted(combos.groupby("Drug"), key=lambda kv: kv[0].lower())]
    return dict(
        pairs={(r["Herb"], r["Drug"], r["Enzyme"]): r for r in pairs.to_dict("records")},
        missing={(r["Herb"], r["Drug"], r["Enzyme"]): r for r in missing.to_dict("records")},
        overview={(r["Herb"], r["Enzyme"]): dict(highest=(None if r["Highest probability"] == "" else float(r["Highest probability"])),
                                                 assessable=int(r["Assessable compounds"]), flagged=int(r["Compounds at 0.5 or more"]), reached=r["Reached 0.5"])
                  for r in overview.to_dict("records")},
        sensitivity=dict(zip(sens["Enzyme"], sens["Test sensitivity"].astype(float))),
        herbs=sorted(combos["Herb"].unique()), drugs=drugs, facts=facts)


def pct(x):
    return f"{round(float(x) * 100)}%"


def drug_label(entry):
    return f"{entry['drug']} - {', '.join(entry['enzymes'])}"


def lookup(data, herb, drug):
    """One item per enzyme of the drug: a pair, or an absent combination (the model ran or could not assess)."""
    items = []
    for enzyme in next(d for d in data["drugs"] if d["drug"] == drug)["enzymes"]:
        key = (herb, drug, enzyme)
        if key in data["pairs"]:
            r = data["pairs"][key]
            items.append(dict(kind="pair", herb=herb, drug=drug, enzyme=enzyme, probability=float(r["Max probability"]), driver=r["Driver"],
                              assessable=int(r["Assessable"]), substrate=r["Substrate sensitivity"], nti=r["Narrow therapeutic index"],
                              prior=r["Prior documentation"], prior_basis=r["Prior documentation basis"], matched=r["Matched term"], quote=r["Source quote"],
                              ref=r["Reference check"], ref_sentence=r["Reference check sentence"], in_training=(r["Driver in training data"] == "Yes"),
                              measured=(None if r["Measured uM"] == "" else float(r["Measured uM"])), assay=r["Measured assay"], sensitivity=data["sensitivity"][enzyme]))
        else:
            r = data["missing"][key]
            ran = bool(RAN.match(r["Reason"])) and not NOT_RAN.match(r["Reason"])
            items.append(dict(kind="absent" if ran else "unassessable", herb=herb, drug=drug, enzyme=enzyme, reason=r["Reason"], sensitivity=data["sensitivity"][enzyme]))
    return items


# ---------------------------------------------------------------- html pieces
def common_name(herb):
    return herb.split(" (")[0]


def latin_name(herb):
    m = re.search(r"\((.*)\)", herb)
    return m.group(1) if m else herb


def logo_html(suffix, height=40):
    """The supplied logo, unchanged except for size, an accessible name and a clip-path id that is unique per copy on the page."""
    svg = (Path(__file__).parent / "assets" / "logo.svg").read_text(encoding="utf-8").strip()
    svg = svg.replace('<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">',
                      f'<svg viewBox="0 0 64 64" width="{height}" height="{height}" role="img" aria-label="PhytoCYP logo" style="flex:none">', 1)
    return svg.replace('id="capsuleClip"', f'id="capsuleClip{suffix}"').replace("url(#capsuleClip)", f"url(#capsuleClip{suffix})")


def brand_html(suffix):
    return (f'<div class="pc-brand{" pc-brand-gate" if suffix == "Gate" else ""}">{logo_html(suffix)}<div><span class="pc-name">{esc(APP_NAME)}</span>'
            f'<span class="pc-sub">{esc(SUBTITLE)}</span></div></div>')


def gate_html():
    return ('<div class="pc-gate"><hr><h2>Research screening notice</h2>'
            f"<p>{esc(NOTICE)}</p></div>")


def probability_html(p):
    return (f'<div class="pc-prob"><span class="pc-plabel">Model probability</span><span class="pc-num" data-field="probability">{p:.3f}</span>'
            f'<div class="pc-probbar"><span style="width:{round(p * 100)}%;background:var(--p{theme.prob_step(p)})"></span></div></div>')


def head_html(item):
    """Title, one muted metadata line and (for a pair) the probability on the right."""
    meta = [esc(latin_name(item["herb"])), f'enzyme <span data-field="enzyme">{esc(item["enzyme"])}</span>']
    right = ""
    if item["kind"] == "pair":
        meta += [f'driver compound <span data-field="driver">{esc(item["driver"])}</span>{MARK_HTML if item.get("in_training") else ""}',
                 f'<span data-field="judged">{item["assessable"]}</span> {"herb chemical" if item["assessable"] == 1 else "herb chemicals"} the model could judge']
        right = probability_html(item["probability"])
    note = f'<div class="pc-meta" data-field="insample-note">{esc(MARK)} {esc(NOTE_IN_TRAINING)}</div>' if item["kind"] == "pair" and item.get("in_training") else ""
    return (f'<div class="pc-head"><div><div class="pc-title" role="heading" aria-level="2">{esc(common_name(item["herb"]))} + {esc(item["drug"])}</div>'
            f'<div class="pc-meta">{" · ".join(meta)}</div>{note}</div>{right}</div>')


def summary_sentence_html(item):
    flags = f"The model flags this herb for {esc(item['enzyme'])}."
    if item["ref"] == "Supported":
        tail = f'A published lab test <span class="pc-ref pc-ref-Supported">agrees</span> (measured {item["measured"]:g} µM).'
    elif item["ref"] == "Contradicted":
        tail = f'A published lab test <span class="pc-ref pc-ref-Contradicted">disagrees</span> (measured {item["measured"]:g} µM).'
    else:
        tail = "No published lab test found."
    return f'<p class="pc-sentence" data-field="summary">{flags} {tail}</p>'


def row_html(name, value, explanation, field):
    return (f'<div class="pc-row" data-row="{field}"><div class="pc-fn">{esc(name)}</div>'
            f'<div><div class="pc-fv" data-field="{field}">{value}</div><div class="pc-fx">{explanation}</div></div></div>')


def substrate_explanation(item):
    return NOTE_SUBSTRATE_SENSITIVE if item["substrate"].startswith("Sensitive") else NOTE_SUBSTRATE_MODERATE


def prior_value(item):
    herb = common_name(item["herb"]).lower()
    if item["prior_basis"] == "no_page":
        return f"The guide has no page for {herb}"
    if item["prior_basis"] == "none":
        return f"Not named in the guide’s {herb} page"
    return f"Named in the guide’s {herb} page"


def source_text(item):
    """(lead sentence, matched term or '', quote or '') for the source text, or None when there is nothing to show (no page for the herb)."""
    if not item["matched"] and not item["quote"]:
        return None
    return (LEAD_NAMES if item["matched"] else LEAD_CLOSEST, item["matched"], item["quote"])


def source_html(item):
    s = source_text(item)
    if s is None:
        return ""
    lead, matched, quote = s
    out = ""
    if matched:
        out += f'<p class="pc-sp"><b>Matched term: </b><span data-field="matched">{esc(matched)}</span></p>'
    out += f'<p class="pc-sp">{esc(lead)}</p>'
    if quote:
        out += f'<p class="pc-sp" data-field="quote">{esc(quote)}</p>'
    return out


def prior_explanation(item):
    out = esc(PRIOR_SOURCE)
    if item["prior_basis"] == "no_page":
        out += f" {esc(NOTE_NO_PAGE)}"
    src = source_html(item)
    if src:
        out += f'<details><summary>Show source text</summary><div class="pc-source">{src}</div></details>'
    return out


def reference_explanation(item):
    if item["ref"] == "Untested":
        return esc(NOTE_UNTESTED)
    start = f"Measured {item['measured']:g} µM ({esc(item['assay'])}). "
    return esc(start) + esc(NOTE_PREDICTED_WEAKER if item["ref"] == "Contradicted" else NOTE_PREDICTED_STRONGER)


def about_model_html(item):
    return (f'<details class="pc-aboutmodel" data-field="model-note"><summary>About this model</summary><div class="pc-source">'
            f'<p class="pc-sp">Detects about {pct(item["sensitivity"])} of true {esc(item["enzyme"])} inhibitors on test compounds (cross-validation, 0.5 threshold).</p>'
            f'<p class="pc-sp">{esc(NOTE_HIGHEST)}</p></div></details>')


def absent_html(item):
    ran = item["kind"] == "absent"
    heading = "The model did not flag this combination." if ran else "The model could not assess this combination."
    sens = (f'<p data-field="sensitivity">On test compounds this model detected about {pct(item["sensitivity"])} of true inhibitors of this enzyme, so some inhibitors are missed.</p>' if ran else "")
    return (f'<div class="pc-absent"><p class="pc-value">{esc(heading)}</p><p data-field="reason">{esc(item["reason"])}</p>{sens}'
            f'<p>{esc(NOTE_NO_INTERACTION)}</p></div>')


def card_html(item):
    """One result, as one block of HTML (the app only places it)."""
    if item["kind"] != "pair":
        return f'<div class="pc-result">{head_html(item)}{absent_html(item)}</div>'
    rows = (row_html("Substrate sensitivity", esc(item["substrate"]), esc(substrate_explanation(item)), "substrate")
            + row_html("Narrow therapeutic index", esc(item["nti"]), esc(NOTE_NTI), "nti")
            + row_html("Prior documentation", esc(prior_value(item)), prior_explanation(item), "prior")
            + row_html("Reference check", f'<span class="pc-ref pc-ref-{esc(item["ref"])}" data-field="reference-label">{esc(item["ref"])}</span>', reference_explanation(item), "reference"))
    return f'<div class="pc-result">{head_html(item)}{summary_sentence_html(item)}<div class="pc-rows">{rows}</div>{about_model_html(item)}</div>'


def cards_html(items):
    return '<div class="pc-gap"></div>'.join(card_html(i) for i in items)


def visible_text(item):
    """All the text a reader sees for one item, including the text inside the closed links (used by the tests)."""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(card_html(item)))).strip()


# ---------------------------------------------------------------- herb overview, model and limits, about
def overview_rows(data, herb):
    return [dict(enzyme=e, **data["overview"][(herb, e)]) for e in ENZYMES]


def overview_table_html(data, herb):
    rows = ""
    for r in overview_rows(data, herb):
        high = "—" if r["highest"] is None else f"{r['highest']:.3f}"
        reached = "Not assessed" if r["assessable"] == 0 else ("Yes" if r["highest"] >= 0.5 else "No")
        rows += f"<tr role=\"row\" data-enzyme=\"{esc(r['enzyme'])}\"><td role=\"cell\">{esc(r['enzyme'])}</td><td role=\"cell\">{high}</td><td role=\"cell\">{r['assessable']}</td><td role=\"cell\">{esc(reached)}</td></tr>"
    return ('<div class="pc-tablewrap"><table class="pc-table pc-fit" role="table"><thead role="rowgroup"><tr role="row"><th role="columnheader">Enzyme</th><th role="columnheader">Highest probability</th><th role="columnheader">Chemicals the model could judge</th><th role="columnheader">Reached the 0.5 threshold</th></tr></thead>'
            f"<tbody role=\"rowgroup\">{rows}</tbody></table></div>")


def herb_assessable(data, herb):
    return any(r["assessable"] > 0 for r in overview_rows(data, herb))


CHART_TEXT_PX = 11            # chart text is never smaller than this
CHART_TILT = "width < 235"    # plot width (px) below which the enzyme names are tilted so they cannot touch (phones 360 px and wider keep them upright)


def overview_chart(data, herb, dark=False):
    """Altair bar chart of the highest probability per enzyme. Bars below 0.5 are pale blue, bars at or above 0.5 medium blue; a dashed 0.5 line with a thin halo is drawn
    on top of the bars and labelled at its right end (None when the model could judge none of the herb’s chemicals)."""
    rows = [r for r in overview_rows(data, herb) if r["assessable"] > 0]
    if not rows:
        return None
    p = theme.DARK if dark else theme.LIGHT
    df = pd.DataFrame({"Enzyme": [r["enzyme"] for r in rows], "Highest probability": [r["highest"] for r in rows],
                       "Colour": [p["bar_high"] if r["highest"] >= 0.5 else p["bar_low"] for r in rows]})
    base = alt.Chart(df).encode(x=alt.X("Enzyme:N", sort=ENZYMES, axis=alt.Axis(title=None, labelFontSize=CHART_TEXT_PX, labelAngle=alt.expr(f"{CHART_TILT} ? -45 : 0"), labelAlign=alt.expr(f"{CHART_TILT} ? 'right' : 'center'"))))
    bars = base.mark_bar(width={"band": 0.6}).encode(y=alt.Y("Highest probability:Q", scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(title=None, values=[0, 0.5, 1])),
                                                    color=alt.Color("Colour:N", scale=None), tooltip=["Enzyme", alt.Tooltip("Highest probability:Q", format=".3f")])
    labels = base.mark_text(dy=-8, color=p["chart_text"], fontSize=CHART_TEXT_PX).encode(y="Highest probability:Q", text=alt.Text("Highest probability:Q", format=".3f"))
    line_df = pd.DataFrame({"y": [0.5]})
    halo = alt.Chart(line_df).mark_rule(color=p["halo"], strokeWidth=5).encode(y="y:Q")
    line = alt.Chart(line_df).mark_rule(strokeDash=[6, 4], color=p["rule"], strokeWidth=2).encode(y="y:Q")
    tag = alt.Chart(pd.DataFrame({"y": [0.5], "t": ["0.5\nthreshold"]})).mark_text(align="left", dx=6, dy=0, color=p["chart_text"], fontSize=CHART_TEXT_PX, lineBreak="\n", x="width").encode(y="y:Q", text="t:N")
    chart = (bars + labels + halo + line + tag).properties(height=260, padding={"right": 5, "left": 5, "top": 10, "bottom": 5}).configure(background=p["bg"]).configure_view(stroke=None)
    return chart.configure_axis(labelColor=p["chart_text"], domainColor=p["chart_grid"], gridColor=p["chart_grid"], tickColor=p["chart_grid"], labelFontSize=CHART_TEXT_PX)


def model_limits_html(data):
    rows = "".join(f'<tr data-enzyme="{e}"><td>{e}</td><td>about {pct(data["sensitivity"][e])}</td></tr>' for e in ENZYMES)
    d6 = data["sensitivity"]["CYP2D6"]
    t = data["facts"]["in_training"]
    return (
        '<div class="pc-prose">'
        "<h3>How to read the probability</h3>"
        f"<p>The number is the model’s probability that a compound blocks the enzyme, from 0 to 1. {esc(LEGEND)}</p>"
        "<h3>How well the model detects true inhibitors</h3>"
        "<p>The table shows, for each enzyme, the share of true inhibitors the model detected on held-out test compounds (cross-validation, at the 0.5 threshold).</p>"
        f'<div class="pc-tablewrap"><table class="pc-table" id="sens-table"><thead><tr><th>Enzyme</th><th>Share of true inhibitors detected</th></tr></thead><tbody>{rows}</tbody></table></div>'
        f'<p data-field="d6">For CYP2D6 the model detected about {pct(d6)} of true inhibitors, so about {100 - round(d6 * 100)}% are missed.</p>'
        "<h3>What the results do and do not say</h3><ul>"
        "<li>Values are stored. Nothing is predicted live.</li>"
        "<li>“The model did not flag this combination” means no compound of that herb reached probability 0.5 for that enzyme. It does not mean the combination has no interaction.</li>"
        "<li>Prior documentation reflects one source, the Memorial Sloan Kettering herb guide. Four herbs (Parsley, Harmal, Clove, Anise) have no page there; for them the label says the guide has no page, which reflects the guide’s coverage and is not a negative finding.</li>"
        "<li>Garlic and peppermint rest on a single compound each that the model could assess (one of five and one of three).</li>"
        "<li>Myrrh could not be assessed: none of its four compounds is similar enough to the compounds the model learned from.</li>"
        "<li>Combined effects of several compounds are putative and not modelled. There is no information on how much of a compound reaches the liver.</li></ul>"
        f'<p data-field="in-training"><b>Limit:</b> {t["n_compounds"]} of the {t["n_distinct_compounds"]} compounds were also in the training data, so their predictions are not independent tests.</p></div>')


# ---------------------------------------------------------------- "The data in plain English" (every number comes from app/data/data_facts.json, written by notebook 18)
def _n(x):
    return f"{int(x):,}"


def _details(summary, body):
    return f'<details><summary>{esc(summary)}</summary><div class="pc-source">{body}</div></details>'


SOURCES_NOTE = ('<p><b>Data sources</b></p>'
                '<p data-field="sources">Training data: Veith et al., 2009 (PubChem AID 1851, via the Therapeutics Data Commons). Herb compounds: published sources. '
                'Drug labels: the FDA examples of drugs that interact with CYP enzymes, and Donnelly et al., 2025. Lab measurements: ChEMBL.</p>')


def sources_html(facts):
    t, h, d, r = facts["training"], facts["herbs"], facts["drugs"], facts["reference"]
    lo, hi = min(v["compounds"] for v in t.values()), max(v["compounds"] for v in t.values())
    per = h["per_herb"]
    fewest, most = min(v["compounds"] for v in per.values()), max(v["compounds"] for v in per.values())
    none = [common_name(k) for k, v in sorted(per.items()) if v["assessable"] == 0]
    single = [common_name(k) for k, v in sorted(per.items()) if v["assessable"] == 1]
    two_enzyme = d["n_drug_enzyme_rows"] - d["n_drugs"]
    nti = ", ".join(d["nti_drug_names"][:-1]) + " and " + d["nti_drug_names"][-1]
    train_rows = "".join(f"<tr><td>{e}</td><td>{_n(t[e]['compounds'])}</td><td>{t[e]['percent_inhibitors']:.1f}%</td></tr>" for e in ENZYMES)
    herb_rows = "".join(f"<tr><td>{esc(name)}</td><td>{v['compounds']}</td><td>{v['assessable']}</td></tr>" for name, v in sorted(per.items()))
    d1 = (f"<p class=\"pc-sp\">Each chemical was tested in a lab for whether it blocks one of five CYP enzymes. After cleaning, each enzyme has between {_n(lo)} and {_n(hi)} chemicals, and the model learned from them. "
          "<b>Limit:</b> these are laboratory results, not results in patients.</p>"
          f'<div class="pc-tablewrap"><table class="pc-table" id="training-table"><thead><tr><th>Enzyme</th><th>Chemicals used</th><th>Share that block the enzyme</th></tr></thead><tbody>{train_rows}</tbody></table></div>'
          )
    d2 = (f"<p class=\"pc-sp\">The {h['n_herbs']} herbs come from three places: published surveys of herb use in Saudi Arabia, the Saudi medicines regulator’s herb-drug assessment, and documented traditional use in the region. "
          f"Each has {fewest} to {most} listed compounds ({h['n_compounds']} listings, {h['n_distinct_compounds']} different compounds), taken from one published source. "
          f"The model could judge {h['n_assessable']} of them; the rest are too different from the training chemicals ({' and '.join(none)} has none, {' and '.join(single)} have one each). "
          "<b>Limit:</b> only the listed compounds are scored, not the whole plant, and the amounts in a real product are unknown.</p>"
          f'<div class="pc-tablewrap"><table class="pc-table" id="herb-table"><thead><tr><th>Herb</th><th>Compounds</th><th>Chemicals the model could judge</th></tr></thead><tbody>{herb_rows}</tbody></table></div>')
    d3 = (f"<p class=\"pc-sp\">The {d['n_drugs']} drugs each have the CYP enzyme that handles them ({d['n_drug_enzyme_rows']} entries; {two_enzyme} drugs appear with two enzymes). "
          f"The FDA table gives the sensitivity class ({d['n_sensitive']} sensitive, {d['n_moderate']} moderate), and {d['n_nti_drugs']} drugs are flagged as narrow therapeutic index ({esc(nti)}) following Donnelly et al., 2025. "
          f"<b>Limit:</b> the FDA has no official list of narrow therapeutic index drugs, so these {d['n_nti_drugs']} come from a published paper.</p>")
    d4 = (f"<p class=\"pc-sp\">ChEMBL holds {r['n_measurements']} measurements for the herb compounds on these enzymes; {r['n_same_source_as_training']} came from the test panel the model learned from, so they were left out, which leaves {r['n_independent']}. "
          f"IC50 is the concentration that cuts an enzyme’s activity in half: “agrees” means the model predicted blocking and the IC50 was 10 µM or stronger, “disagrees” means it was weaker ({r['n_supported']} of {r['n_pairs']} pairs agree, {r['n_contradicted']} disagree and {r['n_untested']} have no published test). "
          "<b>Limit:</b> labs use different set-ups, so equal numbers are not exactly equal readings.</p>"
          f"<p class=\"pc-sp\" data-field=\"lab-coverage\"><b>Limit:</b> the lab comparison covers {r['n_tested']} of the {r['n_pairs']} herb-drug pairs; the other {r['n_untested']} have no published test.</p>"
          )
    details = "".join(_details(name, body) for name, body in
                      [("Enzyme-blocking tests", d1), ("Herb compounds", d2), ("Drug list", d3), ("Published lab measurements", d4)])
    return SOURCES_NOTE + details


def about_html(facts):
    return (
        '<div class="pc-prose">'
        f"<p>{esc(APP_NAME)} is a research prototype for pharmacists and researchers. It screens compounds from 17 medicinal herbs used in the Middle East for their predicted ability to block the cytochrome P450 (CYP) enzymes that break down many drugs, "
        "and compares each prediction with published lab measurements where they exist.</p>"
        f"{sources_html(facts)}"
        "</div>")
