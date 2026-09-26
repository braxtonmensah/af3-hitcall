"""Write the PREREG_MPN621 screen jobs: four arms over three receptors.

Reuses `build_gate`'s primitives (UniProt fetch with caching, YAML writer, the MSYS path guard)
rather than copying them, because the two screens must produce identically-shaped jobs or their
results are not comparable.

Arms, from PREREG_MPN621 and its Amendment 1:

  S     MPN621 (P75174), cleft pocket, NO metal     the question
  N     same receptor and pocket, matched decoys    what "high" means
  O1    M. pneumoniae RNase J (P75497), 1 Zn        paralogue selectivity, the arm that gates a buy
  O2    human CPSF73 (Q9UKF6), 1 Zn                 human off-target
  Z     MPN621 + 1 Zn, a 50-compound subset         metal sensitivity; built after S is scored

Why MPN621 alone carries no metal: its cleft contains no histidine at all (E73, D162, D163 are its
only candidate ligands), while RNase J's retains H373 and H377. MBL zinc sites are histidine-rich, so
the residue evidence says MPN621 has no canonical site and inventing one is the larger assumption.
Amendment 1 records this as a declared deviation from PREREG_VSCREEN Amendment 2's uniform rule, and
arm Z is the pre-registered check on whether it matters.

Pockets are fixed in the pre-registration and are NOT computed here, deliberately: they were chosen
geometrically from the coordinates (`cavity_residues.py`) and committed, so a later run cannot quietly
change them. The model's residue numbering was verified to be UniProt numbering for both Mycoplasma
chains, so these indices apply to the full-length sequences supplied to the engine with no offset.

Usage:
    python build_mpn621.py --selection sel.tsv --msa-prefix /workspace/mpn621/msa
    python build_mpn621.py --selection sel.tsv --msa-prefix ... --arm-z shortlist.csv
"""
import argparse
import collections
import csv
import datetime
import json
import os
import random
import sys

import build_gate as G

HERE = os.path.dirname(os.path.abspath(__file__))
MSA_DIR = os.path.join(HERE, "msa")

# Pocket residues fixed by PREREG_MPN621 and its Amendment 1. Do not edit without an amendment.
POCKETS = {
    "P75174": [15, 18, 37, 69, 71, 73, 74, 142, 162, 163, 201, 234, 329, 332, 334, 358, 359, 363,
               365, 387],
    "P75497": [49, 84, 85, 92, 151, 205, 206, 241, 266, 270, 308, 311, 313, 340, 343, 345, 373, 375,
               377, 401],
    # Arm O2's pocket is the real 6M8Q co-crystal site, resolved from coordinates at build time
    # because it is the one pocket here that comes from an experiment rather than a prediction.
    "Q9UKF6": None,
}

RECEPTORS = {
    "S":  {"acc": "P75174", "metals": [], "note": "MPN621, no metal: no histidine in the cleft"},
    "N":  {"acc": "P75174", "metals": [], "note": "same receptor and pocket as S"},
    "O1": {"acc": "P75497", "metals": [("ZN", 1)], "note": "RNase J paralogue, His373/His377 present"},
    "O2": {"acc": "Q9UKF6", "metals": [("ZN", 1)], "note": "human CPSF73, co-crystal pocket from 6M8Q"},
    "Z":  {"acc": "P75174", "metals": [("ZN", 1)], "note": "MPN621 WITH a zinc: Amendment 1 sensitivity"},
}
PREFIX = {"S": "", "N": "decoy_", "O1": "o1_", "O2": "o2_", "Z": "z_"}
# The validator reads arms from filename prefixes; "decoy_" is the one it treats as the null.
Z_RANDOM_SEED = 30


