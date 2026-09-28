# XLGEO3: the XLGEO2 result is NOT a HelD artefact. The omega-site refutation reproduces to within 0.2 A on an independent conformational state

Run 2026-09-28. Pre-registered in `PREREG_XLGEO3_ROBUSTNESS.md` at commit `0152f34`, **before any
distance was computed on 6WVJ**, with all four possible readings written in advance. Zero GPU.

## 0. Why this check existed

A literature lane found that **6WVK, the template that passed XLGEO2's gate, is *B. subtilis* RNAP bound
to HelD** (Newing et al., *Nat Commun* 2020;11:6420), which **widens the primary channel from 21 A to
47 A**. The deflationary alternative was obvious and had to be tested: **6WVK may have passed simply
because a HelD-opened clamp is roomier, and a roomier structure satisfies more 30 A restraints.**

6WVJ is the elongation complex from the **same study, same lab, same organism, without HelD**.

## 1. Result: registered reading 1. The conclusion stands and is strengthened.

| template | conformational state | control gate | MG354 sites to omega | P(null <= obs) |
|---|---|---|---|---|
| *E. coli* **4YG2** | **sigma70 holoenzyme**, X-ray 3.70 A | 11/17 = **64.7%**, fail | not computed (gate failed) | - |
| *B. subtilis* **6WVK** | **HelD complex, clamp opened to 47 A** | 11/12 = **91.7%**, pass | **69.3 A** | **0.994** |
| *B. subtilis* **6WVJ** | **elongation complex, no HelD** | 13/15 = **86.7%**, pass | **69.5 A** | **0.993** |

**The omega distance reproduces to within 0.2 A, and the null probability to within 0.001, across two
structures whose primary channel differs by 26 A.** The refutation of the omega *site* is robust to the
single largest conformational difference available in this organism's RNAP structures.

**The Firmicute-template advantage is also real and not a HelD artefact**: both *B. subtilis* templates
clear the gate (86.7%, 91.7%) while the *E. coli* holoenzyme does not (64.7%).

**The primary got tighter, not looser:** max pairwise among the three mappable MG354 sites is **38.5 A**
on 6WVJ against 53.0 A on 6WVK. **The 3-of-5 caveat from `RESULT_XLGEO2.md` section 2 still governs and
is unchanged**: a maximum over a subset can only be smaller, so this remains a lower bound and "TIGHT" is
still optimistically biased. Two templates agreeing does not fix a missing-data bias.

## 2. Two corrections to my own earlier pre-registration

1. **`PREREG_XLGEO.md` section 1 calls 4YG2 "*E. coli* RNA polymerase core". It is the sigma70
   holoenzyme** (Murakami, *J Biol Chem* 2013;288:9126-9134, PMID 23389035), at 3.70 A, with sigma70 in
   the cleft. The attempt-1 failure was therefore measured against a structure I had mis-described.
2. **The attempt-1 "gate failure" was never statistically distinguishable from a pass.** 11/17 = 64.7%
   has a **95% CI of [38.3%, 85.8%], which contains 70%.** The registered rule was correctly applied and
   the decision stands, **but "E. coli failed" must never be stated without this sentence.**

## 3. What the literature says the gate should have been

- Interchain crosslink satisfaction in a large benchmark: **~90%** (Bartolec et al., *PNAS*
  2023;120:e2219418120, 28,910 unique residue pairs).
- **In-cell** analogues, the closest published comparison to our control arm: **71.4%** (YugI, 10/14) and
  **75.0%** (YabR, 6/8), O'Reilly et al., *Mol Syst Biol* 2023;19:e11544.
- 30 A Ca-Ca is the correct and already-generous cutoff for DSS/DSSO (Merkley et al., *Protein Sci*
  2014;23:747-759, MD over 807 proteins gives 26-30 A).
- False identifications cannot explain six violations: at the source data's 5% residue-pair FDR, about
  **1 of 17** links is expected wrong.
- RNAP conformational range is large enough to matter: pincer-to-pincer **81 A open, 69 A closed, 64 A
  collapsed** (Chakraborty et al., *Science* 2012;337:591-595).

**So a 70% bar sits at the bottom of the in-cell range and is defensible as a target, but at n = 12-17 it
is a coin-flip instrument**: if the true per-link rate were 0.80, a 70% gate rejects a correct model
**10.6% of the time at n=17 and 20.5% at n=12**.

## 4. Status

- **STANDS, now on two conformational states:** MG354's crosslink sites are **not** at the omega site.
  Combined with the dead fold argument (`PREREG_OMEGA`) and the dead YkzG fold
  (`RESULT_UPF0356_REFUTED.md`), **omega is finished and so is the UPF0356 idea.**
- **STILL BIASED, unchanged:** the "one pocket" reading rests on 3 of 5 sites.
- **No further template.** `PREREG_XLGEO2.md` and `PREREG_XLGEO3_ROBUSTNESS.md` both bind here.
- Unaudited per G6.
