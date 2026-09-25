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

## The future PDB as truth (PREREG_FUTURE, 2026-09-23): the new result

Burke et al. froze AF2/FoldDock models and pDockQ for about 65,000 human pairs by the end of 2021.
Among never-solved pairs (no Interactome3D precedent; 3,301 pairs with a pre-2022 co-complex that
Interactome3D missed were excluded), 575 got their first PDB co-complex in 2022-2026. No model
could have seen them.

| Test (pre-registered) | Confident (pDockQ > 0.23, n = 6,621) | Low (< 0.10, n = 39,817) | Result |
|---|---|---|---|
| F1: solved after 2022 | 2.7% | 1.0% | OR **2.8** [1.9, 4.3] |
| F1b: solved, chains in direct contact | 2.5% | 0.29% | OR **8.8** [5.8, 14.1] |
| F1c: only proteins with pre-2022 structures | 3.6% | 1.6% | OR 2.3 [1.005, 4.9] (just passes) |
| F2: the frozen model's interface matches the new structure (residue F1 >= 0.5) | **81%** of 146 (median F1 0.82) | **1.8%** of 110 | +0.79 [0.72, 0.86] |

**Replicated in yeast with a different pipeline (PREREG_FUTURE_YEAST).** Humphreys et al. 2021
(RoseTTAFold + AF2, ModelArchive ma-bak-cepc, all 1,106 models): 619 had a co-complex before 2022
(excluded), 87 of the remaining 483 were first solved 2022-2026, and **75 of 84 with direct contact
had the right interface (89%, CI [0.82, 0.95], median F1 0.85)** vs 1.1% for a shifted-interface
null (99th percentile 3.6%). Circularity strata: no in-silico start recorded 89% (n = 72), <= 3 A
88% (n = 24). Two organisms, two AI pipelines, the same answer.

**Circularity check (post hoc, `posthoc_future_circularity.py`).** New structures can be built
from AlphaFold models, so F2 could be the model agreeing with itself. Entries recording no in-silico
starting model: 81% (n = 116), the same as entries that record one (80%, n = 30). Resolution <= 3.0 A:
80% (n = 54). X-ray only: 53% [0.32, 0.74] (n = 19), still far above low-confidence models (0 of 15).
Structures deposited before AF-Multimer existed: 3 confident pairs, too few to read. Recording of
starting models is incomplete, and 126 of 146 confident cases are cryo-EM, so some circularity cannot
be excluded; the X-ray subset is the most conservative estimate (about half).

**What it means.** Confident never-solved models also reach the PDB more often (F1). F1 has a caveat:
public AF predictions may steer which complexes labs choose to solve, so this is anticipation, not proof
of cause. Taken with the AUROC results, the screen's weakness on never-solved interactions is
**recall, not precision**. Most true never-solved interactions get low scores (AUROC 0.64 to 0.71). When
the model is confident about an unprecedented complex and that complex is later solved, the predicted
interface is right about 80% of the time (about half in the most conservative subset). For a lab: a
confident never-solved hit is worth a bench experiment; a low score says nothing.

