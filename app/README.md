# PhytoCYP Tracker (Streamlit app)

**PhytoCYP Tracker is a research prototype.** A screening tool for the paper *Machine Learning Prediction of Cytochrome P450 Inhibition by Constituents of Commonly Used Middle Eastern Medicinal Herbs*. Choose a herb and a drug; the app shows a title, the stored model probability, one summary sentence built from the reference check, and four plain finding rows (substrate sensitivity, narrow therapeutic index, prior documentation, reference check), with a collapsed "About this model" link. It reads stored results only: no model runs in the app, nothing is uploaded, nothing is logged.

**Research screening result. Not clinical advice.** The app has no yes/no verdict and does not track users.

An earlier single-file HTML version exists only on the author's computer and is not part of this repository.

## What is in this folder

| Path | What it is |
|---|---|
| `streamlit_app.py` | Entry point. Layout and widgets only. |
| `render.py` | Pure functions that turn data into HTML strings (every data-derived string is HTML-escaped). No Streamlit calls. |
| `theme.py` | Every colour and all CSS, for light and dark. No colour is written anywhere else. The look is a plain reference-entry page: no cards, chips, tints or uppercase labels. |
| `data/` | The four csv files and `data_facts.json` (the numbers in "The data in plain English") the app reads. **Written only by `notebooks/18_streamlit_data.ipynb`.** Do not edit by hand. |
| `assets/logo.svg` | The logo (used in the sidebar, the entry notice and the browser tab). |
| `requirements.txt` | Pinned `streamlit`, `pandas` and `altair` (the three libraries the app imports), nothing else. |
| `test_render.py`, `test_app.py` | Unit tests and browser tests, run by `notebooks/19_streamlit_tests.ipynb`. |
| `screenshots/` | Written by notebook 19. |
| `../.streamlit/config.toml` | Light base theme, no usage statistics, viewer toolbar. |

## Run it locally

From the project root, in an environment that has the two packages in `requirements.txt`:

```
streamlit run app/streamlit_app.py
```

## Recreate the test environments

Both live **outside the repository**; nothing is installed into it.

```
python3 -m venv ~/.cache/herb-cyp-ml-streamlit/env
~/.cache/herb-cyp-ml-streamlit/env/bin/pip install -r app/requirements.txt

python3 -m venv ~/.cache/herb-cyp-ml-playwright/env
~/.cache/herb-cyp-ml-playwright/env/bin/pip install playwright==1.49.1
```

The browser tests use the installed Google Chrome. Then run `notebooks/18_streamlit_data.ipynb` and `notebooks/19_streamlit_tests.ipynb` in order (19 starts and stops its own server on a free local port).

Tested with Streamlit **1.66.1**, pandas 3.1.0, altair 6.3.0, Python 3.13.17 (also installed from `app/requirements.txt` alone in a fresh virtual environment and started from a copy holding only the published files).

## Before you publish

```
.venv/bin/python scripts/check_publish_safety.py
.venv/bin/python scripts/check_provenance.py
```

The first lists every file that would be published and exits non-zero on an absolute local path, a key-like string, an `.env` file, an e-mail address or a file over 25 MB. It is a pattern scan: it cannot prove a file is free of sensitive content, and it does not read inside the PNG screenshots.

## Deploy on Streamlit Community Cloud (done by you; nothing here has been deployed)

1. Put the project in a GitHub repository (public repositories work on the free plan). The files the app needs are `app/`, `.streamlit/config.toml` and nothing else; the rest of the project may stay in the repository or not.
2. Sign in at share.streamlit.io with GitHub and choose **Create app** → **Deploy a public app from GitHub**.
3. Repository: yours. Branch: `main`. **Main file path: `app/streamlit_app.py`.**
4. Under **Advanced settings**, choose a Python version (3.12 or 3.13; the app was tested on 3.13).
5. Dependencies: Community Cloud looks for a requirements file next to the main file first, so `app/requirements.txt` is used. If you also keep the project's own `requirements.txt` at the repository root, the one in `app/` is the one that matters; the root file holds the full research environment and should not be the one the app installs.
6. Deploy. No secrets are needed.

