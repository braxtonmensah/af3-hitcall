"""PREREG_BRIDGE: score the three arms and apply the registered rules.

Usage:
    python score_bridge.py <dir-of-model-files>

Expects model files whose names contain the job name (e.g. TAF5L_TADA1_P, ..._BR, ..._CT), as
produced by AlphaFold Server downloads or Boltz-2 output. Works on .cif and .pdb.

The pre-registered rules, applied in this order and not negotiable at read time:

  G  (gate)      arm P must reproduce the original failure: AT MOST 4 of 20 pairs may show an A-B
                 interface. If more do, BR is reported but NOT interpreted.
  B1 (primary)   BR vs P, McNemar exact on discordant pairs. Supported needs BR - P >= 6 of 20 AND p < 0.05.
  B2 (specificity) BR vs CT, McNemar exact. Without this, the honest claim is only "a third chain
                 helps", never "co-dependency picks the bridge".
  B3 (reported)  mean change in the A-B contact count.

Interface present = >= 5 residue pairs with CB (CA for Gly) within 8 A between chain A and chain B,
in at least 3 of 5 samples. With a single model per job, the sample rule is reported as unmet and the
call is made on that one model, which is recorded as a deviation.
"""
import json
import math
import os
import re
import sys
from collections import defaultdict

import numpy as np

CONTACT_A = 8.0
MIN_PAIRS = 5
MIN_SAMPLES = 3


def parse(path):
    """-> {chain: {resnum: (x, y, z)}} using CB where present, CA otherwise (Gly and CA-only models)"""
    ca, cb = defaultdict(dict), defaultdict(dict)
    if path.lower().endswith(".cif"):
        hdr, cols = [], {}
        for line in open(path, errors="replace"):
            if line.startswith("_atom_site."):
                hdr.append(line.strip().split(".")[1])
                continue
            if hdr and line.startswith(("ATOM", "HETATM")):
                f = line.split()
                if not cols:
                    cols = {k: i for i, k in enumerate(hdr)}
                if len(f) <= max(cols.values()):
                    continue
                atom = f[cols["label_atom_id"]]
                if atom not in ("CA", "CB"):
                    continue
                c = f[cols.get("auth_asym_id", cols["label_asym_id"])]
                try:
                    n = int(f[cols.get("auth_seq_id", cols["label_seq_id"])])
                except ValueError:
                    continue
                xyz = (float(f[cols["Cartn_x"]]), float(f[cols["Cartn_y"]]), float(f[cols["Cartn_z"]]))
                (ca if atom == "CA" else cb)[c][n] = xyz
            elif hdr and line.startswith("#") and cols:
                break
    else:
        for line in open(path, errors="replace"):
            if line.startswith("ATOM"):
                atom = line[12:16].strip()
                if atom not in ("CA", "CB"):
                    continue
                c, n = line[21], int(line[22:26])
                xyz = (float(line[30:38]), float(line[38:46]), float(line[46:54]))
                (ca if atom == "CA" else cb)[c][n] = xyz
    out = {}
    for c in set(ca) | set(cb):
        out[c] = {n: cb[c].get(n, ca[c].get(n)) for n in set(ca[c]) | set(cb[c])}
        out[c] = {n: v for n, v in out[c].items() if v is not None}
    return out


def ab_contacts(chains):
    """A and B are the two LONGEST-ordered chains by file order; the bridge/control is the extra one.
    Chain identity comes from the job's own chain order (A, B, then C), which both engines preserve."""
    ids = sorted(chains)
    if len(ids) < 2:
        return None
    A, B = chains[ids[0]], chains[ids[1]]
    pa = np.array(list(A.values()))
    pb = np.array(list(B.values()))
    if len(pa) == 0 or len(pb) == 0:
        return None
    d = np.sqrt(((pa[:, None, :] - pb[None, :, :]) ** 2).sum(-1))
    return int((d < CONTACT_A).sum())


