"""Build tidy arrays from the Todor et al. 2026 supplementary tables.

Writes to NQ_local/af3-hitcall/data:
  proteins.csv       locus, accession, length, sequence
  S0.npy, raw.npy    476x476 size-corrected / raw ipTM (NaN diagonal)
  corr.npy           paper's profile-correlation matrix
  string_exp.npy     476x476 STRING experimental score
  npools.npy         476x476 number of pools each pair appeared in
"""
import os
import numpy as np
import pandas as pd

ROOT = r"C:\Users\bmens\NQ_local\af3-hitcall"
SUP = os.path.join(ROOT, "suppl")
OUT = os.path.join(ROOT, "data")
os.makedirs(OUT, exist_ok=True)


def f(n):
    return os.path.join(SUP, f"44320_2026_189_MOESM{n}_ESM.xlsx")


seq = pd.read_excel(f(4), sheet_name="mgen_protein_sequences")
seq["accession"] = seq.annotation.str.extract(r"prot_([A-Z]{3}\d+)\.")[0].str.lower()
seq["length"] = seq.aa_sequence.str.rstrip("*").str.len()
loci = list(seq.locus_tag)
idx = {l: i for i, l in enumerate(loci)}
n = len(loci)
seq[["locus_tag", "accession", "length", "aa_sequence"]].to_csv(os.path.join(OUT, "proteins.csv"), index=False)


def matrix(sheet, book=7):
    m = pd.read_excel(f(book), sheet_name=sheet, index_col=0)
    m.index = m.index.astype(str)
    m.columns = m.columns.astype(str)
    missing = set(loci) - set(m.index)
    assert not missing, (sheet, list(missing)[:5])
    return m.loc[loci, loci].apply(pd.to_numeric, errors="coerce").to_numpy(float)


string = matrix("STRING_experimental channel")
np.fill_diagonal(string, np.nan)
np.save(os.path.join(OUT, "string_exp.npy"), string)
np.save(os.path.join(OUT, "corr.npy"), matrix("correlation of corrected ipTM"))

# pair tables (MOESM5) are the primary source for S0 and raw
def pairs(sheet, col):
    d = pd.read_excel(f(5), sheet_name=sheet)
    a = d.protein_pair.str.split("::::", expand=True)
    M = np.full((n, n), np.nan)
    i = a[0].map(idx).to_numpy()
    j = a[1].map(idx).to_numpy()
    ok = ~(pd.isna(i) | pd.isna(j))
    assert ok.all(), d[~ok].head()
    # pairs seen in several pools list every value, tab-separated; S0 is their mean (paper Methods)
    reps = d[col].astype(str).str.split("\t").map(lambda xs: [float(x) for x in xs])
    v = reps.map(np.mean).to_numpy()
    M[i.astype(int), j.astype(int)] = v
    M[j.astype(int), i.astype(int)] = v
    d = d.assign(i=i.astype(int), j=j.astype(int), reps=reps)
    return M, d


S0, s0long = pairs("size_corrected_ipTMS", "size_corrected_ipTM")
raw, _ = pairs("uncorrected_ipTMS", "uncorrected_ipTM")
p2p = pd.read_excel(f(5), sheet_name="pairs_to_pools")
a = p2p.protein_pair.str.split("::::", expand=True)
pools = p2p.pools_pair_is_in.astype(str).str.split("\t")
cnt = pools.map(len)
rep = s0long[["protein_pair", "i", "j", "reps"]].copy()
rep["pools"] = pools.to_numpy()
assert (rep.reps.map(len) == rep.pools.map(len)).all()
rep = rep.explode(["reps", "pools"]).rename(columns={"reps": "s0", "pools": "pool"})
rep.to_csv(os.path.join(OUT, "s0_per_pool.csv"), index=False)
print("per-pool rows", len(rep))
# cross-check against the paper's matrix in MOESM7
m7 = matrix("size_corrected ipTM")
print("max |S0 - MOESM7 matrix|", np.nanmax(np.abs(m7 - S0)))
NP = np.zeros((n, n))
NP[a[0].map(idx), a[1].map(idx)] = cnt
NP[a[1].map(idx), a[0].map(idx)] = cnt

for name, M in [("S0", S0), ("raw", raw), ("npools", NP)]:
    np.save(os.path.join(OUT, f"{name}.npy"), M)

iu = np.triu_indices(n, 1)
print("proteins", n, "pairs", len(iu[0]))
print("S0 finite pairs", np.isfinite(S0[iu]).sum(), " raw finite", np.isfinite(raw[iu]).sum())
print("npools dist", pd.Series(NP[iu]).value_counts().sort_index().to_dict())
# sanity: the paper's own size formula reproduces S0 from raw
L = seq.length.to_numpy()
pred = raw - (-0.036255571 + 0.004470512 * np.sqrt(L[:, None] + L[None, :]))
print("max |S0 - (raw - size formula)|", np.nanmax(np.abs(pred[iu] - S0[iu])))
print("STRING >800 pairs", (string[iu] > 800).sum(), " =999", (string[iu] == 999).sum())
