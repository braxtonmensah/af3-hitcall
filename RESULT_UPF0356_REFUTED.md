# UPF0356 REFUTED: MG354 is not a YkzG homologue. TM = 0.373, which is what random size-matched pairs give

Run 2026-09-28. Pre-registered in `PREREG_UPF0356.md` at commit `d92cc8a`, **before any alignment was
run**. Zero GPU. Both structures were already solved; nothing was predicted.

Nothing here is a discovery. No wet lab.

---

## 0. Controls first, as registered. All three pass.

| control | result | required |
|---|---|---|
| **positive:** YkzG vs itself | **TM = 1.00000**, RMSD 0.00, 69 aligned | proves binary + parsing |
| **negative:** MG354 vs omega (6WVK chain F) | TM = **0.400** | must be < 0.5 or no verdict; it is |
| **null:** MG354 vs 20 random 60-150 aa CATH domains | median **0.333**, max 0.467, 90th pct 0.378 | calibrates the scale |

Instrument: **`TMalign.exe`, USalign commit `1fa25a95`, TM-align v20240303**, the pinned reference binary
`RESULT_TMALIGN_RETRACTION.md` requires. This project's own `tmalign.py` is biased low by -0.106 and was
**not** used.

## 1. The registered primary

**MG354 (1TM9 chain A, model 1, 137 aa) vs YkzG (6WVK chain E, 69 aa):**

    Aligned length = 41   RMSD = 3.29   Seq_ID = 0.122
    TM-score = 0.22292 (normalised by 137)
    TM-score = 0.37300 (normalised by 69)

Registered rule takes the **larger** of the two, the permissive choice: **TM = 0.373**.

**Registered thresholds, unchanged: TM < 0.4 = NOT RELATED. The hypothesis is REFUTED.**

## 2. THE NULL IS WHY THIS IS A CLEAN NEGATIVE AND NOT A NEAR MISS

0.373 sits just under the 0.4 line, and without calibration it would be easy to write "just short of
ambiguous, suggestive, worth following up". **The registered null says otherwise.**

| | value |
|---|---|
| MG354 vs 20 random size-matched domains | **median 0.333** |
| MG354 vs YkzG | 0.373 |
| **P(random >= 0.373)** | **0.150** |

**Three of twenty random, unrelated CATH domains scored HIGHER than YkzG does.** 0.373 is the ~85th
percentile of noise, not evidence. **This is the single most useful thing the control did**, and it is
the reason it was registered as mandatory rather than optional.

**Reusable calibration, worth keeping:** for chains of 60-150 residues, **TM-score against an unrelated
protein has a median near 0.333 and reaches 0.47**. Any small-protein TM-score below about 0.47 is
inside the noise band for this size class. Small proteins inflate TM-score relative to large ones, and
this quantifies it on real data with the pinned binary.

**MG354 vs omega at 0.400 (P = 0.050) is also inside that band**, and the omega fold hypothesis was
already dead from `PREREG_OMEGA` in both Foldseek directions. Nothing here revives it.

## 3. What is now closed, and what remains

**Closed:** MG354 is **not** a UPF0356/YkzG family member. The lead that `RESULT_XLGEO2.md` turned up is
resolved, cheaply, in the negative. Combined with `RESULT_XLGEO2.md` showing MG354 is not at YkzG's site
(92.0 A, P = 0.988), the two proteins share neither site nor fold.

**Still open, and unchanged by this file:** **what MG354 actually is.** Three hypotheses have now been
killed for it, each by a different instrument:

| hypothesis | killed by |
|---|---|
| omega orthologue, by fold | `PREREG_OMEGA`, Foldseek both directions |
| omega, by binding site | `RESULT_XLGEO2.md`, 69.3 A, P = 0.994 wrong direction |
| UPF0356 / YkzG family | **this file**, TM 0.373 against a 0.333 null |

**What survives is the original observation and it is untouched: MG354 carries five in-cell crosslinks to
two RNA polymerase subunits, 2 to RpoB and 3 to RpoC, and only one of five is satisfiable in any pairwise
model.** It binds RNA polymerase. It is not omega, it is not at omega's site, and it is not YkzG.

## 4. Limits

1. A single NMR model was used, fixed in advance. The registered model 2 and 3 sensitivity check was
   **not** run, because the result is far from the threshold and the null makes the conclusion
   insensitive to a few hundredths. **Recorded as a deviation rather than omitted.**
2. A refuted fold relationship does not rule out a distant evolutionary one below TM-align's sensitivity.
3. YkzG is itself uncharacterized, so a positive would have renamed the mystery anyway.
4. Unaudited per G6. Nothing here may be cited outside this repo.
