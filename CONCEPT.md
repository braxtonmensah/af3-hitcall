# The autonomy principle of AI interaction screens

**Claim.** Genome-scale AI screens for protein complexes are *precise but autonomy-limited*.
When a screen is confident about a complex that has never been solved, the predicted interface is
right about 80-90% of the time, judged against structures that did not exist when the predictions
were made. What the screens miss are mostly *non-autonomous* contacts: small interfaces inside large
assemblies, held in place by other subunits. The well-known weakness of these screens on novel
interactions (AUROC 0.57-0.71 here) is therefore a recall problem, not a precision problem.

## Evidence (all pre-registered; see `git log` for order)

| Test | Data | Result |
|---|---|---|
| FUTURE F2 | Human, AF2/FoldDock (Burke 2021 models) vs PDB 2022-26 | 81% of 146 confident never-solved models right vs 2% of 110 low-confidence ones |
| FUTURE F1/F1b | Same | Confident pairs solved afterwards 2.8x as often (8.8x with direct contact) |
| FUTURE-Y | Yeast, RoseTTAFold+AF2 (Humphreys 2021) vs PDB 2022-26 | 89% of 84 right; shifted null 1% |
| Stability | Human cohorts | 80% (released 2022-23) vs 82% (2024-26) |
| Circularity | Both | No in-silico start recorded: 81% human, 89% yeast; <= 3 A: 80%, 88%; human X-ray only 53% (n = 19, the conservative bound) |
| COOP-H | Real structures of AF's hits vs misses | Misses: 27% of interface touches a third chain (hits 11%), from larger assemblies (10.5 vs 6 entities), with pair contacts one third the size (30 vs 85) |
| Nulls that shape the claim | M. genitalium pooled AF3 | Pool context, shared partners, ipSAE/LIS, trunk contact probability, and sample reproducibility do not recover the misses: the information is not in the output |

## Why it matters

1. **For labs.** A confident never-solved hit is worth a bench experiment. A low score says nothing about
   subunits of large assemblies.
2. **For benchmarks.** Scoring screens against STRING or Y2H labels understates their precision on
   novel complexes, because many "true" never-solved pairs are non-autonomous contacts no pairwise
   predictor can see.
3. **For method builders.** Recall on novel interactions will come from inputs (assembly context), not
   from better confidence scores. The rigid composition attempt here failed its own sanity check, so
   the fix remains open.
4. **A leakage-free benchmark design.** "Freeze predictions, wait, score against the future PDB" can be
   run on any published screen with public data.

## How to verify or falsify

- Everything reruns from public data: `build_future.py`, `analysis_future.py`,
  `analysis_future_yeast.py`, `posthoc_future_circularity.py`, `analysis_coop.py`.
- **Forward test:** `registry/` lists 6,010 confident human pairs still unsolved on 2026-09-23, with
  predicted interfaces and a written forecast (>= 60% correct among those solved by 2028-12-31;
  refuted below 50% with n >= 30).

## Limits, stated plainly

- Correctness is measured on pairs that *got solved*. Solvable complexes may be easier than the rest,
  so 80-90% is precision among solved pairs, not among all confident predictions.
- Most new structures are cryo-EM, often built with AlphaFold's help. The strata above bound this, and
  the human X-ray subset gives about half, not 80%.
- Public predictions may steer which complexes get solved, so "solved more often" (F1) is anticipation,
  not proof of cause.
- COOP-H is observational; the causal rescue (fold the missed pair with its bridging subunit) needs GPU
  time and is the next experiment.
