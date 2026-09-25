"""PREREG_HIGHER: is the split-crosslink pattern (some links near, some impossible in the 1:1 model) a
general signature of higher-order assembly? Independent line: over-length self-links (>= 45 A within one
chain). Uses DSSO + DSS links (union), Amendment 2 site resolution (current UniProt sequences), pooled AF3
CA coordinates. Committed pre-registration: PREREG_HIGHER.md."""
import importlib
import json
import os
from collections import defaultdict

import numpy as np
import pandas as pd

os.environ["XL_SEQ"] = "uniprot"
os.environ["XL_DATA"] = "DSSO"
import analysis_xlval as A  # noqa: E402  (module-level load of DSSO links)

L = A.L
NEAR, FAR = 30.0, 45.0
rng = np.random.default_rng(23)


def load_links(which):
    """inter- and intra-protein links for one crosslinker, sites resolved by A.locate, mapped to MG loci."""
    os.environ["XL_DATA"] = which
    importlib.reload(A)
    xdir = os.path.join(L, "xlms2020" if which == "DSSO" else "xlms2020_dss")
    X = pd.read_csv(os.path.join(xdir, f"Myco_InCell_{which}_dataset_5link_5PPI_Links_xiFDR1.2.30.59dev.csv"),
                    index_col=False, low_memory=False)
    X = X[X.isTT & ~X.isDecoy & (X.fdr <= 0.05)].copy()
    X["a"], X["b"] = X.Protein1.map(A.acc), X.Protein2.map(A.acc)
    X["ga"], X["gb"] = X.a.map(A.p2g), X.b.map(A.p2g)
    X = X[X.ga.notna() & X.gb.notna()].copy()
    X["pa"] = [A.site.get(str(k), (None, None))[0] for k in X.LinkID]
    X["pb"] = [A.site.get(str(k), (None, None))[1] for k in X.LinkID]
    X = X[X.pa.notna() & X.pb.notna()].copy()
    X["pa"], X["pb"] = X.pa.astype(int), X.pb.astype(int)
    X["xl"] = which
    return X


X = pd.concat([load_links("DSSO"), load_links("DSS")], ignore_index=True)
mgseq, ix, S0, PRE = A.mgseq, A.ix, A.S0, A.PRE

# index: locus -> npz files containing it
loc_files = defaultdict(list)
for f in sorted(os.listdir(os.path.join(L, "structs_ca"))):
    if f.endswith(".npz"):
        z = np.load(os.path.join(L, "structs_ca", f))
        for l in z["loci"]:
            loc_files[str(l)].append(f)


def chain_coords(f, g):
    z = np.load(os.path.join(L, "structs_ca", f))
    loci = [str(l) for l in z["loci"]]
    if g not in loci:
        return []
    c = loci.index(g)
    return [z[f"xyz{k}"].astype(np.float32)[z["chain"] == c] for k in range(5)]


_cc = {}


def cc(f, g):
    if (f, g) not in _cc:
        _cc[(f, g)] = chain_coords(f, g)
    return _cc[(f, g)]


def pair_models(g1, g2):
    """yield (coords_g1, coords_g2) for every pooled model+sample containing both loci"""
    for f in sorted(set(loc_files[g1]) & set(loc_files[g2])):
        a, b = cc(f, g1), cc(f, g2)
        for k in range(min(len(a), len(b))):
            yield a[k], b[k]


def solo_models(g):
    for f in sorted(loc_files[g]):
        for x in cc(f, g):
            yield x


def mg_sites(row, g1, g2):
    """map one link's two residues onto (g1, g2) in that order; None if unalignable"""
    (ma, ra), (mb, rb) = ((row.a, row.pa), (row.b, row.pb)) if row.ga == g1 else ((row.b, row.pb), (row.a, row.pa))
    return A.mpn2mg(ma, g1).get(ra), A.mpn2mg(mb, g2).get(rb)


# ---------- over-length self-links (independent oligomerisation line) ----------
selfx = X[X.ga == X.gb]
oligo, self_tab = set(), []
for g, sub in selfx.groupby("ga"):
    M = list(solo_models(g))
    if not M:
        continue
    n = min(len(m) for m in M)
    links, over = set(), []
    for r in sub.itertuples():
        x1, x2 = mg_sites(r, g, g)
        if x1 and x2 and x1 != x2 and x1 <= n and x2 <= n:
            links.add((min(x1, x2), max(x1, x2)))
    for (x1, x2) in sorted(links):
        d = min(float(np.linalg.norm(m[x1 - 1] - m[x2 - 1])) for m in M)
        if d >= FAR:
            over.append(((x1, x2), round(d, 1)))
    if over:
        oligo.add(g)
    self_tab.append({"locus": g, "n_self_links": len(links), "n_over_length": len(over),
                     "over": over[:5], "oligomeric": bool(over)})

