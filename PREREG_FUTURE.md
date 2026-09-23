# Pre-registration 12: did frozen AlphaFold predictions anticipate the structures solved afterwards?

Written 2026-09-23, before any PDB entry, release date or SIFTS mapping was joined to the Burke pairs.

## Why

Every never-solved truth set so far is imperfect: STRING (incomplete), crosslinks (proximity), ClinVar
(failed its control), literature (too sparse). The cleanest truth is the future. Burke et al. released
AF2/FoldDock models and pDockQ for about 65,000 human pairs by the end of 2021 (preprint November 2021,
models at archive.bioinfo.se). FoldDock used AF2 weights trained on PDB data to 2018 and no templates.
Complexes first released in the PDB from 2022 on could not have informed those predictions. If
confident never-solved models are mostly real, they should (1) be solved afterwards more often than
low-confidence pairs and (2) match the new experimental interfaces.

## Population (fixed)

Burke S1 rows with a model (`structure_file` present), two different UniProt accessions, and
`int3D_model_structure == 0` (never-solved as Burke defined it). Groups: **confident** pDockQ > 0.23,
**low** pDockQ < 0.10 (middle excluded, as in PREREG_HUMAN).

## Outcome

- PDB co-complex = an entry in which the two accessions map (SIFTS `pdb_chain_uniprot`) to different
  polymer chains. Release date = RCSB `initial_release_date`.
- **Newly solved** = the pair's earliest co-complex entry was released on or after 2022-01-01.
- Pairs whose earliest co-complex was released before 2022-01-01 were precedented but missed by
  Interactome3D; they are **excluded** from both groups (reported as a count).
- **Direct** = in at least one post-2022 co-complex entry the two chains have >= 5 residue pairs with
  CB (CA for Gly) within 8 A (checked on the entries' mmCIF files; the entry with most contacts is the
  reference structure).

## Tests

- **F1 (primary, anticipation)**: rate of newly solved pairs, confident vs low. Odds ratio, node
  bootstrap over proteins, 2,000 reps, 95% CI. **Anticipated** if the CI lower bound > 1.
  - F1b: same with outcome = newly solved AND direct.
  - F1c (confound control): restricted to pairs where both proteins had some PDB structure released
    before 2022 (structurally tractable proteins), since tractable proteins may get both better models
    and more structures.
- **F2 (model correctness)**: for newly solved, direct pairs with a stored model interface
  (`interfaces_v2.jsonl`, exact-sequence UniProt mapping as in CLINVAR2): interface F1 between the
  predicted interface residues (both chains) and the experimental ones, over residues observed in the
  experimental chain. Reported: median F1 and the fraction with F1 >= 0.5 ("correct interface") in the
  confident group, with a bootstrap CI. **Models were right** if the confident group's correct
  fraction exceeds the low-confidence group's with the 95% CI of the difference above 0 (low-group
  models from the stored control set, with more streamed from the Burke archive if fewer than 20).
- Reported: counts at every step, the release-year distribution, and the excluded missed-precedent count.

## Known weaknesses

- SIFTS maps chains to UniProt accessions; isoforms and chimeric constructs can be missed or mis-mapped.
- "Newly solved" depends on what structural biologists chose to study, which tracks biology and fashion,
  not only stability. F1c controls the most obvious part of that.
- pDockQ uses interface pLDDT, which tracks MSA depth, which tracks how conserved and studied proteins
  are. F1c is the partial control.
