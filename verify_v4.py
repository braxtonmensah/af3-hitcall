"""PREREG_VERIFY V4 (residue-pair Fnat from coordinates) and V5 (cutoff x threshold grid).
Recomputes everything from coordinates: models (Burke archive / ModelArchive) and reference structures
(RCSB mmCIF, SIFTS-mapped). Independent of the stored interface sets used by F2 / Y1."""
import gzip
import io
import json
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
import requests
from Bio import Align
from remotezip import RemoteZip

from human_extract import ZIPS
from metrics import ci

L = r"C:\Users\bmens\NQ_local\af3-hitcall"
V = os.path.join(L, "verify")
C = os.path.join(V, "coords")
os.makedirs(C, exist_ok=True)
rng = np.random.default_rng(44)
AA = {"ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I",
      "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P", "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V", "MSE": "M"}

D = pd.read_csv(os.path.join(V, "v1_pairs.csv"))
seqs = json.load(open(os.path.join(L, "burke", "uniprot_seqs.json")))
cur = None
for line in open(os.path.join(L, "future_yeast", "proteome.fasta")):
    if line.startswith(">"):
        cur = line.split("|")[1]; seqs[cur] = ""
    else:
        seqs[cur] += line.strip()
aligner = Align.PairwiseAligner(mode="global", open_gap_score=-10, extend_gap_score=-0.5)
aligner.substitution_matrix = Align.substitution_matrices.load("BLOSUM62")


def seqmap(chain_seq, acc):
    """model-chain index -> UniProt position via exact match or alignment (identity >= 0.95)"""
    ref = seqs[acc]
    if chain_seq == ref:
        return list(range(1, len(ref) + 1))
    aln = aligner.align(chain_seq, ref)[0]
    m = [None] * len(chain_seq)
    for (a0, a1), (b0, b1) in zip(*aln.aligned):
        for k in range(a1 - a0):
            if chain_seq[a0 + k] == ref[b0 + k]:
                m[a0 + k] = b0 + k + 1
    return m


def cb_from_pdb_lines(lines, pdb_format):
    ch = defaultdict(dict)
    cols = []
    for line in lines:
        if pdb_format:
            if not line.startswith("ATOM"):
                continue
            name, res, c, num = line[12:16].strip(), line[17:20], line[21], int(line[22:26])
            xyz = (float(line[30:38]), float(line[38:46]), float(line[46:54]))
        else:
            if line.startswith("_atom_site."):
                cols.append(line.strip().split(".", 1)[1]); continue
            if not line.startswith("ATOM"):
                continue
            f = dict(zip(cols, line.split()))
            name, res, c, num = f["label_atom_id"], f["label_comp_id"], f["label_asym_id"], int(f["label_seq_id"])
            xyz = (float(f["Cartn_x"]), float(f["Cartn_y"]), float(f["Cartn_z"]))
        r = ch[c].setdefault(num, {"aa": AA.get(res, "X"), "x": None})
        if name == "CB" or (name == "CA" and (res == "GLY" or r["x"] is None)):
            r["x"] = xyz
    out = []
    for c in sorted(ch):
        nums = sorted(ch[c])
        out.append(("".join(ch[c][n]["aa"] for n in nums), np.array([ch[c][n]["x"] for n in nums], float)))
    return out


# ---------- model coordinates ----------
S1 = pd.read_csv(os.path.join(L, "burke", "S1.csv"), usecols=["unique_ID", "structure_file"], low_memory=False).dropna().drop_duplicates("unique_ID").set_index("unique_ID")
index = {}


def model_coords(r):
    fp = os.path.join(C, f"model_{r.uid}.npz")
    if os.path.exists(fp):
        z = np.load(fp, allow_pickle=True)
        return {k: (z[k + "_pos"], z[k + "_xyz"]) for k in (r.a, r.b)}
    if r.org == "human":
        if not index:
            for key, url in ZIPS.items():
                with RemoteZip(url) as z:
                    for i in z.infolist():
                        if i.filename.endswith(".pdb"):
                            index.setdefault(os.path.basename(i.filename), (key, i.filename))
        sf = S1.loc[r.uid, "structure_file"]
        cand = [x for x in sf.split(";") if x in index]
        if not cand:
            raise KeyError(f"model file not in archive: {sf}")
        key, member = index[cand[0]]
        with RemoteZip(ZIPS[key]) as z:
            chains = cb_from_pdb_lines(io.TextIOWrapper(io.BytesIO(z.read(member)), encoding="ascii", errors="replace"), True)
    else:
        t = requests.get(f"https://www.modelarchive.org/api/projects/{r.uid}?type=basic__model_file_name", timeout=120).text
        chains = cb_from_pdb_lines(t.splitlines(), False)
    out = {}
    for s, x in chains:
        for acc in (r.a, r.b):
            if acc in out:
                continue
            m = seqmap(s, acc)
            if sum(v is not None for v in m) >= 0.9 * len(s):
                keep = [i for i, v in enumerate(m) if v is not None]
                out[acc] = (np.array([m[i] for i in keep]), x[keep])
                break
    np.savez(fp, **{k + "_pos": v[0] for k, v in out.items()}, **{k + "_xyz": v[1] for k, v in out.items()})
    return out


# ---------- reference coordinates ----------
need_entries = set(D.entry)
seg = defaultdict(list)
with gzip.open(os.path.join(L, "future", "pdb_chain_uniprot.tsv.gz"), "rt") as f:
    next(f); next(f)
    for line in f:
        x = line.rstrip("\n").split("\t")
        if x[0] in need_entries:
            try:
                seg[(x[0], x[1])].append((x[2], int(x[3]), int(x[4]), int(x[7])))
            except ValueError:
                pass


