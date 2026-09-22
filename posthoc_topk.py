"""POST HOC descriptive: bait-level top-k recall by precedent class (strict rule).
A positive pair counts as recovered at k if either protein ranks the other in its top k partners."""
import os, json
import numpy as np
from scipy.stats import rankdata
from analysis_h1_h2_lib import precedent_matrix_strict
D = r"C:\Users\bmens\NQ_local\af3-hitcall\data"
S0 = np.load(os.path.join(D, "S0.npy")); ST = np.load(os.path.join(D, "string_exp.npy"))
n = S0.shape[0]; PRE = precedent_matrix_strict("") | precedent_matrix_strict("_id0")
R = np.full((n, n), np.nan)
for i in range(n):
    m = np.arange(n) != i
    R[i, m] = rankdata(-S0[i, m], method="average")
best = np.fmin(R, R.T)
iu = np.triu_indices(n, 1); y = ST[iu] > 800; pre = PRE[iu]; b = best[iu]
res = {}
for lab, m in [("precedented", y & pre), ("never_solved", y & ~pre), ("all_negatives", ~y)]:
    res[lab] = {f"top{k}": float((b[m] <= k).mean()) for k in (1, 5, 10, 25)}
    res[lab]["n"] = int(m.sum())
    print(lab, res[lab])
json.dump(res, open("results_posthoc_topk.json", "w"), indent=1)

# precision of each bait's top-ranked partner, by class of that top pair
top = np.nanargmin(np.where(np.isnan(R), np.inf, R), axis=1)
pos = ST[np.arange(n), top] > 800
cls = PRE[np.arange(n), top]
has = (ST > 800).sum(1) > 0
out = {}
for lab, m in [("top1_precedented", cls), ("top1_never_solved", ~cls)]:
    for sub, mm in [("all_baits", np.ones(n, bool)), ("baits_with_a_positive", has)]:
        k = m & mm
        out[f"{lab}|{sub}"] = dict(n=int(k.sum()), precision=float(pos[k].mean()))
        print(lab, sub, out[f"{lab}|{sub}"])
res["top1_precision"] = out
json.dump(res, open("results_posthoc_topk.json", "w"), indent=1)
