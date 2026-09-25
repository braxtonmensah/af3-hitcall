# Pre-registration 20: is Mycoplasma RNase J an (MG139-MG423)x2 heterotetramer? (TETRA)

Written 2026-09-25 before building any tetramer model or computing any cross-copy distance.

## Why

In both in-cell crosslink datasets (DSSO and DSS) the MG139-MG423 links split into near links that the
AF3 heterodimer satisfies (MG139 K120 to MG423 502 and 546; MG139 409 to MG423 322) and far links it does
not (MG139 225, 228 and 257 to MG423 224; 51-63 A). Solved RNase J enzymes are dimers of dimers. If the
Mycoplasma enzyme is a heterotetramer of two MG139-MG423 pairs, the far links should be satisfied
**across** the two pairs.

## Method (fixed)

- Templates: every solved RNase J tetramer found by the current-PDB homolog search whose deposited model
  has 4 chains: 3ZQ4, 4XWW, 7WNU, 8CGL, 5WS2, 6LLB (3T3N/3T3O deposit only 2 chains and are excluded). Each is used
  separately.
- The AF3 MG139-MG423 heterodimer (pool 1052, all 5 samples) is treated as a rigid body. MG139 is
  superposed (Kabsch, sequence-aligned CA pairs) on each template chain; the chain that MG423 then
  overlaps best defines the template's heterodimer pairing. The second copy is placed by superposing
  MG139 on the template chain related to the first by the tetramer's other dimer interface.
- Distances: for each of the 6 distinct crosslinked residue pairs (union of DSSO and DSS), the minimum
  CA-CA distance over the four MG139-copy x MG423-copy combinations. Satisfied <= 30 A.
- Null: random MG139 lysine x MG423 lysine pairs, same min-over-copies distance, 1,000 draws of 6 pairs.

## Prediction and rule

**Supported** if, for at least one template, in the majority of the 5 samples: all 3 far links are
satisfied, the 3 near links stay satisfied, and the satisfied fraction (6 links) exceeds the null's 95th
percentile. Clashes (CA-CA < 3 A between copies, more than 20 pairs) are reported and a clashing model
does not count.
