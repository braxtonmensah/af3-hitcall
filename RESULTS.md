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

## Descriptive

- **D1, bait-level FDR 10%** (conservative pooled null): 71 hits over 45 baits; 32% are STRING
  positives, 14x the base rate. Hits with precedent: 60% true. Hits without: 22% true.
- **D2**: the mean of 5 diffusion samples beats the best sample in all 5 groups. This matches the
  benchmark-power result: confidence ranks targets, not draws.

## What this means for a lab running a screen (e.g. phage-host)

1. Trust hits that resemble a stable complex: they are the ones the method finds.
2. Expect a hit list for never-solved interactions to be about 1 in 5 real at a 10% nominal FDR,
   and treat a *negative* result as uninformative for transient interactions.
3. Pool at about 4,000 aa. That is as good as 5,000 aa on matched pairs, and 4k-token jobs fit
   on smaller GPUs. (The token capacity per GPU still needs checking against AF3's docs before
   planning.)
4. Averaging the 5 samples is the right aggregate. Do not pick the best sample, and do not expect
   a second replicate to fix novel interactions.

## Limitations

- Precedent is co-occurrence in a PDB entry, not verified contact.
- STRING and crosslinks are both incomplete, and crosslinks include transient proximity.
- *M. pneumoniae* to *M. genitalium* mapping uses orthologs (398 loci, reciprocal best hit).
- One organism, one model (AF3). Replication in a gamma-proteobacterium (*E. coli* or *Vibrio*)
  is the obvious next test.
- AF3 Output Terms: non-commercial analysis only; cite Abramson et al. 2024 and Todor et al. 2026.
