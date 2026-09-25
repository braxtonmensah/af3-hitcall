# Pre-registration 19: independent replication with the in-cell DSS crosslink dataset (XLDSS)

Written 2026-09-25 before downloading or viewing any row of the DSS dataset (PRIDE PXD017695,
`Myco_InCell_DSS_dataset_5link_5PPI_*`, O'Reilly et al. 2020, same study as the DSSO data but a
different crosslinker and separate experiments).

## Why

XLVAL (DSSO) supported MG241-MG242 (3/3 links at 12-16 A) only after a post hoc sequence fix, and
RNase J-MG423 was borderline (2/4). A different crosslinker from separate in-cell experiments is an
independent test that was not looked at before this was written.

## Method (identical to XLVAL with Amendment 2, fixed now)

- DSS links at 5% link FDR (`isTT`, not decoy, `fdr <= 0.05`), inter-protein, both proteins mapped
  to *M. genitalium* by the existing ortholog table. Sites resolved by locating peptides in current
  UniProt *M. pneumoniae* sequences (the Amendment 2 method), then aligned to *M. genitalium*.
- Same AF3 coordinates (all pools and samples), same CA-CA <= 30 A cutoff (DSS reach is comparable to
  DSSO's), same random cross-chain lysine null (1,000 draws), same "supported" rule.
- Pairs: the 14 XLVAL candidates. Controls: DSS-crosslinked never-solved pairs with S0 < 0.05
  (seed 19, up to 20).

## Pre-specified predictions

- **P1 (the key test):** if MG241-MG242 has DSS links, they satisfy the rule (supported). If it has no
  DSS links, this test is uninformative for it and that is reported.
- **P2:** RNase J-MG423 DSS links, if any, reported with distances; the tetramer idea predicts a mix of
  near and far links again.
- **P3:** controls mostly fail (as with DSSO), or the test is not discriminating.

A candidate becomes a **replicated new complex** only if supported in both DSSO and DSS.
