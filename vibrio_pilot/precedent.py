"""PREREG_VIBRIO: classify each positive pair as precedented / never-solved (H1 primary definition)."""
import json, os, sys, time
from collections import defaultdict
import pandas as pd, requests
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.dirname(os.path.abspath(__file__))
seqs = pd.read_csv(r"C:\Users\bmens\NQ_local\af3-hitcall\vibrio\vc_proteome.tsv", sep="\t")
seqs["locus"] = seqs["Gene Names (ordered locus)"].astype(str).str.split().str[0]
P = pd.read_csv(os.path.join(HERE, "jobs", "proteins.csv"))
S = P[P.kind == "system"].merge(seqs[["locus", "Sequence"]], on="locus")
URL = "https://search.rcsb.org/rcsbsearch/v2/query"
def search(seq):
    q = {"query": {"type": "group", "logical_operator": "and", "nodes": [
        {"type": "terminal", "service": "sequence", "parameters": {"evalue_cutoff": 1e-3, "identity_cutoff": 0.25, "sequence_type": "protein", "value": seq}},
        {"type": "terminal", "service": "text", "parameters": {"attribute": "rcsb_accession_info.initial_release_date", "operator": "less_or_equal", "value": "2021-09-30"}}]},
        "return_type": "polymer_entity", "request_options": {"return_all_hits": True}}
    for a in range(8):
        try:
            r = requests.post(URL, json=q, timeout=120)
            if r.status_code == 204: return []
            if r.status_code == 200: return [h["identifier"] for h in r.json()["result_set"]]
        except requests.exceptions.RequestException:
            pass
        time.sleep(2 ** a)
    raise RuntimeError("rcsb")
hits = {r.name: search(r.Sequence) for r in S.itertuples()}
json.dump(hits, open(os.path.join(HERE, "system_pdb_hits.json"), "w"))
ent = defaultdict(lambda: defaultdict(set))
for nm, es in hits.items():
    for e in es:
        entry, en = e.split("_"); ent[entry][nm].add(en)
POS = [("PilT","PilU"),("CBP","ChiS"),("DprA","ComM"),("PilM","PilN"),("PilN","PilO"),("PilO","PilP"),("PilP","PilQ"),("PilB","PilC"),("PilT","PilC")]
rows = []
for a, b in POS:
    ex = [e for e, m in ent.items() if a in m and b in m and len(m[a] | m[b]) >= 2]
    rows.append(dict(pair=f"{a}-{b}", precedented=bool(ex), n_entries=len(ex), examples=",".join(sorted(ex)[:5]),
                     homologs_a=len(hits[a]), homologs_b=len(hits[b])))
R = pd.DataFrame(rows); print(R.to_string(index=False)); R.to_csv(os.path.join(HERE, "positive_precedent.csv"), index=False)
