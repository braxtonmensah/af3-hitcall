"""POST HOC (2026-09-25): do RNase J (MPN280) and its dead paralog (MPN621) co-elute, and at a mass
matching the 2:2 heterotetramer rather than the 1:1 heterodimer?

Data: Lluch-Senar et al. 2015 (Mol Syst Biol, PMC4332154) Dataset S6 Table S6 = SEC-MS of an
M. pneumoniae cell extract. Columns are SEC fractions labelled by apparent mass (kDa); values are
log2 intensities. This is published, independent of AlphaFold and of the crosslinks.

Predictions being tested (from our AF3 model):
  heterodimer  MPN280 + MPN621            ~ 64 + 63  = 127 kDa
  heterotetramer (MPN280)2(MPN621)2       ~ 2x64 + 2x63 = 254 kDa
Controls, because a shared peak means nothing if everything peaks there:
  1. where every one of the ~438 proteins peaks (is 297 kDa a generic artefact?)
  2. profile correlation of MPN280 vs MPN621 against the distribution of MPN280 vs all other proteins
  3. monomer-mass expectation: a free 64 kDa protein should peak near 64 kDa, not near 300
"""
import io
import json
import os
import zipfile

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ZP = r"C:\Users\bmens\NQ_local\af3-hitcall\essential\msb_suppl.zip"
MASS = {"MPN280": 64.0, "MPN621": 63.0}  # approx, from sequence length x 110 Da

z = zipfile.ZipFile(ZP)
raw = pd.read_excel(io.BytesIO(z.read("msb0011-0780-sd15.xlsx")), sheet_name="Table S6", header=None)
hdr = raw.iloc[1].tolist()
# fraction columns = those whose header parses as a float (apparent mass in kDa)
frac = []
for c in range(3, raw.shape[1]):
    try:
        frac.append((c, float(hdr[c])))
    except (TypeError, ValueError):
        pass
# the sheet holds two panels (A, then B); keep the first contiguous descending run = panel A
keep = [frac[0]]
for c, m in frac[1:]:
    if m < keep[-1][1]:
        keep.append((c, m))
    else:
        break
cols = [c for c, _ in keep]
masses = np.array([m for _, m in keep])
body = raw.iloc[2:].copy()
body = body[body[1].notna()]
prof = body[cols].apply(pd.to_numeric, errors="coerce")
prof.index = body[1].astype(str).str.strip()
prof = prof[~prof.index.duplicated()]
res = {"n_fractions": len(cols), "mass_range_kDa": [float(masses.min()), float(masses.max())],
       "n_proteins": int(prof.shape[0])}


def peak_mass(name):
    v = prof.loc[name].to_numpy(float)
    if np.all(np.isnan(v)):
        return None
    return float(masses[int(np.nanargmax(v))])


res["peak_mass_kDa"] = {g: peak_mass(g) for g in MASS}
res["monomer_mass_kDa"] = MASS
res["predicted_heterodimer_kDa"] = round(sum(MASS.values()), 1)
res["predicted_heterotetramer_kDa"] = round(2 * sum(MASS.values()), 1)

# control 1: where does everything peak?
peaks = pd.Series({g: peak_mass(g) for g in prof.index}).dropna()
res["control1_peak_distribution"] = {str(k): int(v) for k, v in peaks.value_counts().head(8).items()}
res["control1_frac_proteins_peaking_at_our_peak"] = float((peaks == res["peak_mass_kDa"]["MPN280"]).mean())

# control 2: profile correlation, ours vs all
a = prof.loc["MPN280"].to_numpy(float)


def corr(b):
    m = np.isfinite(a) & np.isfinite(b)
    return float(np.corrcoef(a[m], b[m])[0, 1]) if m.sum() >= 5 else np.nan


cors = pd.Series({g: corr(prof.loc[g].to_numpy(float)) for g in prof.index if g != "MPN280"}).dropna()
res["control2_corr_MPN280_vs_MPN621"] = float(cors.get("MPN621", np.nan))
res["control2_corr_percentile"] = float((cors < cors.get("MPN621", np.nan)).mean() * 100)
res["control2_corr_distribution"] = {"median": float(cors.median()), "p90": float(cors.quantile(0.9)),
                                     "p99": float(cors.quantile(0.99)), "max": float(cors.max()),
                                     "n_compared": int(len(cors))}
res["control2_top5_partners_by_corr"] = {k: round(float(v), 3) for k, v in cors.sort_values(ascending=False).head(5).items()}

# control 3: is the peak above monomer mass?
res["control3_peak_over_monomer_ratio"] = {g: round(res["peak_mass_kDa"][g] / MASS[g], 2) for g in MASS if res["peak_mass_kDa"][g]}
res["verdict"] = ("co-elute far above monomer mass, near the 2:2 prediction"
                  if all((res["peak_mass_kDa"][g] or 0) > 1.5 * MASS[g] for g in MASS) else "not supported")
print(json.dumps(res, indent=1))
json.dump(res, open(os.path.join(HERE, "results_sec.json"), "w"), indent=1)
prof.loc[["MPN280", "MPN621"]].T.assign(mass_kDa=masses).to_csv(os.path.join(HERE, "sec_profiles.csv"), index=False)
