# MG354 is an RNA polymerase-associated protein in *Mycoplasma*

> **Status 2026-09-25 (final):** **RNAP3 has now run and SUPPORTS the claim.** A three-chain model
> places 4 of the 5 in-cell crosslinks within reach, with the RpoB-RpoC control at 0.95 and chain-pair
> ipTM 0.910. The omega hypothesis separately lost its fold argument (OMEGA). So: MG354 binds the
> assembled RNA polymerase core; it is not shown to be omega.

Found 2026-09-25 by the pre-registered HIGHER test (`PREREG_HIGHER.md`, committed `edd50fd` before any
distance was computed). Full numbers in `results_higher.json`.

## The claim, stated at the strength the data supports

**MG_354 / MPN_530, annotated in UniProt only as "uncharacterized protein", binds the RNA polymerase
core in living *Mycoplasma* cells.** Five distinct in-cell crosslinks connect it to two different RNAP
subunits: two to RpoB (beta, MG_341) and three to RpoC (beta-prime, MG_340). It is 137 residues.

**What this is not.** It is not a solved structure, and it is not proof that MG354 is the missing omega
subunit. That is the leading hypothesis and it is stated as a hypothesis below.

## Why the method's other answers make this believable

HIGHER asked one question: is a crosslink pattern that splits into satisfied links and links too long
for any 1:1 model a general signature of higher-order assembly? It was run blind across 236 testable
*M. genitalium* pairs. Among confident predictions (S0 > 0.2) the split signature picked out, without
being told what they were:

| Pair | What it is | PDB-derived stoichiometry label |
|---|---|---|
| MG_177-MG_341 | RpoA-RpoB | **higher**: alpha is present in two copies (352 of 356 assemblies) |
| MG_272-MG_273, MG_272-MG_274, MG_273-MG_274 | PdhC-PdhB-PdhA | **higher**: all three pairs, pyruvate dehydrogenase |
| MG_191-MG_192 | Adhesin P1-Adhesin P40/P90 | **ambiguous** (1 assembly each way); demoted to unverified |
| ~~MG_340-MG_341~~ | ~~RpoC-RpoB~~ | **one-to-one** (367 of 370 assemblies). **Removed from this list.** |
| MG_139-MG_423 | RNase J-MG423 | unlabelled: no solved homologous co-complex, which is the point of it |

**This list was corrected by its own pre-registered calibration test** (`PREREG_HIGHER_CAL.md`,
committed before any assembly record was fetched). RpoC-RpoB is a 1:1 pair sitting inside a larger
assembly, so the rule fired on it for the wrong reason and the prereg required its removal. What
stands is four verified higher-order recoveries across two unrelated machines, plus an ambiguous
fifth.

**The error rates, which matter more than the list.** Against PDB-derived labels on 55 pairs, the
split call has sensitivity 75% (9 of 12), a false-positive rate of 12% (5 of 42), and precision 64%
against a 22% base rate, a lift of 2.9x. It is a useful flag, not a determination. Among confident
pairs, 15 of 15 split pairs have an oligomeric partner against 4 of 17 clean dimers.

## The evidence for MG354 specifically

- **Five in-cell crosslinks to the RNAP core**, from two chemistries, at 5% link FDR.
- **Two different subunits.** A single spurious identification does not hit both RpoB and RpoC.
- **No pairwise model explains them.** Of the five links, one is within reach (21.2 A to RpoB) and four
  are not (52.6 A to RpoB; 59.0, 47.3, 51.1 A to RpoC). That is the same pattern RNase J showed before
  TETRA resolved it with the right stoichiometry: the links are real and the 1:1 model is the wrong
  object. A protein bound to the assembled holoenzyme would look exactly like this when scored against
  two-chain models.
- **The RpoB pair is a confident prediction** (S0 = 0.370, above the screen's 99.5th percentile of
  0.152) and carries the split signature.

## The hypothesis: an unrecognised omega-type subunit

Bacterial RNA polymerase is alpha2-beta-beta-prime-omega. Omega is small (about 90 to 100 residues in
*E. coli*), binds primarily beta-prime, and is poorly conserved in sequence.

