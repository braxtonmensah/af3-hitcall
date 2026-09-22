# V. cholerae pooled-AF3 pilot: how to run it

Pre-registered in `../PREREG_VIBRIO.md` (design, positives, precedent classes and scoring are fixed).
There are 85 jobs: 24 competence/chitin proteins plus 60 random decoys, 4,000-aa pools.

## Option A: AlphaFold Server (free, no sponsor needed, about 3 days)

1. Sign in at https://alphafoldserver.com with your Google account.
2. Upload `jobs/afserver_batch01.json` (30 jobs) and submit them. The free tier is about 30 jobs
   per day.
3. Next day: `afserver_batch02.json`; day after: `afserver_batch03.json` (25 jobs).
4. Download every finished job (each is a `fold_vc_pilot_XXX.zip`) into one folder, e.g.
   `C:\Users\bmens\NQ_local\af3-hitcall\vibrio\results\`.
5. Run: `python analyze.py C:\Users\bmens\NQ_local\af3-hitcall\vibrio\results`

AF Server output is non-commercial (AlphaFold Server Output Terms). That is fine for academic work.

## Option B: Big Red 200 (after sponsorship)

Every pool is <= 4,000 tokens, so each fits one A100 40 GB (AF3 limit: 4,352 tokens). Convert each
job to AF3's local input format (`dialect: alphafold3`, one `protein` entry per chain with ids
A, B, C...). Run with default settings: 1 seed, 5 diffusion samples. `analyze.py` reads the
`*_summary_confidences_*.json` files; rename them to the `fold_<job>_summary_confidences_<k>.json`
pattern or adjust the regex.

## What it tells us

- Whether the pooled method recovers known *Vibrio* competence complexes (precedented:
  PilP-PilQ, PilB-PilC, PilT-PilC).
- Whether the Dalia lab's own AF-derived, genetically validated interactions (PilT-PilU,
  CBP-ChiS, DprA-ComM) survive an unbiased pooled screen with decoys. The audit predicts the
  never-solved class does worse.
- The false-positive burden on system proteins against random decoys.

## Literature evidence table (descriptive, Jev, 2026-09-22)

`lit_evidence.mts` searched Europe PMC for every pair of 24 competence/regulatory names (+ Vibrio),
214 of 276 pairs had abstracts, and Jev judged each abstract for a direct interaction (cost $0.43).
Five pairs scored >= 0.8:

| Pair | Jev | Check by hand |
|---|---|---|
| PilT-PilU | 0.88 | correct (Teipen...Dalia 2026) |
| CBP-ChiS | 0.88 | correct (Anderson & Dalia 2025) |
| DprA-ComM | 0.95 | correct (Dalia 2025) |
| ChiS-TfoS | 0.96 | **correct: "ChiS directly interacts with TfoS"** (Hullinger...Dalia 2025). Not in the pilot, because TfoS is absent from the 24 proteins |
| CBP-TfoS | 0.86 | **wrong**: same abstract, which reports ChiS-TfoS, not CBP-TfoS |

It independently recovered all three pre-registered never-solved positives, 4 of 5 calls are correct,
and it found one confirmed interaction the pilot misses. The T4P alignment pairs (PilM-N-O-P-Q) have no
*Vibrio*-specific direct evidence in abstracts, as expected (their evidence is from other species).
