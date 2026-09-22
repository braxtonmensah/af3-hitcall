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
                s = re.search(r"fold_(.+)_summary_confidences_(\d)\.json$", os.path.basename(m))  # zips may nest a folder
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
    allsum = list(summaries(root))
    for job, k, js in allsum:
        job = job.lower()
        if (job, k) in seen or job not in members:
            continue
        seen.add((job, k))
        M = np.array(js["chain_pair_iptm"], float)
        mem = members[job]
        if M.shape[0] != len(mem):  # guard: result must match the designed pool
            print(f"SKIP {job} sample {k}: {M.shape[0]} chains, expected {len(mem)}")
            continue
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
    if len(null) == 0:
        sys.exit("no decoy-decoy pairs scored; check the download folder")
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
    tfos(allsum, null, thr)


def tfos(allsum, null, thr):
    """PREREG_VIBRIO Amendment 2: TfoS (VC_2080) vs all 84 pilot proteins, scored against the main
    pilot's decoy-decoy null. Only TfoS-partner pairs are used; partner-partner pairs are ignored."""
    tp = pd.read_csv(os.path.join(HERE, "jobs", "pools_tfos.csv"))
    ltf = len(json.load(open(os.path.join(HERE, "jobs", "afserver_tfos.json")))[0]["sequences"][0]["proteinChain"]["sequence"])
    members = {r.job: r.loci.split("::::") for r in tp.itertuples()}
    obs, seen = defaultdict(list), set()
    for job, k, js in allsum:
        job = job.lower()
        if (job, k) in seen or job not in members:
            continue
        seen.add((job, k))
        M = np.array(js["chain_pair_iptm"], float)
        mem = members[job]
        if M.shape[0] != len(mem):
            print(f"SKIP {job} sample {k}: {M.shape[0]} chains, expected {len(mem)}")
            continue
        assert mem[0] == "VC_2080"
        for b in range(1, len(mem)):
            obs[mem[b]].append(M[0, b])
    print(f"TfoS jobs with results: {len({j for j, _ in seen})}/{len(members)}; partners scored {len(obs)}/{len(P)}")
    if not obs:
        return
    St = {loc: np.mean(v) - (-0.036255571 + 0.004470512 * np.sqrt(ltf + L[idx[loc]])) for loc, v in obs.items()}
    chis = next(l for l, nm in name.items() if nm == "ChiS")
    if chis not in St:
        print("ChiS-TfoS not yet scored")
        return
    s = St[chis]
    p = 1 - np.searchsorted(null, s, side="left") / len(null)
    rank = int(sum(v > s for v in St.values()) + 1)
    top = sorted(St.items(), key=lambda kv: -kv[1])[:5]
    out = dict(pair="ChiS-TfoS", cls="never-solved", S=float(s), p=float(p), hit=bool(p < 0.01),
               chis_rank_among_tfos_partners=rank, n_partners=len(St), null_99th=float(thr),
               tfos_top5=[(name[l], round(float(v), 3)) for l, v in top])
    print(json.dumps(out, indent=1))
    json.dump(out, open(os.path.join(HERE, "tfos_results.json"), "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
