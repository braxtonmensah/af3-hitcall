"""PREREG_ASSEMBLY2: co-dependency assemblies with a coverage-aware gate and real CORUM 5.0.
Committed pre-registration: PREREG_ASSEMBLY2.md (commit daf6252)."""
import csv
import json
import os
from collections import Counter, defaultdict

import networkx as nx
import numpy as np
import pandas as pd

D = r"C:\Users\bmens\NQ_local\af3-hitcall\depmap"
B = r"C:\Users\bmens\NQ_local\af3-hitcall\burke"
R_EDGE, SEED, MIN_LINES = 0.30, 30, 300
RESOLUTIONS = [0.5, 1.0, 2.0, 4.0]
A2_MIN, A2_MAX = 3, 40

GE = pd.read_csv(os.path.join(D, "CRISPRGeneEffect.csv"), index_col=0, low_memory=False)
GE.columns = [c.split(" (")[0] for c in GE.columns]
GE = GE.loc[:, ~GE.columns.duplicated()]
X = GE.to_numpy(np.float32)
GN = np.array(GE.columns)
sd = np.nanstd(X, axis=0)
universe = np.flatnonzero(sd >= np.nanpercentile(sd, 25))
UG = GN[universe]
print(f"universe: {len(universe)} genes", flush=True)

sub = X[:, universe]
Zf = np.where(np.isfinite(sub), sub, np.nanmean(sub, axis=0))
Zf = (Zf - Zf.mean(0)) / (Zf.std(0) + 1e-9)
n_lines = Zf.shape[0]
finite = np.isfinite(sub)


def exact_r(a, b):
    m = finite[:, a] & finite[:, b]
    if m.sum() < MIN_LINES:
        return None
    u, v = sub[m, a], sub[m, b]
    u = u - u.mean(); v = v - v.mean()
    d = np.sqrt((u * u).sum() * (v * v).sum())
    return None if d == 0 else float((u * v).sum() / d)


print("finding edges in blocks ...", flush=True)
edges = []
BS = 1500
for s in range(0, len(universe), BS):
    e = min(s + BS, len(universe))
    Cb = (Zf[:, s:e].T @ Zf) / n_lines
    for li, gi in enumerate(range(s, e)):
        row = Cb[li]
        for gj in np.flatnonzero(row >= R_EDGE * 0.85):
            if gj <= gi:
                continue
            r = exact_r(gi, int(gj))
            if r is not None and r >= R_EDGE:
                edges.append((UG[gi], UG[gj], r))
    print(f"  {e}/{len(universe)} genes, {len(edges)} edges", flush=True)

G = nx.Graph()
G.add_nodes_from(UG)
for a, b, r in edges:
    G.add_edge(a, b, weight=r)
print(f"graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges", flush=True)

# ---------------- CORUM 5.0 ----------------
corum = {}
with open(os.path.join(D, "corum_humanComplexes.txt"), encoding="utf-8", errors="replace") as fh:
    for row in csv.DictReader(fh, delimiter="\t"):
        gs = {g.strip() for g in str(row.get("subunits_gene_name", "")).split(";") if g.strip()}
        if len(gs) >= 2:
            corum[row["complex_id"]] = gs
print(f"CORUM human complexes: {len(corum)}", flush=True)
corum_pair = set()
for gs in corum.values():
    gl = sorted(gs)
    for i in range(len(gl)):
        for j in range(i + 1, len(gl)):
            corum_pair.add((gl[i], gl[j]))

s1 = pd.read_csv(os.path.join(B, "S1.csv"), low_memory=False)
ev_cols = [c for c in ["Y2H_BioGRID", "pulldown_BioGRID", "Y2H_IntAct", "pulldown_IntAct"] if c in s1.columns]


def truthy(s):
    return s.notna() & ~s.astype(str).str.lower().isin(["false", "0", "nan", "", " "])


s1["has_ev"] = np.logical_or.reduce([truthy(s1[c]) for c in ev_cols])
ev_pair = set()
studied = Counter()
for t in s1.itertuples():
    a, b = str(t._asdict()["_14"]) if False else str(getattr(t, "Gen.id1", "")), str(getattr(t, "Gen.id2", ""))
    a, b = str(s1.at[t.Index, "Gen.id1"]), str(s1.at[t.Index, "Gen.id2"])
    studied[a] += 1
    studied[b] += 1
    if t.has_ev:
        ev_pair.add((a, b) if a < b else (b, a))

UNI = set(UG)
den = {cid: gs & UNI for cid, gs in corum.items()}
den = {cid: gs for cid, gs in den.items() if len(gs) >= 3}
print(f"CORUM complexes with >=3 subunits in the universe: {len(den)}", flush=True)


