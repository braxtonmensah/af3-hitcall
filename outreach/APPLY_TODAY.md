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

### What to write

**What are you working on?**

> I audit AI protein-structure predictions to work out which ones are worth doing an experiment on.
>
> AlphaFold and similar models now predict protein interactions for entire genomes, tens of thousands
> of predictions at a time. Nobody knows which to trust, so most go untested. I measured it properly
> instead of guessing: I took confident predictions published in 2021, before the answers existed, and
> scored them against protein structures that were solved between 2022 and 2026.
>
> Confident predictions about complexes that had never been solved before had the right interface 81%
> of the time in human (n=146) and 89% in yeast (n=84), against 2% for low-confidence predictions. The
> result held after I removed everything with a similar known structure, against a shuffled control,
> under a second independently written scoring method, and across a grid of thresholds. I
> pre-registered all 21 hypotheses in version control before joining the data, and I report the 8 that
> came back negative.
>
> Then I used it to find something. In Mycoplasma pneumoniae, the essential enzyme RNase J pairs with
> MPN621, a protein nobody has characterised, as a 2:2 four-part complex. Five independent published
> lines agree, including in-cell crosslinks from two different chemistries and mass-spec that puts both
> proteins at the same 298 kDa peak. MPN621 has lost all four of RNase J's catalytic residues, so it
> looks like a dead enzyme that holds the complex together. Both subunits are essential, which makes
> the interface an antibacterial target, and it is only 24.6% identical to the closest human protein.

**Why you?**

> I did all of it as an economics sophomore with no lab, no faculty sponsor, no funding and no
> institutional compute. Public data and a laptop. The reason to believe any of it is that I wrote down
> what I expected before I looked, and the repository's commit history proves the order. When checks
> failed, I recorded the retraction rather than quietly dropping the claim.

**What would you do with the money and the week?**

> Re-run the whole pipeline on Boltz-2, which is MIT licensed, so the results are free for anyone
> including companies to build on. AlphaFold Server output is non-commercial and explicitly forbids
> use in ligand-binding prediction, which is why I built a clean-room version from public sequences.
> Then extend it to every organism with public in-cell crosslinking data and publish a ranked list of
> confident, never-solved complexes with the evidence attached.

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
