# PREREG XLGEO3: is the XLGEO2 result an artefact of HelD-induced clamp opening? A robustness check, not a retry

Written 2026-09-28 **before any distance was computed on 6WVJ**, and immediately after learning two facts
about the templates that I did not have when writing `PREREG_XLGEO.md` or `PREREG_XLGEO2.md`.

## 0. This is NOT a third bite at the gate, and here is why that distinction is real

`PREREG_XLGEO2.md` says: "**If the B. subtilis gate also fails, the structural route is ABANDONED. No
third template.**" That clause exists to stop template-shopping after a FAILURE. **6WVK passed.** This
document is the opposite move: it tests whether a **passing** result is an artefact, and it can only
weaken or overturn a conclusion I already published, never rescue a failed one.

**The new information, from a literature lane run after XLGEO2:**

1. **`4YG2` is NOT "E. coli RNA polymerase core" as `PREREG_XLGEO.md` section 1 states.** RCSB records it
   as the ***sigma70 holoenzyme***, X-ray, **3.70 A** (Murakami, *J Biol Chem* 2013;288:9126-9134,
   PMID 23389035). Sigma70 occupies the cleft. **That is a factual error in my pre-registration** and is
   corrected here rather than quietly.
2. **`6WVK`, the template that PASSED, is *B. subtilis* RNAP bound to HelD** (Newing et al., *Nat Commun*
   2020;11:6420, PMID 33339820), which the authors report **widens the primary channel from 21 A to 47 A**
   between beta2 lobe P242 and beta-prime clamp helix N283. **It is plausibly the most clamp-distorted
   RNAP structure in the PDB.**

**So the obvious alternative explanation for XLGEO2 is deflationary: 6WVK passed the 91.7% gate not
because a Firmicute template maps better, but because a HelD-opened clamp is simply roomier, and a roomier
structure satisfies more 30 A restraints.** If that is true, the omega-site conclusion computed on it is
suspect, because omega sits against beta-prime near the clamp.

## 1. Template

**PDB 6WVJ**, the *B. subtilis* RNAP **elongation complex from the same study, same lab, same organism,
without HelD**. Verified composition before writing this: chain **C** = beta, chain **D** = beta-prime,
chain **F** = **omega**, plus DNA/RNA chains N/R/T. It is the matched control for 6WVK by construction.

## 2. Everything inherited unchanged

Same query sequences, same alignment, same 30 A cutoff, same **70% gate** on the 20 RpoB-RpoC control
crosslinks, same primary (**max pairwise Ca-Ca among the mapped MG354 sites**) with the **same
thresholds**, same 1,000-draw composition-matched null for the omega secondary.

## 3. REGISTERED READINGS, all four written before the numbers

1. **Gate passes on 6WVJ and omega is still far (P high, sites farther than null): the XLGEO2 conclusion
   STANDS and is strengthened**, because it survives on a non-distorted structure.
2. **Gate passes but the omega result REVERSES or weakens: `RESULT_XLGEO2.md` section 3 is RETRACTED**,
   and the omega-site refutation is withdrawn. **I report the retraction as the headline, not buried.**
3. **Gate FAILS on 6WVJ while it passed on 6WVK: this is evidence FOR the deflationary explanation** and
   the XLGEO2 gate pass is reported as **conformation-dependent, not template-quality-dependent.** In that
   case **no MG354 number from either B. subtilis template may be quoted**, and the structural route is
   closed as `PREREG_XLGEO2.md` intended.
4. Whatever happens, **both templates' numbers are reported side by side.** Neither is selected.

**No further template after this one, pass or fail.** That is binding.

## 4. Also registered: the gate threshold itself is now known to be shakier than it looked

The same literature lane found published interchain satisfaction rates of ~90% (Bartolec et al., *PNAS*
2023;120:e2219418120) but in-cell analogues at **71-75%** (O'Reilly et al., *Mol Syst Biol* 2023;19:e11544,
YugI 10/14, YabR 6/8), and my own binomial arithmetic puts **11/17 = 64.7% at a 95% CI of [38.3%, 85.8%]**,
which **contains 70%**.

**Therefore: the XLGEO attempt-1 "gate failure" was never statistically distinguishable from a pass.**
That does not change the registered decision, which was correctly applied, but it must travel with any
statement that E. coli "failed". **It is recorded now, before seeing 6WVJ's number, so it cannot be
deployed selectively afterwards.**
