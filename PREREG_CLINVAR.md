# Pre-registration 7: do disease variants validate novel predicted interfaces?

Written 2026-09-22, before any model file was downloaded or any variant was mapped.

## Question

HH2 (crosslinks) could not tell whether a *confident* AF2 interface without structural precedent is
as real as a precedented one. Disease genetics gives a second, independent test with clinical
relevance. Pathogenic missense variants are known to concentrate at true protein interfaces
relative to benign variants. If a novel confident interface is real, it should show that enrichment.
If it is mostly wrong, its enrichment should look like that of fake interfaces.

## Data

- Models: Burke et al. 2023 FoldDock/AF2 models (archive.bioinfo.se/huintaf2, HuRI.zip and humap.zip),
  fetched by byte range.
- Variants: UniProt humsavar (current release): missense variants with UniProt canonical positions.
  Pathogenic = `LP/P`, benign = `LB/B`. `US` (uncertain) is excluded.
- Precedent: `int3D_model_structure` (as in PREREG_HUMAN).

## Groups (fixed)

- **Novel-confident**: pDockQ > 0.23 and no precedent.
- **Precedented-confident**: pDockQ > 0.23 and precedent.
- **Control (mostly-fake interfaces)**: pDockQ < 0.10, a random 1,500 pairs (seed 7).

## Measurement (fixed)

- A chain is used only if its modelled sequence exactly equals the UniProt canonical sequence of
  id1 or id2 (so positions map 1:1). Coverage is reported.
- **Interface residue**: CB (CA for Gly) within 8 A of any CB/CA of the other chain.
- Only residues with pLDDT >= 70 (the model's B-factor column) are counted, interface or not. This
  removes the order/disorder confound (pathogenic variants concentrate in ordered regions).
- For each group, pool across chains: a = pathogenic at interface, b = pathogenic elsewhere,
  c = benign at interface, d = benign elsewhere. OR = (a/b)/(c/d), each count +0.5.
- Uncertainty: bootstrap over proteins (UniProt accessions), 2,000 reps, 95% CI.

## Tests

- **T1 (primary)**: OR_novel / OR_control > 1 with the 95% CI excluding 1, meaning novel confident
  interfaces carry disease signal beyond generic ordered surface.
- **T2**: OR_precedented / OR_control, the same rule (a positive control; expected to pass).
- **T3**: OR_precedented / OR_novel. "Comparable" if the CI includes 1; "precedented stronger" if
  the CI lower bound > 1.

If T2 fails, the method is not sensitive enough to detect real interfaces, and T1/T3 are not
interpreted.

## Limitation stated in advance

Surface-vs-core exposure is not controlled beyond pLDDT. Interface residues are surface residues in
the monomer, and pathogenic variants favour buried cores, which would bias ORs *down* equally in
all groups. The control group absorbs generic effects of this kind.
