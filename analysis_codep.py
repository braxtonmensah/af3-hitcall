"""PREREG_CODEP: are confident never-solved AlphaFold predictions functionally coupled?
Truth source is CRISPR co-dependency (DepMap 24Q4 Public gene effect), which no structure predictor
can have contaminated. Committed pre-registration: PREREG_CODEP.md (commit 0da2677).

Run: py -3.11 analysis_codep.py
"""
import json
import os

import numpy as np
import pandas as pd

B = r"C:\Users\bmens\NQ_local\af3-hitcall\burke"
D = r"C:\Users\bmens\NQ_local\af3-hitcall\depmap"
MIN_LINES = 300
PARALOG_ID = 0.30
rng = np.random.default_rng(27)

# ---------------------------------------------------------------- DepMap
print("loading DepMap gene effect ...", flush=True)
GE = pd.read_csv(os.path.join(D, "CRISPRGeneEffect.csv"), index_col=0, low_memory=False)
GE.columns = [c.split(" (")[0] for c in GE.columns]
GE = GE.loc[:, ~GE.columns.duplicated()]
X = GE.to_numpy(dtype=np.float32)
SYM = {s: i for i, s in enumerate(GE.columns)}
print(f"  {X.shape[0]} cell lines x {X.shape[1]} genes", flush=True)

sd = np.nanstd(X, axis=0)
sd_floor = np.nanpercentile(sd, 25)
ok_var = sd >= sd_floor                                  # F1 variance floor
print(f"  F1 variance floor sd >= {sd_floor:.4f}: {ok_var.sum()} of {len(sd)} genes kept", flush=True)

# ---------------------------------------------------------------- pairs
s1 = pd.read_csv(os.path.join(B, "S1.csv"), low_memory=False)
s1 = s1[(s1.id1 != s1.id2)].copy()
if "homodimers" in s1.columns:
    hd = s1.homodimers.astype(str).str.lower().isin(["true", "1", "yes"])
    s1 = s1[~hd].copy()
s1["key"] = ["_".join(sorted([str(a), str(b)])) for a, b in zip(s1.id1, s1.id2)]
s1 = s1.drop_duplicates("key")
s1["g1"] = s1["Gen.id1"].astype(str)
s1["g2"] = s1["Gen.id2"].astype(str)
s1["prec"] = s1.int3D_model_structure.fillna(0).astype(int) == 1

groups = {
    "T": s1[(s1.pDockQ > 0.23) & (~s1.prec)],
    "L": s1[(s1.pDockQ < 0.10) & (~s1.prec)],
    "P": s1[(s1.pDockQ > 0.23) & (s1.prec)],
}

# ---------------------------------------------------------------- F2 paralog identity
seqs = {}
p = os.path.join(B, "uniprot_seqs.json")
if os.path.exists(p):
    seqs = json.load(open(p))
try:
    from Bio import Align
    aligner = Align.PairwiseAligner(mode="global", open_gap_score=-11, extend_gap_score=-1,
                                    substitution_matrix=Align.substitution_matrices.load("BLOSUM62"))
    HAVE_ALIGNER = True
except Exception as e:                                    # noqa: BLE001
    print("  no aligner available:", e)
    HAVE_ALIGNER = False

_idcache = {}


def identity(a, b):
    """global pairwise identity, or None when a sequence is missing / no aligner"""
    sa, sb = seqs.get(a), seqs.get(b)
    if not sa or not sb or not HAVE_ALIGNER:
        return None
    k = (a, b) if a < b else (b, a)
    if k in _idcache:
        return _idcache[k]
    if max(len(sa), len(sb)) > 2000:                      # keep the alignment cost bounded
        sa, sb = sa[:2000], sb[:2000]
    try:
        aln = aligner.align(sa, sb)[0]
        m = sum(1 for x, y in zip(aln[0], aln[1]) if x == y and x != "-")
        v = m / max(len(sa), len(sb))
    except Exception:                                     # noqa: BLE001
        v = None
    _idcache[k] = v
    return v


# ---------------------------------------------------------------- correlation
def pair_r(i, j):
    a, b = X[:, i], X[:, j]
    m = np.isfinite(a) & np.isfinite(b)
    n = int(m.sum())
    if n < MIN_LINES:
        return None, n
    aa, bb = a[m], b[m]
    aa = aa - aa.mean()
    bb = bb - bb.mean()
    d = np.sqrt((aa * aa).sum() * (bb * bb).sum())
    if d == 0:
        return None, n
    return float((aa * bb).sum() / d), n


