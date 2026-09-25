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


---

# OUTCOME, recorded 2026-09-25: CODEP DOES NOT REPLICATE IN RNAi

**R0 gate PASSES. R1 fails to replicate. R2 is moot because neither half holds.**

| Test | DEMETER2 RNAi | CODEP CRISPR |
|---|---|---|
| Gate (known complexes vs low-confidence) | **+0.0486, CI [0.0287, 0.0703]** | +0.1034, CI [0.0784, 0.1301] |
| Primary (confident never-solved vs low-confidence) | **-0.0042, CI [-0.0129, 0.0047]** | +0.0203, CI [0.0098, 0.0317] |
| CORUM half | -0.0021, CI [-0.0309, 0.0279], does not hold | +0.0585, holds |
| non-CORUM half | -0.0009, CI [-0.0072, 0.0055], does not hold | +0.0047, does not hold |

699 cell lines, 17,309 genes, T = 2,708, L = 16,289, P = 849. No threshold was changed: the 300-line
minimum was met, so the registered deviation clause was not used.

## This is not an underpowering excuse, and that was checked

The obvious defence is that RNAi is noisier. The gates measure exactly that: RNAi's instrument reads
**0.47x** the CRISPR instrument (+0.0486 against +0.1034). A true CRISPR effect of +0.0203 therefore
scales to an expected RNAi effect of about **+0.0095**. The observed RNAi interval's **upper** bound is
**+0.0047**, which is below that expectation. So the scaled-down effect is excluded by the data, and
the point estimate is negative rather than small-and-positive. Low power does not account for this.

## What this means, stated as the pre-registration requires

**The claim that confident never-solved AlphaFold predictions are functionally coupled is not
established.** It was seen in CRISPR and not in RNAi, with a sensitive instrument in both. Per the
consequence written above, CODEP is reported as **not replicated** in `RESULTS.md`, `STATE.md` and the
preprint, beside the original result, with no attempt to explain it away.

What survives is only this: **known complexes are detectably co-dependent in both technologies.** That
is a property of the instruments, not a finding about AlphaFold, and it licenses nothing about the
registry.

**The CORUM-confinement finding is also unsupported.** It was post hoc in CODEP and it did not
reproduce here in either direction, so it should not be cited either.

## Candidate explanations, all speculative and none load-bearing

Offered only so the next person does not have to re-derive them, and none of them rescues the result:
a CRISPR-specific artifact (copy-number effects, guide off-target behaviour, or the Chronos model)
could produce correlated gene effect between the kind of well-modelled, well-studied genes that score
high pDockQ; DEMETER2's panel and gene set differ; RNAi knockdown is partial and measures a different
kind of perturbation. **None of these was tested. The honest position is that the effect did not
replicate and the reason is unknown.**

## BRIDGE is not settled by this

`PREREG_BRIDGE` does not depend on D1. It rests on a different claim, that the *local* neighbourhood
of a pair with independent physical support contains its missing subunit, and it has its own gate and
control arm. This result lowers the prior on co-dependency carrying structural information at all, and
that should be said when BRIDGE is run, but BRIDGE tests it directly rather than assuming it.
