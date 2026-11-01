# Output mapping

Provisional names for the files the notebook (`phytocyp_pipeline.ipynb`) writes to `outputs/`. Rename them once the manuscript numbering is fixed.
`table` and `fig` without `S` are the main-text candidates; `S` marks supplementary or intermediate files.

The numbers in the last column are those of the reference run (31 October 2026). Section numbers refer to the notebook.

## Tables

| File | Section | Contents | Feeds |
|---|---|---|---|
| `table1_training_data_cleaning.csv` | 2 | Per enzyme: starting rows, invalid structures, structures with conflicting labels, duplicates, final compounds, inhibitor fraction | Training counts: 12,579 to 12,549 (CYP1A2), 12,092 to 12,046 (CYP2C9), 12,665 to 12,620 (CYP2C19), 13,130 to 13,086 (CYP2D6), 12,328 to 12,296 (CYP3A4) |
| `table2_model_validation_per_enzyme.csv` | 2 | Per enzyme: compounds, percent inhibitors, scaffolds, scaffold-grouped 5-fold cross-validation (AUROC, AUPRC, sensitivity, specificity) and the AUROC of one scaffold split | Sensitivity 84, 72, 83, 49, 77% (cross-validation, 0.5 threshold); percent inhibitors 46.4, 33.5, 46.0, 19.1, 41.5 |
| `table3_tdc_benchmark.csv` | 2 | AUPRC on the TDC benchmark split (five seeds) for CYP2C9, CYP2D6, CYP3A4, against the best published value | Benchmark comparison |
| `table4_herb_constituent_predictions.csv` | 2 | Probability of each of the 71 herb compounds for each enzyme (blank when outside the applicability domain), domain flags, counts of flagged and assessable enzymes | Probabilities; 53 of 71 compounds assessable; herb-level highest probability |
| `table5_herb_drug_pairs.csv` | 5.1, 5.2 | The 423 herb-drug-enzyme pairs: highest probability, driver compound, drug class, narrow therapeutic index, tier, lab-comparison status | 423 pairs; 33 agree, 82 disagree, 308 untested |
| `table6_priority_pairs.csv` | 5.1, 5.2 | The 29 pairs with a narrow therapeutic index drug and their lab-comparison status | 29 priority pairs (3 agree, 6 disagree, 20 untested) |
| `table7_chembl_comparison.csv` | 5.2 | Independent IC50 and Ki medians (nM) against the model probability, per compound and enzyme | Lab-comparison counts; cut-off sensitivity |
| `table8_sfda_comparison.csv` | 5.3 | Signals of the Saudi Food and Drug Authority report that the model can judge, with the model result | SFDA comparison |
| `table9_pair_table.csv` | 5.5, 9 | One row per pair with the labels shown to users (drug class, narrow therapeutic index, prior documentation, lab check) and a flag for drivers also present in the training data | Result cards of the web app |
| `tableS1_absent_combinations.csv` | 5.5 | The 1,260 herb-drug-enzyme combinations without a pair, with the reason | "Not flagged" and "could not assess" cards |
| `tableS2_cyp3a4_logreg_vs_xgboost.csv` | 3.1 | Logistic regression against XGBoost on a random 80/20 split of CYP3A4 | Algorithm choice |
| `tableS3_calibration.csv` | 4 | Expected and maximum calibration error, Brier score, over-call gap per enzyme (80/20 scaffold split) | Calibration |
| `tableS4_y_scrambling.csv` | 4 | AUROC of real and label-shuffled models | Leakage check |
| `tableS5_scaffold_split_sensitivity.csv` | 4 | Sensitivity, specificity, AUROC of the 80/20 scaffold split per enzyme | CYP2D6 sensitivity 33% on this split against 49% in cross-validation |
| `tableS6_deepcyps_agreement.csv` | 8 | Agreement of the models with DEEPCYPs per enzyme (Spearman, binary agreement at 0.70) | Tool comparison (not a validation) |
| `tableS7_deepcyps_flagged_calls.csv` | 8 | Each flagged compound-enzyme call and whether DEEPCYPs also flags it | Tool comparison |
| `tableS8_herb_level_scores.csv` | 6 | Per herb and enzyme: maximum, number flagged, second highest, mean, mean of the top two | Herb score (maximum rule) |
| `tableS9_mixture_rule_sensitivity.csv` | 6 | Rank correlation of the maximum with the mean and top-two rules | Rule sensitivity |
| `tableS10_priority_pairs_annotated.csv` | 6 | Priority pairs with the number of flagged compounds and the margin to the second compound | Single-compound dependence |
| `tableS11_prior_documentation_agreement.csv` | 5.4 | Prior-documentation label of the 29 priority pairs against a second independent lookup of the herb guide | 29 pairs compared |
| `tableS12_prior_documentation_rule_sensitivity.csv` | 5.4 | Labels and tiers under three matching rules | Rule sensitivity |
| `tableS13_pharmacist_review_sheet.xlsx` | 5.4 | Review workbook (sheets: Review, Method, C3 sensitivity, C3 evidence, Dropped - regional availability, Glossary) | Pharmacist review |
| `tableS14_herb_enzyme_overview.csv` | 9 | Per herb and enzyme: highest probability, assessable compounds, compounds at 0.5 or more | Herb overview of the web app |
| `tableS15_enzyme_sensitivity.csv` | 9 | Cross-validation sensitivity per enzyme | Sensitivity table of the web app |
| `tableS16_herb_raw_probabilities.csv` | 2 | Unmasked model probabilities of the herb compounds (also outside the domain) | Used by the DEEPCYPs comparison by domain |
| `tableS17_pgx_derived_phenotypes.csv` | 7.1 | Metaboliser phenotype frequencies derived from published allele frequencies | Pharmacogenomic layer |
| `tableS18_pgx_derivation_check.csv` | 7.1 | Derived against reported phenotype frequencies | Check of the derivation |
| `tableS19_phenoconversion_invariance.csv` | 7.2 | Mean activity score before and after a moderate inhibitor, per population | Invariance of the relative effect |
| `tableS20_baseline_reserve.csv` | 7.2 | Share of each population at full CYP2D6 activity | Baseline reserve |
| `tableS21_activity_before.csv`, `tableS22_activity_after_moderate.csv` | 7.2 | Activity-score distributions before and after a moderate inhibitor | Phenoconversion |
| `tableS23_threshold_sweep.csv` | 7.2 | Converted fraction across thresholds and conventions | Instability of threshold-based counts |
| `tableS24_deepcyps_agreement_by_domain.csv` | 8 | Agreement with DEEPCYPs for compounds inside and outside the applicability domain of each enzyme | Tool comparison |
| `data_facts.json` | 9 | Every count quoted by the web app: training counts, herbs (17 herbs, 71 listings, 69 different compounds, 53 assessable), drugs (97 drugs, 99 entries, 59 sensitive, 40 moderate, 6 narrow therapeutic index), compounds also in training data (8 of 69), lab comparison (248, 125, 123; 33, 82, 308; 115 of 423), herb guide (12 checked, 8 with a page, 4 without; 29 October 2026) | Numbers in the web app |

## Figures

| File | Section | Contents |
|---|---|---|
| `fig1_calibration_reliability.png` | 4 | Reliability diagrams per enzyme |
| `fig2_y_scrambling.png` | 4 | AUROC of shuffled-label models against the real model |
| `fig3_deepcyps_scatter.png` | 8 | Own model against DEEPCYPs per enzyme |
| `fig4_mixture_scoring.png` | 6 | Alternative herb-score rules against the maximum, and number of flagged compounds |
| `figS1_cyp3a4_logreg_vs_xgboost.png` | 3.1 | ROC and precision-recall curves |
| `figS2_shap_summary.png`, `figS3_shap_logp.png` | 3.2 | SHAP summary and the lipophilicity dependence (CYP3A4) |
| `figS4_shap_10_gingerol.png`, `figS4_shap_apigenin.png`, `figS4_shap_curcumin.png` | 3.2 | SHAP explanation of three flagged herb compounds |
| `figS5_pgx_activity_distributions.png`, `figS6_pgx_cumulative_curves.png` | 7.2 | Activity-score distributions and cumulative curves |