Prior-art check (2026-09-23): benchmarks of AF3 on 2022-2024 PDB entries exist, and Burke et al.
validated some models orthogonally. Not found: a test of a genome-scale screen's frozen,
confidence-stratified predictions against structures solved afterwards.

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
| STRUCT | Is the never-solved deficit a readout artefact? Structure-level scores from the raw AF3 outputs (289 pools streamed from the 101 GB Zenodo archive; 22,875 pairs, 155 never-solved and 394 precedented positives; PREREG_STRUCT) | **No rescue by any score.** Never-solved AUROC: ipTM (S0) 0.727; trunk contact probability 0.655 (diff -0.07, 98.75% CI [-0.16, 0.04]); interface reproducibility over the 5 diffusion samples 0.705 (-0.02 [-0.13, 0.09]). ipSAE and LIS are **degenerate in pooled models** (inter-chain PAE is almost never under 10-12 A, so they are 0 for 99.7% of pairs), and the registered size correction then ranked the tied zeros by length (LIS 0.28): a design flaw, reported, not interpreted. ipTM remains the best readout; the information for never-solved pairs is not hiding elsewhere in the output |
| FUTURE | Did frozen 2021 human predictions anticipate 2022-26 structures? (PREREG_FUTURE) | **Yes**: see the section above. F1 OR 2.8, F1b 8.8, F2 81% vs 2% correct interfaces |
| COOP | Are AF's misses cooperative (non-autonomous) interfaces? (PREREG_COOP) | **Partial** (registered rule: both arms needed). **Arm H passes** (human, real 2022-26 structures of AF2 hits vs misses): misses have 27% of their interface also touching a third chain vs 11% for hits (+0.16, CI [0.06, 0.31]), come from larger assemblies (10.5 vs 6 entities, CI [0.5, 7]) and have far smaller pair contacts (30 vs 85 residue pairs, CI [-70, -38]). **Arm P fails** (M. genitalium pools): a shared STRING partner in the pool does not lift a never-solved pair's score (-0.004, CI [-0.015, 0.002]). Reading: the misses are small, non-autonomous contacts inside big assemblies; pooled AF3 does not recover them just by having a complex partner in the pool |
| COMPOSE | Can misses be recovered by composing A-C and B-C models on a shared partner C? (PREREG_COMPOSE) | **Not shown, and the method failed its sanity arm**: 1 of 13 misses rescued (p = 0.5); on hits, composition was right 9 of 24 times vs 17 of 24 for AF's pairwise models, with clashes in 31-55% of composites and C superposition RMSDs up to 30 A. Rigid single-partner composition is too crude to test the concept; uninformative, not evidence against non-autonomy |
| FUTURE-Y | Yeast replication (Humphreys 2021, RoseTTAFold+AF2) | **Replicates**: 89% correct interfaces [0.82, 0.95], n = 84, null 1% |
| RESCUE (interim, 10 of 20 registered pairs) | Causal test: AF3 on AF's misses alone, + real bridging subunit(s), + non-bridging subunit (PREREG_RESCUE) | **Interim only, verdict waits for n = 20.** Interface correct: pair 3/10, control 4/10, **bridge 6/10**; mean A-B ipTM 0.29 / 0.29 / **0.38**. Bridge fixed 3 pairs and broke none (p = 0.125); vs control 2-0 (p = 0.25). Cleanest cases: ATP5PF-ATP5PO F1 0.00 -> 0.53 (ipTM 0.05 -> 0.38, control 0.00) and TULP3-IFT140 0.12 -> 0.70 (control 0.00). Caveat: in the proteasome pair the non-bridging control also rescued. AF3 alone already gets 3/10 of AF2's misses |
| VERIFY V1-V3 | Trying to break FUTURE (PREREG_VERIFY) | **Survives.** V1 homolog precedent (pre-2022 co-complex of homologs, RCSB E <= 1e-3, id >= 0.25): human confident pairs with NO homolog precedent are right **81% (n = 114, CI [0.73, 0.88])**, same as precedented ones (81%, n = 32); yeast novel 92% (n = 61, CI [0.84, 0.98]); same at identity >= 0 (remote homologs). Search controls: every precedent hit predates 2022; without the date filter the search finds each pair's own reference entry. V2 shift null: 2% (p99 4%) vs 81% observed. V3 entry-cluster bootstrap: CIs unchanged (human [0.75, 0.87], yeast [0.82, 0.95]) |
| VERIFY V4-V5 | Independent metric from raw coordinates + threshold grid (PREREG_VERIFY) | **Survives.** Residue-pair Fnat >= 0.3 recomputed from re-downloaded model and reference coordinates (340/340 pairs mapped): human confident 80% [0.74, 0.87], novel-only 80% [0.72, 0.87]; low 2%; yeast confident 87%, novel-only 90% [0.82, 0.97]. Agrees with the F1 rule on 96-98% of pairs; the recomputed set F1 reproduces 0.808 exactly. V5 grid (human confident): 57% at the strictest (6 A, F1 >= 0.7) to 88% at the loosest (10 A, F1 >= 0.3); 81% at the registered 8 A / 0.5 |
| XLVAL | New M. genitalium complexes supported by AF3 + in-cell crosslinks? (PREREG_XLVAL; CA coordinates for all 2,033 pools streamed from Zenodo) | **Test discriminates** (controls 0/20 supported, mean 5% of links within 30 A). Candidates: 6/10 testable supported, but all are known or published architectures (GatC-ECF pairs = Todor; Opp; ABC ATPase pairs; PstA-PstS) except a minor assignment, **MG121 as the permease partner of the MG119 sugar ABC transporter** (3/3 links ~15 A; neighbouring genes). **The two genuinely new candidates did not stand: RNase J-MG423 (membrane-anchored RNase J paralog) NOT supported** (1/3 links within reach; 51 and 63 A), and **MG241-MG242 untestable** (its 3 links' peptides could not be located). No validated new biology from this round |
| XLVAL post hoc (Amendment 2) | Same test after fixing corrupted residues in the crosslink study's FASTA (current UniProt sequences; 580 vs 327 usable links) | Controls still 0/20. **MG241-MG242 supported** (3/3 links 11.9-16.0 A; all from MG241 K35). RNase J-MG423 2/4 (just meets the rule) |
| XLDSS | Independent replication with the in-cell **DSS** dataset (PXD017695), pre-registered before viewing it | Controls 0/20 (mean 3%). **RNase J-MG423 supported 3/4** (21.3, 15.7, 16.3 A vs null p95 0.35); the two near links (MG139 K120 to MG423 502 and 546) are the **same residue pairs** seen with DSSO; the far links also replicate (MG139 225/228/257 to MG423 224, 51-63 A in the dimer model), pointing to a higher-order assembly. MG241-MG242: 1 DSS link, 14.3 A, consistent but a single link cannot beat the null (P1 not met). **RNase J-MG423 is supported in both crosslinker datasets** (DSSO only after the post hoc fix) |
| TETRA | Is Mycoplasma RNase J an (MG139-MG423)x2 heterotetramer? (PREREG_TETRA) | **Supported on the B. subtilis J1 tetramer template 3ZQ4**: all 6 distinct in-cell links (DSSO + DSS) within 30 A in 5/5 AF3 samples; the far links fall from 51-63 A (dimer) to 12.5-15 A across copies; random-lysine null 95th pct 0.33; 1-7 minor clashes. 8CGL ambiguous (2/5); 4 templates untestable (2 chains). Write-up and model: `new_biology/RNASEJ_MG423.md`. Prior art: B. subtilis J1-J2 heterocomplex (Mathy 2010; Stahl 2024, 9A5V); new here is MG423 as Mycoplasma's J2-type partner and the heterotetramer. The predicted MG423 transmembrane anchor was checked and **retracted** (it is the catalytic core) |
| AFJ | Dedicated AF3 runs of RNase J : MG423 (PREREG_AFJ) | **All 4 outcomes pass; computationally solved.** M. pneumoniae (RNase J : P75174)x2 ipTM 0.83-0.84, all 6 in-cell crosslinks within 30 A in 5/5 samples; M. genitalium the same (0.82, 5/5); heterodimer satisfies only the near links (far 51-63 A); decoy RNase J : PtsI ipTM 0.12-0.17. RNase J : RNase J ipTM 0.50 alone vs 0.81 with MG423 |
| ESSENTIAL + SEC | Independent published evidence for the RNase J : MG423 complex (Lluch-Senar 2015) | **Both subunits essential in M. pneumoniae**: MPN280 E/E, MPN621 E/E **and E by colony isolation**, 0 transposon insertions each; MPN621 is annotated there as "probably non-catalytic". Species caveat: MG_423 is **NE** in M. genitalium. **SEC-MS**: both peak in the same 297.8 kDa fraction (4.7x monomer), excluding the 127 kDa heterodimer and consistent with the 254 kDa 2:2 model; only 5% of 437 proteins peak there; profile r = 0.947 (97.7th pct, not top) |
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

## Prior-art check (2026-09-22, updated 2026-09-23)

- Interface-restricted scores exist: ipSAE (Dunbrack 2025), LIS (Kim et al. 2024), and a PAE-derived
  contact-probability score, Pinc (Badonyi 2026, Protein Science). None was evaluated split by
  structural precedent in a genome-wide screen. Our STRUCT test shows the PAE-cutoff scores collapse
  to zero in 13-protein pools.


- The paper's peer-review file (supplement MOESM3, 3 reviewers) covers size bias, other ipTM
  corrections, binding affinity and methods detail. It does **not** raise the pool-size section
  confound (PH2) or benchmark dependence on PDB precedent (H1, XL, TIME).
- Known in the literature: AF structure accuracy depends on training-set analogues, and one 2025
  preprint reports an AF3 post-cutoff decline in drug-discovery settings. Not found: a
  precedent-stratified evaluation of a genome-wide PPI *screen*, an in-cell XL-MS truth test of one,
  or a time split in the screening setting. Re-check before posting anything.
