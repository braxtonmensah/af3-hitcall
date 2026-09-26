# Pre-registration 30: a small-molecule screen against the MPN621 degenerate cleft (MPN621)

Written 2026-09-26, **before any Boltz-2 score exists for this target**, on any machine. Nothing in
this pre-registration has been run. It supersedes nothing: `PREREG_VSCREEN.md` and its four
amendments stand, and Amendment 4 is the reason this file exists.

## Why this target, and why not the one we had

`PREREG_VSCREEN` aimed a screen at the RNase J : MPN621 protein-protein interface. Amendment 4
measured the interface and closed that route:

| Cavity | *M. pneumoniae* | *M. genitalium* | ratio |
|---|---|---|---|
| RNase J catalytic cleft | 1262 | 1155 | 1.09 |
| **RNase J largest non-catalytic interface cavity** | **26** | **27** | **1.04** |
| **MPN621 degenerate cleft** | **491** | **470** | **1.04** |
| MPN621 largest non-catalytic interface cavity | 273 | 82 | 3.33 |

against KEAP1:p62 575 A^3 (drugged), MDM2:p53 76 (drugged but shallow), c-Fos:c-Jun 0 (flat).

The interface is flat on the RNase J side in both models, and the MPN621 interface cavity that
looked promising does not reproduce. What does reproduce, at a ratio of 1.04 and at a volume
comparable to a drugged reference, is **MPN621's own degenerate cleft**, and that is this target.

**It is a conventional pocket, not an interface.** That matters for the instrument as much as for
the chemistry: Boltz-2's affinity head was trained largely on conventional pockets and has **no
protein-protein affinity module at all** (`cleanroom/BOLTZ_SCHEMA.md`). The previous design asked
the tool a question it was not built for. This one does not.

## The selectivity case, measured rather than asserted

The reason the old design avoided catalytic clefts is that they are conserved, so a ligand in one is
not selective. **MPN621 is the exception, because it has lost the catalytic machinery.** Global
pairwise alignment (BLOSUM62, biopython), comparing the 20 cleft-lining residues:

| Comparison | Global identity | Cleft-lining residues conserved |
|---|---|---|
| MPN621 vs *M. pneumoniae* RNase J (the paralogue) | 24.1% | **5 of 20, 25%** |
| MPN621 vs human CPSF73 (the off-target) | 22.1% | **4 of 20, 20%** |

The cleft is **no more conserved than the protein as a whole**, which is the opposite of what an
active site normally looks like and is what a catalytically-dead cleft should look like. At the four
positions that carry catalysis, RNase J has H81/H83/D85/H86 and human CPSF73 has H71/H73/D75/H76 —
the same His/Asp cluster — while **MPN621 has N69/V71/E73/N74**.

So the two proteins a hit must not hit share a catalytic cluster that the target has lost. That is a
real selectivity prospect. It is **not** a measured selectivity margin, and testing it is what arms
O1 and O2 below are for.

## Arms

| Arm | Receptor | Compounds | Purpose |
|---|---|---|---|
| **S** | MPN621, P75174, pocket-constrained to the cleft | the selection | the question |
| **N** | same | property-matched, same size as S | what "high" means |
| **O1** | *M. pneumoniae* RNase J, P75497, constrained to its catalytic cleft | same as S | **paralogue selectivity** |
| **O2** | human CPSF73, Q9UKF6, constrained to its catalytic cleft | same as S | human off-target |

**O1 is the arm the old design did not have and is the one that matters most.** A compound that hits
both paralogues in the same organism tells you nothing about which one carries the phenotype, and
RNase J is the better-characterised and more conserved of the two, so cross-reactivity is the
default expectation rather than a remote risk.

**The pocket is geometric, from coordinates, and is fixed here:** MPN621 residues
`15, 18, 37, 69, 71, 73, 74, 142, 162, 163, 201, 234, 329, 332, 334, 358, 359, 363, 365, 387`, the
20 nearest the 491 A^3 cavity in `rnasej_mpn_2x2_AF3_model_0.cif`, from
`cleanroom/cavity_residues.py`. It is **not** a truncation by residue number; that defect is recorded
in `PREREG_VSCREEN` Amendment 3 and `build_screen_jobs.require_pocket` now refuses it.

## The gate

