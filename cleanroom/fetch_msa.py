"""Pre-compute the RNase J MSA once, so the virtual screen can run fully offline.

Why this matters: Boltz's --use_msa_server calls the ColabFold MMseqs2 API over the internet. HPC
compute nodes (Quartz) usually have no outbound internet, and re-querying per ligand would be wasteful
anyway. The protein is identical for all 3,273 ligands, so one MSA serves the whole screen.

Output: cleanroom/msa/P75497.a3m, referenced from each YAML so no network is needed at run time.
"""
import os
import tarfile
import time

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "msa")
API = "https://api.colabfold.com"
ACC = "P75497"  # M. pneumoniae RNase J


def seq(acc):
    t = requests.get("https://rest.uniprot.org/uniprotkb/" + acc + ".fasta", timeout=60).text
    return t.split("\n", 1)[1].replace("\n", "")


def submit(s):
    r = requests.post(API + "/ticket/msa", data={"q": ">query\n" + s, "mode": "env"},
                      timeout=120, headers={"User-Agent": "af3-hitcall/1.0"})
    r.raise_for_status()
    return r.json()


def main():
    os.makedirs(OUT, exist_ok=True)
    dest = os.path.join(OUT, ACC + ".a3m")
    if os.path.exists(dest):
        print("already have", dest)
        return
    s = seq(ACC)
    print("sequence length", len(s))
    t = submit(s)
    tid = t.get("id")
    print("ticket", tid, t.get("status"))
    for i in range(200):
        time.sleep(6)
        st = requests.get(API + "/ticket/" + tid, timeout=60).json().get("status")
        if i % 10 == 0:
            print("  ", i * 6, "s:", st, flush=True)
        if st in ("COMPLETE", "ERROR"):
            print("final:", st)
            break
    else:
        print("timed out waiting for the MSA server")
        return
    if st != "COMPLETE":
        print("MSA server returned", st, "- rerun later")
        return
    tgz = os.path.join(OUT, "result.tar.gz")
    with requests.get(API + "/result/download/" + tid, stream=True, timeout=600) as r:
        r.raise_for_status()
        with open(tgz, "wb") as f:
            for c in r.iter_content(1 << 20):
                f.write(c)
    with tarfile.open(tgz) as tf:
        names = tf.getnames()
        print("archive:", names)
        member = next((n for n in names if n.endswith(".a3m")), None)
        if not member:
            print("no .a3m in archive")
            return
        with tf.extractfile(member) as src, open(dest, "wb") as f:
            f.write(src.read())
    n = sum(1 for l in open(dest) if l.startswith(">"))
    print("wrote", dest, "|", n, "sequences")


if __name__ == "__main__":
    main()
