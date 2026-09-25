"""PREREG_HIGHER_CAL: does the split-crosslink signature (results_higher.json, commit 5e231af) track the real
stoichiometry of pairs that have a solved homologous co-complex? Labels come from RCSB assembly 1 copy numbers.
Committed pre-registration: PREREG_HIGHER_CAL.md."""
import json
import os
import re
import time
from collections import Counter, defaultdict

import numpy as np
import pandas as pd
import requests

L = r"C:\Users\bmens\NQ_local\af3-hitcall"
CACHE = os.path.join(L, "data", "rcsb_assemblies.json")
GQL = "https://data.rcsb.org/graphql"
rng = np.random.default_rng(26)

H = json.load(open("results_higher.json"))
P = pd.DataFrame(H["all_pairs"])
P["split2"] = (P.n_near >= 1) & (P.n_far >= 2)
hits = json.load(open(os.path.join(L, "data", "pdb_hits.json")))


def by_entry(locus):
    d = defaultdict(set)
    for e in hits.get(locus, []):
        d[e.split("_")[0]].add(e)
    return d


# ---------- strict co-complex entries per pair ----------
strict = {}
for p in P.pair:
    a, b = p.split("-")
    ea, eb = by_entry(a), by_entry(b)
    strict[p] = {pdb: (sorted(ea[pdb] - eb[pdb]), sorted(eb[pdb] - ea[pdb]))
                 for pdb in set(ea) & set(eb) if (ea[pdb] - eb[pdb]) and (eb[pdb] - ea[pdb])}
need = sorted({pdb for d in strict.values() for pdb in d})

# ---------- fetch assembly records (cached) ----------
Q = """query($ids:[String!]!){ entries(entry_ids:$ids){ rcsb_id
  assemblies{ rcsb_assembly_container_identifiers{assembly_id} pdbx_struct_assembly_gen{ asym_id_list oper_expression } }
  polymer_entities{ rcsb_polymer_entity_container_identifiers{ entity_id asym_ids } } } }"""
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
todo = [x for x in need if x not in cache]
for i in range(0, len(todo), 100):
    ids = todo[i:i + 100]
    for attempt in range(5):
        r = requests.post(GQL, json={"query": Q, "variables": {"ids": ids}}, timeout=120)
        if r.status_code == 200:
            break
        time.sleep(2 ** attempt)
    r.raise_for_status()
    for e in r.json()["data"]["entries"] or []:
        if e:
            cache[e["rcsb_id"]] = e
    for x in ids:
        cache.setdefault(x, None)
    json.dump(cache, open(CACHE, "w"))
    print(f"fetched {min(i + 100, len(todo))}/{len(todo)}", flush=True)


def n_ops(expr):
    """number of operators in an oper_expression: '1', '1,2', '(1-60)', '(1-5)(6-10)' (product of groups)"""
    groups = re.findall(r"\(([^)]*)\)", expr) or [expr]
    n = 1
    for g in groups:
        k = 0
        for item in g.split(","):
            item = item.strip()
            if "-" in item:
                lo, hi = item.split("-")
                k += int(hi) - int(lo) + 1
            elif item:
                k += 1
        n *= max(k, 1)
    return n


def copies(rec):
    """entity id -> copies in assembly 1, or None if unparseable"""
    try:
        asm = [a for a in rec["assemblies"] if a["rcsb_assembly_container_identifiers"]["assembly_id"] == "1"][0]
        asym2ent = {}
        for pe in rec["polymer_entities"]:
            ids = pe["rcsb_polymer_entity_container_identifiers"]
            for s in ids["asym_ids"] or []:
                asym2ent[s] = f"{rec['rcsb_id']}_{ids['entity_id']}"
        c = Counter()
        for g in asm["pdbx_struct_assembly_gen"]:
            k = n_ops(g["oper_expression"])
            for s in g["asym_id_list"]:
                if s in asym2ent:
                    c[asym2ent[s]] += k
        return c
    except (TypeError, IndexError, KeyError, ValueError):
        return None


# ---------- labels ----------
rows, dropped = [], 0
for p, entries in strict.items():
    votes = []
    for pdb, (only_a, only_b) in entries.items():
        c = copies(cache.get(pdb))
        if c is None:
            dropped += 1
            continue
        ca, cb = max(c.get(e, 0) for e in only_a), max(c.get(e, 0) for e in only_b)
        if ca == 0 or cb == 0:  # entity not in assembly 1: this assembly does not contain both
            continue
        votes.append("higher" if max(ca, cb) >= 2 else "one-to-one")
    if not votes:
        continue
    v = Counter(votes)
    label = ("ambiguous" if v["higher"] == v["one-to-one"] else
             "higher" if v["higher"] > v["one-to-one"] else "one-to-one")
    rows.append({"pair": p, "label": label, "n_entries": len(votes), "n_higher": v["higher"],
                 "n_one_to_one": v["one-to-one"]})