def build(df, label):
    rows, drop_sym, drop_var, drop_n, drop_par, kept_no_seq = [], 0, 0, 0, 0, 0
    for t in df.itertuples():
        g1, g2 = t.g1, t.g2
        if g1 not in SYM or g2 not in SYM or g1 == g2:
            drop_sym += 1
            continue
        i, j = SYM[g1], SYM[g2]
        if not (ok_var[i] and ok_var[j]):
            drop_var += 1
            continue
        pid = identity(t.id1, t.id2)
        if pid is None:
            kept_no_seq += 1
        elif pid >= PARALOG_ID:
            drop_par += 1
            continue
        r, n = pair_r(i, j)
        if r is None:
            drop_n += 1
            continue
        rows.append({"g1": g1, "g2": g2, "id1": t.id1, "id2": t.id2, "r": r, "n_lines": n,
                     "pDockQ": float(t.pDockQ),
                     "ge1": float(np.nanmean(X[:, i])), "ge2": float(np.nanmean(X[:, j])),
                     "identity": pid})
    out = pd.DataFrame(rows)
    print(f"  {label}: {len(out)} usable | dropped: symbol {drop_sym}, variance {drop_var}, "
          f"<{MIN_LINES} lines {drop_n}, paralog {drop_par} | kept without sequence {kept_no_seq}",
          flush=True)
    return out


print("building groups (paralog alignment is the slow step) ...", flush=True)
G = {k: build(v, k) for k, v in groups.items()}

# ---------------------------------------------------------------- null
print("null ...", flush=True)
burke_pairs = set(zip(s1.g1, s1.g2)) | set(zip(s1.g2, s1.g1))
cand = np.flatnonzero(ok_var)
null_r = []
tries = 0
while len(null_r) < 50_000 and tries < 400_000:
    tries += 1
    i, j = rng.choice(cand, 2, replace=False)
    if (GE.columns[i], GE.columns[j]) in burke_pairs:
        continue
    r, _ = pair_r(int(i), int(j))
    if r is not None:
        null_r.append(r)
null_r = np.array(null_r)
null_p95 = float(np.percentile(null_r, 95))
print(f"  null n={len(null_r)} mean {null_r.mean():.4f} p95 {null_p95:.4f}", flush=True)


# ---------------------------------------------------------------- bootstrap over proteins
def boot_diff(A, Bg, reps=2000):
    genes = sorted(set(A.g1) | set(A.g2) | set(Bg.g1) | set(Bg.g2))
    gi = {g: k for k, g in enumerate(genes)}
    ia1 = np.array([gi[g] for g in A.g1]); ia2 = np.array([gi[g] for g in A.g2])
    ib1 = np.array([gi[g] for g in Bg.g1]); ib2 = np.array([gi[g] for g in Bg.g2])
    ra, rb = A.r.to_numpy(), Bg.r.to_numpy()
    out = []
    for _ in range(reps):
        c = np.bincount(rng.integers(0, len(genes), len(genes)), minlength=len(genes)).astype(float)
        wa, wb = c[ia1] * c[ia2], c[ib1] * c[ib2]
        if wa.sum() == 0 or wb.sum() == 0:
            continue
        out.append((wa * ra).sum() / wa.sum() - (wb * rb).sum() / wb.sum())
    lo, hi = np.percentile(out, [2.5, 97.5])
    return float(ra.mean() - rb.mean()), [float(lo), float(hi)], len(out)


res = {"depmap_release": "24Q4 Public (figshare 10.25452/figshare.plus.27993248.v1)",
       "n_cell_lines": int(X.shape[0]), "n_genes": int(X.shape[1]),
       "variance_floor_sd": round(float(sd_floor), 5),
       "group_n": {k: int(len(v)) for k, v in G.items()},
       "group_mean_r": {k: round(float(v.r.mean()), 4) for k, v in G.items()},
       "group_median_r": {k: round(float(v.r.median()), 4) for k, v in G.items()},
       "null": {"n": int(len(null_r)), "mean": round(float(null_r.mean()), 4), "p95": round(null_p95, 4)}}

# C4 instrument gate
d, ci, nb = boot_diff(G["P"], G["L"])
res["C4_positive_control"] = {"diff_P_minus_L": round(d, 4), "ci95": [round(c, 4) for c in ci],
                              "n_boot": nb, "sensitive": bool(d > 0 and ci[0] > 0)}

# D1 primary
d1, ci1, nb1 = boot_diff(G["T"], G["L"])
res["D1_primary"] = {"diff_T_minus_L": round(d1, 4), "ci95": [round(c, 4) for c in ci1], "n_boot": nb1}
res["D1_verdict"] = ("NOT INTERPRETED (C4 positive control failed)" if not res["C4_positive_control"]["sensitive"]
                     else "SUPPORTED" if d1 > 0 and ci1[0] > 0
                     else "REFUTED" if ci1[1] < 0 else "INCONCLUSIVE (CI includes 0)")

