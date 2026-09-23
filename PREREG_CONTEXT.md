# Pre-registration 10: pooled AF3 as an in-silico competition assay (context effects)

Written 2026-09-22, before any STRING label, precedent class or AUROC was joined to pool context.
Only label-free design facts were looked at first: 2,027 pools of 4-23 proteins (median 13), every
within-pool pair scored (160,772 pair-pool rows), 38,718 pairs folded in 2 or more pools, and the
per-pool S0 quantiles (99th 0.102, 99.5th 0.167, 99.9th 0.392). The context counts below were
computed without labels.

## Idea

Every pooled prediction is one AF3 model of about 13 proteins. If a third protein X in the same pool
binds A (or B) strongly, it may occupy the interface A would use for B, and suppress a real A-B
interaction in that model. The pooled screen is then a competition assay, and a low score next to a
strong competitor is weaker evidence of "no interaction" than a low score in a quiet pool. The
random pool design means competitor presence is assigned by chance for the 38,718 pairs folded more
than once: a natural experiment.

The audit found never-solved interactions are close to chance. If competition masks them, part of
that weakness is a design artefact that a context-aware score (or pool design) can remove.

## Definitions (fixed)

- Data: `s0_per_pool.csv` (size-corrected ipTM of every pair in every pool).
- tau = 0.2 (about the top 0.6% of per-pool values). Sensitivity: tau = 0.3.
- For pair (A, B) in pool p, over the other members X of p, with a = S0(A,X,p), b = S0(B,X,p):
  **bridge** if some X has a >= tau and b >= tau; else **compete** if some X has max(a, b) >= tau;
  else **clean**. (Label-free counts at tau 0.2: clean 147,873, compete 12,832, bridge 67. Bridges
  are too rare to test and are only described.)
- Positive = STRING experimental > 800; negative = every other pair (as in H1).
  Precedented = `precedent_matrix_strict("") | precedent_matrix_strict("_id0")`; never-solved = not.
- Paired unit: a pair with at least one clean and at least one compete pool (6,016 pairs at tau 0.2).
  delta = mean S0 over its compete pools - mean S0 over its clean pools.
- Uncertainty: node bootstrap (resample proteins, pair weight c_i * c_j), 2,000 reps, 95% CI.

## Tests

- **T1 (primary, competition exists)**: mean delta over positives < 0, CI upper bound < 0; and the
  difference-in-differences delta_pos - delta_neg < 0, CI upper bound < 0.
- **T2 (which class is masked)**: mean delta separately for never-solved and precedented positives.
  "Never-solved interactions are masked" if the never-solved CI upper bound < 0.
- **T3 (specificity, competition not crowding)**: "remote" context = no competitor for A or B, but the
  pool contains some other pair X-Y with S0 >= tau. "Quiet" = no pair in the pool reaches tau.
  delta_remote = mean over remote pools - mean over quiet pools, for positives with both. Competition-
  specific if delta_compete - delta_remote (positives) has CI upper bound < 0.
- **T4 (practical rescue)**: S_ctx = mean S0 over a pair's clean pools if it has any, else the mean over
  all its pools. AUROC(S_ctx) - AUROC(S0), never-solved positives vs all negatives, node bootstrap.
  Rescue if the CI lower bound > 0. Precedented class reported too.
- **Sensitivity (reported, not a gate)**: T1 at tau = 0.3, and T1 with competitors defined
  exogenously (A-X or B-X scored >= tau as the mean over pools other than p; pairs whose competitor
  has no other pool are dropped), which removes same-model coupling between competitor and outcome.

## Known weaknesses

- STRING positives include complex co-members; a "competitor" can be a co-member that should help, not
  hurt. Bridges are the direct measure of that and are rare.
- Same-model coupling: the competitor and the outcome come from one AF3 model. The exogenous
  sensitivity check and the T3 remote control are there for this.
- Negatives sit near S0 = 0, so they cannot fall much; the DiD is mostly the positive delta.
