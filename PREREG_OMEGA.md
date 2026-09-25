# Pre-registration 24: does MG354 have the fold of an RNA polymerase omega subunit? (OMEGA)

Written 2026-09-25, before any structure of MG354 was downloaded or searched, and before any
structural comparison was run.

## Why

HIGHER found MG_354 / MPN_530, annotated only as "uncharacterized protein", tied to RNA polymerase
beta and beta-prime by five in-cell crosslinks (`new_biology/MG354_RNAP.md`). The leading hypothesis
is that it is Mycoplasma's missing omega subunit. Orlando et al. (mBio 2023) found the omega subunits
of Chlamydiae by structural modelling after sequence search failed, and reported that no omega could
be found in Mycoplasma by sequence or by *gmk* synteny. A structure search is the test that worked
for Chlamydia and was not reported for Mycoplasma.

## Data (fixed now)

- **Query:** the AlphaFold Database model of P75248 (MPN_530, the *M. pneumoniae* ortholog of MG354),
  `AF-P75248-F1`, CC-BY 4.0. The *M. pneumoniae* protein is used because it is the one with the
  crosslinks and a Swiss-Prot entry.
- **Reverse query:** AFDB model of *E. coli* omega, P0A800 (rpoZ).
- **Search:** Foldseek web server, mode 3Di+AA, databases `pdb100` and `afdb-swissprot`.

## Omega family (fixed now)

A hit counts as omega-family if its description names any of: RNA polymerase subunit omega, rpoZ,
RPB6, RPABC2, RpoK (archaeal), or the chlamydial omega genes named in Orlando et al.

## Tests

- **Q (quality gate, first).** Mean pLDDT of the MG354 model. If below 60, the model is too
  uncertain for a fold comparison and O1-O2 are reported but **not interpreted**. Omega is partly
  disordered off the polymerase, so a low score is itself an expected outcome and is not evidence
  against the hypothesis.
- **O1 (forward).** MG354 against `pdb100` and `afdb-swissprot`. Report the best omega-family hit,
  its rank, E-value and TM-score.
  - **Supports** if an omega-family hit has E <= 0.01.
  - **Weak support** if an omega-family hit appears with 0.01 < E <= 1.
- **O2 (reverse).** *E. coli* omega against `afdb-swissprot`. Report every Mollicutes hit (Mycoplasma,
  Mycoplasmoides, Ureaplasma, Spiroplasma, Acholeplasma, Mesoplasma) with E-value and rank.
  - **Supports** if P75248 is the top Mollicutes hit with E <= 1.
- **Verdict.** Supported if O1 or O2 supports. **Weakened** if MG354's confident hits (E <= 1e-3)
  belong to one well-annotated, clearly unrelated family and no omega-family hit appears at E <= 1.
  Otherwise inconclusive.

## Reported whatever the outcome

The top ten hits of each search, the pLDDT, and the verdict. A negative structure search is weak
evidence against a small, partly disordered subunit, and that limit is stated with any negative.

## What this cannot show

A fold match says MG354 is shaped like omega. It does not show that it binds where omega binds or
does what omega does. That needs the three-protein structure prediction and a pull-down.
