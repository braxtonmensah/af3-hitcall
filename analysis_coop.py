"""PREREG_COOP: Arm P (pooled natural experiment, M. genitalium) and Arm H (human hit/miss structures)."""
import gzip
import io
import json
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
import requests

from analysis_h1_h2_lib import precedent_matrix_strict
from metrics import ci

rng = np.random.default_rng(1313)
NB = 2000
D = r"C:\Users\bmens\NQ_local\af3-hitcall\data"
FU = r"C:\Users\bmens\NQ_local\af3-hitcall\future"
res = {}

# ------------------------- Arm P -------------------------
ST = np.load(os.path.join(D, "string_exp.npy"))
POS = ST > 800
PRE = precedent_matrix_strict("") | precedent_matrix_strict("_id0")
n = ST.shape[0]
d = pd.read_csv(os.path.join(D, "s0_per_pool.csv"))
mem = defaultdict(set)
for i, j, p in zip(d.i, d.j, d.pool):
    mem[p].update((i, j))


def ctx(i, j, p):
    others = mem[p] - {i, j}
    if any(POS[i, x] and POS[j, x] for x in others):
        return "bridge"
    if any(POS[i, x] or POS[j, x] for x in others):
        return "single"
    return "none"


d["ctx"] = [ctx(i, j, p) for i, j, p in zip(d.i, d.j, d.pool)]
d["pos"] = POS[d.i, d.j]
d["pre"] = PRE[d.i, d.j]
# negatives eligible for P2: non-positive pairs sharing some > 800 partner anywhere
share = (POS.astype(int) @ POS.astype(int)) > 0
d["neg_share"] = ~d.pos & share[d.i, d.j]


def paired(sub, a, b):
    A = sub[sub.ctx.isin(a)].groupby(["i", "j"]).s0.mean()
    Bm = sub[sub.ctx.isin(b)].groupby(["i", "j"]).s0.mean()
    x = (A - Bm).dropna()
    ij = np.array(x.index.tolist()).reshape(-1, 2)
    return ij[:, 0], ij[:, 1], x.to_numpy()


def wmean(i, j, v, w):
    ww = w[i] * w[j]
    return (ww * v).sum() / ww.sum() if ww.sum() > 0 else np.nan


def boot(f):
    pt = f(np.ones(n))
    bs = np.array([f(np.bincount(rng.integers(0, n, n), minlength=n).astype(float)) for _ in range(NB)])
    bs = bs[np.isfinite(bs)]
    return {"est": float(pt), "ci95": ci(bs, 0.95).tolist()}


never = d[d.pos & ~d.pre]
prec = d[d.pos & d.pre]
negs = d[d.neg_share]
bn = paired(never, ["bridge"], ["single", "none"])
bp = paired(prec, ["bridge"], ["single", "none"])
bg = paired(negs, ["bridge"], ["single", "none"])
sn = paired(never, ["single"], ["none"])
res["P_n_pairs"] = {"never": len(bn[2]), "prec": len(bp[2]), "neg": len(bg[2]), "never_single_vs_none": len(sn[2])}
res["P1_delta_bridge_never"] = boot(lambda w: wmean(*bn, w))
res["P1_verdict"] = "PASS" if res["P1_delta_bridge_never"]["ci95"][0] > 0 else "FAIL"
res["P2_DiD_never_minus_neg"] = boot(lambda w: wmean(*bn, w) - wmean(*bg, w))
res["P2_verdict"] = "PASS" if res["P2_DiD_never_minus_neg"]["ci95"][0] > 0 else "FAIL"
res["P3_bridge_minus_single"] = boot(lambda w: wmean(*bn, w) - wmean(*sn, w))
res["P3_delta_single_never"] = boot(lambda w: wmean(*sn, w))
res["P3_verdict"] = "PASS" if res["P3_bridge_minus_single"]["ci95"][0] > 0 else "FAIL"
res["P_delta_bridge_prec"] = boot(lambda w: wmean(*bp, w))
res["P_delta_bridge_neg"] = boot(lambda w: wmean(*bg, w))
print(json.dumps({k: v for k, v in res.items()}, indent=1, default=float), flush=True)

# ------------------------- Arm H -------------------------
p = pd.read_csv(os.path.join(FU, "pairs.csv"))
p = p[~p.missed_precedent & p.newly_solved].copy()
p["new_entries"] = p.new_entries.fillna("").str.split()
ref = {}
for r in p.itertuples():
    top = None
    for e in r.new_entries:
        for c in json.load(open(os.path.join(FU, "entry_contacts", e + ".json"))):
            if set(c["acc"]) == {r.id1, r.id2} and (top is None or c["n_contacts"] > top["n_contacts"]):
                top = dict(c, entry=e)
    if top and top["n_contacts"] >= 5:
        ref[r.uid] = (top["entry"], top["chains"], r.group)
