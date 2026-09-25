"""PREREG_XLHUMAN O3 (novelty): for each supported pair, is it actually new? Three checks, as registered:
a current RCSB homologous co-complex search under the strict rule, the Bartolec Dataset S5 evidence class,
and a Europe PMC search for papers naming both gene symbols. Run after analysis_xlhuman.py."""
import json
import os
import time
from collections import defaultdict

import pandas as pd
import requests

L = r"C:\Users\bmens\NQ_local\af3-hitcall\xlhuman"
RCSB = "https://search.rcsb.org/rcsbsearch/v2/query"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
CACHE = os.path.join(L, "novelty_cache.json")
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}

res = json.load(open("results_xlhuman.json"))
genes = json.load(open(os.path.join(L, "genes.json")))
seqs = {}
sup = [c["key"] for c in res["O1_supported_pairs"]]
accs = sorted({a for k in sup for a in k.split("_")})

for a in accs:
    if a not in cache.get("seq", {}):
        r = requests.get(f"https://rest.uniprot.org/uniprotkb/{a}.fasta", timeout=60)
        cache.setdefault("seq", {})[a] = "".join(r.text.split("\n")[1:])
json.dump(cache, open(CACHE, "w"))


def entities(seq):
    q = {"query": {"type": "terminal", "service": "sequence",
                   "parameters": {"evalue_cutoff": 1e-3, "identity_cutoff": 0.0,
                                  "sequence_type": "protein", "value": seq}},
         "return_type": "polymer_entity", "request_options": {"return_all_hits": True}}
    for attempt in range(6):
        r = requests.post(RCSB, json=q, timeout=180)
        if r.status_code == 204:
            return []
        if r.status_code == 200:
            return [h["identifier"] for h in r.json()["result_set"]]
        time.sleep(2 ** attempt)
    raise RuntimeError(f"RCSB {r.status_code}")


for a in accs:
    if a not in cache.get("ents", {}):
        cache.setdefault("ents", {})[a] = entities(cache["seq"][a])
        json.dump(cache, open(CACHE, "w"))
        print("rcsb", a, len(cache["ents"][a]), flush=True)


def by_entry(acc):
    d = defaultdict(set)
    for e in cache["ents"][acc]:
        d[e.split("_")[0]].add(e)
    return d


def epmc(g1, g2):
    key = f"{g1}|{g2}"
    if key not in cache.get("epmc", {}):
        q = f'"{g1}" AND "{g2}" AND (INTERACT* OR COMPLEX OR BIND*)'
        r = requests.get(EPMC, params={"query": q, "format": "json", "pageSize": 5}, timeout=60).json()
        cache.setdefault("epmc", {})[key] = {
            "hitCount": r["hitCount"],
            "top": [{"id": x.get("id"), "title": x.get("title", "")[:150], "year": x.get("pubYear")}
                    for x in r["resultList"]["result"][:5]]}
        json.dump(cache, open(CACHE, "w"))
    return cache["epmc"][key]


# Bartolec Dataset S5 evidence class
s5 = None
p5 = os.path.join(L, "pnas.2219418120.sd05.xlsx")
if os.path.exists(p5):
    x = pd.ExcelFile(p5)
    for sh in x.sheet_names:
        d = x.parse(sh)
        cols = [c for c in d.columns if "interaction id" in str(c).lower()]
        if cols:
            s5, s5key = d, cols[0]
            break

out = []
for k in sup:
    a, b = k.split("_")
    ea, eb = by_entry(a), by_entry(b)
    strict = sorted({p for p in set(ea) & set(eb) if (ea[p] - eb[p]) and (eb[p] - ea[p])})
    ga, gb = genes.get(a, a), genes.get(b, b)
    lit = epmc(ga, gb)
    row = {"pair": k, "genes": f"{ga}-{gb}", "n_homologous_cocomplex_entries": len(strict),
           "example_entries": strict[:5], "epmc_hits": lit["hitCount"], "epmc_top": lit["top"]}
    if s5 is not None:
        m = s5[s5[s5key].astype(str).str.contains(a, na=False) & s5[s5key].astype(str).str.contains(b, na=False)]
        row["bartolec_s5_rows"] = len(m)
    row["is_new"] = bool(len(strict) == 0 and lit["hitCount"] == 0)
    out.append(row)
    print(f"{row['genes']:16s} homologous co-complex entries {len(strict):5d}  EuropePMC {lit['hitCount']:5d}  "
          f"{'NEW' if row['is_new'] else 'not new'}")
    if strict[:3]:
        print(f"    e.g. {strict[:3]}")
    for t in lit["top"][:2]:
        print(f"    lit: {t['year']} {t['title'][:110]}")

res["O3_novelty"] = out
res["O3_n_new"] = sum(r["is_new"] for r in out)
json.dump(res, open("results_xlhuman.json", "w"), indent=1, default=float)
print("\nO3: pairs meeting 'new':", res["O3_n_new"], "of", len(out))
