# Pre-registration 8: surface-matched disease-variant test (revision of PREREG_CLINVAR)

Written 2026-09-22 after PREREG_CLINVAR failed its positive control (precedented interfaces OR 0.70).
Committed before re-extracting any structure data.

## Why the first design failed (diagnosis, stated before re-running)

Pathogenic missense variants concentrate in buried cores. Interface residues are surface residues of
the monomer. Comparing interface against the whole rest of the protein is therefore dominated by core
burial and biased against interfaces. The low-confidence control meant to absorb this had only 28
variants at ordered interface residues.

## Fix

Compare interface residues only with *other surface residues*, the standard design in this field.

- **Burial**: contact number CN = the number of CB/CA atoms of the same chain within 10 A of the
  residue's CB/CA, computed on each monomer chain in its model.
- **Surface residue** = CN below that chain's median CN, among residues with pLDDT >= 70.
- Counts use surface, ordered residues only: interface vs non-interface, pathogenic (LP/P) vs benign
  (LB/B). OR as before (+0.5), bootstrap over proteins, 2,000 reps, 95% CI. Groups, variant source,
  exact-sequence filter and interface definition are unchanged.

## Tests

- **T2 (positive control, first)**: OR_precedented > 1 with the CI excluding 1. If it fails, stop:
  the approach cannot detect even solved interfaces in this data.
- **T1 (primary)**: OR_novel > 1 with the CI excluding 1, meaning novel confident interfaces carry
  disease signal.
- **T3**: OR_precedented / OR_novel. "Comparable" if the CI includes 1.
- Control (pDockQ < 0.10): reported; expected near 1.

This is the second attempt at this question. Both attempts are reported regardless of outcome.