print("Arm H pairs:", pd.Series([g for _, _, g in ref.values()]).value_counts().to_dict(), flush=True)

cache = os.path.join(FU, "coop_cache")
os.makedirs(cache, exist_ok=True)


def entry_atoms(e):
    """CB/CA coordinates for every polymer chain + entity count; cached as npz"""
    fp = os.path.join(cache, e + ".npz")
    if os.path.exists(fp):
        z = np.load(fp, allow_pickle=True)
        return z["xyz"], z["ch"], int(z["nent"])
    r = requests.get(f"https://files.rcsb.org/download/{e}.cif.gz", timeout=300)
    r.raise_for_status()
    cols, xyz, ch, ents = [], [], [], set()
    for line in io.TextIOWrapper(gzip.GzipFile(fileobj=io.BytesIO(r.content)), encoding="utf-8", errors="replace"):
        if line.startswith("_atom_site."):
            cols.append(line.strip().split(".", 1)[1])
            continue
        if not line.startswith("ATOM"):
            continue
        c = dict(zip(cols, line.split()))
        if c.get("pdbx_PDB_model_num", "1") != "1":
            continue
        ents.add(c["label_entity_id"])
        if c["label_atom_id"] == "CB" or (c["label_atom_id"] == "CA" and c["label_comp_id"] == "GLY"):
            xyz.append((float(c["Cartn_x"]), float(c["Cartn_y"]), float(c["Cartn_z"])))
            ch.append(c["auth_asym_id"])
    xyz, ch = np.array(xyz, np.float32), np.array(ch)
    np.savez(fp, xyz=xyz, ch=ch, nent=len(ents))
    return xyz, ch, len(ents)


with ThreadPoolExecutor(8) as ex:
    list(ex.map(entry_atoms, sorted({e for e, _, _ in ref.values()})))

rows = []
for uid, (e, (ca, cb), g) in ref.items():
    xyz, ch, nent = entry_atoms(e)
    A, B, O = xyz[ch == ca], xyz[ch == cb], xyz[(ch != ca) & (ch != cb)]
    Dab = np.sqrt(((A[:, None] - B[None]) ** 2).sum(-1)) < 8
    ia, ib = Dab.any(1), Dab.any(0)
    iface = np.concatenate([A[ia], B[ib]])
    if len(O):
        near = np.zeros(len(iface), bool)
        for k in range(0, len(O), 4000):  # chunked to bound memory on large assemblies
            near |= (np.sqrt(((iface[:, None] - O[None, k:k + 4000]) ** 2).sum(-1)) < 8).any(1)
        bf = float(near.mean())
    else:
        bf = 0.0
    rows.append(dict(uid=uid, group=g, entry=e, bridged_frac=bf, n_entities=nent, n_chains=len(set(ch)), pair_contacts=int(Dab.sum())))
H = pd.DataFrame(rows)
H.to_csv(os.path.join(FU, "coop_armH.csv"), index=False)


def med_diff(col):
    a = H[H.group == "low"][col].to_numpy(float)
    b = H[H.group == "confident"][col].to_numpy(float)
    pt = np.median(a) - np.median(b)
    bs = [np.median(rng.choice(a, len(a))) - np.median(rng.choice(b, len(b))) for _ in range(NB)]
    return {"median_miss": float(np.median(a)), "median_hit": float(np.median(b)), "diff": float(pt), "ci95": ci(np.array(bs), 0.95).tolist()}


res["H_n"] = H.group.value_counts().to_dict()
res["H1_bridged_frac"] = med_diff("bridged_frac")
res["H1_verdict"] = "PASS" if res["H1_bridged_frac"]["ci95"][0] > 0 else "FAIL"
res["H2_n_entities"] = med_diff("n_entities")
res["H3_pair_contacts"] = med_diff("pair_contacts")
res["H_frac_isolated_dimer_entries"] = {g: float((H[H.group == g].n_chains == 2).mean()) for g in ("confident", "low")}
res["VERDICT"] = "COOPERATIVE MISSES SUPPORTED" if res["P1_verdict"] == "PASS" and res["H1_verdict"] == "PASS" else \
    "PARTIAL" if "PASS" in (res["P1_verdict"], res["H1_verdict"]) else "NOT SUPPORTED"
print(json.dumps(res, indent=1, default=float))
json.dump(res, open("results_coop.json", "w"), indent=1, default=float)
