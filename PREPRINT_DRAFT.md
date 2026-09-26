# Time-split assessment of predicted protein-complex interfaces and a 2:2 RNase J assembly hypothesis in *Mycoplasma*

**Braxton Mensah**
Indiana University Bloomington
*Correspondence:* bsmensah@iu.edu

Every number traces to `RESULTS.md` in the repository and is reproducible from it.

*Funding:* This work received no external funding.
*Competing interests:* The author declares no competing interests.

---

## Abstract

Genome-scale AI structure prediction now proposes protein interactions faster than experiments can test
them, and users cannot tell which proposals deserve bench time. Re-analysing a pooled AlphaFold3 screen
of all 113,050 protein pairs in *Mycoplasma genitalium*, we show its reported accuracy averages two
different populations: pairs with a solved co-complex score AUROC 0.85, while never-solved pairs score
0.71, and on in-cell crosslinks the split is 0.95 versus 0.57. The same split appears in *Bacillus
subtilis* with AlphaFold-Multimer and in the human interactome with AlphaFold2.

We then asked whether the weak class is weak in precision or only in recall. Using predictions frozen
before the answers existed, we scored confident never-solved predictions against complexes released in
2022-2026. Among pairs subsequently solved, their interfaces were correct in **81% of 146 human cases** and **89% of 84 yeast cases**,
against **2%** for low-confidence predictions. The result survived removal of all homologous structural
precedent (81% and 92%), a shuffled-interface null (2%), an entry-level cluster bootstrap, an
independent contact-based metric, and a grid of distance and correctness thresholds. Missed
interactions were instead small, non-autonomous contacts inside large assemblies.

Applying this to *Mycoplasma*, we evaluate a 2:2 assembly hypothesis for RNase J and its partner
MPN621/MG423, whose interaction and paralog relationship were previously described. The predicted
assembly is consistent with published crosslinks and co-elution; the tested 1:1 model does not
account for all six crosslinks. Neither 2:2 stoichiometry nor catalytic inactivity has been directly
measured here. We then measured whether the interface is a plausible small-molecule site and found that
it is not: its largest non-catalytic cavity is 26 and 27 A^3 across the two ortholog models, against
76 A^3 for the shallowest drugged reference in our calibration set, so the surface is large and flat.
The assembly hypothesis merits an experimental stoichiometry test; the interface is not an
antibacterial target.

---

## Introduction

Accurate structure prediction has moved from single chains to complexes, and from individual targets to
whole proteomes. Pooled screens now evaluate every possible protein pair in an organism, tens or hundreds
of thousands of predictions at a time, and report ranked lists of candidate interactions. The bottleneck
has moved accordingly. It is no longer generating hypotheses, it is deciding which of them is worth an
experiment.

That decision rests on the confidence scores the models emit, and on benchmark numbers reported as a
single figure of merit. A screen that reports AUROC 0.81 against a reference interaction set invites the
reading that any given confident prediction has a correspondingly good chance of being real. This
reading is what a triage decision actually depends on, and it is not what the number measures.

The difficulty is that the evaluated population is not homogeneous. Some protein pairs already have a
solved co-complex, often one present in the model's training data. Others have never been solved in
complex by any method. These are not equally hard, and they are not equally interesting. A screen's
purpose is to say something about the second class, because the first class is already known. An
aggregate score computed over both is dominated by whichever class is larger, and tells the user little
about the predictions they would actually act on.

Separating the two classes retrospectively runs into circularity. Any pair used to measure accuracy must
have been solved to serve as ground truth, so the never-solved class is, by construction, the class for
which no contemporaneous ground truth exists. The natural resolution is to wait. Predictions made and
published before a structure existed can be scored against that structure once it appears, and the
ordering of events is externally verifiable from deposition dates rather than asserted by the analyst.

Here we take that approach. We first show that the aggregate accuracy of a genome-wide screen averages
two populations that differ substantially, and that the split reproduces across three organisms, three
prediction systems and two independent notions of ground truth. We then measure interface correctness
for never-solved pairs that received structures later, using models frozen before those answers
existed. Confident predictions often match that selected set of later structures. Misses are associated
with smaller, more assembly-dependent interfaces. Finally, we examine a predicted RNase J assembly in
*Mycoplasma* against previously published experimental evidence and state what remains unmeasured.

