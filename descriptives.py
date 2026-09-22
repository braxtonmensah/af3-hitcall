"""Pre-registered descriptives D1 (bait-level FDR) and D2 (sample-level), PREREG.md.
D1 deviation, stated up front: a per-bait empirical p over 475 partners has resolution 1/475, so
Benjamini-Hochberg at 10% can never reject anything (the smallest p, 1/475, exceeds 0.1/475). The
null is therefore the POOLED distribution of row z-scores over all baits (226k values, including the
~2% true positives, which makes it conservative). z uses the H2 row-robust scaling; p = share of
pooled z >= z_ij. BH is then applied within each bait."""
import json, os
import numpy as np, pandas as pd
from analysis_h1_h2_lib import precedent_matrix

D = r"C:\Users\bmens\NQ_local\af3-hitcall\data"
S0 = np.load(os.path.join(D, "S0.npy")); ST = np.load(os.path.join(D, "string_exp.npy"))
n = S0.shape[0]; POS = ST > 800
PRE = precedent_matrix("") | precedent_matrix("_id0")
med = np.nanmedian(S0, 1); mad = 1.4826 * np.nanmedian(np.abs(S0 - med[:, None]), 1)
mad = np.maximum(mad, 0.25 * np.median(mad))
Z = (S0 - med[:, None]) / mad[:, None]
pool = np.sort(Z[~np.eye(n, dtype=bool)])
rows = []
for i in range(n):
    m = np.arange(n) != i
    z = Z[i, m]
    p = 1 - np.searchsorted(pool, z, side="left") / len(pool)
    o = np.argsort(p); k = np.arange(1, len(p) + 1)
    thr = (p[o] <= 0.10 * k / len(p))
    nh = k[thr].max() if thr.any() else 0
    hits = o[:nh]
    y = POS[i, m][hits]; pr = PRE[i, m][hits]
    rows.append(dict(bait=i, hits=nh, true=int(y.sum()), prec_hits=int(pr.sum()),
                     true_unprec=int((y & ~pr).sum()), npos=int(POS[i, m].sum())))
d = pd.DataFrame(rows)
tot = d.hits.sum()
res = {"D1": {"baits_with_hits": int((d.hits > 0).sum()), "total_hits": int(tot),
              "median_hits_per_bait_with_hits": float(d.hits[d.hits > 0].median()),
              "share_hits_STRING_pos": float(d.true.sum() / tot),
              "share_hits_precedented": float(d.prec_hits.sum() / tot),
              "share_unprecedented_hits_STRING_pos": float(d.true_unprec.sum() / max(1, tot - d.prec_hits.sum())),
              "share_precedented_hits_STRING_pos": float((d.true.sum() - d.true_unprec.sum()) / max(1, d.prec_hits.sum())),
              "baits_with_any_pos": int((d.npos > 0).sum()),
              "baits_with_pos_and_a_true_hit": int(((d.npos > 0) & (d.true > 0)).sum())}}
print(json.dumps(res["D1"], indent=1))

# D2: sample-level, MOESM8 local runs (5 diffusion samples per job)
from metrics import Ranked
df = pd.read_csv(os.path.join(D, "moesm8_pairs.csv"))
d2 = {}
for g, s in df.groupby("group"):
    y = s.y.to_numpy(); one = np.ones(len(s))
    d2[g] = {k: round(Ranked(s[k].to_numpy()).auroc(one * y, one * ~y), 4) for k in ["I", "I_max", "I_s0"]}
res["D2"] = d2
print("D2 AUROC by aggregation (I=mean of 5 samples, I_max=best sample, I_s0=sample 0 only):")
print(pd.DataFrame(d2).T.to_string())
json.dump(res, open("results_descriptives.json", "w"), indent=1, default=float)
