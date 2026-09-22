"""PREREG_TIME.md: memorisation vs stability via post-cutoff-only co-complex precedent."""
import json
import os

import numpy as np
import pandas as pd

from analysis_h1_h2_lib import LOCI, precedent_matrix
from metrics import Ranked, ci

D = r"C:\Users\bmens\NQ_local\af3-hitcall"
rng = np.random.default_rng(930)
S0 = np.load(os.path.join(D, "data", "S0.npy"))
ST = np.load(os.path.join(D, "data", "string_exp.npy"))
n = len(LOCI)
PRE = precedent_matrix("") | precedent_matrix("_id0")
POST = precedent_matrix("_post") & ~PRE


def test(pi, pj, y, label):
    s = S0[pi, pj]
    r = Ranked(s)
    one = np.ones(len(s))
    neg = ~y
    pre, post = PRE[pi, pj], POST[pi, pj]
    never = ~pre & ~post
    m = {"pre": y & pre, "post_only": y & post, "never": y & never}
    rec = {f"n_{k}": int(v.sum()) for k, v in m.items()}
    rec["n_neg_post_only"] = int((neg & post).sum())
    au = {k: r.auroc(one * v, one * neg) for k, v in m.items()}
    rec.update({f"auroc_{k}": v for k, v in au.items()})
    f = (au["post_only"] - au["never"]) / (au["pre"] - au["never"])
    rec["f"] = f
    bs = []
    for _ in range(2000):
        c = np.bincount(rng.integers(0, n, n), minlength=n).astype(float)
        w = c[pi] * c[pj]
        if min((w * v).sum() for v in m.values()) == 0:
            continue
        a = {k: r.auroc(w * v, w * neg) for k, v in m.items()}
        den = a["pre"] - a["never"]
        if abs(den) > 1e-9:
            bs.append((a["post_only"] - a["never"]) / den)
    lo, hi = ci(np.array(bs), 0.95)
    rec["f_ci95"] = [lo, hi]
    if rec["n_post_only"] < 20:
        rec["verdict"] = "UNDERPOWERED"
    elif f >= 0.7 and lo > 0.3:
        rec["verdict"] = "STABILITY"
    elif f <= 0.3 and hi < 0.7:
        rec["verdict"] = "MEMORISATION"
    else:
        rec["verdict"] = "MIXED / INCONCLUSIVE"
    print(label, json.dumps(rec, indent=1, default=float))
    return rec


pi, pj = np.triu_indices(n, 1)
out = {"STRING": test(pi, pj, ST[pi, pj] > 800, "STRING>800")}

# XL-MS truth (same construction as analysis_xl.py)
ix = {l: i for i, l in enumerate(LOCI)}
mp = pd.read_csv(os.path.join(D, "data", "mpn_to_mg.csv"))
m2i = {a: ix[l] for a, l in zip(mp.mpn, mp.mg)}
x = pd.read_csv(os.path.join(D, "xlms2020", "Myco_InCell_DSSO_dataset_5link_5PPI_ppi_xiFDR1.2.30.59dev.csv"), index_col=False)
x = x[x.isTT & ~x.isDecoy & (x.fdr <= 0.05)]
acc = lambda s: str(s).split(";")[0].split("|")[-1]
x["a"], x["b"] = x.Protein1.map(acc), x.Protein2.map(acc)
seen = {m2i[p] for p in pd.concat([x.a, x.b]) if p in m2i}
XL = np.zeros((n, n), bool)
for a, b in zip(x[x.fdrGroup == "Between"].a, x[x.fdrGroup == "Between"].b):
    if a in m2i and b in m2i and m2i[a] != m2i[b]:
        XL[m2i[a], m2i[b]] = XL[m2i[b], m2i[a]] = True
vis = np.array([k in seen for k in range(n)])
keep = vis[pi] & vis[pj]
out["XL"] = test(pi[keep], pj[keep], XL[pi[keep], pj[keep]], "XL-MS")
json.dump(out, open("results_time.json", "w"), indent=1, default=float)
