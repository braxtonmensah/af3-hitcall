"""How conserved is MPN621's cleft against the two proteins a hit must not hit?

`PREREG_MPN621` rests on one claim: MPN621's degenerate cleft is a selectivity prospect because
MPN621 has lost the catalytic machinery that its paralogue (M. pneumoniae RNase J) and the human
off-target (CPSF73) both keep. This measures that claim instead of asserting it, and writes the
numbers the pre-registration quotes.

The informative comparison is **cleft conservation against background identity**. An active site is
normally more conserved than the protein around it, because it is under selection to bind a
substrate. A cleft that is no more conserved than background has lost that constraint, which is what
a catalytically dead cleft should look like and is what makes it a selectivity opportunity.

This is a descriptive measurement over 20 aligned positions. It is a reason to test selectivity, not
a selectivity result; arms O1 and O2 of the pre-registration are the test.

Output: `results_cleft_selectivity.json`.

Usage:
    py -3.11 analysis_cleft_selectivity.py
"""
import json
import os
import urllib.request

from Bio import Align
from Bio.Align import substitution_matrices

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "seqs")

TARGET = ("MPN621", "P75174")
COMPARATORS = [
    ("M_pneumoniae_RNaseJ", "P75497", "the paralogue in the same organism; arm O1"),
    ("human_CPSF73", "Q9UKF6", "the human off-target; arm O2"),
]

# The 20 residues nearest the 491 A^3 cavity in rnasej_mpn_2x2_AF3_model_0.cif, from
# cavity_residues.py. Fixed in PREREG_MPN621 and not to be changed without an amendment.
CLEFT = [15, 18, 37, 69, 71, 73, 74, 142, 162, 163, 201, 234, 329, 332, 334, 358, 359, 363, 365, 387]

# Positions aligning to B. subtilis RNase J1's catalytic H76/D78/H79/H368. On MPN621 none are
# conserved, which is the whole point.
CATALYTIC_EQUIV = [69, 71, 73, 74, 365]


def seq(acc):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, acc + ".fasta")
    if not os.path.exists(p):
        t = urllib.request.urlopen(
            "https://rest.uniprot.org/uniprotkb/%s.fasta" % acc, timeout=90).read().decode()
        if not t.startswith(">"):
            raise SystemExit("UniProt returned no FASTA for " + acc)
        with open(p, "w", newline="\n") as f:
            f.write(t)
    return "".join(open(p).read().split("\n")[1:]).strip()


def aligner():
    a = Align.PairwiseAligner()
    a.substitution_matrix = substitution_matrices.load("BLOSUM62")
    a.open_gap_score = -11
    a.extend_gap_score = -1
    a.mode = "global"
    return a


def compare(target, other, al):
    aln = al.align(target, other)[0]
    m = {}
    for (s1, e1), (s2, e2) in zip(aln.aligned[0], aln.aligned[1]):
        for k in range(e1 - s1):
            m[s1 + k + 1] = s2 + k + 1
    ident = sum(1 for i, j in m.items() if target[i - 1] == other[j - 1])
    background = ident / min(len(target), len(other))
    pairs, same, gap = [], 0, 0
    for r in CLEFT:
        j = m.get(r)
        if j is None:
            gap += 1
            pairs.append({"target": "%s%d" % (target[r - 1], r), "other": None})
            continue
        o = other[j - 1]
        if o == target[r - 1]:
            same += 1
        pairs.append({"target": "%s%d" % (target[r - 1], r), "other": "%s%d" % (o, j),
                      "identical": o == target[r - 1],
                      "catalytic_equivalent": r in CATALYTIC_EQUIV})
    return {"background_identity": round(background, 4),
            "cleft_conserved": same, "cleft_n": len(CLEFT), "cleft_unaligned": gap,
            "cleft_fraction": round(same / len(CLEFT), 3),
            "cleft_vs_background": round((same / len(CLEFT)) / max(background, 1e-9), 2),
            "positions": pairs}


def main():
    al = aligner()
    tgt = seq(TARGET[1])
    out = {"target": {"name": TARGET[0], "accession": TARGET[1], "length": len(tgt)},
           "cleft_residues": CLEFT, "catalytic_equivalent_positions": CATALYTIC_EQUIV,
           "comparisons": {}}
    print("target: %s (%s), %d aa" % (TARGET[0], TARGET[1], len(tgt)))
    print("cleft: %d residues nearest the 491 A^3 cavity\n" % len(CLEFT))
    print("%-24s %10s %14s %10s" % ("comparator", "background", "cleft conserved", "ratio"))
    for name, acc, note in COMPARATORS:
        r = compare(tgt, seq(acc), al)
        out["comparisons"][name] = dict(r, accession=acc, note=note)
        print("%-24s %9.1f%% %6d/%d %5.0f%% %9.2f"
              % (name, 100 * r["background_identity"], r["cleft_conserved"], r["cleft_n"],
                 100 * r["cleft_fraction"], r["cleft_vs_background"]))
    print("\nA ratio near 1 means the cleft is no more conserved than the protein as a whole, i.e.")
    print("it carries no active-site conservation constraint. Above 1 would mean the cleft IS")
    print("conserved and the selectivity premise is weaker than it looks.\n")

    print("The catalytic-equivalent positions, which is where the argument lives:")
    for name in out["comparisons"]:
        ps = [p for p in out["comparisons"][name]["positions"] if p.get("catalytic_equivalent")]
        print("  %-24s %s" % (name, "  ".join(
            "%s->%s" % (p["target"], p["other"] or "gap") for p in ps)))
    print("\nRNase J and CPSF73 share the catalytic His/Asp cluster. MPN621 does not, which is the")
    print("reason a ligand in its cleft could be selective against both.")

    with open(os.path.join(HERE, "results_cleft_selectivity.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("\nwrote results_cleft_selectivity.json")


if __name__ == "__main__":
    main()
