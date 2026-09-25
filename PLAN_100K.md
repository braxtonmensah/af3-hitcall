# The $100k plan, from this science (2026-09-25)

Not a guarantee. A stacked portfolio where one hit clears $100k and the expected value is ~$60k.
Every mechanism below is real, verified this session, and open to a solo undergraduate founder.

## The two blockers I wrongly assumed, now cleared

- **SBIR PI.** The rule is the PI must not be **employed** >50% elsewhere. Being a full-time student is
  not employment. A student founder can be PI on an NIH SBIR. Phase I is **~$323k** (cap $400k).
- **No lab needed to start.** IndieBio provides the lab. Investment up to **$525k** ($250k initial for
  ~8%), ~60 companies funded a year.

## The stack

| # | Mechanism | Amount | When | P(hit) | Needs |
|---|---|---|---|---|---|
| 1 | Emergent Ventures | $1k-50k | rolling, apply Oct | ~25% | Application (drafted) |
| 2 | Astera / Speculative Technologies / Renaissance Philanthropy | $10k-500k | rolling | ~10% | Preprint |
| 3 | **NIH SBIR Phase I** | **~$323k** | deadlines Jan 5 / Apr 5 / Sep 5 | ~15% | LLC + preprint + PI = you |
| 4 | **IndieBio (SOSV)** | **up to $525k** | batch applications | ~2% | LLC + pitch |
| 5 | CARB-X Novel Chemistry for AMR | large | EOI ~Apr 2027 | low without wet data | Validated target + chemistry plan |

Expected value ≈ **$60k**, with a realistic single-hit path above $100k via #3.
Cost to play: ~$30 GPU + ~$100 LLC filing + application time.

## Sequence

**Now (this week, ~$30)**
1. Clean-room Boltz-2 run (`cleanroom/run_boltz.py`, inputs ready). Rented GPU only, never IU hardware.
2. Close the essentiality question (see below).

**October (free)**
3. Preprint + public repo. Establishes priority; required by #2-#5. Costs nothing in patent terms
   because nothing here is patentable.
4. Submit Emergent Ventures (draft in `outreach/`).

**November-December (~$100)**
5. Form an Indiana LLC. Required for #3 and #4. Keep it personally owned, no IU involvement, so
   ownership stays yours under UA-24.
6. Draft the SBIR Phase I aim page around the RNase J : MG423 interface as an antibacterial target.

**January-April**
7. Submit SBIR Phase I (Jan 5 or Apr 5 deadline).
8. Apply to IndieBio.
9. CARB-X EOI if wet-lab validation has landed.

## The one open data item, and why it matters most

**Is MG423 essential despite having lost all four catalytic residues?**
If yes, an essential protein whose only apparent job is holding RNase J together is a textbook
protein-protein-interface target, and it converts "interesting complex" into "validated target" for
#3 and #5. Three ways to get it, in order of effort:
1. Lluch-Senar et al. 2015 (MSB, PMC4332154) Dataset EV: per-gene E / F / NE calls for every MPN gene.
   Fetch the Dataset EV xlsx from embopress.org and look up MPN_280 and MPN_621.
2. Glass et al. 2006 (PNAS) supporting Table: the 100 disrupted (non-essential) M. genitalium genes.
   If MG_139 and MG_423 are absent from that list, both are essential.
3. Email either corresponding author. Undergraduates get answers more often than they expect.

## Wet-lab validation, the real gate on the big money

Cheapest credible experiment: co-purify tagged RNase J and show MG423 comes with it, then size the
complex (SEC or mass photometry) to confirm 2:2. That is days of work in a lab that already grows
Mycoplasma. Routes: a collaborator who wants co-authorship, a CRO, or IndieBio's own labs (#4).
Note the trade-off: an IU faculty sponsor gets it done but moves IP ownership to IU (UA-24).