**The gate is the one already built for `PREREG_VSCREEN` (Amendments 1-3), unchanged, and it must
pass before arm S is interpreted.** `cleanroom/gate_jobs/`, 250 jobs, 3-6 GPU-hours.

It is a **better** gate for this target than for the one it was built for. Three of its four
receptors (CPSF73, SNM1A, Artemis) are conventional catalytic pockets in this same fold family,
which is exactly what MPN621's cleft is. The Tier B interface rung is no longer load-bearing here,
because this screen does not aim at an interface; it is reported but **B2 is not required**.

Criterion **A1 as restated in Amendment 3**: the two representable Tier A rungs, the JTE-607 acid on
CPSF73 and ceftriaxone on Artemis, must each outscore at least 57 of their receptor's 60 matched
decoys. The three metal-chelating rungs remain diagnostics.

## Tests

**M1 (primary).** Mann-Whitney U of arm S against arm N on `affinity_probability_binary`, as AUC
with a bootstrap 95% CI. Enriched if the CI excludes 0.50 above.

**M2 (paralogue selectivity, required for any purchase).** Per compound, score in S minus score in
O1. A shortlisted compound must score **above** its own O1 score. A compound that does not is
recorded as a paralogue cross-reactor and is not bought.

**M3 (human off-target, required for any purchase).** The same against O2.

**M4 (shortlist).** Top 25 of S by score, each with its empirical percentile against N, its O1 and O2
scores, PAINS flag and purchase cost, **labelled as hypotheses requiring experimental test**. As in
`PREREG_VSCREEN`, per-compound significance is unreachable at this null size and no entry is called a
hit or a binder.

**M5 (reported).** Correlation of score with molecular weight and heavy-atom count within S. If
strong, M1 is downgraded to inconclusive regardless of its CI.

## Consequences fixed in advance

- **Gate fails** → nothing here is interpreted, no purchase, and the compound route closes on a
  measured instrument failure rather than on a guess.
- **M1 null** → no enrichment among the screened space at this cleft. No purchase. A real answer.
- **M1 enriched, M2 or M3 fails for a compound** → that compound is not bought, whatever its rank.
- **M1 enriched and M2 and M3 pass for some compounds** → those become a purchase candidate list,
  still described as an enriched set with untested individuals.
- **If MPN621's cleft and RNase J's cleft rank compounds near-identically** (Spearman above 0.9
  across the screen), the two pockets are not being distinguished by the method, the selectivity
  premise is unsupported **by this instrument**, and M2 cannot be used to justify a purchase.

## Limits, stated before the result

- **MPN621 has no known function.** UniProt annotates it only as "Uncharacterized protein MG423
  homolog": no function, no family, no subunit annotation, and **no PDB entry**. A ligand in its
  cleft may do nothing at all. The only functional handle is essentiality.
- **Essentiality is species-split and the split runs the wrong way for generalisation.** MPN621 is
  essential in *M. pneumoniae* (E/E, and E by colony isolation, Lluch-Senar 2015) but its
  *M. genitalium* ortholog MG_423 is annotated **non-essential**. The screen targets the species
  where it is essential, and that must be said whenever the result is presented.
- **The receptor is a prediction.** Both chains have zero PDB entries. The cleft is measured on an
  AF3 model, and the ortholog agreement (1.04) is agreement between two predictions from the same
  engine, which shares whatever systematic error that engine has.
- **Only `model_0` was scanned.** Per-sample variation in the cavity is unmeasured.
- **The conservation numbers are alignment-based**, over 20 positions, and are a reason to test
  selectivity rather than a selectivity result.
- **Boltz-2's out-of-distribution ceiling is mean Pearson R 0.39** on its own blinded set. This
  target is out of distribution. Any ranking from it is a ranking to test, never an affinity.
- **No wet-lab experiment supports any of this**, and *M. pneumoniae* is slow and fastidious to
  culture, so an MIC quote is obtained **before** compounds are bought, not after.

## What is screened

`cleanroom/library_master.tsv`, built by `cleanroom/libgen.py`, deduplicated on InChIKey after
desalting, with source, licence and date per compound. The selection and its property-matched null
are written by `libgen.py --select` and committed before the run; the KS statistics per property are
reported with the result.

---

