"""Score the PREREG_VSCREEN gate. Reads the gate first and refuses to guess.

Criteria, exactly as pre-registered (PREREG_VSCREEN Amendments 1-3):

  A1  Each of the two REPRESENTABLE Tier A rungs must outscore at least 57 of its receptor's 60
      matched decoys (empirical p = 3/61 = 0.049). Those two are the JTE-607 acid on CPSF73 and
      ceftriaxone on Artemis. Amendment 3 demoted the other three Tier A compounds to diagnostics
      because they bind by chelating active-site metals and Boltz-2's affinity head pools only
      protein-binder and binder-binder pairs, so it cannot represent that at all.
  A2  The JTE-607 free acid must outscore its own parent ethyl ester. The ester is a prodrug and not
      the binding species; if it wins, the score is rewarding lipophilicity rather than recognition
      and A1 does not count.
  A3  At most one of the three reactive negative controls may reach the Tier A range.
  B2  The nsp10-nsp14 interface fragment must clear the same 57-of-60 bar. Tier B rests on it alone;
      the IP6 rung was declared and not built (2,283 residues).

Direction matters and is easy to invert. `affinity_probability_binary` is HIGHER for a binder and is
what the pre-registration ranks on. `affinity_pred_value` is log10(IC50) in micromolar, so LOWER is
stronger; it is printed for reference and always labelled, never used for ranking.

This scorer is self-testable, because this repository has already shipped a scorer whose filename
regex silently matched nothing and reported a passing gate computed over zero pairs:

    python score_gate.py --selftest

builds synthetic output using the REAL job names from the manifest and checks that the criteria fire
in both directions. Run it before trusting a real result.

Usage:
    python score_gate.py --out-dir gate_out [--jobs gate_jobs]
    python score_gate.py --selftest
"""
import argparse
import glob
import json
import os
import random
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RANK_FIELD = "affinity_probability_binary"   # higher = binder
REF_FIELD = "affinity_pred_value"            # log10 IC50 uM, LOWER = stronger
BAR_BEATS = 57
BAR_OF = 60

REPRESENTABLE = {"jte607_acid": "cpsf73", "ceftriaxone": "artemis"}
DIAGNOSTIC = {"tao1", "tao2", "snm1a_hydroxamate"}
TIER_B = {"nsp14_fragment": "nsp1014"}
NEGATIVES = {"an3661", "ebselen", "disulfiram"}
ESTER = "jte607_parent_ester"


def load_manifest(jobs_dir):
    p = os.path.join(jobs_dir, "manifest.json")
    if not os.path.exists(p):
        sys.exit("no manifest at %s; the scorer will not infer arms from filenames alone" % p)
    return json.load(open(p))


def read_scores(out_dir):
    """Every affinity JSON under out_dir, keyed by job name.

    Boltz writes predictions under nested per-job directories; the job name is recovered from the
    filename rather than from the directory, and BOTH conventions Boltz has used are accepted
    (affinity_<name>.json, and <name>/affinity.json).
    """
    scores = {}
    pats = ["**/affinity_*.json", "**/affinity.json"]
    for pat in pats:
        for f in glob.glob(os.path.join(out_dir, pat), recursive=True):
            base = os.path.basename(f)
            if base == "affinity.json":
                name = os.path.basename(os.path.dirname(f))
            else:
                name = base[len("affinity_"):-len(".json")]
            try:
                d = json.load(open(f))
            except Exception as e:
                print("  unreadable, skipped: %s (%s)" % (f, e))
                continue
            if RANK_FIELD not in d:
                print("  no %s in %s, skipped" % (RANK_FIELD, f))
                continue
            scores[name] = {"rank": float(d[RANK_FIELD]),
                            "ref": d.get(REF_FIELD)}
    return scores


def beats(value, nulls):
    """How many nulls this value strictly exceeds, and the one-sided empirical p."""
    n_beaten = sum(1 for v in nulls if value > v)
    p = (1 + sum(1 for v in nulls if v >= value)) / (1 + len(nulls))
    return n_beaten, p


