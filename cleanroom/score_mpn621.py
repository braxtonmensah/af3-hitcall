"""Score the PREREG_MPN621 screen. Reads its gate first and reports hypotheses, never hits.

Tests, exactly as pre-registered:

  M1  Mann-Whitney AUC of arm S against the matched null N, with a bootstrap 95% CI. Enriched only
      if the CI excludes 0.50 from above. This is the PRIMARY test, because per-compound significance
      is unreachable at this null size: the floor on an empirical p is 1/(n_null+1), so the top of
      400 compounds would need ~4,000 decoys to clear BH q<0.10. That was established before any
      data existed and it is restated in the output so nobody reads the shortlist as significance.
  M2  Paralogue selectivity. Every shortlisted compound must outscore its OWN score against
      M. pneumoniae RNase J. This is the arm that gates a purchase.
  M3  The same against human CPSF73.
  M4  The shortlist, labelled hypotheses requiring experimental test.
  M5  Whether the score tracks molecular weight or heavy-atom count inside arm S. If it does
      strongly, M1 is downgraded to inconclusive whatever its CI says, because the matched null is
      then carrying the result.

  KILL SWITCH (body of the pre-registration): if Spearman(S, O1) across the whole screen exceeds
  0.90, the method is not distinguishing the two clefts at all, the selectivity premise is
  unsupported BY THIS INSTRUMENT, and M2 cannot justify a purchase however good it looks.

  ARM Z (Amendment 1): if Spearman(S, Z) over the 50 paired compounds is below 0.80, the ranking
  depends on a metal assignment the residue evidence does not settle, and M2/M3 are conditional.

Direction: rank on `affinity_probability_binary`, higher = binder. `affinity_pred_value` is
log10(IC50) in micromolar, so LOWER is stronger; printed for reference only, always labelled.

    python score_mpn621.py --selftest      # run this before trusting a real result

Usage:
    python score_mpn621.py --out-dir mpn621_out [--jobs mpn621_jobs] [--selection selection_v1.tsv]
"""
import argparse
import csv
import glob
import json
import os
import random
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RANK_FIELD = "affinity_probability_binary"
REF_FIELD = "affinity_pred_value"
SHORTLIST_N = 25
KILL_SPEARMAN = 0.90
ARMZ_SPEARMAN = 0.80
BOOT = 4000


# --------------------------------------------------------------------------- statistics

def auc_mw(a, b):
    """P(random a > random b), ties counted as half. Equals the Mann-Whitney U statistic scaled."""
    if not a or not b:
        return float("nan")
    sb = sorted(b)
    import bisect
    tot = 0.0
    for v in a:
        lo = bisect.bisect_left(sb, v)
        hi = bisect.bisect_right(sb, v)
        tot += lo + 0.5 * (hi - lo)
    return tot / (len(a) * len(b))


def auc_ci(a, b, n_boot=BOOT, seed=31):
    rng = random.Random(seed)
    vals = []
    for _ in range(n_boot):
        ra = [a[rng.randrange(len(a))] for _ in range(len(a))]
        rb = [b[rng.randrange(len(b))] for _ in range(len(b))]
        vals.append(auc_mw(ra, rb))
    vals.sort()
    return vals[int(0.025 * n_boot)], vals[int(0.975 * n_boot)]


def _ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def spearman(x, y):
    if len(x) < 3:
        return float("nan")
    rx, ry = _ranks(x), _ranks(y)
    n = len(x)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = sum((a - mx) ** 2 for a in rx) ** 0.5
    dy = sum((b - my) ** 2 for b in ry) ** 0.5
    return num / (dx * dy) if dx and dy else float("nan")


def pearson(x, y):
    n = len(x)
    if n < 3:
        return float("nan")
    mx, my = sum(x) / n, sum(y) / n
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    dx = sum((a - mx) ** 2 for a in x) ** 0.5
    dy = sum((b - my) ** 2 for b in y) ** 0.5
    return num / (dx * dy) if dx and dy else float("nan")


# --------------------------------------------------------------------------- io

