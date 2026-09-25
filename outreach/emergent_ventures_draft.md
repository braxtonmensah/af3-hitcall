# Emergent Ventures application draft (NOT submitted)

Apply at: https://mercatus.tfaforms.net/5099527
Edit this into your own words before sending. Every number below is in the repo and reproducible.

---

## About me

I'm Braxton Mensah, a sophomore at Indiana University studying economics. I taught myself to audit
AI protein-structure predictions using only public data and a laptop.

## The project

AI models like AlphaFold now predict protein interactions for whole genomes, but nobody knows which
predictions to trust. I tested that directly. I took confident predictions made in 2021, before the
structures existed, and checked them against complexes solved in 2022 to 2026. In human and yeast, the
confident predictions of never-before-solved complexes had the right interface 80 to 90% of the time,
against about 2% for low-confidence ones. That result held after removing anything with a similar
solved structure, against a random baseline, and with a second, independent scoring method. Everything
was pre-registered before I looked at the outcome.

Then I used the method to find biology. In Mycoplasma, the essential RNA-degrading enzyme RNase J pairs
with MG423, a protein no one has characterised. Two independent in-cell crosslinking experiments,
AlphaFold 3 run directly on the pair, and a structural template all agree on a four-part complex, with
all six crosslinks satisfied and an unrelated control protein failing. MG423 has lost all four of
RNase J's catalytic residues, so it looks like a dead nuclease that holds the complex together.

To be precise about novelty: the pairing appears, undiscussed, in a 2020 crosslinking dataset, and a
2011 paper noted in one sentence that MG423 might be an inactive paralog. What is new is the four-part
architecture, a validated 3D model, the catalytic-site loss, and the method that found it.

## What the grant would do

$[AMOUNT, e.g. 10,000-15,000] for GPU compute and time to:
1. Re-run the pipeline with an openly licensed model (Boltz-2, MIT) so the results are free for anyone,
   including companies, to build on.
2. Apply it to every organism with public in-cell crosslinking data, and publish a ranked list of
   confident, never-solved complexes with the evidence for each.
3. Release the code and a preprint, and hand the best candidates to labs that can test them.

## Why it scales

The method needs no lab, only public data, so it can run across every sequenced organism. The output is
a short list of real, testable complexes out of hundreds of thousands of AI predictions.

## Links

[Public GitHub repo URL, once public]
[Preprint URL, once posted]
