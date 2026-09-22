"""PREREG_CLINVAR: stream FoldDock models by byte range and keep only per-chain sequence, pLDDT and
interface residues (CB/CA within 8 A of the other chain). Resumable; writes JSONL."""
import io
import json
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
from remotezip import RemoteZip

B = r"C:\Users\bmens\NQ_local\af3-hitcall\burke"
OUT = os.path.join(B, sys.argv[2] if len(sys.argv) > 2 else "interfaces.jsonl")
ZIPS = {"HuRI": "https://archive.bioinfo.se/huintaf2/HuRI.zip", "humap": "https://archive.bioinfo.se/huintaf2/humap.zip"}
AA = {"ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I",
      "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P", "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
      "MSE": "M", "SEC": "U"}


def select():
    d = pd.read_csv(os.path.join(B, "S1.csv"), low_memory=False)
    d = d[d.structure_file.notna()].copy()
    d["prec"] = d.int3D_model_structure.astype(int) == 1
    conf = d[d.pDockQ > 0.23].assign(group=lambda x: np.where(x.prec, "precedented", "novel"))
    ctrl = d[d.pDockQ < 0.10].sample(1500, random_state=7).assign(group="control")
    return pd.concat([conf, ctrl])


def parse(pdb_bytes):
    chains = {}
    for line in io.TextIOWrapper(io.BytesIO(pdb_bytes), encoding="ascii", errors="replace"):
        if not line.startswith("ATOM"):
            continue
        name, res, ch = line[12:16].strip(), line[17:20], line[21]
        num = int(line[22:26])
        c = chains.setdefault(ch, {})
        r = c.setdefault(num, {"aa": AA.get(res, "X"), "ca": None, "cb": None, "plddt": float(line[60:66])})
        xyz = (float(line[30:38]), float(line[38:46]), float(line[46:54]))
        if name == "CA":
            r["ca"] = xyz
        elif name == "CB":
            r["cb"] = xyz
    out = {}
    for ch, res in chains.items():
        nums = sorted(res)
        coords = np.array([res[n]["cb"] or res[n]["ca"] for n in nums], float)
        out[ch] = {"nums": nums, "seq": "".join(res[n]["aa"] for n in nums),
                   "plddt": [round(res[n]["plddt"], 1) for n in nums], "xyz": coords}
    ids = sorted(out)
    if len(ids) != 2:
        return None
    a, b = out[ids[0]], out[ids[1]]
    D = np.sqrt(((a["xyz"][:, None, :] - b["xyz"][None, :, :]) ** 2).sum(-1))

    def cn(x):  # contact number: same-chain CB/CA within 10 A (monomer burial)
        dd = np.sqrt(((x[:, None, :] - x[None, :, :]) ** 2).sum(-1))
        return ((dd < 10).sum(1) - 1).astype(int).tolist()

    ia, ib = (D < 8).any(1), (D < 8).any(0)
    res = {}
    for ch, c, m in [(ids[0], a, ia), (ids[1], b, ib)]:
        res[ch] = {"seq": c["seq"], "start": c["nums"][0], "plddt": c["plddt"],
                   "iface": [int(k) for k in np.flatnonzero(m)], "cn": cn(c["xyz"])}  # 0-based index into seq
    return res


local = threading.local()


def zipfor(key):
    if not hasattr(local, "z"):
        local.z = {}
    if key not in local.z:
        local.z[key] = RemoteZip(ZIPS[key])
    return local.z[key]


def main():
    sel = select()
    done = set()
    if os.path.exists(OUT):
        for line in open(OUT):
            done.add(json.loads(line)["unique_ID"])
    # index members once
    index = {}
    for key, url in ZIPS.items():
        with RemoteZip(url) as z:
            for i in z.infolist():
                if i.filename.endswith(".pdb"):
                    index.setdefault(os.path.basename(i.filename), (key, i.filename))
    print("indexed pdb members", len(index), flush=True)
    todo = [r for r in sel.itertuples() if r.unique_ID not in done]
    print("selected", len(sel), "todo", len(todo), sel.group.value_counts().to_dict(), flush=True)
    lock = threading.Lock()
    miss = 0

    def work(r):
        nonlocal miss
        hit = index.get(r.structure_file)
        if not hit:
            with lock:
                miss += 1
            return
        key, member = hit
        try:
            data = zipfor(key).read(member)
            res = parse(data)
        except Exception as e:  # network hiccup: skip, rerun resumes
            print("ERR", r.unique_ID, e, flush=True)
            return
        if res is None:
            return
        rec = {"unique_ID": r.unique_ID, "id1": r.id1, "id2": r.id2, "group": r.group, "pDockQ": r.pDockQ,
               "prec": bool(r.prec), "chains": res}
        with lock:
            with open(OUT, "a") as f:
                f.write(json.dumps(rec) + "\n")

    with ThreadPoolExecutor(int(sys.argv[1]) if len(sys.argv) > 1 else 8) as ex:
        for k, _ in enumerate(ex.map(work, todo)):
            if k % 500 == 0:
                print("progress", k, "/", len(todo), "missing", miss, flush=True)
    print("done; missing members", miss, flush=True)


if __name__ == "__main__":
    main()
