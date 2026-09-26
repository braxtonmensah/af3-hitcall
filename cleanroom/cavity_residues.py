"""Residues lining the largest interface cavity on a chain, for use as a pocket constraint.

`iface_pocket.py` measures cavity volumes to rank candidate targets. This answers the next question:
*which residues* line that cavity, so the screen's pocket constraint can be chosen geometrically.

That is not a cosmetic difference. The previous constraint came from `pocket[:20]`, the twenty
lowest-numbered of sixty-five interface residues, which on this interface kept 25-357 and discarded
358-569, aiming the screen at the catalytic-proximal half. `build_screen_jobs.require_pocket` now
refuses to truncate and asks for an explicit geometric list. This produces that list.

The cavity grid comes from `iface_pocket.pockets`, reused rather than reimplemented so the residues
and the published volumes describe the same object. Cavities within `--catalytic-exclude` angstroms
of any supplied catalytic residue are skipped, because the catalytic cleft is the one place a hit
would be least selective: it keeps 3 of 4 catalytic residues in human CPSF73, and CPSF73 is already
drugged.

Volumes are conformation-sensitive (the same H. pylori cleft measures 415 A^3 at 2.75 A and 5463 at
4.1 A), so read rank order against `iface_pocket.py`'s calibration set and never the raw number.

Usage:
    py -3.11 cavity_residues.py <model.cif> <chain> <partner> [--catalytic 71,73,74,365]
"""
import argparse
import sys

import numpy as np

import iface_pocket as IP


