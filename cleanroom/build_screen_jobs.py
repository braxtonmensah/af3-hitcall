"""Write Boltz-2 job files for the four screen arms from one selection table.

This replaces `vscreen.py --write`, which is kept for reference but should not be used again. Its
design is the cause of the defects found in commit b3bfd15: it slices one library list into arms
(`lib[:limit]` for the screen, `lib[limit:]` for decoys) and it is called once per arm, so

  - the arms are defined by position in a file rather than by a recorded decision, and the same
    molecule under two ChEMBL ids lands in both the screen and the null,
  - each call takes its own --msa-prefix, so arms written on different days point at different
    machines and one of them dies at run time.

Here the arm membership is read from a selection table produced by `libgen.py --select`, which
deduplicates on InChIKey after desalting, and every arm is written in a single invocation with a
single MSA prefix. A manifest records exactly what was written.

Arms, and the filename prefix each gets so the scorer and the validator can tell them apart:

  screen     (no prefix)  ligand vs the target, steered to the PPI interface
  decoy_     property-matched null vs the same target and the same pocket
  pos_       positive controls vs whichever protein POSITIVE_CONTROLS.md specifies
  off_       the screen compounds vs the human off-target, no pocket constraint

Usage:
    python build_screen_jobs.py --selection selection_v1.tsv --msa-prefix /workspace/screen/msa
    python build_screen_jobs.py --selection selection_v1.tsv --positives positives.tsv \
        --msa-prefix /N/u/bsmensah/Quartz/af3screen/msa --out-dir jobs_v1
"""
import argparse
import collections
import csv
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MSA_DIR = os.path.join(HERE, "msa")
IFACE_JSON = os.path.join(HERE, "..", "rnasej", "results_interface.json")

TARGET_ACC = "P75497"      # RNase J, the interface-bearing subunit
OFFTARGET_ACC = "Q9UKF6"   # human CPSF73, the selectivity control
MAX_POCKET_CONTACTS = 20  # engine-side cap; see require_pocket for why it is not a silent slice

PREFIX = {"screen": "", "decoy": "decoy_", "positive": "pos_", "off": "off_"}


def seq(acc, cache=os.path.join(HERE, "seqs")):
    """UniProt sequence, cached on disk so a rebuild needs no network."""
    os.makedirs(cache, exist_ok=True)
    p = os.path.join(cache, acc + ".fasta")
    if not os.path.exists(p):
        import requests
        t = requests.get("https://rest.uniprot.org/uniprotkb/" + acc + ".fasta", timeout=60).text
        if not t.startswith(">"):
            sys.exit("UniProt returned no FASTA for " + acc)
        with open(p, "w", newline="\n") as f:
            f.write(t)
    return "".join(open(p).read().split("\n")[1:]).replace("\n", "").strip()


def pocket_residues(chain="RNaseJ"):
    """Interface residues on the target, from the predicted heterotetramer.

    Steering to the interface rather than the active site is deliberate: the interface is about 25%
    identical to human CPSF73 while the active site keeps 3 of its 4 catalytic residues, so a
    catalytic-site hit would be the least selective thing we could find.

    **This returns all of them and does not truncate.** vscreen.py wrote `pocket[:20]`, which on
    this interface keeps residues 25-357 and discards 358-569 in their entirety, because the
    ordering is by residue number and has nothing to do with geometry. Measured independently, the
    kept 20 sit a median 15 A from the catalytic site and the dropped 45 sit at 33 A, so the
    truncation quietly aimed the constraint at the catalytic-proximal half, which is the least
    selective part of the interface. Truncation is the caller's decision and it has to be
    geometric; see require_pocket below.
    """
    if not os.path.exists(IFACE_JSON):
        sys.exit("no interface definition at " + IFACE_JSON)
    d = json.load(open(IFACE_JSON))
    key = {"RNaseJ": "RNaseJ", "MPN621": "MPN621"}.get(chain, chain)
    resl = d["interface_residues"].get(key)
    if resl is None:
        sys.exit("no interface residues for %r in %s; available: %s"
                 % (chain, IFACE_JSON, sorted(d["interface_residues"])))
    out = []
    for r in resl:
        n = "".join(c for c in r if c.isdigit())
        if n:
            out.append(int(n))
    return sorted(set(out))


