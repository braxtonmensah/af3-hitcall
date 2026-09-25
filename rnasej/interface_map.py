"""POST HOC (2026-09-25), descriptive: map the RNase J : MG423-homolog interface in the AF3 heterotetramer
and gather the facts that decide whether it is a plausible drug target.

1. Catalytic motifs: does MG423/MPN_621 keep the metallo-beta-lactamase + beta-CASP catalytic residues?
2. Interface: all-atom contacts (<= 5 A) between RNase J and its partner, per residue, per interface type.
3. Human off-target: identity of RNase J and of the interface residues to human CPSF73/CPSF3 (the closest
   human beta-CASP nuclease, itself a drug target) and to human CPSF100.
No claim of druggability follows from geometry alone; this only reports the measurable parts.
"""
import gzip
import io
import json
import os
import zipfile
from collections import defaultdict

import numpy as np
import requests
from Bio import Align

HERE = os.path.dirname(os.path.abspath(__file__))
RES = r"C:\Users\bmens\NQ_local\af3-hitcall\rnasej_results"
CUT = 5.0
J_CHAINS, P_CHAINS = ["A", "B"], ["C", "D"]
aligner = Align.PairwiseAligner(mode="global", open_gap_score=-11, extend_gap_score=-1)
aligner.substitution_matrix = Align.substitution_matrices.load("BLOSUM62")


def useq(acc):
    return requests.get(f"https://rest.uniprot.org/uniprotkb/{acc}.fasta", timeout=60).text.split("\n", 1)[1].replace("\n", "")


SEQ = {k: useq(v) for k, v in {"RNaseJ_MPN": "P75497", "MG423_MPN": "P75174", "BsRNaseJ1": "Q45493",
                               "hCPSF73": "Q9UKF6", "hCPSF100": "Q9P2I0"}.items()}


def amap(a, b):
    """position in a (1-based) -> position in b (1-based), plus % identity over aligned"""
    al = aligner.align(SEQ[a], SEQ[b])[0]
    m, same, tot = {}, 0, 0
    for (x0, x1), (y0, y1) in zip(*al.aligned):
        for k in range(x1 - x0):
            m[x0 + k + 1] = y0 + k + 1
            same += SEQ[a][x0 + k] == SEQ[b][y0 + k]
            tot += 1
    return m, (same / tot if tot else 0), tot


def atoms(cif):
    out = defaultdict(list)
    cols = []
    for line in cif.splitlines():
        if line.startswith("_atom_site."):
            cols.append(line.strip().split(".", 1)[1]); continue
        if not line.startswith("ATOM"):
            continue
        f = dict(zip(cols, line.split()))
        out[f["label_asym_id"]].append((int(f["label_seq_id"]), f["label_comp_id"],
                                       float(f["Cartn_x"]), float(f["Cartn_y"]), float(f["Cartn_z"])))
    return out


with zipfile.ZipFile(os.path.join(RES, "fold_rnasej_mpn_2x2.zip")) as z:
    cif = z.read(next(n for n in z.namelist() if n.endswith("_model_0.cif"))).decode()
A = atoms(cif)
res = {"chains": {k: len({r[0] for r in v}) for k, v in A.items()}}

# ---- 1. catalytic residues ----
# B. subtilis RNase J1 metallo-beta-lactamase / beta-CASP catalytic set (Newman 2011, Li de la Sierra-Gallay 2008):
# motif I H76, motif II H78 D79 H80, motif III H143, motif IV D164(?), beta-CASP H368, plus D78/H80 zinc ligands.
# genuine catalytic/Zn-ligand set only, verified below against the BsJ1 sequence itself
BS_CAT = [76, 78, 79, 368]
cat = {}
for tgt in ("RNaseJ_MPN", "MG423_MPN", "hCPSF73"):
    m, ident, n = amap("BsRNaseJ1", tgt)
    cat[tgt] = {"identity_to_BsJ1": round(ident, 3), "aligned": n,
                "catalytic": {p: (SEQ[tgt][m[p] - 1] + str(m[p]) if p in m else None) for p in BS_CAT}}
    cat[tgt]["catalytic_conserved"] = sum(1 for p in BS_CAT if p in m and SEQ[tgt][m[p] - 1] == SEQ["BsRNaseJ1"][p - 1])
res["BsJ1_residues_at_catalytic_positions"] = {p: SEQ["BsRNaseJ1"][p - 1] + str(p) for p in BS_CAT}
res["catalytic"] = cat

# ---- 2. interface contacts ----
def contacts(c1, c2):
    a1, a2 = A[c1], A[c2]
    x1 = np.array([r[2:] for r in a1]); x2 = np.array([r[2:] for r in a2])
    pairs = set()
    for k in range(0, len(x1), 2000):
        D = np.sqrt(((x1[k:k + 2000, None] - x2[None]) ** 2).sum(-1)) <= CUT
        for i, j in zip(*np.nonzero(D)):
            pairs.add((a1[k + i][0], a2[j][0]))
    return pairs


iface = {}
for j in J_CHAINS:
    for p in P_CHAINS:
        iface[f"{j}-{p}"] = contacts(j, p)
iface["A-B_JJ"] = contacts("A", "B")
iface["C-D_PP"] = contacts("C", "D")
res["interface_sizes"] = {k: len(v) for k, v in iface.items()}
main = max((k for k in iface if "-" in k and k[0] in "AB" and k[2] in "CD"), key=lambda k: len(iface[k]))
res["primary_J_partner_interface"] = main
Jres = sorted({a for a, b in iface[main]})
Pres = sorted({b for a, b in iface[main]})
res["interface_residues"] = {
    "RNaseJ": [SEQ["RNaseJ_MPN"][i - 1] + str(i) for i in Jres],
    "MG423_MPN621": [SEQ["MG423_MPN"][i - 1] + str(i) for i in Pres]}
res["n_interface_residues"] = {"RNaseJ": len(Jres), "partner": len(Pres)}

# ---- 3. human off-target at those residues ----
off = {}
for h in ("hCPSF73", "hCPSF100"):
    m, ident, n = amap("RNaseJ_MPN", h)
    hit = [i for i in Jres if i in m and SEQ["RNaseJ_MPN"][i - 1] == SEQ[h][m[i] - 1]]
    off[h] = {"whole_protein_identity": round(ident, 3), "aligned": n,
              "interface_residues_aligned": sum(i in m for i in Jres),
              "interface_residues_identical": len(hit),
              "interface_identity_pct": round(100 * len(hit) / max(len(Jres), 1), 1)}
res["human_offtarget"] = off
print(json.dumps(res, indent=1, default=str)[:4000])
json.dump({k: v for k, v in res.items()}, open(os.path.join(HERE, "results_interface.json"), "w"), indent=1, default=str)
