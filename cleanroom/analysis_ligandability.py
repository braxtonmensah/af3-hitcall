"""Is the RNase J : MPN621 interface ligandable at all, on either side?

The screen aims a pocket constraint at this interface. That only makes sense if there is a pocket.
`iface_pocket.py` measured the volumes and `TARGET_EXPANSION.md` read them as "screen MPN621's side
instead, it has a 273 A^3 cavity against RNase J's 26". This checks that reading on the second,
independent model the repo already holds (the *M. genitalium* ortholog), and asks how much of each
cavity is actually at the interface.

Both questions matter because of how this project has been wrong before: a single-model measurement
that looks like a finding, and a number that is technically true but describes a different object
than the claim needs.

Output: `results_ligandability.json`, and a printed table.

Usage:
    py -3.11 analysis_ligandability.py
"""
import json
import os

import numpy as np

import cavity_residues as CR
import iface_pocket as IP

HERE = os.path.dirname(os.path.abspath(__file__))
NB = os.path.join(HERE, "..", "new_biology")

# Chain layout of the 2:2 AF3 models, from cleanroom/provenance.json: A,B = RNase J; C,D = partner.
MODELS = {
    "M_pneumoniae": os.path.join(NB, "rnasej_mpn_2x2_AF3_model_0.cif"),
    "M_genitalium": os.path.join(NB, "rnasej_mg_2x2_AF3_model_0.cif"),
}
# Positions aligning to the B. subtilis J1 catalytic residues. On RNase J all four are conserved
# (H83/D85/H86/H377); on the partner none are, so on that chain they mark the degenerate cleft
# rather than an active site. Either way it is the region most similar to RNase J and to human
# CPSF73, so it is the least selective place to aim a ligand.
CATALYTIC = {"RNaseJ": [83, 85, 86, 377], "partner": [71, 73, 74, 365]}
CHAINS = {"RNaseJ": ("A", "C"), "partner": ("C", "A")}

# Calibration from iface_pocket.py's docstring, run with identical parameters.
CALIBRATION = {"KEAP1:p62 (drugged)": 575, "MDM2:p53 (drugged, shallow)": 76,
               "c-Fos:c-Jun bZIP (flat, undrugged)": 0}
CAT_CUT = 8.0
LINING = 5.0


def analyse(path, chain, partner, catalytic):
    chs = IP.load(path)
    _, ra = IP.sasa([chs[chain]])
    _, rab = IP.sasa([chs[chain], chs[partner]])
    iface = {k[1] for k, v in ra.items() if v - rab.get(k, 0) > 1.0}
    cavs = CR.cavity_grids(IP.heavy(chs[chain]), IP.heavy(chs[chain], iface))
    atoms = [(r.id[1], np.array(a.coord, float))
             for r in chs[chain] if r.id[0] == " " for a in r if a.element != "H"]
    rid = np.array([r for r, _ in atoms])
    rxyz = np.array([c for _, c in atoms])
    cat = rxyz[np.isin(rid, catalytic)]
    out = []
    for vol, pts in cavs:
        dcat = (float(np.sqrt(((pts[:, None, :] - cat[None, :, :]) ** 2).sum(-1)).min())
                if len(cat) else None)
        d = np.sqrt(((rxyz[:, None, :] - pts[None, :, :]) ** 2).sum(-1)).min(axis=1)
        lining = {int(r) for r, dd in zip(rid, d) if dd <= LINING}
        at_if = lining & iface
        out.append({"volume": round(vol, 1), "dist_to_catalytic": None if dcat is None else round(dcat, 1),
                    "catalytic_proximal": bool(dcat is not None and dcat < CAT_CUT),
                    "n_lining": len(lining), "n_lining_at_interface": len(at_if),
                    "frac_at_interface": round(len(at_if) / max(1, len(lining)), 3),
                    "lining_residues": sorted(lining)})
    return {"n_interface_residues": len(iface), "cavities": out}


def main():
    res = {"calibration": CALIBRATION, "catalytic_exclude_A": CAT_CUT, "lining_A": LINING,
           "models": {}}
    for species, path in MODELS.items():
        if not os.path.exists(path):
            print("missing model, skipping:", path)
            continue
        res["models"][species] = {}
        for side, (chain, partner) in CHAINS.items():
            res["models"][species][side] = analyse(path, chain, partner, CATALYTIC[side])

    print("Interface cavities, both models, both sides. Read rank order against the calibration:")
    for k, v in CALIBRATION.items():
        print("   %-38s %5d A^3" % (k, v))
    print("\n%-14s %-8s %8s %9s %10s %8s" %
          ("model", "side", "vol A^3", "d_cat A", "catalytic?", "%iface"))
    summary = {}
    for species, sides in res["models"].items():
        for side, d in sides.items():
            for c in d["cavities"][:3]:
                print("%-14s %-8s %8.0f %9s %10s %7.0f%%" %
                      (species, side, c["volume"],
                       "n/a" if c["dist_to_catalytic"] is None else "%.1f" % c["dist_to_catalytic"],
                       "YES" if c["catalytic_proximal"] else "no",
                       100 * c["frac_at_interface"]))
            nonc = [c for c in d["cavities"] if not c["catalytic_proximal"]]
            summary[(species, side)] = nonc[0] if nonc else None
        print()

    print("Largest NON-catalytic interface cavity per model and side, which is the only one a")
    print("selective ligand could aim at:\n")
    print("%-14s %-8s %8s %8s" % ("model", "side", "vol A^3", "%iface"))
    for (species, side), c in summary.items():
        print("%-14s %-8s %8s %8s" % (species, side,
                                      "none" if c is None else "%.0f" % c["volume"],
                                      "-" if c is None else "%.0f%%" % (100 * c["frac_at_interface"])))
    res["largest_non_catalytic"] = {f"{s}/{d}": (None if c is None else
                                                 {"volume": c["volume"],
                                                  "frac_at_interface": c["frac_at_interface"]})
                                    for (s, d), c in summary.items()}
    with open(os.path.join(HERE, "results_ligandability.json"), "w") as f:
        json.dump(res, f, indent=1)
    print("\nwrote results_ligandability.json")


if __name__ == "__main__":
    main()