lab = pd.DataFrame(rows).merge(P, on="pair")
T = lab[lab.label != "ambiguous"].reset_index(drop=True)
res = {"n_pairs": len(P), "n_pairs_with_strict_cocomplex": sum(bool(d) for d in strict.values()),
       "n_entries_needed": len(need), "n_entries_unparseable": dropped, "n_labelled": len(lab),
       "n_ambiguous": int((lab.label == "ambiguous").sum()), "ambiguous": lab[lab.label == "ambiguous"].pair.tolist(),
       "n_higher": int((T.label == "higher").sum()), "n_one_to_one": int((T.label == "one-to-one").sum())}


def wilson(k, n):
    if n == 0:
        return [None, None]
    z, ph = 1.96, k / n
    d = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / d
    h = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / d
    return [round(float(c - h), 3), round(float(c + h), 3)]


def call_stats(call):
    hi, one = T[T.label == "higher"], T[T.label == "one-to-one"]
    k_hi, k_one = int(hi[call].sum()), int(one[call].sum())
    n_call = k_hi + k_one
    base = len(hi) / len(T)
    prec = k_hi / n_call if n_call else None
    return {"sensitivity": round(k_hi / len(hi), 3) if len(hi) else None, "sens_k_n": [k_hi, len(hi)],
            "sens_ci": wilson(k_hi, len(hi)),
            "false_positive_rate": round(k_one / len(one), 3) if len(one) else None, "fpr_k_n": [k_one, len(one)],
            "fpr_ci": wilson(k_one, len(one)),
            "precision": round(prec, 3) if prec is not None else None, "prec_ci": wilson(k_hi, n_call),
            "base_rate_higher": round(base, 3), "lift": round(prec / base, 2) if prec else None}


def c1(call):
    hi, one = T[T.label == "higher"], T[T.label == "one-to-one"]
    out = {"n_higher": len(hi), "n_one_to_one": len(one), "n_call": int(T[call].sum())}
    if len(hi) < 8 or len(one) < 8 or T[call].sum() < 3:
        out["verdict"] = "UNDERPOWERED (descriptive only)"
        out["delta"] = float(hi[call].mean() - one[call].mean()) if len(hi) and len(one) else None
        return out
    loci = sorted({g for p in T.pair for g in p.split("-")})
    li = {g: i for i, g in enumerate(loci)}
    ga = np.array([li[p.split("-")[0]] for p in T.pair]); gb = np.array([li[p.split("-")[1]] for p in T.pair])
    is_hi = (T.label == "higher").values; is_one = ~is_hi; x = T[call].values.astype(float)
    delta = float(x[is_hi].mean() - x[is_one].mean())
    bs = []
    for _ in range(2000):
        c = np.bincount(rng.integers(0, len(loci), len(loci)), minlength=len(loci)).astype(float)
        w = c[ga] * c[gb]
        wh, wo = (w * is_hi).sum(), (w * is_one).sum()
        if wh == 0 or wo == 0:
            continue
        bs.append((w * is_hi * x).sum() / wh - (w * is_one * x).sum() / wo)
    lo, hi_ = np.quantile(bs, [0.025, 0.975])
    out.update(delta=round(delta, 3), ci95=[round(float(lo), 3), round(float(hi_), 3)], n_boot=len(bs),
               verdict="CALIBRATED" if delta > 0 and lo > 0 else "NOT CALIBRATED")
    return out


res["C1_split"] = c1("split")
res["C2_split"] = call_stats("split")
res["C2_clean_as_one_to_one"] = {"rate_clean_given_one_to_one": wilson(int(T[T.label == "one-to-one"].clean.sum()),
                                                                        int((T.label == "one-to-one").sum())),
                                 "k_n_one": [int(T[T.label == "one-to-one"].clean.sum()), int((T.label == "one-to-one").sum())],
                                 "k_n_higher": [int(T[T.label == "higher"].clean.sum()), int((T.label == "higher").sum())]}
res["C3_split2"] = {"C1": c1("split2"), "C2": call_stats("split2")}

RECOVERY = ["MG_340-MG_341", "MG_177-MG_341", "MG_191-MG_192", "MG_272-MG_273", "MG_272-MG_274", "MG_273-MG_274",
            "MG_139-MG_423"]
res["recovery_list_labels"] = {p: (lab[lab.pair == p][["label", "n_higher", "n_one_to_one"]].to_dict("records") or
                                   ["no strict co-complex: unlabelled"])[0] for p in RECOVERY}
res["table"] = lab.sort_values(["label", "S0"], ascending=[True, False])[
    ["pair", "label", "n_entries", "n_higher", "n_one_to_one", "n_links", "n_near", "n_far", "split", "split2", "clean",
     "S0"]].to_dict("records")

print(json.dumps({k: v for k, v in res.items() if k != "table"}, indent=1, default=float))
print()
print(lab.sort_values(["label", "S0"], ascending=[True, False])[
    ["pair", "label", "n_higher", "n_one_to_one", "n_links", "n_near", "n_far", "split", "split2", "clean"]].to_string())
json.dump(res, open("results_higher_cal.json", "w"), indent=1,
          default=lambda o: o.item() if isinstance(o, (np.integer, np.floating, np.bool_)) else o)
