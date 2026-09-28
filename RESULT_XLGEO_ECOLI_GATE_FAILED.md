# XLGEO attempt 1 (E. coli 4YG2): the GATE FAILS at 64.7%. No MG354 number is reported

Run 2026-09-28. Pre-registered in `PREREG_XLGEO.md` at commit `4bb5f7d`, before any distance was
computed. Code `xlgeo.py`, zero GPU.

## 0. The gate, and the registered consequence

> **Registered gate: at least 70% (14 of 20) of the mappable control crosslinks must be within 30 A
> Ca-Ca in the template. Below that ... NO MG354 number is reported.**

| quantity | value |
|---|---|
| RpoB -> 4YG2 chain C (beta) | 1,211 of 1,391 residues mapped, BLOSUM62 score 2038 |
| RpoC -> 4YG2 chain D (beta') | 1,144 of 1,290 residues mapped, score 2294 |
| control crosslinks mappable | **17 of 20** (3 unmappable) |
| **within 30 A** | **11 of 17 = 64.7%** |
| median control distance | **20.6 A** |

**64.7% < 70%. The gate fails. No MG354 distance is reported, and none was inspected.**

## 1. The failure is not an alignment failure, and that matters

A median control distance of **20.6 A** against a 30 A cutoff says most of the mapping is right; 11 of
17 land comfortably inside. The failure is carried by **6 real in-cell crosslinks that exceed 30 A in a
crystal of the core enzyme.**

**The most likely reading is conformational, not methodological.** RNA polymerase is a famously mobile
machine: the clamp swings, and core, holoenzyme and elongation complexes differ substantially. In-cell
crosslinks are collected from a population of states; a single crystal is one state. A static structure
is not guaranteed to satisfy every crosslink from a dynamic machine.

**THIS APPLIES TO RNAP3 TOO, and should be recorded before RNAP3 returns.** RNAP3 asks a predictor for
*one* static three-chain model and scores the same control crosslinks with the same 30 A rule and the
same 0.7 bar. **If 6 of 17 RpoB-RpoC crosslinks are unsatisfiable in a real crystal, RNAP3's control arm
may fail for reasons that have nothing to do with MG354.** That is a limitation of the pre-registered
design, and finding it before the run is worth more than finding it after.

## 2. What was NOT done

- **No MG354 distance was computed or looked at.** The script returns before that block when the gate
  fails, by construction.
- The threshold was **not** adjusted. It stays at 70%.

## 3. Attempt 2, and the multiplicity is stated plainly

`PREREG_XLGEO2.md` registers one further attempt with a **Firmicute** template, *B. subtilis* 6WVK,
because *Mycoplasma* are degenerate Firmicutes and *E. coli* is a gamma-proteobacterium. **That reason is
phylogenetic and holds independently of this failure**; E. coli was chosen first only because 4YG2
contains omega, which serves the exploratory secondary outcome rather than the primary.

**Multiplicity, acknowledged rather than hidden: this will be two templates tried against one 70% gate.**
`PREREG_XLGEO2.md` therefore pre-commits that **if the B. subtilis gate also fails, the structural route
is abandoned and no third template is tried.**

- Unaudited per G6.
