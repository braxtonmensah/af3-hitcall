"""Build the PREREG_VSCREEN gate jobs from primary sources.

The gate asks whether this pipeline can recover known ligands of folds related to the target, because
nothing is known to bind bacterial RNase J itself (POSITIVE_CONTROLS.md, section 5). Every sequence
and every ligand here is fetched from RCSB rather than transcribed, and cached under gate_cache/ so
a rebuild needs no network and the inputs are auditable.

Three decisions are encoded here and each one is a correction to what the plan said before the
structures were read.

**1. Receptors are the crystallised constructs, not full-length UniProt.** 6M8Q's CPSF3 entity is
478 residues against 684 in UniProt; 8C8S's SNM1A is 343 against 1,040. Using full length would
change the protein, cost several times more, and fold domains the co-crystal never contained. The
construct sequence is taken from the polymer entity of the entry that holds the ligand.

**2. One catalytic metal per nuclease chain, as Zn.** The assumption going in was the canonical
di-zinc metallo-beta-lactamase site. The deposited structures of this subfamily do not support it:
6M8Q has 2 Zn for 2 protein copies, 8C8S has 1 Zn, 7APV has 1 Zn (plus a Ni), and 3ZQ4 -- the
B. subtilis RNase J1 tetramer that is the template for this project's own RNase J model -- has 4 Zn
and 4 Ca across 4 chains. That is one catalytic Zn per chain throughout. 8T1Q models Fe rather than
Zn, which Tao et al. attribute to bacterial expression, so Zn is substituted there; PREREG_VSCREEN
Amendment 1 requires one policy applied identically to the gate receptors and the target, and this
is it.

**3. Crystallisation additives are excluded.** PO4, SO4, CL, EDO, DMS and the idiosyncratic second
ions (the Ni in 7APV, the Ca in 3ZQ4) are not modelled. They are artefacts of the drop, not the
biology, and including them for some receptors and not others is exactly the inconsistency the
amendment forbids.

The one receptor exempt from the Zn rule is nsp10-nsp14, which is not an MBL-fold protein: its
2 Zn plus 1 Mg are a structural zinc site and the ExoN catalytic metal, both real, so it is built as
deposited.

Usage:
    python build_gate.py --plan                     # what would be written, and the cost
    python build_gate.py --msa-prefix /workspace/gate/msa --out-dir gate_jobs
    python build_gate.py --msa-prefix ... --decoys 60 --selection selection_v1.tsv
"""
import argparse
import csv
import json
import os
import random
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "gate_cache")
# Matches the screen's constraint width (build_screen_jobs.MAX_POCKET_CONTACTS), because the gate
# only transfers to the screen if the two run the same protocol.
MAX_POCKET_CONTACTS = 20

# Crystallisation additives and structure-idiosyncratic ions: never modelled. See docstring.
ADDITIVES = {"PO4", "SO4", "CL", "EDO", "DMS", "GOL", "ACT", "NI", "CA", "NA", "K"}

# ---------------------------------------------------------------------------- the gate, declared

