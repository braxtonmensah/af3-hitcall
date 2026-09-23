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
| Human HuRI Y2H vs random (AF2/FoldDock, Burke 2023) | **0.92** (n = 1,782) | **0.64** (n = 53,804) |

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
| HH3 | Human, AUROC form vs 1,849 random pairs | **Replicates**: precedented 0.917 vs never-solved 0.636, +0.28, CI [0.27, 0.29] |
| HH2 | Confident models: is a never-solved model as correct as a precedented one? (crosslinks) | **Inconclusive**: 66% vs 52% of crosslinks satisfied, +0.14, CI [-0.08, 0.30], n = 192/116. Low-confidence models: 37% vs 13%, precedent better |
| CLINVAR | Pathogenic vs benign enrichment at predicted interfaces (PREREG_CLINVAR) | **Test failed its positive control**: precedented interfaces OR 0.70 [0.48, 1.04]. Not sensitive, so no conclusion about novel interfaces. Likely cause: interface vs whole-protein comparison is dominated by core burial (pathogenic variants favour cores); the control group had too few ordered interface residues (28 variants). 37,215/37,215 variant wild-types matched the models |
| CLINVAR2 | Surface-matched pathogenic vs benign enrichment (PREREG_CLINVAR2) | **Positive control failed narrowly again**: precedented OR 1.31 [0.93, 1.83]. Not interpreted per prereg. (Descriptive only, no claim: novel OR 1.69 [1.32, 2.16], control 0.65 [0.14, 1.77].) Two attempts, both reported |
| LITJEV | Does AF2 confidence predict literature-confirmed binding in never-solved human pairs? (Jev judge, 2,900 abstracts, $0.78) | **No signal, but underpowered (floor effect)**: lit-direct rate 0.8% confident vs 0.5% low (L1 diff +0.004, CI [-0.010, 0.020]); even precedented reference only 1.8%. Symbol co-mentions are mostly high-throughput papers; the design cannot detect anything. Uninformative |
| CLINVAR2 | Same question, surface-matched (interface vs other surface residues; PREREG_CLINVAR2) | **Positive control failed again**: precedented OR 1.31, CI [0.93, 1.83] (right direction now, v1 was 0.70, but the CI includes 1). Stopped per prereg. Novel OR 1.69 [1.32, 2.16] is reported but **not interpreted**: after two attempts and a failed control it cannot be claimed. Control group had 15 interface variants, too few to mean anything. 13,359/13,359 wild-types matched. The disease-variant route is closed |
| LITJEV | Literature truth via Jev: are confident never-solved human models more often reported as direct binders? (PREREG_LITJEV) | **No signal, and the instrument is insensitive**: L1 (co-mentioned pairs) +0.004, CI [-0.010, 0.020]; L2 (all) +0.003, CI [-0.006, 0.011]. Only 5 of 850 pairs got a direct-binding label, and even the precedented reference reached just 1.8% of co-mentioned pairs, so this says nothing either way. Co-mention itself: 70% confident vs 61% low vs 74% precedented (descriptive; confounded by how well-studied the proteins are) |
| CONTEXT | Is pooled AF3 a competition assay? Same pair folded with vs without a strong third-party binder in the pool (natural experiment, 6,016 pairs; PREREG_CONTEXT) | **No context effect**: positives +0.008, CI [-0.005, 0.024]; never-solved +0.001 [-0.029, 0.031]; competitor defined from other pools -0.005 [-0.025, 0.014]. A clean-pool score does not rescue never-solved pairs (AUROC -0.001, CI [-0.005, 0.002]). Pair predictions are context-independent, so pool composition is not a source of false negatives |
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