def cpsf73_pocket(n=20):
    """The 6M8Q JBG contact residues, mapped onto full-length Q9UKF6.

    Safe because the construct was verified to be a contiguous slice of Q9UKF6 starting at residue 1,
    so construct indices are UniProt indices. Verified, not assumed: the check is repeated here.
    """
    con, off = G.entity_seq("6M8Q", "1", with_offset=True)
    full = G.uniprot_seq("Q9UKF6")
    if not full.startswith(con[:40]) or full[:len(con)] != con:
        sys.exit("6M8Q's construct is no longer a prefix of Q9UKF6; the arm O2 pocket mapping in "
                 "PREREG_MPN621 Amendment 1 does not hold and must be re-derived.")
    pk = G.pocket_from_cif("6M8Q", "JBG", [("A", con)], offsets={"A": off})
    return [i for _, i in pk][:n]


def read_selection(path):
    rows = [r for r in csv.DictReader(open(path), delimiter="\t") if r.get("smiles")]
    if not rows:
        sys.exit("no rows in " + path)
    if "arm" not in rows[0]:
        sys.exit(path + " has no 'arm' column; produce it with libgen.py --select")
    return rows


def main(a):
    if ":" in a.msa_prefix or "\\" in a.msa_prefix:
        sys.exit("--msa-prefix looks like a Windows path: %r\nGit Bash rewrites POSIX paths; prefix "
                 "the command with MSYS_NO_PATHCONV=1 or use PowerShell." % a.msa_prefix)
    if not a.msa_prefix.startswith("/"):
        sys.exit("--msa-prefix must be absolute on the machine that runs the jobs")
    msa_prefix = a.msa_prefix.rstrip("/")

    rows = read_selection(a.selection)
    screen = [r for r in rows if r["arm"] == "screen"]
    decoys = [r for r in rows if r["arm"] == "decoy"]
    if not screen or not decoys:
        sys.exit("selection needs both a screen arm and a decoy arm")

    # Same refusal as build_screen_jobs: a molecule in two arms makes the null uninterpretable.
    seen = {}
    for r in rows:
        seen.setdefault(r["inchikey"], set()).add(r["arm"])
    bad = {k: v for k, v in seen.items() if len(v) > 1}
    if bad:
        print("REFUSING TO WRITE: %d molecules are in more than one arm." % len(bad))
        for k, v in list(bad.items())[:10]:
            print("   %s  %s" % (k, sorted(v)))
        sys.exit(1)

    pockets = dict(POCKETS)
    pockets["Q9UKF6"] = cpsf73_pocket()
    seqs, lens = {}, {}
    for arm, spec in RECEPTORS.items():
        acc = spec["acc"]
        if acc not in seqs:
            seqs[acc] = G.uniprot_seq(acc)
            lens[acc] = len(seqs[acc])
        pk = pockets[acc]
        outside = [p for p in pk if not (1 <= p <= lens[acc])]
        if outside:
            sys.exit("pocket residues outside %s (%d aa): %s" % (acc, lens[acc], outside))
        if not os.path.exists(os.path.join(MSA_DIR, acc + ".a3m")):
            print("  WARNING: no msa/%s.a3m yet; jobs will be written but cannot run offline" % acc)

    print("receptors:")
    for arm in ("S", "N", "O1", "O2", "Z"):
        spec = RECEPTORS[arm]
        acc = spec["acc"]
        print("  %-3s %-8s %4d aa  pocket %2d  metals %-14s %s"
              % (arm, acc, lens[acc], len(pockets[acc]), spec["metals"] or "none", spec["note"]))

    # Arm Z needs arm S's scores, which do not exist at first build. The 25 random members are fixed
    # now by committed seed so that half of arm Z cannot be chosen after seeing anything.
    z_random = random.Random(Z_RANDOM_SEED).sample(screen, min(25, len(screen)))
    z_top = []
    if a.arm_z:
        with open(a.arm_z) as f:
            ids = [r.get("id") or r.get("source_id") for r in csv.DictReader(f)]
        by_id = {r["source_id"]: r for r in screen}
        z_top = [by_id[i] for i in ids if i in by_id][:25]
        if len(z_top) < 25:
            print("  note: arm Z top list resolved %d of 25 from %s" % (len(z_top), a.arm_z))

    want = set(a.arms.upper().replace(",", " ").split()) if a.arms else {"S", "N", "O1", "O2"}
    plan = [(k, v) for k, v in (("S", screen), ("N", decoys), ("O1", screen), ("O2", screen))
            if k in want]
    if not plan:
        sys.exit("--arms selected nothing; known arms are S, N, O1, O2, Z")
    if ("O1" in want or "O2" in want) and not ({"S", "N"} <= want):
        # Staging, not a restriction: the selectivity arms answer a per-compound purchase question
        # and there is nothing to ask it about until M1 says the screen enriched at all. Building
        # them alongside S and N would spend half the budget on a question that a null M1 deletes.
        print("note: building a selectivity arm without S and N. That is only sensible if S and N")
        print("      are already scored; M1 has to enrich before O1 or O2 mean anything.")
    if a.arm_z or a.z_random_only:
        zrows = {r["inchikey"]: r for r in z_random + z_top}
        plan.append(("Z", list(zrows.values())))
    total = sum(len(v) for _, v in plan)
    print("\njobs: " + " | ".join("%s %d" % (k, len(v)) for k, v in plan) + "  = %d" % total)
    print("at 45 s/job that is %.1f GPU-hours; at 90 s, %.1f" % (total * 45 / 3600, total * 90 / 3600))
    if a.plan:
        print("\n--plan only, nothing written")
        return

    os.makedirs(a.out_dir, exist_ok=True)
    manifest = {"created": datetime.datetime.now().isoformat(timespec="seconds"),
                "prereg": "PREREG_MPN621.md + Amendment 1",
                "selection": os.path.basename(a.selection),
                "msa_prefix": msa_prefix, "z_random_seed": Z_RANDOM_SEED,
                "receptors": {k: dict(v, pocket=pockets[v["acc"]]) for k, v in RECEPTORS.items()},
                "jobs": {}}
    written = collections.Counter()
    for arm, rs in plan:
        spec = RECEPTORS[arm]
        acc = spec["acc"]
        pk = [("A", p) for p in pockets[acc]]
        msa = {"A": msa_prefix + "/" + acc + ".a3m"}
        for r in rs:
            name = PREFIX[arm] + r["source_id"]
            path = os.path.join(a.out_dir, name + ".yaml")
            if os.path.exists(path) and not a.force:
                sys.exit("refusing to overwrite %s (use --force)" % path)
            with open(path, "w", newline="\n") as f:
                f.write(G.job_yaml([("A", seqs[acc])], spec["metals"], r["smiles"], msa, pk))
            manifest["jobs"][name] = {"arm": arm, "receptor": acc, "inchikey": r["inchikey"]}
            written[arm] += 1
    with open(os.path.join(a.out_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    print("\nwrote %d jobs to %s" % (sum(written.values()), a.out_dir))
    for arm in ("S", "N", "O1", "O2", "Z"):
        if written[arm]:
            print("   %-3s %5d" % (arm, written[arm]))
    if not written["Z"]:
        print("\nArm Z is not built yet. It is pre-registered and required: rerun with --arm-z once")
        print("arm S is scored, passing the shortlist CSV. Without it the metal choice in Amendment 1")
        print("is untested and M2/M3 cannot be reported as unconditional.")
    print("\nvalidate before spending anything:")
    print("   YAML_DIR=%s py -3.11 validate_jobs.py" % a.out_dir)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selection", required=True)
    ap.add_argument("--msa-prefix", required=True)
    ap.add_argument("--out-dir", default=os.path.join(HERE, "mpn621_jobs"))
    ap.add_argument("--arm-z", help="shortlist CSV of arm S's top compounds, to build arm Z")
    ap.add_argument("--z-random-only", action="store_true",
                    help="build only arm Z's 25 pre-committed random members")
    ap.add_argument("--arms", help="comma-separated subset of S,N,O1,O2 (default all four). "
                    "Stage it: S,N first, and O1,O2 only if M1 enriches")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--force", action="store_true")
    main(ap.parse_args())