## Results

### The published accuracy of a genome-wide screen averages two populations

Our reproduction is exact: size-corrected ipTM gives AUROC 0.806 against STRING experimental > 800 and
0.877 against = 999. Splitting positives by whether a co-complex was in the PDB before AlphaFold3's
cutoff gives 0.85 (n = 1,806) versus 0.71 (n = 827), a gap of +0.145 with a Bonferroni 98.3% CI of
[0.066, 0.242]. Against in-cell crosslinks, a truth set independent of the PDB, the gap widens to 0.95
(n = 65) versus 0.57 (n = 171), +0.378 [0.27, 0.48]. It replicates in *B. subtilis* with
AlphaFold-Multimer and in human HuRI pairs with AlphaFold2 (0.917 vs 0.636, +0.28 [0.27, 0.29]).

A time split shows this is not memorisation: complexes first solved *after* the training cutoff still
score 0.81, close to seen complexes and far above never-solved pairs.

### Confident predictions among later-solved complexes often have the right interface

| Test | Confident | Low confidence |
|---|---|---|
| Human, interface correct (F1 >= 0.5) | **81%** (n = 146) | 2% (n = 110) |
| Yeast, interface correct | **89%** (n = 84) | shuffled null 1% |
| Human, solved at all after 2022 | 2.7% | 1.0% (OR 2.8 [1.9, 4.3]) |
| Human, solved with direct contact | 2.5% | 0.29% (OR 8.8 [5.8, 14.1]) |

Stable across release cohorts (80% for 2022-23, 82% for 2024-26).
The interface fractions are conditional on subsequent structure solving, a selected subset of all
unsolved pairs. They are not calibrated interaction probabilities for the remaining unsolved pairs.

### The result survives every attack we designed

| Threat | Check | Result |
|---|---|---|
| Homologous precedent | No pre-2022 homologous co-complex | Human 81% [0.73, 0.88] (n = 114); yeast 92% [0.84, 0.98] |
| Trivially easy | Interfaces shifted to random positions | 2% human, 1% yeast |
| Pairs not independent | Entry-level cluster bootstrap | CIs unchanged |
| Flattering metric | Residue-pair Fnat from raw coordinates, separate code | 80% human, 87-90% yeast; 96-98% agreement |
| Threshold choice | 6/8/10 A x F1 0.3/0.5/0.7 | 57% to 88%; 81% at the registered setting |
| Circularity (models built from AlphaFold) | Entries with no in-silico starting model | 81% human, 89% yeast; X-ray only 53% (n = 19) |

### What the screens miss is non-autonomous contacts

Comparing real structures of hits and misses: misses have 27% of their interface also touching a third
chain versus 11% for hits (+0.16 [0.06, 0.31]), come from larger assemblies (10.5 vs 6 entities), and
have interfaces one third the size (30 vs 85 residue-pair contacts). Pool composition, shared partners,
interface-restricted confidence scores (ipSAE, LIS), trunk contact probabilities and sample
reproducibility all failed to recover them, so the information is not elsewhere in the output.

### A 2:2 RNase J assembly hypothesis in *Mycoplasma*

| Evidence | Result |
|---|---|
| Pooled AF3 screen | size-corrected ipTM 0.65, top 0.1% of 113,050 pairs, never solved |
| Dedicated AF3, (RNase J)2(MPN621)2 | ipTM 0.84; **6/6 in-cell crosslinks within 30 A in 5/5 samples** |
| Heterodimer only | 3 near links satisfied, 3 far links at 51-63 A |
| Specificity control | RNase J + length-matched PtsI: ipTM 0.12-0.17 |
| Crosslinks, two chemistries | DSSO and DSS agree, same residue pairs |
| SEC-MS (published) | both peak at apparent mass 297.8 kDa = 4.7x monomer; favors a larger assembly over 1:1, but does not alone establish 2:2; 5% of 437 proteins peak there |
| Essentiality (published) | MPN280 **E/E**; MPN621 **E/E and E by colony isolation** |
| Catalytic residues | RNase J 4/4 retained; MPN621 **0/4** |
| Architecture | 178 contacts per heterodimer vs 7-9 across; J-J 60, partner-partner 64 |
| Human off-target | interface 24.6% identical to CPSF73 (which retains 3/4 catalytic residues) |

