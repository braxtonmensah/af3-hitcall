"""Boltz-2 virtual screen against the RNase J : MPN621 interface. Clean-room and commercial-safe.

Why Boltz-2 and not AlphaFold: AlphaFold Server's Output Terms forbid use "IN CONNECTION WITH ANY
AUTOMATED SYSTEM THAT PREDICTS THE BINDING OR INTERACTION OF THE PROTEIN WITH LIGANDS OR PEPTIDES".
Boltz-2 is MIT-licensed, predicts binding affinity natively, and permits commercial use.

Strategy: screen **approved drugs first**. They cost $50-150 to buy, are already safety-tested, and a
hit is a repurposing story that is much faster to publish and fund than novel chemistry. Designing a
genuinely new molecule means custom synthesis at roughly $5k-50k per compound, which is why "find an
existing molecule that binds" is the practical version of "make a compound".

Honest expectations:
  - Protein-protein interfaces are among the hardest small-molecule targets; most are undruggable by
    conventional compounds.
  - Boltz-2's affinity head was trained largely on conventional pockets, so scores at a PPI interface
    are a ranking, not truth.
  - The likely honest outcome is "no convincing hit". That costs ~$2k and still closes or opens the
    compound route, which is what PACE (GBP 1M) and CARB-X require.

Usage:
    python vscreen.py --fetch                  # approved-drug library from ChEMBL (free)
    python vscreen.py --write --limit 400      # Boltz-2 jobs against the interface
    python vscreen.py --write --decoys 50      # random-compound null set
    python vscreen.py --write --offtarget      # same compounds vs human CPSF73 (selectivity)
    # on a rented GPU only (never IU hardware, see COMMERCIAL.md):
    #   pip install boltz -U
    #   boltz predict cleanroom/vscreen_yaml --use_msa_server --out_dir cleanroom/vscreen_out
    python vscreen.py --rank                   # rank, with decoy null and selectivity check
"""
import argparse
import csv
import glob
import json
import os
import random

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, "library_approved.smi")
YDIR = os.path.join(HERE, "vscreen_yaml")
ODIR = os.path.join(HERE, "vscreen_out")
TARGET_ACC = "P75497"          # RNase J, the interface-bearing subunit
OFFTARGET_ACC = "Q9UKF6"       # human CPSF73, the selectivity control
IFACE_JSON = os.path.join(HERE, "..", "rnasej", "results_interface.json")
CHEMBL = "https://www.ebi.ac.uk/chembl/api/data/molecule"
TAB = "\t"


def fetch_library():
    """Approved small molecules from ChEMBL (free REST API; data CC BY-SA 3.0)."""
    rows, offset = [], 0
    while True:
        r = requests.get(CHEMBL, params={"max_phase": 4, "format": "json", "limit": 1000, "offset": offset}, timeout=180)
        r.raise_for_status()
        j = r.json()
        for m in j.get("molecules", []):
            smi = (m.get("molecule_structures") or {}).get("canonical_smiles")
            if smi and len(smi) <= 200 and m.get("molecule_type") == "Small molecule":
                rows.append((smi, m["molecule_chembl_id"]))
        if not (j.get("page_meta") or {}).get("next"):
            break
        offset += 1000
        print("  fetched", len(rows), flush=True)
    seen, uniq = set(), []
    for smi, cid in rows:
        if smi not in seen:
            seen.add(smi)
            uniq.append((smi, cid))
    with open(LIB, "w") as f:
        for smi, cid in uniq:
            f.write(smi + TAB + cid + "\n")
    print("library:", len(uniq), "approved small molecules ->", LIB)


def seq(acc):
    t = requests.get("https://rest.uniprot.org/uniprotkb/" + acc + ".fasta", timeout=60).text
    return t.split("\n", 1)[1].replace("\n", "")


def pocket_residues():
    if not os.path.exists(IFACE_JSON):
        return []
    d = json.load(open(IFACE_JSON))
    out = []
    for r in d["interface_residues"]["RNaseJ"]:
        n = "".join(c for c in r if c.isdigit())
        if n:
            out.append(int(n))
    return sorted(out)


