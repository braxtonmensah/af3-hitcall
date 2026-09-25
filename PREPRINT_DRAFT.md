# Confident AlphaFold predictions of never-solved protein complexes are usually correct, and reveal an essential heterotetrameric RNase J in *Mycoplasma*

**Braxton Mensah**
Indiana University Bloomington
*Correspondence:* bsmensah@iu.edu

**DRAFT — not posted. Every number traces to `RESULTS.md` and is reproducible from the repository.**

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
2022-2026. Their interfaces were correct in **81% of 146 human cases** and **89% of 84 yeast cases**,
against **2%** for low-confidence predictions. The result survived removal of all homologous structural
precedent (81% and 92%), a shuffled-interface null (2%), an entry-level cluster bootstrap, an
independent contact-based metric, and a grid of distance and correctness thresholds. Missed
interactions were instead small, non-autonomous contacts inside large assemblies.

Applying this to *Mycoplasma*, we identify a previously undescribed architecture: the essential
ribonuclease RNase J and the essential, catalytically dead paralog MPN621/MG423 form a 2:2
heterotetramer. Five independent lines agree, and only the tetramer accounts for all six in-cell
crosslinks. The complex is a candidate antibacterial target whose interface is poorly conserved in the
closest human relative.

---

## Introduction

*(To write: AlphaFold and complex prediction; genome-scale screens; the triage problem; that reported
benchmark numbers are aggregate; what a prospective test adds.)*

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

### Confident predictions of never-solved complexes are usually right

| Test | Confident | Low confidence |
|---|---|---|
| Human, interface correct (F1 >= 0.5) | **81%** (n = 146) | 2% (n = 110) |
| Yeast, interface correct | **89%** (n = 84) | shuffled null 1% |
| Human, solved at all after 2022 | 2.7% | 1.0% (OR 2.8 [1.9, 4.3]) |
| Human, solved with direct contact | 2.5% | 0.29% (OR 8.8 [5.8, 14.1]) |

Stable across release cohorts (80% for 2022-23, 82% for 2024-26).

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

### An essential heterotetrameric RNase J in *Mycoplasma*

| Evidence | Result |
|---|---|
| Pooled AF3 screen | size-corrected ipTM 0.65, top 0.1% of 113,050 pairs, never solved |
| Dedicated AF3, (RNase J)2(MPN621)2 | ipTM 0.84; **6/6 in-cell crosslinks within 30 A in 5/5 samples** |
| Heterodimer only | 3 near links satisfied, 3 far links at 51-63 A |
| Specificity control | RNase J + length-matched PtsI: ipTM 0.12-0.17 |
| Crosslinks, two chemistries | DSSO and DSS agree, same residue pairs |
| SEC-MS (published) | both peak at 297.8 kDa = 4.7x monomer; excludes 127 kDa 1:1, fits 254 kDa 2:2; 5% of 437 proteins peak there |
| Essentiality (published) | MPN280 **E/E**; MPN621 **E/E and E by colony isolation** |
| Catalytic residues | RNase J 4/4 retained; MPN621 **0/4** |
| Architecture | 178 contacts per heterodimer vs 7-9 across; J-J 60, partner-partner 64 |
| Human off-target | interface 24.6% identical to CPSF73 (which retains 3/4 catalytic residues) |

MPN621 keeps the fold and loses the chemistry, and removing RNase J's partner drops RNase J
self-association from ipTM 0.81 to 0.50, consistent with a structural subunit.

## Discussion

*(To write: recall not precision; implications for screen design and for benchmark reporting; the
interface as an antibacterial target and why interface-directed beats active-site given CPSF73;
limitations.)*

## Limitations

- Correctness is measured only on pairs that were subsequently solved; solvable complexes may be easier.
- Most 2022-26 structures are cryo-EM and some are built with AlphaFold assistance. The X-ray-only
  subset gives 53%, the conservative bound.
- Public predictions may influence which complexes labs choose to solve, so the "solved more often"
  result is anticipation, not proof of cause.
- **MG423 is non-essential in *M. genitalium*** though essential in *M. pneumoniae*; the target argument
  applies to *M. pneumoniae*.
- The RNase J complex is computational plus published orthogonal data. No new experiment was performed.

## Prior work, stated precisely

- The RNase J : MPN621 interaction is present, undiscussed, in O'Reilly et al. 2020's own PPI table
  (5% PPI FDR).
- That MG423 is an RNase J paralog possibly inactive was noted by Chilamakuri et al. 2011 in one
  sentence, and MPN621 is annotated "probably non-catalytic" by Lluch-Senar et al. 2015.
- *B. subtilis* RNase J1-J2 is a known heterocomplex (Mathy et al. 2010), modelled from crosslinks plus
  deep learning by Stahl et al. 2024 (PDB-IHM 9A5V).
- **New here:** the prospective precision result; the non-autonomy explanation; and for RNase J, the 2:2
  architecture, the crosslink-validated model, measured loss of all four catalytic residues, the
  SEC-based stoichiometry argument, and the interface map.

## Methods

*(To write from the scripts, which are the authoritative record: `analysis_future.py`,
`analysis_future_yeast.py`, `verify_v1.py`, `verify_v4.py`, `analysis_coop.py`, `analysis_xlval.py`,
`analysis_tetra.py`, `rnasej/score_afj.py`, `rnasej/interface_map.py`, `rnasej/sec_coelution.py`.)*

## Data and code availability

Repository with all pre-registrations, analysis code and results: [URL once public]. All input data are
public: Todor et al. 2026 (Zenodo 15499631), Burke et al. 2023, Humphreys et al. 2021 (ModelArchive
ma-bak-cepc), O'Reilly et al. 2020 (PRIDE PXD017711, PXD017695, CC0), Lluch-Senar et al. 2015, RCSB PDB,
SIFTS, UniProt.

**AlphaFold Server output is used here under its Output Terms, which permit scientific publication and
forbid commercial use.**

## Pre-registration statement

Twenty-one hypotheses were pre-registered and committed to version control before the corresponding data
were joined; `git log` preserves the order. Eight returned negative or inconclusive results and are
reported: per-protein normalisation, interface PAE, pool context, structure-level rescue scores,
disease-variant enrichment (twice), literature labels, rigid composition, and pooled shared partners.
Post hoc analyses are labelled as such.
