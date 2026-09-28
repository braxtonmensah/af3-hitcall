# PREREG XLGEO2: the same test on a FIRMICUTE template, and the last attempt either way

Written 2026-09-28 after `RESULT_XLGEO_ECOLI_GATE_FAILED.md`, **before any distance was computed on the
new template**. Zero GPU.

## 0. Why a second template is legitimate, and where it is not

Attempt 1 used *E. coli* 4YG2 and its gate failed at 64.7% against a registered 70%.

**The a priori reason for a Firmicute template exists independently of that failure.** *Mycoplasma* and
the other Mollicutes are **degenerate Firmicutes**, descended from the Bacilli; *E. coli* is a
gamma-proteobacterium, a different phylum. On phylogeny alone *B. subtilis* is the better template and
arguably should have been attempt 1. E. coli was chosen because 4YG2 contains **omega**, which serves
only the **exploratory secondary** outcome, not the primary.

**Where this is not legitimate, stated so it cannot be quietly abused: this is now two shots at one
gate.** Accordingly:

- **If the B. subtilis gate also fails, the structural route is ABANDONED. No third template.** That is
  binding, and it is the entire reason this document exists rather than a quiet re-run.
- Both attempts are reported, pass or fail, in the same place.

## 1. Template

**PDB 6WVK**, *B. subtilis* RNA polymerase. Chain **C** = beta (1,099 observed), chain **D** = beta-prime
(1,184 observed), chain **E** (69 observed) is the candidate **omega**; its identity is verified from the
entity description before use, and if it is not omega the secondary outcome is dropped rather than
computed on the wrong chain.

## 2. Everything else is UNCHANGED from PREREG_XLGEO.md

Same query sequences, same alignment procedure, same 30 A cutoff, same **70% gate on the 20 RpoB-RpoC
control crosslinks**, same primary outcome (**maximum pairwise Ca-Ca distance among the five mapped
MG354 attachment sites**) and the **same thresholds, not adjusted**:

- **<= 60 A: TIGHT**, one pocket.
- **60 to 105 A: COMPATIBLE BUT WEAK.**
- **> 105 A: INCOMPATIBLE** with a single MG354 copy.

Secondary (exploratory, same caveat): centroid-to-omega distance against a 1,000-draw composition-matched
null.

## 3. The conformational caveat now applies to the primary as well

Attempt 1 showed 6 of 17 real RpoB-RpoC in-cell crosslinks exceed 30 A in a core-enzyme crystal, which is
most likely conformational. **Therefore, even if the gate passes, an "INCOMPATIBLE" primary result must be
reported with the caveat that a single conformation may not satisfy crosslinks drawn from a population of
states.** Registered now so it cannot be added or omitted depending on which way the number falls.
