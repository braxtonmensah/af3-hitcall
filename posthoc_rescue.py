"""POST HOC: does any available signal help the never-solved class? Compare, on STRING>800 positives
split by precedent (Pre = either pre-cutoff definition), AUROC vs all negatives for:
S0, raw ipTM, the paper's profile correlation, and the paper's combined S0 + 0.2*corr."""
import os, json
import numpy as np
from analysis_h1_h2_lib import precedent_matrix
from metrics import Ranked, ci
D = r"C:\Users\bmens\NQ_local\af3-hitcall\data"
rng = np.random.default_rng(1)
S0 = np.load(os.path.join(D, "S0.npy")); RAW = np.load(os.path.join(D, "raw.npy"))
C = np.load(os.path.join(D, "corr.npy")); ST = np.load(os.path.join(D, "string_exp.npy"))
n = S0.shape[0]; pi, pj = np.triu_indices(n, 1)
PRE = (precedent_matrix("") | precedent_matrix("_id0"))[pi, pj]
y = ST[pi, pj] > 800; neg = ~y; one = np.ones(len(y))
scores = {"S0": S0[pi, pj], "raw": RAW[pi, pj], "corr": C[pi, pj], "S0+0.2corr": S0[pi, pj] + 0.2 * C[pi, pj]}
R = {k: Ranked(v) for k, v in scores.items()}
res = {}
for lab, m in [("precedented", y & PRE), ("never_solved", y & ~PRE)]:
    res[lab] = {k: round(r.auroc(one * m, one * neg), 4) for k, r in R.items()}
    res[lab]["n"] = int(m.sum())
# CI on (combined - S0) for never-solved
m = y & ~PRE; bs = []
for _ in range(1000):
    c = np.bincount(rng.integers(0, n, n), minlength=n).astype(float); w = c[pi] * c[pj]
    bs.append(R["S0+0.2corr"].auroc(w * m, w * neg) - R["S0"].auroc(w * m, w * neg))
res["never_solved_combined_minus_S0_ci95"] = ci(np.array(bs), 0.95).tolist()
print(json.dumps(res, indent=1, default=float))
json.dump(res, open("results_posthoc_rescue.json", "w"), indent=1, default=float)
