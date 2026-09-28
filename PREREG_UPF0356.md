# PREREG UPF0356: is MG354 structurally related to YkzG, the uncharacterized protein bound to B. subtilis RNA polymerase?

Written 2026-09-28 **before any structural alignment was run**. Zero GPU. Both structures already exist:
nothing is predicted here.

## 0. Where this question came from, and why it is worth asking

`RESULT_XLGEO2.md` used *B. subtilis* RNAP 6WVK as a template and, while verifying chain identities,
found that **chain E is `YkzG` (UPF0356), a ~8 kDa uncharacterized protein bound to the polymerase.**

That is the same *kind* of object as MG354: a small, functionally uncharacterized protein associated with
a Firmicute RNA polymerase. **MG354's own structure is solved** (PDB **1TM9**, NMR, 26 models, chain A,
137 residues, Berkeley Structural Genomics), and YkzG's is solved inside 6WVK. **So the question is
answerable today by superposition, with no prediction and no compute.**

**This is not a repeat of PREREG_OMEGA.** That asked whether MG354 has an omega-family fold and answered
no, in both directions, by Foldseek. It never asked what MG354's fold *is*. **XLGEO2 also showed MG354 is
not at YkzG's site** (92.0 A, P = 0.988), so a positive answer here would mean a shared fold at a
different site, not a substitution.

## 1. Hypothesis and the honest prior

**H:** MG354 and YkzG share a fold, i.e. MG354 is a Mollicute member of the UPF0356 family.

**The prior is weak and I am stating it before the number.** Two small uncharacterized proteins near the
same machine in related phyla is suggestive, but "small protein near RNAP" is a broad class, and
`RESULT_XLGEO2.md` already showed they do not occupy the same site. **A null is the expected outcome.**

## 2. Instrument, pinned

**`TMalign.exe` from `NQ_local\foldnovelty\funding_baseline_20260926\USalign\`, USalign commit
`1fa25a95`, TM-align v20240303.** This is mandatory: `RESULT_TMALIGN_RETRACTION.md` established that this
project's own `tmalign.py` is **biased low by -0.106 overall and -0.144 in the 0.40-0.60 decision zone**,
and that the correct binary was sitting in the repo unused. **`tmalign.py` may not be used here, and no
number from it may be quoted.**

- **Query:** 1TM9 chain A, **model 1 only** (it is an NMR ensemble of 26; using one model is fixed now so
  the choice cannot be made after seeing scores). Model-to-model spread is reported as a sensitivity
  check by re-running models 2 and 3.
- **Target:** 6WVK chain E (YkzG).
- TM-score is **length-normalised by the shorter chain in both directions**; both are reported, and the
  registered decision uses the **larger** of the two, which is the permissive choice.

## 3. Registered thresholds, standard and not invented here

- **TM >= 0.5: SAME FOLD.** The conventional threshold; above it two structures are in the same fold class
  far more often than not.
- **0.4 <= TM < 0.5: AMBIGUOUS.** Reported as ambiguous, never as support.
- **TM < 0.4: NOT RELATED.** The hypothesis is refuted.

**No threshold may be moved after the number is seen.**

## 4. Mandatory controls, all three run and reported before the verdict is stated

1. **Negative control: MG354 vs omega (6WVK chain F).** `PREREG_OMEGA` already says this should be low.
   **If MG354 vs omega returns >= 0.5, the instrument or the chain assignment is wrong and NO verdict is
   reported.**
2. **Positive control: YkzG vs itself**, which must return 1.00, proving the binary runs and is parsed
   correctly.
3. **Size-matched random baseline:** MG354 against **20 randomly chosen small chains (60-150 residues)**
   from the structures already on disk. The observed MG354-YkzG score is reported **against that null
   distribution**, because TM-score between two small proteins is inflated relative to large ones and a
   raw 0.45 means little without knowing what random small pairs give.

## 5. Limits, before the numbers

1. **A shared fold is not a shared function**, and this project has said so about other people's work.
2. **YkzG is itself uncharacterized**, so even a strong hit renames the mystery rather than solving it.
   That must be said in the result, not left implied.
3. 1TM9 is an NMR ensemble; NMR models are softer than crystal structures and TM-scores against them run
   slightly low.
4. Unaudited per G6.
