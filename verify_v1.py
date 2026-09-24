"""PREREG_VERIFY V1 (homologous precedent), V2 (shift null, human), V3 (entry-cluster bootstrap), V5 grid part
that needs no coordinates. Homolog hits cached in NQ_local/af3-hitcall/verify/."""
import json
import os
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
import requests

from metrics import ci

L = r"C:\Users\bmens\NQ_local\af3-hitcall"
V = os.path.join(L, "verify")
os.makedirs(V, exist_ok=True)
rng = np.random.default_rng(1717)
URL = "https://search.rcsb.org/rcsbsearch/v2/query"


def search(seq, ident):
    q = {"query": {"type": "group", "logical_operator": "and", "nodes": [
        {"type": "terminal", "service": "sequence", "parameters": {"evalue_cutoff": 1e-3, "identity_cutoff": ident, "sequence_type": "protein", "value": seq}},
        {"type": "terminal", "service": "text", "parameters": {"attribute": "rcsb_accession_info.initial_release_date", "operator": "less_or_equal", "value": "2021-12-31"}}]},
        "return_type": "polymer_entity", "request_options": {"return_all_hits": True}}
    for a in range(8):
        try:
            r = requests.post(URL, json=q, timeout=180)
            if r.status_code == 204:
                return []
            if r.status_code == 200:
                return [h["identifier"] for h in r.json()["result_set"]]
        except requests.exceptions.RequestException:
            pass
        time.sleep(2 ** a)
    raise RuntimeError("rcsb")


# ---- pair sets ----
H = pd.read_csv(os.path.join(L, "future", "f2_pairs_meta.csv"))
Hp = pd.read_csv(os.path.join(L, "future", "pairs.csv")).set_index("uid")
H["a"], H["b"] = H.uid.map(Hp.id1), H.uid.map(Hp.id2)
H["org"] = "human"
Y = pd.read_csv(os.path.join(L, "future_yeast", "y1_pairs_meta.csv"))
Y = Y.rename(columns={"model": "uid"}).assign(group="confident", org="yeast", correct=lambda x: x.f1 >= 0.5)
seqs = json.load(open(os.path.join(L, "burke", "uniprot_seqs.json")))
cur = None
for line in open(os.path.join(L, "future_yeast", "proteome.fasta")):
    if line.startswith(">"):
        cur = line.split("|")[1]; seqs[cur] = ""
    else:
        seqs[cur] += line.strip()
allp = sorted(set(H.a) | set(H.b) | set(Y.a) | set(Y.b))
print("proteins to search:", len(allp), flush=True)

hits = {}
for ident in (0.25, 0.0):
    fp = os.path.join(V, f"homolog_hits_id{ident:g}.json")
    done = json.load(open(fp)) if os.path.exists(fp) else {}
    todo = [p for p in allp if p not in done]
    with ThreadPoolExecutor(4) as ex:
        for k, (p, h) in enumerate(zip(todo, ex.map(lambda p: search(seqs[p], ident), todo))):
            done[p] = h
            if k % 50 == 0:
                json.dump(done, open(fp, "w")); print("ident", ident, k, "/", len(todo), flush=True)
    json.dump(done, open(fp, "w"))
    hits[ident] = done


def precedented(a, b, h):
    ent = defaultdict(lambda: defaultdict(set))
    for acc in (a, b):
        for e in h.get(acc, []):
            entry, en = e.split("_")
            ent[entry][acc].add(en)
    ex = [e for e, m in ent.items() if a in m and b in m and (m[a] - m[b]) and (m[b] - m[a])]
    return sorted(ex)


D = pd.concat([H[["uid", "org", "group", "a", "b", "entry", "f1"]], Y[["uid", "org", "group", "a", "b", "entry", "f1"]]], ignore_index=True)
D["correct"] = D.f1 >= 0.5
for ident in (0.25, 0.0):
    D[f"prec_id{ident:g}"] = [bool(precedented(a, b, hits[ident])) for a, b in zip(D.a, D.b)]
D["prec_examples"] = [",".join(precedented(a, b, hits[0.25])[:4]) for a, b in zip(D.a, D.b)]
D.to_csv(os.path.join(V, "v1_pairs.csv"), index=False)


