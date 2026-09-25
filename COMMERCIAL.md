# Monetising the RNase J : MG423 work (science routes only) — 2026-09-25

Written after checking the actual licences, patent law, and funder criteria. Nothing here was submitted.

## The three shapes science money can take

1. **Non-dilutive grants and prizes.** No IP required. The only route that reaches $100k+ for someone
   with no lab.
2. **Services.** Consulting on AI-prediction triage. Needs a public credential first (preprint).
3. **Products / licensing.** Needs either patentable IP (we have none) or a clean, useful asset
   (the Boltz-2 rebuild creates one).

## Ranked, with what each actually requires

| Route | $ | Timeline | Hard requirement we don't yet meet |
|---|---|---|---|
| **NIH SBIR Phase I** | **~$323k** (cap $400k) | 9-15 mo | US for-profit small business; **PI employed >50% time by that business** (conflicts with full-time enrolment); ~15-20% success |
| **CARB-X Novel Chemistry for AMR** | large | 2026 EOI window (8-22 Apr) **closed**; next round 2027 | Funds chemistry against a **validated** target + a defined chemistry plan. We have no wet-lab validation and no compounds |
| **Emergent Ventures** | $1k-50k | 1-3 mo, rolling | Just the application. Best near-term fit |
| **Astera / Speculative Technologies / Renaissance Philanthropy** | $10k-500k | 3-9 mo | Fund independent science; need a preprint and a credible plan |
| **Consulting** (triage AI-predicted complexes for biotechs) | $100-200/hr | after preprint | Reaching $100k means 500-1000 hours. Not feasible alongside full-time school |
| **Patent / licensing the complex** | **~$0** | n/a | Natural complex + coordinates are not patentable subject matter (Myriad 2013). Unfixable |

**Honest conclusion:** $100k from this science inside 12 months is unlikely. The credible near-term
number is **$10k-50k** from grants. The routes that reach $100k+ (SBIR, CARB-X) need either a company
with a >50%-time PI, or a wet-lab-validated target. Both are year-2 items, and both need the same two
things first.

## The two things that gate everything

**1. A clean asset.** Every AF3 file here is non-commercial and barred from ligand/docking use. The
clean-room rebuild (`cleanroom/run_boltz.py`) fixes this permanently: Boltz-2 (MIT) + CC0 crosslinks +
CC-BY sequences. Inputs are generated. It needs a rented GPU (~$15-30, roughly 4 chains x 2,260 tokens
x 4 jobs on an 80 GB card).
**Do not run this on Big Red 200 or Quartz** — IU policy UA-24 would then claim the IP.

**2. Target validation.** CARB-X's criterion is a *validated* target. Cheapest credible evidence, in order:
  - **Essentiality** of RNase J and MG423 in Mycoplasma (literature; Glass 2006 and Lluch-Senar 2015
    supplements. **Open item** — the gene-level tables are in supplementary files I could not parse).
    If MG423 is essential *despite* having lost all four catalytic residues, that is a strong argument
    its scaffolding role is the druggable point.
  - **Pull-down + size measurement** confirming the 2:2 complex. Needs a lab partner.
  - Only then: Boltz-2 virtual screen against the interface, then compounds.

## What I would do, in order

1. **Preprint + public repo.** Establishes priority, and is a precondition for grants 3 and 4. It also
   forfeits foreign patent rights, which costs nothing here because nothing is patentable.
2. **Emergent Ventures application** (draft in `outreach/`). Highest probability per hour spent.
3. **Clean-room Boltz-2 run** (~$15-30 of GPU) so the asset is unrestricted before any company talk.
4. **Resolve essentiality** from the two supplements.
5. **Find a wet-lab partner.** This is the real gate on CARB-X and SBIR money. An IU sponsorship gets
   the experiment done but moves IP ownership to IU; an outside lab collaboration does not.

## Standing constraint

You very likely own this work (no IU funds, lab or compute were used). Keep it that way if the
commercial option matters: personal storage, personal or rented compute, no faculty-sponsored runs.
