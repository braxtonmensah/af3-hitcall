"""Do the MSA paths named inside a job set resolve on this machine?

Split out of run_screen.sh as a real file rather than an embedded heredoc. The heredoc version had a
quoting bug that made it die with a SyntaxError, and because the shell only looked at its *output*,
an empty report was read as "everything fine" and the preflight printed OK. A check that fails open
is worse than no check. This exits non-zero on trouble so the caller cannot miss it:

    0  every referenced MSA resolves as written
    3  some do not resolve here, but the files exist in --msa-dir (relinkable)
    4  some exist nowhere on this machine (fatal)
    2  usage or read error

With --relink it rewrites the paths in place, keeping each original as <file>.yaml.orig, and only if
nothing is in the "exists nowhere" class. Relinking is deliberately not the default: the jobs carry
pod-side paths on purpose and they are a committed artifact.

Usage:
    python check_msa_paths.py <job-dir> --msa-dir <dir> [--relink] [--quiet]
"""
import argparse
import glob
import os
import re
import sys

MSA_RE = re.compile(r'msa: *"([^"]*)"')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jobs")
    ap.add_argument("--msa-dir", required=True)
    ap.add_argument("--relink", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    files = sorted(glob.glob(os.path.join(a.jobs, "*.yaml")))
    if not files:
        print("no .yaml files in " + a.jobs)
        return 2
    msa_dir = a.msa_dir.rstrip("/\\")

    # Carriage returns, checked here rather than in the shell. A CR inside a quoted msa: path makes a
    # file that exists report as missing, which STATE.md records as having cost a cycle. Doing it in
    # shell needed a literal CR in the source, and three successive attempts to write one through a
    # heredoc were silently mangled into either nothing or a real CR, so the check kept passing on
    # CRLF input. In Python the byte is just b"\r" and there is nothing to escape.
    # Scoped to the .yaml files the engine parses: manifest.json is text-mode output from Windows
    # Python, so it legitimately carries CRLF and recursing over the directory condemned the set.
    crlf = [f for f in files if b"\r" in open(f, "rb").read()]
    if crlf:
        print("FATAL: %d of %d job file(s) contain carriage returns, e.g. %s"
              % (len(crlf), len(files), ", ".join(os.path.basename(x) for x in crlf[:3])))
        print("       A CR inside a quoted msa: path reports a present file as missing.")
        print("       Fix: python -c \"import glob;[open(f,'wb').write(open(f,'rb').read()"
              ".replace(b'\\r\\n',b'\\n')) for f in glob.glob('%s/*.yaml')]\"" % a.jobs)
        return 5

    refs, per_file = {}, {}
    for f in files:
        try:
            txt = open(f, encoding="utf-8", errors="replace").read()
        except OSError as e:
            print("unreadable: %s (%s)" % (f, e))
            return 2
        paths = MSA_RE.findall(txt)
        per_file[f] = (txt, paths)
        for p in paths:
            refs[p] = refs.get(p, 0) + 1

    if not refs:
        print("no msa: paths in %d job files. Every job would call the MSA server, which needs "
              "internet that compute nodes usually lack." % len(files))
        return 3

    absent, relinkable = [], {}
    for p in sorted(refs):
        if os.path.isfile(p):
            continue
        cand = os.path.join(msa_dir, os.path.basename(p))
        if os.path.isfile(cand):
            relinkable[p] = cand
        else:
            absent.append(p)

    if not a.quiet:
        print("%d job files reference %d distinct MSA paths" % (len(files), len(refs)))
        for p in sorted(refs):
            state = ("ok" if os.path.isfile(p) else
                     "relinkable" if p in relinkable else "ABSENT")
            print("  %-10s %-58s %d jobs" % (state, p, refs[p]))

    if absent:
        print("FATAL: %d MSA path(s) exist nowhere on this machine, including not in %s"
              % (len(absent), msa_dir))
        return 4
    if not relinkable:
        return 0
    if not a.relink:
        print("%d path(s) do not resolve as written but are present in %s. Pass --relink to rewrite."
              % (len(relinkable), msa_dir))
        return 3

    n = 0
    for f, (txt, paths) in per_file.items():
        if not any(p in relinkable for p in paths):
            continue
        orig = f + ".orig"
        if not os.path.exists(orig):
            with open(orig, "w", newline="\n", encoding="utf-8") as fh:
                fh.write(txt)
        out = MSA_RE.sub(lambda m: 'msa: "%s"' % relinkable.get(m.group(1), m.group(1)), txt)
        with open(f, "w", newline="\n", encoding="utf-8") as fh:
            fh.write(out)
        n += 1
    print("relinked %d file(s); originals kept as *.yaml.orig" % n)
    # Re-verify rather than assume the rewrite worked.
    still = [p for f in files
             for p in MSA_RE.findall(open(f, encoding="utf-8", errors="replace").read())
             if not os.path.isfile(p)]
    if still:
        print("FATAL: still unresolved after relink: %s" % sorted(set(still))[:5])
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
