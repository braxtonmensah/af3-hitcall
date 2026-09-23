"""PREREG_FUTURE: did 2021 AF2/FoldDock predictions anticipate complexes released 2022+?
Step A: direct contacts + experimental interfaces from the new entries' mmCIF (cached per entry).
Step B: F1/F1b/F1c anticipation odds ratios. Step C: F2 interface correctness of the frozen models."""
import gzip
import io
import json
import os
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
import requests

from metrics import ci

F = r"C:\Users\bmens\NQ_local\af3-hitcall\future"
B = r"C:\Users\bmens\NQ_local\af3-hitcall\burke"
CACHE = os.path.join(F, "entry_contacts")
os.makedirs(CACHE, exist_ok=True)
rng = np.random.default_rng(2022)
NB = 2000

p = pd.read_csv(os.path.join(F, "pairs.csv"))
p = p[~p.missed_precedent].copy()
p["new_entries"] = p.new_entries.fillna("").str.split()
ns = p[p.newly_solved]
need = sorted({e for es in ns.new_entries for e in es})
accs = set(ns.id1) | set(ns.id2)

# SIFTS segments for the needed entries: (entry, auth chain) -> [(acc, res_beg, res_end, sp_beg)]
seg = defaultdict(list)
with gzip.open(os.path.join(F, "pdb_chain_uniprot.tsv.gz"), "rt") as f:
    next(f); next(f)
    needset = set(need)
    for line in f:
        x = line.rstrip("\n").split("\t")
        if x[0] in needset and x[2] in accs:
            try:
                seg[(x[0], x[1])].append((x[2], int(x[3]), int(x[4]), int(x[7])))
            except ValueError:
                pass


def entry_contacts(e):
    """per (chainA, chainB) of mapped chains: contacts and interface residues in UniProt numbering"""
    out_p = os.path.join(CACHE, e + ".json")
    if os.path.exists(out_p):
        return json.load(open(out_p))
    chains = {c: s for (ee, c), s in seg.items() if ee == e}
    r = requests.get(f"https://files.rcsb.org/download/{e}.cif.gz", timeout=300)
    r.raise_for_status()
    cols, rows = [], defaultdict(dict)
    for line in io.TextIOWrapper(gzip.GzipFile(fileobj=io.BytesIO(r.content)), encoding="utf-8", errors="replace"):
        if line.startswith("_atom_site."):
            cols.append(line.strip().split(".", 1)[1])
            continue
        if not line.startswith("ATOM"):
            continue
        v = line.split()
        c = dict(zip(cols, v))
        if c.get("pdbx_PDB_model_num", "1") != "1":
            continue
        ch = c["auth_asym_id"]
        if ch not in chains:
            continue
        atom, comp, seqid = c["label_atom_id"], c["label_comp_id"], c["label_seq_id"]
        if seqid == "." or not (atom == "CB" or (atom == "CA" and comp == "GLY")):
            continue
        k = int(seqid)
        for acc, rb, re_, sb in chains[ch]:
            if rb <= k <= re_:
                rows[ch][k] = (acc, sb + k - rb, float(c["Cartn_x"]), float(c["Cartn_y"]), float(c["Cartn_z"]))
                break
    res = []
    ids = sorted(rows)
    for a in range(len(ids)):
        for b in range(a + 1, len(ids)):
            A, Bc = list(rows[ids[a]].values()), list(rows[ids[b]].values())
            acA, acB = {x[0] for x in A}, {x[0] for x in Bc}
            if len(acA) != 1 or len(acB) != 1 or acA == acB:
                continue
            xa = np.array([x[2:] for x in A]); xb = np.array([x[2:] for x in Bc])
            D = np.sqrt(((xa[:, None] - xb[None]) ** 2).sum(-1))
            close = D < 8
            res.append({"chains": [ids[a], ids[b]], "acc": [acA.pop(), acB.pop()], "n_contacts": int(close.sum()),
                        "iface": [[A[i][1] for i in np.flatnonzero(close.any(1))], [Bc[j][1] for j in np.flatnonzero(close.any(0))]],
                        "observed": [[x[1] for x in A], [x[1] for x in Bc]]})
    json.dump(res, open(out_p, "w"))
    return res


if not os.path.exists(os.path.join(F, "contacts_done")):
    with ThreadPoolExecutor(8) as ex:
        for k, _ in enumerate(ex.map(entry_contacts, need)):
            if k % 100 == 0:
                print("entries", k, "/", len(need), flush=True)
    open(os.path.join(F, "contacts_done"), "w").write("ok")

# best experimental interface per newly solved pair
best = {}
for r in ns.itertuples():
    top = None
    for e in r.new_entries:
        for c in entry_contacts(e):
            if set(c["acc"]) == {r.id1, r.id2} and (top is None or c["n_contacts"] > top["n_contacts"]):
                top = dict(c, entry=e)
    best[r.uid] = top
p["direct"] = [bool(best.get(u)) and best[u]["n_contacts"] >= 5 for u in p.uid]
p["newly_direct"] = p.newly_solved & p.direct
if "--contacts-only" in sys.argv:  # list pairs needing a model; no group comparison is printed
    have = {json.loads(l)["unique_ID"] for l in open(os.path.join(B, "interfaces_v2.jsonl"))}
    lack = p[p.newly_direct & ~p.uid.isin(have)]
    lack[["uid", "id1", "id2", "group", "pDockQ"]].merge(
        pd.read_csv(os.path.join(B, "S1.csv"), usecols=["unique_ID", "structure_file"]).drop_duplicates("unique_ID"),
        left_on="uid", right_on="unique_ID").to_csv(os.path.join(F, "need_models.csv"), index=False)
    print("pairs needing a streamed model:", len(lack))
    sys.exit(0)

