"""PREREG_XLHUMAN: never-solved human pairs that were predicted confidently in 2021 (Burke et al.
AF2/FoldDock) and are independently supported by in-cell crosslinks (Bartolec et al. 2023 PNAS).
Models are the published 2021 ones, streamed by byte range from archive.bioinfo.se.
Committed pre-registration: PREREG_XLHUMAN.md (commit 2a4c8f8)."""
import json
import os
import sys

import io

import numpy as np
import pandas as pd
from remotezip import RemoteZip

AA3 = {"ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E", "GLY": "G", "HIS": "H",
       "ILE": "I", "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P", "SER": "S", "THR": "T", "TRP": "W",
       "TYR": "Y", "VAL": "V", "MSE": "M", "SEC": "U"}


def parse_ca(pdb_bytes):
    """chain -> {nums, seq, xyz}: CA coordinates only, as the pre-registration specifies."""
    chains = {}
    for line in io.TextIOWrapper(io.BytesIO(pdb_bytes), encoding="ascii", errors="replace"):
        if not line.startswith("ATOM") or line[12:16].strip() != "CA":
            continue
        ch, num = line[21], int(line[22:26])
        chains.setdefault(ch, {})[num] = (AA3.get(line[17:20], "X"),
                                          (float(line[30:38]), float(line[38:46]), float(line[46:54])))
    out = {}
    for ch, res in chains.items():
        nums = sorted(res)
        out[ch] = {"nums": nums, "seq": "".join(res[n][0] for n in nums),
                   "xyz": [list(res[n][1]) for n in nums]}
    return out if len(out) == 2 else None

B = r"C:\Users\bmens\NQ_local\af3-hitcall\burke"
L = r"C:\Users\bmens\NQ_local\af3-hitcall\xlhuman"
MODELS = os.path.join(L, "models.jsonl")
ZIPS = {"HuRI": "https://archive.bioinfo.se/huintaf2/HuRI.zip", "humap": "https://archive.bioinfo.se/huintaf2/humap.zip"}
REACH = {"DSSO": 30.0, "DHSO": 30.0, "DMTMM": 25.0}
CLASSES = {"DSSO": ("K", "K"), "DHSO": ("DE", "DE"), "DMTMM": ("K", "DE")}
rng = np.random.default_rng(22)

# ---------- pairs ----------
s1 = pd.read_csv(os.path.join(B, "S1.csv"), low_memory=False)
s1 = s1[s1.structure_file.notna()].copy()
s1["key"] = ["_".join(sorted([a, b])) for a, b in zip(s1.id1, s1.id2)]

links = pd.read_pickle(os.path.join(L, "all_urps.pkl"))
links = links[links["Crosslink Type"].astype(str).str.lower() == "inter"].copy()
for c in ("Protein 1", "Protein 2"):
    links[c] = links[c].astype(str).str.split("-").str[0]
links["key"] = ["_".join(sorted([a, b])) for a, b in zip(links["Protein 1"], links["Protein 2"])]
links = links.rename(columns={"Cross-linker": "xl", "Protein Position 1": "p1", "Protein Position 2": "p2",
                              "Amino Acid 1": "aa1", "Amino Acid 2": "aa2",
                              "Protein 1": "pr1", "Protein 2": "pr2"})
links = links[links.xl.isin(REACH)]

reg = pd.read_csv("registry/open_confident_human_pairs_2026-09-23.csv")
reg["key"] = ["_".join(sorted([a, b])) for a, b in zip(reg.id1, reg.id2)]
cand_keys = sorted(set(reg.key) & set(links.key))

ctrl_pool = s1[(s1.pDockQ < 0.10) & s1.key.isin(set(links.key))].drop_duplicates("key")
ctrl_keys = sorted(ctrl_pool.sample(min(30, len(ctrl_pool)), random_state=22).key)

want = {k: "candidate" for k in cand_keys} | {k: "control" for k in ctrl_keys if k not in cand_keys}
rows = s1[s1.key.isin(want)].drop_duplicates("key").set_index("key")

# ---------- models (streamed once, cached) ----------
cache = {}
if os.path.exists(MODELS):
    for line in open(MODELS):
        d = json.loads(line)
        cache[d["key"]] = d
todo = [k for k in want if k not in cache]
if todo:
    # the Dataset column, not the filename, says which archive a model lives in; try the other as a fallback
    index = {}
    for z, url in ZIPS.items():
        with RemoteZip(url) as rz:
            index[z] = ({os.path.basename(n): n for n in rz.namelist() if n.endswith(".pdb")}, url)
    with open(MODELS, "a") as out:
        for z in ZIPS:
            items = [(k, str(rows.loc[k, "structure_file"])) for k in todo
                     if z.lower() in str(rows.loc[k, "Dataset"]).lower()
                     and os.path.basename(str(rows.loc[k, "structure_file"])) in index[z][0]]
            if not items:
                continue
            with RemoteZip(ZIPS[z]) as rz:
                names = index[z][0]
                for k, f in items:
                    n = names.get(os.path.basename(f))
                    if n is None:
                        out.write(json.dumps({"key": k, "error": "not in zip"}) + "\n")
                        continue
                    p = parse_ca(rz.read(n))
                    if p is None:
                        out.write(json.dumps({"key": k, "error": "not 2 chains"}) + "\n")
                        continue
                    rec = {"key": k, "chains": p}
                    out.write(json.dumps(rec) + "\n")
                    cache[k] = rec
                    print("model", k, flush=True)