def require_pocket(pocket, limit):
    """Return `limit` pocket contacts, or refuse.

    There is no defensible way to pick 20 of 65 interface residues from residue numbers alone, and
    doing it silently is how the constraint ended up pointed at the wrong half of the interface. A
    geometric selection needs coordinates, which this script does not have: the interface JSON
    carries residue identities only (`human_extract.parse` drops coordinates, see STATE.md). So the
    honest behaviour is to fail and say what is needed.
    """
    if len(pocket) <= limit:
        return pocket
    sys.exit(
        "%d interface residues but the constraint takes at most %d, and this script cannot choose\n"
        "between them: the interface JSON has residue identities, not coordinates, so any subset it\n"
        "picked would be an artefact of residue numbering. That is the defect that aimed the old\n"
        "screen at the catalytic-proximal half of the interface.\n\n"
        "Supply a geometric selection instead, via --pocket-residues with a comma-separated list\n"
        "chosen from the model coordinates (for example the residues lining the target cavity), or\n"
        "raise --max-contacts if the engine will accept all %d."
        % (len(pocket), limit, len(pocket)))


def read_selection(path):
    rows = []
    with open(path) as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if not r.get("smiles"):
                continue
            rows.append(r)
    if not rows:
        sys.exit("no rows in " + path)
    if "arm" not in rows[0]:
        sys.exit(path + " has no 'arm' column; produce it with libgen.py --select")
    return rows


def yaml_for(prot_seq, smiles, msa_path, pocket):
    y = ["version: 1", "sequences:",
         "  - protein:", "      id: A", "      sequence: " + prot_seq]
    if msa_path:
        y.append('      msa: "' + msa_path + '"')
    y += ["  - ligand:", "      id: L", "      smiles: '" + smiles + "'",
          "properties:", "  - affinity:", "      binder: L"]
    if pocket:
        contacts = ", ".join("[A, %d]" % p for p in pocket)
        y += ["constraints:", "  - pocket:", "      binder: L", "      contacts: [" + contacts + "]"]
    return "\n".join(y) + "\n"


