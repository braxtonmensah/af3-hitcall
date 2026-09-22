"""PREREG_HUMAN.md: HH1 (recall by precedent) and HH2 (crosslink correctness of confident models)."""
import json

import numpy as np
import pandas as pd

from metrics import ci

rng = np.random.default_rng(2023)
d = pd.read_csv(r"C:\Users\bmens\NQ_local\af3-hitcall\burke\S1.csv", low_memory=False)
prots = pd.unique(pd.concat([d.id1, d.id2]))
px = {p: k for k, p in enumerate(prots)}
n = len(prots)
d["i"], d["j"] = d.id1.map(px), d.id2.map(px)
d["prec"] = d.int3D_model_structure.astype(int) == 1
d["ct"] = pd.to_numeric(d.crosstotal, errors="coerce").fillna(0)
d["c32"] = pd.to_numeric(d.cross32, errors="coerce").fillna(0)
out = {}


def boot(fn):
    res = []
    for _ in range(2000):
        c = np.bincount(rng.integers(0, n, n), minlength=n).astype(float)
        v = fn(c)
        if v is not None and np.isfinite(v):
            res.append(v)
    return np.array(res)


# HH1
h = d[d.Dataset.str.contains("HURI")].copy()
for thr in (0.23, 0.5):
    y = (h.pDockQ > thr).to_numpy()
    p = h.prec.to_numpy()
    ii, jj = h.i.to_numpy(), h.j.to_numpy()

    def f(c, y=y, p=p, ii=ii, jj=jj):
        w = c[ii] * c[jj]
        a, b = (w * p).sum(), (w * ~p).sum()
        return (w * p * y).sum() / a - (w * ~p * y).sum() / b if a and b else None

    rec = dict(n_prec=int(p.sum()), n_none=int((~p).sum()), rate_prec=float(y[p].mean()), rate_none=float(y[~p].mean()))
    rec["diff"] = rec["rate_prec"] - rec["rate_none"]
    rec["diff_ci95"] = ci(boot(f), 0.95).tolist()
    lo, hi = rec["diff_ci95"]
    rec["verdict"] = "REPLICATES" if rec["diff"] >= 0.20 and lo > 0 else ("FAILS" if lo <= 0 <= hi else "PARTIAL")
    out[f"HH1_pdockq>{thr}"] = rec
    print(f"HH1 pDockQ>{thr}", json.dumps(rec, default=float))

# HH2
x = d[d.ct >= 1].copy()
x["sat"] = x.c32 / x.ct
for lab, m in [("confident", x.pDockQ > 0.23), ("low_confidence", x.pDockQ <= 0.23)]:
    s = x[m]
    p, sat = s.prec.to_numpy(), s.sat.to_numpy()
    ii, jj = s.i.to_numpy(), s.j.to_numpy()

    def g(c, p=p, sat=sat, ii=ii, jj=jj):
        w = c[ii] * c[jj]
        a, b = (w * p).sum(), (w * ~p).sum()
        return (w * p * sat).sum() / a - (w * ~p * sat).sum() / b if a and b else None

    rec = dict(n_prec=int(p.sum()), n_none=int((~p).sum()),
               sat_prec=float(sat[p].mean()) if p.any() else None, sat_none=float(sat[~p].mean()) if (~p).any() else None)
    if p.any() and (~p).any():
        rec["diff"] = rec["sat_prec"] - rec["sat_none"]
        rec["diff_ci95"] = ci(boot(g), 0.95).tolist()
        lo, hi = rec["diff_ci95"]
        if min(rec["n_prec"], rec["n_none"]) < 15:
            rec["verdict"] = "UNDERPOWERED"
        elif lo >= -0.15 and hi <= 0.15:
            rec["verdict"] = "EQUIVALENT"
        elif lo > 0:
            rec["verdict"] = "PRECEDENT BETTER"
        else:
            rec["verdict"] = "INCONCLUSIVE"
    out[f"HH2_{lab}"] = rec
    print(f"HH2 {lab}", json.dumps(rec, default=float))
json.dump(out, open("results_human.json", "w"), indent=1, default=float)
