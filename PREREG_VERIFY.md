# Pre-registration 17: trying to break FUTURE and FUTURE-Y (VERIFY)

Written 2026-09-23 before running any check below. Goal: certainty. Each check targets a specific way
the headline ("confident predictions of never-solved complexes are right 81-89% of the time") could be
wrong. The claim is narrowed or withdrawn according to the rules below, whatever they show.

## V1 (primary threat): homologous precedent

FUTURE excluded pairs whose *own* proteins had a pre-2022 co-complex, but not pairs with a pre-2022
co-complex of **homologs** (for example the same complex from another species). Our own audit showed
precedented complexes are the easy ones. If the 81-89% comes from homolog-precedented pairs, "right
on novel complexes" is false.

- For every protein in the FUTURE F2 set (human, both groups) and the FUTURE-Y Y1 set (yeast): RCSB
  sequence search on the full UniProt sequence, E <= 1e-3, identity >= 0.25 (the audit's rule),
  entries released on or before 2021-12-31.
- **Homolog-precedented** = some pre-2022 entry contains a homolog of each protein, with the strict
  rule (each protein matches an entity the other does not). Sensitivity: identity >= 0 (remote homologs).
- **Rule:** the "novel complexes" claim survives only if, among confident pairs with **no** homolog
  precedent, the correct fraction (F1 >= 0.5) has a 95% bootstrap CI lower bound above 0.5, in human.
  Yeast is reported the same way. If it fails, the claim is narrowed to what the data support.

## V2: is correctness trivially easy? (human)

For each confident human F2 pair, 200 random circular shifts of the predicted interface along each
chain (same as FUTURE-Y Y2). Passes if the observed correct fraction is far above the null's 99th
percentile.

## V3: dependence between pairs

Several pairs come from the same PDB entry. Recompute the correct-fraction CIs with an **entry-level**
cluster bootstrap (resample entries), human and yeast, overall and within V1's no-precedent subset.

## V4: an independent metric

Residue-pair **Fnat**: the fraction of native inter-chain residue pairs (CB/CA within 8 A, UniProt
numbering, observed residues) that the model also has in contact, computed from model coordinates
(streamed again) rather than from the stored residue sets. Acceptable = Fnat >= 0.3. Reported for the
confident and low groups and within V1's subsets; the conclusion must not depend on the metric.

## V5: thresholds

Correct fraction over interface cutoffs 6 / 8 / 10 A and correctness thresholds F1 >= 0.3 / 0.5 / 0.7
(human confident). Reported as a grid.

## What would change the claim

- V1 fails: the claim becomes "confident predictions are right on complexes with homologous
  precedent" (a much weaker, largely known statement), and CONCEPT.md is rewritten to say so.
- V2 near null, or V4 disagreeing with F1: the correctness metric is not trustworthy and the headline
  numbers are withdrawn until fixed.