def read_scores(out_dir):
    scores = {}
    for pat in ("**/affinity_*.json", "**/affinity.json"):
        for f in glob.glob(os.path.join(out_dir, pat), recursive=True):
            base = os.path.basename(f)
            name = (os.path.basename(os.path.dirname(f)) if base == "affinity.json"
                    else base[len("affinity_"):-len(".json")])
            try:
                d = json.load(open(f))
            except Exception:
                continue
            if RANK_FIELD in d:
                scores[name] = {"rank": float(d[RANK_FIELD]), "ref": d.get(REF_FIELD)}
    return scores


def properties(selection):
    props = {}
    if selection and os.path.exists(selection):
        for r in csv.DictReader(open(selection), delimiter="\t"):
            props[r["inchikey"]] = r
    return props


def score(jobs_dir, out_dir, selection=None, quiet=False):
    mpath = os.path.join(jobs_dir, "manifest.json")
    if not os.path.exists(mpath):
        sys.exit("no manifest at " + mpath)
    jobs = json.load(open(mpath))["jobs"]
    scores = read_scores(out_dir)
    if not (set(jobs) & set(scores)):
        sys.exit("NONE of the %d scored files match a job in the manifest. Scored names look like "
                 "%s; manifest names look like %s. Nothing is evaluated."
                 % (len(scores), sorted(scores)[:3] or ["<none>"], sorted(jobs)[:3]))

    # arm -> {inchikey: score}
    by_arm = {}
    for name, meta in jobs.items():
        if name not in scores:
            continue
        by_arm.setdefault(meta["arm"], {})[meta["inchikey"]] = scores[name]["rank"]
    if not quiet:
        print("manifest %d | scored %d | arms: %s"
              % (len(jobs), len(scores), {k: len(v) for k, v in sorted(by_arm.items())}))

    S, N = by_arm.get("S", {}), by_arm.get("N", {})
    if not S or not N:
        sys.exit("arms S and N are both required; got S=%d N=%d" % (len(S), len(N)))
    res = {"n": {k: len(v) for k, v in by_arm.items()}, "tests": {}}

    # ---- M1, pooled and then per stratum
    props = properties(selection)
    a, b = list(S.values()), list(N.values())
    auc = auc_mw(a, b)
    lo, hi = auc_ci(a, b)
    verdict = "enriched" if lo > 0.5 else ("anti-enriched" if hi < 0.5 else "null")
    res["tests"]["M1"] = {"auc": round(auc, 4), "ci": [round(lo, 4), round(hi, 4)],
                          "verdict": verdict, "n_screen": len(a), "n_null": len(b)}

    # A pooled AUC over two populations is the mistake this project already made once: its headline
    # 0.81 averages a precedented population at 0.85 and a never-solved one at 0.71. The selection is
    # drawn half rule-of-three fragments and half drug-like, so the primary test is reported per
    # stratum as well as pooled, and a pooled figure is never quoted alone.
    strata = {}
    for k in S:
        st = (props.get(k) or {}).get("stratum")
        if st:
            strata.setdefault(st, {"S": [], "N": []})["S"].append(S[k])
    for k in N:
        st = (props.get(k) or {}).get("stratum")
        if st and st in strata:
            strata[st]["N"].append(N[k])
    per = {}
    for st, d in sorted(strata.items()):
        if len(d["S"]) < 20 or len(d["N"]) < 20:
            per[st] = {"n_screen": len(d["S"]), "n_null": len(d["N"]),
                       "note": "too few to read separately"}
            continue
        sa = auc_mw(d["S"], d["N"])
        slo, shi = auc_ci(d["S"], d["N"])
        per[st] = {"auc": round(sa, 4), "ci": [round(slo, 4), round(shi, 4)],
                   "verdict": "enriched" if slo > 0.5 else
                              ("anti-enriched" if shi < 0.5 else "null"),
                   "n_screen": len(d["S"]), "n_null": len(d["N"])}
    res["tests"]["M1_by_stratum"] = per
    if per:
        verdicts = {v.get("verdict") for v in per.values() if "verdict" in v}
        res["tests"]["M1"]["strata_disagree"] = len(verdicts) > 1
        if len(verdicts) > 1:
            res["tests"]["M1"]["verdict"] += " (POOLED; strata disagree, read them separately)"

    # ---- M5, read before M1 is believed
    mw = [(float(props[k]["mw"]), S[k]) for k in S if k in props and props[k].get("mw")]
    hv = [(float(props[k]["heavy"]), S[k]) for k in S if k in props and props[k].get("heavy")]
    res["tests"]["M5"] = {
        "pearson_score_vs_mw": round(pearson([x for x, _ in mw], [y for _, y in mw]), 4) if mw else None,
        "pearson_score_vs_heavy": round(pearson([x for x, _ in hv], [y for _, y in hv]), 4) if hv else None,
        "n": len(mw)}
    size_driven = any(v is not None and abs(v) >= 0.3
                      for v in (res["tests"]["M5"]["pearson_score_vs_mw"],
                                res["tests"]["M5"]["pearson_score_vs_heavy"]))
    res["tests"]["M5"]["size_driven"] = size_driven
    if size_driven and verdict == "enriched":
        res["tests"]["M1"]["verdict"] = "inconclusive (size-driven, M5)"

    # ---- kill switch
    O1, O2 = by_arm.get("O1", {}), by_arm.get("O2", {})
    common = sorted(set(S) & set(O1))
    if common:
        rho = spearman([S[k] for k in common], [O1[k] for k in common])
        res["tests"]["kill_switch"] = {
            "spearman_S_vs_O1": round(rho, 4), "n": len(common),
            "pockets_indistinguishable": bool(rho > KILL_SPEARMAN),
            "threshold": KILL_SPEARMAN}
    else:
        res["tests"]["kill_switch"] = {"status": "arm O1 not run; stage 3 of the pre-registered "
                                                 "staging. M2 cannot be evaluated yet."}

    # ---- arm Z
    Z = by_arm.get("Z", {})
    zc = sorted(set(S) & set(Z))
    if zc:
        rz = spearman([S[k] for k in zc], [Z[k] for k in zc])
        res["tests"]["arm_Z"] = {"spearman_S_vs_Z": round(rz, 4), "n": len(zc),
                                 "metal_dependent": bool(rz < ARMZ_SPEARMAN),
                                 "threshold": ARMZ_SPEARMAN}
    else:
        res["tests"]["arm_Z"] = {"status": "not run; required by Amendment 1 before M2/M3 are "
                                           "reported as unconditional"}

    # ---- M4 shortlist, with M2/M3 per compound
    nulls = sorted(N.values())
    import bisect
    short = sorted(S, key=lambda k: -S[k])[:SHORTLIST_N]
    rows = []
    for k in short:
        pct = bisect.bisect_left(nulls, S[k]) / len(nulls)
        p_emp = (1 + sum(1 for v in nulls if v >= S[k])) / (1 + len(nulls))
        pr = props.get(k, {})
        row = {"inchikey": k, "id": pr.get("source_id"), "source": pr.get("source"),
               "score_S": round(S[k], 4), "pct_vs_null": round(pct, 4),
               "empirical_p": round(p_emp, 4),
               "score_O1": round(O1[k], 4) if k in O1 else None,
               "score_O2": round(O2[k], 4) if k in O2 else None,
               "pains": pr.get("pains"), "mw": pr.get("mw")}
        row["M2_pass"] = None if k not in O1 else bool(S[k] > O1[k])
        row["M3_pass"] = None if k not in O2 else bool(S[k] > O2[k])
        rows.append(row)
    res["shortlist"] = rows

    if not quiet:
        m1 = res["tests"]["M1"]
        print("\nM1  AUC %.4f  CI [%.4f, %.4f]  -> %s   (S=%d vs N=%d)"
              % (m1["auc"], m1["ci"][0], m1["ci"][1], m1["verdict"], m1["n_screen"], m1["n_null"]))
        for st, d in sorted(res["tests"].get("M1_by_stratum", {}).items()):
            if "auc" in d:
                print("    %-9s AUC %.4f  CI [%.4f, %.4f]  -> %-14s (n=%d vs %d)"
                      % (st, d["auc"], d["ci"][0], d["ci"][1], d["verdict"],
                         d["n_screen"], d["n_null"]))
            else:
                print("    %-9s %s (n=%d vs %d)" % (st, d["note"], d["n_screen"], d["n_null"]))
        if res["tests"]["M1"].get("strata_disagree"):
            print("    STRATA DISAGREE. The pooled AUC averages two populations and must not be")
            print("    quoted alone; this is the error this project's own 0.81 headline made.")
        m5 = res["tests"]["M5"]
        print("M5  score vs MW r=%s | vs heavy atoms r=%s | size-driven: %s"
              % (m5["pearson_score_vs_mw"], m5["pearson_score_vs_heavy"], m5["size_driven"]))
        ks = res["tests"]["kill_switch"]
        print("KILL  %s" % (("Spearman(S,O1)=%.4f over %d, pockets indistinguishable: %s"
                            % (ks["spearman_S_vs_O1"], ks["n"], ks["pockets_indistinguishable"]))
                           if "spearman_S_vs_O1" in ks else ks["status"]))
        az = res["tests"]["arm_Z"]
        print("ARM Z %s" % (("Spearman(S,Z)=%.4f over %d, metal-dependent: %s"
                            % (az["spearman_S_vs_Z"], az["n"], az["metal_dependent"]))
                           if "spearman_S_vs_Z" in az else az["status"]))

        print("\nM4 shortlist. THESE ARE HYPOTHESES REQUIRING EXPERIMENTAL TEST, not hits.")
        print("Per-compound significance is unreachable here: the empirical p floor is 1/%d=%.4f, so"
              % (len(nulls) + 1, 1 / (len(nulls) + 1)))
        print("the top of %d compounds would need about %d decoys to clear BH q<0.10."
              % (len(S), int(len(S) / 0.10) - 1))
        print("\n%-4s %-16s %8s %8s %8s %8s %6s %6s"
              % ("#", "id", "score", "pct", "emp.p", "O1", "M2", "PAINS"))
        for i, r in enumerate(rows[:10], 1):
            print("%-4d %-16s %8.4f %8.3f %8.4f %8s %6s %6s"
                  % (i, r["id"] or "?", r["score_S"], r["pct_vs_null"], r["empirical_p"],
                     "%.4f" % r["score_O1"] if r["score_O1"] is not None else "-",
                     "-" if r["M2_pass"] is None else ("ok" if r["M2_pass"] else "FAIL"),
                     r["pains"]))

        print("\nWhat this licenses:")
        if m1["verdict"].startswith("null"):
            print("  M1 null. No enrichment detected at this cleft. NO COMPOUNDS BOUGHT. A real answer.")
        elif m1["verdict"].startswith("inconclusive"):
            print("  M1 downgraded by M5: the score tracks ligand size, so the matched null is")
            print("  carrying the result. Inconclusive regardless of the CI. No purchase.")
        elif "spearman_S_vs_O1" in ks and ks["pockets_indistinguishable"]:
            print("  The two clefts rank the screen near-identically, so this instrument is not")
            print("  distinguishing them. The selectivity premise is unsupported BY THIS METHOD and")
            print("  M2 cannot justify a purchase however good the margins look.")
        elif "spearman_S_vs_O1" not in ks:
            print("  M1 enriched. Arm O1 is the next stage: selectivity is unevaluated, so nothing")
            print("  is bought yet.")
        elif az.get("metal_dependent"):
            print("  Selectivity margins are metal-dependent (arm Z). M2/M3 are conditional on a")
            print("  metal assignment the residue evidence does not settle. No purchase.")
        else:
            print("  M1 enriched, selectivity evaluated. The shortlist is an enriched set with")
            print("  untested individuals. Get an MIC quote before buying anything.")
    return res