# Amendment 1, 2026-09-26: the metal is a confound in the selectivity arm, and it is measured rather than assumed away

Written **before any Boltz-2 score exists for this target**. What has been read since the body of this
file: the cleft residue identities, the model-to-UniProt index mapping, and the 6M8Q construct
mapping. No prediction has been run.

`PREREG_VSCREEN` Amendment 2 fixed a metal policy of **one catalytic Zn per MBL-beta-CASP nuclease
chain**, applied identically to every receptor. Applying it here exposes a problem that policy cannot
settle.

## The measurement

Residues lining each cleft, checked for zinc ligands:

| Receptor | Cleft residues | Potential Zn ligands | Histidines |
|---|---|---|---|
| **MPN621 (target, arm S)** | RNTNVENSDDRSMRAGRSNS | E73, D162, D163 | **none** |
| **RNase J (paralogue, arm O1)** | FEDYSTNSSNSESNPNHSHE | E84, D85, E311, H373, H377, E401 | **H373, H377** |

MBL zinc sites are histidine-rich; the family signature is HxHxDH. **MPN621's cleft has no histidine
at all**, consistent with it having lost catalysis, while RNase J's retains two. Carboxylates alone
can coordinate zinc, but weakly and without the geometry, so **whether MPN621 holds a catalytic metal
is genuinely unresolved** and no policy statement makes it resolved.

## Why this is a confound and not a detail

Arm O1 is the selectivity test that justifies a purchase. If MPN621 is built without a zinc and
RNase J with one, then a compound can score higher on MPN621 **because its pocket has no competing
metal in it**, not because of any complementarity to MPN621. That failure mode points in the
direction that flatters the target, which is the worst direction for it to point.

Building MPN621 *with* a zinc is not obviously safer: a zinc with no histidines to hold it may drift
during folding and distort the very pocket being screened.

## What is fixed now

**The screen runs with MPN621 metal-free**, because the residue evidence says it has no canonical
site and inventing one is the larger assumption. RNase J and CPSF73 are built with one Zn each,
because they have the His/Asp cluster. **This is a declared deviation from `PREREG_VSCREEN`
Amendment 2's uniform rule, and the reason is that the rule assumed every receptor in the comparison
is a metalloenzyme, which is exactly what is not true here.**

**Arm Z (sensitivity, pre-registered now, not optional).** The **top 25 of arm S by score plus 25
screen compounds drawn at random by committed seed** are re-run against MPN621 **with one Zn**, same
pocket, same everything else. 50 jobs.

- **If the Spearman correlation between arm S and arm Z on those 50 exceeds 0.8**, the ranking does
  not depend on the metal and the selectivity result stands as reported.
- **If it does not**, the ranking is metal-dependent, the choice above is load-bearing rather than
  incidental, and **M2 and M3 must be reported as conditional on a metal assignment the evidence does
  not settle**. No purchase on a metal-dependent selectivity margin.

Arm Z is a subset rather than a duplicate of arm S because doubling the largest arm to answer a
sensitivity question is not a good use of the budget, and 50 paired compounds is enough for a
Spearman at this threshold.

## Two index facts confirmed, recorded so nobody re-derives them

- **The AF3 model's residue numbering is UniProt numbering**, verified residue by residue for both
  chains: chain A against P75497 (569 of 569, zero mismatches) and chain C against P75174 (561 of
  561, zero mismatches). So the pre-registered cleft residues are valid against the full-length
  sequences supplied to the engine, and no offset applies.
- **6M8Q's CPSF3 construct is a contiguous slice of Q9UKF6 beginning at residue 1**, so the
  co-crystal pocket for arm O2 carries over to the full-length sequence unchanged, and the existing
  `msa/Q9UKF6.a3m` is the right MSA for it. Arm O2 uses the **real co-crystal pocket**, not a
  predicted cavity, which makes it the best-grounded of the three pockets in this screen.

## Arm O1's pocket, fixed now

RNase J's catalytic cleft, the 20 residues nearest its 1262 A^3 cavity in the same model, by the same
geometric rule as the target's: `49, 84, 85, 92, 151, 205, 206, 241, 266, 270, 308, 311, 313, 340,
343, 345, 373, 375, 377, 401`. It contains D85 and H377, two of the four catalytic residues, which is
the check that it is the right site.