MPN621 retains the fold but lacks four aligned catalytic residues. Activity has not been assayed here.
Changing chain composition drops predicted RNase J self-association confidence from ipTM 0.81 to
0.50, which motivates a structural-role hypothesis but does not measure cellular stabilization.

## Discussion

The central result is a reframing. On never-solved pairs, a genome-wide screen scores AUROC 0.71
against STRING and 0.57 against crosslinks. In our later-solved subset, confident predictions have
the right interface in 81% of human cases and 89% of yeast cases, against 2% for low-confidence human
predictions. This supports a useful triage signal in that selected subset. It does not establish the
precision of the screen over all unsolved pairs, because subsequent structure solving is selective.

This distinction changes how a screen should be used. Ranking metrics reward recovering as many true
positives as possible, which is the right objective when the output is a ranked list to be read in full.
It is the wrong objective when the output is a shortlist for experiments, where the cost of a false
positive is a wasted assay and the cost of a false negative is an opportunity that was never visible in
the first place. The time-split evidence supports considering confident never-solved predictions for
bench follow-up alongside independent evidence and experimental cost. Prospective validation on an
unselected set is still needed before treating confidence as the probability of a cellular interaction.

It also changes how these systems should be benchmarked. Reporting one accuracy figure over a mixed
population can overstate performance on the class users care about and obscure a useful signal within
the later-solved subset. We would
argue for stratifying by structural precedent as a default in this literature, because the split we find
is large, it is consistent across systems, and it is invisible in the pooled statistic.

What the screens miss has a structural explanation rather than a scoring one. Missed interactions have
roughly one third the interface area of recovered ones, 30 versus 85 residue-pair contacts, come from
larger assemblies, and are substantially more likely to have their interface also contacting a third
chain. These are non-autonomous contacts, interfaces that do not form in isolation because they are
stabilised by the rest of the assembly. Asking a pairwise predictor about them is close to ill-posed: the
question presupposes a two-body complex that does not independently exist. Consistent with that reading,
six separate attempts to recover the misses from information already in the output all failed, including
pool composition, shared partners, interface-restricted confidence scores, trunk contact probabilities
and sample reproducibility. The information is not being discarded by the scoring function, it is absent
from a pairwise calculation. That suggests the productive direction is assembly-aware prediction rather
than better post-hoc rescoring of pairwise output.

The *Mycoplasma* RNase J case illustrates how a prediction can be followed with independent evidence.
The pooled screen placed the pair in the top 0.1% of 113,050 candidates. A dedicated 2:2 prediction
reaches ipTM 0.84 and is consistent with six reported crosslinks across five model samples; the tested
1:1 pose leaves three links at 51 to 63 A. Published SEC-MS gives both proteins an apparent peak at
297.8 kDa, compatible with a larger assembly but not a direct stoichiometry measurement. The
interaction and paralog assignment had already been reported. Both subunits are essential in
*M. pneumoniae*, but that does not establish that disrupting this interface is lethal. MPN621 lacks
four aligned catalytic residues; a structural role and catalytic inactivity remain hypotheses pending
direct experiments.

**For drug discovery, we measured this interface and it is not a small-molecule target.** A buried-cavity
scan of both ortholog models, calibrated against KEAP1:p62 (575 A^3, drugged), MDM2:p53 (76 A^3, drugged
but shallow) and the c-Fos:c-Jun coiled coil (0 A^3, flat), puts the largest **non-catalytic** cavity at
the interface on the RNase J side at **26 and 27 A^3** in *M. pneumoniae* and *M. genitalium*
respectively. The interface buries 4,941 A^2 in total, which makes it a large, flat surface: the classic
undruggable case. The partner side carries a 273 A^3 cavity in one model, but that value does **not**
reproduce, measuring 82 A^3 in the ortholog, while the three other cavities we measured agree within 9%
between models. Only 28% of that cavity's lining residues are interface residues in the model where it
is largest, so it is a pocket that touches the interface rather than an interface pocket.

We report this because the opposite claim would have been the more fundable one. The one cavity in this
system that does reproduce is MPN621's own degenerate cleft (491 and 470 A^3, a ratio of 1.04), which is
not an interface site at all.

