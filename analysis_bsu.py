"""PREREG_BSU.md: does the precedent effect replicate in B. subtilis with AlphaFold-Multimer?"""
import json
import os
from collections import defaultdict

import numpy as np
import pandas as pd

from metrics import Ranked, ci

D = r"C:\Users\bmens\NQ_local\af3-hitcall"
rng = np.random.default_rng(168)
ev5 = pd.read_excel(os.path.join(D, "oreilly", "MSB-19-e11544-s003.xlsx"), sheet_name="Dataset EV5")
ev5 = ev5[ev5["uniprot 1"] != ev5["uniprot 2"]].copy()
accs = sorted(set(ev5["uniprot 1"]) | set(ev5["uniprot 2"]))
ax = {a: k for k, a in enumerate(accs)}
n = len(accs)


def prec_for(tag, strict=False):
    hits = json.load(open(os.path.join(D, "data", f"bsu_hits_{tag}.json")))
    ent = defaultdict(lambda: defaultdict(set))
    for a, es in hits.items():
        for e in es:
            entry, en = e.split("_")
            ent[entry][a].add(en)
    pairs = set()
    for m in ent.values():
        ls = list(m)
        for x in range(len(ls)):
            for y in range(x + 1, len(ls)):
                ea, eb = m[ls[x]], m[ls[y]]
                if ((ea - eb) and (eb - ea)) if strict else len(ea | eb) >= 2:
                    pairs.add(frozenset((ls[x], ls[y])))
    return np.array([frozenset((a, b)) in pairs for a, b in zip(ev5["uniprot 1"], ev5["uniprot 2"])])


ii = ev5["uniprot 1"].map(ax).to_numpy()
jj = ev5["uniprot 2"].map(ax).to_numpy()
xl = ev5["crosslinking MS"].astype(bool).to_numpy()
comp = ev5["co-Frac MS"].astype(bool).to_numpy() & ~xl
iptm = ev5.iptm.to_numpy()
hit = iptm >= 0.5
out = {}
for tag, strict in [("pre", False), ("pre", True), ("any", False)]:
    f = os.path.join(D, "data", f"bsu_hits_{tag}.json")
    if not os.path.exists(f) or len(json.load(open(f))) < len(accs):
        print(tag, "search incomplete, skipped")
        continue
    P = prec_for(tag, strict)
    tag = tag + ("_strict" if strict else "")
    pp, pu = xl & P, xl & ~P
    rec = {"n_xl_prec": int(pp.sum()), "n_xl_unprec": int(pu.sum()),
           "recall_prec": float(hit[pp].mean()), "recall_unprec": float(hit[pu].mean()),
           "n_comp_prec": int((comp & P).sum()), "n_comp_unprec": int((comp & ~P).sum()),
           "comp_hit_rate_prec": float(hit[comp & P].mean()) if (comp & P).any() else None,
           "comp_hit_rate_unprec": float(hit[comp & ~P].mean())}
    rec["diff"] = rec["recall_prec"] - rec["recall_unprec"]
    bs = []
    for _ in range(2000):
        c = np.bincount(rng.integers(0, n, n), minlength=n).astype(float)
        w = c[ii] * c[jj]
        a, b = (w * pp).sum(), (w * pu).sum()
        if a and b:
            bs.append((w * pp * hit).sum() / a - (w * pu * hit).sum() / b)
    rec["diff_ci95"] = ci(np.array(bs), 0.95).tolist()
    # secondary: AUROC XL+ vs comparator within stratum
    r = Ranked(iptm)
    for lab, m in [("prec", P), ("unprec", ~P)]:
        pos, neg = (xl & m).astype(float), (comp & m).astype(float)
        rec[f"auroc_xl_vs_comp_{lab}"] = r.auroc(pos, neg) if pos.sum() and neg.sum() else None
    lo, hi = rec["diff_ci95"]
    if min(rec["n_xl_prec"], rec["n_xl_unprec"]) < 25:
        rec["verdict"] = "UNDERPOWERED"
    elif rec["diff"] >= 0.20 and lo > 0:
        rec["verdict"] = "REPLICATES"
    elif lo <= 0 <= hi:
        rec["verdict"] = "FAILS TO REPLICATE"
    else:
        rec["verdict"] = "PARTIAL"
    out[tag] = rec
    print(tag, json.dumps(rec, indent=1, default=float))
json.dump(out, open("results_bsu.json", "w"), indent=1, default=float)
