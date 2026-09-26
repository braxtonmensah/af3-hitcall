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

## 6,010 or 6,009? Both, and they count different things

Two numbers for this registry appear in the repository and they are reconcilable, not a contradiction:

- **6,010** distinct **accession pairs**. This is the row count of
  `open_confident_human_pairs_2026-09-23.csv`, every `uid` is unique, and it is the figure quoted in
  `CONCEPT.md`, `PITCH.md` and the outreach drafts.
- **6,009** distinct **gene-symbol pairs**. This is what `POSTHOC.md`'s PH-DRUG join reports, because
  CORUM is keyed on gene symbols.

The single pair responsible is **TADA3-TADA2A**, which appears under two accessions for TADA2A:

| uid | TADA2A accession |
|---|---|
| `O75478_O75528` | O75478, the canonical entry |
| `A0A024R0Y4_O75528` | A0A024R0Y4, a second accession for the same gene |

So one gene pair is represented by two rows. This is inherited from the upstream accession set, not
introduced here. Neither figure is wrong; **quote 6,010 for pairs and 6,009 for gene-level
interfaces**, and if a single number is needed for an external claim, use 6,009, because a reader will
read "pairs" as distinct interactions and TADA3-TADA2A is one interaction.
