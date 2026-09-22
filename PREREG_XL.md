# Pre-registration 2: does H1 survive a truth set that does not come from the PDB?

Written 2026-09-22 after H1-H3 and PH1 (see POSTHOC.md). Committed before any AF3 score was
joined to the crosslinking data.

## Why

H1 showed that STRING positives with a solved homologous co-complex score AUROC 0.85, and those
without score 0.71. PH1 showed that pairs whose proteins are both structurally known but never
solved together score only 0.655. There are two readings, and they matter differently to a lab:

- **(a) Model**: AF3 is genuinely weaker on interfaces it has no template or training analogue for.
- **(b) Labels**: STRING's non-PDB positives include indirect co-complex associations (AP-MS,
  co-fractionation) that are not direct contacts, so no contact predictor could score them.

In-cell crosslinking MS reports residue pairs within about 30 A, which is direct proximity measured
in living cells, independent of the PDB. If (b) is right, crosslinked pairs without co-complex
precedent should score about as well as precedented ones. If (a) is right, the gap persists.

## Data

- O'Reilly et al. 2020 (Science), PRIDE PXD017711, file
  `Myco_InCell_DSSO_dataset_5link_5PPI_ppi_xiFDR...csv`: *M. pneumoniae* in-cell DSSO crosslinks,
  5% PPI-level FDR as deposited.
- **XL-positive** = fdrGroup "Between", isTT true, not decoy, fdr <= 0.05, both proteins mapped to
  *M. genitalium* by reciprocal best hit (`map_mpn_mg.py`, 398 loci).
- **XL-negative** = pairs of mapped proteins that were both observed in the crosslink data (any
  target link, including self-links) with no heteromeric crosslink between them. This controls for
  abundance: both proteins were visible to the assay.
- Score: S0 (the paper's size-corrected ipTM). Precedent: the H1 primary definition.

## Test (single primary)

AUROC(S0; precedented XL-positives vs XL-negatives) minus AUROC(S0; unprecedented XL-positives vs
XL-negatives). Node bootstrap over proteins, 2,000 reps, 95% CI.

- **(a) supported**: difference >= 0.10 and the CI excludes 0.
- **(b) supported**: CI includes 0 and the unprecedented AUROC >= 0.80.
- Anything else: inconclusive, reported as such.

Also reported: the counts, the AUROC for XL-positives that are STRING-negative (novel to STRING), and
the precedented/unprecedented split among XL-positives. If there are fewer than 30 unprecedented
XL-positives, the test is declared underpowered and not interpreted.
