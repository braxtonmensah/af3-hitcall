"""Fetch one MSA per gate receptor chain, keyed to the CONSTRUCT sequence.

`fetch_msa.py` fetches by UniProt accession and names the file after it. That is wrong for the gate.
The gate's receptors are the crystallised constructs from the ligand-bearing PDB entries, not the
full-length proteins: CPSF3 is 478 residues here against 684 in UniProt, SNM1A is 343 against 1,040.
An MSA built from the full-length sequence has columns that do not correspond to the sequence in the
job, so it is not merely suboptimal, it is the wrong alignment.

So this asks build_gate.py for the exact sequence it writes into each job, and names each MSA
`<receptor>_<chain>.a3m`, which is what build_gate's `msa_for()` references.

Uses the public ColabFold MMseqs2 API, which is the same service `fetch_msa.py` already uses. One
submission per distinct chain, five in total, and it skips any that already exist.

Usage:
    py -3.11 fetch_msa_gate.py                # all gate receptor chains
    py -3.11 fetch_msa_gate.py cpsf73_A       # just one
"""
import hashlib
import os
import sys
import tarfile
import time

import requests

import build_gate as G

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "msa")
API = "https://api.colabfold.com"
UA = {"User-Agent": "af3-hitcall/1.0 (academic; pre-registered screen)"}


def targets(only=None):
    """(name, sequence) per receptor chain the gate actually uses."""
    out = []
    ligands = [l for l in G.LIGANDS if not l.get("optional")]
    for r in sorted({l["receptor"] for l in ligands}):
        spec = G.RECEPTORS[r]
        for cid, ent in sorted(spec["entities"].items()):
            name = "%s_%s" % (r, cid)
            if only and name != only:
                continue
            out.append((name, G.entity_seq(spec["pdb"], ent)))
    return out


def fetch_one(name, s):
    dest = os.path.join(OUT, name + ".a3m")
    if os.path.exists(dest):
        n = sum(1 for l in open(dest, errors="replace") if l.startswith(">"))
        print("%-12s already present, %d sequences" % (name, n))
        return True
    print("%-12s %d aa, submitting" % (name, len(s)), flush=True)
    r = requests.post(API + "/ticket/msa", data={"q": ">query\n" + s, "mode": "env"},
                      timeout=180, headers=UA)
    r.raise_for_status()
    tid = r.json().get("id")
    st = None
    for i in range(300):
        time.sleep(6)
        try:
            st = requests.get(API + "/ticket/" + tid, timeout=60, headers=UA).json().get("status")
        except Exception as e:
            print("   poll error, retrying:", e)
            continue
        if i % 10 == 0:
            print("   %-10s %4ds %s" % (name, i * 6, st), flush=True)
        if st in ("COMPLETE", "ERROR"):
            break
    if st != "COMPLETE":
        print("%-12s NOT COMPLETE (%s); rerun later" % (name, st))
        return False
    tgz = os.path.join(OUT, "_%s.tar.gz" % name)
    with requests.get(API + "/result/download/" + tid, stream=True, timeout=900, headers=UA) as resp:
        resp.raise_for_status()
        with open(tgz, "wb") as f:
            for c in resp.iter_content(1 << 20):
                f.write(c)
    with tarfile.open(tgz) as tf:
        member = next((n for n in tf.getnames() if n.endswith(".a3m")), None)
        if not member:
            print("%-12s no .a3m in archive: %s" % (name, tf.getnames()))
            return False
        with tf.extractfile(member) as src:
            data = src.read()
    # Write atomically: a half-written a3m would be treated as present on the next run.
    tmp = dest + ".part"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, dest)
    os.remove(tgz)
    # The first record must be the query we sent, or the alignment is for a different protein.
    lines = data.decode("utf-8", "replace").splitlines()
    first = "".join(l for l in lines[1:] if not l.startswith(">")).split(">")[0]
    first = "".join(c for c in first if c.isalpha() and c.isupper())
    ok = first[:60] == s[:60]
    n = sum(1 for l in lines if l.startswith(">"))
    print("%-12s wrote %d sequences | query row matches the construct: %s"
          % (name, n, "yes" if ok else "NO -- do not use this MSA"))
    return ok


def main():
    os.makedirs(OUT, exist_ok=True)
    only = sys.argv[1] if len(sys.argv) > 1 else None
    ts = targets(only)
    if not ts:
        sys.exit("no matching gate chain; known: %s" % [n for n, _ in targets()])
    print("%d MSA(s) to ensure\n" % len(ts))
    ok = 0
    for name, s in ts:
        try:
            ok += bool(fetch_one(name, s))
        except Exception as e:
            print("%-12s FAILED: %s" % (name, e))
    print("\n%d of %d ready in %s" % (ok, len(ts), OUT))
    if ok == len(ts):
        print("the gate can now run offline; validate with:")
        print("  YAML_DIR=gate_jobs py -3.11 validate_jobs.py")


if __name__ == "__main__":
    main()
