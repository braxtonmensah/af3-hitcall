# The pitch

Every claim below is true and checkable. That is what makes it usable; nothing here needs inflating.

---

## The one-liner

**AlphaFold tells you a million protein pairs might interact. Nobody could tell you which ones to
believe. I measured it, prospectively, and built the triage layer. It is right 81% of the time where
the field assumed it was unreliable.**

## The 30-second version

Structure prediction won a Nobel Prize and then created a problem nobody solved: the models now
propose interactions for entire genomes, tens of thousands at a time, and every proposal costs weeks
and thousands of dollars to test. Labs are sitting on prediction lists they cannot act on.

The field's own benchmarks made it worse. They report one accuracy number averaged over two completely
different populations: pairs that already have a solved structure, and pairs that have never been
solved. The first group is the easy one and it is also the useless one, because it is already known.
The second group is the entire point of running a screen, and on it the reported numbers look bad,
AUROC 0.71, so people discount exactly the predictions they should be acting on.

I ran the test nobody had run. I took confident predictions published in **2021**, before the answers
existed, and scored them against protein structures solved in **2022 to 2026**. Not a retrospective
benchmark, a frozen forecast checked against the future.

**Confident predictions of never-before-solved complexes had the right interface 81% of the time in
human and 89% in yeast. Low-confidence predictions: 2%.** That is a 40x separation that the aggregate
statistic completely hides.

The conclusion is not "these models are unreliable." It is **"these models are high-precision and
low-recall,"** which is the opposite operational advice. If a screen is confident about a never-solved
pair, run the experiment.

## Proof it works: I used it and found a drug target

I pointed it at *Mycoplasma pneumoniae* and it surfaced a complex nobody had described: the essential
ribonuclease **RNase J bound to MPN621 as a 2:2 heterotetramer**, out of 113,050 candidate pairs.

Then I tried to kill it, and could not:

- Dedicated prediction hits ipTM 0.84 and satisfies **all six in-cell crosslinks in all five samples**
- The 2:1 alternative strands three of those crosslinks at 51 to 63 A, so only the tetramer explains the data
- Crosslinks from **two different chemistries** agree on the same residue pairs
- Published mass-spec puts both proteins at the same 298 kDa peak, which excludes 1:1 and fits 2:2
- **Both subunits are essential**
- MPN621 has lost **all four** of RNase J's catalytic residues. It is a dead enzyme that holds the complex together.

**Why this is a drug target:** both subunits essential means breaking the complex kills the organism.
The closest human protein, CPSF73, keeps three of four catalytic residues, so anything aimed at the
active site is a selectivity disaster. But the **interface is only 24.6% identical to the human
protein**. The hard target is the selective one. That inverts the usual medicinal chemistry logic and
it is the whole reason this is interesting.

*M. pneumoniae* causes community-acquired pneumonia and macrolide resistance is rising.

## Why me

Economics sophomore. No lab, no faculty sponsor, no funding, no institutional compute. Public data and
a laptop.

And the part that actually matters: **I pre-registered all 21 hypotheses in version control before
joining the data, and I report the 8 that came back negative.** `git log` proves the order. When a
check failed I recorded the retraction instead of quietly dropping the claim.

That is the moat. Anyone with a GPU can generate predictions. Almost nobody can tell you which to
trust and hand you the receipts. In a field where reproducibility is the central complaint, a method
whose ordering is externally verifiable is a different kind of asset.

## What it becomes

The first output already exists: a ranked registry of **6,010 confident, never-solved human complexes**
with the evidence attached. Right now it is a file. It should be a product.

Every structural biology group, every AI-drug-discovery company, and every protein-design startup has
the same problem and currently solves it by guessing or by gut. The deliverable is a ranked,
evidence-backed shortlist with a measured precision number attached. Nobody else can quote a measured
precision, because nobody else ran the prospective test.

With money and time: reimplement on Boltz-2 (MIT licensed, commercially clean), extend the registry to
every organism with public in-cell crosslinking data, and take it to the labs that are guessing today.

---

## What I will not claim, and why it matters to you

RNase J is a **known** metallo-beta-lactamase fold. This is not a new fold, and I will not say it is.
The novel contributions are the 2:2 architecture, the validated model, the measured catalytic loss,
the stoichiometry argument and the interface map. The interaction itself appears, undiscussed, in a
2020 crosslinking table.

I say this because the whole product is "you can trust this number." An applicant who oversells by one
sentence is an applicant whose 81% you should not believe either. The restraint is the credential.
