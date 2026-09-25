"""PREREG_TETRA: place two copies of the AF3 MG139-MG423 heterodimer on solved RNase J tetramer templates and
test whether the replicated far crosslinks are satisfied across copies."""
import gzip
import io
import itertools
import json
import os

import numpy as np
import pandas as pd
import requests
from Bio import Align

L = r"C:\Users\bmens\NQ_local\af3-hitcall"
rng = np.random.default_rng(20)
TEMPLATES = ["3ZQ4", "4XWW", "7WNU", "8CGL", "5WS2", "6LLB"]
NEAR = [(120, 502), (120, 546), (409, 322)]
FAR = [(225, 224), (228, 224), (257, 224)]
LINKS = NEAR + FAR
AA = {"ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I",
      "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P", "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V", "MSE": "M"}
P = pd.read_csv(os.path.join(L, "data", "proteins.csv")).set_index("locus_tag")
SEQ = {g: P.loc[g, "aa_sequence"].rstrip("*") for g in ("MG_139", "MG_423")}
al = Align.PairwiseAligner(mode="global", open_gap_score=-10, extend_gap_score=-0.5)
al.substitution_matrix = Align.substitution_matrices.load("BLOSUM62")


def template(pid):
    t = requests.get(f"https://files.rcsb.org/download/{pid}.cif.gz", timeout=120).content
    cols, ch = [], {}
    for line in io.TextIOWrapper(gzip.GzipFile(fileobj=io.BytesIO(t)), encoding="utf-8", errors="replace"):
        if line.startswith("_atom_site."):
            cols.append(line.strip().split(".", 1)[1]); continue
        if not line.startswith("ATOM"):
            continue
        f = dict(zip(cols, line.split()))
        if f["label_atom_id"] != "CA" or f.get("pdbx_PDB_model_num", "1") != "1" or f["label_comp_id"] not in AA:
            continue
        c = ch.setdefault(f["auth_asym_id"], {"seq": [], "xyz": []})
        c["seq"].append(AA[f["label_comp_id"]]); c["xyz"].append((float(f["Cartn_x"]), float(f["Cartn_y"]), float(f["Cartn_z"])))
    return {k: ("".join(v["seq"]), np.array(v["xyz"])) for k, v in ch.items() if len(v["seq"]) > 200}


def pairs(qseq, tseq):
    a = al.align(qseq, tseq)[0]
    out = []
    for (a0, a1), (b0, b1) in zip(*a.aligned):
        out += list(zip(range(a0, a1), range(b0, b1)))
    return np.array(out)


def kabsch(P_, Q_):
    pc, qc = P_.mean(0), Q_.mean(0)
    U, S, Vt = np.linalg.svd((P_ - pc).T @ (Q_ - qc))
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    R = Vt.T @ np.diag([1, 1, d]) @ U.T
    return R, qc - R @ pc


def place(x139, x423, tchains, X):
    """superpose MG139 on template chain X; return transformed (MG139, MG423) and per-chain MG423 RMSD"""
    pr = pairs(SEQ["MG_139"], tchains[X][0])
    R, t = kabsch(x139[pr[:, 0]], tchains[X][1][pr[:, 1]])
    a, b = x139 @ R.T + t, x423 @ R.T + t
    rms = {}
    for Y, (s, xy) in tchains.items():
        if Y == X:
            continue
        p2 = pairs(SEQ["MG_423"], s)
        rms[Y] = float(np.sqrt(((b[p2[:, 0]] - xy[p2[:, 1]]) ** 2).sum(1).mean()))
    return a, b, rms


def mind(copies, i, j):
    return min(np.linalg.norm(a[i - 1] - b[j - 1]) for a, _ in copies for _, b in copies)


z = np.load(os.path.join(L, "structs_ca", "250310_mgen_allbyall_1052.npz"))
loci, ch = list(z["loci"]), z["chain"]
K139 = [k + 1 for k, c in enumerate(SEQ["MG_139"]) if c == "K"]
K423 = [k + 1 for k, c in enumerate(SEQ["MG_423"]) if c == "K"]
res = {}
for pid in TEMPLATES:
    try:
        T = template(pid)
    except Exception as e:
        res[pid] = {"error": str(e)}; continue
    if len(T) < 4:
        res[pid] = {"error": f"{len(T)} protein chains"}; continue
    samples = []
    for k in range(5):
        xyz = z[f"xyz{k}"].astype(float)
        x139, x423 = xyz[ch == loci.index("MG_139")], xyz[ch == loci.index("MG_423")]
        best = None
        for X in T:  # copy 1 anchored on X; its MG423 chain Y = best overlap
            a1, b1, rms1 = place(x139, x423, T, X)
            Y = min(rms1, key=rms1.get)
            for Z in T:  # copy 2 on another chain Z, its MG423 on the remaining chain W
                if Z in (X, Y):
                    continue
                W = next(c for c in T if c not in (X, Y, Z))
                a2, b2, rms2 = place(x139, x423, T, Z)
                score = rms1[Y] + rms2[W]
                if best is None or score < best[0]:
                    best = (score, X, Y, Z, W, rms1[Y], rms2[W], [(a1, b1), (a2, b2)])
        _, X, Y, Z, W, r1, r2, copies = best
        d = [mind(copies, i, j) for i, j in LINKS]
        clash = int(sum((np.linalg.norm(copies[0][m][:, None] - copies[1][n][None], axis=-1) < 3).sum() for m in (0, 1) for n in (0, 1)))
        null = []
        for _ in range(1000):
            rr = [(rng.choice(K139), rng.choice(K423)) for _ in LINKS]
            null.append(np.mean([mind(copies, i, j) <= 30 for i, j in rr]))
        sat = np.array(d) <= 30
        samples.append({"pairing": f"{X}{Y}+{Z}{W}", "mg423_fit_rmsd": [round(r1, 1), round(r2, 1)], "dist": [round(v, 1) for v in d],
                        "near_ok": bool(sat[:3].all()), "far_ok": bool(sat[3:].all()), "frac": float(sat.mean()),
                        "null_p95": float(np.quantile(null, 0.95)), "clash_pairs": clash})
    ok = [s["near_ok"] and s["far_ok"] and s["frac"] > s["null_p95"] and s["clash_pairs"] <= 20 for s in samples]
    res[pid] = {"samples": samples, "supported": sum(ok) >= 3}
    print(pid, "supported" if res[pid]["supported"] else "not", [(s["pairing"], s["dist"], s["clash_pairs"]) for s in samples[:2]])
res["VERDICT"] = "HETEROTETRAMER SUPPORTED" if any(v.get("supported") for v in res.values() if isinstance(v, dict)) else "NOT SUPPORTED"
print(res["VERDICT"])
json.dump(res, open("results_tetra.json", "w"), indent=1, default=float)
