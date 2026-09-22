# Results: what a genome-wide AlphaFold3 screen can and cannot find

Data: Todor et al. 2026 (pooled-AF3, *M. genitalium*, all 113,050 pairs) re-analysed, plus
O'Reilly et al. 2020 in-cell crosslinking MS (*M. pneumoniae*, PRIDE PXD017711) as a truth set
independent of the PDB. No GPU was used. Every test was pre-registered and committed before the
join (see `git log`), except the analyses marked POST HOC.

The reproduction is exact: size-corrected ipTM AUROC is 0.806 (STRING > 800) and 0.877 (= 999),
matching the paper.

## Headline

**The screen is excellent at finding stable complexes of the kind that get solved, and close to
chance on interactions that have never been solved.** The published 0.81 averages the two.

| Truth set | Co-complex in PDB before AF3 cutoff | Never solved |
|---|---|---|
| STRING experimental > 800 | **0.85** (n = 1,806) | **0.71** (n = 827) |
| In-cell crosslinks (5% FDR) | **0.95** (n = 65) | **0.57** (n = 171) |

AUROC of size-corrected ipTM against all negatives. H1 is confirmed: the gap is +0.145, with a
Bonferroni 98.3% CI of [0.066, 0.242]. On crosslinks the gap is +0.378, 95% CI [0.27, 0.48].

## What was tested

| # | Hypothesis | Verdict |
|---|---|---|
| H1 | Benchmark inflated by structural precedent | **Confirmed**, both precedent definitions |
| H2 | Per-protein null (robust row/column z) beats size correction | **Rejected**: AUPRC 0.111 -> 0.099, CI below 0 |
| H3 | Interface PAE (pae_min) beats size-corrected ipTM | **Rejected**: +0.006, CI [-0.012, 0.023]; wins 3 of 5 |
| XL | H1 gap survives an independent, non-PDB truth set | **Confirmed (model, not labels)**: 0.95 vs 0.57 |
| BSU | Replicates in *B. subtilis* with AlphaFold-Multimer (PREREG_BSU) | **Replicates** under the registered rule: crosslinked pairs reach ipTM >= 0.5 at 53% with precedent vs 21% without, +0.32, CI [0.08, 0.55]. Under the corrected strict rule: +0.23, CI [-0.02, 0.47], same direction but borderline. No-date sensitivity: 40% vs 12%, +0.28, CI [0.08, 0.47] |
| HH1 | Human interactome (AF2/FoldDock, HuRI Y2H), recall by precedent | **Replicates** (3rd organism, 3rd model): confident (pDockQ > 0.23) 75% with an Interactome3D model vs 10% without, +0.65, CI [0.60, 0.71]; at > 0.5: 61% vs 1.2% |
| HH2 | Confident models: is a never-solved model as correct as a precedented one? (crosslinks) | **Inconclusive**: 66% vs 52% of crosslinks satisfied, +0.14, CI [-0.08, 0.30], n = 192/116. Low-confidence models: 37% vs 13%, precedent better |
| TIME | Memorisation or stability? | **Stability, at the margin**: f = 0.81, CI [0.302, 1.15] vs a 0.30 bar |

**TIME in plain words.** STRING positives whose only solved complex appeared *after* AF3's
training and template cutoff (so AF3 never saw it) still score 0.81, close to seen complexes
(0.85) and far above never-solved pairs (0.65). AF3 is not just recalling the PDB; it recognises
the class of stable, obligate complexes. The crosslink version of this test is underpowered
(14 pairs).

## Post hoc (leads, not claims)

- **PH1.** Among STRING positives, pairs whose proteins are *both* structurally known but never
  solved together score 0.655, which is *worse* than pairs involving an unknown protein (0.77). The
  co-complex matters, not whether the proteins are known: +0.196, CI [0.12, 0.27].
- **PH2. The paper's pool-size figure (Fig. 3) is confounded.** Each pool size was run on a
  disjoint ~95-protein section (zero shared proteins). Against the genome-wide screen on the same
  pairs, 4k-aa pools (+0.012) and 5k-aa pools (+0.011) are indistinguishable (difference -0.001,
  CI [-0.06, 0.07]). The paper's "needs at least 5,000 aa" is not supported; 4,000 aa does as well.
  The pooling-vs-pairs benefit is real on matched pairs (pairs 0.456 vs 0.786).
