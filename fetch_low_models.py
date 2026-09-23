"""PREREG_FUTURE F2: stream Burke models for newly solved, direct pairs that have no stored model."""
import json
import os

import pandas as pd
from remotezip import RemoteZip

from human_extract import ZIPS, parse

F = r"C:\Users\bmens\NQ_local\af3-hitcall\future"
need = pd.read_csv(os.path.join(F, "need_models.csv"))
index = {}
for key, url in ZIPS.items():
    with RemoteZip(url) as z:
        for i in z.infolist():
            if i.filename.endswith(".pdb"):
                index.setdefault(os.path.basename(i.filename), (key, i.filename))
zs = {k: RemoteZip(u) for k, u in ZIPS.items()}
with open(os.path.join(F, "extra_low_models.jsonl"), "w") as out:
    for r in need.itertuples():
        hit = index.get(r.structure_file)
        if not hit:
            print("missing", r.uid); continue
        res = parse(zs[hit[0]].read(hit[1]))
        if res:
            out.write(json.dumps({"unique_ID": r.uid, "id1": r.id1, "id2": r.id2, "group": r.group, "pDockQ": r.pDockQ, "chains": res}) + "\n")
print("fetched", len(need))
