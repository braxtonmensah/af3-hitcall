"""PREREG_XL.md: H1 re-tested against in-cell crosslinking MS (independent of the PDB)."""
import json
import os

import numpy as np
import pandas as pd

from analysis_h1_h2_lib import LOCI, precedent_matrix
from metrics import Ranked, ci

D = r"C:\Users\bmens\NQ_local\af3-hitcall"
rng = np.random.default_rng(2020)
S0 = np.load(os.path.join(D, "data", "S0.npy"))
ST = np.load(os.path.join(D, "data", "string_exp.npy"))
P = precedent_matrix("")
n = len(LOCI)
ix = {l: i for i, l in enumerate(LOCI)}

mp = pd.read_csv(os.path.join(D, "data", "mpn_to_mg.csv"))
m2i = {a: ix[l] for a, l in zip(mp.mpn, mp.mg)}
x = pd.read_csv(os.path.join(D, "xlms2020", "Myco_InCell_DSSO_dataset_5link_5PPI_ppi_xiFDR1.2.30.59dev.csv"),
                index_col=False)
x = x[x.isTT & ~x.isDecoy & (x.fdr <= 0.05)]


def acc(s):
    return str(s).split(";")[0].split("|")[-1]


x["a"], x["b"] = x.Protein1.map(acc), x.Protein2.map(acc)
seen = {m2i[p] for p in pd.concat([x.a, x.b]) if p in m2i}
XL = np.zeros((n, n), bool)
for a, b in zip(x[x.fdrGroup == "Between"].a, x[x.fdrGroup == "Between"].b):
    if a in m2i and b in m2i and m2i[a] != m2i[b]:
        XL[m2i[a], m2i[b]] = XL[m2i[b], m2i[a]] = True

pi, pj = np.triu_indices(n, 1)
vis = np.array([i in seen for i in range(n)])
cand = vis[pi] & vis[pj]
pi, pj = pi[cand], pj[cand]
y = XL[pi, pj]
prec = P[pi, pj]
s = S0[pi, pj]
neg = ~y
pp, pu = y & prec, y & ~prec
r = Ranked(s)
one = np.ones(len(s))
res = {"n_proteins_visible": int(vis.sum()), "n_pairs": int(len(s)), "n_xl_pos": int(y.sum()),
       "n_pos_precedented": int(pp.sum()), "n_pos_unprecedented": int(pu.sum()),
       "auroc_all": r.auroc(one * y, one * neg),
       "auroc_precedented": r.auroc(one * pp, one * neg),
       "auroc_unprecedented": r.auroc(one * pu, one * neg)}
novel = y & ~(ST[pi, pj] > 800)
res["n_xl_pos_string_negative"] = int(novel.sum())
res["auroc_xl_pos_string_negative"] = r.auroc(one * novel, one * neg)
res["auroc_xl_pos_string_negative_unprecedented"] = r.auroc(one * (novel & ~prec), one * neg)
res["n_xl_pos_string_negative_unprecedented"] = int((novel & ~prec).sum())

bs = []
for _ in range(2000):
    c = np.bincount(rng.integers(0, n, n), minlength=n).astype(float)
    w = c[pi] * c[pj]
    if (w * pu).sum() == 0 or (w * pp).sum() == 0:
        continue
    bs.append(r.auroc(w * pp, w * neg) - r.auroc(w * pu, w * neg))
res["diff"] = res["auroc_precedented"] - res["auroc_unprecedented"]
res["diff_ci95"] = ci(np.array(bs), 0.95).tolist()
lo, hi = res["diff_ci95"]
if res["n_pos_unprecedented"] < 30:
    res["verdict"] = "UNDERPOWERED"
elif res["diff"] >= 0.10 and lo > 0:
    res["verdict"] = "(a) MODEL: gap persists on independent truth"
elif lo <= 0 <= hi and res["auroc_unprecedented"] >= 0.80:
    res["verdict"] = "(b) LABELS: gap vanishes on independent truth"
else:
    res["verdict"] = "INCONCLUSIVE"
print(json.dumps(res, indent=1))
json.dump(res, open("results_xl.json", "w"), indent=1, default=float)