**The field has looked for Mycoplasma's omega and failed.** Orlando et al. (mBio 2023, "Identification
and Structural Modeling of the RNA Polymerase Omega Subunits in Chlamydiae and Other Obligate
Intracellular Bacteria") report that an NCBI search found no annotated *rpoZ* in *M. genitalium* or
other Mycoplasma species, and that checking the gene immediately downstream of *gmk*, the canonical
*rpoZ* position, found no similarity to *rpoZ*.

**That search could not have found MG354.** In *M. pneumoniae*, *gmk* is MPN_246 and this protein is
MPN_530. It is not at the *gmk* locus and it is not detectable by sequence similarity to *rpoZ*. Both
of the field's two search strategies, homology and synteny, were blind to it. In-cell proximity to
beta and beta-prime is a third, independent way to look, and it is the one that found something.

Consistent with omega: the size (137 aa), the binding partners (beta and beta-prime), and being
otherwise functionless in annotation. Not yet shown: the binding site, and whether it occupies the
omega position rather than being a separate regulator.

**Update, OMEGA readout (PREREG_OMEGA, 2026-09-25): the fold does not look like omega.** The
structure search came back with no omega-family hit in either direction. MG354's model is confident
(mean pLDDT 91.2), its only confident structural matches are its own orthologs, and *E. coli* omega
searched against Swiss-Prot models finds 635 hits and no Mollicutes protein at all. Under the
registered rule that is *inconclusive* (the "weakened" branch needs a confident unrelated family, and
there is none), but in plain terms the fold argument for omega is gone. What remains is the crosslink
evidence that MG354 binds RNA polymerase, which the fold search does not touch. The better-supported
reading is now **an RNA polymerase-associated protein of unknown function**, not a missing omega.

**Prior art we had missed.** MG354's structure is not unknown: PDB **1TM9** is an NMR structure of
*M. genitalium* MG354 from the Berkeley Structural Genomics Center (Foldseek E = 5e-9, 69% identity to
the *M. pneumoniae* ortholog). Its function is uncharacterized; its fold is not. Any write-up should
cite 1TM9 and say "uncharacterized function", never "unknown structure".

## What would settle it, in order of cost

1. ~~A dedicated structure prediction of MG354 with RpoB and RpoC together.~~ **DONE 2026-09-25, and
   it supports the reading.** AlphaFold Server, 2,817 residues, 5 samples. Control first: RpoB-RpoC
   0.95 of 20 links within 30 A in every sample (bar 0.70), chain-pair ipTM 0.910. Primary: **4 of 5
   MG354 links satisfied** in the best sample (13.0, 20.8, 15.6, 19.8 A) against a null of p95 0.40.
   Three of five samples give 4/5 and their MG354 ipTM is 0.57/0.43; the two that fail collapse to
   0.17/0.15, so confidence and crosslink satisfaction agree. The one link that fails everywhere is at
   **residue 1**, a flexible N-terminus and the least reliable site assignment. What the pairwise
   models could not show, the three-chain model does: MG354 reaches both beta and beta-prime at once.
2. ~~Fold comparison against solved omega subunits.~~ **Done (OMEGA): no omega-like fold found.**
   The NMR structure 1TM9 already exists and can be used directly in any docking or modelling step.
3. **Pull-down of tagged RpoC**, testing whether MG354 co-purifies. A lab experiment, days not months.

## Honest limits

- The MG_341-MG_354 split rests on **two links only**, the minimum the pre-registration allows. The
  broader MG354-to-RNAP claim rests on five.
- The RpoC pair's prediction is not confident (S0 = 0.177), so its three far links may reflect a wrong
  model rather than a higher-order arrangement. Both readings are consistent with MG354 binding the
  assembled core; neither is proven.
- MG354 itself shows no over-length self-links (5 self-links, 0 over-length), so there is no evidence
  it is present in more than one copy. Omega is a single copy, which is consistent, but the absence is
  weak evidence either way at n=5.
- Crosslink site resolution carries the errors documented in XLVAL Amendments 1 and 2.
- P1's confidence interval is [0.022, 0.674] and barely excludes zero. The post-hoc controls
  (rate-based, link-count-matched, confident-only) all hold and are reported in `RESULTS.md`, but they
  are post hoc.

## Data

O'Reilly et al. 2020 in-cell DSSO and DSS crosslinks; Todor et al. 2026 pooled AlphaFold3 models of all
113,050 *M. genitalium* pairs. Both public. Analysis: `analysis_higher.py`. Nothing here required a lab.
