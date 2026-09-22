"""Shared precedent helpers (same definition as the pre-registered H1 code)."""
import json
import os
from collections import defaultdict

import numpy as np
import pandas as pd

D = r"C:\Users\bmens\NQ_local\af3-hitcall\data"
LOCI = list(pd.read_csv(os.path.join(D, "proteins.csv")).locus_tag)


def _hits(tag):
    return json.load(open(os.path.join(D, f"pdb_hits{tag}.json")))


def has_homolog(tag=""):
    h = _hits(tag)
    return np.array([bool(h[l]) for l in LOCI])


def precedent_matrix(tag=""):
    hits = _hits(tag)
    by_entry = defaultdict(lambda: defaultdict(set))
    for l, ents in hits.items():
        for e in ents:
            entry, ent = e.split("_")
            by_entry[entry][l].add(ent)
    n = len(LOCI)
    ix = {l: i for i, l in enumerate(LOCI)}
    P = np.zeros((n, n), bool)
    for m in by_entry.values():
        ls = list(m)
        for a in range(len(ls)):
            for b in range(a + 1, len(ls)):
                if len(m[ls[a]] | m[ls[b]]) >= 2:
                    i, j = ix[ls[a]], ix[ls[b]]
                    P[i, j] = P[j, i] = True
    return P