The selectivity comparisons we can make are these. The closest human relative,
CPSF73, retains three of four aligned catalytic residues, while the compared interface residues are
24.6% identical. Those comparisons neither establish selectivity nor show that the interface can be
inhibited by a compound. No antibacterial activity has been measured here.

Several limits bound these conclusions and are worth stating alongside them. Correctness can only be
measured on pairs that someone later solved, and solvable complexes may simply be easier ones, so 81% and
89% are estimates for a population that is not quite the population of interest. Many recent depositions
are cryo-EM and some were built with AlphaFold assistance; the X-ray-only subset gives 53% on 19 cases,
which we report as a smaller, more conservative subset. The RNase J assembly hypothesis rests on
computation plus published orthogonal data, and no new experiment was performed here. MG423 is
non-essential in *M. genitalium* even though MPN621 is essential in *M. pneumoniae*; target-related
inferences must therefore be species-specific.

## Limitations

- Correctness is measured only on pairs that were subsequently solved; solvable complexes may be easier.
- Most 2022-26 structures are cryo-EM and some are built with AlphaFold assistance. The X-ray-only
  subset gives 53%, the conservative bound.
- Public predictions may influence which complexes labs choose to solve, so the "solved more often"
  result is anticipation, not proof of cause.
- **MG423 is non-essential in *M. genitalium*** though MPN621 is essential in *M. pneumoniae*;
  essentiality cannot be generalized between species.
- The RNase J complex is computational plus published orthogonal data. No new experiment was performed.

## Prior work, stated precisely

- The RNase J : MPN621 interaction is present in O'Reilly et al. 2020's PPI table (5% PPI FDR),
  and the study's supplementary text discusses MPN621 as the missing RNase J paralog.
- That MG423 is an RNase J paralog possibly inactive was noted by Chilamakuri et al. 2011 in one
  sentence, and MPN621 is annotated "probably non-catalytic" by Lluch-Senar et al. 2015.
- *B. subtilis* RNase J1-J2 is a known heterocomplex (Mathy et al. 2010), modelled from crosslinks plus
  deep learning by Stahl et al. 2024 (PDB-IHM 9A5V).
- **New here:** a time-split interface-correctness estimate for later-solved pairs; analysis of missed
  contacts; and for RNase J, a computational 2:2 model consistent with published crosslinks, a
  sequence-based catalytic-residue comparison, the SEC-based stoichiometry argument, and an interface
  map. The cellular assembly and biochemical roles remain to be measured.

## Methods

The scripts named below are the authoritative record; this section describes what they do. Each
pre-registration file (`PREREG_*.md`) was committed before the corresponding data were joined, and
`git log` preserves that ordering.

**Data.** The *M. genitalium* pooled screen and its scores are from Todor et al. 2026 (Zenodo 15499631).
Frozen 2021 predictions are the Burke et al. 2023 human set and the Humphreys et al. 2021 yeast set
(ModelArchive ma-bak-cepc). In-cell crosslinks are O'Reilly et al. 2020 (PRIDE PXD017711 and PXD017695,
CC0). Essentiality and SEC-MS are from Lluch-Senar et al. 2015. Reference structures, sequence mappings
and annotations are from RCSB PDB, SIFTS and UniProt. All are public.

**Reproducing the screen and stratifying it.** `analysis_h1_h2.py` and `analysis_h3.py` recompute
size-corrected ipTM and score it against STRING experimental evidence at two thresholds, and against the
crosslink set. Positives are split by whether a co-complex for that pair existed in the PDB before the
predictor's training cutoff, giving the solved and never-solved strata. `analysis_time.py` performs the
time split that distinguishes memorisation from generalisation, scoring complexes first solved after the
cutoff separately. `analysis_bsu.py` and `analysis_human.py` repeat the stratification in *B. subtilis*
with AlphaFold-Multimer and in human HuRI pairs with AlphaFold2.

**The prospective test.** `analysis_future.py` and `analysis_future_yeast.py` implement PREREG_FUTURE.
Step A extracts direct contacts and experimental interfaces from the mmCIF of each entry released in
2022-2026, cached per entry. Step B computes anticipation odds ratios for whether a confident 2021
prediction was subsequently solved at all, and solved with direct contact. Step C scores interface
correctness of the frozen models against the later structure, with F1 >= 0.5 as the registered criterion.
Because the models were published before the reference structures were deposited, the ordering is
verifiable from deposition dates rather than asserted.

