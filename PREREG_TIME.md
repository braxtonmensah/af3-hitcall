# Pre-registration 3: memorisation or stability? A time split on PDB precedent

Written 2026-09-22, after the XL-MS result (PREREG_XL.md verdict (a)). Committed before the
post-cutoff PDB search was run.

## Why

Pairs with a co-complex in the PDB score far higher (STRING positives 0.85 vs 0.71; in-cell XL-MS
positives 0.95 vs 0.57). Two explanations remain:

- **Memorisation / templates**: AF3 recalls complexes it trained on or retrieves as templates. Both
  AF3 training and the AF Server's default template search stop at 2021-09-30 (alphafoldserver.com
  FAQ; the paper's local runs used the same cutoff).
- **Stability**: complexes that get solved are stable, obligate and well-folded, and AF3 predicts that
  class well whether or not it has seen them.

Complexes whose *only* structural precedent was released after 2021-09-30 are stable enough to have
been solved, yet unseen by AF3. Where they score separates the two explanations.

## Definitions

- **Post-cutoff hits**: the same RCSB search as H1 (mmseqs2, E <= 1e-3, identity >= 0.25) restricted to
  entries released on or after 2021-10-01.
- **Pre** = co-complex precedent before the cutoff under EITHER pre-cutoff definition (primary or the
  E-only sensitivity), so that weak older homolog complexes also count as "seen".
- **Post-only** = co-complex precedent in post-cutoff entries AND not Pre.
- **Never** = neither.
- Truth sets: STRING experimental > 800 (primary) and XL-MS positives (secondary; XL visibility
  negatives as in PREREG_XL.md). Score: S0.

## Test

Gap fraction f = (AUROC_postonly - AUROC_never) / (AUROC_pre - AUROC_never), each AUROC taken
against the same negatives. Node bootstrap (2,000 reps) with a 95% CI on f.

- **Stability**: f >= 0.7 and the CI lower bound > 0.3.
- **Memorisation**: f <= 0.3 and the CI upper bound < 0.7.
- Otherwise mixed or inconclusive.
- **Underpowered** if fewer than 20 post-only positives; then only counts are reported.
