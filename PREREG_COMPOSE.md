# Pre-registration 14: can composing autonomous interfaces recover AF's misses? (COMPOSE)

Written 2026-09-23 after COOP, before building any composite model. Only availability was counted:
among FUTURE newly-solved direct pairs, 15 misses (pDockQ < 0.10) and 34 hits (> 0.23) have a third
protein C in the reference entry with Burke models for both A-C and B-C at pDockQ > 0.23; 66 misses
have some C with both models at any confidence.

## Idea

COOP-H found AF's misses are small, non-autonomous contacts inside large assemblies. If AF's confident
predictions are right (FUTURE) and the misses are non-autonomous, then an A-B contact that AF cannot
see directly should appear when two **autonomous** predictions sharing a partner are composed:
superimpose the A-C and B-C models on C, and read the A-B contact off the composite. No GPU is needed.
Assembling complexes from pairwise models is known (MoLPC, CombFold). Using it to recover a screen's
missed pairs, validated on structures the models never saw, is the new part.

## Method (fixed)

- C = the protein in the reference entry (other than A, B) maximising min(pDockQ(A,C), pDockQ(B,C)).
- Models: Burke FoldDock PDBs for A-C and B-C (streamed from archive.bioinfo.se); chains mapped to
  UniProt by exact sequence (residue k -> position k+1). Pairs failing mapping are dropped and counted.
- Superposition: Kabsch on CB (CA for Gly) of C residues with pLDDT >= 70 in both models (>= 30 such
  residues required); A from the A-C model and B from the B-C model moved into one frame.
- Composite A-B interface: residues of A and B with CB within 8 A of the other. Clash = more than 10 CB
  pairs closer than 3 A (reported).
- Score: interface F1 against the reference structure's A-B interface over observed residues, exactly
  as FUTURE F2. **Correct** = F1 >= 0.5.

## Tests

- **K1 (primary)**: among the 15 confident-C misses, fraction correct by composition vs by AF's own
  pairwise A-B model (paired). Rescue if composition is correct more often (exact McNemar-type sign
  test, one-sided p < 0.05) **and** at least 5 of 15 are correct.
- K2: the same over all 66 misses with any C (secondary).
- K3 (sanity): composition on the 34 confident-C hits; it should mostly agree with the experiment.

## Known weaknesses

- n = 15 for the primary. This is a pilot of the concept, and it says so.
- C is chosen from the real entry, so this assumes knowing which assembly the pair belongs to. That
  information is what complex-membership resources (hu.MAP, CORUM) supply without structures.
- Burke's A-C and B-C models are pairwise predictions frozen in 2021; the reference structures are
  from 2022 on, so the same no-leakage argument as FUTURE applies.