# C1 essentiality-matched
allp = pd.concat([G["T"].assign(grp="T"), G["L"].assign(grp="L")])
allp["minge"] = np.minimum(allp.ge1, allp.ge2)
allp["stratum"] = pd.qcut(allp.minge, 5, labels=False, duplicates="drop")
strata, wsum, wtot = [], 0.0, 0.0
for s, sub in allp.groupby("stratum"):
    a, b = sub[sub.grp == "T"], sub[sub.grp == "L"]
    if len(a) < 10 or len(b) < 10:
        strata.append({"stratum": int(s), "n_T": len(a), "n_L": len(b), "diff": None})
        continue
    diff = float(a.r.mean() - b.r.mean())
    w = len(a) + len(b)
    strata.append({"stratum": int(s), "n_T": len(a), "n_L": len(b),
                   "mean_r_T": round(float(a.r.mean()), 4), "mean_r_L": round(float(b.r.mean()), 4),
                   "diff": round(diff, 4)})
    wsum += diff * w
    wtot += w
pooled = wsum / wtot if wtot else None
# bootstrap the pooled stratified difference over proteins
genes = sorted(set(allp.g1) | set(allp.g2))
gi = {g: k for k, g in enumerate(genes)}
i1 = np.array([gi[g] for g in allp.g1]); i2 = np.array([gi[g] for g in allp.g2])
isT = (allp.grp == "T").to_numpy(); rr = allp.r.to_numpy(); st = allp.stratum.to_numpy()
bs = []
for _ in range(2000):
    c = np.bincount(rng.integers(0, len(genes), len(genes)), minlength=len(genes)).astype(float)
    w = c[i1] * c[i2]
    num = den = 0.0
    for s in np.unique(st):
        m = st == s
        wt, wl = w[m & isT], w[m & ~isT]
        if wt.sum() == 0 or wl.sum() == 0:
            continue
        dd = (wt * rr[m & isT]).sum() / wt.sum() - (wl * rr[m & ~isT]).sum() / wl.sum()
        ww = wt.sum() + wl.sum()
        num += dd * ww
        den += ww
    if den:
        bs.append(num / den)
clo, chi = np.percentile(bs, [2.5, 97.5])
res["C1_essentiality_matched"] = {"pooled_diff": round(pooled, 4) if pooled is not None else None,
                                  "ci95": [round(float(clo), 4), round(float(chi), 4)],
                                  "holds": bool(pooled and pooled > 0 and clo > 0),
                                  "strata": strata}

# C2 CORUM sanity
if "CORUM_ID_selection" in s1.columns:
    cor = set(s1[s1.CORUM_ID_selection.notna()].key)
    for k, v in G.items():
        v["corum"] = ["_".join(sorted([a, b])) in cor for a, b in zip(v.id1, v.id2)]
    res["C2_corum"] = {k: {"n": int(v.corum.sum()),
                           "mean_r": round(float(v[v.corum].r.mean()), 4) if v.corum.sum() else None}
                       for k, v in G.items()}

# D2 the output list
claimed = res["D1_verdict"] == "SUPPORTED" and res["C1_essentiality_matched"]["holds"]
hits = G["T"][G["T"].r > null_p95].sort_values("r", ascending=False)
res["D2"] = {"threshold_null_p95": round(null_p95, 4), "n_above": int(len(hits)),
             "frac_of_T": round(float(len(hits) / max(len(G["T"]), 1)), 4),
             "frac_of_L_above": round(float((G["L"].r > null_p95).mean()), 4),
             "claimed": bool(claimed),
             "top": hits.head(60)[["g1", "g2", "id1", "id2", "r", "pDockQ", "ge1", "ge2", "n_lines"]]
                        .round(4).to_dict("records")}

print()
print(json.dumps({k: v for k, v in res.items() if k != "D2"}, indent=1, default=float))
print(f"\nD2: {len(hits)} of {len(G['T'])} T pairs above the null 95th pct "
      f"({res['D2']['frac_of_T']:.1%}), vs {res['D2']['frac_of_L_above']:.1%} of L")
print("\ntop 25 by co-dependency:")
for t in hits.head(25).itertuples():
    print(f"  {t.g1:>12s} - {t.g2:<12s} r={t.r:6.3f}  pDockQ={t.pDockQ:.2f}  "
          f"ge {t.ge1:6.3f}/{t.ge2:6.3f}")

json.dump(res, open("results_codep.json", "w"), indent=1, default=float)
for k, v in G.items():
    v.to_csv(f"codep_group_{k}.csv", index=False)
