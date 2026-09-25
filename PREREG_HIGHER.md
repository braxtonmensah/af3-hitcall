# Pre-registration 23: the split-crosslink signature of higher-order assembly (HIGHER)

Written 2026-09-25, before computing any distance for this test and before any pair's signature was
looked at. Uses only data already in the repository (O'Reilly 2020 DSSO and DSS links, the pooled
AF3 CA coordinates, the *M. genitalium* proteome).

## Why

TETRA established one thing on one complex. For MG_139-MG_423, three in-cell crosslinks sat at
51-63 A in the two-chain model, which is beyond any crosslinker's reach, and the same three fell to
12.5-15 A once the pair was modelled as a 2:2 heterotetramer. The unsatisfiable links were not noise
and not a wrong prediction. They were the assembly telling us there were more copies than we had
modelled.

That reading has never been tested as a general rule. If it holds, it converts a one-off result into
an instrument: **a pair whose crosslinks split into a satisfied set and an impossible set is a pair
whose stoichiometry is higher than 1:1**, and the pooled screens already contain hundreds of such
pairs nobody has looked at this way.

If it fails, then the RNase J far links were special pleading and TETRA is weaker than it reads. That
outcome is reported.

## Definitions (fixed now)

- **Usable link**: an inter-protein crosslink at 5% link FDR, both proteins mapped to *M. genitalium*,
  sites resolved by the Amendment 1 peptide-location method, residues alignable to the *M. genitalium*
  sequence. DSSO and DSS links are pooled (union of distinct residue pairs); the split by crosslinker
  is also reported.
- **Model distance**: CA-CA in a pooled AF3 model containing both proteins. Per link, the statistic is
  the **minimum over all models and samples**, which is the most favourable case for the dimer.
- **Near link**: minimum distance <= 30 A (within reach).
- **Impossible link**: minimum distance >= 45 A. The gap between 30 and 45 A is deliberately left
  unclassified so borderline links decide nothing.
- **Split signature**: a pair with at least one near link AND at least one impossible link.
- **Clean dimer**: a pair with at least two usable links, all of them near.
- **Testable pair**: at least two usable links and at least one model.

## The independent evidence line: over-length self-links

A crosslink between two residues of the *same* protein whose CA-CA distance in that protein's own
chain is >= 45 A cannot be satisfied within one copy of that chain. The standard reading is that the
protein is present as more than one copy. This is computed from the same files and is independent of
the inter-protein test.

- **Oligomeric partner**: a pair in which at least one of the two proteins has at least one
  over-length self-link.

## Tests

**P1 (primary).** P(oligomeric partner | split signature) minus P(oligomeric partner | clean dimer).
Bootstrap over proteins, 2,000 replicates, 95% CI.
- **Supported** if the difference is positive and the CI excludes 0.
- **Refuted** if the CI excludes 0 in the negative direction.
- **Inconclusive** otherwise, including if either group has fewer than 8 pairs, which is declared
  underpowered and not interpreted.

**P2 (positive control).** MG_139-MG_423 must carry the split signature. If it does not, the
definitions do not reproduce the result they were built from and P1 is not interpreted.

**P3 (output, conditional on P1).** The list of pairs that (a) carry the split signature, (b) have an
oligomeric partner, and (c) have no strict pre-2021 co-complex precedent. These are the predicted
higher-order assemblies. Each is a hypothesis for the bench, not a solved structure.

## Reported whatever the outcome

Counts for every group, the full per-pair table, and the negative result if P1 fails. Pairs excluded
for too few links or no model are counted.

## Limitations, stated before the result

- An over-length self-link can also reflect conformational flexibility or a disordered region rather
  than oligomerisation. It is evidence, not proof, and the P3 list inherits that uncertainty.
- The pooled models were not built to represent stoichiometry, so "impossible in this model" means
  impossible in a 1:1 arrangement, not impossible in principle.
- Crosslink site resolution carries the errors documented in XLVAL Amendment 1 and 2.
- This test cannot say *what* the higher-order arrangement is. TETRA needed a homologous template to
  settle 2:2 for RNase J, and each P3 pair would need the same.
