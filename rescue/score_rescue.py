"""PREREG_RESCUE scorer. Usage: python score_rescue.py <folder with fold_rescue_*.zip or unzipped folders>
Chains A, B are the pair (full UniProt sequences, so residue k -> position k)."""
import glob
import io
import json
import os
import re
import sys
import zipfile
from math import comb

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
FU = r"C:\Users\bmens\NQ_local\af3-hitcall\future"
R = pd.read_csv(os.path.join(HERE, "rescue_pairs.csv"))
P = pd.read_csv(os.path.join(FU, "pairs.csv")).set_index("uid")


def files(root):
    for z in glob.glob(os.path.join(root, "**", "*.zip"), recursive=True):
        with zipfile.ZipFile(z) as f:
            for m in f.namelist():
                yield os.path.basename(m), f.read(m)
    for pth in glob.glob(os.path.join(root, "**", "fold_rescue_*"), recursive=True):
        if os.path.isfile(pth):
            yield os.path.basename(pth), open(pth, "rb").read()


def ab_iface(cif):
    cols, pts = [], {"A": {}, "B": {}}
    for line in cif.decode().splitlines():
        if line.startswith("_atom_site."):
            cols.append(line.strip().split(".", 1)[1]); continue
        if not line.startswith("ATOM"):
            continue
        c = dict(zip(cols, line.split()))
        ch = c["label_asym_id"]
        if ch not in pts:
            continue
        if c["label_atom_id"] == "CB" or (c["label_atom_id"] == "CA" and c["label_comp_id"] == "GLY"):
            pts[ch][int(c["label_seq_id"])] = (float(c["Cartn_x"]), float(c["Cartn_y"]), float(c["Cartn_z"]))
    ka, kb = sorted(pts["A"]), sorted(pts["B"])
    xa, xb = np.array([pts["A"][k] for k in ka]), np.array([pts["B"][k] for k in kb])
    D = np.sqrt(((xa[:, None] - xb[None]) ** 2).sum(-1)) < 8
    return {k for k, h in zip(ka, D.any(1)) if h}, {k for k, h in zip(kb, D.any(0)) if h}


def exp(uid, a, b):
    top = None
    for e in str(P.loc[uid, "new_entries"]).split():
        for c in json.load(open(os.path.join(FU, "entry_contacts", e + ".json"))):
            if set(c["acc"]) == {a, b} and (top is None or c["n_contacts"] > top["n_contacts"]):
                top = c
    E, O = set(), set()
    for k, acc in enumerate(top["acc"]):
        E |= {(acc, x) for x in top["iface"][k]}
        O |= {(acc, x) for x in top["observed"][k]}
    return E, O


out = {}
for name, data in files(sys.argv[1]):
    m = re.match(r"fold_rescue_(\d\d)_(pair|bridge|ctrl)_(model|summary_confidences)_(\d)\.(cif|json)$", name)
    if not m:
        continue
    k, arm, kind, s = int(m.group(1)), m.group(2), m.group(3), int(m.group(4))
    d = out.setdefault((k, arm), {"f1": {}, "iptm": {}})
    r = R.iloc[k - 1]
    if kind == "model":
        ia, ib = ab_iface(data)
        E, O = exp(r.uid, r.a, r.b)
        Pset = ({(r.a, x) for x in ia} | {(r.b, x) for x in ib}) & O
        d["f1"][s] = 2 * len(Pset & E) / (len(Pset) + len(E)) if (Pset or E) else 0.0
    else:
        d["iptm"][s] = json.loads(data)["chain_pair_iptm"][0][1]
rows = [dict(pair=k, arm=a, f1_model0=v["f1"].get(0, np.nan), f1_mean=np.mean(list(v["f1"].values())) if v["f1"] else np.nan,
             iptm_ab=np.mean(list(v["iptm"].values())) if v["iptm"] else np.nan) for (k, a), v in sorted(out.items())]
T = pd.DataFrame(rows)
T.to_csv(os.path.join(HERE, "rescue_results.csv"), index=False)
W = T.pivot(index="pair", columns="arm", values="f1_model0").dropna()
ok = W >= 0.5


def sign(x, y):
    a, b = int((ok[x] & ~ok[y]).sum()), int((~ok[x] & ok[y]).sum())
    n = a + b
    return a, b, (sum(comb(n, i) for i in range(a, n + 1)) / 2 ** n if n else 1.0)


res = {"n_pairs_complete": len(W), "correct": {a: int(ok[a].sum()) for a in ok.columns},
       "mean_iptm_ab": T.groupby("arm").iptm_ab.mean().to_dict()}
if {"pair", "bridge"} <= set(ok.columns):
    a, b, p = sign("bridge", "pair")
    res["R1_bridge_vs_pair"] = {"bridge_only": a, "pair_only": b, "p": p,
                                "verdict": "RESCUE" if p < 0.05 and ok["bridge"].sum() >= 6 else "NOT SHOWN"}
if {"ctrl", "bridge"} <= set(ok.columns):
    a, b, p = sign("bridge", "ctrl")
    res["R2_bridge_vs_ctrl"] = {"bridge_only": a, "ctrl_only": b, "p": p, "verdict": "SPECIFIC" if p < 0.05 else "NOT SHOWN"}
print(json.dumps(res, indent=1, default=float))
json.dump(res, open(os.path.join(HERE, "results_rescue.json"), "w"), indent=1, default=float)
