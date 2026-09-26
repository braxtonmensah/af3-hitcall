# RNase J-MG423 structural hypothesis: prior biology identified

Status: **specific, computationally supported 2:2 structural hypothesis; core biological claim already published.**
The pre-registered AF3 outcomes passed, and two crosslinker datasets from the same published study support
the modeled interface. Neither structure prediction nor those crosslinks directly measure a 2:2 complex in cells.
The 2020 study's [supplementary text, p. 12](https://pure.mpg.de/rest/items/item_3247325_3/component/file_3247344/content)
explicitly says MPN621 interacts with RNase J, identifies it as the missing paralog, and introduces that
finding by describing RNase J1/J2 as a heterotetramer in other bacteria. Thus the interaction, paralog
assignment, and implied 2:2 stoichiometry cannot be claimed as newly discovered here.

## Dedicated AlphaFold 3 runs (AlphaFold Server, 2026-09-25)

| Job | ipTM | Crosslinks within 30 A |
|---|---|---|
| *M. pneumoniae* RNase J (P75497) x2 + MG423 homolog (P75174) x2 | **0.83-0.84** (RNase J : partner 0.81-0.82) | **6/6 in 5/5 samples** (14-23 A) |
| *M. genitalium* MG139 x2 + MG423 x2 | 0.82 | 6/6 in 5/5 samples |
| Heterodimer only (P75497 + P75174) | 0.81 | 3 near links yes, 3 far links no (51-63 A), as predicted |
| Decoy: RNase J x2 + PtsI (P75168, length-matched) x2 | 0.31 overall; RNase J : decoy **0.12-0.17** | n/a |

AF3 received no crosslink information. It builds a confident heterotetramer that satisfies every in-cell
crosslink, and it does not pair RNase J confidently with an unrelated protein. The RNase J : RNase J
interface scores ipTM ~0.50 without MG423 and ~0.81 with it. This compares model confidence under
different chain compositions; it does not measure stabilization.
Models: `rnasej_mpn_2x2_AF3_model_0.cif`, `rnasej_mg_2x2_AF3_model_0.cif`. AF Server may use PDB templates up
to 2021-09-30 (e.g. B. subtilis RNase J1, 3ZQ4); the crosslinks were never an input.
Every step was pre-registered (PREREG_XLVAL, PREREG_XLDSS, PREREG_TETRA); post hoc steps are marked.

## Claim

In *Mycoplasma genitalium* (and *M. pneumoniae*), the uncharacterized protein **MG423** (UniProt P47662;
*M. pneumoniae* ortholog P75174) is the partner of the essential RNA-degrading enzyme **RNase J (MG139,
P47385)**. The two are a candidate J1/J2-type heterodimer, and the models predict that two heterodimers can
assemble into a **heterotetramer** in a dimer-of-dimers arrangement resembling the *B. subtilis* RNase J1
tetramer (3ZQ4).

## Evidence

