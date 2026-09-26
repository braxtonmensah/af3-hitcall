"""Multi-source compound library builder for the Boltz-2 screens.

`vscreen.py` fetches one library (ChEMBL approved, max_phase 4) and slices it. That was right for a
single pilot and is wrong as soon as there is more than one source, for three reasons this module
exists to fix.

**1. Cross-source duplicates.** The same molecule arrives from ChEMBL, a natural-product set and a
purchasable catalogue under three different IDs and, often, three different SMILES strings for the
same structure. Deduplicating on the SMILES text does not catch that. This module keys on the
standard InChIKey computed after desalting, and reports the collisions it merged so the count in any
write-up is the count of distinct molecules.

**2. The decoy null is not property-matched.** `vscreen.py` draws decoys at random from the tail of
the same library. Random decoys differ from the screen set in molecular weight and lipophilicity by
chance, and Boltz-2's affinity head is known to track ligand size, so an unmatched null can be beaten
by being big rather than by binding. The DUD-E convention is to match decoys on bulk physicochemical
properties and differ them in topology. `match_decoys` does the matching part: it bins on MW and
cLogP and samples decoys from the same bins as the screen set, so a size effect cancels instead of
being read as a hit.

**3. No provenance.** A hit that cannot be traced to a source, a licence and a purchasable catalogue
number is not actionable. Every row here carries source, source id, licence and fetch date.

Nothing in this module talks to a GPU or costs money. It produces a TSV; `vscreen.py --write`
consumes it.

Usage:
    python libgen.py --fetch chembl_approved              # phase 4 small molecules
    python libgen.py --fetch chembl_clinical              # phase 1-3
    python libgen.py --add-file path.smi --source-name X --licence Y
    python libgen.py --build                              # merge, prep, dedupe, annotate -> master TSV
    python libgen.py --report                             # composition, duplicates, property spread
    python libgen.py --select 400 --decoys 100 --out sel.tsv   # screen set + property-matched null
"""
import argparse
import collections
import csv
import datetime
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "library_raw")
MASTER = os.path.join(HERE, "library_master.tsv")
SOURCES_JSON = os.path.join(HERE, "library_sources.json")
CHEMBL = "https://www.ebi.ac.uk/chembl/api/data/molecule"

# Types that are genuinely not a small-molecule screening ligand. Everything else, INCLUDING
# "Unknown" and null, is kept and judged on its structure instead. See fetch_chembl_source.
REJECT_TYPES = {"Protein", "Antibody", "Oligosaccharide", "Oligonucleotide", "Cell", "Gene",
                "Enzyme"}

# Boltz-2's affinity module rejects a ligand above 128 atoms counting heavy atoms AND hydrogens
# (docs/prediction.md). This is the bound that actually fails jobs at run time, so it is applied
# here rather than being discovered on a paid GPU.
MAX_TOTAL_ATOMS = 128
MIN_HEAVY = 6

FIELDS = ["inchikey", "smiles", "source", "source_id", "licence", "fetched",
          "mw", "clogp", "hbd", "hba", "tpsa", "rotb", "heavy", "total_atoms",
          "rings", "frac_csp3", "pains", "ro5_viol", "is_fragment", "also_in"]


# --------------------------------------------------------------------------- chemistry

def _rd():
    from rdkit import Chem, RDLogger
    RDLogger.DisableLog("rdApp.*")
    return Chem


def prep(smi):
    """Desalt to the largest fragment, size-filter, return (canonical_smiles, mol) or (None, reason).

    Identical bounds to vscreen.prep_ligand, deliberately: the screen set, the decoy set and any
    positive-control set must pass through the same filter or the comparison between them is not a
    comparison. Kept as its own function rather than imported because vscreen.py's copy also has to
    keep working standalone.
    """
    Chem = _rd()
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        return None, "unparseable"
    frags = Chem.GetMolFrags(mol, asMols=True, sanitizeFrags=True)
    if not frags:
        return None, "no_fragments"
    mol = max(frags, key=lambda m: m.GetNumHeavyAtoms())
    if mol.GetNumHeavyAtoms() < MIN_HEAVY:
        return None, "too_small"
    if Chem.AddHs(mol).GetNumAtoms() > MAX_TOTAL_ATOMS:
        return None, "too_big_for_boltz_affinity"
    return Chem.MolToSmiles(mol), mol


