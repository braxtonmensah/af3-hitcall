# Pre-registration 34: is the H1 gap a residual length artifact? (LENMATCH)

Committed before computing any stratified statistic. Registered 2026-09-26.

## The threat

H1 reports that size-corrected ipTM (S0) separates precedented positives from negatives at
AUROC 0.85 and never-solved positives at 0.71, a gap of 0.145.

S0 is a *size-corrected* score. The correction is a single global trend fitted by Todor et al.
If that correction leaves residual length dependence, and if precedented pairs differ
systematically in length from never-solved pairs, then part or all of the H1 gap could be a
length artifact rather than an effect of structural precedent.

This is plausible rather than hypothetical. Proteins that get crystallised early tend to be
well-behaved and abundant, and complexes deposited before 2021 are not a random length sample of
the proteome. No test in this repository has controlled for it. It is the first question a
reviewer should ask about a size-corrected score, and it has not been asked here.

## Definitions

- **L(pair)** = length(A) + length(B), from `proteins.csv`, summed residue counts.
- **Precedented / unprecedented** as defined in PREREG.md H1 (RCSB mmseqs2, E <= 1e-3,
  identity >= 0.25, PDB entries released on or before 2021-09-30, two distinct entities).
- **Positives** = STRING experimental > 800. **Negatives** = all non-positives, as in H1.
- **Strata** = quintiles of L computed over **all pairs**, with cut points fixed before any
  AUROC is computed.

## Test

Within each stratum s, compute AUROC of S0 for precedented positives against all negatives in
s, and for unprecedented positives against the same negatives in s.

    gap(s) = AUROC_prec(s) - AUROC_unprec(s)

Primary statistic is the weighted mean of gap(s), weighting each stratum by its total positive
count. Strata containing fewer than 20 unprecedented positives are dropped and the drop is
reported.

Uncertainty by the repository's standard node bootstrap (`metrics.node_weights`, resampling
proteins so pair dependence is respected), 2000 replicates, recomputing the full stratified
statistic in each replicate.

## Decision rule, fixed in advance

- **Confirmed**: weighted gap >= 0.05 and the 95% CI excludes 0. The H1 gap is not explained by
  length.
- **Rejected**: the 95% CI includes 0. The H1 gap is not separable from length in this design,
  and every claim resting on it must be restated.
- **Between**: weighted gap in (0, 0.05) with a CI excluding 0, reported as "direction supported,
  size below threshold".

## Reported regardless of outcome

- Median and interquartile L for precedented and unprecedented positives.
- Spearman correlation between L and S0 over all pairs, and within positives only.
- Per-stratum gap, and the count of precedented and unprecedented positives in each stratum.
- Any stratum dropped for thinness.

## What would change the claim

If LENMATCH is rejected, the headline of this project becomes unsupported as stated, and the
README, the preprint and any outreach describing a precedent effect must be corrected to say
that precedent and length are confounded in this dataset. No post-hoc reweighting will be
introduced to rescue it.