def score(jobs_dir, out_dir, quiet=False):
    man = load_manifest(jobs_dir)
    jobs = man["jobs"]
    scores = read_scores(out_dir)

    # The check that the old scorer lacked. If the names in the output do not intersect the names in
    # the manifest, every criterion below would be computed over nothing and report a pass.
    known = set(jobs)
    got = set(scores)
    overlap = known & got
    if not overlap:
        sys.exit("NONE of the %d scored files match a job in the manifest. Scored names look like "
                 "%s; manifest names look like %s. Nothing is evaluated."
                 % (len(got), sorted(got)[:3] or ["<none>"], sorted(known)[:3]))
    missing = [j for j in known if j not in got]
    if not quiet:
        print("manifest %d jobs | scored %d | matched %d | missing %d"
              % (len(known), len(got), len(overlap), len(missing)))
        if missing:
            print("  missing (first 6): %s" % missing[:6])

    nulls = {}
    for name, meta in jobs.items():
        if meta.get("arm") == "gate_null" and name in scores:
            nulls.setdefault(meta["receptor"], []).append(scores[name]["rank"])
    if not quiet:
        print("\nnull sizes per receptor: %s" % {k: len(v) for k, v in sorted(nulls.items())})

    gate = {}
    for name, meta in jobs.items():
        if meta.get("arm") != "gate" or name not in scores:
            continue
        # The compound label is the part after the tier token, which the manifest also carries.
        short = name.split("_", 2)[-1]
        gate[short] = {"receptor": meta["receptor"], "tier": meta.get("tier"),
                       "representable": meta.get("representable"),
                       "rank": scores[name]["rank"], "ref": scores[name]["ref"]}

    res = {"criteria": {}, "compounds": {}, "null_sizes": {k: len(v) for k, v in nulls.items()}}
    rows = []
    for short, g in sorted(gate.items()):
        nl = nulls.get(g["receptor"], [])
        if not nl:
            rows.append((short, g, None, None, "NO NULL for %s" % g["receptor"]))
            continue
        nb, p = beats(g["rank"], nl)
        g.update(beats_n=nb, null_n=len(nl), p=p)
        res["compounds"][short] = g
        rows.append((short, g, nb, p, ""))

    if not quiet:
        print("\n%-22s %-9s %-6s %-14s %8s %9s %10s" %
              ("compound", "receptor", "tier", "role", "score", "beats", "emp. p"))
        for short, g, nb, p, note in rows:
            role = ("RUNG" if short in REPRESENTABLE or short in TIER_B else
                    "diagnostic" if short in DIAGNOSTIC else
                    "negative" if short in NEGATIVES or short == ESTER else "")
            print("%-22s %-9s %-6s %-14s %8.4f %5s/%-3s %10s" %
                  (short, g["receptor"], g.get("tier", "?"), role, g["rank"],
                   nb if nb is not None else "-", g.get("null_n", "-"),
                   "%.4f" % p if p is not None else note))

    # ---- A1
    a1_detail = {}
    a1 = True
    for c, recv in REPRESENTABLE.items():
        g = res["compounds"].get(c)
        if not g:
            a1 = False
            a1_detail[c] = "MISSING"
            continue
        ok = g["beats_n"] >= BAR_BEATS and g["null_n"] >= BAR_OF
        a1_detail[c] = {"beats": g["beats_n"], "of": g["null_n"], "pass": ok}
        a1 = a1 and ok
    res["criteria"]["A1"] = {"pass": a1, "bar": "%d of %d" % (BAR_BEATS, BAR_OF), "detail": a1_detail}

    # ---- A2
    acid = res["compounds"].get("jte607_acid")
    est = res["compounds"].get(ESTER)
    if acid and est:
        a2 = acid["rank"] > est["rank"]
        res["criteria"]["A2"] = {"pass": a2, "acid": acid["rank"], "ester": est["rank"]}
    else:
        res["criteria"]["A2"] = {"pass": False, "reason": "acid or ester not scored"}

    # ---- A3: how many reactive negatives reach the representable rungs' range
    rung_vals = [res["compounds"][c]["rank"] for c in REPRESENTABLE if c in res["compounds"]]
    floor = min(rung_vals) if rung_vals else None
    reached = [c for c in NEGATIVES
               if c in res["compounds"] and floor is not None
               and res["compounds"][c]["rank"] >= floor]
    res["criteria"]["A3"] = {"pass": len(reached) <= 1, "reached": reached,
                             "rung_floor": floor}

    # ---- B2
    b2_detail = {}
    b2 = True
    for c, recv in TIER_B.items():
        g = res["compounds"].get(c)
        if not g:
            b2 = False
            b2_detail[c] = "MISSING"
            continue
        ok = g["beats_n"] >= BAR_BEATS and g["null_n"] >= BAR_OF
        b2_detail[c] = {"beats": g["beats_n"], "of": g["null_n"], "pass": ok}
        b2 = b2 and ok
    res["criteria"]["B2"] = {"pass": b2, "detail": b2_detail}

    tier_a = bool(a1 and res["criteria"]["A2"]["pass"] and res["criteria"]["A3"]["pass"])
    res["tier_A_pass"] = tier_a
    res["tier_B_pass"] = bool(b2)

    if not quiet:
        print("\n" + "=" * 74)
        for k in ("A1", "A2", "A3", "B2"):
            c = res["criteria"][k]
            print("  %-3s %-5s %s" % (k, "PASS" if c["pass"] else "FAIL",
                                      json.dumps({x: y for x, y in c.items() if x != "pass"})))
        print("\n  Tier A: %s    Tier B: %s" % ("PASS" if tier_a else "FAIL",
                                                "PASS" if b2 else "FAIL"))
        print("\n  Diagnostics (metal chelators; the affinity head cannot represent their mode,")
        print("  so failure here is a property of the model and does NOT fail the gate):")
        for c in sorted(DIAGNOSTIC):
            g = res["compounds"].get(c)
            if g:
                print("    %-22s beats %d/%d, p=%.4f" % (c, g["beats_n"], g["null_n"], g["p"]))
        print("\n  What this licenses, per PREREG_VSCREEN Amendment 1:")
        if not tier_a:
            print("    Tier A FAILED. Stop. No screen result means anything in either direction,")
            print("    and no compounds are bought.")
        elif not b2:
            print("    Tier A passed, Tier B failed. The method finds active sites, not interfaces.")
            print("    A null at an INTERFACE is uninformative. A conventional-pocket screen")
            print("    (PREREG_MPN621) is still interpretable; an interface screen is not.")
        else:
            print("    Both tiers passed. An interface null would be a publishable negative.")
    return res


