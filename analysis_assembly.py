"""PREREG_ASSEMBLY: can CRISPR co-dependency alone say which proteins to fold together?
Committed pre-registration: PREREG_ASSEMBLY.md (commit a829e73)."""
import json
import os
from collections import Counter, defaultdict

import networkx as nx
import numpy as np
import pandas as pd

D = r"C:\Users\bmens\NQ_local\af3-hitcall\depmap"
B = r"C:\Users\bmens\NQ_local\af3-hitcall\burke"
R_EDGE, RES, SEED, SMIN, SMAX, MIN_LINES = 0.30, 1.0, 29, 3, 60, 300
rng = np.random.default_rng(SEED)

GE = pd.read_csv(os.path.join(D, "CRISPRGeneEffect.csv"), index_col=0, low_memory=False)
GE.columns = [c.split(" (")[0] for c in GE.columns]
GE = GE.loc[:, ~GE.columns.duplicated()]
X = GE.to_numpy(np.float32)
GN = np.array(GE.columns)
sd = np.nanstd(X, axis=0)
ok_var = sd >= np.nanpercentile(sd, 25)

mean_ge = np.nanmean(X, axis=0)
ndep = np.nansum(X < -0.6, axis=0)
fdep = ndep / np.sum(np.isfinite(X), axis=0)
selective = (mean_ge > -0.35) & (ndep >= 15) & (fdep <= 0.25)
universe = np.flatnonzero(ok_var & (selective | (mean_ge < -0.35)))
print(f"gene universe: {len(universe)}", flush=True)

# correlation with a shared-line floor; mean-fill only to find candidate edges, exact r on candidates
sub = X[:, universe]
Z = np.where(np.isfinite(sub), sub, np.nanmean(sub, axis=0))
Z = (Z - Z.mean(0)) / (Z.std(0) + 1e-9)
C = (Z.T @ Z) / Z.shape[0]
np.fill_diagonal(C, 0)
cand = np.argwhere(C >= R_EDGE * 0.85)          # slightly loose, exact test below
cand = cand[cand[:, 0] < cand[:, 1]]
print(f"candidate edges to verify exactly: {len(cand)}", flush=True)


def exact_r(i, j):
    a, b = X[:, i], X[:, j]
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < MIN_LINES:
        return None
    aa, bb = a[m] - a[m].mean(), b[m] - b[m].mean()
    d = np.sqrt((aa * aa).sum() * (bb * bb).sum())
    return None if d == 0 else float((aa * bb).sum() / d)


G = nx.Graph()
G.add_nodes_from(GN[universe])
kept = 0
for a, b in cand:
    ia, ib = int(universe[a]), int(universe[b])
    r = exact_r(ia, ib)
    if r is not None and r >= R_EDGE:
        G.add_edge(GN[ia], GN[ib], weight=r)
        kept += 1
print(f"edges kept at r >= {R_EDGE}: {kept}", flush=True)

comms = nx.algorithms.community.louvain_communities(G, resolution=RES, seed=SEED, weight="weight")
clusters = [sorted(c) for c in comms if SMIN <= len(c) <= SMAX]
print(f"communities: {len(comms)}, size {SMIN}-{SMAX}: {len(clusters)}", flush=True)

# ---------------- annotation ----------------
s1 = pd.read_csv(os.path.join(B, "S1.csv"), low_memory=False)
s1["gA"] = s1["Gen.id1"].astype(str)
s1["gB"] = s1["Gen.id2"].astype(str)
ev_cols = [c for c in ["Y2H_BioGRID", "pulldown_BioGRID", "Y2H_IntAct", "pulldown_IntAct"] if c in s1.columns]


def truthy(s):
    return s.notna() & ~s.astype(str).str.lower().isin(["false", "0", "nan", "", " "])


s1["has_ev"] = np.logical_or.reduce([truthy(s1[c]) for c in ev_cols])
corum_pair, ev_pair = set(), set()
gene_complexes = defaultdict(set)
for t in s1.itertuples():
    k = (t.gA, t.gB) if t.gA < t.gB else (t.gB, t.gA)
    if pd.notna(t.CORUM_ID_selection):
        corum_pair.add(k)
        for cid in str(t.CORUM_ID_selection).replace(";", ",").split(","):
            cid = cid.strip()
            if cid:
                gene_complexes[t.gA].add(cid)
                gene_complexes[t.gB].add(cid)
    if t.has_ev:
        ev_pair.add(k)

