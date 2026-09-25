# Pre-registration 31: does CODEP replicate in RNAi? (CODEP_R)

Written 2026-09-25, **before any DEMETER2 file was downloaded** and before any RNAi dependency profile
was joined to any predicted pair.

## Why

CODEP is the only non-structural validation this project has, so it carries more weight than any other
single result and deserves the hardest replication available. Two things need testing:

1. **Is the effect a CRISPR artifact?** DepMap gene effect comes from one perturbation technology
   (Cas9 knockout), one library design and one pipeline. Correlated gene-effect profiles can arise
   from shared off-target guide behaviour, copy-number artifacts, or the Chronos model itself.
2. **The CORUM split was post hoc.** CODEP's most consequential finding, that the effect holds inside
   annotated complexes (+0.0585) and vanishes outside them (+0.0047), was discovered after seeing the
   data. A post hoc split is a hypothesis, not a result. Here it is **pre-registered as a primary
   test**, which is the only way to convert it into one.

**DEMETER2 is the hardest available replication.** It is RNAi, not CRISPR: shRNA knockdown rather than
knockout, a different failure mode (seed-based off-target rather than guide cutting), different cell
line panels, different laboratories (Achilles, DRIVE, Marcotte), and it predates the CRISPR data. An
effect present in both is not an artifact of either technology.

## Data, pinned before download

- **DEMETER2 combined gene dependency scores**, `D2_combined_gene_dep_scores.csv`, figshare article
  **6025238** (DEMETER2 data, deposited 2020-04-09), file id 13515395, 160.6 MB. Rows or columns are
  genes named `SYMBOL (ENTREZ)`; the orientation is detected and recorded, not assumed.
- More negative means more dependent, as in CRISPR gene effect. No rescaling is applied.
- **Burke et al. S1** groups exactly as in CODEP.
- **CORUM 5.0 human complexes**, Zenodo `10.5281/zenodo.17419058`, for the pre-registered split.
  CODEP used Burke's pairwise CORUM column; this uses the real complex list, so a pair counts as
  CORUM-annotated if both members appear together in at least one CORUM complex.

## Design: identical to CODEP wherever possible

Groups **T** (pDockQ > 0.23, never solved), **L** (pDockQ < 0.10, never solved), **P** (pDockQ > 0.23,
precedented), defined from Burke S1 exactly as in `analysis_codep.py`. Statistic is the Pearson
correlation of the two genes' dependency profiles across shared cell lines.

Thresholds carried over unchanged from CODEP so that nothing is re-tuned:

- minimum **300** shared cell lines, dropped and counted otherwise;
- variance floor at the **25th percentile** of per-gene SD, computed within DEMETER2;
- paralog exclusion at **>= 30%** global sequence identity;
- bootstrap over **proteins**, 2,000 replicates, 95% CI, seed 31.

If DEMETER2 has fewer than 300 cell lines in total, the line minimum drops to **100** and that
substitution is reported prominently as a deviation, because it is the one threshold the smaller panel
may make impossible.

## Tests

**R0 (instrument gate, read first).** mean r in **P** minus mean r in **L**.
- Sensitive if positive with the 95% CI excluding 0.
- **If R0 fails, nothing below is interpreted.** RNAi is noisier than CRISPR and a failure here most
  likely means the panel is too small or too noisy to see complexes at all, which is a statement about
  the replication attempt, not about CODEP.

**R1 (primary replication).** mean r in **T** minus mean r in **L**.
- **Replicates** if positive with the 95% CI excluding 0.
- **Fails to replicate** if the CI includes 0.
- **Contradicts** if the CI excludes 0 in the negative direction, which would mean CODEP's D1 is
  technology-specific and the preprint must say so.

**R2 (the pre-registered CORUM split, the one that matters).** R1 computed separately within
CORUM-annotated pairs and within non-CORUM pairs.
- CODEP's post hoc finding predicts: **positive with CI excluding 0 inside CORUM, and a CI including 0
  outside CORUM.**
- **Confirmed** only if both halves come out that way. If the non-CORUM half is positive and clears
  zero here, then CODEP's post hoc split was noise and **the preprint must drop the claim that the
  effect is confined to annotated complexes.**

**R3 (essentiality-matched, as CODEP's C1).** Quintiles of `min(mean dependency)`, pooled
sample-size-weighted difference with bootstrap CI.

## Consequences fixed in advance

- R1 replicates and R2 confirms: CODEP's finding, including the limit it places on the registry, is
  stated in the preprint as replicated across two perturbation technologies. This is the strongest
  form the claim can take.
- R1 replicates and R2 does not: the functional validation stands and **the CORUM confinement is
  retracted**, which would make the registry look better, and that is precisely why it is written down
  before the result.
- R1 fails while R0 passes: CODEP is reported as **not replicated in RNAi** in `RESULTS.md`, `STATE.md`
  and the preprint, next to the original result, with no attempt to explain it away.

## Limitations, stated before the result

- RNAi knockdown is partial and seed effects are pervasive, so DEMETER2 is noisier than CRISPR. A
  smaller effect here is expected even if the biology is identical, and R1 tests direction and
  significance rather than effect size equality.
- DEMETER2's cell line panel overlaps DepMap's, so the two datasets are not fully independent in
  samples even though they are independent in technology. The overlap is reported.
- DEMETER2 is from 2018-2020 and its gene set is smaller, so some pairs testable in CODEP will be
  untestable here. Counts are reported at every step.
