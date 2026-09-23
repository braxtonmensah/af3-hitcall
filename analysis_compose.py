"""PREREG_COMPOSE: recover AF's missed (non-autonomous) interfaces by composing autonomous A-C and B-C
models on their shared partner C, scored against 2022+ structures exactly as FUTURE F2."""
import gzip
import io
import json
import os
from collections import defaultdict
from math import comb

import numpy as np
import pandas as pd
from remotezip import RemoteZip

from human_extract import ZIPS

FU = r"C:\Users\bmens\NQ_local\af3-hitcall\future"
B = r"C:\Users\bmens\NQ_local\af3-hitcall\burke"
AA = {"ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I",
      "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P", "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V"}
seqs = json.load(open(os.path.join(B, "uniprot_seqs.json")))
H = pd.read_csv(os.path.join(FU, "coop_armH.csv"))
P = pd.read_csv(os.path.join(FU, "pairs.csv")).set_index("uid")
ents = set(H.entry)
chmap = defaultdict(dict)
with gzip.open(os.path.join(FU, "pdb_chain_uniprot.tsv.gz"), "rt") as f:
    next(f); next(f)
    for line in f:
        x = line.split("\t")
        if x[0] in ents:
            chmap[x[0]][x[1]] = x[2]
S1 = pd.read_csv(os.path.join(B, "S1.csv"), usecols=["id1", "id2", "pDockQ", "structure_file"], low_memory=False).dropna(subset=["structure_file"])
best_model = {}
for a, b, q, sf in zip(S1.id1, S1.id2, S1.pDockQ, S1.structure_file):
    k = frozenset((a, b))
    if k not in best_model or q > best_model[k][0]:
        best_model[k] = (q, sf)

index = {}
for key, url in ZIPS.items():
    with RemoteZip(url) as z:
        for i in z.infolist():
            if i.filename.endswith(".pdb"):
                index.setdefault(os.path.basename(i.filename), (key, i.filename))
zs = {k: RemoteZip(u) for k, u in ZIPS.items()}


def load_model(a, b):
    """{acc: (positions 1-based, CB xyz, plddt)} for a Burke model, exact-sequence mapped"""
    sf = best_model[frozenset((a, b))][1]
    key, member = index[sf]
    chains = defaultdict(dict)
    for line in io.TextIOWrapper(io.BytesIO(zs[key].read(member)), encoding="ascii", errors="replace"):
        if not line.startswith("ATOM"):
            continue
        name, res, ch, num = line[12:16].strip(), line[17:20], line[21], int(line[22:26])
        r = chains[ch].setdefault(num, {"aa": AA.get(res, "X"), "ca": None, "cb": None, "pl": float(line[60:66])})
        xyz = (float(line[30:38]), float(line[38:46]), float(line[46:54]))
        if name == "CA":
            r["ca"] = xyz
        elif name == "CB":
            r["cb"] = xyz
    out = {}
    for ch, rr in chains.items():
        nums = sorted(rr)
        s = "".join(rr[n]["aa"] for n in nums)
        acc = next((x for x in (a, b) if seqs.get(x) == s), None)
        if acc:
            out[acc] = (np.arange(1, len(nums) + 1), np.array([rr[n]["cb"] or rr[n]["ca"] for n in nums]), np.array([rr[n]["pl"] for n in nums]))
    return out if len(out) == 2 else None


def kabsch(Pm, Qm):
    """rotation R, translation t such that R @ p + t ~ q"""
    pc, qc = Pm.mean(0), Qm.mean(0)
    Hm = (Pm - pc).T @ (Qm - qc)
    U, S, Vt = np.linalg.svd(Hm)
    dd = np.sign(np.linalg.det(Vt.T @ U.T))
    R = Vt.T @ np.diag([1, 1, dd]) @ U.T
    return R, qc - R @ pc


def exp_iface(uid, a, b):
    r = P.loc[uid]
    top = None
    for e in str(r.new_entries).split():
        for c in json.load(open(os.path.join(FU, "entry_contacts", e + ".json"))):
            if set(c["acc"]) == {a, b} and (top is None or c["n_contacts"] > top["n_contacts"]):
                top = c
    E, O = set(), set()
    for k, acc in enumerate(top["acc"]):
        E |= {(acc, x) for x in top["iface"][k]}
        O |= {(acc, x) for x in top["observed"][k]}
    return E, O


def f1(Pset, E, O):
    Pp = Pset & O
    return 2 * len(Pp & E) / (len(Pp) + len(E)) if (Pp or E) else 0.0


models = {}
for fn in [os.path.join(B, "interfaces_v2.jsonl"), os.path.join(FU, "extra_low_models.jsonl")]:
    for line in open(fn):
        rec = json.loads(line)
        models[rec["unique_ID"]] = rec