# Each receptor names the PDB entry whose polymer entities give the construct sequence. `entities`
# maps the chain id used in the job to the entity id in that entry. `metals` is the policy outcome,
# not the deposition: a list of (CCD code, copies).
RECEPTORS = {
    "cpsf73": {
        "pdb": "6M8Q", "entities": {"A": "1"}, "metals": [("ZN", 1)], "pocket_ref": ("6M8Q", "JBG"),
        "note": "human CPSF73/CPSF3 catalytic segment, 478 aa. Deposited with 2 Zn for 2 copies.",
    },
    "snm1a": {
        "pdb": "8C8S", "entities": {"A": "1"}, "metals": [("ZN", 1)], "pocket_ref": ("8C8S", "U2O"),
        "note": "human SNM1A/DCLRE1A, 343 aa. Deposited with 1 Zn.",
    },
    "artemis": {
        "pdb": "7APV", "entities": {"A": "1"}, "metals": [("ZN", 1)], "pocket_ref": ("7APV", "9F2"),
        "note": "human Artemis/DCLRE1C, 362 aa. Deposited 1 Zn + 1 Ni; the Ni is dropped as an "
                "additive. NOTE the Zn here is a STRUCTURAL His2Cys2 site (H229/H255/C257/C273), "
                "14.1 A from ceftriaxone, not the catalytic metal: 7APV models no catalytic metal "
                "at all. Kept because the site is real biology, but it is not the same kind of Zn "
                "as the one in 6M8Q or 8C8S.",
    },
    "nsp1014": {
        "pdb": "9FWM", "entities": {"A": "1", "B": "2"}, "metals": [("ZN", 2), ("MG", 1)], "pocket_ref": ("9FWM", "A1IGR"),
        "note": "SARS-CoV-2 nsp10 (131 aa) + nsp14 ExoN (290 aa). Not MBL fold; built as deposited.",
    },
    # Declared and deliberately NOT built by default. The Drosophila Integrator cleavage module is
    # IntS4 1032 + IntS11 597 + IntS9 654 = 2,283 residues, which is an 80GB-class job per ligand
    # and would cost more than the entire main screen. Recorded here so that the reason it is absent
    # is in the code rather than in someone's memory. --with-integrator builds it anyway.
    "integrator": {
        "pdb": "7SN8", "entities": {"A": "1", "B": "2", "C": "3"}, "metals": [("ZN", 1)], "pocket_ref": ("7SN8", "IHP"),
        "optional": True,
        "note": "Drosophila IntS4-IntS9-IntS11 + IP6. 2,283 residues: infeasible on affordable GPUs.",
    },
}

# tier: what a pass licenses. expect: the direction the criterion predicts.
LIGANDS = [
    # Tier A: known active-site ligands of this fold, each with a co-crystal.
    dict(name="jte607_acid", ccd="JBG", receptor="cpsf73", tier="A", expect="high",
         representable=True,
         why="Kd 370 nM reported, co-crystal 6M8Q. Boron-free and does not chelate the metals, so "
             "it tests pocket recognition rather than metal coordination. That property is now "
             "load-bearing: the affinity head pools only protein-binder and binder-binder pairs "
             "and cannot see ions, so this is one of only three rungs whose binding mode it can "
             "represent at all. The gate rests on it."),
    dict(name="tao1", ccd="XYX", pdb="8T1Q", receptor="cpsf73", tier="A", expect="high",
         representable=False,
         why="photoaffinity + probe displacement + co-crystal 8T1Q. Anionic boronate whose boron "
             "oxygens coordinate the active-site metals. The affinity head cannot represent that, "
             "so this rung is EXPECTED TO FAIL for a reason internal to the model. Diagnostic, "
             "not load-bearing."),
    dict(name="tao2", ccd="XZC", pdb="8T1R", receptor="cpsf73", tier="A", expect="high",
         representable=False,
         why="near-analogue of tao1, co-crystal 8T1R. Same metal-chelating mode, same expected "
             "failure."),
    dict(name="snm1a_hydroxamate", ccd="U2O", receptor="snm1a", tier="A", expect="high",
         representable=False,
         why="IC50 0.8 uM on purified enzyme, co-crystal 8C8S. Second MBL-beta-CASP protein, but "
             "the hydroxamate chelates both metals and its pocket is the metal-binding motif "
             "itself (H37/S38/D39/H40/H96/D118), so the affinity head cannot represent it either. "
             "Diagnostic."),
    dict(name="ceftriaxone", ccd="9F2", receptor="artemis", tier="A", expect="high",
         representable=True,
         why="co-crystal 7APV at 65 uM. The deliberate weak rung, and measured from the "
             "coordinates it is NOT a metal chelator: its closest atom is 14.1 A from the only Zn "
             "in the entry, which is a structural His2Cys2 site. So its mode is representable and "
             "it is a real rung, not just a diagnostic."),
    # Tier B: a ligand at a protein-protein interface, which is what the screen actually asks.
    dict(name="nsp14_fragment", ccd="A1IGR", receptor="nsp1014", tier="B", expect="high",
         representable=True,
         why="1H-indole-3-carboxamide, 9 heavy atoms, from the nsp10-nsp14 fragment campaign "
             "(PMID 40794865). A true drug-like fragment at a nuclease/partner interface, and the "
             "harder and more informative of the two Tier B rungs. No metal contact, so its mode "
             "is representable. Tier B rests on it alone."),
    dict(name="ip6", ccd="IHP", receptor="integrator", tier="B", expect="high", optional=True,
         why="the only documented small molecule at a PPI interface in this fold family, 55 A from "
             "the INTS11 active site (7SN8). A hexa-anion in an electropositive pocket is the "
             "easiest interface case imaginable, so a pass here is weak evidence."),
    # Negative controls. These sharpen Tier A: each one fails for a stated, different reason.
    dict(name="jte607_parent_ester", smiles="CCOC(=O)[C@H](Cc1ccccc1)NC(=O)c1cc(Cl)c(OCCN2CCN(C)CC2)c(Cl)c1O",
         receptor="cpsf73", tier="neg", expect="below_jte607_acid",
         why="the prodrug ester, not the binding species. If it outscores its own free acid the "
             "pipeline is rewarding lipophilicity rather than recognition."),
    dict(name="an3661", smiles="B1(C2=C(CO1)C=CC=C2CCC(=O)O)O", receptor="cpsf73", tier="neg",
         expect="low",
         why="potent antiparasitic, human cytotoxicity 60 to >100 uM across six lines, i.e. no "
             "evidence of engaging the human protein."),
    dict(name="ebselen", smiles="O=C1N(c2ccccc2)[Se]c2ccccc21", receptor="artemis", tier="neg",
         expect="low", why="inhibits by selenium/thiol reactivity, no co-crystal. A structure-based "
                          "score should not rationalise it. May also fail to featurise: Se."),
    dict(name="disulfiram", smiles="CCN(CC)C(=S)SSC(=S)N(CC)CC", receptor="artemis", tier="neg",
         expect="low", why="thiol-reactive, no co-crystal."),
]

