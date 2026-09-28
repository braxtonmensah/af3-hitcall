# XLGEO2: the gate passes on a Firmicute template, the omega SITE is refuted, and the "one pocket" verdict is downward-biased and must not be quoted alone

Run 2026-09-28. Pre-registered in `PREREG_XLGEO2.md` at commit `05ba0ce`, before any distance was
computed on this template. Results `results_xlgeo2.json`. Zero GPU.

Nothing here is a discovery. No wet lab. Read section 2 before quoting section 1.

---

## 0. The gate passes, and the a priori reason for the template was right

| template | control links mappable | within 30 A | median |
|---|---|---|---|
| *E. coli* 4YG2 (attempt 1) | 17 of 20 | 11 of 17 = **64.7%**, gate FAILS | 20.6 A |
| ***B. subtilis* 6WVK (attempt 2)** | 12 of 20 | **11 of 12 = 91.7%, gate PASSES** | 21.4 A |

The Firmicute template was registered in advance on phylogeny (Mollicutes are degenerate Firmicutes) and
it behaves better, 91.7% against 64.7%. **The tradeoff is coverage**: it maps only 12 of the 20 control
crosslinks against E. coli's 17.

**Chain identity was verified before use, and the check mattered.** `PREREG_XLGEO2.md` guessed chain E was
omega. **It is not: chain E is `YkzG`, a UPF0356 uncharacterized protein, and omega is chain F.** The
secondary was computed on F. Deviation from the letter of the prereg (which said to drop the secondary if
E was not omega) recorded here: using the correctly identified chain serves the registered intent, which
was to avoid computing on the wrong chain.

## 1. The registered primary fires TIGHT

| | C1060 | B262 | C375 |
|---|---|---|---|
| **C1060** | 0.0 | 41.3 | 51.7 |
| **B262** | 41.3 | 0.0 | 53.0 |
| **C375** | 51.7 | 53.0 | 0.0 |

**Maximum pairwise Ca-Ca = 53.0 A**, which is inside the registered `<= 60 A: TIGHT, one pocket` band.

## 2. THE CAVEAT THAT GOVERNS SECTION 1: only 3 of 5 sites mapped, and the statistic is biased by that

**RpoB 289 and RpoC 171 are UNMAPPABLE on this template.** The registered primary was the maximum
pairwise distance among **five** sites; it was computed over **three**.

**A maximum over a subset can only be smaller than the maximum over the full set.** Dropping two sites can
never increase the spread and can easily decrease it. **So 53.0 A is a LOWER BOUND on the true five-site
spread, and the TIGHT verdict is optimistically biased by construction.** The true value could sit in the
WEAK band or past the 105 A INCOMPATIBLE line; this file cannot distinguish those.

**Therefore: the registered verdict fired, and the registered verdict is not trustworthy here.** It is
reported because it was registered, and it is immediately qualified because the qualification is
arithmetic, not opinion. **Do not quote "one pocket, 53 A" without this paragraph.**

The registered conformational caveat also still applies: 6 of 17 real in-cell crosslinks exceeded 30 A in
the E. coli crystal, so a single conformation may not satisfy crosslinks drawn from a population of states.

## 3. The clean result: MG354's sites are NOT at the omega site

Secondary outcome, exploratory as registered, against a 1,000-draw composition-matched null (2 on RpoB,
3 on RpoC):

| reference | centroid distance | null median | P(null <= observed) |
|---|---|---|---|
| **omega (chain F)** | **69.3 A** | 46.3 A | **0.994** |
| YkzG (chain E), post-hoc | 92.0 A | - | 0.988 |

**The five sites are FARTHER from omega than 99.4% of random site sets.** The effect is significant in
the direction **opposite** to the omega hypothesis.

**This closes the omega idea from the other side.** `PREREG_OMEGA` already killed the fold argument (no
omega-family hit in either direction, Foldseek both ways). The site argument was the only version left,
and it is now refuted rather than merely unsupported: MG354's crosslinks do not point at where omega sits
on the polymerase. **MG354 binds RNA polymerase somewhere else.**

**Unlike section 1, this conclusion is robust to the missing sites**, because a centroid over 3 of 5
sites is an unbiased-in-direction summary and the observed distance is far outside the null in the wrong
direction for the hypothesis. Still exploratory, and still not a claim about function.

## 4. A lead this turned up, recorded and NOT tested here

**The *B. subtilis* RNA polymerase in 6WVK has a small uncharacterized protein bound to it: `YkzG`
(UPF0356, ~8 kDa).** That is structurally the same *kind* of object as MG354, an uncharacterized small
protein sitting on a Firmicute RNAP, and its binding site is solved.

**Section 3 shows MG354's sites are not at the YkzG site either (92.0 A, P = 0.988)**, so MG354 is not
simply the Mycoplasma YkzG occupying the same pocket. Whether the two are nonetheless related in
sequence or fold is **untested here and must be registered before it is run.**

## 5. What this does and does not establish

**Does:** the omega *site* hypothesis is refuted. The Firmicute template is the right one and passes the
mapping gate at 91.7%.

**Does NOT:** it does not establish that one MG354 copy can satisfy all five crosslinks, because two
sites are missing and the statistic is biased toward saying yes. **RNAP3 remains the decisive test**,
because a three-chain model has every residue present and needs no cross-species mapping at all.

- Unaudited per G6. Nothing here may be cited outside this repo.
