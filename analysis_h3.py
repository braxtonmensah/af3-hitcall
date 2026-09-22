"""Pre-registered H3: interface PAE (chain_pair_pae_min) vs size-corrected ipTM on the paper's
local pool-size experiment (MOESM8), plus D2 (sample-level: mean vs max vs single draw)."""
import ast
import json
import os
import sys
from collections import defaultdict

import numpy as np
import pandas as pd

from metrics import Ranked, ci

D = r"C:\Users\bmens\NQ_local\af3-hitcall"
REPS = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
LEVEL = 1 - 0.05 / 3
rng = np.random.default_rng(3)

prot = pd.read_csv(os.path.join(D, "data", "proteins.csv"))
acc2i = {a: i for i, a in enumerate(prot.accession)}
L = prot.length.to_numpy()
ST = np.load(os.path.join(D, "data", "string_exp.npy"))
n = len(prot)

m = pd.read_excel(os.path.join(D, "suppl", "44320_2026_189_MOESM8_ESM.xlsx"), sheet_name="mgen_pools")
m = m[m.group.notna()]


def size_expect(i, j):
    return -0.036255571 + 0.004470512 * np.sqrt(L[i] + L[j])


# collect per (group, pair) observations: list over pools of per-sample arrays
obs = defaultdict(lambda: {"iptm": [], "pae": []})
unmapped = set()
for _, r in m.iterrows():
    ids = [c.split(".")[0] for c in r.chain_ids.split("_")]
    ix = [acc2i.get(c) for c in ids]
    if any(v is None for v in ix):
        unmapped.update(c for c, v in zip(ids, ix) if v is None)
        continue
    ip = np.array([ast.literal_eval(r[f"model{k}_chain_pair_iptm"]) for k in range(5)], float)
    pa = np.array([ast.literal_eval(r[f"model{k}_chain_pair_pae_min"]) for k in range(5)], float)
    for a in range(len(ix)):
        for b in range(a + 1, len(ix)):
            i, j = sorted((ix[a], ix[b]))
            key = (r.group, i, j)
            # chain_pair_iptm is symmetric; pae_min is directional -> average both directions
            obs[key]["iptm"].append(ip[:, a, b])
            obs[key]["pae"].append((pa[:, a, b] + pa[:, b, a]) / 2)
print("unmapped chain ids:", sorted(unmapped)[:10], len(unmapped))

rows = []
for (g, i, j), v in obs.items():
    ip = np.stack(v["iptm"])  # pools x 5
    pa = np.stack(v["pae"])
    e = size_expect(i, j)
    rows.append(dict(group=g, i=i, j=j, y=ST[i, j] > 800, npool=len(ip),
                     I=ip.mean() - e, P=-pa.mean(),
                     I_max=ip.max(axis=1).mean() - e, I_s0=ip[:, 0].mean() - e,
                     P_max=-pa.min(axis=1).mean(), P_s0=-pa[:, 0].mean(),
                     I_raw=ip.mean()))
df = pd.DataFrame(rows)
print(df.groupby("group").agg(pairs=("y", "size"), pos=("y", "sum")))


def node_boot_diff(sub, a, b):
    """Paired node bootstrap of AUROC(a) - AUROC(b); pair weight c_i*c_j."""
    ra, rb = Ranked(sub[a].to_numpy()), Ranked(sub[b].to_numpy())
    y = sub.y.to_numpy()
    ii, jj = sub.i.to_numpy(), sub.j.to_numpy()
    out = []
    for _ in range(REPS):
        c = np.bincount(rng.integers(0, n, n), minlength=n).astype(float)
        w = c[ii] * c[jj]
        if (w * y).sum() == 0 or (w * ~y).sum() == 0:
            continue
        out.append(ra.auroc(w * y, w * ~y) - rb.auroc(w * y, w * ~y))
    return np.array(out)


res = {"groups": {}}
wins = 0
for g, sub in df.groupby("group"):
    one = np.ones(len(sub))
    y = sub.y.to_numpy()
    rec = {"pairs": len(sub), "pos": int(y.sum())}
    for s in ["I", "P", "I_max", "I_s0", "P_max", "P_s0", "I_raw"]:
        rr = Ranked(sub[s].to_numpy())
        rec[f"auroc_{s}"] = rr.auroc(one * y, one * ~y)
        rec[f"auprc_{s}"] = rr.auprc(one * y, one * ~y)
    rec["P_minus_I"] = rec["auroc_P"] - rec["auroc_I"]
    wins += rec["P_minus_I"] > 0
    res["groups"][g] = rec
    print(g, {k: round(v, 3) if isinstance(v, float) else v for k, v in rec.items()})

# pooled test: stack groups (a pair appearing in several groups contributes once per group)
bs = node_boot_diff(df, "P", "I")
one = np.ones(len(df))
y = df.y.to_numpy()
pooled = Ranked(df.P.to_numpy()).auroc(one * y, one * ~y) - Ranked(df.I.to_numpy()).auroc(one * y, one * ~y)
res["pooled_P_minus_I"] = pooled
res["pooled_ci"] = ci(bs, LEVEL).tolist()
res["wins"] = int(wins)
res["verdict"] = "CONFIRMED" if wins >= 4 and res["pooled_ci"][0] > 0 else "REJECTED"
print("H3", json.dumps({k: v for k, v in res.items() if k != "groups"}, indent=1))
json.dump(res, open("results_h3.json", "w"), indent=1, default=float)
df.to_csv(os.path.join(D, "data", "moesm8_pairs.csv"), index=False)