# Named and excluded, so nobody adds them back: refuted as colloidal aggregators, PMID 33972249.
EXCLUDED = {"RNPA2000", "purpurin", "iriginol hexaacetate"}


# ---------------------------------------------------------------------------- fetching, cached

def _cached(name, url, parse=json.loads):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, name)
    if not os.path.exists(p):
        try:
            txt = urllib.request.urlopen(url, timeout=120).read().decode()
        except Exception as e:
            sys.exit("fetch failed for %s: %s" % (url, e))
        # Written via a temp file and renamed. A partial write leaves a file that exists and is
        # therefore treated as cached, so the next run reads truncated JSON and fails somewhere
        # unrelated. encoding is not optional either: RCSB descriptions carry prime and dash
        # characters that Windows' default cp1252 cannot encode, and that is what truncated it.
        tmp = p + ".part"
        with open(tmp, "w", newline="\n", encoding="utf-8") as f:
            f.write(txt)
        os.replace(tmp, p)
    return parse(open(p, encoding="utf-8").read())


TAG_PATTERNS = [
    # Terminal expression tags, matched only at the termini. Stripping these is not cosmetic: 6M8Q's
    # CPSF3 entity begins GSSHHHHHHSSGLVPRGSH, a His6 plus a thrombin site, and **a His tag chelates
    # metals**. Leaving it in a job that also supplies a Zn ion invites the tag to take the zinc,
    # on the receptor that carries the gate's load-bearing rung. It is also 19 residues of
    # disordered linker the model would try to place.
    r"^[GSAM]{0,6}H{6,10}[GSAM]{0,4}(?:LVPR.?GS)?[GSAMH]{0,4}",
    r"^M?[GSA]{0,4}(?:ENLYFQ[GS]?)",
    r"^M?[GSA]{0,4}(?:WSHPQFEK)[GSA]{0,6}",
    r"(?:H{6,10})[GSAM]{0,6}$",
]


