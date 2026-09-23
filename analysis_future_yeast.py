"""PREREG_FUTURE_YEAST: Humphreys 2021 yeast models (ModelArchive ma-bak-cepc) vs PDB complexes
released 2022+. Stages cache to NQ_local/af3-hitcall/future_yeast."""
import gzip
import io
import json
import os
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
import requests
from Bio import Align

from metrics import ci

Y = r"C:\Users\bmens\NQ_local\af3-hitcall\future_yeast"
FU = r"C:\Users\bmens\NQ_local\af3-hitcall\future"
os.makedirs(os.path.join(Y, "entry_contacts"), exist_ok=True)
rng = np.random.default_rng(1505)
AA = {"ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I",
      "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P", "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V", "MSE": "M"}
S = requests.Session()


def get(url, **kw):
    for k in range(6):
        try:
            r = S.get(url, timeout=120, **kw)
            if r.status_code in (200, 404):
                return r
        except Exception:
            pass
        time.sleep(3 * (k + 1))
    raise RuntimeError(url)


# ---------- stage 1: models ----------
MP = os.path.join(Y, "models.jsonl")


def fetch_model(k):
    mid = f"ma-bak-cepc-{k:04d}"
    r = get(f"https://www.modelarchive.org/api/projects/{mid}?type=basic__model_file_name")
    if r.status_code == 404 or r.text.startswith("{"):
        return None
    cols, ch = [], defaultdict(dict)
    for line in r.text.splitlines():
        if line.startswith("_atom_site."):
            cols.append(line.strip().split(".", 1)[1]); continue
        if not line.startswith("ATOM"):
            continue
        c = dict(zip(cols, line.split()))
        a, comp, asym, seq = c["label_atom_id"], c["label_comp_id"], c["label_asym_id"], int(c["label_seq_id"])
        rr = ch[asym].setdefault(seq, {"aa": AA.get(comp, "X"), "x": None})
        if a == "CB" or (a == "CA" and comp == "GLY") or (a == "CA" and rr["x"] is None):
            if a == "CB" or comp == "GLY" or rr["x"] is None:
                rr["x"] = (float(c["Cartn_x"]), float(c["Cartn_y"]), float(c["Cartn_z"]))
    ids = sorted(ch)
    if len(ids) != 2:
        return {"id": mid, "error": f"{len(ids)} chains"}
    out = {"id": mid, "chains": []}
    X = []
    for a in ids:
        nums = sorted(ch[a])
        out["chains"].append({"seq": "".join(ch[a][n]["aa"] for n in nums)})
        X.append(np.array([ch[a][n]["x"] for n in nums]))
    D = np.sqrt(((X[0][:, None] - X[1][None]) ** 2).sum(-1)) < 8
    out["chains"][0]["iface"] = np.flatnonzero(D.any(1)).tolist()
    out["chains"][1]["iface"] = np.flatnonzero(D.any(0)).tolist()
    return out


