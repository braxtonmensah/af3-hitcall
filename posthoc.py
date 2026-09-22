"""POST HOC (not pre-registered; written after H1-H3 results were seen).

PH1  Is H1 about the co-complex (template / training recall) or about the proteins being
     structurally known at all? Split positives by: co-complex precedent / both proteins have a
     PDB homolog but never together / at least one protein has no PDB homolog.
PH2  Pool-size experiment re-analysed on matched pairs. Each pool size in the paper's Fig. 3 ran on
     a disjoint ~95-protein section; compare each condition with the genome-wide screen on the
     SAME pairs, so section difficulty cancels.
"""
import json
import os

import numpy as np
import pandas as pd

from metrics import Ranked, ci
from analysis_h1_h2_lib import precedent_matrix, has_homolog

D = r"C:\Users\bmens\NQ_local\af3-hitcall\data"
REPS = 2000
rng = np.random.default_rng(11)
S0 = np.load(os.path.join(D, "S0.npy"))
ST = np.load(os.path.join(D, "string_exp.npy"))
n = S0.shape[0]
pi, pj = np.triu_indices(n, 1)
y = ST[pi, pj] > 800
neg = ~y
s0 = S0[pi, pj]
r0 = Ranked(s0)
res = {}


def boot(fn):
    out = []
    for _ in range(REPS):
        c = np.bincount(rng.integers(0, n, n), minlength=n).astype(float)
        out.append(fn(c))
    return np.array(out)


# ---------------- PH1 ----------------
for tag in ["", "_id0"]:
    P = precedent_matrix(tag)[pi, pj]
    h = has_homolog(tag)
    both = h[pi] & h[pj]
    strata = {"co_complex": y & P, "both_known_not_together": y & ~P & both, "not_both_known": y & ~P & ~both}
    one = np.ones(len(s0))
    rec = {}
    for k, m in strata.items():
        rec[k] = {"n": int(m.sum()), "auroc": r0.auroc(one * m, one * neg), "auprc_vs_base": None}
    # key contrast: co_complex minus both_known_not_together (same "known protein" status)
    a, b = strata["co_complex"], strata["both_known_not_together"]
    bs = boot(lambda c: r0.auroc(c[pi] * c[pj] * a, c[pi] * c[pj] * neg) - r0.auroc(c[pi] * c[pj] * b, c[pi] * c[pj] * neg))
    rec["co_minus_bothknown"] = rec["co_complex"]["auroc"] - rec["both_known_not_together"]["auroc"]
    rec["co_minus_bothknown_ci95"] = ci(bs, 0.95).tolist()
    b2 = strata["not_both_known"]
    bs2 = boot(lambda c: r0.auroc(c[pi] * c[pj] * b, c[pi] * c[pj] * neg) - r0.auroc(c[pi] * c[pj] * b2, c[pi] * c[pj] * neg))
    rec["bothknown_minus_notknown"] = rec["both_known_not_together"]["auroc"] - rec["not_both_known"]["auroc"]
    rec["bothknown_minus_notknown_ci95"] = ci(bs2, 0.95).tolist()
    # negatives too: does AF3 score precedented NON-interactors higher?
    rec["neg_coComplex_vs_neg_bothknown_auroc"] = r0.auroc(one * (neg & P), one * (neg & ~P & both))
    res[f"PH1{tag or '_primary'}"] = rec
    print("PH1", tag or "primary", json.dumps(rec, indent=1, default=float))

# ---------------- PH2 ----------------
df = pd.read_csv(os.path.join(D, "moesm8_pairs.csv"))
ph2 = {}
deltas = {}
for g, sub in df.groupby("group"):
    ii, jj, yy = sub.i.to_numpy(), sub.j.to_numpy(), sub.y.to_numpy()
    rc, rg = Ranked(sub.I.to_numpy()), Ranked(S0[ii, jj])
    one = np.ones(len(sub))
    d = rc.auroc(one * yy, one * ~yy) - rg.auroc(one * yy, one * ~yy)

    def f(c, rc=rc, rg=rg, ii=ii, jj=jj, yy=yy):
        w = c[ii] * c[jj]
        if (w * yy).sum() == 0:
            return np.nan
        return rc.auroc(w * yy, w * ~yy) - rg.auroc(w * yy, w * ~yy)

    bs = boot(f)
    deltas[g] = bs
    ph2[g] = {"auroc_condition": rc.auroc(one * yy, one * ~yy), "auroc_genomewide_same_pairs": rg.auroc(one * yy, one * ~yy),
              "delta": d, "delta_ci95": ci(bs[np.isfinite(bs)], 0.95).tolist(), "pos": int(yy.sum())}
# sections are disjoint, so their bootstraps are independent: difference of deltas
dd = deltas["pools_5k"] - deltas["pools_4k"]
ph2["delta5k_minus_delta4k"] = ph2["pools_5k"]["delta"] - ph2["pools_4k"]["delta"]
ph2["delta5k_minus_delta4k_ci95"] = ci(dd[np.isfinite(dd)], 0.95).tolist()
dd3 = deltas["pools_4k"] - deltas["pools_3k"]
ph2["delta4k_minus_delta3k"] = ph2["pools_4k"]["delta"] - ph2["pools_3k"]["delta"]
ph2["delta4k_minus_delta3k_ci95"] = ci(dd3[np.isfinite(dd3)], 0.95).tolist()
res["PH2"] = ph2
print("PH2", json.dumps(ph2, indent=1, default=float))
json.dump(res, open("results_posthoc.json", "w"), indent=1, default=float)
