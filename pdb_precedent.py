"""H1 precedent: which PDB entries (released <= 2021-09-30, AF3's cutoff) contain a homolog of each
M. genitalium protein. RCSB mmseqs2 search, E <= 1e-3, identity >= 0.25, polymer-entity hits.
Uses sequences only (no scores, no STRING). Output: data/pdb_hits.json {locus: [entity_id, ...]}.
"""
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import requests

OUT = r"C:\Users\bmens\NQ_local\af3-hitcall\data"
URL = "https://search.rcsb.org/rcsbsearch/v2/query"
CUTOFF = "2021-09-30"
IDENT = float(sys.argv[1]) if len(sys.argv) > 1 else 0.25
TAG = "" if IDENT == 0.25 else f"_id{IDENT:g}"


def search(seq):
    q = {
        "query": {"type": "group", "logical_operator": "and", "nodes": [
            {"type": "terminal", "service": "sequence", "parameters": {
                "evalue_cutoff": 1e-3, "identity_cutoff": IDENT,
                "sequence_type": "protein", "value": seq}},
            {"type": "terminal", "service": "text", "parameters": {
                "attribute": "rcsb_accession_info.initial_release_date",
                "operator": "less_or_equal", "value": CUTOFF}}]},
        "return_type": "polymer_entity",
        "request_options": {"return_all_hits": True},
    }
    for attempt in range(6):
        r = requests.post(URL, json=q, timeout=120)
        if r.status_code == 204:  # no hits
            return []
        if r.status_code == 200:
            return [h["identifier"] for h in r.json()["result_set"]]
        time.sleep(2 ** attempt)
    raise RuntimeError(f"RCSB {r.status_code}: {r.text[:200]}")


def main():
    prot = pd.read_csv(os.path.join(OUT, "proteins.csv"))
    path = os.path.join(OUT, f"pdb_hits{TAG}.json")
    done = json.load(open(path)) if os.path.exists(path) else {}
    todo = [(l, s.rstrip("*")) for l, s in zip(prot.locus_tag, prot.aa_sequence) if l not in done]
    print("todo", len(todo))
    with ThreadPoolExecutor(4) as ex:
        for k, (locus, hits) in enumerate(zip([t[0] for t in todo], ex.map(lambda t: search(t[1]), todo))):
            done[locus] = hits
            if k % 25 == 0:
                json.dump(done, open(path, "w"))
                print(k, locus, len(hits), flush=True)
    json.dump(done, open(path, "w"))
    n_hit = sum(bool(v) for v in done.values())
    print(f"proteins with >=1 PDB homolog: {n_hit}/{len(done)}")


if __name__ == "__main__":
    main()
