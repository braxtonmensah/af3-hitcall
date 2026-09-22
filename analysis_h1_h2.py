"""Pre-registered H1 (structural-precedent inflation) and H2 (per-protein null), PREREG.md."""
import json
import os
import sys
from collections import defaultdict

import numpy as np
import pandas as pd

from metrics import Ranked, ci, node_weights, per_bait

D = r"C:\Users\bmens\NQ_local\af3-hitcall\data"
REPS = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
LEVEL = 1 - 0.05 / 3  # Bonferroni over three primary tests
rng = np.random.default_rng(20260922)

S0 = np.load(os.path.join(D, "S0.npy"))
ST = np.load(os.path.join(D, "string_exp.npy"))
prot = pd.read_csv(os.path.join(D, "proteins.csv"))
loci = list(prot.locus_tag)
n = len(loci)
pi, pj = np.triu_indices(n, 1)
y800 = ST[pi, pj] > 800
y999 = ST[pi, pj] == 999
neg_all = ~y800
neg_zero = ST[pi, pj] == 0
out = {}


def point(score, ypos, yneg):
    r = Ranked(score)
    w = np.ones(len(score))
    return r.auroc(w * ypos, w * yneg), r.auprc(w * ypos, w * yneg)


# ---------- reproduction of the paper ----------
s0 = S0[pi, pj]
out["repro"] = {
    "S0_auroc_800": point(s0, y800, ~y800)[0],
    "S0_auroc_999": point(s0, y999, ~y999)[0],
    "S0_auprc_800": point(s0, y800, ~y800)[1],
    "base_rate_800": float(y800.mean()),
}
print("reproduction", out["repro"])


# ---------- H2 score ----------
def row_z(S):
    M = S.copy()
    med = np.nanmedian(M, axis=1)
    mad = 1.4826 * np.nanmedian(np.abs(M - med[:, None]), axis=1)
    mad = np.maximum(mad, 0.25 * np.median(mad))
    return (M - med[:, None]) / mad[:, None]


Z = row_z(S0)
S2 = (Z + Z.T) / 2
s2 = S2[pi, pj]


# ---------- H1 precedent ----------
def precedent(tag):
    hits = json.load(open(os.path.join(D, f"pdb_hits{tag}.json")))
    by_entry = defaultdict(lambda: defaultdict(set))  # entry -> locus -> entities
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
                ea, eb = m[ls[a]], m[ls[b]]
                # distinct entities: some a-entity differs from some b-entity
                if len(ea | eb) >= 2:
                    i, j = ix[ls[a]], ix[ls[b]]
                    P[i, j] = P[j, i] = True
    return P[pi, pj]


def h1(prec, label):
    pp = y800 & prec
    pu = y800 & ~prec
    rows = {"n_pos_precedented": int(pp.sum()), "n_pos_unprecedented": int(pu.sum()),
            "n_neg_precedented": int((neg_all & prec).sum())}
    r = Ranked(s0)
    one = np.ones(len(s0))
    for nm, neg in [("negall", neg_all), ("negzero", neg_zero)]:
        a_p = r.auroc(one * pp, one * neg)
        a_u = r.auroc(one * pu, one * neg)
        rows[f"auroc_prec_{nm}"] = a_p
        rows[f"auroc_unprec_{nm}"] = a_u
        rows[f"diff_{nm}"] = a_p - a_u
    # also: do precedented NEGATIVES score higher than unprecedented negatives? (memorised co-occurrence)
    rows["auroc_negprec_vs_negunprec"] = r.auroc(one * (neg_all & prec), one * (neg_all & ~prec))
    bs = []
    for w in node_weights(n, pi, pj, rng, REPS):
        bs.append(r.auroc(w * pp, w * neg_all) - r.auroc(w * pu, w * neg_all))
    bs = np.array(bs)
    rows["diff_ci"] = ci(bs, LEVEL).tolist()
    d = rows["diff_negall"]
    lo, hi = rows["diff_ci"]
    rows["verdict"] = ("CONFIRMED" if d >= 0.10 and lo > 0 else
                       "REJECTED" if lo <= 0 <= hi else "DIRECTION SUPPORTED, BELOW THRESHOLD")
    print(label, json.dumps(rows, indent=1))
    return rows


out["H1_primary"] = h1(precedent(""), "H1 primary (id>=0.25)")
out["H1_sensitivity"] = h1(precedent("_id0"), "H1 sensitivity (E only)")

# ---------- H2 test ----------
r0, r2 = Ranked(s0), Ranked(s2)
one = np.ones(len(s0))
h2 = {
    "auprc_S0": r0.auprc(one * y800, one * ~y800), "auprc_S2": r2.auprc(one * y800, one * ~y800),
    "auroc_S0": r0.auroc(one * y800, one * ~y800), "auroc_S2": r2.auroc(one * y800, one * ~y800),
    "auprc999_S0": r0.auprc(one * y999, one * ~y999), "auprc999_S2": r2.auprc(one * y999, one * ~y999),
}
bs = np.array([r2.auprc(w * y800, w * ~y800) - r0.auprc(w * y800, w * ~y800)
               for w in node_weights(n, pi, pj, rng, REPS)])
h2["auprc_diff"] = h2["auprc_S2"] - h2["auprc_S0"]
h2["auprc_diff_ci"] = ci(bs, LEVEL).tolist()
POS = ST > 800
pb0, pb2 = per_bait(S0, POS), per_bait(S2, POS)
h2["n_baits"] = len(pb0)
for k, nm in [(1, "recall5"), (2, "prec5"), (3, "mrr")]:
    h2[f"{nm}_S0"], h2[f"{nm}_S2"] = pb0[:, k].mean(), pb2[:, k].mean()
    d = pb2[:, k] - pb0[:, k]
    bb = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(REPS)]
    h2[f"{nm}_diff_ci"] = ci(np.array(bb), LEVEL).tolist()
lo = h2["auprc_diff_ci"][0]
h2["verdict"] = "CONFIRMED" if lo > 0 and h2["recall5_S2"] >= h2["recall5_S0"] else "REJECTED"
print("H2", json.dumps(h2, indent=1))
out["H2"] = h2

json.dump(out, open("results_h1_h2.json", "w"), indent=1, default=float)
