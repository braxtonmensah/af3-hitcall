"""Stream one inner zip of the Todor Zenodo archive and write compact per-pool features.

Usage: python extract_structs.py <inner zip name> [max_pools]
Output: structs/<pool>.json with, per chain pair and sample: ipTM (from summary), ipSAE, LIS,
contact-prob max/sum (trunk, sample 0), and interface residue sets (CB 8 A) for reproducibility.
Nothing but these features is stored.
"""
import json
import os
import re
import sys
import time
import zlib
from collections import defaultdict

import numpy as np
import orjson
import pandas as pd
import requests

from streamzip import members

ROOT = r"C:\Users\bmens\NQ_local\af3-hitcall"
OUT = os.path.join(ROOT, "structs")
URL = "https://zenodo.org/records/15499631/files/AF3_completed_zips.zip?download=1"
os.makedirs(OUT, exist_ok=True)
SEQ2LOC = {s.rstrip("*"): l for l, s in pd.read_csv(os.path.join(ROOT, "data", "proteins.csv"))[["locus_tag", "aa_sequence"]].values}


class Inflate:
    """file-like: HTTP range stream of one outer-zip member, inflated on the fly, with retries"""

    def __init__(self, start, size):
        self.start, self.size, self.pos = start, size, 0
        self.d = zlib.decompressobj(-15)
        self.buf = b""
        self._open()

    def _open(self):
        r = requests.get(URL, headers={"Range": f"bytes={self.start + self.pos}-{self.start + self.size - 1}"}, stream=True, timeout=120)
        r.raise_for_status()
        self.it = r.iter_content(1 << 20)

    def read(self, k):
        while len(self.buf) < k and not self.d.eof:
            try:
                c = next(self.it)
            except StopIteration:
                break
            except Exception:
                time.sleep(5)
                self._open()  # resume at the byte we reached
                continue
            self.pos += len(c)
            self.buf += self.d.decompress(c)
        b, self.buf = self.buf[:k], self.buf[k:]
        return b


def arr2d(text, key, n):
    i = text.index(f'"{key}"')
    a = text.index("[[", i)
    b = text.index("]]", a) + 2
    return np.array(orjson.loads(text[a:b]), dtype=np.float32).reshape(n, n)


def arr1d(text, key):
    i = text.index(f'"{key}"')
    a = text.index("[", i)
    b = text.index("]", a)
    return json.loads(text[a:b + 1])


def d0(L):
    L = np.maximum(L, 27.0)
    return 1.24 * np.cbrt(L - 15) - 1.8


def pae_feats(pae, chains):
    """ipSAE (Dunbrack 2025, d0 per residue, PAE cutoff 10) and LIS (Kim 2024, PAE <= 12) per ordered chain pair"""
    ids = sorted(set(chains))
    idx = {c: np.where(np.array(chains) == c)[0] for c in ids}
    out = {}
    for a in ids:
        for b in ids:
            if a >= b:
                continue
            res = {}
            for x, y in ((a, b), (b, a)):
                P = pae[np.ix_(idx[x], idx[y])]
                valid = P < 10
                nv = valid.sum(1)
                dd = d0(nv.astype(float))[:, None]
                tm = 1 / (1 + (P / dd) ** 2)
                per = np.where(nv > 0, (tm * valid).sum(1) / np.maximum(nv, 1), 0)
                res[x + y] = float(per.max())
                lis = P <= 12
                res["lis" + x + y] = float(((12 - P) / 12)[lis].mean()) if lis.any() else 0.0
            out[a + b] = {"ipsae": max(res[a + b], res[b + a]), "lis": (res["lis" + a + b] + res["lis" + b + a]) / 2}
    return out