def pairwise_iface(uid):
    rec = models.get(uid)
    if not rec:
        return None
    out = set()
    got = 0
    for ch in rec["chains"].values():
        acc = next((x for x in (rec["id1"], rec["id2"]) if seqs.get(x) == ch["seq"]), None)
        if acc:
            got += 1
            out |= {(acc, k + 1) for k in ch["iface"]}
    return out if got == 2 else None


rows = []
for r in H.itertuples():
    a, b = P.loc[r.uid, "id1"], P.loc[r.uid, "id2"]
    cands = [c for c in set(chmap[r.entry].values()) - {a, b} if frozenset((a, c)) in best_model and frozenset((b, c)) in best_model]
    if not cands:
        continue
    c = max(cands, key=lambda x: min(best_model[frozenset((a, x))][0], best_model[frozenset((b, x))][0]))
    qmin = min(best_model[frozenset((a, c))][0], best_model[frozenset((b, c))][0])
    row = dict(uid=r.uid, group=r.group, entry=r.entry, C=c, qmin=qmin, status="ok")
    try:
        mac, mbc = load_model(a, c), load_model(b, c)
    except Exception as ex:
        row["status"] = f"fetch error {ex}"
        rows.append(row); continue
    if not mac or not mbc:
        row["status"] = "no exact-seq mapping"
        rows.append(row); continue
    _, c1, pl1 = mac[c]
    _, c2, pl2 = mbc[c]
    good = (pl1 >= 70) & (pl2 >= 70)
    if good.sum() < 30:
        row["status"] = "C too disordered"
        rows.append(row); continue
    R, t = kabsch(c2[good], c1[good])  # move the B-C frame onto the A-C frame
    posA, xa, _ = mac[a]
    posB, xb, _ = mbc[b]
    xb = xb @ R.T + t
    D = np.sqrt(((xa[:, None] - xb[None]) ** 2).sum(-1))
    comp = {(a, int(p)) for p in posA[(D < 8).any(1)]} | {(b, int(p)) for p in posB[(D < 8).any(0)]}
    E, O = exp_iface(r.uid, a, b)
    pw = pairwise_iface(r.uid)
    row.update(rmsd_C=float(np.sqrt((((c2[good] @ R.T + t) - c1[good]) ** 2).sum(1).mean())),
               clash=int((D < 3).sum()) > 10, n_comp=len(comp), f1_comp=f1(comp, E, O),
               f1_pair=f1(pw, E, O) if pw is not None else np.nan)
    rows.append(row)
    print(row, flush=True)

K = pd.DataFrame(rows)
K.to_csv(os.path.join(FU, "compose_pairs.csv"), index=False)
ok = K[K.status == "ok"].copy()
ok["comp_ok"] = ok.f1_comp >= 0.5
ok["pair_ok"] = ok.f1_pair >= 0.5


def sign_test(d):
    """one-sided exact test on discordant pairs: composition right & pairwise wrong vs the reverse"""
    x = int((d.comp_ok & ~d.pair_ok).sum()); y = int((~d.comp_ok & d.pair_ok).sum())
    nn = x + y
    p = sum(comb(nn, k) for k in range(x, nn + 1)) / 2 ** nn if nn else 1.0
    return x, y, p


res = {"status_counts": {f"{g}|{s}": int(v) for (g, s), v in K.groupby(["group", "status"]).size().items()}}
for lab, sub in [("K1_misses_confidentC", ok[(ok.group == "low") & (ok.qmin > 0.23)]),
                 ("K2_misses_anyC", ok[ok.group == "low"]),
                 ("K3_hits_confidentC", ok[(ok.group == "confident") & (ok.qmin > 0.23)])]:
    x, y, pval = sign_test(sub.dropna(subset=["f1_pair"]))
    res[lab] = {"n": len(sub), "composition_correct": int(sub.comp_ok.sum()), "pairwise_correct": int(sub.pair_ok.sum()),
                "median_f1_comp": float(sub.f1_comp.median()) if len(sub) else None,
                "median_f1_pair": float(sub.f1_pair.median()) if len(sub) else None,
                "discordant_comp_only": x, "discordant_pair_only": y, "one_sided_p": pval,
                "clash_frac": float(sub.clash.mean()) if len(sub) else None}
k1 = res["K1_misses_confidentC"]
res["K1_verdict"] = "RESCUE" if k1["one_sided_p"] < 0.05 and k1["composition_correct"] >= 5 else "NOT SHOWN"
print(json.dumps(res, indent=1, default=float))
json.dump(res, open("results_compose.json", "w"), indent=1, default=float)