def ref_coords(entry, a, b):
    """best (most contacts) chain pair mapping to a and b: {acc: (uniprot positions, xyz)}"""
    fp = os.path.join(C, f"ref_{entry}_{a}_{b}.npz")
    if os.path.exists(fp):
        z = np.load(fp, allow_pickle=True)
        return {k: (z[k + "_pos"], z[k + "_xyz"]) for k in (a, b)}
    chains = {c: s for (e, c), s in seg.items() if e == entry and any(acc in (a, b) for acc, *_ in s)}
    t = requests.get(f"https://files.rcsb.org/download/{entry}.cif.gz", timeout=300).content
    cols, rows = [], defaultdict(dict)
    for line in io.TextIOWrapper(gzip.GzipFile(fileobj=io.BytesIO(t)), encoding="utf-8", errors="replace"):
        if line.startswith("_atom_site."):
            cols.append(line.strip().split(".", 1)[1]); continue
        if not line.startswith("ATOM"):
            continue
        f = dict(zip(cols, line.split()))
        if f.get("pdbx_PDB_model_num", "1") != "1" or f["auth_asym_id"] not in chains or f["label_seq_id"] == ".":
            continue
        name, comp, k = f["label_atom_id"], f["label_comp_id"], int(f["label_seq_id"])
        if not (name == "CB" or (name == "CA" and comp == "GLY")):
            continue
        for acc, rb, re_, sb in chains[f["auth_asym_id"]]:
            if rb <= k <= re_ and acc in (a, b):
                rows[f["auth_asym_id"]][k] = (acc, sb + k - rb, float(f["Cartn_x"]), float(f["Cartn_y"]), float(f["Cartn_z"]))
                break
    best, bestn = None, -1
    ids = sorted(rows)
    for i in ids:
        for j in ids:
            A, B_ = list(rows[i].values()), list(rows[j].values())
            if i >= j or not A or not B_ or {x[0] for x in A} == {x[0] for x in B_}:
                continue
            xa, xb = np.array([x[2:] for x in A]), np.array([x[2:] for x in B_])
            n = int((np.sqrt(((xa[:, None] - xb[None]) ** 2).sum(-1)) < 8).sum())
            if n > bestn:
                best, bestn = (A, B_), n
    out = {}
    for grp in best:
        acc = grp[0][0]
        out[acc] = (np.array([x[1] for x in grp]), np.array([x[2:] for x in grp], float))
    np.savez(fp, **{k + "_pos": v[0] for k, v in out.items()}, **{k + "_xyz": v[1] for k, v in out.items()})
    return out


def contacts(c, a, b, cut):
    pa, xa = c[a]; pb, xb = c[b]
    Dm = np.sqrt(((xa[:, None] - xb[None]) ** 2).sum(-1)) < cut
    i, j = np.nonzero(Dm)
    return {(int(pa[x]), int(pb[y])) for x, y in zip(i, j)}


rows = []


def work(r):
    try:
        m, n = model_coords(r), ref_coords(r.entry, r.a, r.b)
        if len(m) < 2 or len(n) < 2:
            return dict(uid=r.uid, status="unmapped")
        obs_a, obs_b = set(n[r.a][0].tolist()), set(n[r.b][0].tolist())
        out = dict(uid=r.uid, status="ok")
        for cut in (6, 8, 10):
            nat = contacts(n, r.a, r.b, cut)
            mod = {p for p in contacts(m, r.a, r.b, cut) if p[0] in obs_a and p[1] in obs_b}
            out[f"fnat_{cut}"] = len(nat & mod) / len(nat) if nat else np.nan
            E = {("a", p[0]) for p in nat} | {("b", p[1]) for p in nat}
            P = {("a", p[0]) for p in mod} | {("b", p[1]) for p in mod}
            out[f"f1set_{cut}"] = 2 * len(P & E) / (len(P) + len(E)) if (P or E) else 0.0
        return out
    except Exception as ex:
        return dict(uid=r.uid, status=f"error {type(ex).__name__}: {ex}"[:120])


with ThreadPoolExecutor(6) as ex:
    rows = list(ex.map(work, D.itertuples()))
R = D.merge(pd.DataFrame(rows), on="uid")
R.to_csv(os.path.join(V, "v4_pairs.csv"), index=False)
ok = R[R.status == "ok"]


def frac(v):
    v = np.asarray(v, float)
    if not len(v):
        return None
    bs = [rng.choice(v, len(v)).mean() for _ in range(2000)]
    return {"n": int(len(v)), "frac": float(v.mean()), "ci95": ci(np.array(bs), 0.95).tolist()}


res = {"status": R.status.value_counts().to_dict(), "V4": {}, "V5_human_confident": {}}
for org in ("human", "yeast"):
    for grp in ("confident", "low"):
        s = ok[(ok.org == org) & (ok.group == grp)]
        if not len(s):
            continue
        for lab, m in (("all", s.index == s.index), ("no_homolog_precedent", ~s["prec_id0.25"].astype(bool))):
            t = s[m]
            res["V4"][f"{org}|{grp}|{lab}"] = {"fnat_ge_0.3": frac(t.fnat_8 >= 0.3), "median_fnat": float(t.fnat_8.median()) if len(t) else None,
                                               "agreement_with_F1_rule": float(((t.fnat_8 >= 0.3) == (t.f1 >= 0.5)).mean()) if len(t) else None}
hc = ok[(ok.org == "human") & (ok.group == "confident")]
for cut in (6, 8, 10):
    for th in (0.3, 0.5, 0.7):
        res["V5_human_confident"][f"cut{cut}_F1>={th}"] = float((hc[f"f1set_{cut}"] >= th).mean())
print(json.dumps(res, indent=1, default=float))
json.dump(res, open("results_verify_v4.json", "w"), indent=1, default=float)