# ---------- inter-protein pairs: split signature vs clean dimer ----------
inter = X[X.ga != X.gb]
pairs = {}
for (a, b), sub in inter.groupby([inter[["ga", "gb"]].min(axis=1), inter[["ga", "gb"]].max(axis=1)]):
    M = list(pair_models(a, b))
    if not M:
        continue
    n1, n2 = min(len(m[0]) for m in M), min(len(m[1]) for m in M)
    links = set()
    for r in sub.itertuples():
        x1, x2 = mg_sites(r, a, b)
        if x1 and x2 and x1 <= n1 and x2 <= n2:
            links.add((x1, x2))
    links = sorted(links)
    if len(links) < 2:
        continue
    dmin = [min(float(np.linalg.norm(m[0][x1 - 1] - m[1][x2 - 1])) for m in M) for (x1, x2) in links]
    near = [d <= NEAR for d in dmin]
    far = [d >= FAR for d in dmin]
    pairs[(a, b)] = {"pair": f"{a}-{b}", "n_links": len(links), "n_models": len(M),
                     "min_dist": [round(d, 1) for d in dmin],
                     "n_near": int(sum(near)), "n_far": int(sum(far)),
                     "split": bool(any(near) and any(far)), "clean": bool(all(near)),
                     "oligomeric_partner": bool(a in oligo or b in oligo),
                     "S0": float(S0[ix[a], ix[b]]), "prec": bool(PRE[ix[a], ix[b]])}

P = pd.DataFrame(pairs.values())
split = P[P.split]
clean = P[P.clean]
res = {"n_testable_pairs": len(P), "n_split": len(split), "n_clean": len(clean),
       "n_proteins_with_self_links": len(self_tab), "n_oligomeric_proteins": len(oligo)}

# ---------- P2: positive control ----------
pc = pairs.get(("MG_139", "MG_423"))
res["P2_positive_control"] = pc if pc else "MG_139-MG_423 not testable"
res["P2_passes"] = bool(pc and pc["split"])

# ---------- P1: primary ----------
if len(split) < 8 or len(clean) < 8:
    res["P1_verdict"] = f"UNDERPOWERED (split={len(split)}, clean={len(clean)}; need >= 8 each)"
elif not res["P2_passes"]:
    res["P1_verdict"] = "NOT INTERPRETED (P2 positive control failed)"
else:
    p_split = float(split.oligomeric_partner.mean())
    p_clean = float(clean.oligomeric_partner.mean())
    loci = sorted({g for p in pairs for g in p})
    li = {g: i for i, g in enumerate(loci)}
    ga = np.array([li[p[0]] for p in pairs]); gb = np.array([li[p[1]] for p in pairs])
    is_split = P.split.values; is_clean = P.clean.values; olig = P.oligomeric_partner.values
    bs = []
    for _ in range(2000):
        c = np.bincount(rng.integers(0, len(loci), len(loci)), minlength=len(loci)).astype(float)
        w = c[ga] * c[gb]
        ws, wc = (w * is_split).sum(), (w * is_clean).sum()
        if ws == 0 or wc == 0:
            continue
        bs.append((w * is_split * olig).sum() / ws - (w * is_clean * olig).sum() / wc)
    lo, hi = np.quantile(bs, [0.025, 0.975])
    res.update(P1_p_oligomeric_given_split=p_split, P1_p_oligomeric_given_clean=p_clean,
               P1_diff=p_split - p_clean, P1_ci95=[float(lo), float(hi)], P1_n_boot=len(bs))
    res["P1_verdict"] = ("SUPPORTED" if (p_split - p_clean) > 0 and lo > 0 else
                         "REFUTED" if hi < 0 else "INCONCLUSIVE (CI includes 0)")

# ---------- P3 ----------
p3 = split[(split.oligomeric_partner) & (~split.prec)].sort_values("S0", ascending=False)
res["P3_predicted_higher_order_novel"] = p3.to_dict("records")
res["all_pairs"] = P.sort_values("S0", ascending=False).to_dict("records")
res["self_links"] = sorted(self_tab, key=lambda d: -d["n_over_length"])

print(json.dumps({k: v for k, v in res.items() if k not in ("all_pairs", "self_links", "P3_predicted_higher_order_novel")}, indent=1, default=float))
print("\nP3 predicted higher-order, no precedent:", len(p3))
for r in p3.head(15).itertuples():
    print(f"  {r.pair:20s} S0={r.S0:.3f} links={r.n_links} near={r.n_near} far={r.n_far} dists={r.min_dist}")
json.dump(res, open("results_higher.json", "w"), indent=1, default=lambda o: o.item() if isinstance(o, (np.integer, np.floating, np.bool_)) else o)
