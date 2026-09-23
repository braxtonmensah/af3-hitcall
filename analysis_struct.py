"""PREREG_STRUCT: do structure-level scores (ipSAE, LIS, trunk contact prob, sample reproducibility)
rescue never-solved interactions? Scores per pair are means over its pools in the analysis set."""
import glob
import json
import os
from collections import defaultdict
from itertools import combinations

import numpy as np
import pandas as pd

from analysis_h1_h2_lib import precedent_matrix_strict
from metrics import Ranked, ci

ROOT = r"C:\Users\bmens\NQ_local\af3-hitcall"
rng = np.random.default_rng(20260923)
NB = 2000
P = pd.read_csv(os.path.join(ROOT, "data", "proteins.csv"))
ix = {l: k for k, l in enumerate(P.locus_tag)}
L = P.aa_sequence.str.rstrip("*").str.len().to_numpy()
n = len(P)
ST = np.load(os.path.join(ROOT, "data", "string_exp.npy"))
DRY = os.environ.get("DRYRUN") == "1"  # code test only: labels permuted, results meaningless
if DRY:
    perm = np.random.default_rng(0).permutation(n)
    ST = ST[perm][:, perm]
    NB = 20
PRE = precedent_matrix_strict("") | precedent_matrix_strict("_id0")
s0pp = pd.read_csv(os.path.join(ROOT, "data", "s0_per_pool.csv")).set_index(["pool", "i", "j"]).s0

acc = defaultdict(lambda: defaultdict(list))  # (i, j) -> score -> per-pool values
files = sorted(glob.glob(os.path.join(ROOT, "structs", "*.json")))
for f in files:
    F = json.load(open(f))
    loci = F["loci"]
    if any(l is None for l in loci):
        continue
    ch = [chr(65 + k) for k in range(len(loci))]
    S = [F["samples"][k] for k in "01234"]
    for a, b in combinations(range(len(loci)), 2):
        key = ch[a] + ch[b]
        i, j = sorted((ix[loci[a]], ix[loci[b]]))
        A = acc[(i, j)]
        A["S0"].append(s0pp[(F["pool"], i, j)])
        A["IPSAE"].append(np.mean([s["pae"][key]["ipsae"] for s in S]))
        A["LIS"].append(np.mean([s["pae"][key]["lis"] for s in S]))
        A["CP"].append(F["cp"][key][0])
        sets = []
        for s in S:
            fa, fb = s["iface"].get(key, [[], []])
            sets.append({("a", r) for r in fa} | {("b", r) for r in fb})
        jac = [len(x & y) / len(x | y) if (x and y) else 0.0 for x, y in combinations(sets, 2)]
        A["REP"].append(float(np.mean(jac)))

pairs = sorted(acc)
pi = np.array([p[0] for p in pairs])
pj = np.array([p[1] for p in pairs])
names = ["S0", "IPSAE", "LIS", "CP", "REP"]
raw = {k: np.array([np.mean(acc[p][k]) for p in pairs]) for k in names}
size = np.sqrt(L[pi] + L[pj])
X = np.c_[np.ones(len(size)), size]
sc = {"S0": raw["S0"]}
for k in names[1:]:
    beta = np.linalg.lstsq(X, raw[k], rcond=None)[0]  # label-free size correction, as the paper did for ipTM
    sc[k] = raw[k] - X @ beta
    sc[k + "_raw"] = raw[k]

y = ST[pi, pj] > 800
pre = PRE[pi, pj]
neg = (~y).astype(float)
never = (y & ~pre).astype(float)
prec = (y & pre).astype(float)
R = {k: Ranked(v) for k, v in sc.items()}
res = {"n_pools": len(files), "n_pairs": len(pairs), "n_neg": int((~y).sum()), "n_never": int(never.sum()), "n_prec": int(prec.sum()),
       "size_corr_beta": {}, "auroc": {}}
for k, r in R.items():
    res["auroc"][k] = {"never": r.auroc(never, neg), "prec": r.auroc(prec, neg)}


def boot(stat):
    pt = stat(np.ones(n))
    bs = np.array([stat(np.bincount(rng.integers(0, n, n), minlength=n).astype(float)) for _ in range(NB)])
    bs = bs[np.isfinite(bs)]
    return pt, bs


prim = {}
for k in ["IPSAE", "LIS", "CP", "REP"]:
    def st(w, k=k):
        ww = w[pi] * w[pj]
        return R[k].auroc(ww * never, ww * neg) - R["S0"].auroc(ww * never, ww * neg)
    pt, bs = boot(st)
    lo, hi = ci(bs, 0.9875).tolist()
    prim[k] = {"diff": pt, "ci98.75": [lo, hi], "verdict": "RESCUE" if lo > 0 else "NO RESCUE"}
res["primary"] = prim
best = max(prim, key=lambda k: prim[k]["diff"])


def gapdiff(w):
    ww = w[pi] * w[pj]
    g = lambda r: r.auroc(ww * prec, ww * neg) - r.auroc(ww * never, ww * neg)
    return g(R["S0"]) - g(R[best])


pt, bs = boot(gapdiff)
res["secondary_gap_closure"] = {"score": best, "gap_S0_minus_gap_score": pt, "ci95": ci(bs, 0.95).tolist()}
print(json.dumps(res, indent=1, default=float))
json.dump(res, open("results_struct_DRYRUN.json" if DRY else "results_struct.json", "w"), indent=1, default=float)