def frac_ci(v, clusters=None):
    v = np.asarray(v, float)
    if len(v) == 0:
        return {"n": 0}
    bs = [rng.choice(v, len(v)).mean() for _ in range(2000)]
    out = {"n": int(len(v)), "correct": float(v.mean()), "ci95_pair": ci(np.array(bs), 0.95).tolist()}
    if clusters is not None:  # V3: resample entries
        cl = pd.Series(v).groupby(np.asarray(clusters)).agg(["sum", "count"])
        s, c = cl["sum"].to_numpy(), cl["count"].to_numpy()
        bc = []
        for _ in range(2000):
            i = rng.integers(0, len(cl), len(cl))
            bc.append(s[i].sum() / c[i].sum())
        out["ci95_entry"] = ci(np.array(bc), 0.95).tolist()
        out["n_entries"] = int(len(cl))
    return out


res = {"V1": {}, "V3": {}}
for org in ("human", "yeast"):
    for grp in ("confident", "low"):
        sub = D[(D.org == org) & (D.group == grp)]
        if not len(sub):
            continue
        for ident in (0.25, 0.0):
            col = f"prec_id{ident:g}"
            for lab, m in (("homolog_precedented", sub[col]), ("no_homolog_precedent", ~sub[col])):
                res["V1"][f"{org}|{grp}|id{ident:g}|{lab}"] = frac_ci(sub[m].correct, sub[m].entry)
        res["V3"][f"{org}|{grp}|all"] = frac_ci(sub.correct, sub.entry)
k = "human|confident|id0.25|no_homolog_precedent"
lo = res["V1"][k].get("ci95_pair", [0])[0]
res["V1_rule_human"] = {"key": k, "ci_lower": lo, "verdict": "SURVIVES" if lo > 0.5 else "FAILS: narrow the claim"}

# ---- V2: circular-shift null for human confident (needs the predicted/observed sets again) ----
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
FU = os.path.join(L, "future")
models = {}
for fn in [os.path.join(L, "burke", "interfaces_v2.jsonl"), os.path.join(FU, "extra_low_models.jsonl")]:
    for line in open(fn):
        r = json.loads(line); models[r["unique_ID"]] = r


def exp_sets(uid, a, b):
    top = None
    for e in str(Hp.loc[uid, "new_entries"]).split():
        for c in json.load(open(os.path.join(FU, "entry_contacts", e + ".json"))):
            if set(c["acc"]) == {a, b} and (top is None or c["n_contacts"] > top["n_contacts"]):
                top = c
    E, O = set(), set()
    for k2, acc in enumerate(top["acc"]):
        E |= {(acc, x) for x in top["iface"][k2]}
        O |= {(acc, x) for x in top["observed"][k2]}
    return E, O


def pred_set(rec):
    out = set()
    for ch in rec["chains"].values():
        acc = next((x for x in (rec["id1"], rec["id2"]) if seqs.get(x) == ch["seq"]), None)
        if acc:
            out |= {(acc, k2 + 1) for k2 in ch["iface"]}
    return out


def f1(P, E, O):
    Pp = P & O
    return 2 * len(Pp & E) / (len(Pp) + len(E)) if (Pp or E) else 0.0


conf = D[(D.org == "human") & (D.group == "confident")]
obs, null_rates = [], []
per_pair_null = []
for r in conf.itertuples():
    P = pred_set(models[r.uid]); E, O = exp_sets(r.uid, r.a, r.b)
    obs.append(f1(P, E, O) >= 0.5)
    lens = {r.a: len(seqs[r.a]), r.b: len(seqs[r.b])}
    nulls = []
    for _ in range(200):
        sh = {acc: int(rng.integers(1, n)) for acc, n in lens.items()}
        nulls.append(f1({(acc, (x - 1 + sh[acc]) % lens[acc] + 1) for acc, x in P}, E, O) >= 0.5)
    per_pair_null.append(np.mean(nulls))
sim = [(rng.random(len(per_pair_null)) < np.array(per_pair_null)).mean() for _ in range(10000)]
res["V2_human_confident"] = {"observed_correct": float(np.mean(obs)), "null_mean": float(np.mean(sim)), "null_p99": float(np.quantile(sim, 0.99)),
                             "passes": bool(np.mean(obs) > np.quantile(sim, 0.99))}
print(json.dumps(res, indent=1, default=float))
json.dump(res, open("results_verify_v1.json", "w"), indent=1, default=float)
