"""POST HOC: value of a second pool replicate. Pairs seen in >=2 pools (38,718): AUROC of one
pool's value vs the mean of two, on the same pairs. Averages over 20 random draws of which pools are
used; node-bootstrap CI on the difference, also split by precedent."""
import json, os
import numpy as np, pandas as pd
from analysis_h1_h2_lib import precedent_matrix
from metrics import Ranked, ci
D = r"C:\Users\bmens\NQ_local\af3-hitcall\data"
rng = np.random.default_rng(5)
ST = np.load(os.path.join(D, "string_exp.npy")); n = ST.shape[0]
PRE = precedent_matrix("") | precedent_matrix("_id0")
rep = pd.read_csv(os.path.join(D, "s0_per_pool.csv"))
g = rep.groupby(["i", "j"]).s0.apply(list)
g = g[g.map(len) >= 2]
ii = np.array([k[0] for k in g.index]); jj = np.array([k[1] for k in g.index])
y = ST[ii, jj] > 800; pre = PRE[ii, jj]
vals = list(g.values)
one1, two = [], []
for d in range(20):
    a = np.array([v[rng.permutation(len(v))[:2]] if False else rng.choice(v, 2, replace=False) for v in vals])
    one1.append(a[:, 0]); two.append(a.mean(1))
res = {"n_pairs": int(len(vals)), "n_pos": int(y.sum())}
for lab, m in [("all", np.ones(len(y), bool)), ("precedented_pos", pre), ("unprecedented_pos", ~pre)]:
    yy = y & m; neg = ~y
    R1 = [Ranked(s) for s in one1[:5]]; R2 = [Ranked(s) for s in two[:5]]
    ones = np.ones(len(y))
    a1 = np.mean([r.auroc(ones * yy, ones * neg) for r in R1]); a2 = np.mean([r.auroc(ones * yy, ones * neg) for r in R2])
    bs = []
    for _ in range(500):
        c = np.bincount(rng.integers(0, n, n), minlength=n).astype(float); w = c[ii] * c[jj]
        k = rng.integers(0, 5)
        bs.append(R2[k].auroc(w * yy, w * neg) - R1[k].auroc(w * yy, w * neg))
    res[lab] = {"n_pos": int(yy.sum()), "auroc_1pool": a1, "auroc_2pool_mean": a2, "gain": a2 - a1, "gain_ci95": ci(np.array(bs), 0.95).tolist()}
    print(lab, json.dumps(res[lab], default=float))
json.dump(res, open("results_posthoc_replicates.json", "w"), indent=1, default=float)