def a0_of(part):
    node2cl = {}
    for i, c in enumerate(part):
        for g in c:
            node2cl[g] = i
    rec = 0
    cov = []
    for cid, gs in den.items():
        cl = Counter(node2cl[g] for g in gs if g in node2cl)
        cov.append(len(gs))
        if cl and cl.most_common(1)[0][1] > len(gs) / 2:
            rec += 1
    return rec / len(den), rec, float(np.median(cov))


def a2_of(part):
    out = []
    for c in part:
        c = sorted(c)
        if not (A2_MIN <= len(c) <= A2_MAX):
            continue
        nc = ne = npair = 0
        rs = []
        for i in range(len(c)):
            for j in range(i + 1, len(c)):
                k = (c[i], c[j])
                npair += 1
                if k in corum_pair:
                    nc += 1
                if k in ev_pair:
                    ne += 1
                if G.has_edge(c[i], c[j]):
                    rs.append(G[c[i]][c[j]]["weight"])
        if nc == 0 and (ne / npair if npair else 0) < 0.25:
            out.append({"size": len(c), "mean_r": round(float(np.mean(rs)) if rs else 0, 3),
                        "frac_ev": round(ne / npair, 3) if npair else 0,
                        "median_studied": float(np.median([studied.get(g, 0) for g in c])),
                        "members": " ".join(c)})
    return out


print("clustering at four resolutions ...", flush=True)
best = None
allres = {}
for res in RESOLUTIONS:
    part = nx.algorithms.community.louvain_communities(G, resolution=res, seed=SEED, weight="weight")
    mod = nx.algorithms.community.modularity(G, part, weight="weight", resolution=res)
    a0, rec, mcov = a0_of(part)
    allres[str(res)] = {"modularity": round(mod, 4), "n_comm": len(part), "A0": round(a0, 4),
                        "A0_recovered": rec, "median_coverage": mcov,
                        "sizes_3_40": int(sum(1 for c in part if A2_MIN <= len(c) <= A2_MAX))}
    print(f"  res {res}: modularity {mod:.4f}, {len(part)} communities, A0 {a0:.1%} ({rec}/{len(den)})", flush=True)
    if best is None or mod > best[1]:
        best = (res, mod, part)

res_star, mod_star, part_star = best
print(f"\nchosen by modularity: resolution {res_star} (modularity {mod_star:.4f})", flush=True)

print("degree-preserving null ...", flush=True)
Gn = nx.double_edge_swap(G.copy(), nswap=10 * G.number_of_edges(),
                         max_tries=300 * G.number_of_edges(), seed=SEED)
part_null = nx.algorithms.community.louvain_communities(Gn, resolution=res_star, seed=SEED)
a0n, recn, _ = a0_of(part_null)

a0s, recs, mcov = a0_of(part_star)
A2 = a2_of(part_star)
A2n = a2_of(part_null)
pure = []
for c in part_star:
    if len(c) < 3:
        continue
    cnt = Counter()
    for cid, gs in corum.items():
        k = len(gs & set(c))
        if k:
            cnt[cid] = k
    if cnt:
        pure.append(cnt.most_common(1)[0][1] / len(c))

gate = bool(a0s >= 0.35 and a0n > 0 and a0s >= 3 * a0n)
out = {"universe": int(len(universe)), "edges": int(G.number_of_edges()),
       "corum_complexes": len(corum), "denominator": len(den), "median_coverage": mcov,
       "resolutions": allres, "chosen_resolution": res_star, "modularity": round(mod_star, 4),
       "A0": round(a0s, 4), "A0_recovered": recs, "A0_null": round(a0n, 4), "A0_null_recovered": recn,
       "A0_ratio_to_null": round(a0s / a0n, 2) if a0n else None,
       "A0_gate_passes": gate,
       "A1_purity_ge_0.5": int(sum(1 for p in pure if p >= 0.5)), "A1_clusters": len(pure),
       "A2_n": len(A2), "A3_null_A2": len(A2n), "A2_exceeds_null": bool(len(A2) > len(A2n))}
print("\n" + json.dumps(out, indent=1))
if A2:
    med_a2 = float(np.median([c["median_studied"] for c in A2]))
    print(f"\nA4 confound: median 'times seen in Burke S1' for A2 cluster members = {med_a2:.0f}")
    out["A4_median_studied_A2"] = med_a2
    print("\ntop A2 clusters:" if gate else "\nA2 clusters (NOT INTERPRETED, gate failed):")
    for c in sorted(A2, key=lambda x: -x["mean_r"])[:20]:
        print(f"  n={c['size']:2d} r={c['mean_r']:.3f} ev={c['frac_ev']:.2f} studied={c['median_studied']:.0f}  {c['members'][:100]}")
json.dump(out, open("results_assembly2.json", "w"), indent=1)
pd.DataFrame(A2).to_csv("assembly2_unannotated.csv", index=False)
