"""For a chain pair A-B: (1) BSA of the interface, (2) with the PARTNER REMOVED,
the largest concave pocket on A's surface that lies at the interface.

(2) is the quantity that matters for ligandability: it asks whether the surface
the partner covers is a groove a small molecule could sit in, not whether there
is leftover void in the complex. Coarse LIGSITE-style grid scan, 1.0 A, probe
1.4 A, protein required within 10 A along >=5 of 7 directions. Calibrate against
references run the same way rather than reading the absolute number.

Written 2026-09-25 for cleanroom/TARGET_EXPANSION.md. Not pre-registered; this is
a descriptive measurement used to rank candidate screening targets, not a test.

Usage:
    py -3.11 iface_pocket.py <model.cif|pdb> <A-B[,C-D,...]> "<label>"

Calibration actually run (same parameters), for reading the output:
    KEAP1 Kelch : p62   3ADE A-B   BSA  814 A^2   pocket 575 A^3   (drugged)
    MDM2 : p53          1YCR A-B   BSA 1450 A^2   pocket  76 A^3   (drugged, shallow)
    c-Fos : c-Jun bZIP  1FOS E-F   BSA 2352 A^2   pocket   0 A^3   (flat, undrugged)

Absolute volumes are conformation- and resolution-sensitive: the H. pylori RNase J
catalytic cleft measures 415 A^3 in 7PCR (2.75 A) and 5463 A^3 in 8CGL (4.1 A).
Read rank order against the references, never the raw number.
"""
import sys, warnings, numpy as np
warnings.filterwarnings("ignore")
from Bio.PDB import MMCIFParser, PDBParser
from Bio.PDB.SASA import ShrakeRupley
from scipy import ndimage

DEPTH = 10.0
SPACING = 1.0
PSP_CUT = 5
HYDRO = set("ALA VAL LEU ILE MET PHE TRP PRO CYS GLY TYR".split())
VDW = {"C": 1.70, "N": 1.55, "O": 1.52, "S": 1.80, "P": 1.80, "SE": 1.90,
       "ZN": 1.39, "MG": 1.73, "MN": 1.73, "FE": 1.80}


def load(path):
    P = MMCIFParser(QUIET=True) if path.lower().endswith(".cif") else PDBParser(QUIET=True)
    m = next(iter(P.get_structure("s", path)))
    return {c.id: c for c in m}


def sasa(chain_objs):
    from Bio.PDB.Structure import Structure
    from Bio.PDB.Model import Model
    st = Structure("t"); m = Model(0); st.add(m)
    for ch in chain_objs:
        m.add(ch.copy())
    ShrakeRupley().compute(m, level="A")
    per = {}
    for ch in m:
        for res in ch:
            if res.id[0] != " ":
                continue
            per[(ch.id, res.id[1])] = sum(a.sasa for a in res if a.element != "H")
    return sum(per.values()), per


def heavy(ch, resids=None):
    out = []
    for res in ch:
        if res.id[0] != " ":
            continue
        if resids is not None and res.id[1] not in resids:
            continue
        for a in res:
            if a.element != "H":
                out.append(a)
    return out


def shift(arr, d):
    out = np.zeros_like(arr)
    src, dst = [], []
    for ax in range(3):
        s = d[ax]
        if s == 0:
            src.append(slice(None)); dst.append(slice(None))
        elif s > 0:
            src.append(slice(0, -s)); dst.append(slice(s, None))
        else:
            src.append(slice(-s, None)); dst.append(slice(0, s))
    out[tuple(dst)] = arr[tuple(src)]
    return out