def cif_iface(text):
    """interface residue sets per chain pair: residues with CB (CA for Gly) within 8 A of the other chain"""
    xyz, ch, rs = [], [], []
    for line in text.splitlines():
        if not line.startswith("ATOM"):
            continue
        f = line.split()
        # AF3 mmCIF atom_site: group id type_symbol label_atom_id label_alt_id label_comp_id label_asym_id label_entity_id label_seq_id ...
        atom, comp, asym, seq = f[3], f[5], f[6], f[8]
        if atom == "CB" or (atom == "CA" and comp == "GLY"):
            xyz.append((float(f[10]), float(f[11]), float(f[12])))
            ch.append(asym)
            rs.append(int(seq))
    xyz = np.array(xyz)
    ch = np.array(ch)
    rs = np.array(rs)
    out = {}
    ids = sorted(set(ch))
    for a in ids:
        A = ch == a
        for b in ids:
            if a >= b:
                continue
            B = ch == b
            D = np.sqrt(((xyz[A][:, None, :] - xyz[B][None, :, :]) ** 2).sum(-1))
            close = D < 8
            ia, ib = np.where(close.any(1))[0], np.where(close.any(0))[0]
            if len(ia):
                out[a + b] = [rs[A][ia].tolist(), rs[B][ib].tolist()]
    return out


def main(inner, max_pools=10 ** 9):
    lst = [l.split("\t") for l in open(os.path.join(ROOT, "AF3_completed_zips.zip.list")).read().splitlines()]
    row = next(r for r in lst if r[4] == f"AF3_completed_zips/{inner}")
    off, csize = int(row[3]), int(row[1])
    # local header of the outer member: 30 + name + extra
    h = requests.get(URL, headers={"Range": f"bytes={off}-{off + 29}"}, timeout=60).content
    nl, el = int.from_bytes(h[26:28], "little"), int.from_bytes(h[28:30], "little")
    f = Inflate(off + 30 + nl + el, csize)
    cur, feats, npools = None, None, 0

    def flush():
        nonlocal npools
        if cur and feats.get("loci") and len(feats["samples"]) == 5:
            json.dump(feats, open(os.path.join(OUT, cur + ".json"), "w"))
            npools += 1
            print(inner, "pool", cur, "done", npools, flush=True)
        if feats:
            feats["loci"] = None

    want = lambda n: bool(re.search(r"(job_request\.json|model_\d\.cif|summary_confidences_\d\.json|full_data_\d\.json)$", n))
    for name, b in members(f, want):
        pool = name.split("/")[0]
        if "/" not in name:
            continue
        if pool != cur:
            flush()
            if npools >= max_pools:
                break
            cur = pool
            feats = {"pool": pool, "samples": {}, "skip": os.path.exists(os.path.join(OUT, pool + ".json")) or "allbyall" not in pool}
        if b is None or feats["skip"]:
            continue
        t = b.decode()
        if name.endswith("job_request.json"):
            j = json.loads(t)
            j = j[0] if isinstance(j, list) else j
            seqs = [s["proteinChain"]["sequence"] for s in j["sequences"]]
            feats["loci"] = [SEQ2LOC.get(s) for s in seqs]
            continue
        k = re.search(r"_(\d)\.(cif|json)$", name).group(1)
        S = feats["samples"].setdefault(k, {})
        if "summary_confidences" in name:
            S["iptm"] = json.loads(t)["chain_pair_iptm"]
        elif name.endswith(".cif"):
            S["iface"] = cif_iface(t)
        elif "full_data" in name:
            chains = arr1d(t, "token_chain_ids")
            n = len(chains)
            pae = arr2d(t, "pae", n)
            S["pae"] = pae_feats(pae, chains)
            if k == "0":
                cp = arr2d(t, "contact_probs", n)
                ids = sorted(set(chains))
                ix = {c: np.where(np.array(chains) == c)[0] for c in ids}
                feats["cp"] = {a + b: [float(cp[np.ix_(ix[a], ix[b])].max()), float(cp[np.ix_(ix[a], ix[b])].sum())]
                               for a in ids for b in ids if a < b}
        del t, b
    flush()
    print(inner, "FINISHED pools", npools, flush=True)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 9)
