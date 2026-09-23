"""PREREG_FUTURE data build: co-complex PDB entries (SIFTS) and RCSB release dates for the Burke
never-solved pairs. Writes future/pairs.csv (one row per pair, with its group and outcome fields)."""
import gzip
import json
import os
import time
from collections import defaultdict

import pandas as pd
import requests

F = r"C:\Users\bmens\NQ_local\af3-hitcall\future"
B = r"C:\Users\bmens\NQ_local\af3-hitcall\burke"

d = pd.read_csv(os.path.join(B, "S1.csv"), low_memory=False).rename(columns={"Gen.id1": "g1", "Gen.id2": "g2"})
d = d[d.structure_file.notna() & (d.id1 != d.id2) & (d.int3D_model_structure.fillna(0).astype(int) == 0)].copy()
d["group"] = pd.cut(d.pDockQ, [-1, 0.10, 0.23, 2], labels=["low", "mid", "confident"], right=False)
d = d[d.group != "mid"].drop_duplicates("unique_ID")
print("population", d.group.value_counts().to_dict())

# SIFTS: accession -> {entry: set(chains)}
acc = set(d.id1) | set(d.id2)
m = defaultdict(lambda: defaultdict(set))
with gzip.open(os.path.join(F, "pdb_chain_uniprot.tsv.gz"), "rt") as f:
    next(f); next(f)
    for line in f:
        e, ch, sp = line.split("\t")[:3]
        if sp in acc:
            m[sp][e].add(ch)
print("accessions with any PDB chain:", len(m), "of", len(acc))


def cocomplex(a, b):
    out = []
    for e in set(m[a]) & set(m[b]):
        ca, cb = m[a][e], m[b][e]
        if (ca - cb) and (cb - ca):  # each on a chain the other is not (strict, as in the audit)
            out.append(e)
    return out


d["entries"] = [cocomplex(a, b) for a, b in zip(d.id1, d.id2)]
need = sorted({e for es in d.entries for e in es} | {e for a in acc for e in m[a]})
print("entries needing dates:", len(need))

cache_p = os.path.join(F, "release_dates.json")
dates = json.load(open(cache_p)) if os.path.exists(cache_p) else {}
todo = [e for e in need if e not in dates]
Q = "query($ids:[String!]!){entries(entry_ids:$ids){rcsb_id rcsb_accession_info{initial_release_date}}}"
for k in range(0, len(todo), 400):
    ids = [e.upper() for e in todo[k:k + 400]]
    for attempt in range(5):
        try:
            r = requests.post("https://data.rcsb.org/graphql", json={"query": Q, "variables": {"ids": ids}}, timeout=120)
            r.raise_for_status()
            for x in r.json()["data"]["entries"] or []:
                if x and x["rcsb_accession_info"]:
                    dates[x["rcsb_id"].lower()] = x["rcsb_accession_info"]["initial_release_date"][:10]
            break
        except Exception as ex:
            print("retry", ex)
            time.sleep(5)
    if k % 8000 == 0:
        print("dates", len(dates), "/", len(need), flush=True)
        json.dump(dates, open(cache_p, "w"))
json.dump(dates, open(cache_p, "w"))

CUT = "2022-01-01"
rows = []
for r in d.itertuples():
    ds = sorted((dates.get(e, "9999"), e) for e in r.entries)
    first = ds[0][0] if ds else None
    new = [e for dt, e in ds if dt >= CUT and dt != "9999"]
    tract = all(any(dates.get(e, "9999") < CUT for e in m[a]) for a in (r.id1, r.id2))
    rows.append(dict(uid=r.unique_ID, id1=r.id1, id2=r.id2, g1=r.g1, g2=r.g2, pDockQ=r.pDockQ,
                     group=r.group, n_cocomplex=len(ds), first_release=first,
                     missed_precedent=bool(first and first < CUT), newly_solved=bool(first and first >= CUT),
                     new_entries=" ".join(new), tractable=tract))
out = pd.DataFrame(rows)
out.to_csv(os.path.join(F, "pairs.csv"), index=False)
print("missed precedent (excluded):", int(out.missed_precedent.sum()), "| newly solved total:", int(out.newly_solved.sum()))