# --------------------------------------------------------------------------- self-test

def selftest(jobs_dir):
    """Build synthetic output with the REAL job names and check both directions."""
    man = load_manifest(jobs_dir)
    jobs = man["jobs"]
    print("self-test over %d real job names from %s\n" % (len(jobs), jobs_dir))
    rng = random.Random(7)

    def write(tmp, mapping):
        for name, val in mapping.items():
            d = os.path.join(tmp, name)
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "affinity.json"), "w") as f:
                json.dump({RANK_FIELD: val, REF_FIELD: -1.0}, f)

    def build(passing):
        m = {}
        for name, meta in jobs.items():
            if meta.get("arm") == "gate_null":
                m[name] = rng.uniform(0.0, 0.5)
            else:
                short = name.split("_", 2)[-1]
                if passing and (short in REPRESENTABLE or short in TIER_B):
                    m[name] = 0.99
                elif passing and short == ESTER:
                    m[name] = 0.10
                elif passing:
                    m[name] = 0.20
                else:
                    m[name] = 0.05          # every rung below the null: must FAIL
        return m

    ok = True
    for label, passing, expect in (("all rungs high", True, True),
                                   ("all rungs low", False, False)):
        tmp = tempfile.mkdtemp()
        try:
            write(tmp, build(passing))
            r = score(jobs_dir, tmp, quiet=True)
            got = r["tier_A_pass"]
            flag = "ok" if got == expect else "WRONG"
            if got != expect:
                ok = False
            print("  %-16s -> Tier A %-5s (expected %-5s) %s"
                  % (label, "PASS" if got else "FAIL", "PASS" if expect else "FAIL", flag))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    # A2 must be able to fail on its own: rungs high, but the ester beats the acid.
    tmp = tempfile.mkdtemp()
    try:
        m = build(True)
        for name in jobs:
            if name.endswith("_" + ESTER):
                m[name] = 0.999
        write(tmp, m)
        r = score(jobs_dir, tmp, quiet=True)
        a2 = r["criteria"]["A2"]["pass"]
        print("  %-16s -> A2 %-5s (expected FAIL) %s"
              % ("ester beats acid", "PASS" if a2 else "FAIL", "ok" if not a2 else "WRONG"))
        ok = ok and not a2
        if r["tier_A_pass"]:
            print("    WRONG: Tier A passed despite A2 failing")
            ok = False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # And the failure this repo actually shipped: names that match nothing.
    tmp = tempfile.mkdtemp()
    try:
        write(tmp, {"totally_unrelated_name": 0.9})
        try:
            score(jobs_dir, tmp, quiet=True)
            print("  %-16s -> did NOT refuse. WRONG" % "no name overlap")
            ok = False
        except SystemExit:
            print("  %-16s -> refused to score. ok" % "no name overlap")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\nself-test %s" % ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs", default=os.path.join(HERE, "gate_jobs"))
    ap.add_argument("--out-dir")
    ap.add_argument("--json", help="write the result here")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest(a.jobs))
    if not a.out_dir:
        ap.error("--out-dir is required unless --selftest")
    r = score(a.jobs, a.out_dir)
    if a.json:
        with open(a.json, "w") as f:
            json.dump(r, f, indent=1)
        print("\nwrote", a.json)
