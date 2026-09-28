"""XLGEO: are MG354's five in-cell crosslinks satisfiable by ONE copy on a solved RNAP core?

Pre-registered in PREREG_XLGEO.md at commit 4bb5f7d, BEFORE any distance was computed.
Gate first (20 RpoB-RpoC control crosslinks, >=70% within 30 A), then the MG354 primary.

Usage:  py -3.11 xlgeo.py
"""
import json, os, re, sys, warnings
import numpy as np
warnings.filterwarnings("ignore")

from Bio.PDB import MMCIFParser
from Bio.PDB.Polypeptide import is_aa, three_to_index, index_to_one
from Bio import Align
from Bio.Align import substitution_matrices

HERE = os.path.dirname(os.path.abspath(__file__))
GEO  = r"C:\Users\bmens\NQ_local\af3-hitcall\rnapgeo"
CIF  = os.path.join(GEO, "4yg2.cif")
YAML = os.path.join(HERE, "cleanroom", "rnap3", "rnap3_mg354_rpoB_rpoC.yaml")
LINKS= os.path.join(HERE, "cleanroom", "rnap3", "links.json")
CUT  = 30.0
TEMPLATE = {"B": "C", "C": "D"}          # query chain -> 4YG2 chain (RpoB->beta, RpoC->beta')
rng = np.random.default_rng(25)


def chain_obs(model, cid):
    """-> (sequence string, [resnum], Nx3 CA coords) over OBSERVED residues, in order."""
    seq, nums, xyz = [], [], []
    for r in model[cid]:
        if not is_aa(r) or "CA" not in r:
            continue
        try:
            seq.append(index_to_one(three_to_index(r.get_resname())))
        except Exception:
            continue
        nums.append(r.id[1])
        xyz.append(r["CA"].coord)
    return "".join(seq), nums, np.asarray(xyz, dtype=float)


def query_seqs():
    txt = open(YAML, encoding="utf-8").read()
    ids = re.findall(r"id:\s*(\w+)", txt)
    seqs = re.findall(r"sequence:\s*([A-Z]+)", txt)
    return dict(zip(ids, seqs))


def build_map(qseq, tseq, tnums):
    """Global align query onto observed template; -> {query_resnum(1-based): template_resnum}."""
    al = Align.PairwiseAligner()
    al.substitution_matrix = substitution_matrices.load("BLOSUM62")
    al.open_gap_score, al.extend_gap_score = -11, -1
    al.mode = "global"
    a = al.align(qseq, tseq)[0]
    m = {}
    for (qs, qe), (ts, te) in zip(a.aligned[0], a.aligned[1]):
        for k in range(qe - qs):
            m[qs + k + 1] = tnums[ts + k]
        
    return m, a.score


