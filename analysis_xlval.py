"""PREREG_XLVAL: are in-cell crosslinks (M. pneumoniae, DSSO) within reach across AF3's predicted interface
for never-solved, confidently predicted M. genitalium pairs? CA-CA <= 30 A; random cross-chain lysine null."""
import json
import os
from collections import defaultdict

import numpy as np
import pandas as pd
from Bio import Align

from analysis_h1_h2_lib import LOCI, precedent_matrix_strict

L = r"C:\Users\bmens\NQ_local\af3-hitcall"
rng = np.random.default_rng(19 if os.environ.get("XL_DATA") == "DSS" else 18)
CAND = [("MG_139", "MG_423"), ("MG_098", "MG_099"), ("MG_014", "MG_015"), ("MG_411", "MG_412"), ("MG_179", "MG_180"),
        ("MG_027", "MG_150"), ("MG_119", "MG_121"), ("MG_241", "MG_242"), ("MG_098", "MG_181"), ("MG_078", "MG_080"),
        ("MG_127", "MG_249"), ("MG_001", "MG_419"), ("MG_409", "MG_410"), ("MG_098", "MG_179")]
CUT = 30.0

ix = {l: i for i, l in enumerate(LOCI)}
S0 = np.load(os.path.join(L, "data", "S0.npy"))
PRE = precedent_matrix_strict("") | precedent_matrix_strict("_id0")
mgseq = {l: s.rstrip("*") for l, s in pd.read_csv(os.path.join(L, "data", "proteins.csv"))[["locus_tag", "aa_sequence"]].values}
mp = pd.read_csv(os.path.join(L, "data", "mpn_to_mg.csv"))
p2g = dict(zip(mp.mpn, mp.mg))
mpnseq, cur = {}, None
for line in open(os.path.join(L, "xlms2020", "Full_database_combined.fasta")):
    if line.startswith(">"):
        cur = line[1:].split()[0].split("|")[1] if "|" in line else line[1:].split()[0]; mpnseq[cur] = ""
    else:
        mpnseq[cur] += line.strip()

acc = lambda s: str(s).split(";")[0].split("|")[-1]
# POST HOC option (XLVAL Amendment 2, after results): the crosslink study's FASTA has corrupted residues in some
# entries (e.g. "K(a"); XL_SEQ=uniprot swaps in current UniProt sequences for M. pneumoniae proteins.
if os.environ.get("XL_SEQ") == "uniprot":
    cache = os.path.join(L, "verify", "mpn_uniprot_seqs.json")
    if not os.path.exists(cache):
        import requests
        import re as _re
        got, accs = {}, sorted(a for a in mpnseq if _re.fullmatch(r"[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9][A-Z][A-Z0-9]{2}[0-9]", a))
        for k in range(0, len(accs), 100):
            t = requests.get("https://rest.uniprot.org/uniprotkb/accessions", params={"accessions": ",".join(accs[k:k + 100]), "format": "fasta"}, timeout=120).text
            cur2 = None
            for line in t.splitlines():
                if line.startswith(">"):
                    cur2 = line.split("|")[1]; got[cur2] = ""
                elif cur2:
                    got[cur2] += line.strip()
        json.dump(got, open(cache, "w"))
    mpnseq.update(json.load(open(cache)))
XL = os.environ.get("XL_DATA", "DSSO")  # PREREG_XLDSS: "DSS" reads the independent DSS dataset (PXD017695)
XDIR = os.path.join(L, "xlms2020" if XL == "DSSO" else "xlms2020_dss")
X = pd.read_csv(os.path.join(XDIR, f"Myco_InCell_{XL}_dataset_5link_5PPI_Links_xiFDR1.2.30.59dev.csv"), index_col=False, low_memory=False)
X = X[X.isTT & ~X.isDecoy & (X.fdr <= 0.05)].copy()
X["a"], X["b"] = X.Protein1.map(acc), X.Protein2.map(acc)
X["ga"], X["gb"] = X.a.map(p2g), X.b.map(p2g)
X = X[X.ga.notna() & X.gb.notna() & (X.ga != X.gb)]
# Site resolution (PREREG_XLVAL Amendment 1): the Links file's protein positions do not match this FASTA for
# many proteins (different start sites), so each link's site is recomputed by locating its peptides in the
# sequence: site = peptide position + link position within the peptide. Links whose peptides cannot be
# located are dropped and counted.
PP = pd.read_csv(os.path.join(XDIR, f"Myco_InCell_{XL}_dataset_5link_5PPI_PeptidePairs_xiFDR1.2.30.59dev.csv"), index_col=False, low_memory=False)
PP = PP[PP.isTT & ~PP.isDecoy].rename(columns={"link id": "link_id"})


def locate(protacc, pep, pos_in_pep):
    s = mpnseq.get(protacc)
    pep = "".join(ch for ch in str(pep) if ch.isupper())
    i = s.find(pep) if s else -1
    return i + int(str(pos_in_pep).split(";")[0]) if i >= 0 else None


site = {}
for r in PP.itertuples():
    a1, a2 = acc(r.Protein1), acc(r.Protein2)
    s1, s2 = locate(a1, r.Peptide1, r.FromSite), locate(a2, r.Peptide2, r.ToSite)
    if s1 and s2:
        site.setdefault(str(r.link_id), (s1, s2))
X["pa"] = [site.get(str(k), (None, None))[0] for k in X.LinkID]
X["pb"] = [site.get(str(k), (None, None))[1] for k in X.LinkID]
X = X[X.pa.notna()].copy()
X["pa"], X["pb"] = X.pa.astype(int), X.pb.astype(int)