def write_jobs(limit, decoys, offtarget):
    os.makedirs(YDIR, exist_ok=True)
    acc = OFFTARGET_ACC if offtarget else TARGET_ACC
    prot = seq(acc)
    pocket = [] if offtarget else pocket_residues()
    lib = [l.split(TAB) for l in open(LIB).read().splitlines() if TAB in l]
    if decoys:
        random.seed(25)
        chosen = random.sample(lib, min(decoys, len(lib)))
        tag = "decoy_"
    else:
        chosen = lib[:limit]
        tag = "off_" if offtarget else ""
    for smi, cid in chosen:
        y = ["version: 1", "sequences:",
             "  - protein:", "      id: A", "      sequence: " + prot,
             "  - ligand:", "      id: L", "      smiles: '" + smi + "'",
             "properties:", "  - affinity:", "      binder: L"]
        if pocket:
            # steer to the PPI interface, not the catalytic site: the interface is only 24.6% identical
            # to human CPSF73, while the active site keeps 3 of 4 catalytic residues
            contacts = ", ".join("[A, " + str(p) + "]" for p in pocket[:20])
            y += ["constraints:", "  - pocket:", "      binder: L", "      contacts: [" + contacts + "]"]
        open(os.path.join(YDIR, tag + cid + ".yaml"), "w").write("\n".join(y) + "\n")
    print("wrote", len(chosen), "jobs to", YDIR, "| target:", acc, "| pocket residues:", len(pocket))


def rank():
    rows = []
    for f in glob.glob(os.path.join(ODIR, "**", "affinity_*.json"), recursive=True):
        d = json.load(open(f))
        name = os.path.basename(f).replace("affinity_", "").replace(".json", "")
        rows.append({"id": name,
                     "is_decoy": name.startswith("decoy_"),
                     "is_offtarget": name.startswith("off_"),
                     "pred_affinity": d.get("affinity_pred_value"),
                     "binary_prob": d.get("affinity_probability_binary")})
    if not rows:
        print("no results in", ODIR, "- run boltz predict first")
        return
    real = [r for r in rows if not r["is_decoy"] and not r["is_offtarget"]]
    dec = [r for r in rows if r["is_decoy"]]
    real.sort(key=lambda r: -(r["binary_prob"] or 0))
    out = os.path.join(HERE, "vscreen_shortlist.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["rank", "id", "pred_affinity", "binary_prob"])
        w.writeheader()
        for i, r in enumerate(real[:25], 1):
            w.writerow({"rank": i, "id": r["id"], "pred_affinity": r["pred_affinity"], "binary_prob": r["binary_prob"]})
    print(len(real), "compounds scored; top 25 ->", out)
    if dec:
        best_dec = max((d["binary_prob"] or 0) for d in dec)
        n_above = sum(1 for r in real if (r["binary_prob"] or 0) > best_dec)
        print("decoy null: best decoy prob", round(best_dec, 3), "|", n_above, "real compounds beat every decoy")
        if n_above == 0:
            print("  -> the screen found nothing. Do not buy compounds. This is a valid, cheap answer.")
    off = {r["id"].replace("off_", ""): r["binary_prob"] for r in rows if r["is_offtarget"]}
    if off:
        print("\nselectivity check vs human CPSF73:")
        for r in real[:10]:
            o = off.get(r["id"])
            if o is not None:
                flag = "  <-- liability" if o >= (r["binary_prob"] or 0) else ""
                print("  ", r["id"], "target", round(r["binary_prob"] or 0, 3), "CPSF73", round(o, 3), flag)
    print("\nBefore spending money: get a written MIC quote for M. pneumoniae. It is slow and fastidious")
    print("to culture, and M. genitalium is worse. Quote first, buy second.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--rank", action="store_true")
    ap.add_argument("--limit", type=int, default=400)
    ap.add_argument("--decoys", type=int, default=0, help="write N random-compound decoy jobs as a null")
    ap.add_argument("--offtarget", action="store_true", help="write jobs against human CPSF73 instead")
    a = ap.parse_args()
    if a.fetch:
        fetch_library()
    if a.write:
        write_jobs(a.limit, a.decoys, a.offtarget)
    if a.rank:
        rank()
    if not any((a.fetch, a.write, a.rank)):
        ap.print_help()