def pockets(atoms, near_atoms):
    if not near_atoms:
        return []
    coords = np.array([a.coord for a in atoms], float)
    radii = np.array([VDW.get(a.element.upper(), 1.7) + 1.4 for a in atoms])
    lo = coords.min(0) - 4.0
    hi = coords.max(0) + 4.0
    dims = np.ceil((hi - lo) / SPACING).astype(int) + 1
    occ = np.zeros(dims, bool)
    for c, r in zip(coords, radii):
        i0 = np.maximum(((c - r - lo) / SPACING).astype(int), 0)
        i1 = np.minimum(((c + r - lo) / SPACING).astype(int) + 1, dims)
        if np.any(i0 >= i1):
            continue
        gx = np.arange(i0[0], i1[0]) * SPACING + lo[0]
        gy = np.arange(i0[1], i1[1]) * SPACING + lo[1]
        gz = np.arange(i0[2], i1[2]) * SPACING + lo[2]
        d2 = ((gx[:, None, None] - c[0]) ** 2 + (gy[None, :, None] - c[1]) ** 2
              + (gz[None, None, :] - c[2]) ** 2)
        occ[i0[0]:i1[0], i0[1]:i1[1], i0[2]:i1[2]] |= d2 <= r * r
    free = ~occ
    psp = np.zeros(dims, np.int8)
    for d in [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1), (1, 1, -1), (1, -1, 1), (-1, 1, 1)]:
        step = SPACING * (sum(x * x for x in d) ** 0.5)
        n = max(1, int(round(DEPTH / step)))
        af = np.zeros(dims, bool); ab = np.zeros(dims, bool)
        sh = occ
        for _ in range(n):
            sh = shift(sh, d); af |= sh
        sh = occ
        dn = tuple(-x for x in d)
        for _ in range(n):
            sh = shift(sh, dn); ab |= sh
        psp += (af & ab & free).astype(np.int8)
    pk = (psp >= PSP_CUT) & free
    if not pk.any():
        return []
    lab, n = ndimage.label(pk)
    sizes = ndimage.sum(pk, lab, range(1, n + 1))
    nc = np.array([a.coord for a in near_atoms], float)
    out = []
    for k in np.argsort(sizes)[::-1][:150]:
        if sizes[k] < 10:
            break
        pts = np.argwhere(lab == k + 1) * SPACING + lo
        dmin = np.sqrt(((pts[:, None, :] - nc[None, :, :]) ** 2).sum(-1)).min()
        if dmin <= 4.0:
            out.append(sizes[k] * SPACING ** 3)
    return sorted(out, reverse=True)


def run(path, pairs, label):
    print("\n=== %s   [%s]" % (label, path))
    chs = load(path)
    for a, b in pairs:
        if a not in chs or b not in chs:
            print("  skip %s-%s (absent)" % (a, b)); continue
        sa, ra = sasa([chs[a]]); sb, rb = sasa([chs[b]]); sab, rab = sasa([chs[a], chs[b]])
        bsa = sa + sb - sab
        ifa = {k[1] for k, v in ra.items() if v - rab.get(k, 0) > 1.0}
        ifb = {k[1] for k, v in rb.items() if v - rab.get(k, 0) > 1.0}
        hyd = tot = 0.0
        for ch, per, ids in ((a, ra, ifa), (b, rb, ifb)):
            for res in chs[ch]:
                if res.id[0] != " " or res.id[1] not in ids:
                    continue
                d = per[(ch, res.id[1])] - rab.get((ch, res.id[1]), 0)
                tot += d
                if res.get_resname() in HYDRO:
                    hyd += d
        pa = pockets(heavy(chs[a]), heavy(chs[a], ifa))
        pb = pockets(heavy(chs[b]), heavy(chs[b], ifb))
        print("  %s-%s BSA=%6.0f A2 tot (%5.0f/side) | iface res %d+%d | apolar %2.0f%% | "
              "pockets on %s at iface: %s | on %s: %s  (A3)"
              % (a, b, bsa, bsa / 2, len(ifa), len(ifb), 100 * hyd / max(tot, 1),
                 a, [round(v) for v in pa[:3]], b, [round(v) for v in pb[:3]]))


if __name__ == "__main__":
    run(sys.argv[1], [tuple(p.split("-")) for p in sys.argv[2].split(",")],
        sys.argv[3] if len(sys.argv) > 3 else "")