def cavity_grids(atoms, near_atoms, keep=8):
    """Same detection as iface_pocket.pockets, but returns the grid points per cavity.

    iface_pocket.pockets returns volumes only. Rather than change its output and risk moving the
    numbers already written into TARGET_EXPANSION.md, the detection is repeated here with identical
    parameters and the point sets are kept.
    """
    from scipy import ndimage
    if not near_atoms:
        return []
    coords = np.array([a.coord for a in atoms], float)
    radii = np.array([IP.VDW.get(a.element.upper(), 1.7) + 1.4 for a in atoms])
    lo = coords.min(0) - 4.0
    hi = coords.max(0) + 4.0
    dims = np.ceil((hi - lo) / IP.SPACING).astype(int) + 1
    occ = np.zeros(dims, bool)
    for c, r in zip(coords, radii):
        i0 = np.maximum(((c - r - lo) / IP.SPACING).astype(int), 0)
        i1 = np.minimum(((c + r - lo) / IP.SPACING).astype(int) + 1, dims)
        if np.any(i0 >= i1):
            continue
        gx = np.arange(i0[0], i1[0]) * IP.SPACING + lo[0]
        gy = np.arange(i0[1], i1[1]) * IP.SPACING + lo[1]
        gz = np.arange(i0[2], i1[2]) * IP.SPACING + lo[2]
        d2 = ((gx[:, None, None] - c[0]) ** 2 + (gy[None, :, None] - c[1]) ** 2
              + (gz[None, None, :] - c[2]) ** 2)
        occ[i0[0]:i1[0], i0[1]:i1[1], i0[2]:i1[2]] |= d2 <= r * r
    free = ~occ
    psp = np.zeros(dims, np.int8)
    for d in [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1), (1, 1, -1), (1, -1, 1), (-1, 1, 1)]:
        step = IP.SPACING * (sum(x * x for x in d) ** 0.5)
        n = max(1, int(round(IP.DEPTH / step)))
        af = np.zeros(dims, bool)
        ab = np.zeros(dims, bool)
        sh = occ
        for _ in range(n):
            sh = IP.shift(sh, d)
            af |= sh
        sh = occ
        dn = tuple(-x for x in d)
        for _ in range(n):
            sh = IP.shift(sh, dn)
            ab |= sh
        psp += (af & ab & free).astype(np.int8)
    pk = (psp >= IP.PSP_CUT) & free
    if not pk.any():
        return []
    lab, n = ndimage.label(pk)
    sizes = ndimage.sum(pk, lab, range(1, n + 1))
    nc = np.array([a.coord for a in near_atoms], float)
    out = []
    for k in np.argsort(sizes)[::-1][:150]:
        if sizes[k] < 10:
            break
        pts = np.argwhere(lab == k + 1) * IP.SPACING + lo
        dmin = np.sqrt(((pts[:, None, :] - nc[None, :, :]) ** 2).sum(-1)).min()
        if dmin <= 4.0:
            out.append((float(sizes[k] * IP.SPACING ** 3), pts))
        if len(out) >= keep:
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("chain")
    ap.add_argument("partner")
    ap.add_argument("--catalytic", default="",
                    help="comma-separated catalytic residue numbers on <chain>, to exclude their cleft")
    ap.add_argument("--catalytic-exclude", type=float, default=8.0,
                    help="skip a cavity whose nearest point is within this many A of a catalytic residue")
    ap.add_argument("--lining", type=float, default=5.0, help="residue within this distance of a cavity point")
    ap.add_argument("--top", type=int, default=20, help="how many lining residues to print")
    a = ap.parse_args()

    cat = {int(x) for x in a.catalytic.replace(",", " ").split()} if a.catalytic else set()
    chs = IP.load(a.model)
    if a.chain not in chs or a.partner not in chs:
        sys.exit("chains present: %s" % sorted(chs))
    sa, ra = IP.sasa([chs[a.chain]])
    sb, _ = IP.sasa([chs[a.partner]])
    sab, rab = IP.sasa([chs[a.chain], chs[a.partner]])
    iface = {k[1] for k, v in ra.items() if v - rab.get(k, 0) > 1.0}
    print("%s-%s: BSA %.0f A2 total, %d interface residues on %s"
          % (a.chain, a.partner, sa + sb - sab, len(iface), a.chain))

    atoms = IP.heavy(chs[a.chain])
    cavs = cavity_grids(atoms, IP.heavy(chs[a.chain], iface))
    if not cavs:
        sys.exit("no interface cavity found on chain %s" % a.chain)

    # residue coordinates once, for lining and for the catalytic distance test
    res_atoms = []
    for res in chs[a.chain]:
        if res.id[0] != " ":
            continue
        for at in res:
            if at.element != "H":
                res_atoms.append((res.id[1], np.array(at.coord, float)))
    rid = np.array([r for r, _ in res_atoms])
    rxyz = np.array([c for _, c in res_atoms])
    cat_xyz = rxyz[np.isin(rid, list(cat))] if cat else np.zeros((0, 3))

    print("\n%-4s %9s %8s  %s" % ("rank", "vol A^3", "cat d(A)", "verdict"))
    chosen = None
    for i, (vol, pts) in enumerate(cavs, 1):
        if len(cat_xyz):
            dcat = float(np.sqrt(((pts[:, None, :] - cat_xyz[None, :, :]) ** 2).sum(-1)).min())
        else:
            dcat = float("nan")
        skip = len(cat_xyz) and dcat < a.catalytic_exclude
        verdict = "CATALYTIC CLEFT, skipped" if skip else ("selected" if chosen is None else "")
        print("%-4d %9.0f %8.1f  %s" % (i, vol, dcat, verdict))
        if not skip and chosen is None:
            chosen = (vol, pts, dcat)

    if chosen is None:
        sys.exit("every interface cavity on %s is catalytic-proximal; nothing to aim at" % a.chain)

    vol, pts, dcat = chosen
    d = np.sqrt(((rxyz[:, None, :] - pts[None, :, :]) ** 2).sum(-1)).min(axis=1)
    best = {}
    for r, dd in zip(rid, d):
        if dd <= a.lining and (r not in best or dd < best[r]):
            best[r] = dd
    order = sorted(best, key=lambda r: best[r])
    print("\nselected cavity: %.0f A^3, %.1f A from the nearest catalytic residue, "
          "%d lining residues within %.1f A" % (vol, dcat, len(order), a.lining))
    at_iface = [r for r in order if r in iface]
    print("of which %d are interface residues" % len(at_iface))
    sel = order[:a.top]
    print("\nnearest %d lining residues, nearest first:" % len(sel))
    print("  " + ", ".join("%d(%.1f)" % (r, best[r]) for r in sel))
    print("\npass to build_screen_jobs.py --pocket-residues:")
    print(",".join(str(r) for r in sorted(sel)))


if __name__ == "__main__":
    main()