print("models cached:", sum(1 for k in want if k in cache and "chains" in cache[k]), "of", len(want))


def ok_class(aa, cls):
    return aa in cls


def test_pair(key):
    rec = cache.get(key)
    if not rec or "chains" not in rec:
        return {"key": key, "status": "no model"}
    (ida, A), (idb, Bc) = sorted(rec["chains"].items())
    acc_a, acc_b = key.split("_")  # chain order in the file follows id1,id2 of the row
    r = rows.loc[key]
    if [r.id1, r.id2] == [acc_b, acc_a]:
        acc_a, acc_b = acc_b, acc_a
    XA, XB = np.array(A["xyz"]), np.array(Bc["xyz"])
    NA, NB = {n: i for i, n in enumerate(A["nums"])}, {n: i for i, n in enumerate(Bc["nums"])}
    sub = links[links.key == key]
    used, failed, dists = [], 0, []
    for t in sub.itertuples():
        # orient the link onto (chain A accession, chain B accession)
        p1, p2, a1, a2, pr1, pr2 = t.p1, t.p2, str(t.aa1), str(t.aa2), t.pr1, t.pr2
        if pr1 == acc_b and pr2 == acc_a:
            p1, p2, a1, a2, pr1, pr2 = p2, p1, a2, a1, pr2, pr1
        if pr1 != acc_a or pr2 != acc_b:
            continue
        c1, c2 = CLASSES[t.xl]
        i, j = NA.get(int(p1)), NB.get(int(p2))
        if i is None or j is None:
            failed += 1
            continue
        if A["seq"][i] != a1 or Bc["seq"][j] != a2 or not (ok_class(a1, c1) and ok_class(a2, c2)):
            failed += 1
            continue
        d = float(np.linalg.norm(XA[i] - XB[j]))
        used.append((int(p1), int(p2), t.xl, round(d, 1), d <= REACH[t.xl]))
        dists.append(d <= REACH[t.xl])
    if len(used) < 2:
        return {"key": key, "status": "untestable (<2 usable links)", "n_usable": len(used), "n_failed_site": failed,
                "links": used}
    frac = float(np.mean(dists))
    # null: random residue pairs of the same classes, same model, 1000 draws
    nulls = []
    for (p1, p2, xl, _, _) in used:
        c1, c2 = CLASSES[xl]
        ia = [i for i, ch in enumerate(A["seq"]) if ch in c1]
        jb = [j for j, ch in enumerate(Bc["seq"]) if ch in c2]
        if not ia or not jb:
            nulls.append(np.zeros(1000))
            continue
        d = np.linalg.norm(XA[rng.choice(ia, 1000)] - XB[rng.choice(jb, 1000)], axis=1)
        nulls.append((d <= REACH[xl]).astype(float))
    null = np.mean(nulls, axis=0)
    p95 = float(np.quantile(null, 0.95))
    return {"key": key, "status": "testable", "n_usable": len(used), "n_failed_site": failed,
            "satisfied_fraction": round(frac, 3), "null_p95": round(p95, 3), "null_mean": round(float(null.mean()), 3),
            "supported": bool(frac >= 0.5 and frac > p95), "links": used}


res = {"n_registry_pairs": len(reg), "n_inter_urps": len(links),
       "n_candidates_with_links": len(cand_keys), "n_controls": len(ctrl_keys)}
cands = [test_pair(k) for k in cand_keys]
ctrls = [test_pair(k) for k in ctrl_keys]
tc = [c for c in cands if c["status"] == "testable"]
tk = [c for c in ctrls if c["status"] == "testable"]
res["candidates_testable"] = len(tc)
res["controls_testable"] = len(tk)
res["controls_supported"] = sum(c["supported"] for c in tk)
res["discrimination_passes"] = bool(len(tk) >= 10 and res["controls_supported"] <= max(3, 0.10 * len(tk)))
res["candidates_supported"] = sum(c["supported"] for c in tc)
res["O1_supported_pairs"] = [c for c in tc if c["supported"]]
res["candidates"] = cands
res["controls"] = ctrls
print(json.dumps({k: v for k, v in res.items() if k not in ("candidates", "controls", "O1_supported_pairs")}, indent=1))
print("\nsupported candidates:")
for c in res["O1_supported_pairs"]:
    print(" ", c["key"], c["n_usable"], "links", c["satisfied_fraction"], "null p95", c["null_p95"], c["links"])
json.dump(res, open("results_xlhuman.json", "w"), indent=1, default=float)