## What changed in the second design pass

- The pastel tiles, pills, chips and uppercase labels are gone; the Result tab is a title, a number, one sentence and four hairline-separated rows.
- The Continue button text was invisible (dark on dark): a general paragraph-colour rule outranked the button rule. The button now has white text in every state in both themes.
- The thick blue bar beside the search box arrow was the focus outline of the inner typing field; the ring is now drawn around the whole box.
- The narrow therapeutic index explanation is now the neutral definition for Yes and No.
- The About tab has "The data in plain English" and a word list; every number in it is written by notebook 18 to `app/data/data_facts.json`.
- `.gitignore` lists `.venv`, `env/`, `.env` files and caches.

## Round 2 of the design (29 Oct 2026)

- The gate notice is one paragraph. The summary sentence sits on a pale band (the only background fill on the Result page); each finding row has a 4 px marker in a fixed colour for its type of information (blue, lilac, sand, teal); herb names are lower case inside sentences.
- Herb overview chart: bars below 0.5 are pale blue, bars at or above 0.5 medium blue; the dashed 0.5 line has a thin halo and is drawn above the bars. In dark mode the "reached 0.5" blue is `#4E84C8` rather than `#7FB0E8`, so that the pale light line keeps 3:1 contrast against it.
- In dark mode the chart line under the bars reads "Brighter bars reached the 0.5 threshold." because the flagged bars are the lighter ones there; in light mode it reads "Darker bars…" as specified.
- The bottom banner is a pale blue-grey band (dark slate on light, light slate on dark), no longer navy.
- The drug box is labelled "Drug" (placeholder "Search for a drug", caption "Each drug is listed with its enzyme."); every option still shows its enzyme.
- The About tab is a short opening, one source table (Data, Source, Used for), five "Details" disclosures, "Key terms" and "References" (since replaced: see round 7 below). Every number in it is written by notebook 18 to `app/data/data_facts.json`, which also holds the herb-selection basis (13 survey herbs, 2 regulator-only, 2 traditional-use-only) and the 17 herb references.
- "17 medicinal herbs used in the Middle East" replaces "17 commonly used Middle Eastern herbs": the repo's records show survey prevalence figures for 13 herbs only; turmeric and ginkgo come from the Saudi regulator's assessment and olive and harmal from documented traditional use, with no prevalence figure.
- The sand marker colour is a muted tan (hue about 40 degrees); it is exempt by name from the "no amber" test, because it marks a type of information and never a status.
- One reference title in the list (the cinnamon review) contains the word "safe"; reference titles are quoted verbatim and are excluded from the banned-word sweep.

## Round 3 of the design (30 Oct 2026)

