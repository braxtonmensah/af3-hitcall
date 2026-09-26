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


IPTM_BAR = 0.5           # Amendment 1: the conventional confident-interface threshold, untuned
# Key spellings for the chain-pair ipTM matrix. AlphaFold Server writes chain_pair_iptm in
# *_summary_confidences_*.json; Boltz-2 writes pair_chains_iptm in confidence_*.json.
PAIR_KEYS = ("chain_pair_iptm", "pair_chains_iptm", "chain_pair_iptm_matrix")


def read_ab_iptm(path, arm=None):
    """Chain-pair ipTM(A,B) from a confidence file, or (None, reason).

    `arm` is the authority on how many chains the job had, because the confidence file is not: when
    the chain-pair matrix is missing there is nothing in it to count. Arm P is two chains by design
    and BR and CT are three, so passing the arm is what stops a three-chain job from silently
    falling back to its whole-complex value. Without it, a BR job whose matrix is absent was accepted
    as if it were a pair, which is the exact substitution this function exists to prevent.

    This is the quantity PREREG_BRIDGE Amendment 1 specifies, and for the three-chain arms it is NOT
    the top-level `iptm`. Whole-complex ipTM on a BR or CT job averages A-B, A-C and B-C, so a bridge
    that docks confidently to A while leaving A-B unchanged would move it, which is exactly the
    inference the amended criterion exists to avoid. RNAP3 showed the size of the gap in practice:
    whole-complex 0.87 while the pair of interest was 0.57.

    The top-level value is accepted ONLY when the job has two chains, where the two coincide. For a
    three-chain job with no chain-pair matrix the criterion is unevaluable and says so, rather than
    silently substituting a different number.
    """
    try:
        d = json.load(open(path, errors="replace"))
    except Exception as e:
        return None, "unreadable: %s" % e
    for k in PAIR_KEYS:
        m = d.get(k)
        if isinstance(m, list) and len(m) >= 2 and isinstance(m[0], list) and len(m[0]) >= 2:
            try:
                return float(m[0][1]), "chain_pair(%s)[0][1], %d chains" % (k, len(m))
            except (TypeError, ValueError):
                pass
    top = d.get("iptm")
    n_ch = None
    for k in PAIR_KEYS:
        if isinstance(d.get(k), list):
            n_ch = len(d[k])
    if top is None:
        return None, "no ipTM field and no chain-pair matrix"
    # Arm decides the chain count when the file cannot. P is two chains, BR and CT are three.
    expected = {"P": 2, "BR": 3, "CT": 3}.get((arm or "").upper())
    n_ch = n_ch if n_ch is not None else expected
    if n_ch is None:
        return None, ("no chain-pair matrix and no arm given, so the chain count is unknown and a "
                      "whole-complex ipTM cannot be accepted as the A-B pair")
    if n_ch > 2:
        return None, ("only whole-complex ipTM for a %d-chain job; the amended criterion needs the "
                      "A-B pair and these are not the same number" % n_ch)
    return float(top), "top-level iptm (2-chain job, equals the A-B pair)"


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
    iptm = defaultdict(dict)
    for f in sorted(os.listdir(d)):
        if not f.lower().endswith((".cif", ".pdb")):
            continue
        # NOT \b after the arm token: in "fold_taf5l_tada1_p_model_0.cif" the next character is "_",
        # which is a word character, so \b never matches and every file is silently skipped.
        m = re.search(r"([A-Za-z0-9]+)_([A-Za-z0-9]+)_(P|BR|CT)(?=_model|_|\.|$)", f, re.I)
        if not m:
            continue
        pair, arm = f"{m.group(1).upper()}-{m.group(2).upper()}", m.group(3).upper()
        ch = parse(os.path.join(d, f))
        n = ab_contacts(ch)
        if n is None:
            continue
        jobs[pair].setdefault(arm, []).append(n)

    # The amended criterion (Amendment 1) reads chain-pair ipTM from the engine's confidence files,
    # which are separate from the coordinate files scanned above. Matched on the same job token.
    iptm_notes = {}
    for f in sorted(os.listdir(d)):
        if not f.lower().endswith(".json"):
            continue
        if "confidence" not in f.lower():
            continue
        m = re.search(r"([A-Za-z0-9]+)_([A-Za-z0-9]+)_(P|BR|CT)(?=_model|_|\.|$)", f, re.I)
        if not m:
            continue
        pair, arm = f"{m.group(1).upper()}-{m.group(2).upper()}", m.group(3).upper()
        v, why = read_ab_iptm(os.path.join(d, f), arm)
        iptm_notes.setdefault((pair, arm), set()).add(why)
        if v is not None:
            iptm[pair].setdefault(arm, []).append(v)

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

    # ---------------- amended criterion (Amendment 1), reported BESIDE the primary
    amended_rows, amended_arm = [], {"P": 0, "BR": 0, "CT": 0}
    for pair in sorted(set(jobs) | set(iptm)):
        r = {"pair": pair}
        for arm in ("P", "BR", "CT"):
            vals = iptm.get(pair, {}).get(arm, [])
            if not vals:
                r[arm] = None
                r[arm + "_n"] = 0
                continue
            hit = sum(1 for v in vals if v >= IPTM_BAR)
            present = hit >= MIN_SAMPLES if len(vals) >= MIN_SAMPLES else (hit > 0)
            r[arm] = bool(present)
            r[arm + "_iptm_max"] = round(max(vals), 4)
            r[arm + "_n"] = len(vals)
            amended_arm[arm] += bool(present)
        amended_rows.append(r)

    def disc_rows(rws, a, b):
        bo = co = 0
        for r in rws:
            if r.get(a) is None or r.get(b) is None:
                continue
            if r[a] and not r[b]:
                bo += 1
            elif r[b] and not r[a]:
                co += 1
        return bo, co

    have_iptm = any(v for pa in iptm.values() for v in pa.values())
    if not have_iptm:
        res["amended"] = {
            "status": "NOT EVALUATED: no chain-pair ipTM found in this directory.",
            "needs": "the engine's *confidence*.json files alongside the coordinates",
            "notes": sorted({w for ws in iptm_notes.values() for w in ws}) or
                     ["no confidence files matched a job name"],
            "why_it_matters": ("Amendment 1 made the ipTM rule the one a claim may rest on. The "
                               "registered contact rule below is reported first and is expected to "
                               "fail the gate, so a run scored WITHOUT the amended criterion reports "
                               "the opposite gate verdict from the one the amendment established.")}
    else:
        ab, ac = disc_rows(amended_rows, "BR", "P")
        ab2, ac2 = disc_rows(amended_rows, "BR", "CT")
        res["amended"] = {
            "criterion": "chain-pair ipTM(A,B) >= %.1f in >= %d of 5 samples" % (IPTM_BAR, MIN_SAMPLES),
            "interface_present": amended_arm,
            "sources": sorted({w for ws in iptm_notes.values() for w in ws}),
            "G_prime": {"P_present": amended_arm["P"], "bar": 4,
                        "passes": amended_arm["P"] <= 4},
            "B1_prime": {"BR_only": ab, "P_only": ac,
                         "delta": amended_arm["BR"] - amended_arm["P"],
                         "mcnemar_p": round(mcnemar_exact(ab, ac), 5),
                         "supported": bool(amended_arm["BR"] - amended_arm["P"] >= 6
                                           and mcnemar_exact(ab, ac) < 0.05)},
            "B2_prime": {"BR_only": ab2, "CT_only": ac2,
                         "mcnemar_p": round(mcnemar_exact(ab2, ac2), 5),
                         "passes": bool(mcnemar_exact(ab2, ac2) < 0.05
                                        and amended_arm["BR"] > amended_arm["CT"])},
            "rows": amended_rows}
        a = res["amended"]
        a["claim_allowed"] = bool(a["G_prime"]["passes"] and a["B1_prime"]["supported"]
                                  and a["B2_prime"]["passes"])
        a["disclosure"] = ("Any claim resting on this rests on an AMENDED criterion, recorded "
                           "2026-09-25 20:40 before the outcome data existed. Quote that date and "
                           "Amendment 1's disclosure alongside it.")
        # The disagreement is itself the result, per the amendment.
        res["primary_vs_amended_disagree"] = bool(
            res["G_gate"]["passes"] != a["G_prime"]["passes"])

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
