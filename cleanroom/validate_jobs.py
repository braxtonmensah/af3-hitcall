"""Validate the virtual-screen YAMLs before paying for GPU time.

Every failure caught here is a job that would otherwise crash mid-run on a rented pod. Checks:
  - the YAML parses and has the fields Boltz-2 needs (protein, ligand, affinity property)
  - the SMILES is parseable by RDKit and sane in size (Boltz-2's affinity head was trained on
    drug-like ligands; a 200-heavy-atom peptide is not a screening hit, it is a crash risk)
  - the MSA path is the pod-side path, identical across jobs, and the file exists locally
  - pocket contacts are 1-based positions inside the protein sequence
  - job ids are unique, so no result silently overwrites another

Usage:
    python validate_jobs.py                 # report
    python validate_jobs.py --prune         # move failing jobs to vscreen_yaml_rejected/
"""
import argparse
import collections
import os
import re
import shutil

from rdkit import Chem, RDLogger

RDLogger.DisableLog("rdApp.*")

HERE = os.path.dirname(os.path.abspath(__file__))
YDIR = os.path.join(HERE, "vscreen_yaml")
RDIR = os.path.join(HERE, "vscreen_yaml_rejected")
MSA_DIR = os.path.join(HERE, "msa")
POD_MSA_PREFIX = "/workspace/screen/msa/"
# Boltz-2 affinity rejects ligands above 128 atoms counting heavy atoms AND hydrogens
# (docs/prediction.md). This is the bound that actually fails jobs at run time.
MAX_TOTAL_ATOMS = 128


def parse(path):
    """Minimal reader for the flat YAML shape vscreen.py writes. Avoids a PyYAML dependency."""
    text = open(path).read()
    seq = re.search(r"sequence:\s*(\S+)", text)
    smi = re.search(r"smiles:\s*'([^']*)'", text)
    msa = re.search(r'msa:\s*"?([^"\n]+?)"?\s*$', text, re.M)
    contacts = re.findall(r"\[A,\s*(\d+)\]", text)
    return {
        "sequence": seq.group(1) if seq else None,
        "smiles": smi.group(1) if smi else None,
        "msa": msa.group(1) if msa else None,
        "contacts": [int(c) for c in contacts],
        "has_affinity": "affinity:" in text and "binder: L" in text,
    }


def check(path):
    """Return a list of problems with one job file. Empty list means the job is safe to run."""
    bad = []
    d = parse(path)
    if not d["sequence"]:
        bad.append("no protein sequence")
    if not d["has_affinity"]:
        bad.append("no affinity property")
    if not d["smiles"]:
        bad.append("no SMILES")
    else:
        mol = Chem.MolFromSmiles(d["smiles"])
        if mol is None:
            bad.append("unparseable SMILES")
        else:
            n = mol.GetNumHeavyAtoms()
            total = Chem.AddHs(mol).GetNumAtoms()
            if n < 6:
                bad.append("ligand too small (%d heavy atoms)" % n)
            elif total > MAX_TOTAL_ATOMS:
                bad.append("over Boltz-2 affinity limit (%d atoms with H, max %d)"
                           % (total, MAX_TOTAL_ATOMS))
            if "." in d["smiles"]:
                bad.append("multi-component SMILES (salt/mixture)")
    if not d["msa"]:
        bad.append("no MSA (job would need the MSA server, i.e. internet)")
    elif not d["msa"].startswith(POD_MSA_PREFIX):
        bad.append("MSA path is not pod-side: " + d["msa"])
    elif not os.path.exists(os.path.join(MSA_DIR, os.path.basename(d["msa"]))):
        bad.append("MSA file missing locally: " + os.path.basename(d["msa"]))
    if d["sequence"]:
        out_of_range = [c for c in d["contacts"] if c < 1 or c > len(d["sequence"])]
        if out_of_range:
            bad.append("pocket contacts outside sequence: %s" % out_of_range[:5])
    return bad, d


def main(prune):
    files = sorted(f for f in os.listdir(YDIR) if f.endswith(".yaml"))
    problems, msas, seqs, ids = {}, collections.Counter(), collections.Counter(), collections.Counter()
    for f in files:
        bad, d = check(os.path.join(YDIR, f))
        ids[f[:-5]] += 1
        if d["msa"]:
            msas[d["msa"]] += 1
        if d["sequence"]:
            seqs[d["sequence"][:30] + "/%d" % len(d["sequence"])] += 1
        if bad:
            problems[f] = bad

    print("%d job files in %s" % (len(files), YDIR))
    real = [f for f in files if not f.startswith(("decoy_", "off_"))]
    print("  %d screen, %d decoy, %d off-target"
          % (len(real), sum(f.startswith("decoy_") for f in files), sum(f.startswith("off_") for f in files)))
    for label, ctr in (("MSA", msas), ("protein", seqs)):
        print("  %s variants: %d" % (label, len(ctr)))
        for k, v in ctr.most_common():
            print("    %-70s %d jobs" % (k, v))
    dupes = [k for k, v in ids.items() if v > 1]
    if dupes:
        print("  DUPLICATE job ids (results would overwrite):", dupes)

    if not problems:
        print("\nAll %d jobs valid. Safe to run." % len(files))
        return
    print("\n%d jobs with problems:" % len(problems))
    by_reason = collections.Counter()
    for f, bad in sorted(problems.items()):
        print("  %-28s %s" % (f, "; ".join(bad)))
        for b in bad:
            by_reason[re.sub(r"\(.*\)|:.*", "", b).strip()] += 1
    print("\n  by reason:")
    for r, n in by_reason.most_common():
        print("    %-45s %d" % (r, n))
    if prune:
        os.makedirs(RDIR, exist_ok=True)
        for f in problems:
            shutil.move(os.path.join(YDIR, f), os.path.join(RDIR, f))
        print("\nmoved %d failing jobs to %s; %d remain runnable"
              % (len(problems), RDIR, len(files) - len(problems)))
    else:
        print("\nre-run with --prune to move these out of the run directory")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--prune", action="store_true")
    main(ap.parse_args().prune)