def main():
    s = MMCIFParser(QUIET=True).get_structure("x", CIF)
    model = next(s.get_models())
    Q = query_seqs()
    links = json.load(open(LINKS))

    tinfo, maps = {}, {}
    for qc, tc in TEMPLATE.items():
        tseq, tnums, txyz = chain_obs(model, tc)
        tinfo[qc] = (tnums, txyz, {n: i for i, n in enumerate(tnums)})
        maps[qc], sc = build_map(Q[qc], tseq, tnums)
        print("chain %s (%d aa) -> 4YG2 %s (%d observed):  %d residues mapped, align score %.0f"
              % (qc, len(Q[qc]), tc, len(tseq), len(maps[qc]), sc))

    def coord(qc, qres):
        t = maps[qc].get(qres)
        if t is None: return None
        nums, xyz, idx = tinfo[qc]
        return xyz[idx[t]]

    print("\n" + "="*72)
    print("GATE: RpoB-RpoC control crosslinks (registered: >=70% within 30 A)")
    print("="*72)
    ok = tot = unmap = 0
    dists = []
    for c1, r1, c2, r2 in links["control"]:
        a, b = coord(c1, r1), coord(c2, r2)
        if a is None or b is None:
            unmap += 1; continue
        d = float(np.linalg.norm(a - b)); dists.append(d); tot += 1
        if d <= CUT: ok += 1
    frac = ok / tot if tot else 0.0
    print("  mappable %d of %d (unmappable %d)" % (tot, len(links["control"]), unmap))
    print("  within %.0f A: %d of %d = %.1f%%   median %.1f A" % (CUT, ok, tot, 100*frac, np.median(dists)))
    GATE = frac >= 0.70
    print("  GATE %s" % ("PASSES" if GATE else "FAILS -> no MG354 number is reported"))
    if not GATE:
        json.dump({"gate_pass": False, "control_frac": frac}, open("results_xlgeo.json","w"), indent=1)
        return

    print("\n" + "="*72)
    print("PRIMARY: spread of the five MG354 attachment sites")
    print("="*72)
    pts, labels = [], []
    for ac, ar, pc, pr in links["mg354"]:
        c = coord(pc, pr)
        print("  MG354 %-4d -> %s %-5d  %s" % (ar, {"B":"RpoB","C":"RpoC"}[pc], pr,
                                               "mapped" if c is not None else "UNMAPPABLE"))
        if c is not None:
            pts.append(c); labels.append("%s%d" % (pc, pr))
    pts = np.asarray(pts)
    n = len(pts)
    D = np.linalg.norm(pts[:,None,:] - pts[None,:,:], axis=-1)
    mx = float(D.max())
    print("\n  sites mapped: %d of 5" % n)
    print("  pairwise Ca-Ca distance matrix (A):")
    print("      " + "".join("%8s" % l for l in labels))
    for i,l in enumerate(labels):
        print("  %-5s" % l + "".join("%8.1f" % D[i,j] for j in range(n)))
    print("\n  MAX PAIRWISE = %.1f A" % mx)
    verdict = "TIGHT (<=60): one pocket" if mx <= 60 else ("COMPATIBLE BUT WEAK (60-105)" if mx <= 105 else "INCOMPATIBLE (>105): one copy cannot make all five")
    print("  REGISTERED VERDICT: %s" % verdict)

    print("\n" + "="*72)
    print("SECONDARY (exploratory): distance to omega, chain E")
    print("="*72)
    oseq, onums, oxyz = chain_obs(model, "E")
    ocen = oxyz.mean(axis=0)
    cen = pts.mean(axis=0)
    dobs = float(np.linalg.norm(cen - ocen))
    pool = {qc: tinfo[qc][1] for qc in TEMPLATE}
    null = []
    for _ in range(1000):
        pick = [pool["B"][rng.integers(len(pool["B"]))] for _ in range(2)] + \
               [pool["C"][rng.integers(len(pool["C"]))] for _ in range(3)]
        null.append(np.linalg.norm(np.asarray(pick).mean(axis=0) - ocen))
    null = np.asarray(null)
    p = float((null <= dobs).mean())
    print("  centroid of the 5 sites to omega centroid: %.1f A" % dobs)
    print("  null (1000 draws, 2 on RpoB + 3 on RpoC):  median %.1f A, 5th pct %.1f A" % (np.median(null), np.percentile(null,5)))
    print("  P(null <= observed) = %.3f" % p)
    print("  NOTE: exploratory. The omega FOLD argument is dead (PREREG_OMEGA); a shared site")
    print("        would not by itself make MG354 an omega orthologue.")

    json.dump({"gate_pass": True, "control_within_30A": [ok, tot], "control_frac": frac,
               "mg354_sites": labels, "max_pairwise_A": mx, "verdict": verdict,
               "omega_centroid_dist_A": dobs, "omega_null_p": p,
               "pairwise": D.tolist()}, open("results_xlgeo.json","w"), indent=1)
    print("\nwrote results_xlgeo.json")


if __name__ == "__main__":
    main()
