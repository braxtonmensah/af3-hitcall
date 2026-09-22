"""UniProt canonical sequences for all accessions in Burke S1 (for exact position mapping)."""
import json, os, time
import pandas as pd, requests
B = r"C:\Users\bmens\NQ_local\af3-hitcall\burke"
d = pd.read_csv(os.path.join(B, "S1.csv"), low_memory=False, usecols=["id1", "id2"])
accs = sorted(set(d.id1) | set(d.id2))
path = os.path.join(B, "uniprot_seqs.json")
seqs = json.load(open(path)) if os.path.exists(path) else {}
todo = [a for a in accs if a not in seqs]
print("accessions", len(accs), "todo", len(todo))
for k in range(0, len(todo), 100):
    chunk = todo[k:k + 100]
    for attempt in range(5):
        try:
            r = requests.get("https://rest.uniprot.org/uniprotkb/accessions",
                             params={"accessions": ",".join(chunk), "format": "tsv", "fields": "accession,sequence"}, timeout=120)
            if r.status_code == 200: break
        except requests.exceptions.RequestException:
            pass
        time.sleep(2 ** attempt)
    for line in r.text.strip().split("\n")[1:]:
        a, s = line.split("\t"); seqs[a] = s
    for a in chunk: seqs.setdefault(a, None)
    if k % 1000 == 0:
        json.dump(seqs, open(path, "w")); print(k, flush=True)
json.dump(seqs, open(path, "w"))
print("have sequences", sum(v is not None for v in seqs.values()), "/", len(seqs))
