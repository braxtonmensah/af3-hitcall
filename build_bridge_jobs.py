"""PREREG_BRIDGE: build the 60 jobs (20 pairs x 3 arms) and pick the control third protein D by the
rule fixed in the pre-registration, not by choice.

D = among genes that are selectively essential by the CODEP definition and whose length is within 25%
of the bridge C's length, the one whose min(r(A,D), r(B,D)) is closest to zero FROM ABOVE, excluding
any gene sharing a CORUM complex with A, B or C. The length window widens in 10% steps if empty, and
that is reported per pair.

Writes Boltz-2 YAML for every arm. Run: py -3.11 build_bridge_jobs.py
"""
import csv
import json
import os

import numpy as np
import pandas as pd

D_DIR = r"C:\Users\bmens\NQ_local\af3-hitcall\depmap"
B_DIR = r"C:\Users\bmens\NQ_local\af3-hitcall\burke"
OUT = os.path.join("cleanroom", "bridge")
os.makedirs(OUT, exist_ok=True)

# ---- sequences ----
sp = list(csv.DictReader(open(os.path.join(D_DIR, "human_sp.tsv"), encoding="utf-8"), delimiter="\t"))
by_gene, by_acc = {}, {}
for r in sp:
    g, acc = r["Gene Names (primary)"], r["Entry"]
    rec = {"acc": acc, "gene": g, "len": int(r["Length"]), "seq": r["Sequence"]}
    by_acc[acc] = rec
    if g and (g not in by_gene or rec["len"] > by_gene[g]["len"]):
        by_gene[g] = rec

# ---- gene effect ----
GE = pd.read_csv(os.path.join(D_DIR, "CRISPRGeneEffect.csv"), index_col=0, low_memory=False)
GE.columns = [c.split(" (")[0] for c in GE.columns]
GE = GE.loc[:, ~GE.columns.duplicated()]
X = GE.to_numpy(np.float32)
SYM = {s: i for i, s in enumerate(GE.columns)}
GN = np.array(GE.columns)
sd = np.nanstd(X, axis=0)
ok = sd >= np.nanpercentile(sd, 25)


def stats(i):
    v = X[:, i]
    v = v[np.isfinite(v)]
    if len(v) < 300:
        return None
    return {"mean": float(v.mean()), "ndep": int((v < -0.6).sum()), "fdep": float((v < -0.6).mean())}


def selective(s):
    return bool(s and s["mean"] > -0.35 and s["ndep"] >= 15 and s["fdep"] <= 0.25)


def exact_r(i, j):
    a, b = X[:, i], X[:, j]
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 300:
        return None
    aa, bb = a[m] - a[m].mean(), b[m] - b[m].mean()
    d = np.sqrt((aa * aa).sum() * (bb * bb).sum())
    return None if d == 0 else float((aa * bb).sum() / d)


print("scoring selective genes ...", flush=True)
sel_idx = [i for i in range(X.shape[1]) if ok[i] and selective(stats(i))]
print(f"  {len(sel_idx)} selectively essential genes", flush=True)

# ---- CORUM co-membership, to exclude same-complex controls ----
s1 = pd.read_csv(os.path.join(B_DIR, "S1.csv"), low_memory=False)
corum_partners = {}
if "CORUM_ID_selection" in s1.columns:
    sub = s1[s1.CORUM_ID_selection.notna()]
    for a, b in zip(sub["Gen.id1"].astype(str), sub["Gen.id2"].astype(str)):
        corum_partners.setdefault(a, set()).add(b)
        corum_partners.setdefault(b, set()).add(a)

BR = pd.read_csv("codep_bridges.csv").head(20)
jobs, table = [], []
for t in BR.itertuples():
    a_rec = by_acc.get(t.id1) or by_gene.get(t.g1)
    b_rec = by_acc.get(t.id2) or by_gene.get(t.g2)
    c_rec = by_gene.get(t.bridge)
    if not (a_rec and b_rec and c_rec):
        print(f"  skip {t.g1}-{t.g2}: missing sequence")
        continue
    ia, ib = SYM[t.g1], SYM[t.g2]
    banned = {t.g1, t.g2, t.bridge}
    for g in (t.g1, t.g2, t.bridge):
        banned |= corum_partners.get(g, set())
    # control D: closest to zero from above, inside a widening length window
    best, window = None, 0.25
    while best is None and window <= 0.95:
        cands = []
        for i in sel_idx:
            g = GN[i]
            if g in banned or g not in by_gene:
                continue
            if abs(by_gene[g]["len"] - c_rec["len"]) / c_rec["len"] > window:
                continue
            ra, rb = exact_r(ia, int(i)), exact_r(ib, int(i))
            if ra is None or rb is None:
                continue
            m = min(ra, rb)
            if m > 0:
                cands.append((m, g))
        if cands:
            cands.sort()
            best = cands[0]
        else:
            window += 0.10
    if best is None:
        print(f"  skip {t.g1}-{t.g2}: no control found")
        continue
    d_rec = by_gene[best[1]]
    table.append({"pair": f"{t.g1}-{t.g2}", "r_pair": t.r_pair, "pDockQ": t.pDockQ,
                  "bridge": t.bridge, "bridge_min_r": t.bridge_min_r,
                  "control": best[1], "control_min_r": round(best[0], 4),
                  "control_len_window": round(window, 2),
                  "len_A": a_rec["len"], "len_B": b_rec["len"],
                  "len_C": c_rec["len"], "len_D": d_rec["len"]})
    for arm, chains in (("P", [a_rec, b_rec]),
                        ("BR", [a_rec, b_rec, c_rec]),
                        ("CT", [a_rec, b_rec, d_rec])):
        name = f"{t.g1}_{t.g2}_{arm}"
        y = ["version: 1", "sequences:"]
        for k, rec in enumerate(chains):
            y += ["  - protein:", f"      id: {chr(65 + k)}", f"      sequence: {rec['seq']}"]
        with open(os.path.join(OUT, name + ".yaml"), "w", newline="\n") as fh:
            fh.write("\n".join(y) + "\n")
        jobs.append({"name": name, "pair": f"{t.g1}-{t.g2}", "arm": arm,
                     "chains": [r["gene"] for r in chains],
                     "tokens": sum(r["len"] for r in chains)})

pd.DataFrame(table).to_csv("bridge_design.csv", index=False)
json.dump(jobs, open(os.path.join(OUT, "jobs.json"), "w"), indent=1)
tok = [j["tokens"] for j in jobs]
print(f"\nwrote {len(jobs)} jobs to {OUT}")
print(f"  tokens: median {int(np.median(tok))}, max {max(tok)}  (AF3 on an 80GB card tops out near 5120)")
print(f"  over 5120 tokens: {sum(1 for x in tok if x > 5120)} jobs")
print()
print(pd.DataFrame(table)[["pair", "bridge", "bridge_min_r", "control", "control_min_r", "len_C", "len_D"]]
      .to_string(index=False))
