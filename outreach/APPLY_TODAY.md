# Two applications you can send today

**Neither is submitted. Both are yours to send.** Together they are $11,000 and about 20 minutes.

Nothing pays out today. What you can do today is start the clock on the two fastest-moving sources
that fit you, and Z Fellows in particular is known for quick turnarounds on rolling applications.

---

## 1. Z Fellows — $10,000

**Form:** https://docs.google.com/forms/u/0/d/1z5HG9Pj0hIxS2oZL_wcJS5QqDZlcVbkhYGHp5Kp_IGM/viewform
**Rolling, no deadline. No need to quit school, no company required, any age.**

**The terms, read them before you accept anything.** The $10,000 is an *optional* investment at a
$1B valuation cap that converts at your next priced round. At that cap the dilution is on the order of
0.001%, so it is close to free money, but it is an investment and not a grant. You can also take part
with no investment and no equity at all. Nothing obliges you to accept the money to join the cohort.

### The framing problem, read this before writing anything

**Z Fellows funds builders, not papers.** They are betting you will build something. A submission that
reads "I did a rigorous study and wrote it up" is a category error there, however good the study is.

So invert it. **The method is the product; the paper is the proof it works.** Same facts, different
ask. Labs are drowning in AI-predicted interactions with no way to decide which deserve an experiment,
and you built the thing that decides, then validated it prospectively. The registry of 6,010 confident
never-solved pairs is the first output of that tool, not a byproduct of a paper.

**What are you working on?**

> Deciding which AI-predicted protein interactions are worth a wet-lab experiment.
>
> AlphaFold and its successors now predict interactions for entire genomes, tens of thousands at a
> time. An experiment to test one costs weeks and real money, and the confidence scores come with no
> interpretation, so almost all of them go untested. There is no triage layer. I built one.
>
> Then I did the thing nobody had done: I measured whether it works, prospectively. I took confident
> predictions published in 2021, before the answers existed, and scored them against structures solved
> between 2022 and 2026. Confident predictions of complexes never solved before had the right
> interface 81% of the time in human (n=146) and 89% in yeast (n=84), against 2% for low-confidence
> ones. It held after removing everything with a similar known structure, against a shuffled control,
> under a second independently written scorer, and across a grid of thresholds.
>
> The first output is a ranked registry of 6,010 confident, never-solved human complexes with the
> evidence attached. I used it myself to find one: an essential 2:2 RNase J complex in Mycoplasma
> pneumoniae whose partner subunit has lost all four catalytic residues, supported by five independent
> published lines including in-cell crosslinks from two chemistries. Both subunits are essential and
> the interface is only 24.6% identical to the closest human protein, so it is an antibacterial target.

**Why you?**

> I did all of it as an economics sophomore with no lab, no faculty sponsor, no funding and no
> institutional compute. Public data and a laptop. I pre-registered all 21 hypotheses in version
> control before joining the data, `git log` proves the order, and I report the 8 that came back
> negative. When a check failed I recorded the retraction instead of quietly dropping the claim. That
> discipline is the product's moat: anyone can generate predictions, almost nobody can tell you which
> to trust and show their work.

**What would you do with the money and the week?**

> Turn the pipeline into something other people can run. Re-implement it on Boltz-2, which is MIT
> licensed, so the output is free for anyone including companies to build on. Extend the registry to
> every organism with public in-cell crosslinking data. Then take it to the labs and biotechs that
> are currently guessing, and find out what they would pay for a ranked, evidence-backed shortlist.

**Links:** repository, preprint. *Both need to be public first. This is the bottleneck.*

---

## 2. 1517 Fund, Medici Project — $1,000

**Page:** https://www.1517fund.com/medici-project
For young people doing zero-to-one work, North America and EU. Small, fast, low friction.

Use a compressed version of the same text. The angle 1517 selects for is doing serious work outside
an institution, which is literally your situation, so lead with that rather than with the biology:

> I am an economics sophomore with no lab and no funding who measured how often confident AI protein
> predictions are actually right, prospectively, using only public data and a laptop, and then used the
> method to identify an essential bacterial enzyme complex that had never been described. Everything
> was pre-registered before the data were joined, including the eight tests that failed.

---

## The thing gating both

Both forms ask for links. Right now the repository is private and the preprint is not posted, so both
applications have to say "trust me" instead of "check it yourself." For a result whose entire selling
point is that you can verify the order of events in `git log`, that is most of the pitch thrown away.

`LICENSE` is written and the repository is secret-scanned and clean. What remains is your read-through
of the preprint and making the repo public.

---

## What not to say

Do not write "new protein fold" or "completely new biology." RNase J is a known
metallo-beta-lactamase fold. The new part is the assembly architecture and the measured catalytic
loss. Your own foldnovelty work showed TM-score novelty does not discriminate, so that claim is both
wrong and contradicted by your own data. The defensible version is stronger anyway, because it
survives being checked.
