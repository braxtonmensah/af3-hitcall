# The no-lab route to a compound, and how to fund it (2026-09-25)

> **CORRECTION, 2026-09-26, and it voids the seven-figure route described below.** PACE's 2025
> antibacterial therapeutics call is restricted to drug-resistant **Gram-negative** priority pathogens
> and explicitly excludes Gram-positives and mycobacteria. CARB-X's eligibility runs off the CDC 2013
> and WHO 2017 lists. ***M. pneumoniae* is on neither list**, and this cannot be fixed by changing
> organism, because **RNase J is absent from *E. coli* and most Gammaproteobacteria**, which is PACE's
> entire target list. The target family does not exist in the pathogens these funders pay for.
>
> Everything below that treats PACE or CARB-X as a reachable destination is therefore wrong. The
> reasoning is kept for the record rather than deleted. *H. pylori* is the only candidate in this
> project with even a plausible route, being WHO 2017 High priority and Gram-negative. See `COSTS.md`.


You were right that a lab is not the blocker, and I was wrong to treat it as one. Free wet-lab capacity
exists and is open to you. But one limit is physical and no amount of computation removes it.

## What computation can and cannot do

**Can, and some is already built:**

| Step | Tool | Status |
|---|---|---|
| Rank purchasable compounds against the interface | Boltz-2 affinity, MIT licence | **built** (`cleanroom/vscreen.py`, 3,273 approved drugs, decoy null, CPSF73 selectivity arm) |
| Design novel molecules | generative models (REINVENT, etc.) | possible, needs setup |
| Check they can actually be made | retrosynthesis prediction (AiZynthFinder, ASKCOS) | possible, free/open |
| Predict toxicity and absorption | ADMET models | possible, free |
| Predict human off-target risk | sequence/structure comparison | **done**: interface only 24.6% identical to CPSF73 |

**Cannot, ever:**
- Turn a SMILES string into a physical molecule.
- Show that a compound kills bacteria. That requires bacteria.
- Satisfy any funder that asks for "activity". PACE and CARB-X both require measured activity, and no
  amount of predicted affinity substitutes.

So the honest statement is: a virtual lab produces **ranked hypotheses**, and the funding gate is
**measured activity**. The good news is that the measurement is free.

## Free wet-lab capacity, verified

**1. NIAID Preclinical Services — In Vitro Assessment of Antimicrobial Activity.**
Their words: *"NIAID's free preclinical services... Product developers from academia, nonprofit
organizations, industry, and government can request preclinical services. You need not be a grantee of
NIAID or another NIH Institute or Center."*
- Cost: **free**. NIAID pays its contractor; you get the report and the data.
- IP: a Nonclinical Evaluation Agreement covers confidentiality and IP, per organisation, five years.
- Process: contact a DMID program officer → NCEA → request via their portal → review → contractor runs
  the study. Contact for this service: **invitro@mail.nih.gov**
- Review criteria that matter for us: within DMID mission, **sufficient quantity and quality of product
  available**, **preliminary data adequate to advance the product**, and a plan for what comes next.
- **Implication: they assay compounds you supply. You must still supply the compound.**
- **Caution: NCEAs are per organisation.** If you sign as an IU affiliate, IU is the organisation and
  IU's IP policy is in play. If you want to own it, sign as your own LLC.

**2. CO-ADD (University of Queensland) — free antimicrobial screening.**
- Free screening for academic groups worldwide; send **1 mg** of pure compound.
- Panel: 5 ESKAPE pathogens plus 2 fungi. **Mycoplasma is not on that panel**, so it tests general
  antibacterial activity, not our target organism. Useful, not decisive.
- No IP claims, and there is a confidentiality window so you can publish or patent hits first.
- 300,000+ compounds screened from 45 countries.

**3. CC4CARB — Chemistry Center for Combating Antibacterial Resistant Bacteria.**
Provides *"synthesis, acquisition, and distribution of rationally designed, focused libraries... at no
cost to the global scientific community."* This is the closest thing to free compound synthesis.
Focused on Gram-negative programmes, so fit for a Mycoplasma target needs checking.

## The actual cost, once the free services are used

| Item | Cost |
|---|---|
| Virtual screen (GPU) | $30-100 |
| Compounds, 10-20 approved drugs from a catalogue | $500-2,000, or possibly $0 via CC4CARB |
| In vitro antimicrobial assay | **$0** via NIAID PCS |
| Mycoplasma-specific MIC, if NIAID cannot cover it | quote first; Mycoplasma is slow and fastidious |

**Total realistic cash: a few hundred to ~$2,000.** Not $300k. The expensive-looking path is mostly free.

## So how is it funded?

The sequence matters, because funders pay for the *next* step, not the current one.

1. **Now, self-funded (~$100).** Run the virtual screen. Output: a ranked shortlist that survives a
   decoy null and a selectivity check, or an honest negative.
2. **Now, free.** Email invitro@mail.nih.gov and a DMID program officer to ask whether a Mycoplasma
   in vitro antimicrobial assessment is within scope, and what preliminary data they would need. This
   costs one email and tells you whether the free route is open before you spend anything.
3. **~$500-2,000, self-funded or a small grant.** Buy the top compounds. Emergent Ventures ($5-50k,
   rolling) comfortably covers this and is the right size for it.
4. **Free.** Submit compounds to NIAID PCS and/or CO-ADD.
5. **If anything shows activity**, that is measured antibacterial activity against an essential,
   structurally validated target. That is the entry criterion for **PACE (up to GBP 1M, open worldwide
   to academia and SMEs)** and **CARB-X**. This is the only route on the board that reaches seven
   figures, and steps 1-4 cost under $2k.
6. **If nothing shows activity**, you have a real negative result, a publishable one, for under $2k.
   PPI interfaces are hard; most are not druggable by small molecules. Expect this outcome.

## What this changes

The blocker was never the lab and never $300k. It is **one email to NIAID** and **a few hundred dollars
of compounds**. The large funding follows measured activity, and cannot precede it.
