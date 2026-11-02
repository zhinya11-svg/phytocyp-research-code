# PhytoCYP research code

Code and small data files for a screening study of cytochrome P450 (CYP) enzyme inhibition by compounds of 17 medicinal herbs used in the Middle East.
Gradient-boosted models (XGBoost) trained on the public Veith et al. screening data predict, for 71 herb-compound listings (69 different compounds),
the probability of inhibiting CYP1A2, CYP2C9, CYP2C19, CYP2D6 and CYP3A4. The predictions are combined into herb-drug pairs
and compared with published laboratory measurements (ChEMBL), the Saudi Food and Drug Authority signal report and the Memorial Sloan Kettering herb guide.

These are screening results. They have not been validated in patients and are not clinical advice.

Everything is produced by one notebook, `phytocyp_pipeline.ipynb`, which runs from top to bottom without manual steps.

## Contents

| Path | What it holds |
|---|---|
| `phytocyp_pipeline.ipynb` | The whole analysis: data, models, evaluation, herb-drug pairs and checks, figures and tables |
| `src/` | Functions used by the notebook (`cyp_pipeline.py` cleaning, features, training and validation; `mixture.py`; `calibration.py`; `prior_documentation.py`; `pgx_convert.py`; `phenoconversion.py`; `dome_analysis.py` baselines, confidence intervals and train-versus-held-out performance for the five enzymes) |
| `data/` | Small curated input tables (see "Data") |
| `scripts/` | Optional steps: ChEMBL re-download, DEEPCYPs run, publish-safety scan |
| `outputs/` | Written by the notebook; `outputs/MAPPING.md` says which output feeds which number |
| `requirements.txt` | Pinned package versions |

## Environment

