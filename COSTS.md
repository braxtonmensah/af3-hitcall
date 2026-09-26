# What this costs, itemised (2026-09-25)

Real prices, checked today. Nothing has been bought and no GPU has been started.

## 1. GPU — much cheaper than I first said

Live RunPod prices, on-demand:

| GPU | VRAM | $/hr | Fits |
|---|---|---|---|
| **RTX 4090** | 24 GB | **$0.34** | the virtual screen (1 protein + 1 ligand, ~600 tokens) |
| L40S | 48 GB | $0.79 | screen, comfortably |
| A100 SXM | 80 GB | $1.39 | the 4-chain heterotetramer re-runs (2,260 tokens) |

**Virtual screen, 300 compounds + 50 decoys + a selectivity arm:** each job is small, roughly 30-60 s
once the protein MSA is cached. Call it 4-8 hours on a 4090 including setup.
**Estimated cost: $2-5.** My earlier "$30-100" was wrong; I was pricing the wrong hardware.

**Clean-room heterotetramer rebuild** (4 jobs, 2,260 tokens each) on an A100: ~2-3 hours, **$3-5**.

**Total GPU to do everything: under $10.**

### The free option, and the decision that was actually taken

**Superseded on 2026-09-25. Read `IP_RECORD.md`, which is the contemporaneous record and governs.**

This section used to say "do not use Quartz, pay the $10 on RunPod". The screen was subsequently
moved onto Quartz. The reasoning, recorded before the run, is that UA-24's definition of "University
Resources" explicitly excludes "resources routinely made available for general educational, research,
and administrative purposes", and Quartz is free to every student, self-service, needs no sponsor and
no allocation. Big Red 200 stays off limits because it requires both.

**What is genuinely unresolved, stated plainly.** UA-24's exclusion has no bright-line test, so this
is a reading, not a ruling. Two things keep the exposure small today: nothing here is patentable as
it stands (a natural complex and its coordinates are not patentable subject matter, *Myriad* 2013),
and the screen uses Boltz-2 (MIT) rather than AlphaFold Server output. The question only becomes live
if the screen yields a method-of-use candidate. **The open item is a written confirmation from IU's
Innovation and Commercialization Office, which costs nothing.** Get that before any compound work, not
after.

**If you want the question to disappear entirely**, the RunPod path still exists and still costs about
$10. That buys certainty rather than compute.

## 2. Compounds

The screen has not run, so **there is no drug list yet.** That is the honest position: which compounds
to buy is the screen's output, and it needs the GPU first. What is fixed now is the cost structure.

**Library the screen draws from:** 3,273 approved small molecules from ChEMBL, already downloaded.

**Suppliers for approved drugs in small quantities:**

| Supplier | Typical price, 5-10 mg | Notes |
|---|---|---|
| MedChemExpress | ~$50-120 | broad approved-drug coverage, small sizes available |
| Cayman Chemical | ~$50-150 | good for older approved drugs |
| Selleck Chemicals | ~$70-150 | sells an FDA-approved library too |
| MilliporeSigma | ~$60-250 | widest catalogue, often pricier |
| TargetMol | ~$50-100 | often cheapest |

**Quantity needed is tiny.** CO-ADD asks for **1 mg**. NIAID will specify, but MIC work is milligram
scale. The smallest vial most suppliers sell already exceeds what you need, so buy the smallest size.

**Cost scenarios:**

| Scenario | Compounds | Cost |
|---|---|---|
| Minimum viable test | top 5 hits | **$250-600** |
| Recommended | top 10-15 hits + 3 negative controls | **$650-1,800** |
| If CC4CARB supplies them | any | **$0** (Gram-negative focus; fit needs checking) |

Buy only after the screen's decoy null and CPSF73 selectivity check. If nothing beats the decoys, buy
nothing: that is a valid result for the price of $5 of GPU.

## 3. Assay

| Route | Cost | Covers our organism? |
|---|---|---|
| **NIAID Preclinical Services** | **$0** | asking — this is the open question in the draft email |
| **CO-ADD** | **$0** | no, ESKAPE panel only; broad activity check |
| Commercial CRO, *M. pneumoniae* MIC | quote needed | yes, but Mycoplasma is slow and fastidious; get it in writing |

## 4. Bottom line

| Item | Cost |
|---|---|
| GPU, everything | under $10 |
| Compounds, recommended tier | $650-1,800 |
| Assay | $0 if NIAID or CO-ADD accept |
| **Total to measured antibacterial activity** | **roughly $700-1,800** |

That is the full cash cost of reaching measured antibacterial activity. It is not $300k, and it never
was.

**CORRECTED 2026-09-25. This paragraph used to say that was "the evidence that PACE (up to GBP 1M,
open worldwide) and CARB-X require". That is wrong and it must not be repeated in an application.**

Checked against the current calls: **PACE's 2025 antibacterial therapeutics call is restricted to
drug-resistant Gram-negative priority pathogens** (Enterobacteriaceae prioritising *E. coli* and
*K. pneumoniae*, *A. baumannii*, *P. aeruginosa*) and explicitly excludes Gram-positives,
mycobacteria, and Gram-negatives outside its target product profiles. **CARB-X's eligibility runs off
the CDC 2013 and WHO 2017 priority lists**, and its 2026 round is scoped to priority Gram-negatives
plus neonatal sepsis. ***M. pneumoniae* is on none of those lists.**

**And this is not fixable by changing organism within the same idea: RNase J is absent from *E. coli*
and most Gammaproteobacteria**, which is PACE's entire target list. The target family does not exist
in the pathogens these two funders pay for.

The one candidate here with even a plausible route is ***H. pylori***, which was High priority on WHO
2017 (which CARB-X still references) and is Gram-negative. That is a reason it is worth considering
on the science, recorded in `cleanroom/TARGET_EXPANSION.md`; it is **not** a reason to pick a target,
and "which funder" should never be that reason.

Sources: [PACE 2025 call](https://iuk-business-connect.org.uk/opportunities/pace-pathways-to-antimicrobial-clinical-ef%EF%AC%81cacy-2025-antibacterial-therapeutics/),
[CARB-X 2026 round](https://carb-x.org/carb-x-news/carb-x-launches-2026-funding-round-to-address-global-burden-of-amr/).

## 5. What is left, in order

| # | Step | Blocked on | Cost |
|---|---|---|---|
| 1 | Send the NIAID email (`outreach/EMAIL_NIAID.md`) | **you** | $0 |
| 2 | Run the virtual screen | **your go-ahead on ~$5** | $2-5 |
| 3 | Review shortlist: decoy null + CPSF73 selectivity | me, after step 2 | $0 |
| 4 | Get supplier quotes for the named hits | me (prices) + you (ordering) | $0 |
| 5 | Buy compounds | **you** | $650-1,800 |
| 6 | Ship to NIAID and/or CO-ADD | **you** | shipping only |
| 7 | If activity: apply to PACE and CARB-X | both | $0 |
| — | Also open: preprint sections, YC application (**Nov 2**), Emergent Ventures, RESCUE's last pairs | | |

**Two things only you can do right now:** send the NIAID email, and approve ~$5 of GPU.
