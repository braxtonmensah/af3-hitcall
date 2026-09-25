"""PREREG_RNAP3: are MG354's five in-cell crosslinks within reach in a three-chain model?

Usage:  python score_rnap3.py <model.cif | model.pdb>

Reads the model, assigns chains by length (MG354 136, RpoB 1391, RpoC 1290), then applies the
pre-registered rule: read the RpoB-RpoC control first, and only interpret MG354 if the control
passes. Works on AlphaFold Server .cif and Boltz-2 .cif/.pdb alike.
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CUT = 30.0
LEN = {"A": 136, "B": 1391, "C": 1290}   # MG354, RpoB, RpoC
NAME = {"A": "MG354", "B": "RpoB", "C": "RpoC"}
rng = np.random.default_rng(25)


def parse(path):
    """-> {chain_label: {resnum: (x,y,z)}} for CA atoms, keyed by the file's own chain ids"""
    ch = {}
    if path.lower().endswith(".cif"):
        cols, inloop, hdr = {}, False, []
        for line in open(path, errors="replace"):
            if line.startswith("_atom_site."):
                hdr.append(line.strip().split(".")[1]); inloop = True; continue
            if inloop and (line.startswith("#") or line.startswith("loop_")):
                if cols: break
                inloop = bool(hdr); continue
            if hdr and line.startswith(("ATOM", "HETATM")):
                f = line.split()
                if not cols:
                    cols = {k: i for i, k in enumerate(hdr)}
                if f[cols["label_atom_id"]] != "CA":
                    continue
                c = f[cols.get("auth_asym_id", cols["label_asym_id"])]
                try:
                    n = int(f[cols.get("auth_seq_id", cols["label_seq_id"])])
                except ValueError:
                    continue
                ch.setdefault(c, {})[n] = (float(f[cols["Cartn_x"]]), float(f[cols["Cartn_y"]]), float(f[cols["Cartn_z"]]))
    else:
        for line in open(path, errors="replace"):
            if line.startswith("ATOM") and line[12:16].strip() == "CA":
                ch.setdefault(line[21], {})[int(line[22:26])] = (float(line[30:38]), float(line[38:46]), float(line[46:54]))
    return ch


def assign(ch):
    """map file chain ids -> A/B/C by residue count (the three lengths are far apart)"""
    out = {}
    for want, n in LEN.items():
        best = min(ch, key=lambda c: abs(len(ch[c]) - n))
        if abs(len(ch[best]) - n) > 25:
            sys.exit(f"no chain near {n} residues for {NAME[want]}; found {[(c, len(v)) for c, v in ch.items()]}")
        out[want] = ch.pop(best)
    return out


def d(ch, c1, r1, c2, r2):
    a, b = ch[c1].get(r1), ch[c2].get(r2)
    return None if a is None or b is None else float(np.linalg.norm(np.array(a) - np.array(b)))


def null(ch, links, seqs):
    """random lysine (or N-term) pairs across the same chain pairs, 1000 draws"""
    frac = []
    for _ in range(1000):
        hit = 0
        for c1, _r1, c2, _r2 in links:
            K1 = [i for i, aa in enumerate(seqs[c1], 1) if aa == "K"] or list(ch[c1])
            K2 = [i for i, aa in enumerate(seqs[c2], 1) if aa == "K"] or list(ch[c2])
            v = d(ch, c1, int(rng.choice(K1)), c2, int(rng.choice(K2)))
            hit += (v is not None and v <= CUT)
        frac.append(hit / len(links))
    return float(np.mean(frac)), float(np.quantile(frac, 0.95))


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    L = json.load(open(os.path.join(HERE, "links.json")))
    S = json.load(open(r"C:\Users\bmens\NQ_local\af3-hitcall\omega\seqs.json"))
    seqs = {"A": S["MG354_MPN530"], "B": S["RpoB_MPN516"], "C": S["RpoC_MPN515"]}
    ch = assign(parse(sys.argv[1]))
    print(f"chains: " + ", ".join(f"{NAME[k]} {len(v)} res" for k, v in ch.items()))

    ctl = [(a, int(b), c, int(e)) for a, b, c, e in L["control"]]
    dc = [d(ch, *x) for x in ctl]
    ok = [v for v in dc if v is not None]
    fc = sum(v <= CUT for v in ok) / len(ok)
    print(f"\nCONTROL  RpoB-RpoC, {len(ok)} links: {fc:.2f} within {CUT:.0f} A   median {np.median(ok):.1f} A")
    if fc < 0.7:
        print("  -> CONTROL FAILS (<0.70). Per PREREG_RNAP3 the MG354 result is NOT interpreted.")
    else:
        print("  -> control passes; MG354 result is interpretable")

    mg = [(a, int(b), c, int(e)) for a, b, c, e in L["mg354"]]
    dm = [d(ch, *x) for x in mg]
    print(f"\nPRIMARY  MG354, {len(mg)} links:")
    for (c1, r1, c2, r2), v in zip(mg, dm):
        print(f"  {NAME[c1]:5s} {r1:5d} <-> {NAME[c2]:5s} {r2:5d}   " + ("n/a" if v is None else f"{v:6.1f} A  {'OK' if v <= CUT else 'far'}"))
    good = [v for v in dm if v is not None]
    n_ok = sum(v <= CUT for v in good)
    nm, np95 = null(ch, mg, seqs)
    print(f"\n  satisfied {n_ok} of {len(good)}   null mean {nm:.2f}  null p95 {np95:.2f}")
    frac = n_ok / len(good)
    if fc < 0.7:
        v = "NOT INTERPRETED (control failed)"
    elif n_ok >= 4 and frac > np95:
        v = "SUPPORTED: MG354 binds the assembled core"
    elif n_ok >= 2 and frac > np95:
        v = "PARTIAL"
    elif n_ok <= 1:
        v = "NOT SUPPORTED: three chains do not explain the crosslinks either"
    else:
        v = "INCONCLUSIVE"
    print(f"\n  VERDICT: {v}")


if __name__ == "__main__":
    main()