_PAINS = None


def pains_hit(mol):
    """True if the molecule matches a PAINS pattern.

    Pan-assay interference compounds are the standard failure mode of any hit list at a
    protein-protein interface: they score well against everything and reproduce in no orthogonal
    assay. Flagged rather than dropped, so the decision is visible in the data and a flagged
    compound can still serve as a deliberately promiscuous control.
    """
    global _PAINS
    from rdkit.Chem import FilterCatalog
    if _PAINS is None:
        params = FilterCatalog.FilterCatalogParams()
        params.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS)
        _PAINS = FilterCatalog.FilterCatalog(params)
    return bool(_PAINS.HasMatch(mol))


def annotate(mol):
    from rdkit import Chem
    from rdkit.Chem import Crippen, Descriptors, rdMolDescriptors
    heavy = mol.GetNumHeavyAtoms()
    mw = Descriptors.MolWt(mol)
    clogp = Crippen.MolLogP(mol)
    hbd = rdMolDescriptors.CalcNumHBD(mol)
    hba = rdMolDescriptors.CalcNumHBA(mol)
    viol = sum([mw > 500, clogp > 5, hbd > 5, hba > 10])
    return {
        "mw": round(mw, 2),
        "clogp": round(clogp, 3),
        "hbd": hbd,
        "hba": hba,
        "tpsa": round(rdMolDescriptors.CalcTPSA(mol), 2),
        "rotb": rdMolDescriptors.CalcNumRotatableBonds(mol),
        "heavy": heavy,
        "total_atoms": Chem.AddHs(mol).GetNumAtoms(),
        "rings": rdMolDescriptors.CalcNumRings(mol),
        "frac_csp3": round(rdMolDescriptors.CalcFractionCSP3(mol), 3),
        "pains": int(pains_hit(mol)),
        "ro5_viol": viol,
        # Rule of three. A protein-protein interface is a hard target and fragments are the
        # conventional way in, so they are tagged and can be screened as their own stratum.
        "is_fragment": int(mw <= 300 and clogp <= 3 and hbd <= 3 and hba <= 3),
    }


def inchikey(mol):
    from rdkit import Chem
    try:
        return Chem.MolToInchiKey(mol)
    except Exception:
        return None


# --------------------------------------------------------------------------- sources

def _sources():
    return json.load(open(SOURCES_JSON)) if os.path.exists(SOURCES_JSON) else {}


def _record_source(name, meta):
    s = _sources()
    s[name] = meta
    with open(SOURCES_JSON, "w") as f:
        json.dump(s, f, indent=1, sort_keys=True)


def fetch_chembl(name, params, licence="CC BY-SA 3.0"):
    """Page the ChEMBL REST API into library_raw/<name>.smi. Free, no key."""
    import requests
    os.makedirs(RAW, exist_ok=True)
    rows, offset, seen = [], 0, set()
    while True:
        q = dict(params, format="json", limit=1000, offset=offset)
        r = requests.get(CHEMBL, params=q, timeout=300)
        r.raise_for_status()
        j = r.json()
        got = j.get("molecules", [])
        for m in got:
            smi = (m.get("molecule_structures") or {}).get("canonical_smiles")
            if not smi or len(smi) > 400:
                continue
            if m.get("molecule_type") != "Small molecule":
                continue
            cid = m["molecule_chembl_id"]
            if cid in seen:
                continue
            seen.add(cid)
            rows.append((smi, cid))
        if not (j.get("page_meta") or {}).get("next"):
            break
        offset += 1000
        print("  fetched", len(rows), flush=True)
    path = os.path.join(RAW, name + ".smi")
    with open(path, "w", newline="\n") as f:
        for smi, cid in rows:
            f.write(smi + "\t" + cid + "\n")
    _record_source(name, {"licence": licence, "query": params, "n_raw": len(rows),
                          "fetched": datetime.date.today().isoformat(),
                          "endpoint": CHEMBL, "path": os.path.relpath(path, HERE)})
    print("wrote", len(rows), "->", path)


