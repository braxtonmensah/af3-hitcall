"""Robustness of H1, XL and TIME to the strict precedent rule (self-caught definition flaw)."""
import json, os
import numpy as np, pandas as pd
from analysis_h1_h2_lib import LOCI, precedent_matrix, precedent_matrix_strict
from metrics import Ranked, ci
D = r"C:\Users\bmens\NQ_local\af3-hitcall"
rng = np.random.default_rng(99)
S0 = np.load(os.path.join(D, "data", "S0.npy")); ST = np.load(os.path.join(D, "data", "string_exp.npy"))
n = len(LOCI); pi, pj = np.triu_indices(n, 1)
y = ST[pi, pj] > 800; neg = ~y; r = Ranked(S0[pi, pj]); one = np.ones(len(y))
res = {}
for lab, Pm in [("original", precedent_matrix("")), ("strict", precedent_matrix_strict(""))]:
    p = Pm[pi, pj]; pp, pu = y & p, y & ~p
    bs = []
    for _ in range(2000):
        c = np.bincount(rng.integers(0, n, n), minlength=n).astype(float); w = c[pi] * c[pj]
        bs.append(r.auroc(w * pp, w * neg) - r.auroc(w * pu, w * neg))
    res[lab] = dict(n_prec=int(pp.sum()), n_unprec=int(pu.sum()), auroc_prec=r.auroc(one * pp, one * neg),
                    auroc_unprec=r.auroc(one * pu, one * neg), diff_ci983=ci(np.array(bs), 1 - 0.05 / 3).tolist())
    res[lab]["diff"] = res[lab]["auroc_prec"] - res[lab]["auroc_unprec"]
    print("H1", lab, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in res[lab].items()})
changed = precedent_matrix("")[pi, pj] & ~precedent_matrix_strict("")[pi, pj]
res["pairs_reclassified"] = int(changed.sum()); res["positives_reclassified"] = int((changed & y).sum())
print("pairs losing precedent under strict rule:", res["pairs_reclassified"], " of which STRING positives:", res["positives_reclassified"])
json.dump(res, open("results_posthoc_strict.json", "w"), indent=1, default=float)
