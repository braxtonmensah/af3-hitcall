"""Validate the virtual-screen YAMLs before paying for GPU time.

Every failure caught here is a job that would otherwise crash mid-run on a rented pod. Checks:
  - the YAML parses and has the fields Boltz-2 needs (protein, ligand, affinity property)
  - the SMILES is parseable by RDKit and sane in size (Boltz-2's affinity head was trained on
    drug-like ligands; a 200-heavy-atom peptide is not a screening hit, it is a crash risk)
  - the MSA path resolves to a readable file (here or in msa/) and is identical across jobs
  - pocket contacts are 1-based positions inside the protein sequence
  - job ids are unique, so no result silently overwrites another
  - the same MOLECULE does not appear in both the screen arm and the decoy arm. Unique job ids do
    not give you this: ChEMBL ships the same structure under several ids as different salt forms,
    and after desalting they are one molecule. A compound sitting in both arms caps its own null,
    because it can never score above the best decoy when it *is* the best decoy.

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
# The job directory is "vscreen_yaml" in the repo but the Quartz bundle ships it as "yaml"
# (see cleanroom/quartz/PUSH.md, "Rebuilding the bundle"). Accept either, or an explicit override,
# so the validator can be run in the place where the compute is actually spent.
YDIR = next((d for d in (os.environ.get("YAML_DIR"), os.path.join(HERE, "vscreen_yaml"),
                         os.path.join(HERE, "yaml")) if d and os.path.isdir(d)),
            os.path.join(HERE, "vscreen_yaml"))
RDIR = YDIR.rstrip("/\\") + "_rejected"
MSA_DIR = os.path.join(HERE, "msa")
POD_MSA_PREFIX = os.environ.get("POD_MSA_PREFIX", "")  # set it only when jobs must target a remote layout
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
    # What actually kills a job is an MSA the compute node cannot read, not a path that fails to
    # match one particular host's layout. The old check hardcoded the RunPod prefix, so every job
    # failed when validated on Quartz and --prune would have emptied the run directory. Resolve the
    # path instead: absolute and readable from here, or present in the local msa/ directory.
    elif not os.path.isfile(d["msa"]):
        # Do NOT fall back to checking the basename against msa/. That masks exactly the failure this
        # is here to catch: a path that is subtly wrong (MSYS rewriting /N/u/... to N:/u/..., a stray
        # CR, the wrong home) but whose filename happens to exist locally. Run this on the machine
        # that will run the jobs and the resolve test is the whole test.
        if os.path.isfile(os.path.join(MSA_DIR, os.path.basename(d["msa"]))):
            bad.append("MSA path does not resolve, though msa/%s exists: %s"
                       % (os.path.basename(d["msa"]), d["msa"]))
        else:
            bad.append("MSA file missing: " + d["msa"])
    elif POD_MSA_PREFIX and not d["msa"].startswith(POD_MSA_PREFIX):
        bad.append("MSA path is not pod-side: " + d["msa"])
    if d["sequence"]:
        out_of_range = [c for c in d["contacts"] if c < 1 or c > len(d["sequence"])]
        if out_of_range:
            bad.append("pocket contacts outside sequence: %s" % out_of_range[:5])
    return bad, d


def arm_of(name):
    """Which arm a job belongs to, from the filename conventions the builders write.

    build_gate.py uses its own prefixes (gate_A_, gate_B_, gate_neg_, gnull_), and leaving them out
    meant the gate's 250 jobs all counted as "screen": the cross-arm duplicate check silently did
    not apply to the gate at all, which is the one place a molecule appearing in both the scored arm
    and its null would be hardest to notice.
    """
    if name.startswith("gnull_"):
        return "decoy"
    if name.startswith("gate_neg_"):
        return "negative"
    if name.startswith("gate_"):
        return "positive"
    if name.startswith("decoy_"):
        return "decoy"
    if name.startswith("off_"):
        return "off"
    if name.startswith("pos_"):
        return "positive"
    return "screen"


def cross_arm_report(by_key):
    """Report molecules that appear in more than one arm.

    screen <-> off is by design: the off-target arm is deliberately the same compounds run against
    the selectivity protein. Every other pairing is a defect, and screen <-> decoy is the one that
    silently destroys the result rather than just wasting money.
    """
    fatal, waste = [], []
    for key, jobs in by_key.items():
        if len(jobs) < 2:
            continue
        arms = {arm_of(j) for j in jobs}
        same_arm = collections.Counter(arm_of(j) for j in jobs)
        for arm, n in same_arm.items():
            if n > 1:
                waste.append((arm, sorted(j for j in jobs if arm_of(j) == arm)))
        if "decoy" in arms and ("screen" in arms or "positive" in arms or "negative" in arms):
            fatal.append(sorted(jobs))
        elif "positive" in arms and "screen" in arms:
            fatal.append(sorted(jobs))
    return fatal, waste


def main(prune):
    files = sorted(f for f in os.listdir(YDIR) if f.endswith(".yaml"))
    problems, msas, seqs, ids = {}, collections.Counter(), collections.Counter(), collections.Counter()
    by_key = collections.defaultdict(list)
    for f in files:
        bad, d = check(os.path.join(YDIR, f))
        ids[f[:-5]] += 1
        if d["msa"]:
            msas[d["msa"]] += 1
        if d["sequence"]:
            seqs[d["sequence"][:30] + "/%d" % len(d["sequence"])] += 1
        if d["smiles"]:
            mol = Chem.MolFromSmiles(d["smiles"])
            if mol is not None:
                # Key on the protein too. The same ligand against two different proteins is two
                # different jobs; only a collision on the same protein is a duplicate.
                try:
                    prot = (d["sequence"] or "")[:40]
                    by_key[(Chem.MolToInchiKey(mol), prot)].append(f[:-5])
                except Exception:
                    pass
        if bad:
            problems[f] = bad

    print("%d job files in %s" % (len(files), YDIR))
    arms = collections.Counter(arm_of(f[:-5]) for f in files)
    print("  " + ", ".join("%d %s" % (v, k) for k, v in sorted(arms.items())))
    for label, ctr in (("MSA", msas), ("protein", seqs)):
        print("  %s variants: %d" % (label, len(ctr)))
        for k, v in ctr.most_common():
            print("    %-70s %d jobs" % (k, v))

    # Several MSA *files* is normal: one per protein, so a two-protein run has two. Several MSA
    # *directories* is not, and it is not cosmetic. It means the arms were written at different
    # times with different --msa-prefix values, so no single machine can resolve them all and
    # whichever arm points at the other host's layout dies at run time, after the setup is paid
    # for. Counted as a defect rather than printed as neutral information.
    prefixes = collections.Counter()
    for m, v in msas.items():
        prefixes[os.path.dirname(m)] += v
    mixed_msa = len(prefixes) > 1
    if mixed_msa:
        print("\n  FATAL: jobs point at %d different MSA directories. One machine cannot resolve"
              % len(prefixes))
        print("  all of them, so whichever arm names the other host's layout will fail at run time.")
        print("  Rewrite the whole set with one --msa-prefix before spending any GPU time.")
        for p, v in prefixes.most_common():
            print("    %-62s %d jobs" % (p, v))
    dupes = [k for k, v in ids.items() if v > 1]
    if dupes:
        print("  DUPLICATE job ids (results would overwrite):", dupes)

    fatal, waste = cross_arm_report(by_key)
    if waste:
        n = sum(len(j) - 1 for _, j in waste)
        print("\n  %d jobs are a repeat of a molecule already in the same arm (paid twice for one answer):" % n)
        for arm, jobs in sorted(waste)[:20]:
            print("    %-9s %s" % (arm, " = ".join(jobs)))
        if len(waste) > 20:
            print("    ... and %d more" % (len(waste) - 20))
    if fatal:
        print("\n  FATAL: %d molecules appear in the decoy null AND in a scored arm." % len(fatal))
        print("  Each one caps its own null: it cannot score above the best decoy when it is the")
        print("  best decoy, and it caps every compound below it too. Re-draw the decoy set with")
        print("  libgen.py --select, which deduplicates on InChIKey after desalting.")
        for jobs in sorted(fatal):
            print("    " + " = ".join(jobs))

    if not problems and not fatal and not mixed_msa:
        print("\nAll %d jobs valid. Safe to run." % len(files))
        return
    if not problems:
        print("\nPer-job checks all pass, but the set as a whole is not safe to run. See above.")
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
