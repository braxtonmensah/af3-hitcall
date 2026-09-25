# Pre-registration 28: can co-dependency pick the subunit that rescues a failed pairwise prediction? (BRIDGE)

Written 2026-09-25, **before any structure in this test has been predicted** and before any distance
or interface score in it has been computed. The candidate pairs and their predicted bridges were fixed
by `analysis_codep.py` and `codep_bridges.csv` and are committed with this file.

## Why

Three results in this repository say the same thing from three directions:

- **H1**: the screen is strong on complexes with structural precedent and near-chance on the rest.
- **COOP arm H**: the misses are small, non-autonomous interfaces inside large assemblies. A pairwise
  calculation cannot see a contact that only exists when a third subunit is present.
- **CODEP** (today): the functional signal behaves identically. Confident predictions beat
  low-confidence ones inside annotated complexes (+0.0585) and not at all outside them (+0.0047).

**RESCUE** already showed that supplying the real bridging subunit helps (interim: bridge 6/10 vs pair
3/10 vs non-bridging control 4/10, n = 10, not significant). But RESCUE chose each bridge from curated
knowledge of the complex, so it cannot be applied to a pair whose complex nobody has annotated, which
is precisely the class where the method fails.

**This test asks whether the bridge can be chosen from data instead of from knowledge.** CRISPR
co-dependency is available genome-wide for 17,916 genes and needs no curation. If it picks bridges
that work, the method's documented blind spot becomes addressable at scale.

That the picker already recovers PRKCI for PARD3-PARD6B (the PAR polarity complex), TADA2B for
KAT2A-TADA3 (the SAGA HAT module), WASHC4 for WASHC5-WASHC3 and NDUFS1 for NDUFS3-NDUFV2 is
encouraging and is **not** evidence: those are recognitions after the fact, and recognition is what
this project keeps proving is worthless without a denominator.

## Population (fixed, committed in `codep_bridges.csv`)

The **top 20 rows** of `codep_bridges.csv` by `r_pair`. Each is a human protein pair that:

- Burke et al. modelled with **pDockQ < 0.10** (AlphaFold pairwise failure),
- has **no co-complex structure** (`int3D_model_structure == 0`),
- has CRISPR co-dependency **r > 0.20**, about twice the pre-registered null 95th percentile,
- has both genes **selectively essential** (mean gene effect > -0.35, at least 15 lines below -0.6,
  dependency in at most 25% of lines),
- and has a **bridge C** = the gene maximising `min(r(A,C), r(B,C))` over all genes passing the
  variance floor, excluding A and B.

## Arms (three predictions per pair, 60 jobs)

| Arm | Chains |
|---|---|
| **P** (pair) | A + B |
| **BR** (bridge) | A + B + C, where C is the co-dependency bridge |
| **CT** (control) | A + B + D |

**D, the control third protein, is fixed now by rule, not by choice:** among genes that are
selectively essential by the same definition and whose length is within 25% of C's, D is the one whose
`min(r(A,D), r(B,D))` is **closest to zero from above**, excluding any gene within the same CORUM
complex as A, B or C. So D is a same-shaped, equally essential protein that co-dependency says is
*not* coupled to this pair. If no D satisfies the length window, it is widened in 10% steps and that is
reported per pair.

Boltz-2 (MIT) or AlphaFold3, one copy of each chain, 5 diffusion samples, seed 28. The same engine is
used for all three arms of a pair; the engine is recorded per pair.

## Outcome

For each job, on the **A-B pair only** (the third chain is context, never scored):

- **Interface present** = at least **5 residue pairs** with CB (CA for Gly) within **8 A** between
  chain A and chain B, in at least 3 of the 5 samples.
- **ipTM(A,B)** as reported by the engine for that chain pair.

## Tests

**G (gate, read first).** Arm **P** must reproduce the original failure: at most **4 of 20** pairs may
show an A-B interface in arm P. If more do, then Boltz-2/AF3 simply solves what AF2/FoldDock could not,
the premise is wrong, and BR is reported but **not interpreted** as a rescue.

**B1 (primary).** Number of pairs with an A-B interface in **BR** minus in **P**.
- **Supported** if BR exceeds P by at least **6 of 20** and the exact McNemar test on the discordant
  pairs gives p < 0.05.
- **Refuted** if BR is less than or equal to P.
- **Inconclusive** otherwise.

**B2 (specificity, required for any claim).** BR versus **CT**.
- The claim "**co-dependency picks the bridge**" requires BR > CT by McNemar p < 0.05. If BR beats P
  but not CT, the honest conclusion is that **any** third chain helps, which is a statement about
  multi-chain context and not about co-dependency, and it must be written that way.

**B3 (reported, not decisive).** Mean change in ipTM(A,B) from P to BR and from P to CT.

## Consequences fixed in advance

- If B1 and B2 both pass, the claim is: *co-dependency selects a rescuing subunit without prior
  knowledge of the complex, in the class where pairwise prediction fails.* That is written into
  `RESULTS.md` and the preprint, with the n and the McNemar p.
- If B1 passes and B2 fails, the claim is only: *adding a third chain helps.* No credit to
  co-dependency.
- If B1 fails, the non-autonomy explanation survives (COOP arm H is independent of this) but
  **co-dependency-guided rescue is dead** and must not be proposed again in this project, including in
  any grant application.

## Limitations, stated before the result

- 20 pairs is small. The mitoribosome is over-represented in the top of `codep_bridges.csv`, so a
  success may be a statement about one assembly rather than a general method. The per-complex
  breakdown is reported and no general claim is made if more than half the successes are mitoribosomal.
- Co-dependency cannot distinguish a physical bridge from a pathway partner, so a working bridge does
  not prove C touches A or B.
- A trimer is still a fragment of a large assembly. Failure of BR does not show the pair is not real;
  it may only show that three chains are not enough.
- The engine differs from the AF2/FoldDock that produced the original failure, which G is there to
  detect but cannot fully remove.
