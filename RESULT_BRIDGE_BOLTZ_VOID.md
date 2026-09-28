# BRIDGE on Boltz-2 is VOID at the gate, and the reason is a reusable methods finding: a contact-based interface criterion cannot grade a predictor that always docks

Run 2026-09-28 on IU Quartz H100s (free, RT Project 197). Registered in `PREREG_BRIDGE.md` and
`PREREG_BRIDGE_BOLTZ.md` (commit `911ee96`), which fixed the gate and pre-committed the response to
exactly this outcome. Results `results_bridge.json`. 15 of 20 pairs complete at scoring time; see
section 3 for why the remaining 5 cannot change the verdict.

---

## 0. The registered gate failed, and the registered consequence applies

`PREREG_BRIDGE.md`: arm **P** (the pair alone) must reproduce the original AlphaFold/FoldDock failure,
**at most 4 of 20** pairs showing an A-B interface, or "the engine has simply solved what AF2/FoldDock
could not, and the whole premise is void".

**Observed: arm P shows an interface in 13 of 15 pairs.** The scorer's own verdict, unedited:

    "verdict": "NOT INTERPRETED: gate failed, the engine solves what AF2/FoldDock could not"
    "claim_allowed": false

`PREREG_BRIDGE_BOLTZ.md` pre-committed the rest, and it binds: **"If Boltz arm P shows more than 4 of 20
interfaces, BRIDGE-on-Boltz is VOID ... I do not fall back to the AlphaFold Server P in order to rescue
B1 or B2."** No fallback is made. The 2026-09-25 AlphaFold Server arm P (2 of 20, which passed) is
reported as a separate engine's answer and is **not** merged with these arms.

## 1. The two criteria disagree, and that disagreement is the finding

| criterion | arm P with interface | gate |
|---|---|---|
| **registered primary:** >= 5 residue pairs with CB (CA for Gly) within 8 A, in >= 3 of 5 samples | **13 of 15** | **FAILS** |
| **Amendment 1** (registered 2026-09-25 20:40, before outcome data): chain-pair ipTM >= 0.5 in >= 3 of 5 samples | **1 of 15** | passes |

`results_bridge.json` flags this itself: `"primary_vs_amended_disagree": true`.

**A 13-vs-1 disagreement between two interface definitions on the same coordinates is not a tie to be
broken by preference. It says the primary criterion is measuring something else.**

**The diagnosis: Boltz-2, like AlphaFold-Multimer, always returns ONE compact assembly.** It does not have
an option to place two chains apart. So "are there 5 CB pairs within 8 A between chain A and chain B" is
close to asking "did the predictor output a complex", and the answer is almost always yes. The per-pair
table shows precisely that shape: **P, BR and CT nearly all read "yes"**, across arms that were designed
to differ.

**So the contact criterion cannot distinguish "docked" from "correctly docked" on modern co-folding
output.** ipTM can, because it is a confidence estimate rather than a geometric consequence of the output
format. **That is a reusable evaluation lesson, and it is the most valuable thing this run produced.**

**It is not a licence to switch criteria.** Amendment 1's own disclosure is recorded in the results file
and must travel with any use of it: *"Any claim resting on this rests on an AMENDED criterion, recorded
2026-09-25 20:40 before the outcome data existed."*

## 2. Under the amended criterion there is no effect either. BRIDGE is a NULL, not just void.

Even taking the criterion whose gate passes:

| test | result |
|---|---|
| B1 (BR vs P), primary | BR_only 0, P_only 1, delta **-1**, McNemar **p = 1.0**, supported **false** |
| B2 (BR vs CT), primary | BR_only 0, CT_only 1, McNemar **p = 1.0**, passes **false** |
| B1' (amended ipTM) | BR_only 0, P_only 0, delta -1, **p = 1.0**, supported **false** |

**Adding a co-dependency-selected third chain did not rescue a single pair, under either criterion.**
`RUN.md` states that B2 "is what licenses any claim about co-dependency"; B2 does not pass, on either
reading.

**So the co-dependency-picks-the-bridge idea is now dead across two independent tests**, after
`CODEP_R` (the CRISPR co-dependency signal failed to replicate in RNAi and the functional-coupling claim
was withdrawn). Two different experimental designs, two nulls. **Stop building on co-dependency as a
selector.**

## 3. Why the 5 incomplete pairs cannot rescue this

The bar is **at most 4 of 20**. Arm P already shows **13**. Even if all 5 remaining P jobs showed no
interface, P would be **13 of 20**, more than three times the bar. **The gate verdict is arithmetically
determined and will not change.** The run was allowed to finish for completeness of the record, not
because the answer was open.

## 4. What this cost and what it bought

Cost: about 60 H100 jobs, all free, plus roughly an hour of setup across three real failures
(`cleanroom/QUARTZ_GOTCHAS.md`).

Bought:
1. **A registered null on co-dependency-selected bridges**, which closes a line rather than leaving it
   ambiguous.
2. **The evaluation finding in section 1**, which applies to anyone grading co-folding output by contacts.
   This project's own `BenchPower` audit is about exactly this class of error, and this is a fresh instance
   of it found in our own pre-registration.
3. **Confirmation that running all three arms on one engine was the right call.** Had BR/CT been run on
   Boltz against the AlphaFold Server arm P, B1 would have compared 12 Boltz interfaces against 2
   AlphaFold ones and looked like a spectacular positive. **That confound would have produced a false
   result, and `PREREG_BRIDGE_BOLTZ.md` is the only reason it did not.**

## 5. Limits

- 15 of 20 pairs at scoring; the gate is decided, the exact B1/B2 counts are not final.
- **8 of the 20 pairs are mitoribosomal**, a weakness `PREREG_BRIDGE.md` registered in advance. With a
  null result it does not matter, but no general claim is made either way.
- The contact criterion's failure is argued from the output format plus the 13-vs-1 split, not from an
  independent ground-truth set. **Demonstrating it properly would need pairs with known-correct and
  known-incorrect interfaces scored under both criteria.** That is a real experiment and it has not
  been run.
- Unaudited per G6.
