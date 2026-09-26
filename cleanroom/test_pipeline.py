"""End-to-end test of the screen pipeline, at a scale that runs in seconds and needs no GPU.

Every stage has its own self-test. Nothing checked that they compose, and composition is where this
pipeline has actually broken: a scorer whose filenames did not match the builder's, a builder whose
pocket indices did not match the sequence after a tag was stripped, a preflight whose checks passed
on input they should have rejected. Those are all interface defects between two stages that were each
fine alone.

So this walks the real chain with the real modules:

    library_master.tsv -> libgen --select -> build_mpn621 -> validate_jobs -> check_msa_paths
                       -> synthetic Boltz output -> score_mpn621

and asserts at each boundary that the next stage can actually read what the previous one wrote. It
uses a tiny selection and a fake MSA so it costs nothing and can run on any machine.

Usage:
    py -3.11 test_pipeline.py
"""
import csv
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
N = 12                     # compounds per arm; small enough to be instant


def run(args, cwd=HERE, expect=0, env=None):
    e = dict(os.environ, **(env or {}))
    p = subprocess.run([PY] + args if args[0].endswith(".py") else args,
                       cwd=cwd, capture_output=True, text=True, env=e)
    if expect is not None and p.returncode != expect:
        print("--- command failed: %s" % " ".join(args))
        print(p.stdout[-3000:])
        print(p.stderr[-3000:])
        raise SystemExit("stage failed with %d, expected %d" % (p.returncode, expect))
    return p


def main():
    checks, failed = [], []

    def ok(name, cond, detail=""):
        checks.append(name)
        if not cond:
            failed.append("%s %s" % (name, detail))
        print("  %-52s %s %s" % (name, "ok" if cond else "FAIL", detail if not cond else ""))

    tmp = tempfile.mkdtemp(prefix="pipetest_")
    try:
        sel = os.path.join(tmp, "sel.tsv")
        jobs = os.path.join(tmp, "jobs")
        out = os.path.join(tmp, "out")
        msa = os.path.join(tmp, "msa")
        os.makedirs(msa, exist_ok=True)

        print("1. selection")
        run(["libgen.py", "--select", str(N), "--decoys", str(N), "--stratify", "--out", sel])
        rows = list(csv.DictReader(open(sel), delimiter="\t"))
        ok("selection has both arms", {"screen", "decoy"} <= {r["arm"] for r in rows})
        ok("selection is stratified", "stratum" in rows[0] and
           len({r["stratum"] for r in rows}) == 2)
        keys = {}
        for r in rows:
            keys.setdefault(r["inchikey"], set()).add(r["arm"])
        ok("no molecule in two arms", not any(len(v) > 1 for v in keys.values()))

        print("\n2. job build")
        # A fake MSA per receptor, so the preflight has something real to resolve.
        for acc in ("P75174", "P75497", "Q9UKF6"):
            with open(os.path.join(msa, acc + ".a3m"), "w", newline="\n") as f:
                f.write(">query\nAAAA\n")
        run(["build_mpn621.py", "--selection", sel, "--msa-prefix", "/fake/msa",
             "--arms", "S,N", "--out-dir", jobs])
        yamls = [f for f in os.listdir(jobs) if f.endswith(".yaml")]
        ok("wrote 2N job files", len(yamls) == 2 * N, "got %d" % len(yamls))
        man = json.load(open(os.path.join(jobs, "manifest.json")))
        ok("manifest covers every job", set(man["jobs"]) == {f[:-5] for f in yamls})
        ok("manifest records inchikeys the selection knows",
           {m["inchikey"] for m in man["jobs"].values()} <= set(keys))

        # The interface that broke before: pocket indices must be inside the sequence in the job.
        bad = []
        for f in yamls:
            txt = open(os.path.join(jobs, f)).read()
            seq = txt.split("sequence: ")[1].split("\n")[0].strip()
            import re
            for _, idx in re.findall(r"\[(\w+), (\d+)\]", txt):
                if not (1 <= int(idx) <= len(seq)):
                    bad.append((f, idx, len(seq)))
        ok("every pocket index is inside its sequence", not bad, str(bad[:3]))

        print("\n3. validator")
        p = run(["validate_jobs.py"], expect=None, env={"YAML_DIR": jobs})
        ok("validator sees the arms", "decoy" in p.stdout and "screen" in p.stdout)
        ok("validator finds no cross-arm duplicates", "FATAL: " not in p.stdout
           or "different MSA directories" in p.stdout, p.stdout[-200:])

        print("\n4. preflight")
        p = run(["check_msa_paths.py", jobs, "--msa-dir", msa], expect=3)
        ok("MSA check reports relinkable (exit 3)", True)
        p = run(["check_msa_paths.py", jobs, "--msa-dir", tmp], expect=4)
        ok("MSA check is FATAL when files are absent (exit 4)", True)
        # CRLF must be caught
        crdir = os.path.join(tmp, "crjobs")
        os.makedirs(crdir, exist_ok=True)
        src = os.path.join(jobs, yamls[0])
        with open(os.path.join(crdir, "x.yaml"), "wb") as f:
            f.write(open(src, "rb").read().replace(b"\n", b"\r\n"))
        run(["check_msa_paths.py", crdir, "--msa-dir", msa], expect=5)
        ok("MSA check is FATAL on CRLF (exit 5)", True)

        print("\n5. scoring, on synthetic output in both Boltz layouts")
        rng = random.Random(5)
        names = sorted(man["jobs"])
        for i, name in enumerate(names):
            meta = man["jobs"][name]
            v = rng.uniform(0.5, 1.0) if meta["arm"] == "S" else rng.uniform(0.0, 0.5)
            if i % 2:                                   # <name>/affinity.json
                d = os.path.join(out, name)
                os.makedirs(d, exist_ok=True)
                target = os.path.join(d, "affinity.json")
            else:                                       # affinity_<name>.json
                os.makedirs(out, exist_ok=True)
                target = os.path.join(out, "affinity_%s.json" % name)
            json.dump({"affinity_probability_binary": v, "affinity_pred_value": -1.0},
                      open(target, "w"))
        rj = os.path.join(tmp, "res.json")
        p = run(["score_mpn621.py", "--jobs", jobs, "--out-dir", out, "--selection", sel,
                 "--json", rj])
        res = json.load(open(rj))
        ok("scorer read every job in both layouts",
           res["n"].get("S", 0) == N and res["n"].get("N", 0) == N,
           "S=%s N=%s" % (res["n"].get("S"), res["n"].get("N")))
        ok("M1 detects the planted enrichment", res["tests"]["M1"]["verdict"].startswith("enriched"),
           res["tests"]["M1"]["verdict"])
        ok("per-stratum M1 present", bool(res["tests"].get("M1_by_stratum")))
        ok("kill switch reports not-run rather than passing",
           "status" in res["tests"]["kill_switch"])
        ok("arm Z reports not-run rather than passing", "status" in res["tests"]["arm_Z"])
        ok("shortlist carries ids from the selection",
           all(r["id"] for r in res["shortlist"][:3]))
        ok("shortlist rows have no O1 score yet",
           all(r["score_O1"] is None for r in res["shortlist"]))

        print("\n6. the gate scorer's own self-test still passes")
        p = run(["score_gate.py", "--selftest"], expect=None)
        ok("gate self-test passes", "self-test PASSED" in p.stdout)

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n%d checks, %d failed" % (len(checks), len(failed)))
    for f in failed:
        print("  FAILED: " + f)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
