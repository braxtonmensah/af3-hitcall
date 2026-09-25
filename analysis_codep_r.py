"""PREREG_CODEP_R: does CODEP replicate in RNAi (DEMETER2), and does the CORUM split hold when it is
pre-registered rather than post hoc? Committed pre-registration: PREREG_CODEP_R.md (commit a79d1e8)."""
import csv
import json
import os

import numpy as np
import pandas as pd

D = r"C:\Users\bmens\NQ_local\af3-hitcall\depmap"
B = r"C:\Users\bmens\NQ_local\af3-hitcall\burke"
PARALOG_ID = 0.30
rng = np.random.default_rng(31)

print("loading DEMETER2 ...", flush=True)
R = pd.read_csv(os.path.join(D, "D2_combined_gene_dep_scores.csv"), index_col=0, low_memory=False)
R.index = [str(i).split(" (")[0] for i in R.index]
R = R[~R.index.duplicated()]
X = R.to_numpy(dtype=np.float32).T                      # rows = cell lines, cols = genes
SYM = {s: i for i, s in enumerate(R.index)}
print(f"  {X.shape[0]} cell lines x {X.shape[1]} genes", flush=True)

MIN_LINES = 300 if X.shape[0] >= 300 else 100
DEVIATION = None if MIN_LINES == 300 else f"line minimum lowered to {MIN_LINES}: panel has only {X.shape[0]} lines"
if DEVIATION:
    print("  DEVIATION:", DEVIATION, flush=True)

sd = np.nanstd(X, axis=0)
sd_floor = np.nanpercentile(sd, 25)
ok_var = sd >= sd_floor
print(f"  variance floor {sd_floor:.4f}: {ok_var.sum()} of {len(sd)} genes kept", flush=True)

# ---------------- pairs ----------------
s1 = pd.read_csv(os.path.join(B, "S1.csv"), low_memory=False)
s1 = s1[s1.id1 != s1.id2].copy()
if "homodimers" in s1.columns:
    s1 = s1[~s1.homodimers.astype(str).str.lower().isin(["true", "1", "yes"])].copy()
s1["key"] = ["_".join(sorted([str(a), str(b)])) for a, b in zip(s1.id1, s1.id2)]
s1 = s1.drop_duplicates("key")
s1["g1"] = s1["Gen.id1"].astype(str)
s1["g2"] = s1["Gen.id2"].astype(str)
s1["prec"] = s1.int3D_model_structure.fillna(0).astype(int) == 1
groups = {"T": s1[(s1.pDockQ > 0.23) & (~s1.prec)],
          "L": s1[(s1.pDockQ < 0.10) & (~s1.prec)],
          "P": s1[(s1.pDockQ > 0.23) & (s1.prec)]}

# ---------------- real CORUM pair set ----------------
corum_pair = set()
with open(os.path.join(D, "corum_humanComplexes.txt"), encoding="utf-8", errors="replace") as fh:
    for row in csv.DictReader(fh, delimiter="\t"):
        gs = sorted({g.strip() for g in str(row.get("subunits_gene_name", "")).split(";") if g.strip()})
        for i in range(len(gs)):
            for j in range(i + 1, len(gs)):
                corum_pair.add((gs[i], gs[j]))
print(f"  CORUM annotated gene pairs: {len(corum_pair)}", flush=True)

# ---------------- paralog filter ----------------
seqs = json.load(open(os.path.join(B, "uniprot_seqs.json"))) if os.path.exists(os.path.join(B, "uniprot_seqs.json")) else {}
try:
    from Bio import Align
    aligner = Align.PairwiseAligner(mode="global", open_gap_score=-11, extend_gap_score=-1,
                                    substitution_matrix=Align.substitution_matrices.load("BLOSUM62"))
    HAVE = True
except Exception:                                        # noqa: BLE001
    HAVE = False
_ic = {}


def identity(a, b):
    sa, sb = seqs.get(a), seqs.get(b)
    if not sa or not sb or not HAVE:
        return None
    k = (a, b) if a < b else (b, a)
    if k in _ic:
        return _ic[k]
    if max(len(sa), len(sb)) > 2000:
        sa, sb = sa[:2000], sb[:2000]
    try:
        aln = aligner.align(sa, sb)[0]
        v = sum(1 for x, y in zip(aln[0], aln[1]) if x == y and x != "-") / max(len(sa), len(sb))
    except Exception:                                    # noqa: BLE001
        v = None
    _ic[k] = v
    return v


def pair_r(i, j):
    a, b = X[:, i], X[:, j]
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < MIN_LINES:
        return None
    aa, bb = a[m] - a[m].mean(), b[m] - b[m].mean()
    d = np.sqrt((aa * aa).sum() * (bb * bb).sum())
    return None if d == 0 else float((aa * bb).sum() / d)


