"""PREREG_LITJEV: L1 (co-mentioned pairs) and L2 (all pairs), confident vs low, never-solved human pairs."""
import json

import numpy as np

from metrics import ci

rng = np.random.default_rng(99)
r = [json.loads(l) for l in open(r"C:\Users\bmens\NQ_local\af3-hitcall\burke\litjev.jsonl")]
G = {g: [x for x in r if x["group"] == g] for g in ("confident", "low", "prec_ref")}


def rate(xs):
    return float(np.mean([x["best"] >= 0.8 for x in xs])) if xs else float("nan")


def diff_ci(a, b):
    ya = np.array([x["best"] >= 0.8 for x in a], float)
    yb = np.array([x["best"] >= 0.8 for x in b], float)
    bs = [rng.choice(ya, len(ya)).mean() - rng.choice(yb, len(yb)).mean() for _ in range(2000)]
    return ya.mean() - yb.mean(), ci(np.array(bs), 0.95).tolist()


res = {"n": {g: len(v) for g, v in G.items()},
       "co_mention_rate": {g: float(np.mean([x["n_abstracts"] > 0 for x in v])) if v else None for g, v in G.items()},
       "lit_direct_rate_all": {g: rate(v) for g, v in G.items()},
       "lit_direct_rate_comentioned": {g: rate([x for x in v if x["n_abstracts"] > 0]) for g, v in G.items()}}
cm = {g: [x for x in v if x["n_abstracts"] > 0] for g, v in G.items()}
d1, c1 = diff_ci(cm["confident"], cm["low"])
d2, c2 = diff_ci(G["confident"], G["low"])
res["L1_comentioned_conf_minus_low"] = {"diff": d1, "ci95": c1, "verdict": "SIGNAL" if c1[0] > 0 else "NO SIGNAL"}
res["L2_all_conf_minus_low"] = {"diff": d2, "ci95": c2, "verdict": "SIGNAL" if c2[0] > 0 else "NO SIGNAL"}
from collections import Counter
res["evidence_types_confident_direct"] = Counter(x["evidence"] for x in G["confident"] if x["best"] >= 0.8)
print(json.dumps(res, indent=1, default=float))
json.dump(res, open("results_litjev.json", "w"), indent=1, default=float)