def main(a):
    rows = read_selection(a.selection)
    positives = read_selection(a.positives) if a.positives else []
    for p in positives:
        p["arm"] = "positive"

    # Refuse to write an arm layout that cannot give a clean answer. This is the defect that capped
    # the null last time, so it is checked before any file is created rather than after.
    seen = {}
    for r in rows + positives:
        seen.setdefault(r["inchikey"], set()).add(r["arm"])
    bad = {k: v for k, v in seen.items() if len(v) > 1}
    if bad:
        print("REFUSING TO WRITE: %d molecules are in more than one arm of the selection." % len(bad))
        for k, v in list(bad.items())[:10]:
            print("   %s  %s" % (k, sorted(v)))
        sys.exit(1)

    target = seq(TARGET_ACC)
    if a.pocket_residues:
        pocket = sorted({int(x) for x in a.pocket_residues.replace(",", " ").split()})
        print("pocket: %d residues supplied on the command line" % len(pocket))
    else:
        pocket = require_pocket(pocket_residues(a.pocket_chain), a.max_contacts)
    out_of_range = [p for p in pocket if p < 1 or p > len(target)]
    if out_of_range:
        sys.exit("pocket residues outside the target sequence: %s" % out_of_range[:5])

    msa_prefix = a.msa_prefix.rstrip("/")
    # Git Bash on Windows rewrites an argument that looks like a POSIX absolute path into a Windows
    # one: --msa-prefix /workspace/screen/msa arrives as C:/Program Files/Git/workspace/screen/msa.
    # It is silent, and the result is 1,200 job files carrying a path no compute node has. Caught
    # here because the failure otherwise surfaces on the pod after the setup is paid for.
    # Fix: MSYS_NO_PATHCONV=1 before the command, or run it from PowerShell.
    if ":" in msa_prefix or "\\" in msa_prefix:
        sys.exit("--msa-prefix looks like a Windows path: %r\n"
                 "The jobs run on Linux, so this must be a POSIX absolute path. If you are in Git\n"
                 "Bash, it rewrote the argument; prefix the command with MSYS_NO_PATHCONV=1 or run\n"
                 "it from PowerShell." % msa_prefix)
    if not msa_prefix.startswith("/"):
        sys.exit("--msa-prefix must be absolute on the machine that runs the jobs: %r" % msa_prefix)
    os.makedirs(a.out_dir, exist_ok=True)
    written = collections.Counter()
    manifest = {"created": datetime.datetime.now().isoformat(timespec="seconds"),
                "selection": os.path.basename(a.selection),
                "positives": os.path.basename(a.positives) if a.positives else None,
                "msa_prefix": msa_prefix,
                "target": TARGET_ACC, "offtarget": OFFTARGET_ACC,
                "pocket_residues": pocket,
                "pocket_chain": a.pocket_chain,
                "jobs": {}}

    def write(arm, cid, prot_acc, prot_seq, smiles, use_pocket):
        name = PREFIX[arm] + cid
        path = os.path.join(a.out_dir, name + ".yaml")
        if os.path.exists(path) and not a.force:
            sys.exit("refusing to overwrite %s (use --force)" % path)
        msa = msa_prefix + "/" + prot_acc + ".a3m" if os.path.exists(
            os.path.join(MSA_DIR, prot_acc + ".a3m")) else None
        if msa is None:
            sys.exit("no MSA in msa/ for %s. Run fetch_msa.py first; without it every job calls "
                     "the MSA server and compute nodes have no internet." % prot_acc)
        # newline="\n" is load-bearing: these run on Linux, and Windows text mode leaves a carriage
        # return inside the quoted msa: path, which reports a present file as missing.
        with open(path, "w", newline="\n") as f:
            f.write(yaml_for(prot_seq, smiles, msa, pocket if use_pocket else None))
        written[arm] += 1
        manifest["jobs"][name] = {"arm": arm, "protein": prot_acc, "inchikey": cid}

    for r in rows:
        arm = r["arm"]
        if arm not in ("screen", "decoy"):
            sys.exit("unexpected arm %r in selection" % arm)
        write(arm, r["source_id"], TARGET_ACC, target, r["smiles"], use_pocket=True)

    for r in positives:
        write("positive", r["source_id"], TARGET_ACC, target, r["smiles"], use_pocket=True)

    if a.offtarget:
        off = seq(OFFTARGET_ACC)
        for r in rows:
            if r["arm"] != "screen":
                continue
            # No pocket constraint on the off-target: the point is to ask whether the compound binds
            # the human protein anywhere, not whether it binds one chosen spot on it. Constraining
            # it would understate the liability, which is the wrong direction for a safety check.
            write("off", r["source_id"], OFFTARGET_ACC, off, r["smiles"], use_pocket=False)

    mpath = os.path.join(a.out_dir, "manifest.json")
    with open(mpath, "w") as f:
        json.dump(manifest, f, indent=1)

    total = sum(written.values())
    print("wrote %d jobs to %s" % (total, a.out_dir))
    for arm in ("screen", "decoy", "positive", "off"):
        if written[arm]:
            print("   %-9s %5d" % (arm, written[arm]))
    print("   manifest -> " + mpath)
    if not written["positive"]:
        print("\nNO POSITIVE-CONTROL ARM. PREREG_VSCREEN's gate G1 cannot be evaluated without it,")
        print("and without G1 the screen arms are reported but not interpreted. Pass --positives.")
    est = total * 45 / 3600.0
    print("\nestimated %0.1f GPU-hours at 45 s per job (repo figure is 30-60 s)" % est)
    print("run cleanroom/validate_jobs.py with YAML_DIR=%s before spending any of it" % a.out_dir)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selection", required=True, help="TSV from libgen.py --select")
    ap.add_argument("--positives", help="TSV of positive controls, same columns, arm ignored")
    ap.add_argument("--msa-prefix", required=True,
                    help="directory holding the .a3m files ON THE MACHINE THAT WILL RUN THE JOBS")
    ap.add_argument("--out-dir", default=os.path.join(HERE, "jobs"))
    ap.add_argument("--offtarget", action="store_true", default=True)
    ap.add_argument("--no-offtarget", dest="offtarget", action="store_false")
    ap.add_argument("--pocket-residues",
                    help="explicit, geometrically chosen pocket residues (comma or space separated)")
    ap.add_argument("--pocket-chain", default="RNaseJ",
                    help="which side of the interface to steer to, as keyed in results_interface.json")
    ap.add_argument("--max-contacts", type=int, default=MAX_POCKET_CONTACTS)
    ap.add_argument("--force", action="store_true", help="overwrite existing job files")
    main(ap.parse_args())