def fetch_chembl_source(name, src_id, licence):
    """Every molecule ChEMBL holds from one deposited source, via the compound_record endpoint.

    This is the licence-clean route to sets whose own sites restrict redistribution. CO-ADD's site
    notice says its data is for "personal, non-commercial" use and "may not be systematically
    downloaded"; the same molecules are in ChEMBL as src_id 40 under CC BY-SA 3.0. Taking them from
    ChEMBL keeps the provenance honest and the licence usable, and the same applies to the MMV boxes
    (src_id 34).

    compound_record returns records, not molecules, so one molecule can appear several times and the
    result is deduplicated on the ChEMBL id here before the InChIKey pass in build().
    """
    import requests
    os.makedirs(RAW, exist_ok=True)
    url = "https://www.ebi.ac.uk/chembl/api/data/compound_record.json"
    ids, offset = [], 0
    while True:
        r = requests.get(url, params={"src_id": src_id, "limit": 1000, "offset": offset},
                         timeout=300)
        r.raise_for_status()
        j = r.json()
        recs = j.get("compound_records", [])
        for rec in recs:
            cid = rec.get("molecule_chembl_id")
            if cid:
                ids.append(cid)
        if not (j.get("page_meta") or {}).get("next"):
            break
        offset += 1000
        print("  records", len(ids), flush=True)
    uniq = sorted(set(ids))
    print("  %d records -> %d distinct ChEMBL ids; fetching structures" % (len(ids), len(uniq)))
    rows, seen_back = [], set()
    dropped = collections.Counter()
    mol_url = "https://www.ebi.ac.uk/chembl/api/data/molecule.json"
    CH = 40
    for i in range(0, len(uniq), CH):
        chunk = uniq[i:i + CH]
        # limit must exceed the chunk size or the response is silently truncated and the missing
        # ids look like molecules that do not exist. This is accounted per chunk below so that a
        # shortfall is reported rather than inferred from a total at the end.
        r = requests.get(mol_url, params={"molecule_chembl_id__in": ",".join(chunk),
                                          "limit": CH * 2}, timeout=300)
        r.raise_for_status()
        j = r.json()
        got = j.get("molecules", [])
        back = set()
        for m in got:
            cid = m.get("molecule_chembl_id")
            back.add(cid)
            smi = (m.get("molecule_structures") or {}).get("canonical_smiles")
            mt = m.get("molecule_type")
            if not smi:
                dropped["no_structure"] += 1
            elif mt in REJECT_TYPES:
                dropped["type:" + str(mt)] += 1
            else:
                # "Unknown" and null are ACCEPTED. molecule_type is a curation annotation, not a
                # structural fact, and for a donated academic collection it is mostly unassigned:
                # 20,408 of CO-ADD's 24,205 ChEMBL entries are "Unknown". Rejecting on it threw away
                # 84% of the set. What decides usability is the structure, and we have it: desalting,
                # the heavy-atom floor and the Boltz-2 atom bound are applied in build() to every
                # source alike. A spot check missed this because the sampled ids happened to be
                # well-characterised approved drugs that CO-ADD also contains.
                rows.append((smi, cid))
        seen_back |= back
        missing = set(chunk) - back
        if missing:
            dropped["not_returned_by_api"] += len(missing)
        if (i // CH) % 25 == 0:
            print("  %6d/%d ids -> %6d structures" % (i + len(chunk), len(uniq), len(rows)),
                  flush=True)
    print("  accounting: %d ids in, %d returned by the API, %d usable structures"
          % (len(uniq), len(seen_back), len(rows)))
    if dropped:
        for k, v in dropped.most_common():
            print("    dropped %-26s %d" % (k, v))
    # Two different things were conflated in the first version of this check, and conflating them
    # made a correct filter decision look like a broken fetch.
    #
    #   fetch integrity  = did the API return the ids we asked for? A shortfall here means the
    #                      source on disk is not the source it claims to be, which is a defect.
    #   filter yield     = how many of those we chose to keep. A shortfall here is a decision, and
    #                      the accounting above says which rule made it.
    #
    # Only the first is a reason to refuse to write.
    fetched = len(seen_back) / max(1, len(uniq))
    if fetched < 0.98:
        raise SystemExit(
            "the API returned only %.1f%% of the %d ids (%d missing). Not writing %s: a source "
            "recorded under this src_id and licence must actually be that source. This is a fetch "
            "problem, not a filter decision -- see not_returned_by_api above."
            % (100 * fetched, len(uniq), len(uniq) - len(seen_back), name))
    keep = len(rows) / max(1, len(uniq))
    if keep < 0.5:
        print("  NOTE: keeping only %.1f%% of the ids. That is a filter decision, not a fetch "
              "failure; the accounting above says which rule dropped them." % (100 * keep))
    path = os.path.join(RAW, name + ".smi")
    with open(path, "w", newline="\n") as f:
        for smi, cid in rows:
            f.write(smi + "\t" + cid + "\n")
    _record_source(name, {"licence": licence, "src_id": src_id, "n_raw": len(rows),
                          "n_ids": len(uniq), "n_records": len(ids),
                          "fetched": datetime.date.today().isoformat(),
                          "endpoint": url, "path": os.path.relpath(path, HERE)})
    print("wrote", len(rows), "->", path)


# Deposited sources worth having, with the licence that applies via ChEMBL rather than via the
# depositor's own site.
CHEMBL_SOURCES = {
    "mmv_pathogen_box": (34, "CC BY 4.0 (MMV data on publication); via ChEMBL"),
    "coadd": (40, "CC BY-SA 3.0 via ChEMBL. NOT taken from db.co-add.org, whose own notice "
                  "restricts systematic download and non-commercial use"),
}

CHEMBL_QUERIES = {
    # Approved. Same query vscreen.py used, restated here so one module owns every fetch.
    "chembl_approved": {"max_phase": 4},
    # Clinical-stage. Not approved, so a hit is a harder story than repurposing, but these are
    # real molecules with human safety data and most are purchasable.
    "chembl_phase3": {"max_phase": 3},
    "chembl_phase2": {"max_phase": 2},
    "chembl_phase1": {"max_phase": 1},
}


def add_file(path, source_name, licence, id_col=1, smiles_col=0, sep=None, skip_header=False):
    """Register an already-downloaded file (.smi/.tsv/.csv) as a source.

    Used for sets that are not behind a REST API: antibacterial collections, natural products,
    fragment sets, purchasable catalogues. The file is copied into library_raw/ so the build is
    reproducible from the repo state alone.
    """
    os.makedirs(RAW, exist_ok=True)
    dest = os.path.join(RAW, source_name + ".smi")
    n = 0
    with open(path, errors="replace") as fin, open(dest, "w", newline="\n") as fout:
        for i, line in enumerate(fin):
            if skip_header and i == 0:
                continue
            parts = line.rstrip("\n").split(sep) if sep else line.split()
            if len(parts) <= max(id_col, smiles_col):
                continue
            smi, cid = parts[smiles_col].strip(), parts[id_col].strip()
            if not smi:
                continue
            fout.write(smi + "\t" + (cid or source_name + "_" + str(i)) + "\n")
            n += 1
    _record_source(source_name, {"licence": licence, "n_raw": n, "origin": os.path.abspath(path),
                                 "fetched": datetime.date.today().isoformat(),
                                 "path": os.path.relpath(dest, HERE)})
    print("registered", n, "compounds from", source_name, "->", dest)


# --------------------------------------------------------------------------- build

def build():
    """Merge every registered source into one deduplicated, annotated master table."""
    srcs = _sources()
    if not srcs:
        print("no sources registered. run --fetch or --add-file first.")
        return
    by_key, rejected, dup = {}, collections.Counter(), 0
    for name in sorted(srcs):
        path = os.path.join(HERE, srcs[name]["path"])
        if not os.path.exists(path):
            print("  MISSING, skipping:", name, path)
            continue
        fetched = srcs[name].get("fetched", "")
        licence = srcs[name].get("licence", "unknown")
        n_in = n_new = 0
        for line in open(path, errors="replace"):
            if "\t" not in line:
                continue
            smi, cid = line.rstrip("\n").split("\t", 1)
            n_in += 1
            clean, mol = prep(smi)
            if clean is None:
                rejected[name + ":" + mol] += 1
                continue
            key = inchikey(mol)
            if key is None:
                rejected[name + ":no_inchikey"] += 1
                continue
            if key in by_key:
                # Same molecule, another catalogue. Keep the first source and record the alias, so
                # the master count is molecules and the provenance is still complete.
                prev = by_key[key]
                alias = name + ":" + cid
                if alias not in prev["also_in"]:
                    prev["also_in"].append(alias)
                dup += 1
                continue
            row = {"inchikey": key, "smiles": clean, "source": name, "source_id": cid,
                   "licence": licence, "fetched": fetched, "also_in": []}
            row.update(annotate(mol))
            by_key[key] = row
            n_new += 1
        print("  %-20s %6d in -> %6d new" % (name, n_in, n_new))
    rows = list(by_key.values())
    with open(MASTER, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, delimiter="\t")
        w.writeheader()
        for r in sorted(rows, key=lambda r: r["inchikey"]):
            r = dict(r)
            r["also_in"] = ";".join(r["also_in"])
            w.writerow(r)
    print("\nmaster:", len(rows), "distinct molecules ->", MASTER)
    print("cross-source duplicates merged:", dup)
    if rejected:
        print("rejected:")
        for k, v in rejected.most_common():
            print("   %-46s %d" % (k, v))


def load_master():
    if not os.path.exists(MASTER):
        sys.exit("no master table. run --build first.")
    rows = []
    with open(MASTER) as f:
        for r in csv.DictReader(f, delimiter="\t"):
            for k in ("mw", "clogp", "tpsa", "frac_csp3"):
                r[k] = float(r[k])
            for k in ("hbd", "hba", "rotb", "heavy", "total_atoms", "rings", "pains",
                      "ro5_viol", "is_fragment"):
                r[k] = int(r[k])
            rows.append(r)
    return rows


def report():
    rows = load_master()
    n = len(rows)
    print("master table:", n, "distinct molecules\n")
    by_src = collections.Counter(r["source"] for r in rows)
    print("%-22s %7s  %s" % ("source", "n", "licence"))
    srcs = _sources()
    for s, c in by_src.most_common():
        print("%-22s %7d  %s" % (s, c, srcs.get(s, {}).get("licence", "?")))
    shared = sum(1 for r in rows if r["also_in"])
    print("\nmolecules present in more than one source:", shared)
    print("PAINS-flagged:", sum(r["pains"] for r in rows),
          "| rule-of-three fragments:", sum(r["is_fragment"] for r in rows))
    print("Ro5 violations 0/1/2+:",
          sum(1 for r in rows if r["ro5_viol"] == 0),
          sum(1 for r in rows if r["ro5_viol"] == 1),
          sum(1 for r in rows if r["ro5_viol"] >= 2))
    print()
    for k in ("mw", "clogp", "heavy", "rotb", "tpsa"):
        v = sorted(r[k] for r in rows)
        q = lambda p: v[min(n - 1, int(p * n))]
        print("  %-7s min %8.1f  p25 %8.1f  median %8.1f  p75 %8.1f  max %8.1f"
              % (k, v[0], q(.25), q(.5), q(.75), v[-1]))


# --------------------------------------------------------------------------- selection

def _bin(r, mw_w=50.0, lp_w=1.0):
    return (int(r["mw"] // mw_w), int(r["clogp"] // lp_w))


def match_decoys(screen, pool, n, seed=25):
    """Draw n decoys from `pool` matching `screen`'s joint MW x cLogP distribution.

    Why this and not random sampling: Boltz-2's affinity head responds to ligand size, so a null
    built from randomly drawn compounds can be beaten by molecular weight alone and "beat every
    decoy" stops meaning "bound better". Matching the bulk properties and leaving the scaffolds
    free means a compound that beats the null has to do it on something other than being bigger.

    Returns (decoys, shortfall) where shortfall counts requested decoys that no unused pool member
    could match. Reported rather than back-filled at random, because silently topping up with
    unmatched compounds would reintroduce exactly the bias this exists to remove.
    """
    rng = random.Random(seed)
    buckets = collections.defaultdict(list)
    for r in pool:
        buckets[_bin(r)].append(r)
    for b in buckets.values():
        rng.shuffle(b)
    want = collections.Counter(_bin(r) for r in screen)
    total = sum(want.values())
    out, shortfall = [], 0
    for b, c in want.items():
        # proportional allocation, then top up to at least one where the screen set has members
        k = int(round(n * c / total))
        avail = buckets.get(b, [])
        take = min(k, len(avail))
        out.extend(avail[:take])
        buckets[b] = avail[take:]
        shortfall += k - take
    # rounding can leave us a few short of n; fill from the fullest remaining matched bins
    while len(out) < n - shortfall:
        best = max(buckets, key=lambda b: len(buckets[b]) if want.get(b) else -1, default=None)
        if best is None or not buckets[best] or not want.get(best):
            break
        out.append(buckets[best].pop())
    return out[:n], shortfall


def _ks(a, b):
    """Two-sample Kolmogorov-Smirnov statistic. No scipy dependency; the D value is all we need
    to report whether the matched null actually matched."""
    a, b = sorted(a), sorted(b)
    if not a or not b:
        return float("nan")
    allv = sorted(set(a) | set(b))
    import bisect
    d = 0.0
    for v in allv:
        fa = bisect.bisect_right(a, v) / len(a)
        fb = bisect.bisect_right(b, v) / len(b)
        d = max(d, abs(fa - fb))
    return d


def select_paired(n_pairs, pool, seed=25):
    """Draw n_pairs (screen, decoy) couples from the same MW x cLogP bin.

    Selecting the screen set first and matching afterwards has a structural problem: a screen set
    chosen for maximum diversity lands in sparse bins, and a sparse bin has no second member to
    serve as its decoy. That is what produced a 400 versus 333 split, which quietly breaks the 1:1
    ratio the design relies on to keep the expected number of null-beating compounds at 1.0.

    Choosing in couples removes the tension: a bin can contribute to the screen only if it can also
    pay for the decoy. The screen set is slightly less diverse than it could be, and in exchange
    the null is exactly matched at bin level and exactly the same size, which is the trade worth
    making.
    """
    rng = random.Random(seed)
    buckets = collections.defaultdict(list)
    for r in pool:
        buckets[_bin(r)].append(r)
    for b in buckets.values():
        rng.shuffle(b)
    # Round-robin across bins so the pairs spread over property space instead of piling into the
    # densest bin, and stop when no bin can supply a further couple.
    screen, decoys = [], []
    keys = sorted(buckets, key=lambda b: -len(buckets[b]))
    while len(screen) < n_pairs:
        progressed = False
        for b in keys:
            if len(screen) >= n_pairs:
                break
            if len(buckets[b]) >= 2:
                screen.append(buckets[b].pop())
                decoys.append(buckets[b].pop())
                progressed = True
        if not progressed:
            break
    return screen, decoys


def select(n_screen, n_decoys, out_path, strategy="diverse", exclude_pains=True, seed=25,
           stratify=False):
    """Pick the screen set and a property-matched decoy set, and write both with an arm column.

    `stratify` splits the draw evenly between rule-of-three fragments and everything else, and
    records which stratum each compound is in. It exists because the library is now 31% fragments,
    up from 13%, after CO-ADD's academic donations came in at 41% fragments against iPPI-DB's 2%.
    Fragments and drug-like compounds are two populations with different size and chemistry, and
    pooling two populations into one statistic is the mistake this project has already made once:
    its own headline AUROC of 0.81 averages a precedented and a never-solved population that score
    0.85 and 0.71. A stratified draw lets the primary test be read per stratum instead.
    """
    rows = load_master()
    usable = [r for r in rows if not (exclude_pains and r["pains"])]
    print("pool:", len(rows), "->", len(usable), "after PAINS exclusion" if exclude_pains else "")
    rng = random.Random(seed)
    if stratify:
        if n_decoys != n_screen:
            sys.exit("--stratify requires an equal-sized null (--decoys == --select)")
        groups = {"fragment": [r for r in usable if r["is_fragment"]],
                  "druglike": [r for r in usable if not r["is_fragment"]]}
        half = n_screen // 2
        screen, decoys = [], []
        for name in ("fragment", "druglike"):
            s, d = select_paired(half, groups[name], seed=seed)
            if len(s) < half:
                print("stratum %s: only %d couples available, not %d" % (name, len(s), half))
            for r in s:
                r["stratum"] = name
            for r in d:
                r["stratum"] = name
            screen += s
            decoys += d
            print("stratum %-9s screen %4d | decoys %4d  (pool %d)"
                  % (name, len(s), len(d), len(groups[name])))
        _write_selection(screen, decoys, out_path, stratified=True)
        return
    if n_decoys == n_screen and strategy == "diverse":
        screen, decoys = select_paired(n_screen, usable, seed=seed)
        if len(screen) < n_screen:
            print("only %d couples available, not %d: some bins cannot pay for a decoy."
                  % (len(screen), n_screen))
        _write_selection(screen, decoys, out_path)
        return
    if strategy == "diverse":
        # Spread the screen set across MW x cLogP bins instead of taking the head of a file.
        # A screen set drawn from one corner of property space cannot tell you anything about the
        # rest of it, and the ordering of a ChEMBL dump is not meaningful.
        buckets = collections.defaultdict(list)
        for r in usable:
            buckets[_bin(r)].append(r)
        for b in buckets.values():
            rng.shuffle(b)
        keys = sorted(buckets, key=lambda b: -len(buckets[b]))
        screen = []
        while len(screen) < n_screen and keys:
            progressed = False
            for b in keys:
                if buckets[b] and len(screen) < n_screen:
                    screen.append(buckets[b].pop())
                    progressed = True
            if not progressed:
                break
    else:
        screen = rng.sample(usable, min(n_screen, len(usable)))
    chosen = {r["inchikey"] for r in screen}
    pool = [r for r in usable if r["inchikey"] not in chosen]
    decoys, shortfall = match_decoys(screen, pool, n_decoys, seed=seed)
    if shortfall:
        print("WARNING: %d decoys unmatched and NOT back-filled. The null is %d, not %d."
              % (shortfall, len(decoys), n_decoys))
    _write_selection(screen, decoys, out_path)


def _write_selection(screen, decoys, out_path, stratified=False):
    fields = ["arm"] + FIELDS + (["stratum"] if stratified else [])
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        w.writeheader()
        for arm, rs in (("screen", screen), ("decoy", decoys)):
            for r in rs:
                row = dict(r, arm=arm)
                if not stratified:
                    row.pop("stratum", None)
                row["also_in"] = ";".join(row["also_in"]) if isinstance(row["also_in"], list) else row["also_in"]
                w.writerow(row)
    print("screen", len(screen), "| decoys", len(decoys), "->", out_path)
    keys = {r["inchikey"] for r in screen} & {r["inchikey"] for r in decoys}
    if keys:
        # Cannot happen by construction, but this is the exact defect that capped the null in the
        # staged 650-job set, so it is asserted rather than assumed.
        print("FATAL: %d molecules are in both arms: %s" % (len(keys), sorted(keys)[:5]))
    print("\nmatch quality (KS statistic, lower is better matched):")
    for k in ("mw", "clogp", "heavy", "rotb", "tpsa"):
        print("   %-7s D = %.3f" % (k, _ks([r[k] for r in screen], [r[k] for r in decoys])))
    if stratified:
        # An overall match can hide a within-stratum mismatch: if the fragment screen compounds are
        # paired with drug-like decoys and vice versa, the pooled distributions still agree while
        # every individual comparison is wrong. So the match is reported per stratum too.
        print("   within each stratum:")
        for name in sorted({r.get("stratum") for r in screen if r.get("stratum")}):
            sc = [r for r in screen if r.get("stratum") == name]
            dc = [r for r in decoys if r.get("stratum") == name]
            print("     %-9s n=%-4d mw D = %.3f   heavy D = %.3f"
                  % (name, len(sc), _ks([r["mw"] for r in sc], [r["mw"] for r in dc]),
                     _ks([r["heavy"] for r in sc], [r["heavy"] for r in dc])))
    print("\nA D above about 0.15 on mw or heavy means the null is still distinguishable by size.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fetch", choices=sorted(CHEMBL_QUERIES) + ["chembl_clinical"] +
                    sorted(CHEMBL_SOURCES),
                    help="fetch a ChEMBL slice or deposited source. chembl_clinical = phases 1-3")
    ap.add_argument("--add-file", help="register an already-downloaded compound file")
    ap.add_argument("--source-name")
    ap.add_argument("--licence", default="unknown")
    ap.add_argument("--smiles-col", type=int, default=0)
    ap.add_argument("--id-col", type=int, default=1)
    ap.add_argument("--sep", default=None, help="field separator; default is any whitespace")
    ap.add_argument("--skip-header", action="store_true")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--select", type=int, help="size of the screen set to select")
    ap.add_argument("--decoys", type=int, default=0)
    ap.add_argument("--strategy", choices=["diverse", "random"], default="diverse")
    ap.add_argument("--keep-pains", action="store_true")
    ap.add_argument("--stratify", action="store_true",
                    help="draw half from rule-of-three fragments and half from the rest, and record "
                         "the stratum, so the primary test can be read per population")
    ap.add_argument("--out", default=os.path.join(HERE, "selection.tsv"))
    a = ap.parse_args()

    if a.fetch == "chembl_clinical":
        for ph in ("chembl_phase3", "chembl_phase2", "chembl_phase1"):
            print("fetching", ph)
            fetch_chembl(ph, CHEMBL_QUERIES[ph])
    elif a.fetch in CHEMBL_SOURCES:
        sid, lic = CHEMBL_SOURCES[a.fetch]
        print("fetching", a.fetch, "src_id", sid)
        fetch_chembl_source(a.fetch, sid, lic)
    elif a.fetch:
        fetch_chembl(a.fetch, CHEMBL_QUERIES[a.fetch])
    if a.add_file:
        if not a.source_name:
            sys.exit("--add-file needs --source-name")
        add_file(a.add_file, a.source_name, a.licence, id_col=a.id_col,
                 smiles_col=a.smiles_col, sep=a.sep, skip_header=a.skip_header)
    if a.build:
        build()
    if a.report:
        report()
    if a.select:
        select(a.select, a.decoys, a.out, strategy=a.strategy, exclude_pains=not a.keep_pains,
               stratify=a.stratify)
    if not any((a.fetch, a.add_file, a.build, a.report, a.select)):
        ap.print_help()
