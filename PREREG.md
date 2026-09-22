# Pre-registration: hit-calling in genome-wide AlphaFold3 interaction screens

Written 2026-09-22, committed before any score was joined to the truth set.
Data: Todor et al., Mol Syst Biol 2026 (pooled-AlphaFold3, *M. genitalium*, 476 proteins,
113,050 pairs). Supplementary Datasets EV2-EV5 (Europe PMC PMC13047044). Raw files live in
`C:\Users\bmens\NQ_local\af3-hitcall` (not in OneDrive, not in git).

What has been looked at before this file: the paper text, the sheet names and column headers,
row counts, one example row of MOESM8, and the paper's own published AUROCs. No score has been
compared against STRING by me.

## Why

A lab running a genome-wide AF3 screen (e.g. Dalia, IU Biology) needs to know which hits are real.
The paper reports AUROC 0.81 (STRING experimental >800) for size-corrected ipTM. Three things that
number may hide, each testable on public data without a GPU:

1. The truth set leaks. STRING's experimental channel imports PDB co-complexes, and AF3 was trained
   on (and templates from) the PDB up to 2021-09-30. Pairs with a solved homologous complex may be
   easy recall, not prediction.
2. The score has a per-protein background. Size correction removes a global trend. Some proteins
   may score high against everything ("sticky"); a bait-level null would remove that.
3. The screening question is per bait. A lab asks "what binds my protein?", not "rank all 113k
   pairs". Global AUROC is dominated by dense complexes (ribosome, RNAP, transporters).

## Definitions (fixed)

- **Proteins**: the 476 loci in Dataset EV1/MOESM4. **Pairs**: unordered, i != j, 113,050.
- **Truth**: STRING experimental channel matrix in MOESM7 (the paper's own benchmark, downloaded
  3/18/2025 by the authors). Primary positive = score > 800. Secondary positive = 999.
  Negatives = all other pairs (paper's convention). Sensitivity: negatives = score 0 only.
- **S0** (baseline) = the paper's size-corrected ipTM, MOESM5 `size_corrected_ipTMS`.
- **Metrics**: AUROC (for comparability), AUPRC (primary; positives are 2.3%), and per-bait:
  for each protein with >= 1 positive, rank its 475 partners; recall@5 and reciprocal rank of the
  best-ranked true partner, macro-averaged over baits.
- **Uncertainty**: pairs are not independent (they share proteins). All CIs are node bootstraps:
  resample the 476 proteins with replacement (2,000 reps), score the induced pairs. Comparisons are
  paired (same resample for both scores). Three primary tests, so a claim needs the Bonferroni
  98.3% CI on the difference to exclude 0.

## H1. The benchmark is inflated by structural precedent

**Precedent**: for each protein, RCSB sequence search (mmseqs2, E <= 1e-3, identity >= 0.25)
against polymer entities in PDB entries released on or before 2021-09-30. A pair is *precedented*
if some entry contains a match to protein A and a match to protein B in two distinct entities.
(Co-occurrence in an entry, not verified contact; stated as a limitation.)

**Test**: AUROC of S0 for precedented positives vs all negatives, minus AUROC for unprecedented
positives vs the same negatives.

- **Confirmed** if the difference >= 0.10 and the 98.3% CI excludes 0.
- **Rejected** if the CI includes 0.
- Between: reported as "direction supported, size below threshold".

Reported regardless: the number of positives without precedent, and S0's AUROC on them. That
number is the honest estimate for novel biology, which is what a phage-host screen is.

## H2. A per-protein null beats size correction alone

**Primary variant (the only one that counts)**: for protein i, over its 475 partners,
m_i = median(S0_i.), s_i = 1.4826 * MAD(S0_i.), floored at 0.25 * median_k(s_k).
z_ij = (S0_ij - m_i) / s_i. **S2_ij = (z_ij + z_ji) / 2.**

**Test**: AUPRC(S2) - AUPRC(S0), >800 positives, node bootstrap.

- **Confirmed** if the 98.3% CI excludes 0 on the positive side AND per-bait recall@5 does not get
  worse (point estimate >= S0).
- **Rejected** otherwise.

Exploratory, never claimed: APC correction (S_ij - S_i.S_.j / S_..), row/column percentile ranks,
min(z_ij, z_ji), combination with the paper's profile-correlation score.

## H3. Interface PAE beats size-corrected ipTM (local runs, MOESM8)

MOESM8 has per-sample `chain_pair_iptm` and `chain_pair_pae_min` for the paper's pool-size
experiment (pairs, 2k, 3k, 4k, 5k aa pools; ~4,500 pairs each).

**P_ij** = -(mean over the 5 samples of (pae_min[i][j] + pae_min[j][i]) / 2).
**I_ij** = mean over 5 samples of chain_pair_iptm[i][j], minus the paper's size formula
(-0.036255571 + 0.004470512 * sqrt(len_i + len_j)). Pairs in more than one pool are averaged.

**Test**: AUROC(P) - AUROC(I) per group vs STRING >800.

- **Confirmed** if P wins in >= 4 of 5 groups AND the pooled difference (groups stacked, node
  bootstrap) has a 98.3% CI excluding 0.
- **Rejected** otherwise.

## Descriptive, no hypothesis

- **D1. Bait-level FDR.** Empirical p for pair (i,j) = share of i's partners scoring >= S_ij,
  Benjamini-Hochberg within each bait. Per bait: hits at FDR 10%, and the share that are STRING
  positives. This is the number a wet lab would act on.
- **D2. Sample-level.** Across the 5 diffusion samples in MOESM8: mean vs max vs single sample.
  This connects to the benchmark-power result (confidence ranks targets, not draws).

## Stop rules

- If H1 is confirmed and H2 and H3 are rejected, the finding is "published screen accuracy
  overstates novel-interaction accuracy". That is still reportable, and nothing gets tuned to rescue
  a hypothesis.
- No new score variants get promoted to primary after seeing results. Anything found afterwards is
  labelled post hoc and needs a fresh test on held-out data (e.g. the paper's second Zenodo dataset
  or a new organism).

## Licence

The data is AlphaFold3 Server Output / AF3 Output. Non-commercial analysis only, cite
Abramson et al. 2024 and Todor et al. 2026, and no training of structure-prediction models on it.
A scoring rule fitted here is a benchmark statistic, not a structure predictor.

## Amendment 1 (2026-09-22, before any score was joined to STRING)

The RCSB search at identity >= 0.25 misses clear homologs: MG_001 (DnaN) has no hit at 0.25, but
4TR6 at 22.8% identity, E = 2e-18. AF3's template search has no identity floor. **H1 is re-run
with a sensitivity definition: E <= 1e-3, no identity floor.** The primary definition, test and
thresholds are unchanged, and the sensitivity result is reported next to it. It is not used to
rescue or replace the primary result.
