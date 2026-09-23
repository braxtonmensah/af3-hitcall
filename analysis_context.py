"""PREREG_CONTEXT: pooled AF3 as a competition assay. T1-T4 plus sensitivity, exactly as registered."""
import json
import os
import sys
from collections import defaultdict

import numpy as np
import pandas as pd

from analysis_h1_h2_lib import precedent_matrix_strict
from metrics import Ranked, ci

D = r"C:\Users\bmens\NQ_local\af3-hitcall\data"
rng = np.random.default_rng(20260922)
NB = 2000
d = pd.read_csv(os.path.join(D, "s0_per_pool.csv"))
S0 = np.load(os.path.join(D, "S0.npy"))
ST = np.load(os.path.join(D, "string_exp.npy"))
n = S0.shape[0]
POS = ST > 800
PRE = precedent_matrix_strict("") | precedent_matrix_strict("_id0")

# pair totals over pools, for the exogenous (other-pool) competitor definition
tot = defaultdict(lambda: [0.0, 0])
for i, j, s in zip(d.i, d.j, d.s0):
    tot[(i, j)][0] += s
    tot[(i, j)][1] += 1


def other_mean(a, b, s_here):
    a, b = min(a, b), max(a, b)
    t, c = tot[(a, b)]
    return (t - s_here) / (c - 1) if c > 1 else np.nan


def contexts(tau, exo=False):
    """one row per (pair, pool): ctx in clean/compete/bridge, plus remote/quiet flags"""
    out = []
    for p, g in d.groupby("pool"):
        s = {}
        for i, j, x in zip(g.i, g.j, g.s0):
            s[(i, j)] = s[(j, i)] = x
        mem = set(g.i) | set(g.j)
        strong = [(i, j) for i, j, x in zip(g.i, g.j, g.s0) if x >= tau]
        for i, j, x in zip(g.i, g.j, g.s0):
            br = cp = False
            undefined = False
            for X in mem - {i, j}:
                if exo:
                    a, b = other_mean(i, X, s[(i, X)]), other_mean(j, X, s[(j, X)])
                    if (np.isnan(a) and s[(i, X)] >= tau) or (np.isnan(b) and s[(j, X)] >= tau):
                        undefined = True  # a same-pool competitor with no other pool to confirm it
                    a, b = np.nan_to_num(a), np.nan_to_num(b)
                else:
                    a, b = s[(i, X)], s[(j, X)]
                if a >= tau and b >= tau:
                    br = True
                elif max(a, b) >= tau:
                    cp = True
            ctx = "bridge" if br else "compete" if cp else "undefined" if undefined else "clean"
            remote = any(u not in (i, j) and v not in (i, j) for u, v in strong)
            out.append((i, j, p, x, ctx, remote))
    return pd.DataFrame(out, columns=["i", "j", "pool", "s0", "ctx", "remote"])


def paired(c, a_mask, b_mask):
    """per pair: mean S0 over pools in a_mask minus over pools in b_mask (pairs having both)"""
    A = c[a_mask].groupby(["i", "j"]).s0.mean()
    B = c[b_mask].groupby(["i", "j"]).s0.mean()
    x = (A - B).dropna()
    ij = np.array(x.index.tolist())
    return ij[:, 0], ij[:, 1], x.to_numpy()


def wmean(i, j, v, cnt):
    w = cnt[i] * cnt[j]
    return (w * v).sum() / w.sum() if w.sum() > 0 else np.nan


def boot(stat):
    pt = stat(np.ones(n))
    bs = [stat(np.bincount(rng.integers(0, n, n), minlength=n).astype(float)) for _ in range(NB)]
    bs = np.array(bs)
    return {"est": float(pt), "ci95": ci(bs[np.isfinite(bs)], 0.95).tolist()}


def delta_tests(c):
    i, j, v = paired(c, c.ctx == "compete", c.ctx == "clean")
    pos, pre = POS[i, j], PRE[i, j]
    g = {"pos": pos, "neg": ~pos, "never": pos & ~pre, "prec": pos & pre}
    r = {"n_pairs": {k: int(m.sum()) for k, m in g.items()}}
    for k, m in g.items():
        r[f"delta_{k}"] = boot(lambda w, m=m: wmean(i[m], j[m], v[m], w))
    r["DiD_pos_minus_neg"] = boot(lambda w: wmean(i[pos], j[pos], v[pos], w) - wmean(i[~pos], j[~pos], v[~pos], w))
    return r, (i, j, v)


res = {}
c = contexts(0.2)
res["context_counts"] = c.ctx.value_counts().to_dict()
res["bridge_rows_positive"] = int(POS[c.i[c.ctx == "bridge"], c.j[c.ctx == "bridge"]].sum())
t, (ci_, cj_, cv_) = delta_tests(c)
res["T1_T2"] = t
res["T1_verdict"] = "COMPETITION" if t["delta_pos"]["ci95"][1] < 0 and t["DiD_pos_minus_neg"]["ci95"][1] < 0 else "NOT SHOWN"
res["T2_verdict"] = "NEVER-SOLVED MASKED" if t["delta_never"]["ci95"][1] < 0 else "NOT SHOWN"

# T3: remote-but-clean vs quiet, positives
clean = c.ctx == "clean"
ri, rj, rv = paired(c, clean & c.remote, clean & ~c.remote)
rpos = POS[ri, rj]
pp = POS[ci_, cj_]
res["T3"] = {"n_pos_remote": int(rpos.sum()),
             "delta_remote_pos": boot(lambda w: wmean(ri[rpos], rj[rpos], rv[rpos], w)),
             "compete_minus_remote_pos": boot(lambda w: wmean(ci_[pp], cj_[pp], cv_[pp], w) - wmean(ri[rpos], rj[rpos], rv[rpos], w))}
res["T3_verdict"] = "COMPETITION-SPECIFIC" if res["T3"]["compete_minus_remote_pos"]["ci95"][1] < 0 else "NOT SHOWN"

# T4: context-aware score
cm = c[clean].groupby(["i", "j"]).s0.mean()
Sctx = S0.copy()
for (a, b), x in cm.items():
    Sctx[a, b] = Sctx[b, a] = x
pi, pj = np.triu_indices(n, 1)
y = POS[pi, pj]
neg = (~y).astype(float)
R0, R1 = Ranked(S0[pi, pj]), Ranked(Sctx[pi, pj])
res["T4"] = {"n_pairs_changed": int((Sctx[pi, pj] != S0[pi, pj]).sum())}
for lab, m in [("never_solved", y & ~PRE[pi, pj]), ("precedented", y & PRE[pi, pj])]:
    mm = m.astype(float)

    def st(w, mm=mm):
        ww = w[pi] * w[pj]
        return R1.auroc(ww * mm, ww * neg) - R0.auroc(ww * mm, ww * neg)
    res["T4"][lab] = {"auroc_S0": R0.auroc(mm, neg), "auroc_Sctx": R1.auroc(mm, neg), "diff": boot(st)}
res["T4_verdict"] = "RESCUE" if res["T4"]["never_solved"]["diff"]["ci95"][0] > 0 else "NOT SHOWN"

# sensitivity
res["sens_tau0.3"], _ = delta_tests(contexts(0.3))
res["sens_exogenous_tau0.2"], _ = delta_tests(contexts(0.2, exo=True))
print(json.dumps(res, indent=1, default=float))
json.dump(res, open("results_context.json", "w"), indent=1, default=float)
