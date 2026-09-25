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

### The free option, and why it is not free

Quartz (IU) has 4x V100 nodes free to undergraduates and would run the screen fine.
**But using IU compute triggers IU policy UA-24**, which claims patentable IP created with significant
use of university resources. For a $2-5 saving you would hand IU any claim arising from a hit.
**Recommendation: pay the $10 on RunPod.** Use Quartz only if you decide the academic route (Biswas,
faculty sponsor) is the plan and IU involvement is fine.

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

That is the full cash cost of reaching the evidence that PACE (up to GBP 1M, open worldwide) and CARB-X
require. It is not $300k, and it never was.

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