Python 3.13.17 (tested). Create an environment and install the pinned versions:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m ipykernel install --user --name phytocyp --display-name "PhytoCYP"
```

The packages were installed on macOS (Apple silicon). RDKit, XGBoost and PyTDC versions matter for exact reproduction of the numbers.

## Running

From the repository root:

```bash
jupyter nbconvert --to notebook --execute phytocyp_pipeline.ipynb --output executed.ipynb
```

or open the notebook and use Run All. The notebook must be started from the repository root (it checks this). All paths are relative.
Random seeds are set (seed 42 for the models, the domain sample and the splits), and a second run gives identical output files.

Runtime: about 6 to 8 minutes on a recent laptop, plus the download of the training data on the first run. The first run needs an internet connection.

## Data

Downloaded by the notebook on first run (`data/raw/`, not stored in the repository):

- The five CYP training sets `CYP1A2_Veith`, `CYP2C9_Veith`, `CYP2C19_Veith`, `CYP2D6_Veith`, `CYP3A4_Veith` from the Therapeutics Data Commons (TDC),
  derived from the PubChem cytochrome P450 qHTS panel (AID 1851). The TDC benchmark split (`admet_group`) is downloaded the same way.
  - Veith H, Southall N, Huang R, et al. Comprehensive characterization of cytochrome P450 isozyme selectivity across chemical libraries. Nat Biotechnol. 2009;27(11):1050-1055. doi:10.1038/nbt.1581
  - Huang K, Fu T, Gao W, et al. Artificial intelligence foundation for therapeutic science. Nat Chem Biol. 2022;18(10):1033-1036. doi:10.1038/s41589-022-01131-2
  - The TDC code is under the MIT licence; for each dataset the TDC README refers to the licence on the TDC website. Check it before redistributing derived data.

Shipped in `data/` (hand-curated, with the source recorded per row):

| File | Content | Source |
|---|---|---|
| `herb_constituents.csv` | 71 herb-compound listings with PubChem CID, SMILES and the published review each came from | One review per herb (citation, PMID and DOI per row) |
| `herb_selection_sources.csv` | Why each of the 17 herbs was chosen (surveys, regulator, traditional use) | Citations per row |
| `cyp_drug_substrates.csv` | 97 drugs, 99 drug-enzyme entries, with the FDA class (59 sensitive, 40 moderate) and a narrow therapeutic index flag (6 drugs) | FDA, "Drug Development and Drug Interactions: Examples of Drugs that Interact with CYP Enzymes and Transporter Systems", retrieved 26 October 2026, https://www.fda.gov/drugs/drug-interactions-labeling/healthcare-professionals-fdas-examples-drugs-interact-cyp-enzymes-and-transporter-systems ; Donnelly M, et al. Narrow therapeutic index drugs: FDA experience, views, and operations. Clin Pharmacol Ther. 2025;117(1):116-129. doi:10.1002/cpt.3460 |
| `chembl_measured.csv` | 248 ChEMBL activity records for the herb compounds on the five enzymes, frozen | ChEMBL web service, retrieved 27 October 2026 (release not recorded); Zdrazil B, et al. The ChEMBL Database in 2023. Nucleic Acids Res. 2024;52(D1):D1180-D1192. doi:10.1093/nar/gkad1004. ChEMBL data are released under the Creative Commons Attribution-ShareAlike 3.0 Unported licence |
| `sfda_signals.csv` | 41 herb-drug signals assessed by the Saudi Food and Drug Authority | Alghamdi W, et al. Signal detection and assessment of herb-drug interactions: Saudi Food and Drug Authority experience. Drugs Real World Outcomes. 2023;10(4):577-585, Table 2. doi:10.1007/s40801-023-00388-w |
| `c3_mskcc_lookup.csv`, `STEP_8c_c3_independent*.csv` | What the Memorial Sloan Kettering "About Herbs" guide says for the 12 herbs checked (8 with a page, 4 without), checked 29 October 2026; a second independent lookup | https://www.mskcc.org/cancer-care/diagnosis-treatment/symptom-management/integrative-medicine/herbs |
| `pgx_phenotype_frequencies.csv` | Published and derived metaboliser phenotype frequencies | Goljan 2022; Qumsieh 2011; Aynacioglu 1999; Koopmans 2021 (full citations in the `Source` column) |
| `benchmark/deepcyps_predictions.csv` | Stored DEEPCYPs predictions for the 71 listings (see below) | Ai D, et al. DEEPCYPs: a deep learning platform for enhanced cytochrome P450 activity prediction. Front Pharmacol. 2023;14:1099093. doi:10.3389/fphar.2023.1099093 |
| `benchmark/deepcyps_input.csv`, `constituents_keyed.csv`, `comparator_survey.csv` | Input for the DEEPCYPs run, InChIKeys for the ChEMBL download, and the survey of comparison tools | Project records |

The data sources keep their own licences and terms. Datasets other than the small tables above are not redistributed here.

## Data provenance

`data/chembl_measured.csv` was merged from two ChEMBL downloads (activities and assays) retrieved from the ChEMBL web service on 27 October 2026.
The merge step was not saved as code, so the file is shipped as retrieved. `scripts/fetch_chembl_activities.py` and `scripts/fetch_chembl_assays.py`
document how the raw downloads were made. Licences and terms of the data files are listed in `DATA_LICENCES.md`.

SMILES were retrieved from PubChem by CID; the retrieval step is not part of the shipped code.

## Optional steps (not part of the default run)

**Re-download the ChEMBL records.** `scripts/fetch_chembl_activities.py` and `scripts/fetch_chembl_assays.py` query the ChEMBL web service
for the compounds in `data/herb_constituents.csv` and write to `data/chembl_fetch/`. The merge and filter step that produced the frozen
`data/chembl_measured.csv` from these two downloads was not saved as a script, and the web service changes over time, so a fresh download will not
reproduce the frozen file exactly. The notebook always reads the frozen file.

**Regenerate the DEEPCYPs predictions.** DEEPCYPs is third-party code and is not included. The predictions in `data/benchmark/deepcyps_predictions.csv` were produced
with the authors' published checkpoints (https://github.com/idrugLab/FP-GNN_CYP, commit `4784da71d8a9cce29d102372d27f0fb0ffc27d22`, 14 May 2022):

1. Clone that repository into an empty directory outside this one and create a separate virtual environment for it (used: Python 3.13, torch 2.14.1,
   rdkit 2026.09.1, numpy 2.5.4, scikit-learn 1.9.1, against the authors' pins of Python 3.7, torch 1.9.0, rdkit 2021.09.3, numpy 1.19.5).
2. Run `python scripts/run_deepcyps.py <path-to-clone> data/benchmark/deepcyps_input.csv <output-dir>`. The wrapper allow-lists `argparse.Namespace` for
   `torch.load` (PyTorch 2.6 and later default to `weights_only=True`; `weights_only=False` was not used) and sets `cuda` to false for CPU use. No file in the clone is modified.
3. The script writes one file per enzyme. They were aligned to the rows of `herb_constituents.csv` by canonical SMILES (0 mismatches over 142 checks) and joined into
   `deepcyps_predictions.csv`; that alignment step was done interactively and is not saved as a script.

DEEPCYPs was trained on the same PubChem AID 1851 data as the models here, so the comparison in section 8 of the notebook is not a validation.

**Publish-safety scan.** `python scripts/check_publish_safety.py` scans the repository for absolute local paths, key-like strings and e-mail addresses.

## Outputs

`outputs/` is created by the notebook. `outputs/MAPPING.md` lists every file with its section, contents and the result it feeds. Output file names are provisional and may change before publication. `outputs/data_facts.json` holds every count quoted by the accompanying web app. Section 10 of the notebook adds the baseline, confidence-interval and training-versus-held-out tables (`tableS25` to `tableS29`), which are written to `outputs/` when the notebook runs.

Reference values from the run that produced the numbers above: scaffold-grouped cross-validation sensitivity at the 0.5 threshold 83.5% (CYP1A2), 72.0% (CYP2C9), 82.7% (CYP2C19),
49.0% (CYP2D6) and 76.8% (CYP3A4); 423 herb-drug pairs; 33 agree, 82 disagree and 308 have no published test; 53 of 71 compounds assessable; 8 of 69 compounds also in the training data.

## Limitations

- The training labels are single-concentration-range screening outcomes (PubChem AID 1851), not potencies.
- 8 of the 69 compounds (apigenin, harmaline, harmalol, harman, harmine, kaempferol, luteolin, quercetin) are also in at least one training set; their predictions are not independent tests.
- Herb scores use the highest compound probability; no concentrations are available, and combined effects of compounds are not modelled.
- The ChEMBL release behind the frozen measurement file is not recorded.
- The models fit their training data almost perfectly (training AUROC about 0.99); all reported performance is on held-out data.
- Confidence intervals come from 5 cross-validation folds and a bootstrap that treats compounds as independent, although compounds sharing a scaffold are correlated; the bootstrap intervals are therefore optimistic.

## Web application

The web application lives in `app/` and is live at https://phytocyp-tracker.streamlit.app.

## Licensing

The code is under the MIT licence (`LICENSE`). The data files have their own terms, listed in `DATA_LICENCES.md`.
Tables compiled by the author are CC BY 4.0, except the files listed in `DATA_LICENCES.md` as under other terms
(`chembl_measured.csv` is CC BY-SA 3.0 and `sfda_signals.csv` is CC BY-NC 4.0).
