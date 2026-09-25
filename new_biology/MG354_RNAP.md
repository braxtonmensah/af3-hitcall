# MG354 is an RNA polymerase-associated protein in *Mycoplasma*

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

| Pair | What it is | Known stoichiometry |
|---|---|---|
| MG_340-MG_341 | RpoC-RpoB | RNA polymerase core, alpha2-beta-beta-prime |
| MG_177-MG_341 | RpoA-RpoB | alpha is present in **two copies** |
| MG_191-MG_192 | Adhesin P1-Adhesin P40/P90 | Nap adhesin, a dimer of heterodimers |
| MG_272-MG_273, MG_272-MG_274, MG_273-MG_274 | PdhC-PdhB-PdhA | pyruvate dehydrogenase, a 60-subunit E2 core with E1 alpha2beta2 |
| MG_139-MG_423 | RNase J-MG423 | the 2:2 heterotetramer from TETRA |

Four independent textbook higher-order assemblies, recovered by a distance rule that knows nothing
about any of them. Among confident pairs, **15 of 15 split pairs have an oligomeric partner against 4
of 17 clean dimers.**

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
otherwise functionless in annotation. Not yet shown: the fold, the binding site, and whether it
occupies the omega position rather than being a separate regulator.

## What would settle it, in order of cost

1. **A dedicated structure prediction of MG354 with RpoB and RpoC together**, then check whether all
   five crosslinks fall within reach. This is the direct analogue of what TETRA did for RNase J and
   needs GPU time, not a lab.
2. **Fold comparison** of the predicted MG354 monomer against solved omega subunits. If it carries the
   omega fold despite no sequence similarity, that is close to decisive.
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
