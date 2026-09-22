"""Pilot extension (PREREG_VIBRIO Amendment 2): TfoS (VC_2080) against all 84 pilot proteins.
TfoS is in every pool; partners fill the rest of a 4,000-aa cap, and each partner appears once."""
import json, os
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
src = pd.read_csv(r"C:\Users\bmens\NQ_local\af3-hitcall\vibrio\vc_proteome.tsv", sep="\t")
src["locus"] = src["Gene Names (ordered locus)"].astype(str).str.split().str[0]
seq = dict(zip(src.locus, src.Sequence))
P = pd.read_csv(os.path.join(HERE, "jobs", "proteins.csv"))
tfos = seq["VC_2080"]; cap = 4000 - len(tfos)
partners = P.sort_values("length", ascending=False)[["locus", "length"]].values.tolist()
pools, cur, size = [], [], 0
for loc, L in partners:  # first-fit decreasing
    placed = False
    for p in pools:
        if p["size"] + L <= cap:
            p["m"].append(loc); p["size"] += L; placed = True; break
    if not placed:
        pools.append({"m": [loc], "size": L})
jobs, rows = [], []
for k, p in enumerate(pools, 1):
    name = f"vc_tfos_{k:02d}"
    mem = ["VC_2080"] + p["m"]
    rows.append(dict(job=name, n=len(mem), aa=len(tfos) + p["size"], loci="::::".join(mem)))
    jobs.append({"name": name, "modelSeeds": [], "dialect": "alphafoldserver", "version": 1,
                 "sequences": [{"proteinChain": {"sequence": seq[m], "count": 1}} for m in mem]})
pd.DataFrame(rows).to_csv(os.path.join(HERE, "jobs", "pools_tfos.csv"), index=False)
json.dump(jobs, open(os.path.join(HERE, "jobs", "afserver_tfos.json"), "w"))
print("TfoS length", len(tfos), "| pools", len(pools), "| max aa", max(r["aa"] for r in rows), "| partners", sum(len(p["m"]) for p in pools))