def mcnemar_exact(b, c):
    """two-sided exact McNemar on discordant counts b (BR only) and c (other only)"""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def main(d):
    jobs = defaultdict(dict)
    for f in sorted(os.listdir(d)):
        if not f.lower().endswith((".cif", ".pdb")):
            continue
        m = re.search(r"([A-Za-z0-9]+)_([A-Za-z0-9]+)_(P|BR|CT)\b", f, re.I)
        if not m:
            continue
        pair, arm = f"{m.group(1).upper()}-{m.group(2).upper()}", m.group(3).upper()
        ch = parse(os.path.join(d, f))
        n = ab_contacts(ch)
        if n is None:
            continue
        jobs[pair].setdefault(arm, []).append(n)

    rows, per_arm = [], {"P": 0, "BR": 0, "CT": 0}
    for pair, arms in sorted(jobs.items()):
        r = {"pair": pair}
        for arm in ("P", "BR", "CT"):
            vals = arms.get(arm, [])
            if not vals:
                r[arm] = None
                r[arm + "_n"] = 0
                continue
            hit = sum(1 for v in vals if v >= MIN_PAIRS)
            present = hit >= MIN_SAMPLES if len(vals) >= MIN_SAMPLES else (hit > 0)
            r[arm] = bool(present)
            r[arm + "_contacts"] = int(max(vals))
            r[arm + "_n"] = len(vals)
            per_arm[arm] += bool(present)
        rows.append(r)

    n_pairs = len(rows)
    res = {"n_pairs": n_pairs, "interface_present": per_arm,
           "single_model_deviation": any(r.get("P_n", 0) < MIN_SAMPLES for r in rows)}

    res["G_gate"] = {"P_present": per_arm["P"], "bar": 4,
                     "passes": per_arm["P"] <= 4,
                     "note": "arm P must reproduce the original AlphaFold failure"}

    def disc(a, b):
        bo = co = 0
        for r in rows:
            if r.get(a) is None or r.get(b) is None:
                continue
            if r[a] and not r[b]:
                bo += 1
            elif r[b] and not r[a]:
                co += 1
        return bo, co

    b, c = disc("BR", "P")
    res["B1_primary"] = {"BR_only": b, "P_only": c, "delta": per_arm["BR"] - per_arm["P"],
                         "mcnemar_p": round(mcnemar_exact(b, c), 5),
                         "supported": bool(per_arm["BR"] - per_arm["P"] >= 6 and mcnemar_exact(b, c) < 0.05)}
    b2, c2 = disc("BR", "CT")
    res["B2_specificity"] = {"BR_only": b2, "CT_only": c2,
                             "mcnemar_p": round(mcnemar_exact(b2, c2), 5),
                             "passes": bool(mcnemar_exact(b2, c2) < 0.05 and per_arm["BR"] > per_arm["CT"])}

    if not res["G_gate"]["passes"]:
        res["verdict"] = "NOT INTERPRETED: gate failed, the engine solves what AF2/FoldDock could not"
    elif res["B1_primary"]["supported"] and res["B2_specificity"]["passes"]:
        res["verdict"] = "SUPPORTED: co-dependency selects a rescuing subunit without prior knowledge"
    elif res["B1_primary"]["supported"]:
        res["verdict"] = "PARTIAL: a third chain helps, but specificity to co-dependency is NOT shown"
    else:
        res["verdict"] = "NOT SUPPORTED"

    print(json.dumps(res, indent=1))
    print()
    print(f"{'pair':>22s}  {'P':>5s} {'BR':>5s} {'CT':>5s}")
    for r in rows:
        f = lambda k: ("-" if r.get(k) is None else ("yes" if r[k] else "no"))   # noqa: E731
        print(f"{r['pair']:>22s}  {f('P'):>5s} {f('BR'):>5s} {f('CT'):>5s}")
    json.dump({"summary": res, "rows": rows}, open("results_bridge.json", "w"), indent=1)
    print("\nwrote results_bridge.json")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