def uniprot_seq(acc):
    """Native sequence, cached. The authority on where a construct's tag ends."""
    txt = _cached("up_%s.fasta" % acc, "https://rest.uniprot.org/uniprotkb/%s.fasta" % acc,
                  parse=lambda t: t)
    return "".join(txt.split("\n")[1:]).strip()


def strip_tags(s, acc=None, probe=15):
    """Trim terminal expression tags. Returns (sequence, n_trimmed_from_N_terminus).

    Anchored to the native UniProt sequence rather than to regexes, because guessing where a tag
    ends is exactly the kind of thing that goes wrong quietly: a pattern for His6 plus a thrombin
    site over-trimmed 6M8Q by three residues and ate the native MSA that Q9UKF6 begins with. Here
    the first position whose following `probe`-mer occurs in the native sequence is the true start
    of the construct, and everything before it is tag.

    The N-terminal count is returned because every residue index taken from the deposited
    coordinates indexes the UNTRIMMED sequence. Trimming without shifting those indices would leave
    the pocket pointing at the wrong residues, which is the same class of defect as the pocket
    truncation recorded in PREREG_VSCREEN Amendment 3.
    """
    if not acc:
        return s, 0
    try:
        native = uniprot_seq(acc)
    except SystemExit:
        return s, 0
    if not native:
        return s, 0
    n_trim = 0
    for i in range(0, min(len(s) - probe, 80)):
        if s[i:i + probe] in native:
            n_trim = i
            break
    else:
        return s, 0
    if n_trim and len(s) - n_trim < 80:
        return s, 0
    s = s[n_trim:]
    # Trailing tag: walk back while the tail stops matching the native sequence.
    for j in range(len(s), max(len(s) - 80, 80), -1):
        if s[j - probe:j] in native:
            s = s[:j]
            break
    return s, n_trim


def entity_seq(pdb, entity, with_offset=False):
    d = _cached("%s_ent%s.json" % (pdb, entity),
                "https://data.rcsb.org/rest/v1/core/polymer_entity/%s/%s" % (pdb, entity))
    s = (d.get("entity_poly") or {}).get("pdbx_seq_one_letter_code_can", "")
    s = "".join(s.split())
    if not s:
        sys.exit("no sequence for %s entity %s" % (pdb, entity))
    refs = ((d.get("rcsb_polymer_entity_container_identifiers") or {})
            .get("reference_sequence_identifiers") or [])
    acc = next((r.get("database_accession") for r in refs
                if (r.get("database_name") or "").upper().startswith("UNIPROT")), None)
    s, n_trim = strip_tags(s, acc)
    # Canonical one-letter code can carry X for modified residues; Boltz needs standard residues.
    bad = set(s) - set("ACDEFGHIKLMNPQRSTVWY")
    if bad:
        print("  note: %s ent%s contains non-standard residues %s, replacing with G"
              % (pdb, entity, sorted(bad)))
        for b in bad:
            s = s.replace(b, "G")
    return (s, n_trim) if with_offset else s


def cif_text(pdb):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, pdb + ".cif")
    if not os.path.exists(p):
        tmp = p + ".part"
        with open(tmp, "wb") as f:
            f.write(urllib.request.urlopen(
                "https://files.rcsb.org/download/%s.cif" % pdb, timeout=180).read())
        os.replace(tmp, p)
    return open(p, encoding="utf-8", errors="replace").read()


