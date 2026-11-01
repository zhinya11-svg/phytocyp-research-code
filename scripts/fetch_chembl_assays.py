"""Optional: download ChEMBL assay metadata (source id, description) for the assays in data/chembl_fetch/chembl_activities.csv.

Run from the repository root after fetch_chembl_activities.py:  python scripts/fetch_chembl_assays.py

The source id separates records that come from the PubChem screening panel the models were trained on from independent measurements.
A failed request is reported and skipped; the script exits with an error if any assay could not be fetched, so no blank row is written.
"""
import csv
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parent.parent / "data" / "chembl_fetch"
assays = sorted(pd.read_csv(OUT / "chembl_activities.csv")["assay"].dropna().unique())
failed = []
with open(OUT / "assay_info.csv", "w", newline="") as handle:
    writer = csv.writer(handle)
    writer.writerow(["assay", "src_id", "description"])
    for assay in assays:
        result = subprocess.run(["curl", "-s", "--max-time", "30",
                                 f"https://www.ebi.ac.uk/chembl/api/data/assay/{assay}.json?only=assay_chembl_id,description,src_id"],
                                capture_output=True, text=True)
        try:
            record = json.loads(result.stdout)
            writer.writerow([assay, record.get("src_id"), (record.get("description") or "").replace("\n", " ")])
        except json.JSONDecodeError:
            failed.append(assay)
print(f"{len(assays) - len(failed)} of {len(assays)} assays fetched")
if failed:
    print("not fetched:", ", ".join(failed))
    sys.exit(1)