- The "Prototype" tag and the word "lookup" are gone (subtitle: "Herb and cytochrome P450 screening"); the notice still opens with "PhytoCYP Tracker is a research prototype."
- The bottom banner is removed on every screen, with the padding reserved for it. The disclaimer now lives in the gate notice only: the Model and limits tab lost its first paragraph in round 2 and the About opening does not repeat it.
- The theme switch moved out of the sidebar to the top right of the main area: on the tab row on a computer, left of Streamlit's three-dot menu and right-aligned with the content column; on the top row on a phone. It is raised above Streamlit's header so a tap reaches it. Space works natively; Enter works through a 1-pixel helper frame (`st.iframe`) that only listens for Enter while the switch has focus.
- Row markers are 5 px: blue #4F86C6, violet #8B6FC0, rose #C9739B, teal #2F9C95 (lighter equivalents in dark mode). The colour rule is now enforced by the explicit allowlist in `app/theme.py` and the tests, not by hue ranges.
- "Assessable compounds" became "herb chemicals the model could judge" (singular: "herb chemical") on the result, "Chemicals the model could judge" in the overview and About tables. The stored reasons for absent combinations (in `app/data/`, written by notebook 18 from the project's results) say "assessed" and were not edited.
- Model and limits lost two sentences; the drug caption is italic without a full stop; the About tab has a new opening, no closing line, no "Herb pages" disclosure and no "Key terms".

## Round 4 of the design (30 Oct 2026)

- Gate notice: the first two sentences became one: "PhytoCYP Tracker is a research prototype and a research screening aid built from a machine-learning model and published data." The rest of the paragraph is unchanged.
- The Herb and Drug boxes: when clicked or focused they get a thin 1 px slate border on the outer box only (`#1F2A44` in light mode, `#E2E8F0` in dark mode, both already on the allowlist, at least 3:1 against the page); no blue outline, glow or shadow, and nothing on the inner typing field.
- About: the "Where the data comes from" heading and table were replaced by a small italic "Data sources:" note. The four disclosures (now without the "Details:" prefix) are unchanged and the "References" section was removed in round 7; the two tables inside the collapsed "Details" disclosures (chemicals per enzyme, compounds per herb) were kept.

## Round 5 of the design (30 Oct 2026)

- The four finding rows on the Result tab have an 8 px gap between them, so each coloured marker is a separate block (hairlines kept).
- The herb overview table is sized to its content with even column gaps instead of stretching across the page.
- The About "Data sources:" note has the same size and text colour as the opening paragraph (still italic).
- Streamlit Community Cloud adds a "Fork" and a GitHub button to the toolbar. No configuration setting hides only Fork (`toolbarMode = "viewer"` hides developer options; "minimal" keeps options set externally, which is what these two buttons are), so one narrow rule in `theme.py` hides the toolbar button that carries a text label. The GitHub icon is unlabelled and stays. The rule is tested here against a copy of the live toolbar markup; it only has an effect on the deployed page.
- Chart text on phones (31 Oct 2026): all chart text is 11 px, the "0.5 threshold" label is on two lines and the extra right margin was removed, so on a 390 px phone the bars are about 55 px apart and every text is at least 16 px clear of the next. On plots narrower than 235 px (about 320 px phones) the enzyme names tilt 45 degrees so nothing overlaps.

## Round 6 of the design (31 Oct 2026)

- The herb overview table is as wide as the chart below it. It is laid out as a grid of four automatic columns, so every header sits on one row on a computer and the free width is shared equally between the columns (even gaps, numbers directly under their headers, hairline rows). Table roles are set explicitly so screen readers still read it as a table. On a phone headers may wrap; nothing is cut off. All tables now keep their headers on one row on a computer.
- The sidebar logo block and the tab row start on the same line, 24 px under Streamlit's 60 px header band (84 px from the top of the page). The collapse arrow sits in the header band, 38 px above the logo, no longer touching the top edge. On a phone the theme switch stays in the header band beside the menu, above the content.
- `.devcontainer/` is removed again. It is GitHub's Codespaces template and it comes back when the pencil (edit) icon in Streamlit's owner toolbar offers to add a dev container: do not click it.

## Round 7 of the design (31 Oct 2026)

- About: "Data sources" (no colon, bold, own line) now sits above an upright paragraph that has exactly the opening paragraph's font family, size, colour and line height. The pointer to the removed section is gone from the Herb compounds sentence.
- About: the "References" section is removed. The published review behind each herb's compounds (one per herb, 17 in all, written by notebook 18 into `app/data/data_facts.json`) is now listed herb by herb inside the "Herb compounds" disclosure, below its text and table. The full formal citations of Veith et al. 2009, Donnelly et al. 2024, the FDA table, the Therapeutics Data Commons, ChEMBL and the three papers on the choice of the Memorial Sloan Kettering guide no longer appear in the app; the Data sources note names them. They remain in the project's own records.
- The four disclosures are labelled exactly "Enzyme-blocking tests", "Herb compounds", "Drug list" and "Published lab measurements".
- Dark mode: Streamlit Community Cloud draws its toolbar GitHub icon as an image with the light-mode text colour baked in, which vanished on the dark page. One narrow rule in `theme.py` (dark mode only) turns that single icon light grey. It cannot be seen on a local run, because the button only exists on the deployed page; the test checks the rule against a copy of Cloud's icon image and the deployed page is checked after each push.

## Round 7c of the design (31 Oct 2026)

- The full formal citations are back in the About tab, inside the disclosures where they belong, with no separate References section: "Enzyme-blocking tests" (Veith et al. 2009; the two Therapeutics Data Commons papers), "Drug list" (the FDA table with its retrieval date; Donnelly et al.), "Published lab measurements" (the ChEMBL database paper and the ChEMBL web services paper), and "Herb compounds" (the review behind each herb, as before). Prior documentation has its own short paragraph under the Data sources paragraph: the Memorial Sloan Kettering "About Herbs" guide with its check date, and the papers by Sansevere and White, Rizvi et al., and Hou et al. that support using it.
- One style for all: the first six authors then "et al.", a sentence-case title, journal, year and numbers, then the DOI (or web address) as a link that opens in a new tab.
- Every DOI was checked before use against PubMed, Crossref or DataCite, and the FDA and MSK pages were opened. The ChEMBL release number was not recorded when the data were fetched, so none is stated.
- The root `README.md` data sources paragraph lists the same sources as the About tab.

## Round 7d of the design (31 Oct 2026)

- The About tab keeps six general citations, each in its disclosure: Veith et al. 2009 and Huang et al. 2022 (the only Therapeutics Data Commons citation) in "Enzyme-blocking tests"; the FDA examples page (with its retrieval date) and Donnelly et al. 2025 in "Drug list"; Zdrazil et al. 2024 (ChEMBL) in "Published lab measurements"; the Memorial Sloan Kettering "About Herbs" guide (with its check date) in the Prior documentation paragraph. The herb-by-herb review list in "Herb compounds" is unchanged.
- Removed: the Therapeutics Data Commons NeurIPS 2021 paper, the ChEMBL web services paper, and the Sansevere, Rizvi and Hou papers, with the sentence that introduced them. The Prior documentation paragraph now cites only the MSK guide.
- The FDA link now points to the "FDA's Examples of Drugs that Interact with CYP Enzymes and Transporter Systems" page, which is where the drug list comes from (the old link was the index table page). The page's definitions match the app: sensitive is an AUC increase of 5-fold or more, moderate is 2-fold or more but under 5-fold.
- Donnelly et al. is cited as 2025;117(1):116-129, published online 11 November 2024.
- Root README: the Data sources paragraph keeps source names only (no full citations), matching the six; the full citations live in the About tab.

## Round 8 of the design (31 Oct 2026)

- The About tab carries no citations any more: the six citation links (Veith, Huang, the FDA examples page, Donnelly, Zdrazil, the Memorial Sloan Kettering guide), the "Sources" blocks in all four disclosures and the list of the published review behind each herb are removed. The Data sources paragraph still names the sources in plain text and now ends with "Lab measurements: ChEMBL."
- The Prior documentation paragraph is gone from About. The Model and limits tab and the Result tab still name the Memorial Sloan Kettering guide. The review references stay in `data/data_facts.json` and `data/herb_constituents.csv`.
- New limit lines: "Limit: these are laboratory results, not results in patients." (Enzyme-blocking tests) and "Limit: the FDA has no official list of narrow therapeutic index drugs, so these {n} come from a published paper." (Drug list, number computed from the data).
- The Herb compounds paragraph no longer shows the bracketed group counts (13, 2, 2) and says "one published source"; the herb total, compound range, 71 in all and 53 judged are still computed from `data_facts.json`.
- The unused citation code (the citation table, link and citation helpers, the FDA and MSK address constants) and its three style rules were deleted. The earlier Round 7c and 7d sections above describe a state that no longer applies to About.
- Root `README.md`: the Data sources paragraph keeps the source names and no longer points to citations in the About tab.

## Round 9 of the design (31 Oct 2026)

- The Data sources paragraph now says "Herb compounds: published sources." (was "published reviews"), to match the Herb compounds disclosure ("one published source"). Nothing else in the paragraph changed.
- Dark-mode GitHub icon on the deployed page was checked on the live app: it is drawn light (about 234, 234, 234 on a 11, 18, 32 page, about 15:1) on desktop and phone, so the dark rule from round 7 stays unchanged.
- Found on the live app: on a 390 px phone the theme switch covered the toolbar GitHub icon (both themes). The phone switch now sits 96 px from the right edge instead of 56 px, ending left of the icon; the test checks the clearance.

## Round 10 of the design (31 Oct 2026): fixes from the final audit

- **In-training compounds.** Eight of the 69 distinct herb compounds (apigenin, harmaline, harmalol, harman, harmine, kaempferol, luteolin, quercetin) are also in the training sets (found by notebook 18 by comparing standardised structures; recorded in `data_facts.json`, `in_training`). A Result card whose driver compound was in the training data of that card's enzyme (39 pairs) shows a plain dagger beside the driver and a muted legend line under the metadata; the probability stays. Model and limits has the limit line "8 of the 69 compounds were also in the training data, so their predictions are not independent tests." There is no per-compound table in the app, so the marker sits on the Result card.
- **Eliglustat on CYP3A4** is now a moderate sensitive substrate (the FDA table lists it as sensitive for CYP2D6 only). Drug counts: 59 sensitive and 40 moderate (still 97 drugs and 99 entries). Four pairs (Chamomile, Parsley, Ginger, Ginkgo with eliglustat on CYP3A4) change their class label and their research tier (2, 2, 3, 3 become 4); no probability, driver, flag or lab check changed.
- **PubChem CID** of furanoeudesma-1,3-diene is 13874240 (was 5281531) in all four files that held it; the SMILES already matched. No prediction changed.
- The internal "pending verification" note was removed from `src/mixture.py` (logic untouched).
- Model and limits: "CYP2D6 sensitivity is 49% in the main evaluation and 33% on the harder 80/20 split, so 49% is the more favourable figure." The 33% comes from `results/scaffold_split_sensitivity.csv`, a new file written by notebook 12.
- About, Published lab measurements: "the lab comparison covers 115 of the 423 herb-drug pairs; the other 308 have no published test" (from `data_facts.json`).

## Round 11 of the design (31 Oct 2026)

- Model and limits: the line "CYP2D6 sensitivity is 49% in the main evaluation and 33% on the harder 80/20 split ..." was removed (round 10 had added it). The sentence above it and the table stay. `results/scaffold_split_sensitivity.csv` and the cell in notebook 12 that writes it stay; the app no longer reads the file (notebook 18 and `render.py` lost the code that used it, and `enzyme_sensitivity.csv` is back to two columns).
- About, Herb compounds: "(71 in all)" now reads "(71 listings, 69 different compounds)", both computed from `data/herb_constituents.csv` by notebook 18 (`n_compounds`, `n_distinct_compounds` in `data_facts.json`; apigenin and luteolin are listed under two herbs). Model and limits still says "8 of the 69 compounds" and the two numbers agree (notebook 18 asserts it). No other place in the app or the README files states a compound total.

## Limitations (stated in the app too)

- The probabilities are model outputs on held-out-validated data, not measurements in patients.
- A herb's value is the highest probability among its compounds that the model could assess; combined effects of several compounds are not modelled.
- Test sensitivity differs by enzyme (the app shows each one); for CYP2D6 it is lowest, so a missing flag there means less.
- "Not flagged" means no assessed compound reached 0.5. It does not mean there is no interaction. Myrrh could not be assessed for any enzyme.
- Garlic and peppermint rest on a single herb chemical the model could judge.
- The tool covers 17 herbs, 97 drugs and five enzymes only.
- **Dark mode and the browser:** Streamlit itself keeps a theme key in the browser's local storage and sets an anti-forgery cookie (`_streamlit_xsrf`). The app adds no cookie, no storage and no logging of its own, but these two come with Streamlit and cannot be removed from inside the app.
- The page icon and the logo are the supplied SVG, unchanged.
- The dropdown lists are drawn by Streamlit in a layer outside the page; they are themed by their accessibility roles, so a future Streamlit version may need the selectors in `theme.py` revisited. That is why the Streamlit version is pinned.
- On a phone (narrow screen) the sidebar starts collapsed; open it with the arrow at the top left.