def build(df, label):
    rows, ds, dv, dn, dp = [], 0, 0, 0, 0
    for t in df.itertuples():
        g1, g2 = t.g1, t.g2
        if g1 not in SYM or g2 not in SYM or g1 == g2:
            ds += 1
            continue
        i, j = SYM[g1], SYM[g2]
        if not (ok_var[i] and ok_var[j]):
            dv += 1
            continue
        pid = identity(t.id1, t.id2)
        if pid is not None and pid >= PARALOG_ID:
            dp += 1
            continue
        r = pair_r(i, j)
        if r is None:
            dn += 1
            continue
        k = (g1, g2) if g1 < g2 else (g2, g1)
        rows.append({"g1": g1, "g2": g2, "r": r, "corum": k in corum_pair,
                     "m1": float(np.nanmean(X[:, i])), "m2": float(np.nanmean(X[:, j]))})
    out = pd.DataFrame(rows)
    print(f"  {label}: {len(out)} usable | dropped symbol {ds}, var {dv}, lines {dn}, paralog {dp}", flush=True)
    return out


print("building groups ...", flush=True)
G = {k: build(v, k) for k, v in groups.items()}


def boot(A, Bg, reps=2000):
    if len(A) < 5 or len(Bg) < 5:
        return None, [None, None], 0
    genes = sorted(set(A.g1) | set(A.g2) | set(Bg.g1) | set(Bg.g2))
    gi = {g: i for i, g in enumerate(genes)}
    a1 = np.array([gi[g] for g in A.g1]); a2 = np.array([gi[g] for g in A.g2])
    b1 = np.array([gi[g] for g in Bg.g1]); b2 = np.array([gi[g] for g in Bg.g2])
    ra, rb = A.r.to_numpy(), Bg.r.to_numpy()
    out = []
    for _ in range(reps):
        c = np.bincount(rng.integers(0, len(genes), len(genes)), minlength=len(genes)).astype(float)
        wa, wb = c[a1] * c[a2], c[b1] * c[b2]
        if wa.sum() == 0 or wb.sum() == 0:
            continue
        out.append((wa * ra).sum() / wa.sum() - (wb * rb).sum() / wb.sum())
    lo, hi = np.percentile(out, [2.5, 97.5])
    return float(ra.mean() - rb.mean()), [float(lo), float(hi)], len(out)


res = {"dataset": "DEMETER2 combined (figshare 6025238, file 13515395)",
       "n_lines": int(X.shape[0]), "n_genes": int(X.shape[1]), "min_lines": MIN_LINES,
       "deviation": DEVIATION,
       "group_n": {k: int(len(v)) for k, v in G.items()},
       "group_mean_r": {k: round(float(v.r.mean()), 4) for k, v in G.items()}}

d, ci, nb = boot(G["P"], G["L"])
res["R0_gate"] = {"diff": round(d, 4), "ci95": [round(c, 4) for c in ci], "n_boot": nb,
                  "sensitive": bool(d is not None and d > 0 and ci[0] > 0)}

d1, ci1, nb1 = boot(G["T"], G["L"])
res["R1_primary"] = {"diff": round(d1, 4), "ci95": [round(c, 4) for c in ci1], "n_boot": nb1}
res["R1_verdict"] = ("NOT INTERPRETED (R0 failed)" if not res["R0_gate"]["sensitive"]
                     else "REPLICATES" if d1 > 0 and ci1[0] > 0
                     else "CONTRADICTS" if ci1[1] < 0 else "FAILS TO REPLICATE (CI includes 0)")

# R2: the pre-registered CORUM split
r2 = {}
for lab, sel in (("CORUM", True), ("non-CORUM", False)):
    a, b = G["T"][G["T"].corum == sel], G["L"][G["L"].corum == sel]
    dd, cc, nn = boot(a, b)
    r2[lab] = {"n_T": len(a), "n_L": len(b),
               "mean_r_T": round(float(a.r.mean()), 4) if len(a) else None,
               "mean_r_L": round(float(b.r.mean()), 4) if len(b) else None,
               "diff": round(dd, 4) if dd is not None else None,
               "ci95": [round(c, 4) for c in cc] if dd is not None else None,
               "holds": bool(dd is not None and dd > 0 and cc[0] > 0)}
res["R2_corum_split"] = r2
res["R2_confirms_codep"] = bool(r2["CORUM"]["holds"] and not r2["non-CORUM"]["holds"])

# R3 essentiality-matched
allp = pd.concat([G["T"].assign(grp="T"), G["L"].assign(grp="L")])
allp["minm"] = np.minimum(allp.m1, allp.m2)
allp["st"] = pd.qcut(allp.minm, 5, labels=False, duplicates="drop")
num = den = 0.0
for s, sub in allp.groupby("st"):
    a, b = sub[sub.grp == "T"], sub[sub.grp == "L"]
    if len(a) < 10 or len(b) < 10:
        continue
    w = len(a) + len(b)
    num += (a.r.mean() - b.r.mean()) * w
    den += w
res["R3_essentiality_matched_pooled"] = round(num / den, 4) if den else None

print()
print(json.dumps(res, indent=1, default=float))
json.dump(res, open("results_codep_r.json", "w"), indent=1, default=float)
