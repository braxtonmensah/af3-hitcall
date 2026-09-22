# Pre-registration 6: human interactome (AlphaFold2 / FoldDock), Burke et al. 2023

Written 2026-09-22, before any score was cross-tabulated against precedent or crosslinks. Only
coverage counts have been viewed: 65,484 pairs; Interactome3D model = 2,937; pairs with >= 1 mapped
crosslink = 528 (242 precedented, 286 not).

## Data

Burke et al., Nat Struct Mol Biol 2023 (PMC9935395), Supplementary Table 1: pDockQ for 65,484 human
pairs from HuRI (yeast two-hybrid, direct binary) and hu.MAP 2.0 (complexes), modelled with
AlphaFold2 through FoldDock. A third organism, a third model, and disease-relevant proteins.

- **Precedent** = `int3D_model_structure == 1`: Interactome3D has an experimental or domain-homology
  model for the pair. This is the authors' own flag, not my RCSB pipeline, so it is a
  definition-robustness check as well.
- **Confident** = pDockQ > 0.23 (the paper's "acceptable model" threshold). Sensitivity: > 0.5.
- **Crosslink satisfaction** = `cross32 / crosstotal`: the share of mapped in-cell/in-vitro crosslinks
  within 32 A (lysine NZ-NZ) on the predicted model. This is independent evidence that the *model*
  is right.

## HH1: recall by precedent (replication of H1/BSU)

Among HuRI pairs (Dataset contains HURI): P(confident | precedent) - P(confident | none). Node bootstrap
over proteins, 2,000 reps, 95% CI.

- **Replicates** if the difference >= 0.20 and the CI lower bound > 0.
- **Fails** if the CI includes 0.
- Otherwise partial.

Caveat, stated now: there are no clean negatives in this table, and Y2H has its own false positives.
This is a recall contrast, not an AUROC.

## HH2: when AF2 is confident, is a never-solved model as correct as a precedented one?

Among pairs with crosstotal >= 1 AND pDockQ > 0.23: mean per-pair crosslink satisfaction, precedented
minus none. Node bootstrap, 95% CI.

- **Equivalent** (a confident novel model is as trustworthy as a precedented one) if the whole CI lies
  within [-0.15, +0.15].
- **Precedent better** if the CI lower bound > 0.
- Otherwise inconclusive.
- **Underpowered** if either stratum has fewer than 15 pairs.

Also reported: the same contrast for low-confidence pairs (pDockQ <= 0.23), to show whether confidence
itself carries the correctness signal.

Why HH2 matters: H1-TIME said AF recognises stable complexes. The practical question for a lab is
whether a *confident* hit without precedent can be trusted structurally. HH2 answers that with
evidence that doesn't come from the PDB.