**Attacks.** Homologous precedent is removed in `bsu_precedent.py` and `pdb_precedent.py` by excluding
any pair with a pre-2022 homologous co-complex. The shuffled null relocates interfaces to random
positions of matched size. Non-independence is handled by an entry-level cluster bootstrap.
`verify_v1.py` and `verify_v4.py` implement PREREG_VERIFY, recomputing residue-pair Fnat directly from
coordinates for both models and SIFTS-mapped reference structures, in separate code from the stored
interface sets used in Step C, and sweeping a grid of distance cutoffs (6, 8, 10 A) crossed with F1
thresholds (0.3, 0.5, 0.7). Circularity from AlphaFold-assisted model building is addressed by restricting
to entries with no in-silico starting model, and separately to X-ray-only entries.

**Negative results.** The registered hypotheses below returned negative or inconclusive results and
are reported rather than dropped: per-protein normalisation and interface PAE (`posthoc.py`), pool context
(`analysis_context.py`), structure-level rescue (`analysis_struct.py`, `rescue/score_rescue.py`),
disease-variant enrichment twice (`analysis_clinvar.py`, `analysis_clinvar2.py`), literature labels
(`analysis_litjev.py`), rigid composition (`analysis_compose.py`) and pooled shared partners
(`analysis_coop.py`).

**RNase J.** `rnasej/score_afj.py` implements PREREG_AFJ, scoring dedicated AlphaFold Server predictions
of (RNase J)2(MPN621)2 against the four registered outcomes, with a length-matched PtsI decoy as the
specificity control. Crosslink satisfaction is evaluated as Ca-Ca distance below 30 A, across all five
returned samples. Note that AF Server orders chains by entity, all copies of entity 1 before entity 2,
which the scorer accounts for. `analysis_xlval.py` resolves crosslink sites against current UniProt
sequences, because the published crosslink FASTA contains corrupted residues; this raised usable links
from 327 to 580. `analysis_tetra.py` implements PREREG_TETRA, placing two copies of the heterodimer on
solved RNase J tetramer templates to test whether the far crosslinks are satisfied across copies rather
than within one. Interface contacts, catalytic-residue retention and the CPSF73 comparison are computed
in `rnasej/interface_map.py`; the SEC-MS stoichiometry argument is in `rnasej/sec_coelution.py`.

**Statistics.** `metrics.py` provides tie-aware weighted AUROC and AUPRC and the node bootstrap used
throughout. The bootstrap resamples proteins rather than pairs, so pair (i, j) carries weight c_i * c_j
where c is each protein's multiplicity in the resample; this respects the dependence induced by a protein
appearing in many pairs. Scores do not change between replicates, so each score vector is sorted once and
each replicate is a bincount over tie groups. Confidence intervals on differences between strata are
Bonferroni-corrected where multiple comparisons are reported.

## Data and code availability

Repository with all pre-registrations, analysis code and results: [URL once public]. All input data are
public: Todor et al. 2026 (Zenodo 15499631), Burke et al. 2023, Humphreys et al. 2021 (ModelArchive
ma-bak-cepc), O'Reilly et al. 2020 (PRIDE PXD017711, PXD017695, CC0), Lluch-Senar et al. 2015, RCSB PDB,
SIFTS, UniProt.

**AlphaFold Server output is used here under its Output Terms, which permit scientific publication and
forbid commercial use.**

## Pre-registration statement

Every hypothesis was pre-registered and committed to version control before the corresponding data
were joined; `git log` preserves the order. The repository holds 33 pre-registration files
(`PREREG*.md`); this paper reports the subset listed in Methods. The registered hypotheses that
returned negative or inconclusive results are named there and are reported rather than dropped:
per-protein normalisation, interface PAE, pool context, structure-level rescue scores,
disease-variant enrichment (twice), literature labels, rigid composition, and pooled shared
partners. Tests registered after this draft, including OMEGA, ASSEMBLY, ASSEMBLY2 and CODEP_R, also
returned negative or inconclusive results and are recorded in `RESULTS.md`. Post hoc analyses are
labelled as such.