complex_members = defaultdict(set)
for g, cids in gene_complexes.items():
    for cid in cids:
        complex_members[cid].add(g)

node2cl = {}
for i, c in enumerate(clusters):
    for g in c:
        node2cl[g] = i

# ---------------- A0 gate ----------------
uni = set(GN[universe])
rec, tot = 0, 0
for cid, members in complex_members.items():
    inside = members & uni
    if len(inside) < 3:
        continue
    tot += 1
    cl = Counter(node2cl[g] for g in inside if g in node2cl)
    if cl and cl.most_common(1)[0][1] > len(inside) / 2:
        rec += 1
a0 = rec / tot if tot else 0.0
print(f"\nA0: {rec}/{tot} CORUM complexes majority-recovered = {a0:.1%}  "
      f"({'SENSITIVE' if a0 >= 0.40 else 'FAILS GATE'})", flush=True)


def pair_stats(c):
    n_c = n_e = n_p = 0
    rs = []
    for i in range(len(c)):
        for j in range(i + 1, len(c)):
            k = (c[i], c[j]) if c[i] < c[j] else (c[j], c[i])
            n_p += 1
            if k in corum_pair:
                n_c += 1
            if k in ev_pair:
                n_e += 1
            if G.has_edge(c[i], c[j]):
                rs.append(G[c[i]][c[j]]["weight"])
    return n_c, n_e, n_p, float(np.mean(rs)) if rs else 0.0


rows = []
for i, c in enumerate(clusters):
    n_c, n_e, n_p, mr = pair_stats(c)
    cl = Counter()
    for g in c:
        for cid in gene_complexes.get(g, ()):
            cl[cid] += 1
    purity = (cl.most_common(1)[0][1] / len(c)) if cl else 0.0
    rows.append({"cluster": i, "size": len(c), "mean_r": round(mr, 3),
                 "corum_pairs": n_c, "ev_pairs": n_e, "n_pairs": n_p,
                 "frac_ev": round(n_e / n_p, 3) if n_p else 0.0,
                 "purity": round(purity, 3), "members": " ".join(c)})
T = pd.DataFrame(rows).sort_values("mean_r", ascending=False)
A2 = T[(T.corum_pairs == 0) & (T.frac_ev < 0.25)]
print(f"A1: clusters with purity >= 0.5: {(T.purity >= 0.5).sum()} of {len(T)}")
print(f"A2: unannotated clusters (no CORUM pair, <25% with any evidence): {len(A2)}", flush=True)

# ---------------- A3 degree-preserving null ----------------
print("A3 null (degree-preserving shuffle) ...", flush=True)
Gn = nx.double_edge_swap(G.copy(), nswap=10 * G.number_of_edges(), max_tries=200 * G.number_of_edges(), seed=SEED)
cn = [sorted(c) for c in nx.algorithms.community.louvain_communities(Gn, resolution=RES, seed=SEED)
      if SMIN <= len(c) <= SMAX]
n2 = 0
for c in cn:
    n_c, n_e, n_p, _ = pair_stats(c)
    if n_c == 0 and (n_e / n_p if n_p else 0) < 0.25:
        n2 += 1
print(f"  null: {len(cn)} clusters in range, {n2} would qualify for A2", flush=True)

res = {"universe": int(len(universe)), "edges": int(kept), "r_edge": R_EDGE,
       "n_communities": int(len(comms)), "n_clusters_in_range": int(len(clusters)),
       "A0_recovered": int(rec), "A0_total": int(tot), "A0_frac": round(a0, 4),
       "A0_sensitive": bool(a0 >= 0.40),
       "A1_purity_ge_0.5": int((T.purity >= 0.5).sum()),
       "A2_n": int(len(A2)), "A3_null_clusters": int(len(cn)), "A3_null_A2": int(n2),
       "A2_exceeds_null": bool(len(A2) > n2)}
print("\n" + json.dumps(res, indent=1))
print("\ntop unannotated clusters by internal co-dependency:")
for t in A2.head(20).itertuples():
    print(f"  n={t.size:2d} mean r={t.mean_r:.3f} ev={t.frac_ev:.2f}  {t.members[:110]}")
T.to_csv("assembly_clusters.csv", index=False)
A2.to_csv("assembly_unannotated.csv", index=False)
json.dump(res, open("results_assembly.json", "w"), indent=1)
