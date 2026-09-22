"""B. subtilis precedent for PREREG_BSU: fetch UniProt sequences, run the same RCSB search.
Writes data/bsu_hits_pre.json and data/bsu_hits_any.json {accession: [entity ids]}."""
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import requests

D = r"C:\Users\bmens\NQ_local\af3-hitcall"
URL = "https://search.rcsb.org/rcsbsearch/v2/query"
ev5 = pd.read_excel(os.path.join(D, "oreilly", "MSB-19-e11544-s003.xlsx"), sheet_name="Dataset EV5")
accs = sorted(set(ev5["uniprot 1"]) | set(ev5["uniprot 2"]))
seq_path = os.path.join(D, "data", "bsu_seqs.json")
if os.path.exists(seq_path):
    seqs = json.load(open(seq_path))
else:
    seqs = {}
    for k in range(0, len(accs), 100):
        chunk = accs[k:k + 100]
        r = requests.get("https://rest.uniprot.org/uniprotkb/accessions",
                         params={"accessions": ",".join(chunk), "format": "tsv", "fields": "accession,sequence"}, timeout=120)
        r.raise_for_status()
        for line in r.text.strip().split("\n")[1:]:
            a, s = line.split("\t")
            seqs[a] = s
    json.dump(seqs, open(seq_path, "w"))
print("accessions", len(accs), "sequences", len(seqs))


def search(seq, dated):
    nodes = [{"type": "terminal", "service": "sequence", "parameters": {
        "evalue_cutoff": 1e-3, "identity_cutoff": 0.25, "sequence_type": "protein", "value": seq}}]
    if dated:
        nodes.append({"type": "terminal", "service": "text", "parameters": {
            "attribute": "rcsb_accession_info.initial_release_date", "operator": "less_or_equal", "value": "2021-09-30"}})
    q = {"query": {"type": "group", "logical_operator": "and", "nodes": nodes},
         "return_type": "polymer_entity", "request_options": {"return_all_hits": True}}
    r = None
    for attempt in range(8):
        try:
            r = requests.post(URL, json=q, timeout=120)
        except requests.exceptions.RequestException:
            time.sleep(2 ** attempt)
            continue
        if r.status_code == 204:
            return []
        if r.status_code == 200:
            return [h["identifier"] for h in r.json()["result_set"]]
        time.sleep(2 ** attempt)
    raise RuntimeError(getattr(r, "status_code", "conn"))


for tag, dated in [("pre", True), ("any", False)]:
    path = os.path.join(D, "data", f"bsu_hits_{tag}.json")
    done = json.load(open(path)) if os.path.exists(path) else {}
    todo = [a for a in seqs if a not in done]
    with ThreadPoolExecutor(2) as ex:
        for k, (a, h) in enumerate(zip(todo, ex.map(lambda a: search(seqs[a], dated), todo))):
            done[a] = h
            if k % 50 == 0:
                json.dump(done, open(path, "w"))
    json.dump(done, open(path, "w"))
    print(tag, "with >=1 homolog:", sum(bool(v) for v in done.values()), "/", len(done))
