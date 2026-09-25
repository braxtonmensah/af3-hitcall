# Y Combinator application draft — Early Decision for Students (NOT submitted)

**Deadline: November 2, 2026, 8pm PT** for a guaranteed decision by **December 11, 2026**.
Early Decision: funded on acceptance, batch deferred until after graduation (2029).
Apply at ycombinator.com/apply. Edit into your own voice; do not send my wording verbatim.

**Honest framing note.** YC funds companies, not findings. The company is the triage platform. The
RNase J complex is the proof it works. Do not pitch "I discovered a protein complex"; pitch "AI proposes
millions of protein interactions and nobody can tell which are real. I can, and I measured it."

---

## Company name
Suggestions: Interfold, Nulla Bio, Triage Bio. Pick something you can say out loud.

## Describe what your company does in 50 characters or less
`Tells drug teams which AI protein predictions are real`  (53 — trim to 50)

## What is your company going to make?

AI models now predict protein interactions for entire genomes, but nobody can tell which predictions
deserve a real experiment. On a published genome-wide screen, the confidence score separates
already-solved complexes well (AUROC 0.85) and is near chance (0.57-0.71) on interactions never solved
before, which is exactly the class anyone doing discovery cares about. So teams either trust everything
and waste bench money, or trust nothing and throw away real biology.

We build the triage layer. Given predicted complexes, we return a calibrated probability that the
interface is actually right, by combining structure prediction with orthogonal public evidence
(in-cell crosslinking, size-exclusion proteomics) that most groups never touch.

## How far along are you?

Working pipeline, and it is validated prospectively rather than on a benchmark we could have tuned.
I took protein-complex predictions frozen in 2021 and scored them against structures released in
2022-2026, which no model had seen. Confident predictions of never-before-solved complexes had the
correct interface **81% of the time in human (n=146)** and **89% in yeast (n=84)**, against **2%** for
low-confidence predictions. Twenty-one hypotheses were pre-registered in git before the data were
joined; eight came back negative and are published as negative.

Then I used it to find something. In *Mycoplasma pneumoniae* the essential ribonuclease RNase J turns
out to form a 2:2 complex with an essential, catalytically dead paralog that nobody had characterised.
Five independent lines agree: AlphaFold3 (ipTM 0.84), in-cell crosslinks from two different chemistries
(6/6 satisfied, and only the 2:2 arrangement explains all six), published size-exclusion data putting
both proteins in the same 298 kDa fraction, and transposon data showing both genes are essential. A
length-matched control protein does not bind (0.12).

## What do you understand about this business that others don't?

Two things, both measured rather than assumed.

First, the field reports one accuracy number for these screens, and it is an average of two populations
that behave completely differently. Splitting them changes what the tool is for.

Second, everyone reads the low-confidence tail as "the model is wrong." It is not. It is
**recall failure, not precision failure**. Confident novel predictions are usually right; what the
screens miss are small contacts inside large assemblies that only exist when other subunits are present
(misses touch a third chain across 27% of their interface versus 11% for hits, with interfaces one
third the size). That means the fix is in the input, not in better confidence scores. I tested four
proposed score-based fixes and all four failed, which is why I know.

## Who are your competitors, and who might become competitors?

DeepMind, Isomorphic, and every AI-bio platform company generate predictions. Almost nobody sells
*triage* of predictions. The closest work is interface-restricted confidence scores (ipSAE, LIS) and
integrative modelling groups. I tested ipSAE and LIS directly; both collapse to zero in pooled
predictions and neither recovers the novel class.

## How do you make money?

Drug and target-discovery groups pay to avoid dead-end experiments; one wasted structural biology
programme costs far more than the tool. Start as paid validation projects on a customer's own
prediction set, then productise as a service over their pipeline.

## Why did you pick this idea to work on?

I wanted to know whether AI protein predictions could be trusted, could not find anyone who had tested
it the honest way, and had the public data to do it. Then it found real biology, which told me the
method was worth building into something.

## Founders

Solo founder, sophomore at Indiana University, self-taught in computational structural biology.
**Early Decision**: fund now, batch after graduation.

---

## Before you submit

- YC wants a 1-minute founder video. Film it plainly: what it does, the 81%/2% number, the RNase J case.
- Do not overclaim: the RNase J complex is computationally solved and supported by published orthogonal
  data. There is no new wet-lab experiment yet. Reviewers punish overclaiming and reward precision.
- Have the preprint public before you submit. It is the evidence the whole application rests on.
- Acceptance odds are ~1%. Apply anyway; it costs an evening and the decision is free.
- Note for diligence: the commercial product must not be built on AlphaFold Server output (non-commercial
  terms). The Boltz-2 clean-room rebuild exists for exactly this and is already written.
