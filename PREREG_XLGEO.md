# PREREG XLGEO: are MG354's five in-cell crosslinks geometrically satisfiable by ONE copy, and where on the polymerase do they point?

Written 2026-09-28 **before any distance was computed**. Zero GPU. Template `4YG2` downloaded and its
chain composition inspected before writing this; **no crosslink distance was measured.**

## 0. Why this exists, and why it is not RNAP3

RNAP3 (`PREREG_RNAP3.md`) asks a three-chain predictor whether MG354's five crosslinks are satisfiable.
It has now failed twice on compute: AlphaFold Server was never run, and Boltz-2 OOM'd on an 80 GB H100
because the pair representation for 2,817 tokens is 2817^2 x 128 x 4 = 4.07 GB per tensor.

**This test needs no predictor at all.** The five MG354 crosslinks land on RpoB and RpoC, and **the
RpoB-RpoC core is already solved** in many bacteria. If the five attachment sites are scattered across a
150 A machine, no single 136-residue protein can touch them all, and that is knowable from a real
structure today. It is a different and in one way stronger question, because it depends on crystallography
rather than on a model.

## 1. Template and mapping

- **Template: PDB 4YG2**, *E. coli* RNA polymerase core. Chain **C** = beta (rpoB, residues 3-1342),
  chain **D** = beta-prime (rpoC, 8-1376), chain **E** = **omega (rpoZ, 2-90)**. The second copy
  (I/J/K) is ignored; only the first is used.
- **Chosen because it contains omega.** The MG354-as-omega fold argument is dead (`PREREG_OMEGA`: no
  omega-family hit in either direction), but **the omega SITE question is untouched by that**, and only a
  structure with omega present can ask it.
- *M. genitalium* RpoB (1391 aa) and RpoC (1290 aa) are taken from
  `cleanroom/rnap3/rnap3_mg354_rpoB_rpoC.yaml` chains B and C, the same sequences RNAP3 would have used.
- Mapping is by **global pairwise alignment** (BLOSUM62) of each Mycoplasma chain onto the observed
  residues of its *E. coli* counterpart. A Mycoplasma residue with no aligned, observed template residue
  is **reported as unmappable, never silently dropped.**

## 2. THE GATE, read first, same bar as PREREG_RNAP3

The 20 **RpoB-RpoC control crosslinks** in `cleanroom/rnap3/links.json` are real in-cell crosslinks
between two chains whose relative geometry the template already fixes. **They validate the mapping.**

**Registered gate: at least 70% (14 of 20) of the mappable control crosslinks must be within 30 A
Ca-Ca in the template. Below that, the alignment or the template is wrong, and NO MG354 number is
reported.** 30 A is the cutoff `score_rnap3.py` already uses.

## 3. Primary outcome and registered thresholds

**Primary: the maximum pairwise Ca-Ca distance among the five mapped MG354 attachment sites**
(RpoB 262, RpoB 289, RpoC 171, RpoC 375, RpoC 1060).

The reach argument, fixed now: MG354 is 136 residues, so its longest internal dimension is about 45 A.
The crosslinks attach at MG354 residues 1, 22, 55 and 128, and each crosslink spans at most 30 A. Two
partner sites touched by one MG354 copy can therefore be at most about **45 + 30 + 30 = 105 A** apart,
and that is the fully extended worst case.

- **<= 60 A: TIGHT.** The five sites form one pocket. Strongly consistent with a single specific site.
- **60 to 105 A: COMPATIBLE BUT WEAK.** Possible for one copy only in an extended arrangement. Reported
  as weak, not as support.
- **> 105 A: INCOMPATIBLE.** No single MG354 copy can make all five. That would imply **more than one
  copy**, or that some crosslinks are non-specific. This would be a genuine result and is the outcome I
  am registering as live, not as a formality.

**No threshold may be adjusted after the number is seen.**

## 4. Secondary, and it is exploratory, labelled as such now

Distance from the **centroid of the five mapped sites** to the **centroid of omega (chain E)**, compared
against a null built from 1,000 random 5-site draws from the mappable RpoB/RpoC surface positions,
matched to the same chain composition (2 on RpoB, 3 on RpoC).

**This is exploratory and cannot support an "MG354 is omega" claim on its own**, because the fold
argument already failed and a site can be shared by unrelated proteins. Reported with that sentence
attached. A null-indistinguishable result is reported just as loudly as a close one.

## 5. Limits, stated before the numbers

1. **A template is not the Mycoplasma structure.** *E. coli* and *M. genitalium* RNAP differ in loops and
   insertions, so mapped positions carry alignment error. The gate in section 2 is what makes this
   tolerable, and if the gate fails the whole file reports nothing.
2. **A crosslink is a distance restraint, not a contact.** 30 A Ca-Ca is permissive.
3. **The MG354-RpoB arm rests on only 2 links** and the whole claim on 5, exactly as
   `new_biology/MG354_RNAP.md` already records.
4. Nothing here shows MG354 is a subunit, or functional, or stoichiometric. It tests one geometric
   question.
5. Unaudited per G6.