def pocket_from_cif(pdb, ccd, entity_chains, cutoff=5.0, offsets=None):
    """Residues within `cutoff` A of the named ligand, as (chain_id, seq_index) pairs.

    Why this exists: the screen steers each ligand to the RNase J interface with a `pocket`
    constraint. If the gate ran unconstrained, the gate and the screen would not be the same
    protocol, and a gate pass would not transfer to the screen -- a pocket constraint changes both
    the pose search and, plausibly, the score. So each gate ligand is constrained to its OWN
    crystallographic site. Same protocol, different and correct pocket.

    Positions are returned as 1-based indices into the entity's canonical sequence, because that is
    what Boltz indexes, and label_seq_id in the deposited file is already that index.
    """
    text = cif_text(pdb)
    lines = [l for l in text.splitlines() if l.startswith(("ATOM ", "HETATM"))]
    if not lines:
        return []
    # The atom_site loop is fixed-column in the PDBx flat form RCSB serves; parse by field order
    # from the loop header rather than assuming offsets.
    hdr = []
    for l in text.splitlines():
        if l.startswith("_atom_site."):
            hdr.append(l.strip().split(".", 1)[1])
        elif hdr and not l.startswith("_atom_site."):
            break
    if not hdr:
        return []
    ix = {k: i for i, k in enumerate(hdr)}
    need = ["group_PDB", "label_comp_id", "label_asym_id", "label_seq_id",
            "Cartn_x", "Cartn_y", "Cartn_z", "label_atom_id"]
    if any(k not in ix for k in need):
        return []
    lig, prot = [], []
    for l in lines:
        f = l.split()
        if len(f) < len(hdr):
            continue
        comp = f[ix["label_comp_id"]]
        try:
            xyz = (float(f[ix["Cartn_x"]]), float(f[ix["Cartn_y"]]), float(f[ix["Cartn_z"]]))
        except ValueError:
            continue
        if comp == ccd:
            lig.append(xyz)
        elif f[ix["group_PDB"]] == "ATOM":
            sid = f[ix["label_seq_id"]]
            if sid not in (".", "?"):
                prot.append((f[ix["label_asym_id"]], int(sid), xyz))
    if not lig:
        return []
    c2 = cutoff * cutoff
    # Keep the closest approach per residue, not just membership. The list gets truncated to 20
    # contacts later and the truncation has to be geometric: taking the 20 lowest residue NUMBERS
    # is what vscreen.py did, and on the RNase J interface that silently kept residues 25-357 and
    # threw away 358-569 entirely, biasing the constraint toward one half of the interface.
    best = {}
    for asym, sid, (x, y, z) in prot:
        for (lx, ly, lz) in lig:
            d2 = (x - lx) ** 2 + (y - ly) ** 2 + (z - lz) ** 2
            if d2 <= c2:
                k = (asym, sid)
                if k not in best or d2 < best[k]:
                    best[k] = d2
    hits = set(best)
    # Map deposited asym ids onto the chain letters this job uses. Single-chain receptors take the
    # asym that carries the most contacts; multi-chain ones are mapped by order of first appearance.
    order = []
    for asym, _ in sorted(hits):
        if asym not in order:
            order.append(asym)
    counts = {}
    for asym, _ in hits:
        counts[asym] = counts.get(asym, 0) + 1
    want = [c for c, _ in entity_chains]
    if len(want) == 1:
        top = max(counts, key=counts.get)
        sel = [(want[0], sid, best[(asym, sid)]) for asym, sid in hits if asym == top]
    else:
        mapping = {a: want[i] for i, a in enumerate(sorted(counts, key=counts.get, reverse=True))
                   if i < len(want)}
        sel = [(mapping[a], sid, best[(a, sid)]) for a, sid in hits if a in mapping]
    # Shift to the trimmed sequence the job actually carries. label_seq_id indexes the UNTRIMMED
    # entity sequence, so a stripped expression tag moves every index; a contact that fell inside
    # the tag is dropped rather than remapped, because it has no counterpart in the job.
    if offsets:
        shifted = []
        for c, sid, d2 in sel:
            off = offsets.get(c, 0)
            if sid - off >= 1:
                shifted.append((c, sid - off, d2))
        sel = shifted
    # Nearest first, so a later truncation keeps the residues that actually line the site.
    sel.sort(key=lambda t: t[2])
    return [(c, sid) for c, sid, _ in sel]


