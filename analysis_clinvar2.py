"""PREREG_CLINVAR2.md: surface-matched pathogenic-vs-benign enrichment at predicted interfaces."""
import json
import os
import re
from collections import defaultdict

import numpy as np

from metrics import ci

B = r"C:\Users\bmens\NQ_local\af3-hitcall\burke"
rng = np.random.default_rng(11)
THREE = {"Ala": "A", "Arg": "R", "Asn": "N", "Asp": "D", "Cys": "C", "Gln": "Q", "Glu": "E", "Gly": "G", "His": "H", "Ile": "I",
         "Leu": "L", "Lys": "K", "Met": "M", "Phe": "F", "Pro": "P", "Ser": "S", "Thr": "T", "Trp": "W", "Tyr": "Y", "Val": "V"}

# humsavar: accession -> {position: set(categories)}, with the wild-type residue for a sanity check
var = defaultdict(lambda: defaultdict(set))
wt = {}
pat = re.compile(r"^\S+\s+(\S+)\s+VAR_\d+\s+p\.([A-Z][a-z]{2})(\d+)([A-Z][a-z]{2})\s+(LP/P|LB/B|US)\b")
for line in open(os.path.join(B, "humsavar.txt"), encoding="utf-8", errors="replace"):
    m = pat.match(line)
    if not m:
        continue
    acc, w, pos, _, cat = m.groups()
    if cat == "US":
        continue
    var[acc][int(pos)].add("P" if cat == "LP/P" else "B")
    wt[(acc, int(pos))] = THREE.get(w, "X")
print("humsavar proteins with P/B variants:", len(var))

seqs = json.load(open(os.path.join(B, "uniprot_seqs.json")))
recs = [json.loads(l) for l in open(os.path.join(B, "interfaces_v2.jsonl"))]
print("models:", len(recs))

# per (group, protein) counts a,b,c,d over residues with pLDDT >= 70
cells = defaultdict(lambda: np.zeros(4))
cover = defaultdict(lambda: [0, 0])
wt_ok = wt_bad = 0
for r in recs:
    for ch in r["chains"].values():
        cover[r["group"]][1] += 1
        acc = next((a for a in (r["id1"], r["id2"]) if seqs.get(a) == ch["seq"]), None)
        if acc is None:
            continue
        cover[r["group"]][0] += 1
        iface = set(ch["iface"])
        cnv = np.array(ch["cn"])
        ordered = np.array(ch["plddt"]) >= 70
        if ordered.sum() < 5:
            continue
        med = np.median(cnv[ordered])  # chain median CN among ordered residues
        for k, pl in enumerate(ch["plddt"]):
            if pl < 70 or cnv[k] >= med:  # surface, ordered residues only
                continue
            pos = k + 1  # exact-sequence match -> index k is UniProt position k+1
            cats = var.get(acc, {}).get(pos)
            if not cats:
                continue
            if wt.get((acc, pos)) == ch["seq"][k]:
                wt_ok += 1
            else:
                wt_bad += 1
            at = k in iface
            if "P" in cats:
                cells[(r["group"], acc)][0 if at else 1] += 1
            if "B" in cats:
                cells[(r["group"], acc)][2 if at else 3] += 1
print("wild-type residue check: match", wt_ok, "mismatch", wt_bad)
print("chain coverage (exact UniProt match / total):", {g: v for g, v in cover.items()})

groups = ["novel", "precedented", "control"]
prot = {g: sorted(a for (gg, a) in cells if gg == g) for g in groups}
allp = sorted({a for (_, a) in cells})
pidx = {a: k for k, a in enumerate(allp)}
M = {g: np.array([cells[(g, a)] for a in prot[g]]) for g in groups}
I = {g: np.array([pidx[a] for a in prot[g]]) for g in groups}


def orr(tab):
    a, b, c, d = tab + 0.5
    return (a / b) / (c / d)


point = {g: orr(M[g].sum(0)) for g in groups}
counts = {g: M[g].sum(0).astype(int).tolist() for g in groups}
bs = defaultdict(list)
for _ in range(2000):
    w = np.bincount(rng.integers(0, len(allp), len(allp)), minlength=len(allp)).astype(float)
    o = {g: orr((M[g] * w[I[g]][:, None]).sum(0)) for g in groups}
    bs["novel/control"].append(o["novel"] / o["control"])
    bs["precedented/control"].append(o["precedented"] / o["control"])
    bs["precedented/novel"].append(o["precedented"] / o["novel"])
    for g in groups:
        bs[g].append(o[g])
res = {"counts_[P_iface,P_else,B_iface,B_else]": counts, "OR": point,
       "OR_ci95": {g: ci(np.array(bs[g]), 0.95).tolist() for g in groups}}
for k in ["novel/control", "precedented/control", "precedented/novel"]:
    num, den = k.split("/")
    res[k] = {"ratio": point[num] / point[den], "ci95": ci(np.array(bs[k]), 0.95).tolist()}
t2 = res["OR_ci95"]["precedented"][0] > 1
t1 = res["OR_ci95"]["novel"][0] > 1
lo3, hi3 = res["precedented/novel"]["ci95"]
res["T2_positive_control_passes"] = bool(t2)
res["T1_novel_interfaces_carry_disease_signal"] = bool(t1) if t2 else "not interpreted (T2 failed)"
res["T3"] = ("precedented stronger" if lo3 > 1 else "comparable" if lo3 <= 1 <= hi3 else "novel stronger") if t2 else "not interpreted"
print(json.dumps(res, indent=1, default=float))
json.dump(res, open("results_clinvar2.json", "w"), indent=1, default=float)
