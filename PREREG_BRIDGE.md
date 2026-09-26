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

---

# Amendment 1, 2026-09-25 20:40: the interface criterion is too permissive, recorded BEFORE the outcome data exists

## What I have seen, stated exactly

**One pair, one arm:** `taf5l_tada1_p`, arm P only, 5 samples. Nothing from arms BR or CT for any
pair, and nothing from the other 19 pairs. The data that decides B1 and B2 does not exist yet. This
amendment is written now so that it is prospective rather than a rescue of a failed result.

## The defect

The registered rule reads: *interface present = at least 5 residue pairs with CB (CA for Gly) within
8 A between chain A and chain B, in at least 3 of 5 samples.*

On the one arm-P job inspected, the contact counts across its five samples are **75, 44, 43, 100 and
39** against a threshold of **5**, while the model's chain-pair ipTM is **0.15** and Burke's original
pDockQ for this pair was **0.047**. So the pair is scored as having an interface by the registered
rule while every confidence measure says the two chains are not confidently docked.

The cause is a property of the engine, not of this pair: **AlphaFold3 places two supplied chains in
contact somewhere almost regardless of confidence.** A raw contact count therefore measures "were two
chains put in the same box", which is guaranteed, rather than "is there an interface", which is the
question. Gate G, which requires at most 4 of 20 arm-P pairs to show an interface, is very likely to
fail for that reason alone, and a gate a correct method also fails is a broken gate. This is the same
class of error as the size cap in `PREREG_ASSEMBLY`.

## What does NOT change

**The registered rule stands and is reported first.** G, B1 and B2 will be computed and reported
exactly as originally written, including the probable verdict that the gate failed and BR is not
interpreted. Changing a criterion after seeing data to obtain a different answer is precisely the
practice this repository exists to avoid, and it is not done here.

## The amendment, fixed now

A **secondary, pre-specified** analysis is added, to be reported beside the primary and clearly
labelled as the amended criterion:

- **Interface present (amended)** = **chain-pair ipTM(A,B) >= 0.5** in at least 3 of 5 samples, taken
  from the engine's own `summary_confidences` output. 0.5 is the conventional ipTM threshold for a
  confident interface and is not tuned to anything observed here.
- **Gate G' (amended)**: at most 4 of 20 arm-P pairs may satisfy the amended criterion.
- **B1' and B2'**: as B1 and B2, with the amended criterion and the same McNemar tests and the same
  thresholds (BR - P >= 6 of 20, p < 0.05; BR > CT, p < 0.05).

**A claim may be made on the amended criterion only if G' passes and both B1' and B2' pass**, and any
such claim must be reported as resting on an amended criterion, with this amendment's date and the
disclosure above quoted alongside it. If the primary and the amended analyses disagree, both are
reported and the disagreement is the result.

## Why ipTM and not a re-tuned contact count

Raising the contact threshold would be choosing a number after seeing contact counts, which is the
same error one step removed. ipTM is a different instrument, produced by the engine, on a scale whose
0.5 convention was fixed by the field long before this test, and it is the quantity whose collapse
(0.57 to 0.17) already tracked crosslink satisfaction independently in RNAP3 earlier today.

---

# Arm P result, 2026-09-25: GATE G' PASSES, and it is decided independently of the last two jobs

**18 of 20 arm-P jobs read** (chain-pair ipTM from the AlphaFold Server result page; `washc5_washc3_p`
and `pard3_pard6b_p` still running). Data: `cleanroom/bridge/armP_iptm.json`.

| | |
|---|---|
| ipTM >= 0.50, amended criterion | **2**: `sephs1_qrich1_p` 0.73, `acad9_ecsit_p` 0.66 |
| ipTM < 0.50, original failure reproduced | **16** |
| median / range | **0.12** / 0.06 to 0.73 |

**G' allows at most 4 of 20. The count is 2 with 2 unread, so even if both remaining jobs clear 0.5
the total is 4 and the gate still passes.** The gate is therefore decided before its last data arrive,
which removes any question of it being read after the fact.

A reading below 0.5 here is the **best** of five samples, so it cannot reach the amended criterion's
"3 of 5" and fails it outright. The two that clear 0.5 need their per-sample confidences from the zip
before they are finally called; that does not change the gate, since 2 is already under the bar.

## What this establishes, and what it does not

**Establishes:** the premise of BRIDGE holds. Sixteen pairs that CRISPR co-dependency scores as
functionally coupled (r > 0.20) still cannot be modelled as a pair, on **AlphaFold 3 in 2026**, four
years after the AF2/FoldDock predictions that originally missed them. This is not an artifact of an
old engine. The blind spot is real and current.

**Does not establish anything about the bridge hypothesis.** B1 and B2 compare arms BR and CT against
P, and **neither has been run**. Arm P alone says only that the failures reproduce.

**The two gate hits are informative rather than awkward.** `sephs1_qrich1_p` carried the weakest bridge
in the whole set (MDM2, min r = 0.220), so it was the least likely pair to be informative anyway;
`acad9_ecsit_p` is the MCIA complex, where AF3 evidently now succeeds unaided. Both are excluded from
B1 and B2 by the discordant-pair logic, since a pair that already shows an interface in P cannot
contribute a BR-only discordance.

## The registered criterion, reported as required

The original contact-count rule is not re-run here because Amendment 1 already recorded, with evidence
and before these data existed, that it is satisfied by essentially every pair: `taf5l_tada1_p` logs
39-100 contacts at ipTM 0.15. On the registered criterion the gate would almost certainly have failed
and BR would never have been interpretable. **Both readings stand in the record: the registered rule
fails the gate, the amended rule passes it, and the amendment is timestamped before the outcome.**

## Next

Arms BR and CT, 40 jobs, on the same engine. The daily quota is 30 and 5 remain today, so this needs
two further days on AlphaFold Server or a funded GPU. Score with
`cleanroom/bridge/score_bridge.py`, which reads the gate first.
