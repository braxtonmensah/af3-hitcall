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


---

## Creative search, 2026-09-25: what the AMR funding ecosystem actually pays for

I checked the categories outside conventional grants: DeSci/BioDAOs, European antibacterial incubators,
and AMR-specific accelerators. No new mechanism delivers $300k in 30 days. But the search produced one
structural insight that changes strategy.

**The AMR money is gated on having a compound, not a target.**

| Programme | Money | What it needs | Us |
|---|---|---|---|
| **PACE** (Pathways to Antimicrobial Clinical Efficacy) | **up to £1M** | Hit-to-Lead or Lead Optimisation. Academia and SMEs **worldwide**, no UK partner needed | Need a compound |
| **CARB-X** Novel Chemistry | large | "novel chemistry scaffolds with activity against validated bacterial targets" | Need a chemistry plan |
| **ENABLE-2** | free platform access, non-dilutive, keep your IP | Compounds with MIC <= 32 ug/mL, **European institutions only**, Gram-negatives/S. aureus/E. faecium | **Not eligible**: US-based, no compounds, wrong organism |
| **BARDA BAA** | varies, rolling to 2028, worldwide | nonclinical efficacy in animal models | Far beyond |
| **INCATE** Stage I / II | **EUR 10k** / up to **EUR 250k** | early-stage ventures worldwide, rolling | Stage I plausibly eligible now |
| **MicroDAO** (AMR-focused DeSci) | unclear, early | decentralised grants, "faster funding decisions", welcomes work overlooked by institutions | Worth an enquiry |

**The implication.** We have a validated target and no compound, which is the one thing almost nobody
funds. Converting the target into even a weak compound moves us from "no eligible programmes" to
"eligible for PACE (£1M) and CARB-X".

**And that conversion is cheap, roughly $1-3k, not a grant:**
1. Boltz-2 virtual screen against the interface (MIT licence permits this; AlphaFold Server's terms
   explicitly forbid it). GPU cost ~$30-100.
2. Buy the top 10-20 predicted binders from a catalogue supplier. Typically $50-150 each.
3. One MIC assay panel against *M. pneumoniae* at a CRO. Hundreds to low thousands.
   Caveat: Mycoplasma is slow and fastidious to culture, so get a written quote first, and note
   *M. genitalium* is harder than *M. pneumoniae*.

If any compound shows activity, PACE and CARB-X open, and both are an order of magnitude above SBIR.
If none does, that is a real answer too and it cost ~$2k instead of a year.

**This is the highest-leverage spend available on this project.** It is not fast money, but it is the
step that converts an unfundable asset into a fundable one.