| Line of evidence | Result |
|---|---|
| AF3 genome-wide pooled screen (Todor et al. 2026) | MG139-MG423 size-corrected ipTM 0.65, top 0.1% of 113,050 pairs; never solved |
| Our validation of such predictions | Not established for this candidate; do not assign an 80-90% success rate |
| In-cell crosslinks, DSSO (O'Reilly 2020, PXD017711) | 4 MG139-MG423 links; 2 within 30 A of the AF3 heterodimer interface (post hoc sequence fix) |
| In-cell crosslinks, DSS (PXD017695), second crosslinker in same study | 4 links; 3 within 30 A (null 95th pct 0.35). The two near links are the **same residue pairs** as with DSSO (MG139 K120 to MG423 502 and 546) |
| Far links, both datasets | MG139 225/228/257 to MG423 224: 51-63 A in the **AF3-predicted** 1:1 pose; this pose does not explain them |
| Heterotetramer on the 3ZQ4 template | **All 6 distinct links within 30 A in 5/5 AF3 samples** (far links 12.5-15 A across copies; random-lysine null 95th pct 0.33); 1-7 minor CA clashes. Copy placement used structural fit only, never the crosslinks |
| Controls | 0/20 crosslinked low-confidence pairs pass the same test (both datasets) |

**How many independent lines this is, stated exactly, because "five independent" overstates it.**
The five *published* lines come from **three** studies, and two pairs of them share a study:

| # | Line | Study |
|---|---|---|
| 1 | AF3 genome-wide pooled screen | Todor et al. 2026 |
| 2 | In-cell crosslinks, DSSO | O'Reilly et al. 2020 |
| 3 | In-cell crosslinks, DSS | O'Reilly et al. 2020, **same study**, second chemistry |
| 4 | Transposon essentiality | Lluch-Senar et al. 2015 |
| 5 | SEC-MS co-elution at 297.8 kDa | Lluch-Senar et al. 2015, **same study** |

Lines 2 and 3 detect **the same residue pairs** (MG139 K120 to MG423 502 and 546), so the second
chemistry rules out a crosslinker artefact rather than adding an independent observation. Lines 4 and
5 come from one paper's two supplementary tables.

So the accurate phrasing is **"five published lines from three independent studies"**, and that is
what `STATE.md` and the outreach drafts now say. Three independent studies is still strong; claiming
five independent lines was not supportable and this table is the reason.


Model: `rnaseJ_MG139_MG423_heterotetramer_CA.pdb` (MG139 = chains A, C; MG423 = chains B, D; CA only).

## Essentiality and co-elution from published data (2026-09-25)

Both from Lluch-Senar et al. 2015, *Mol Syst Biol* (PMC4332154), transposon essentiality + SEC-MS.
Independent of AlphaFold and of the crosslinks.

**Both subunits are essential in *M. pneumoniae*.** Their Table S2:

| Gene | Name / annotation | Transposon insertions | Essentiality |
|---|---|---|---|
| MPN280 | `rnjA`, Ribonuclease J1 | 0 (both thresholds) | **E** / **E** |
| MPN621 | `rnj`, **"Probably non-catalytic ribonuclease J1"** | 0 (both thresholds) | **E** / **E**, plus **E by colony isolation** |

So the catalytically dead subunit is itself essential, and it is the one with the extra
colony-isolation confirmation. An essential protein whose only apparent job is holding RNase J
together is a protein-protein-interface target by definition.
Note their annotation already says "probably non-catalytic", so that idea is prior art; our
contribution is measuring it (0 of 4 catalytic residues retained).

**Species caveat, stated plainly.** Their Table S11 compares species: MPN280/MG_139 is essential in
both, but **MG_423 is non-essential in *M. genitalium*** (E in MPN, NE in MG, citing Glass 2006).
The target-validation argument therefore holds for *M. pneumoniae*, the organism the crosslinks come
from, and not for *M. genitalium*.

**SEC-MS co-elution supports 2:2, not 1:1** (`rnasej/sec_coelution.py`). In their size-exclusion
chromatography of a cell extract, both proteins peak in the **same fraction, apparent mass 298 kDa**:

| Check | Result |
|---|---|
| Peak fraction, MPN280 and MPN621 | both 297.8 kDa |
| Monomer masses | 64 and 63 kDa, so both elute at **4.7x monomer** |
| Predicted 1:1 heterodimer | 127 kDa — **excluded** |
| Predicted 2:2 heterotetramer | 254 kDa — consistent (SEC runs elongated complexes high) |
| Specificity: proteins peaking in that fraction | only 5% of 437 |
| Profile correlation | r = 0.947, the 97.7th percentile of MPN280 vs 298 other proteins |

Honest limits: r = 0.947 is high but not the single highest (MPN262 reaches 0.964), and co-fractionation
alone cannot prove a direct interaction. What it does do is favour a ~2:2-sized assembly over a
heterodimer, from data that knew nothing about our model.

## Interface map and target assessment (post hoc, `rnasej/interface_map.py`, 2026-09-25)

**Architecture is a dimer of heterodimers.** All-atom contacts (<= 5 A) in the M. pneumoniae AF3 model:
RNase J(A)-partner(C) 178 contacts and B-D 178, but A-D only 9 and B-C only 7. The two heterodimers are
joined by a RNase J : RNase J interface (60 contacts) and a partner : partner interface (64).
The main interface buries 65 RNase J residues and 66 partner residues.

**MG423/MPN_621 lacks four aligned catalytic residues (sequence analysis, not an activity measurement).** Against *B. subtilis* RNase J1
(Q45493), whose catalytic/Zn-ligand residues are H76, D78, H79, H368:

| Protein | Identity to BsJ1 | Catalytic residues kept |
|---|---|---|
| RNase J, MPN_280 (P75497) | 39.9% | **4/4** (H83, D85, H86, H377) |
| MG423 homolog, MPN_621 (P75174) | 25.1% | **0/4** (V71, E73, N74, N365) |
| Human CPSF73 (Q9UKF6) | 25.2% | 3/4 at aligned positions |

So the partner keeps the fold and loses the chemistry: consistent with a structural/regulatory subunit
rather than a second nuclease.

**Human off-target.** The nearest human relative is CPSF73 (CPSF3), itself a drug target. RNase J is 25%
identical to it overall, and the 65 interface residues are only **24.6% identical** to CPSF73 (16.9% to
CPSF100). The interface sequence comparison identifies a possible route to selectivity, but says nothing yet
about ligand binding, cellular activity, or human off-target effects.

Interface residue lists: `rnasej/results_interface.json`.

## Prior art and remaining contribution

**Corrected 2026-09-25 after a deeper prior-art and geometry check:**

- **The interaction and missing-paralog assignment are explicitly published.** RNase J (P75497) -
  P75174 is in O'Reilly et al. 2020's PPI table at 5% PPI FDR (reported fdr = 0.0). The study's
  [supplementary text, p. 12](https://pure.mpg.de/rest/items/item_3247325_3/component/file_3247344/content)
  also discusses MPN621 as the missing RNase J paralog, immediately after describing the J1/J2
  heterotetramer in other bacteria. This is direct prior art for the biological interpretation.
- **MG423 being an RNase J paralog that may be inactive is published.** Chilamakuri et al. 2011,
  *Comparative and Functional Genomics* 2011:878973, one sentence: "It has been documented that presence
  of paralogs in Mycoplasma genitalium (MG139 and MG423) and Mycoplasma pneumoniae (MPN280 and MPN261)
  along with other bacteria could be as inactive forms." No structure, no interaction data, no complex.
  (That sentence also has a locus error: MPN_261 is DNA topoisomerase 1; the real MG423 ortholog is
  **MPN_621**.)
- **Closest methodological prior art:** *B. subtilis* RNase J1-J2 is a known heterocomplex (Mathy et al.
  2010) and was modelled from crosslinks + deep learning in 2024 (Stahl et al., *Nat. Commun.*, PDB-IHM
  9A5V). The present analysis adds a structural prediction for the Mycoplasma pair, whose interaction
  was already described.

**What this work adds, stated narrowly:**
1. A **specific predicted 3D arrangement** for the pair discussed in the 2020 supplement, with a 2:2
   geometry compatible with six reported crosslinks in five AF3 samples. The precise arrangement remains
   a testable structural hypothesis, and cellular 2:2 stoichiometry remains unmeasured here.
2. Sequence mapping of four catalytic residues and an interface map that can guide experiments. Loss of
   catalytic activity, a stabilizing role, and drug selectivity have not been measured here.

**Novelty verdict:** this is not a verified discovery of new Mycoplasma RNase J biology. The main
interaction and paralog role were published explicitly, and the 2:2 stoichiometry was strongly suggested
by analogy in that same passage. Treat this as a structural follow-up unless independent experiments
demonstrate a previously unknown mechanism or arrangement.
The specific Mycoplasma 3D prediction is not discussed in Todor et al. 2026 (text and supplements checked).

## Retracted during checking

- **"MG423 is membrane-anchored."** UniProt predicts two transmembrane helices (29-49, 80-100), but both
  align without insertion to MG139's catalytic core (41-61, 92-112), and AF3 folds the first as a
  beta-strand. The sequence-based topology is uncertain; these observations do not establish cellular
  localization or exclude membrane association through a partner.

## Limitations

- Crosslinks are from *M. pneumoniae*, mapped to *M. genitalium* by orthology.
- The DSSO support needed a post hoc fix for corrupted sequences in the crosslink study's FASTA; the DSS
  result was pre-registered before the data were seen.
- The tetramer is template-based (3ZQ4, *B. subtilis* J1). One other template (8CGL) is ambiguous; four
  could not be tested (only two chains deposited).
- ~7 links in total; structure prediction and crosslinks are both indirect.
- The six distinct links share hotspot residues and are not six independent observations. In an exploratory
  degree-preserving reassignment of these same lysine sites on AF3 model 0, 4/48 distinct rewired link
  graphs also have all six distances <=30 A; the observed assignment alone has the shortest mean distance
  (17.31 A). This is a geometric stress test, not an XL-MS p-value (`rnasej/audit_link_specificity.py`).
- A rigid search of alternative 1:1 placements found 36/40 random starts could satisfy all six <=30 A
  restraints before steric filtering. Eight refined placements still had 15-41 interprotein CA pairs <3 A,
  so none is a credible atomic model. This finite search shows that link distances alone do not logically
  require 2:2; it does not establish that a clash-free 1:1 structure exists (`rnasej/test_heterodimer_geometry.py`).
- ipTM changes between separate model compositions do not measure stabilization or binding free energy.

## How a lab could test it (cheapest first)

1. Co-purification: tagged MG139 (or MPN ortholog) pulls down MG423, and vice versa, from cell lysate.
2. Size-exclusion / mass photometry of the purified pair: ~250 kDa heterotetramer vs ~125 kDa heterodimer.
3. Disrupt the predicted tetramer interface (residues around MG139 225-257 / MG423 224) and check assembly
   state; disrupt the K120 region of the heterodimer interface and check co-purification.
4. Cryo-EM of the co-expressed complex.

## Other, weaker findings from the same search

- **MG241-MG242**, a heterodimer of two uncharacterized paralogs (Pfam MPN337 family): 4 in-cell links
  (3 DSSO + 1 DSS) all 12-16 A, but all from one MG241 lysine (K35); consistent, not decisive.
- **MG121 as the permease of the MG119 sugar ABC transporter**: 3/3 DSSO links ~15 A and a replicated DSS
  link; expected from gene neighbourhood.
