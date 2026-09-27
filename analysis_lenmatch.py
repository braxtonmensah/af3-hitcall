"""LENMATCH (PREREG_LENMATCH.md): is the H1 precedent gap a residual length artifact?

Stratifies on summed pair length, recomputes the precedented-minus-unprecedented AUROC gap
within strata, and bootstraps over proteins. Decision rule fixed in PREREG_LENMATCH.md.
"""
import json
import os
import sys
from collections import defaultdict

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from metrics import Ranked, ci

D = r"C:\Users\bmens\NQ_local\af3-hitcall\data"
REPS = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
MIN_UNPREC = 20
rng = np.random.default_rng(20260926)

S0 = np.load(os.path.join(D, "S0.npy"))
ST = np.load(os.path.join(D, "string_exp.npy"))
prot = pd.read_csv(os.path.join(D, "proteins.csv"))
loci = list(prot.locus_tag)
lens = prot.length.to_numpy(float)
n = len(loci)
pi, pj = np.triu_indices(n, 1)
s0 = S0[pi, pj]
y800 = ST[pi, pj] > 800
neg_all = ~y800
L = lens[pi] + lens[pj]


def precedent(tag=""):
    hits = json.load(open(os.path.join(D, f"pdb_hits{tag}.json")))
    by_entry = defaultdict(lambda: defaultdict(set))
    for l, ents in hits.items():
        for e in ents:
            entry, ent = e.split("_")
            by_entry[entry][l].add(ent)
    P = np.zeros((n, n), bool)
    ix = {l: i for i, l in enumerate(loci)}
    for entry, m in by_entry.items():
        ls = list(m)
        for a in range(len(ls)):
            for b in range(a + 1, len(ls)):
                if len(m[ls[a]] | m[ls[b]]) >= 2:
                    i, j = ix[ls[a]], ix[ls[b]]
                    P[i, j] = P[j, i] = True
    return P[pi, pj]


prec = precedent()
pp = y800 & prec        # precedented positives
pu = y800 & ~prec       # never-solved positives

# strata: quintiles of L over ALL pairs, cut points fixed before any AUROC
cuts = np.quantile(L, [0.2, 0.4, 0.6, 0.8])
strat = np.digitize(L, cuts)
r = Ranked(s0)
one = np.ones(len(s0))

keep, per_stratum = [], []
for s in range(5):
    m = strat == s
    n_p, n_u = int((pp & m).sum()), int((pu & m).sum())
    row = {"stratum": s, "n_prec_pos": n_p, "n_unprec_pos": n_u,
           "n_neg": int((neg_all & m).sum()),
           "L_range": [float(L[m].min()), float(L[m].max())]}
    if n_u >= MIN_UNPREC and n_p > 0:
        a_p = r.auroc(one * (pp & m), one * (neg_all & m))
        a_u = r.auroc(one * (pu & m), one * (neg_all & m))
        row.update({"auroc_prec": a_p, "auroc_unprec": a_u, "gap": a_p - a_u, "used": True})
        keep.append(s)
    else:
        row["used"] = False
        row["dropped_reason"] = f"unprecedented positives {n_u} < {MIN_UNPREC}"
    per_stratum.append(row)


def stratified_gap(w):
    num = den = 0.0
    for s in keep:
        m = strat == s
        wp_p, wp_u, wn = w * (pp & m), w * (pu & m), w * (neg_all & m)
        if wp_p.sum() <= 0 or wp_u.sum() <= 0 or wn.sum() <= 0:
            continue
        g = r.auroc(wp_p, wn) - r.auroc(wp_u, wn)
        wt = wp_p.sum() + wp_u.sum()
        num += wt * g
        den += wt
    return num / den if den > 0 else np.nan


point_gap = stratified_gap(one)
boot = np.array([stratified_gap(c[pi] * c[pj]) for c in
                 (np.bincount(rng.integers(0, n, n), minlength=n).astype(float)
                  for _ in range(REPS))])
boot = boot[~np.isnan(boot)]
lo, hi = ci(boot, 0.95)

if lo > 0 and point_gap >= 0.05:
    verdict = "CONFIRMED: the H1 gap is not explained by length"
elif lo <= 0 <= hi:
    verdict = "REJECTED: gap not separable from length"
else:
    verdict = "BETWEEN: direction supported, size below threshold"

out = {
    "unstratified_gap_for_reference": float(
        r.auroc(one * pp, one * neg_all) - r.auroc(one * pu, one * neg_all)),
    "length_descriptives": {
        "median_L_precedented_pos": float(np.median(L[pp])),
        "iqr_L_precedented_pos": [float(np.quantile(L[pp], .25)), float(np.quantile(L[pp], .75))],
        "median_L_unprecedented_pos": float(np.median(L[pu])),
        "iqr_L_unprecedented_pos": [float(np.quantile(L[pu], .25)), float(np.quantile(L[pu], .75))],
        "spearman_L_vs_S0_all_pairs": float(spearmanr(L, s0).statistic),
        "spearman_L_vs_S0_positives_only": float(spearmanr(L[y800], s0[y800]).statistic),
    },
    "per_stratum": per_stratum,
    "strata_used": keep,
    "strata_dropped": [s for s in range(5) if s not in keep],
    "stratified_gap": float(point_gap),
    "ci95": [float(lo), float(hi)],
    "n_boot_valid": int(len(boot)),
    "verdict": verdict,
}
print(json.dumps(out, indent=1))
json.dump(out, open("results_lenmatch.json", "w"), indent=1)