def ccd_smiles(ccd):
    d = _cached("cc_%s.json" % ccd, "https://data.rcsb.org/rest/v1/core/chemcomp/%s" % ccd)
    best = None
    for s in d.get("pdbx_chem_comp_descriptor", []):
        if s.get("type") == "SMILES_CANONICAL" and "OpenEye" in (s.get("program") or ""):
            best = s.get("descriptor")
    if best is None:
        for s in d.get("pdbx_chem_comp_descriptor", []):
            if "SMILES" in (s.get("type") or ""):
                best = s.get("descriptor")
                break
    if not best:
        sys.exit("no SMILES for CCD " + ccd)
    return best, (d.get("chem_comp") or {}).get("name", "")


# ---------------------------------------------------------------------------- writing

def job_yaml(chains, metals, binder_smiles, msa_paths, pocket=None):
    """Boltz-2 input: protein chains, metal ions, one scored binder.

    Metals are written as CCD references rather than SMILES because a bare ion has no covalent
    structure to canonicalise and the CCD code is what the deposition itself uses.
    """
    y = ["version: 1", "sequences:"]
    for cid, seq in chains:
        y += ["  - protein:", "      id: " + cid, "      sequence: " + seq]
        if msa_paths.get(cid):
            y.append('      msa: "' + msa_paths[cid] + '"')
    used = {c for c, _ in chains} | {"L"}
    nxt = (c for c in "MNOPQRSTUVWXYZ" if c not in used)
    for ccd, n in metals:
        for _ in range(n):
            y += ["  - ligand:", "      id: " + next(nxt), "      ccd: " + ccd]
    y += ["  - ligand:", "      id: L", "      smiles: '" + binder_smiles + "'",
          "properties:", "  - affinity:", "      binder: L"]
    if pocket:
        contacts = ", ".join("[%s, %d]" % (c, i) for c, i in pocket[:MAX_POCKET_CONTACTS])
        y += ["constraints:", "  - pocket:", "      binder: L", "      contacts: [" + contacts + "]"]
    return "\n".join(y) + "\n"