- **XL robustness.** Unprecedented crosslinked pairs stay at 0.57-0.62 when requiring >= 2 or 3
  crosslinks, and when dropping the top hubs (EF-Tu, DnaK).
- **Replicates.** A second pool per pair buys +0.016 AUROC overall (CI 0.003-0.031) and +0.010 for
  never-solved positives (CI spans 0). Extra compute does not rescue the weak class.

- **Gap replicates in the paper's independent local runs** (MOESM8; each condition is its own
  protein section, so this is suggestive, not matched). Precedented vs never-solved AUROC:
  pairs 0.48 / 0.43, 3k 0.73 / 0.60, 4k 0.90 / 0.65, 5k 0.92 / 0.65. **Pooling's accuracy gain goes
  almost entirely to precedented complexes.**
- **Adjacency proxy** (never-solved pairs <= 2 genes apart, a crude obligate-partner proxy): 0.83
  vs 0.71, the direction the stability reading predicts, but n = 23 and the CI spans 0.
- **A bait's #1 hit** (post hoc, strict precedent rule). When the top-ranked partner forms a
  precedented complex (93 of 476 baits), 81% are STRING positives. When it is never-solved
  (383 baits), 10% are (29% among baits with any known partner). STRING is incomplete, so
  these are lower bounds, but for most baits the top hit is in the weak class.
- **Self-caught definition flaw.** The original precedent rule let a homomer split across several
  entities (e.g. 6OJY, a PilT4 hexamer with 5 entities) count as a co-complex for any two paralogs.
  The strict rule (each protein must match an entity the other does not) reclassifies 133 pairs,
  3 of them positives; H1 is unchanged (+0.143, 98.3% CI [0.059, 0.239]).

## Descriptive

- **D1, bait-level FDR 10%** (conservative pooled null): 71 hits over 45 baits; 32% are STRING
  positives, 14x the base rate. Hits with precedent: 60% true. Hits without: 22% true.
- **D2**: the mean of 5 diffusion samples beats the best sample in all 5 groups. This matches the
  benchmark-power result: confidence ranks targets, not draws.

## What this means for a lab running a screen (e.g. phage-host)

1. Trust hits that resemble a stable complex: they are the ones the method finds.
2. Expect a hit list for never-solved interactions to be about 1 in 5 real at a 10% nominal FDR,
   and treat a *negative* result as uninformative for transient interactions.
3. Pool at about 4,000 aa. On matched pairs that is as good as 5,000 aa (post hoc; confirm
   prospectively). This matters at IU. AF3's docs give a maximum of 4,352 tokens on an A100 40 GB,
   5,120 on 80 GB, and 1,280 on a V100 (with unified memory). Big Red 200's GPU nodes are
   4x A100 40 GB, so 5k pools do not fit there but 4k pools do. Quartz's V100s are limited to about
   1k-aa pools, and the matched-pairs data show small pools lose most of the benefit (2k pools:
   -0.14 AUROC vs the genome-wide screen on the same pairs).
4. Averaging the 5 samples is the right aggregate. Do not pick the best sample, and do not expect
   a second replicate to fix novel interactions.

## Limitations

- Precedent is co-occurrence in a PDB entry, not verified contact.
- STRING and crosslinks are both incomplete, and crosslinks include transient proximity.
- *M. pneumoniae* to *M. genitalium* mapping uses orthologs (398 loci, reciprocal best hit).
- Two organisms (*M. genitalium* with AF3, *B. subtilis* with AF-Multimer), both Firmicutes/
  Mollicutes. A gamma-proteobacterium (*Vibrio*) is the obvious next test; it is pre-registered in
  `PREREG_VIBRIO.md` and needs GPU time.
- AF3 Output Terms: non-commercial analysis only; cite Abramson et al. 2024 and Todor et al. 2026.

## Prior-art check (2026-09-22)

- The paper's peer-review file (supplement MOESM3, 3 reviewers) covers size bias, other ipTM
  corrections, binding affinity and methods detail. It does **not** raise the pool-size section
  confound (PH2) or benchmark dependence on PDB precedent (H1, XL, TIME).
- Known in the literature: AF structure accuracy depends on training-set analogues, and one 2025
  preprint reports an AF3 post-cutoff decline in drug-discovery settings. Not found: a
  precedent-stratified evaluation of a genome-wide PPI *screen*, an in-cell XL-MS truth test of one,
  or a time split in the screening setting. Re-check before posting anything.
