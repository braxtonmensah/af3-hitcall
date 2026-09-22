"""Design the V. cholerae pooled-AF3 pilot (see PREREG_VIBRIO.md).

System proteins: Dalia-lab competence / chitin-sensing machinery. Decoys: random N16961 proteins
(fixed seed), used as each bait's null partners. Pools are a greedy cover of all pairs under a
4,000-aa cap: the largest size that fits Big Red 200's A100 40 GB (AF3 docs: 4,352 tokens), and on
matched pairs as good as 5,000 aa (POSTHOC PH2).

Outputs (vibrio_pilot/jobs/): afserver_batchNN.json (<= 30 jobs each, AF Server upload format),
pools.csv (job -> proteins), proteins.csv."""
import json
import os
import re

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = r"C:\Users\bmens\NQ_local\af3-hitcall\vibrio\vc_proteome.tsv"
OUT = os.path.join(HERE, "jobs")
CAP = 4000
SEED = 20260922
N_DECOYS = 60

SYSTEM = {  # locus: (name, role)
    "VC_0462": ("PilT", "retraction ATPase"),
    "VC_0463": ("PilU", "retraction ATPase"),
    "VC_0620": ("CBP", "chitin-binding SBP"),
    "VC_0622": ("ChiS", "chitin sensor HK"),
    "VC_0048": ("DprA", "recombination mediator"),
    "VC_0032": ("ComM", "helicase"),
    "VC_2423": ("PilA", "major pilin"),
    "VC_2424": ("PilB", "extension ATPase"),
    "VC_2425": ("PilC", "platform"),
    "VC_2426": ("PilD", "prepilin peptidase"),
    "VC_2630": ("PilQ", "secretin"),
    "VC_2631": ("PilP", "alignment"),
    "VC_2632": ("PilO", "alignment"),
    "VC_2633": ("PilN", "alignment"),
    "VC_2634": ("PilM", "alignment"),
    "VC_0857": ("VC0857", "minor pilin"),
    "VC_0858": ("VC0858", "minor pilin"),
    "VC_0859": ("VC0859", "minor pilin"),
    "VC_0860": ("VC0860", "minor pilin"),
    "VC_0861": ("VC0861", "minor pilin"),
    "VC_1917": ("ComEA", "DNA receptor"),
    "VC_1879": ("ComEC", "DNA channel"),
    "VC_1153": ("TfoX", "regulator"),
    "VC_0396": ("QstR", "regulator"),
}
EXCLUDE = re.compile(r"pilus|pilin|competence|chitin|secretion|fimbri|twitching|DprA|Smf|ComM|transformation", re.I)


def main():
    d = pd.read_csv(SRC, sep="\t")
    d["locus"] = d["Gene Names (ordered locus)"].astype(str).str.split().str[0]
    d = d[d.Sequence.notna()]
    sysrows = []
    for loc, (name, role) in SYSTEM.items():
        m = d[d.locus == loc]
        assert len(m) == 1, loc
        sysrows.append(dict(locus=loc, name=name, role=role, kind="system",
                            accession=m.Entry.iloc[0], length=int(m.Length.iloc[0]), sequence=m.Sequence.iloc[0]))
    pool = d[(~d.locus.isin(SYSTEM)) & d.Length.between(100, 600) & ~d["Protein names"].astype(str).str.contains(EXCLUDE)]
    dec = pool.sample(N_DECOYS, random_state=SEED)
    decrows = [dict(locus=r.locus, name=r.locus, role=str(r["Protein names"])[:60], kind="decoy",
                    accession=r.Entry, length=int(r.Length), sequence=r.Sequence) for _, r in dec.iterrows()]
    P = pd.DataFrame(sysrows + decrows).reset_index(drop=True)
    n = len(P)
    L = P.length.to_numpy()
    rng = np.random.default_rng(SEED)
    covered = np.eye(n, dtype=bool)
    pools = []
    while not covered.all():
        missing = (~covered).sum(1)
        start = rng.choice(np.flatnonzero(missing == missing.max()))
        members, size = [start], L[start]
        while True:
            cand = [k for k in range(n) if k not in members and size + L[k] <= CAP]
            if not cand:
                break
            gain = np.array([(~covered[k, members]).sum() for k in cand], float)
            if gain.max() == 0:
                break
            # new pairs per residue, so long proteins don't crowd out coverage
            score = gain / L[cand]
            k = cand[int(np.argmax(score + 1e-9 * rng.random(len(cand))))]
            members.append(k)
            size += L[k]
        for a in members:
            covered[a, members] = True
        pools.append(members)
    os.makedirs(OUT, exist_ok=True)
    P.drop(columns="sequence").to_csv(os.path.join(OUT, "proteins.csv"), index=False)
    rows, jobs = [], []
    for k, mem in enumerate(pools, 1):
        name = f"vc_pilot_{k:03d}"
        rows.append(dict(job=name, n=len(mem), aa=int(L[mem].sum()), loci="::::".join(P.locus[mem])))
        jobs.append({"name": name, "modelSeeds": [], "dialect": "alphafoldserver", "version": 1,
                     "sequences": [{"proteinChain": {"sequence": P.sequence[m], "count": 1}} for m in mem]})
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "pools.csv"), index=False)
    for b in range(0, len(jobs), 30):
        json.dump(jobs[b:b + 30], open(os.path.join(OUT, f"afserver_batch{b // 30 + 1:02d}.json"), "w"))
    npairs = n * (n - 1) // 2
    per = pd.DataFrame(rows)
    print(f"proteins {n} ({len(sysrows)} system, {len(decrows)} decoys), pairs {npairs}, pools {len(pools)}, "
          f"batches {int(np.ceil(len(pools) / 30))}, pool size median {per.n.median()} proteins / {per.aa.median()} aa, max aa {per.aa.max()}")


if __name__ == "__main__":
    main()
