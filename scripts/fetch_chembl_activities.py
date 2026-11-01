"""Optional: download ChEMBL activity records for the herb compounds on the five CYP targets.

Run from the repository root:  python scripts/fetch_chembl_activities.py [--limit N]

For each compound in data/herb_constituents.csv the molecule is found by the first block of its InChIKey and its activity records
(limited to the five CYP targets) are written to data/chembl_fetch/chembl_activities.csv. The web service changes over time, so a new download
will not reproduce the frozen file data/chembl_measured.csv exactly; the notebook reads the frozen file. The merge and filter step that produced
that file from this download and the assay download was not saved as a script.
"""
import argparse
import csv
import json
import subprocess
from pathlib import Path

import pandas as pd
from rdkit import Chem
from rdkit.Chem import inchi

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "chembl_fetch"
TARGETS = {"CHEMBL3356": "CYP1A2", "CHEMBL3397": "CYP2C9", "CHEMBL3622": "CYP2C19",
           "CHEMBL289": "CYP2D6", "CHEMBL340": "CYP3A4"}
FIELDS = "target_chembl_id,standard_type,standard_relation,standard_value,standard_units,pchembl_value,assay_chembl_id"
BASE = "https://www.ebi.ac.uk/chembl/api/data"


def get(url):
    result = subprocess.run(["curl", "-s", "--max-time", "40", url], capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


parser = argparse.ArgumentParser()
parser.add_argument("--limit", type=int, default=None, help="only the first N compounds (for a quick test)")
limit = parser.parse_args().limit

herbs = pd.read_csv(ROOT / "data" / "herb_constituents.csv").drop_duplicates("Compound")
compounds = [(row.Compound, inchi.MolToInchiKey(Chem.MolFromSmiles(row.SMILES))) for row in herbs.itertuples()][:limit]

OUT.mkdir(parents=True, exist_ok=True)
with open(OUT / "chembl_activities.csv", "w", newline="") as handle:
    writer = csv.writer(handle)
    writer.writerow(["Compound", "ChEMBL_ID", "Enzyme", "standard_type", "relation", "value", "units", "pchembl", "assay"])
    found = with_data = 0
    for i, (compound, key) in enumerate(compounds, 1):
        skeleton = key.split("-")[0]
        reply = get(f"{BASE}/molecule.json?molecule_structures__standard_inchi_key__startswith={skeleton}&limit=3&only=molecule_chembl_id")
        ids = [m["molecule_chembl_id"] for m in (reply or {}).get("molecules", [])]
        if not ids:
            print(f"{i:3d} {compound:<28} not in ChEMBL")
            continue
        found += 1
        molecule = ids[0]
        reply = get(f"{BASE}/activity.json?molecule_chembl_id={molecule}&limit=1000&only={FIELDS}")
        rows = [a for a in (reply or {}).get("activities", []) if a.get("target_chembl_id") in TARGETS]
        for a in rows:
            writer.writerow([compound, molecule, TARGETS[a["target_chembl_id"]], a.get("standard_type"), a.get("standard_relation"),
                             a.get("standard_value"), a.get("standard_units"), a.get("pchembl_value"), a.get("assay_chembl_id")])
        with_data += bool(rows)
        print(f"{i:3d} {compound:<28} {molecule:<16} {len(rows):4d} CYP activities")
print(f"\nIn ChEMBL: {found}/{len(compounds)}   with CYP data: {with_data}")
