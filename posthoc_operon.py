"""POST HOC exploratory: within never-solved STRING positives, do genomically adjacent pairs
(|MG number difference| <= 2, a crude operon / obligate-partner proxy) score higher?"""
import os, re, json
import numpy as np, pandas as pd
from analysis_h1_h2_lib import LOCI, precedent_matrix_strict
from metrics import Ranked, ci
D = r"C:\Users\bmens\NQ_local\af3-hitcall\data"
rng = np.random.default_rng(4)
S0 = np.load(os.path.join(D, "S0.npy")); ST = np.load(os.path.join(D, "string_exp.npy"))
n = len(LOCI); pi, pj = np.triu_indices(n, 1)
num = np.array([int(re.search(r"(\d+)", l).group(1)) for l in LOCI])
adj = np.abs(num[pi] - num[pj]) <= 2
PRE = (precedent_matrix_strict("") | precedent_matrix_strict("_id0"))[pi, pj]
y = ST[pi, pj] > 800; neg = ~y; r = Ranked(S0[pi, pj]); one = np.ones(len(y))
res = {}
for lab, m in [("never_adjacent", y & ~PRE & adj), ("never_distant", y & ~PRE & ~adj),
               ("prec_adjacent", y & PRE & adj), ("prec_distant", y & PRE & ~adj)]:
    res[lab] = dict(n=int(m.sum()), auroc=r.auroc(one * m, one * neg)); print(lab, res[lab])
a, b = y & ~PRE & adj, y & ~PRE & ~adj
bs = []
for _ in range(2000):
    c = np.bincount(rng.integers(0, n, n), minlength=n).astype(float); w = c[pi] * c[pj]
    if (w * a).sum() and (w * b).sum(): bs.append(r.auroc(w * a, w * neg) - r.auroc(w * b, w * neg))
res["never_adj_minus_distant_ci95"] = ci(np.array(bs), 0.95).tolist(); print(res["never_adj_minus_distant_ci95"])
json.dump(res, open("results_posthoc_operon.json", "w"), indent=1, default=float)