# --------------------------------------------------------------------------- self-test

def selftest(jobs_dir, selection):
    mpath = os.path.join(jobs_dir, "manifest.json")
    jobs = json.load(open(mpath))["jobs"]
    print("self-test over %d real job names\n" % len(jobs))
    rng = random.Random(3)
    ok = True

    def run(assign, label, check):
        nonlocal ok
        tmp = tempfile.mkdtemp()
        try:
            for name, meta in jobs.items():
                d = os.path.join(tmp, name)
                os.makedirs(d, exist_ok=True)
                json.dump({RANK_FIELD: assign(name, meta), REF_FIELD: -1.0},
                          open(os.path.join(d, "affinity.json"), "w"))
            r = score(jobs_dir, tmp, selection, quiet=True)
            good, got = check(r)
            print("  %-26s -> %-34s %s" % (label, got, "ok" if good else "WRONG"))
            ok = ok and good
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    run(lambda n, m: rng.uniform(0, 1),
        "S and N from one pool", lambda r: (r["tests"]["M1"]["verdict"] == "null",
                                            "M1 " + r["tests"]["M1"]["verdict"]))
    run(lambda n, m: rng.uniform(0.4, 1.0) if m["arm"] == "S" else rng.uniform(0, 0.6),
        "S shifted above N", lambda r: (r["tests"]["M1"]["verdict"] == "enriched",
                                        "M1 " + r["tests"]["M1"]["verdict"]))
    run(lambda n, m: rng.uniform(0, 0.6) if m["arm"] == "S" else rng.uniform(0.4, 1.0),
        "S shifted below N", lambda r: (r["tests"]["M1"]["verdict"] == "anti-enriched",
                                        "M1 " + r["tests"]["M1"]["verdict"]))

    # M5 must veto an enrichment that is really molecular weight
    props = properties(selection)
    def by_mw(name, meta):
        k = meta["inchikey"]
        w = float(props.get(k, {}).get("mw", 300) or 300)
        v = min(max((w - 150) / 500.0, 0.0), 1.0)
        return v + (0.25 if meta["arm"] == "S" else 0.0)
    run(by_mw, "enrichment driven by MW",
        lambda r: ("size-driven" in r["tests"]["M1"]["verdict"] or r["tests"]["M5"]["size_driven"],
                   "M1 " + r["tests"]["M1"]["verdict"]))

    # Strata must be read separately when they disagree. Fragments enriched, drug-like not: the
    # pooled AUC can look positive while half the library shows nothing, which is the failure mode
    # this project's own 0.81 headline has.
    props_st = properties(selection)
    def split(name, meta):
        st = (props_st.get(meta["inchikey"]) or {}).get("stratum")
        if meta["arm"] == "S" and st == "fragment":
            return rng.uniform(0.55, 1.0)
        if meta["arm"] == "S":
            return rng.uniform(0.0, 0.5)
        return rng.uniform(0.0, 0.5)
    if any((props_st.get(m["inchikey"]) or {}).get("stratum") for m in jobs.values()):
        run(split, "strata disagree",
            lambda r: (bool(r["tests"]["M1"].get("strata_disagree")),
                       "disagree flag %s" % r["tests"]["M1"].get("strata_disagree")))
    else:
        print("  %-26s -> selection has no stratum column; skipped" % "strata disagree")

    tmp = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(tmp, "nope"), exist_ok=True)
        json.dump({RANK_FIELD: 0.9}, open(os.path.join(tmp, "nope", "affinity.json"), "w"))
        try:
            score(jobs_dir, tmp, selection, quiet=True)
            print("  %-26s -> did NOT refuse                    WRONG" % "no name overlap")
            ok = False
        except SystemExit:
            print("  %-26s -> refused to score                  ok" % "no name overlap")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # AUC agrees with scipy's Mann-Whitney, if scipy is present
    try:
        from scipy.stats import mannwhitneyu, spearmanr
        a = [rng.gauss(0.6, 0.2) for _ in range(300)]
        b = [rng.gauss(0.5, 0.2) for _ in range(300)]
        mine = auc_mw(a, b)
        u = mannwhitneyu(a, b, alternative="two-sided").statistic / (len(a) * len(b))
        good = abs(mine - u) < 1e-9
        print("  %-26s -> mine %.6f vs scipy %.6f   %s"
              % ("AUC vs scipy", mine, u, "ok" if good else "WRONG"))
        ok = ok and good
        ms, ss = spearman(a, b), spearmanr(a, b).statistic
        good = abs(ms - ss) < 1e-9
        print("  %-26s -> mine %.6f vs scipy %.6f   %s"
              % ("Spearman vs scipy", ms, ss, "ok" if good else "WRONG"))
        ok = ok and good
    except ImportError:
        print("  scipy not available; AUC and Spearman unverified against a reference")

    print("\nself-test %s" % ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs", default=os.path.join(HERE, "mpn621_jobs"))
    ap.add_argument("--out-dir")
    ap.add_argument("--selection", default=os.path.join(HERE, "selection_v1.tsv"))
    ap.add_argument("--json")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest(a.jobs, a.selection))
    if not a.out_dir:
        ap.error("--out-dir is required unless --selftest")
    r = score(a.jobs, a.out_dir, a.selection)
    if a.json:
        with open(a.json, "w") as f:
            json.dump(r, f, indent=1)
        print("\nwrote", a.json)
