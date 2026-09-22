"""Score the V. cholerae pilot exactly as PREREG_VIBRIO.md fixes it. Written before any results.

Usage: python analyze.py <dir with AF Server downloads (fold_*.zip or unzipped folders)>
Reads *summary_confidences_[0-4].json per job; chain order = order in the submitted job.
"""
import glob
import io
import json
import os
import re
import sys
import zipfile
from collections import defaultdict

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
P = pd.read_csv(os.path.join(HERE, "jobs", "proteins.csv"))
pools = pd.read_csv(os.path.join(HERE, "jobs", "pools.csv"))
idx = {l: k for k, l in enumerate(P.locus)}
name = dict(zip(P.locus, P.name))
L = P.length.to_numpy()
n = len(P)
PRECEDENTED = {"PilP-PilQ", "PilB-PilC", "PilT-PilC"}  # PREREG_VIBRIO Amendment 1 (strict rule)
POS = [("PilT", "PilU"), ("CBP", "ChiS"), ("DprA", "ComM"), ("PilM", "PilN"), ("PilN", "PilO"),
       ("PilO", "PilP"), ("PilP", "PilQ"), ("PilB", "PilC"), ("PilT", "PilC")]


def summaries(root):
    """yield (job_name, sample_k, dict) from zips or folders"""
    for z in glob.glob(os.path.join(root, "**", "*.zip"), recursive=True):
        with zipfile.ZipFile(z) as f:
            for m in f.namelist():
                s = re.search(r"fold_(.+)_summary_confidences_(\d)\.json$", m)
                if s:
                    yield s.group(1), int(s.group(2)), json.load(io.TextIOWrapper(f.open(m)))
    for p in glob.glob(os.path.join(root, "**", "*summary_confidences_*.json"), recursive=True):
        s = re.search(r"fold_(.+)_summary_confidences_(\d)\.json$", os.path.basename(p))
        if s:
            yield s.group(1), int(s.group(2)), json.load(open(p))


def main(root):
    members = {r.job: [idx[l] for l in r.loci.split("::::")] for r in pools.itertuples()}
    obs = defaultdict(list)
    seen = set()
    for job, k, js in summaries(root):
        job = job.lower()
        if (job, k) in seen or job not in members:
            continue
        seen.add((job, k))
        M = np.array(js["chain_pair_iptm"], float)
        mem = members[job]
        for a in range(len(mem)):
            for b in range(a + 1, len(mem)):
                i, j = sorted((mem[a], mem[b]))
                obs[(i, j)].append(M[a, b])
    jobs_done = len({j for j, _ in seen})
    print(f"jobs with results: {jobs_done}/{len(members)}")
    S = np.full((n, n), np.nan)
    for (i, j), v in obs.items():
        S[i, j] = S[j, i] = np.mean(v) - (-0.036255571 + 0.004470512 * np.sqrt(L[i] + L[j]))
    dec = (P.kind == "decoy").to_numpy()
    iu = np.triu_indices(n, 1)
    null = S[iu][dec[iu[0]] & dec[iu[1]]]
    null = np.sort(null[np.isfinite(null)])
    thr = np.quantile(null, 0.99)
    byname = {v: idx[k] for k, v in name.items()}
    rows = []
    for a, b in POS:
        i, j = byname[a], byname[b]
        s = S[i, j]
        p = 1 - np.searchsorted(null, s, side="left") / len(null)

        def rank(x, y):
            v = S[x].copy()
            v[x] = -np.inf
            return int((v > S[x, y]).sum() + 1)

        rows.append(dict(pair=f"{a}-{b}", cls="precedented" if f"{a}-{b}" in PRECEDENTED else "never-solved", S=s, p=p, hit=p < 0.01, rank_a=rank(i, j), rank_b=rank(j, i),
                         mean_rank=(rank(i, j) + rank(j, i)) / 2))
    R = pd.DataFrame(rows)
    sysm = (P.kind == "system").to_numpy()
    sd = S[iu][(sysm[iu[0]] & dec[iu[1]]) | (dec[iu[0]] & sysm[iu[1]])]
    print(R.to_string(index=False))
    for c, g in R.groupby("cls"):
        print(f"{c}: hits {int(g.hit.sum())}/{len(g)}, median bait rank {g.mean_rank.median()}")
    print(f"decoy-decoy null n={len(null)}, 99th pct S={thr:.3f}; system-decoy pairs over threshold: "
          f"{(sd > thr).sum()}/{np.isfinite(sd).sum()}")
    R.to_csv(os.path.join(HERE, "pilot_results.csv"), index=False)


if __name__ == "__main__":
    main(sys.argv[1])
