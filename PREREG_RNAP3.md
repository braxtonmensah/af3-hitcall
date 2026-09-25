# Pre-registration 25: does a three-chain model place MG354's crosslinks within reach? (RNAP3)

Written 2026-09-25, before any structure of this complex was predicted and before any distance in it
was computed. This is the test named as step 1 in `new_biology/MG354_RNAP.md`.

## Why

HIGHER found MG354 (MPN_530) tied to RNA polymerase beta (RpoB, MPN_516) and beta-prime (RpoC,
MPN_515) by five in-cell crosslinks, of which only one is satisfiable in any pairwise model. The
reading offered was that MG354 binds the assembled core, so no two-chain model can hold all five.
That is a prediction and this is its test: build the three chains together and see whether the links
come within reach.

## Model

- **Boltz-2** (MIT licence) on a rented GPU. Not AlphaFold Server, whose output is non-commercial and
  barred from downstream use (`COMMERCIAL.md`). Nothing here touches IU compute, so the work stays
  outside IU policy UA-24.
- Chains, one copy each: MPN_530 (136 aa), MPN_516 (1391 aa), MPN_515 (1290 aa). Total 2,817 residues.
- *M. pneumoniae* sequences, because the crosslinks are *M. pneumoniae*. This removes the
  ortholog-alignment step that XLVAL needed.
- Default sampling, 5 diffusion samples, seed 25. MSA from the Boltz pipeline.

## The links (fixed now, from the 5% link FDR data, Amendment 2 site resolution)

**MG354 to the core, the five under test:**

| # | Chain A | Res | Chain B | Res | Crosslinker |
|---|---|---|---|---|---|
| 1 | RpoC | 171 | MG354 | 128 | **DSSO and DSS** |
| 2 | RpoC | 1060 | MG354 | 22 | DSSO |
| 3 | RpoC | 375 | MG354 | 128 | DSS |
| 4 | RpoB | 262 | MG354 | 55 | DSS |
| 5 | RpoB | 289 | MG354 | 1 | DSS |

Link 1 is seen with two different chemistries in separate experiments.

**Internal positive control:** the 23 distinct RpoB-RpoC links in the same data. The RpoB-RpoC
interface is a known, conserved one, so a correct model must satisfy most of them. This control is
independent of MG354 and is what makes the MG354 numbers interpretable.

## Tests

- **C (control, read first).** Fraction of RpoB-RpoC links with CA-CA <= 30 A, over all samples.
  - If **below 0.7**, the model has not reproduced a known interface and **the MG354 result is not
    interpreted**. Reported either way.
- **T1 (primary).** Fraction of the five MG354 links with CA-CA <= 30 A, best sample.
  - **Supported** if **>= 4 of 5** are satisfied and the fraction beats the null's 95th percentile.
  - **Partial** if 2 or 3 of 5 are satisfied and beat the null.
  - **Not supported** if <= 1 of 5, which would mean the three-chain arrangement does not explain the
    crosslinks either and the "binds the assembled core" reading is wrong as stated.
- **Null.** Random lysine pairs drawn across the same two chains, 1,000 draws, same cutoff, same
  models. (Link 5 is at residue 1, an N-terminus, and is drawn from N-termini plus lysines.)
- **T2 (reported, not decisive).** Boltz ipTM for MG354 against each of RpoB and RpoC, and where
  MG354 sits relative to the known omega-binding site on beta-prime.

## Reported whatever the outcome

All five distances, the control fraction, the null, the ipTM values, and the verdict. A failure here
is a real result: it would say MG354's crosslinks need something beyond these three chains, such as
the alpha subunits, a different stoichiometry, or that the association is wrong.

## What this cannot show

A satisfied crosslink set is consistent with binding, not proof of it. It says the in-cell distance
restraints and the predicted structure agree. Only an experiment settles whether MG354 is bound in
the cell, and a pull-down of tagged RNA polymerase remains the right one.
