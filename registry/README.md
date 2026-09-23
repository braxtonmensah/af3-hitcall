# Forward prediction registry (frozen 2026-09-23)

`open_confident_human_pairs_2026-09-23.csv` lists the 6,010 human protein pairs that Burke et al.'s
2021 AF2/FoldDock screen modelled confidently (pDockQ > 0.23), that had no co-complex structure before
2022, and that still have none in the PDB as of the SIFTS release of 2026-09-20. For each pair, the
predicted interface residues (UniProt numbering) are given. SHA-256 of the file is in `SHA256.txt`,
and the git commit that adds it fixes the date.

## The forecast (made before any of these structures exist)

Based on PREREG_FUTURE (81% correct interfaces, 53% in the X-ray-only subset, stable across the
2022-23 and 2024-26 cohorts):

1. **Correctness.** Among registry pairs whose first PDB co-complex with direct contact (>= 5 CB pairs
   < 8 A) is released between 2026-10-01 and 2028-12-31, **at least 60%** will have predicted-interface
   F1 >= 0.5 against the new structure (method: `analysis_future.py` F2). Point expectation: about 80%.
2. **Anticipation.** Over the same window, registry pairs will get a first co-complex at **at least
   twice** the rate of the low-confidence (pDockQ < 0.10) never-solved pairs (FUTURE measured 2.8x).
3. **Refutation.** If, with at least 30 qualifying pairs, the correct fraction is below 50%, the claim
   "confident never-solved AF predictions are usually right" is refuted for this screen.

Expected volume: FUTURE saw 2.5% of confident pairs solved with direct contact in about 4.7 years,
so roughly 30 or more registry pairs a year, fewer if the field's pace slows.

## How to check

Rebuild `future/pairs.csv` with `build_future.py` (change `CUT` to 2026-10-01 and the population to
the registry pairs), then run `analysis_future.py`. Everything uses public data (Burke S1 and models,
SIFTS, RCSB).