aligner = Align.PairwiseAligner(mode="global", open_gap_score=-10, extend_gap_score=-0.5)
aligner.substitution_matrix = Align.substitution_matrices.load("BLOSUM62")
_mapcache = {}


def mpn2mg(mpn_acc, mg):
    """dict: M. pneumoniae residue (1-based) -> M. genitalium residue (1-based) via global alignment"""
    if (mpn_acc, mg) not in _mapcache:
        clean = lambda q: "".join(c if c in "ACDEFGHIKLMNPQRSTVWYBZX" else "X" for c in q)
        aln = aligner.align(clean(mpnseq[mpn_acc]), clean(mgseq[mg]))[0]
        m = {}
        for (a0, a1), (b0, b1) in zip(*aln.aligned):
            for k in range(a1 - a0):
                m[a0 + k + 1] = b0 + k + 1
        _mapcache[(mpn_acc, mg)] = m
    return _mapcache[(mpn_acc, mg)]


pools = defaultdict(list)
for i, j, p in pd.read_csv(os.path.join(L, "data", "s0_per_pool.csv"), usecols=["i", "j", "pool"]).itertuples(index=False):
    pools[(i, j)].append(p)


def models(g1, g2):
    """yield (CA of g1, CA of g2) for every extracted pool x sample containing the pair"""
    i, j = sorted((ix[g1], ix[g2]))
    for p in pools[(i, j)]:
        f = os.path.join(L, "structs_ca", p + ".npz")
        if not os.path.exists(f):
            continue
        z = np.load(f)
        loci = list(z["loci"]); ch = z["chain"]
        if g1 not in loci or g2 not in loci:
            continue
        c1, c2 = loci.index(g1), loci.index(g2)
        for k in range(5):
            xyz = z[f"xyz{k}"].astype(np.float32)
            yield xyz[ch == c1], xyz[ch == c2]


def evaluate(g1, g2):
    sub = X[((X.ga == g1) & (X.gb == g2)) | ((X.ga == g2) & (X.gb == g1))]
    links, dropped = [], 0
    for r in sub.itertuples():
        # orient so the first residue belongs to g1
        (ma, ra), (mb, rb) = ((r.a, r.pa), (r.b, r.pb)) if r.ga == g1 else ((r.b, r.pb), (r.a, r.pa))
        x1, x2 = mpn2mg(ma, g1).get(ra), mpn2mg(mb, g2).get(rb)
        if x1 is None or x2 is None:
            dropped += 1
        else:
            links.append((x1, x2))
    links = sorted(set(links))
    M = list(models(g1, g2))
    out = {"pair": f"{g1}-{g2}", "S0": float(S0[ix[g1], ix[g2]]), "prec": bool(PRE[ix[g1], ix[g2]]), "n_links": len(links),
           "dropped": dropped, "n_models": len(M)}
    if not M or not links:
        return out
    dist = np.array([[np.linalg.norm(a[x1 - 1] - b[x2 - 1]) for (x1, x2) in links] for a, b in M])  # models x links
    sat = (dist <= CUT).mean()
    K1 = [k + 1 for k, c in enumerate(mgseq[g1]) if c == "K"]
    K2 = [k + 1 for k, c in enumerate(mgseq[g2]) if c == "K"]
    null = []
    for _ in range(1000):
        rk = [(rng.choice(K1), rng.choice(K2)) for _ in links]
        null.append(np.mean([[np.linalg.norm(a[x1 - 1] - b[x2 - 1]) <= CUT for (x1, x2) in rk] for a, b in M]))
    p95 = float(np.quantile(null, 0.95))
    out.update(satisfied=float(sat), median_dist=float(np.median(dist)), min_dist_per_link=[round(float(v), 1) for v in dist.min(0)],
               null_mean=float(np.mean(null)), null_p95=p95, supported=bool(sat >= 0.5 and sat > p95), links=links)
    return out


if __name__ == "__main__":
    res = {"candidates": [evaluate(a, b) for a, b in CAND]}
    # controls: crosslinked, never-solved, S0 < 0.05, with extracted pools (seed 18, up to 20)
    pairs = {tuple(sorted((a, b))) for a, b in zip(X.ga, X.gb)}
    ctrl = [p for p in sorted(pairs) if not PRE[ix[p[0]], ix[p[1]]] and S0[ix[p[0]], ix[p[1]]] < 0.05]
    rng.shuffle(ctrl)
    res["controls"] = []
    for a, b in ctrl:
        e = evaluate(a, b)
        if e.get("n_models") and e.get("n_links"):
            res["controls"].append(e)
        if len(res["controls"]) >= 20:
            break
    c = res["controls"]
    res["control_summary"] = {"n": len(c), "supported": sum(x.get("supported", False) for x in c),
                              "mean_satisfied": float(np.mean([x["satisfied"] for x in c])) if c else None}
    res["test_discriminates"] = bool(c and res["control_summary"]["supported"] <= 0.25 * len(c))
    for x in res["candidates"]:
        print(x["pair"], {k: x.get(k) for k in ("S0", "n_links", "dropped", "n_models", "satisfied", "null_p95", "supported", "min_dist_per_link")})
    print("controls:", res["control_summary"], "discriminates:", res["test_discriminates"])
    outname = "results_xldss.json" if XL == "DSS" else ("results_xlval_uniprotseq.json" if os.environ.get("XL_SEQ") == "uniprot" else "results_xlval.json")
    json.dump(res, open(outname, "w"), indent=1, default=lambda o: o if not isinstance(o, (np.integer, np.floating)) else o.item())
