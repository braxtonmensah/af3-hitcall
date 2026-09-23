# Pre-registration 11: is the never-solved deficit a readout artefact? (structure-level scores)

Written 2026-09-22 while the structure features were being extracted and before any of them was
joined to STRING, precedent, or crosslink labels.

## Idea

Every result so far scores a pair by chain-pair ipTM, a single global number per chain pair. Transient,
never-solved interactions tend to have small interfaces, and ipTM is known to under-rate small
interfaces (the motivation for ipSAE, Dunbrack 2025, and LIS, Kim et al. 2024). The AF3 output also
carries information the screen never used: a residue-level PAE map, the trunk's inter-chain
**contact probabilities** (from the distogram head, not from confidence), and 5 diffusion samples whose
interfaces can agree or not. If any of these recovers never-solved interactions, the screen's weak
class is partly a scoring artefact and can be fixed after the fact, with no new GPU time.

## Data (fixed before joining labels)

- Todor et al. 2026 Zenodo record 15499631, `AF3_completed_zips.zip`, streamed without storing raw
  files. The analysis set is every `250310_mgen_allbyall_*` pool fully extracted from the first 12
  inner zips in archive order (`pilot_zips.txt`), chosen by position only.
- Extraction check (label-free): the per-pool ipTM recomputed from the summaries and size-corrected
  matches the published per-pool S0 to 1.8e-8, so chain-to-protein mapping is correct.

## Scores (per pair, mean over its pools in the analysis set)

- **S0** (comparator): the published size-corrected ipTM, averaged over the same pools only.
- **IPSAE**: ipSAE per sample (PAE cutoff 10 A, per-residue d0, max over the two directions), mean over
  the 5 samples.
- **LIS**: mean of (12 - PAE)/12 over inter-chain residue pairs with PAE <= 12, both directions, mean
  over samples.
- **CP**: maximum trunk contact probability between the two chains (sample 0 file; trunk quantity).
- **REP**: interface reproducibility. For each sample, the interface is the set of residues (both
  chains) with CB (CA for Gly) within 8 A of the other chain. REP = mean Jaccard over the 10 sample
  pairs, where an empty set counts as Jaccard 0.
- Size correction for the four new scores, as the paper did for ipTM: OLS of score on
  sqrt(len_A + len_B) over all pairs in the analysis set (label-free), residuals used. Raw versions
  reported too.

## Labels and tests

Positive = STRING experimental > 800, negative = all other pairs in the analysis set. Precedented =
`precedent_matrix_strict("") | precedent_matrix_strict("_id0")`, never-solved = not.

- **Primary (rescue), one test per score**: AUROC(score) - AUROC(S0), never-solved positives vs all
  negatives. Node bootstrap, 2,000 reps. Bonferroni over the 4 scores: 98.75% CI. **Rescue** if the
  lower bound > 0.
- **Secondary (does the gap close)**: for the score with the largest primary point estimate, the
  precedent gap AUROC(precedented) - AUROC(never-solved) compared with the same gap under S0 (95% CI of
  the difference of gaps).
- Reported: precedented-class AUROC for every score, and the in-cell crosslink truth (O'Reilly 2020
  set as in PREREG_XL) for any score that passes the primary.

## Known weaknesses

- One truth set (STRING experimental) for the primary. The crosslink check is there for any pass.
- The subset is a fraction of the screen, so power is lower than the full-data tests.
- ipSAE and LIS are existing scores; what is new is testing whether they rescue the class a
  genome-wide screen fails on. CP (trunk contact probability) and REP have not been used for
  hit-calling in this setting as far as the prior-art check found.