if not os.path.exists(MP):
    recs = []
    with ThreadPoolExecutor(8) as ex:
        for k in range(1, 3000, 200):
            batch = [x for x in ex.map(fetch_model, range(k, k + 200)) if x]
            recs += batch
            print("models", len(recs), flush=True)
            if not batch:
                break
    with open(MP, "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
models = [json.loads(l) for l in open(MP)]
models = [m for m in models if "chains" in m]
print("models with 2 chains:", len(models))

# ---------- stage 2: map to S288c ----------
PP = os.path.join(Y, "proteome.fasta")
if not os.path.exists(PP):
    open(PP, "w").write(get("https://rest.uniprot.org/uniprotkb/stream?query=proteome:UP000002311&format=fasta").text)
prot, cur = {}, None
for line in open(PP):
    if line.startswith(">"):
        cur = line.split("|")[1]; prot[cur] = ""
    else:
        prot[cur] += line.strip()
by_seq = {s: a for a, s in prot.items()}
aligner = Align.PairwiseAligner(mode="global", open_gap_score=-10, extend_gap_score=-0.5)
aligner.substitution_matrix = Align.substitution_matrices.load("BLOSUM62")
kmer = defaultdict(set)
for a, s in prot.items():
    for i in range(0, len(s) - 8, 4):
        kmer[s[i:i + 8]].add(a)


def map_chain(seq):
    """-> (acc, list mapping model index -> UniProt position or None)"""
    if seq in by_seq:
        return by_seq[seq], list(range(1, len(seq) + 1))
    votes = defaultdict(int)
    for i in range(0, len(seq) - 8, 2):
        for a in kmer.get(seq[i:i + 8], ()):
            votes[a] += 1
    if not votes:
        return None, None
    acc = max(votes, key=votes.get)
    aln = aligner.align(seq, prot[acc])[0]
    m = [None] * len(seq)
    ident = 0
    for (a0, a1), (b0, b1) in zip(*aln.aligned):
        for k in range(a1 - a0):
            m[a0 + k] = b0 + k + 1
            ident += seq[a0 + k] == prot[acc][b0 + k]
    cov = sum(x is not None for x in m) / len(seq)
    if cov >= 0.9 and ident / max(1, sum(x is not None for x in m)) >= 0.95:
        return acc, m
    return None, None


pairs = []
for m in models:
    mp = [map_chain(c["seq"]) for c in m["chains"]]
    if any(a is None for a, _ in mp) or mp[0][0] == mp[1][0]:
        continue
    pred = set()
    for (acc, idx), c in zip(mp, m["chains"]):
        pred |= {(acc, idx[i]) for i in c["iface"] if idx[i] is not None}
    pairs.append(dict(model=m["id"], a=mp[0][0], b=mp[1][0], pred=pred,
                      lens={mp[0][0]: len(prot[mp[0][0]]), mp[1][0]: len(prot[mp[1][0]])}))
print("mapped heterodimer models:", len(pairs))

# ---------- stage 3: co-complexes, dates ----------
accs = {p["a"] for p in pairs} | {p["b"] for p in pairs}
sm = defaultdict(lambda: defaultdict(set))
seg = defaultdict(list)
with gzip.open(os.path.join(FU, "pdb_chain_uniprot.tsv.gz"), "rt") as f:
    next(f); next(f)
    for line in f:
        x = line.rstrip("\n").split("\t")
        if x[2] in accs:
            sm[x[2]][x[0]].add(x[1])
            try:
                seg[(x[0], x[1])].append((x[2], int(x[3]), int(x[4]), int(x[7])))
            except ValueError:
                pass
for p in pairs:
    a, b = p["a"], p["b"]
    p["entries"] = [e for e in set(sm[a]) & set(sm[b]) if (sm[a][e] - sm[b][e]) and (sm[b][e] - sm[a][e])]
need = sorted({e for p in pairs for e in p["entries"]})
DP = os.path.join(Y, "dates.json")
dates = json.load(open(DP)) if os.path.exists(DP) else {}
Q = "query($ids:[String!]!){entries(entry_ids:$ids){rcsb_id rcsb_accession_info{initial_release_date}}}"
todo = [e for e in need if e not in dates]
for k in range(0, len(todo), 400):
    r = S.post("https://data.rcsb.org/graphql", json={"query": Q, "variables": {"ids": [e.upper() for e in todo[k:k + 400]]}}, timeout=120).json()
    for x in r["data"]["entries"] or []:
        dates[x["rcsb_id"].lower()] = x["rcsb_accession_info"]["initial_release_date"][:10]
json.dump(dates, open(DP, "w"))
CUT = "2022-01-01"
for p in pairs:
    ds = sorted(dates.get(e, "9999") for e in p["entries"])
    p["first"] = ds[0] if ds else None
    p["missed"] = bool(ds) and ds[0] < CUT
    p["new"] = bool(ds) and ds[0] >= CUT and ds[0] != "9999"
    p["new_entries"] = [e for e in p["entries"] if CUT <= dates.get(e, "9999") < "9999"]
res = {"n_models": len(models), "n_mapped": len(pairs), "excluded_earlier_cocomplex": sum(p["missed"] for p in pairs),
       "eligible": sum(not p["missed"] for p in pairs), "newly_solved": sum(p["new"] for p in pairs)}
res["Y3_frac_newly_solved"] = res["newly_solved"] / max(1, res["eligible"])
print(res, flush=True)


# ---------- stage 4: contacts in new entries ----------
def entry_contacts(e):
    fp = os.path.join(Y, "entry_contacts", e + ".json")
    if os.path.exists(fp):
        return json.load(open(fp))
    chains = {c: s for (ee, c), s in seg.items() if ee == e}
    r = get(f"https://files.rcsb.org/download/{e}.cif.gz")
    cols, rows = [], defaultdict(dict)
    for line in io.TextIOWrapper(gzip.GzipFile(fileobj=io.BytesIO(r.content)), encoding="utf-8", errors="replace"):
        if line.startswith("_atom_site."):
            cols.append(line.strip().split(".", 1)[1]); continue
        if not line.startswith("ATOM"):
            continue
        c = dict(zip(cols, line.split()))
        if c.get("pdbx_PDB_model_num", "1") != "1" or c["auth_asym_id"] not in chains or c["label_seq_id"] == ".":
            continue
        if not (c["label_atom_id"] == "CB" or (c["label_atom_id"] == "CA" and c["label_comp_id"] == "GLY")):
            continue
        k = int(c["label_seq_id"])
        for acc, rb, re_, sb in chains[c["auth_asym_id"]]:
            if rb <= k <= re_:
                rows[c["auth_asym_id"]][k] = (acc, sb + k - rb, float(c["Cartn_x"]), float(c["Cartn_y"]), float(c["Cartn_z"]))
                break
    out = []
    ids = sorted(rows)
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            A, Bc = list(rows[ids[i]].values()), list(rows[ids[j]].values())
            aA, aB = {x[0] for x in A}, {x[0] for x in Bc}
            if len(aA) != 1 or len(aB) != 1 or aA == aB:
                continue
            D = np.sqrt(((np.array([x[2:] for x in A])[:, None] - np.array([x[2:] for x in Bc])[None]) ** 2).sum(-1)) < 8
            out.append({"acc": [aA.pop(), aB.pop()], "n_contacts": int(D.sum()),
                        "iface": [[A[k][1] for k in np.flatnonzero(D.any(1))], [Bc[k][1] for k in np.flatnonzero(D.any(0))]],
                        "observed": [[x[1] for x in A], [x[1] for x in Bc]]})
    json.dump(out, open(fp, "w"))
    return out


newE = sorted({e for p in pairs if p["new"] for e in p["new_entries"]})
with ThreadPoolExecutor(8) as ex:
    list(ex.map(entry_contacts, newE))

# ---------- stage 5: Y1 / Y2 ----------
rows = []
for p in pairs:
    if not p["new"]:
        continue
    top = None
    for e in p["new_entries"]:
        for c in entry_contacts(e):
            if set(c["acc"]) == {p["a"], p["b"]} and (top is None or c["n_contacts"] > top["n_contacts"]):
                top = dict(c, entry=e)
    if not top or top["n_contacts"] < 5:
        continue
    E, O = set(), set()
    for k, acc in enumerate(top["acc"]):
        E |= {(acc, x) for x in top["iface"][k]}
        O |= {(acc, x) for x in top["observed"][k]}

    def f1(Pset):
        Pp = Pset & O
        return 2 * len(Pp & E) / (len(Pp) + len(E)) if (Pp or E) else 0.0

    null = []
    for _ in range(200):
        sh = {acc: int(rng.integers(1, L)) for acc, L in p["lens"].items()}
        null.append(f1({(acc, (x - 1 + sh[acc]) % p["lens"][acc] + 1) for acc, x in p["pred"]}))
    rows.append(dict(model=p["model"], a=p["a"], b=p["b"], entry=top["entry"], first=p["first"], f1=f1(p["pred"]),
                     null_correct=float(np.mean(np.array(null) >= 0.5))))
R = pd.DataFrame(rows)
R.to_csv(os.path.join(Y, "y1_pairs.csv"), index=False)
v = (R.f1 >= 0.5).to_numpy()
bs = [rng.choice(v, len(v)).mean() for _ in range(2000)]
lo, hi = ci(np.array(bs), 0.95).tolist()
res["Y1"] = {"n": len(R), "frac_correct": float(v.mean()), "ci95": [lo, hi], "median_f1": float(R.f1.median()),
             "verdict": "REPLICATES" if lo > 0.5 else "NOT SHOWN"}
# null: fraction correct in each of 200 shift replicates is approximated by per-pair null probability
nsim = [(rng.random(len(R)) < R.null_correct.to_numpy()).mean() for _ in range(10000)]
res["Y2_null"] = {"mean_frac_correct": float(np.mean(nsim)), "p99": float(np.quantile(nsim, 0.99)),
                  "Y1_exceeds_p99": bool(v.mean() > np.quantile(nsim, 0.99))}
res["release_years"] = R["first"].str[:4].value_counts().sort_index().to_dict()
print(json.dumps(res, indent=1, default=float))
json.dump(res, open("results_future_yeast.json", "w"), indent=1, default=float)
