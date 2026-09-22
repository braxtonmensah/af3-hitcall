"""POST HOC robustness of the XL-MS result (not pre-registered).
Does the precedented/unprecedented gap survive (i) requiring more crosslinks per pair, which
favours specific interfaces over transient crowding contacts, and (ii) dropping crosslink hubs?"""
import json, os
import numpy as np, pandas as pd
from analysis_h1_h2_lib import LOCI, precedent_matrix
from metrics import Ranked, ci

D = r"C:\Users\bmens\NQ_local\af3-hitcall"
rng = np.random.default_rng(7)
S0 = np.load(os.path.join(D, "data", "S0.npy")); P = precedent_matrix("")
n = len(LOCI); ix = {l: i for i, l in enumerate(LOCI)}
mp = pd.read_csv(os.path.join(D, "data", "mpn_to_mg.csv")); m2i = {a: ix[l] for a, l in zip(mp.mpn, mp.mg)}
x = pd.read_csv(os.path.join(D, "xlms2020", "Myco_InCell_DSSO_dataset_5link_5PPI_ppi_xiFDR1.2.30.59dev.csv"), index_col=False)
x = x[x.isTT & ~x.isDecoy & (x.fdr <= 0.05)]
acc = lambda s: str(s).split(";")[0].split("|")[-1]
x["a"], x["b"] = x.Protein1.map(acc), x.Protein2.map(acc)
seen = {m2i[p] for p in pd.concat([x.a, x.b]) if p in m2i}
bt = x[(x.fdrGroup == "Between") & x.a.isin(m2i) & x.b.isin(m2i)].copy()
bt["i"], bt["j"] = bt.a.map(m2i), bt.b.map(m2i)
bt = bt[bt.i != bt.j]
deg = pd.concat([bt.i, bt.j]).value_counts()
out = {}
for label, minlinks, drop_hubs in [("links>=1", 1, 0), ("links>=2", 2, 0), ("links>=3", 3, 0),
                                   ("links>=1, drop top-5 hubs", 1, 5), ("links>=2, drop top-5 hubs", 2, 5)]:
    hubs = set(deg.index[:drop_hubs])
    XL = np.zeros((n, n), bool); weak = np.zeros((n, n), bool)
    for i, j, c in zip(bt.i, bt.j, bt["count links"]):
        (XL if c >= minlinks else weak)[i, j] = True
    XL |= XL.T; weak |= weak.T
    pi, pj = np.triu_indices(n, 1)
    vis = np.array([k in seen and k not in hubs for k in range(n)])
    keep = vis[pi] & vis[pj] & ~weak[pi, pj]  # weaker XL pairs are neither positive nor negative
    pi, pj = pi[keep], pj[keep]
    y = XL[pi, pj]; prec = P[pi, pj]; r = Ranked(S0[pi, pj]); one = np.ones(len(pi))
    pp, pu, neg = y & prec, y & ~prec, ~y
    bs = []
    for _ in range(1000):
        c = np.bincount(rng.integers(0, n, n), minlength=n).astype(float); w = c[pi] * c[pj]
        if (w * pu).sum() and (w * pp).sum():
            bs.append(r.auroc(w * pp, w * neg) - r.auroc(w * pu, w * neg))
    out[label] = dict(n_prec=int(pp.sum()), n_unprec=int(pu.sum()),
                      auroc_prec=r.auroc(one * pp, one * neg), auroc_unprec=r.auroc(one * pu, one * neg),
                      diff_ci95=ci(np.array(bs), 0.95).tolist())
    o = out[label]
    print(f"{label:28s} prec n={o['n_prec']:3d} AUROC {o['auroc_prec']:.3f} | unprec n={o['n_unprec']:3d} AUROC {o['auroc_unprec']:.3f} | diff CI {np.round(o['diff_ci95'],3)}")
print("top XL hubs:", [(LOCI[k], int(v)) for k, v in deg.head(8).items()])
json.dump(out, open("results_posthoc_xl.json", "w"), indent=1, default=float)