def main(a):
    if ":" in a.msa_prefix or "\\" in a.msa_prefix:
        sys.exit("--msa-prefix looks like a Windows path: %r\nGit Bash rewrites POSIX paths; "
                 "prefix the command with MSYS_NO_PATHCONV=1 or use PowerShell." % a.msa_prefix)
    if not a.msa_prefix.startswith("/"):
        sys.exit("--msa-prefix must be absolute on the machine that runs the jobs")
    msa_prefix = a.msa_prefix.rstrip("/")

    ligands = [l for l in LIGANDS if not l.get("optional") or a.with_integrator]
    receptors_used = sorted({l["receptor"] for l in ligands})
    for r in receptors_used:
        if RECEPTORS[r].get("optional") and not a.with_integrator:
            sys.exit("internal: optional receptor %s selected" % r)

    # Resolve every sequence and ligand first, so a fetch failure costs nothing written.
    print("resolving receptors")
    chains, seqs, offsets = {}, {}, {}
    for r in receptors_used:
        spec = RECEPTORS[r]
        cs, off = [], {}
        for cid, ent in sorted(spec["entities"].items()):
            seq_s, n_trim = entity_seq(spec["pdb"], ent, with_offset=True)
            cs.append((cid, seq_s))
            off[cid] = n_trim
            seqs["%s_%s" % (r, cid)] = seq_s
        chains[r] = cs
        offsets[r] = off
        n = sum(len(x) for _, x in cs)
        trimmed = ", ".join("%s-%d" % (c, v) for c, v in off.items() if v)
        print("  %-11s %s  %d chain(s), %4d residues, metals %s%s"
              % (r, spec["pdb"], len(cs), n, spec["metals"],
                 "  tag trimmed: " + trimmed if trimmed else ""))

    # Pocket per (receptor, structure, ligand), resolved once and reused.
    _pk_cache = {}

    def pockets_for(r, pdb, ccd):
        k = (r, pdb, ccd)
        if k not in _pk_cache:
            pk = pocket_from_cif(pdb, ccd, chains[r], offsets=offsets[r])
            if not pk:
                sys.exit("no pocket contacts found for %s in %s; refusing to write an "
                         "unconstrained gate job, because the screen is constrained and the two "
                         "would not be the same protocol" % (ccd, pdb))
            lens = {c: len(x) for c, x in chains[r]}
            bad = [(c, i) for c, i in pk if not (1 <= i <= lens.get(c, 0))]
            if bad:
                sys.exit("pocket indices outside the trimmed sequence for %s/%s: %s. A tag was "
                         "stripped without shifting the coordinates' indices." % (pdb, ccd, bad[:5]))
            _pk_cache[k] = pk
        return _pk_cache[k]

    print("resolving pockets from the co-crystals")
    ref_pocket = {}
    for r in receptors_used:
        rp, rc = RECEPTORS[r]["pocket_ref"]
        ref_pocket[r] = pockets_for(r, rp, rc)
        pk = ref_pocket[r]
        chs = sorted({c for c, _ in pk})
        print("  %-11s %s/%-6s %3d contacts on chain(s) %s%s"
              % (r, rp, rc, len(pk), ",".join(chs),
                 "  <- spans the interface" if len(chs) > 1 else ""))

    print("resolving ligands")
    for l in ligands:
        if l.get("ccd"):
            l["smiles"], nm = ccd_smiles(l["ccd"])
            print("  %-22s %-7s %s" % (l["name"], l["ccd"], nm[:40]))
        else:
            print("  %-22s %-7s (given as SMILES)" % (l["name"], "-"))
    # Which rungs the affinity head can represent at all. Boltz-2's affinity module pools only
    # protein-to-binder and binder-to-binder pairs and its own paper states it "does not explicitly
    # handle such cofactors, including ions". So supplying the zincs fixes the POSE and not the
    # SCORE, and a ligand that binds by chelating those metals cannot be scored for the thing that
    # makes it bind. Three rungs survive that; three do not, and those three are relabelled
    # diagnostics rather than being allowed to fail the gate on the model's behalf.
    rep = [l["name"] for l in ligands if l.get("representable") is True]
    diag = [l["name"] for l in ligands if l.get("representable") is False]
    print("\n  affinity head CAN represent the binding mode of: %s" % ", ".join(rep))
    print("  CANNOT (metal chelators, expected to fail by construction): %s" % ", ".join(diag))
    if len(rep) < 2:
        sys.exit("fewer than two representable rungs; the gate would rest on a single compound")

    # The null: the same matched decoys, run against each gate receptor, so "above the 95th
    # percentile of the null" has a per-receptor meaning. This is the part the amendment's "about
    # 15 jobs" estimate left out, and it is most of the gate's cost.
    decoys = []
    if a.decoys:
        if not os.path.exists(a.selection):
            sys.exit("--decoys needs --selection (a table from libgen.py --select): " + a.selection)
        pool = [r for r in csv.DictReader(open(a.selection), delimiter="\t")
                if r.get("arm") == "decoy"]
        if len(pool) < a.decoys:
            sys.exit("selection has %d decoys, asked for %d" % (len(pool), a.decoys))
        decoys = random.Random(29).sample(pool, a.decoys)

    n_gate = len(ligands)
    n_null = len(decoys) * len(receptors_used)
    total = n_gate + n_null
    res_by_job = {r: sum(len(s) for _, s in chains[r]) for r in receptors_used}
    mean_res = sum(res_by_job[l["receptor"]] for l in ligands) / max(1, n_gate)
    print("\ngate compounds %d | null %d decoys x %d receptors = %d | total %d jobs"
          % (n_gate, len(decoys), len(receptors_used), n_null, total))
    # Cost scales worse than linearly with sequence length, so this is a floor, not a forecast.
    print("mean receptor size %d residues; the repo's 30-60 s/job figure was measured on a "
          "569-residue single chain" % mean_res)
    print("at 45 s/job that is %.1f GPU-hours; at 90 s/job, %.1f" % (total * 45 / 3600, total * 90 / 3600))

    if a.plan:
        print("\n--plan only, nothing written")
        return

    os.makedirs(a.out_dir, exist_ok=True)
    manifest = {"receptors": {}, "jobs": {}, "policy": {
        "metals": "one catalytic Zn per MBL-beta-CASP nuclease chain; nsp10-nsp14 as deposited "
                  "(2 Zn + 1 Mg); crystallisation additives and idiosyncratic second ions excluded",
        "receptor_sequences": "crystallised construct from the polymer entity of the ligand-bearing "
                             "PDB entry, not full-length UniProt",
        "excluded_compounds": sorted(EXCLUDED),
    }}
    for r in receptors_used:
        manifest["receptors"][r] = {k: v for k, v in RECEPTORS[r].items() if k != "entities"}
        manifest["receptors"][r]["chains"] = {c: len(s) for c, s in chains[r]}

    written = 0

    def msa_for(r):
        # One MSA per chain, named by receptor and chain. fetch_msa.py must produce these before a
        # run; without them every job calls the MSA server and compute nodes have no internet.
        return {c: "%s/%s_%s.a3m" % (msa_prefix, r, c) for c, _ in chains[r]}

    def emit(name, r, smiles, pocket, meta):
        nonlocal written
        p = os.path.join(a.out_dir, name + ".yaml")
        if os.path.exists(p) and not a.force:
            sys.exit("refusing to overwrite %s (use --force)" % p)
        with open(p, "w", newline="\n") as f:
            f.write(job_yaml(chains[r], RECEPTORS[r]["metals"], smiles, msa_for(r), pocket))
        manifest["jobs"][name] = dict(meta, receptor=r, residues=res_by_job[r],
                                      pocket_contacts=len(pocket or []))
        written += 1

    for l in ligands:
        # A ligand with its own co-crystal is constrained to its own site; everything else on that
        # receptor uses the receptor's reference pocket. Decoys get the reference pocket too, so
        # the null answers "what does an unrelated compound score when forced into this same
        # pocket", which is the comparison the pass criteria assume.
        if l.get("ccd") and l.get("pdb"):
            pk = pockets_for(l["receptor"], l["pdb"], l["ccd"])
        elif l.get("ccd"):
            pk = pockets_for(l["receptor"], RECEPTORS[l["receptor"]]["pdb"], l["ccd"])
        else:
            pk = ref_pocket[l["receptor"]]
        emit("gate_%s_%s" % (l["tier"], l["name"]), l["receptor"], l["smiles"], pk,
             {"tier": l["tier"], "expect": l["expect"], "why": l["why"],
              "ccd": l.get("ccd"), "arm": "gate",
              "representable": l.get("representable")})
    for r in receptors_used:
        for d in decoys:
            emit("gnull_%s_%s" % (r, d["source_id"]), r, d["smiles"], ref_pocket[r],
                 {"tier": "null", "arm": "gate_null", "inchikey": d["inchikey"]})

    with open(os.path.join(a.out_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    print("\nwrote %d jobs to %s" % (written, a.out_dir))
    print("MSAs required (fetch_msa.py, one per receptor chain):")
    for r in receptors_used:
        for c, s in chains[r]:
            print("   %s_%s.a3m   (%d aa)" % (r, c, len(s)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--msa-prefix", default="/workspace/gate/msa")
    ap.add_argument("--out-dir", default=os.path.join(HERE, "gate_jobs"))
    ap.add_argument("--decoys", type=int, default=0,
                    help="decoys per receptor, drawn from the committed selection table")
    ap.add_argument("--selection", default=os.path.join(HERE, "selection_v1.tsv"))
    ap.add_argument("--with-integrator", action="store_true",
                    help="also build the 2,283-residue Integrator/IP6 rung")
    ap.add_argument("--plan", action="store_true", help="resolve and cost it, write nothing")
    ap.add_argument("--force", action="store_true")
    main(ap.parse_args())