# ---- F1: anticipation (node bootstrap over proteins) ----
prot = sorted(set(p.id1) | set(p.id2))
px = {a: k for k, a in enumerate(prot)}
I, J = p.id1.map(px).to_numpy(), p.id2.map(px).to_numpy()
conf = (p.group == "confident").to_numpy()


def odds(y, w, m):
    a = (w * (y & conf & m)).sum(); b = (w * (~y & conf & m)).sum()
    c = (w * (y & ~conf & m)).sum(); d = (w * (~y & ~conf & m)).sum()
    return ((a + .5) / (b + .5)) / ((c + .5) / (d + .5)), a / max(a + b, 1e-9), c / max(c + d, 1e-9)


res = {"n": p.group.value_counts().to_dict(), "excluded_missed_precedent": int(pd.read_csv(os.path.join(F, "pairs.csv")).missed_precedent.sum()),
       "release_years_newly_solved": ns.first_release.str[:4].value_counts().sort_index().to_dict()}
for lab, y, m in [("F1_newly_solved", p.newly_solved.to_numpy(), np.ones(len(p), bool)),
                  ("F1b_newly_solved_direct", p.newly_direct.to_numpy(), np.ones(len(p), bool)),
                  ("F1c_tractable_only", p.newly_solved.to_numpy(), p.tractable.to_numpy())]:
    o, rc, rl = odds(y, np.ones(len(p)), m)
    bs = []
    for _ in range(NB):
        c = np.bincount(rng.integers(0, len(prot), len(prot)), minlength=len(prot)).astype(float)
        bs.append(odds(y, c[I] * c[J], m)[0])
    lo, hi = ci(np.array(bs), 0.95).tolist()
    res[lab] = {"OR": o, "ci95": [lo, hi], "rate_confident": rc, "rate_low": rl,
                "n_events_conf": int((y & conf & m).sum()), "n_events_low": int((y & ~conf & m).sum()),
                "verdict": "ANTICIPATED" if lo > 1 else "NOT SHOWN"}

# ---- F2: were the frozen models' interfaces right? ----
seqs = json.load(open(os.path.join(B, "uniprot_seqs.json")))
models = {}
for line in open(os.path.join(B, "interfaces_v2.jsonl")):
    rec = json.loads(line)
    models[rec["unique_ID"]] = rec
extra_p = os.path.join(F, "extra_low_models.jsonl")
if os.path.exists(extra_p):
    for line in open(extra_p):
        rec = json.loads(line)
        models[rec["unique_ID"]] = rec


def pred_iface(rec):
    out = {}
    for ch in rec["chains"].values():
        acc = next((a for a in (rec["id1"], rec["id2"]) if seqs.get(a) == ch["seq"]), None)
        if acc:
            out[acc] = {k + 1 for k in ch["iface"]}
    return out if len(out) == 2 else None


rows = []
for r in p[p.newly_direct].itertuples():
    rec = models.get(r.uid)
    if rec is None:
        rows.append(dict(uid=r.uid, group=r.group, f1=np.nan, status="no model"))
        continue
    P = pred_iface(rec)
    if P is None:
        rows.append(dict(uid=r.uid, group=r.group, f1=np.nan, status="no exact-seq mapping"))
        continue
    b = best[r.uid]
    E, O = set(), set()
    for k, acc in enumerate(b["acc"]):
        E |= {(acc, x) for x in b["iface"][k]}
        O |= {(acc, x) for x in b["observed"][k]}
    Pp = {(acc, x) for acc, xs in P.items() for x in xs} & O
    f1 = 2 * len(Pp & E) / (len(Pp) + len(E)) if (Pp or E) else 0.0
    rows.append(dict(uid=r.uid, group=r.group, f1=f1, status="ok", entry=b["entry"], n_pred=len(Pp), n_exp=len(E)))
R = pd.DataFrame(rows)
R.to_csv(os.path.join(F, "f2_pairs.csv"), index=False)
res["F2_status_counts"] = R.groupby(["group", "status"]).size().to_dict()
ok = R[R.status == "ok"]
g = {k: ok[ok.group == k].f1.to_numpy() for k in ("confident", "low")}
res["F2"] = {k: {"n": len(v), "median_f1": float(np.median(v)) if len(v) else None,
                 "frac_correct_f1_ge_0.5": float((v >= 0.5).mean()) if len(v) else None} for k, v in g.items()}
if len(g["confident"]) and len(g["low"]):
    bs = [(rng.choice(g["confident"], len(g["confident"])) >= .5).mean() - (rng.choice(g["low"], len(g["low"])) >= .5).mean() for _ in range(NB)]
    d = (g["confident"] >= .5).mean() - (g["low"] >= .5).mean()
    lo, hi = ci(np.array(bs), 0.95).tolist()
    res["F2"]["diff_correct_conf_minus_low"] = {"diff": float(d), "ci95": [lo, hi], "verdict": "MODELS RIGHT" if lo > 0 else "NOT SHOWN"}
    res["F2"]["ci95_conf_correct"] = ci(np.array([(rng.choice(g["confident"], len(g["confident"])) >= .5).mean() for _ in range(NB)]), 0.95).tolist()
print(json.dumps(res, indent=1, default=str))
json.dump(res, open("results_future.json", "w"), indent=1, default=str)
