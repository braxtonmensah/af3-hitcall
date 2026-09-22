# Pre-registration 9: does AF2 confidence carry real signal in the never-solved class? (literature truth via Jev)

Written 2026-09-22, before any literature search or Jev call on human pairs.

## Why

HH2 (crosslinks) was inconclusive, and the disease-variant test (CLINVAR v1) failed its positive
control. A third independent truth source is the literature itself. Jev (TypeSafe System One)
judged ~1,200 *Vibrio* abstracts for $0.43, recovered all 3 known Dalia-lab interactions, and was
wrong on 1 of 5 flagged pairs.

## Sample (fixed, seed 20260922)

From Burke S1 HuRI pairs with **no Interactome3D precedent**:
- **Confident**: 350 random pairs with pDockQ > 0.23.
- **Low**: 350 random pairs with pDockQ < 0.10.
- Reference: 150 random precedented pairs with pDockQ > 0.23.

## Labels (fixed)

For each pair, Europe PMC: `"SYM1" AND "SYM2" AND HAS_ABSTRACT:y` using gene symbols
(`Gen.id1`, `Gen.id2`), top 5 by relevance. Jev (jev-1.13 via `jev/src/jev.ts`) judges each abstract:
- noul: does it report evidence that the two proteins physically interact directly?
- choice: the strongest evidence type.

**lit_direct** = max noul >= 0.8 over the pair's abstracts. **co-mentioned** = at least 1 abstract.

## Tests

- **L1 (primary)**: among never-solved pairs that are co-mentioned, P(lit_direct | confident) -
  P(lit_direct | low). Bootstrap over pairs, 2,000 reps, 95% CI. **Signal** if the CI lower bound
  > 0. Conditioning on co-mention controls for "well-studied proteins get both more papers and
  cleaner models".
- **L2 (secondary)**: the same difference unconditioned (lit_direct = 0 when no abstracts).
- Reported: the precedented-confident reference rate, the co-mention rate per group, and Jev spend.

## Known weaknesses

- Gene-symbol ambiguity adds noise.
- Jev's observed error rate on this task is about 1 in 5 flagged pairs. Label noise dilutes
  differences but does not create them between groups, because the same judge is used for all.
- The literature favours stable, well-studied complexes; that is the thing being probed, so it is
  stated rather than corrected.
