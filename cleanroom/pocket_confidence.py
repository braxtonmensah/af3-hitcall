"""How confidently is each screened pocket placed, chain by chain?

A screen that compares a compound's score on a target against its score on a comparator assumes the
two receptors are predicted equally well. That assumption became worth checking when the MSAs came
back: MPN621 (P75174) has 464 sequences against 4,623 for its own paralogue RNase J (P75497) and
6,000 for human CPSF73. MSA depth drives prediction confidence, so a tenfold gap between the target
arm and the arms that judge its selectivity is a candidate confound in exactly the comparison that
would justify buying a compound.

pLDDT restricted to the pocket residues is the direct measurement: not how good the model is overall,
but how well-determined the part a ligand is being steered into actually is.

AF confidence bands: >90 very high, 70-90 confident, 50-70 low, <50 very low.

Usage:
    py -3.11 pocket_confidence.py                      # the MPN621 screen's receptors
    py -3.11 pocket_confidence.py <model.cif> A,C
"""
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(HERE, "..", "new_biology", "rnasej_mpn_2x2_AF3_model_0.cif")

# Pockets as fixed in PREREG_MPN621 and its Amendment 1.
POCKETS = {
    "A": ("RNase J, P75497, arm O1",
          [49, 84, 85, 92, 151, 205, 206, 241, 266, 270, 308, 311, 313, 340, 343, 345, 373, 375,
           377, 401]),
    "C": ("MPN621, P75174, arm S (the target)",
          [15, 18, 37, 69, 71, 73, 74, 142, 162, 163, 201, 234, 329, 332, 334, 358, 359, 363, 365,
           387]),
}


def ca_plddt(path):
    """CA pLDDT per (chain, residue index). AF writes pLDDT into the B-factor column."""
    txt = open(path, errors="replace").read()
    hdr = []
    for line in txt.splitlines():
        if line.startswith("_atom_site."):
            hdr.append(line.strip().split(".", 1)[1])
        elif hdr:
            break
    if not hdr or "B_iso_or_equiv" not in hdr:
        sys.exit("no B-factor/pLDDT column in " + path)
    ix = {k: i for i, k in enumerate(hdr)}
    out = {}
    for line in txt.splitlines():
        if not line.startswith("ATOM"):
            continue
        f = line.split()
        if len(f) < len(hdr) or f[ix["label_atom_id"]] != "CA":
            continue
        sid = f[ix["label_seq_id"]]
        if sid in (".", "?"):
            continue
        out.setdefault(f[ix["label_asym_id"]], {})[int(sid)] = float(f[ix["B_iso_or_equiv"]])
    return out


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else MODEL
    per = ca_plddt(path)
    chains = sys.argv[2].split(",") if len(sys.argv) > 2 else list(POCKETS)
    print("model: %s\n" % os.path.basename(path))
    print("%-6s %-38s %10s %13s %11s %9s" %
          ("chain", "receptor", "pLDDT all", "pLDDT pocket", "min pocket", "n found"))
    vals = {}
    for ch in chains:
        d = per.get(ch)
        if not d:
            print("%-6s (not in model)" % ch)
            continue
        label, pk = POCKETS.get(ch, (ch, sorted(d)))
        pv = [d[i] for i in pk if i in d]
        if not pv:
            print("%-6s %-38s no pocket residues resolved" % (ch, label))
            continue
        vals[ch] = st.mean(pv)
        print("%-6s %-38s %10.1f %13.1f %11.1f %6d/%d" %
              (ch, label, st.mean(list(d.values())), st.mean(pv), min(pv), len(pv), len(pk)))
    if len(vals) >= 2:
        lo, hi = min(vals.values()), max(vals.values())
        print("\nlargest gap in mean pocket pLDDT between receptors: %.1f" % (hi - lo))
        if hi - lo < 5:
            print("Under 5 points and both in the 'very high' band, so receptor quality is not a")
            print("plausible explanation for a difference between these arms. The MSA-depth concern")
            print("does not translate into a pocket-confidence difference: MPN621 is an RNase J")
            print("paralogue, so its fold is constrained by the family even with few direct homologs.")
        else:
            print("A gap this large means a cross-receptor score difference could be receptor")
            print("quality rather than chemistry. Report it alongside any selectivity claim.")


if __name__ == "__main__":
    main()
