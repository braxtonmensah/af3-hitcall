# Pre-registration 16: causal rescue of AF's misses with their bridging subunits (RESCUE)

Written 2026-09-23, before any job was submitted. Jobs are in `rescue/afserver_rescue.json`; the pair
list is `rescue/rescue_pairs.csv`.

## Idea

COOP-H found that AF's misses are non-autonomous contacts inside large assemblies. If so, folding
the missed pair **together with the subunits that contact its interface** should recover the
interface, and adding an **unrelated subunit from the same assembly** should not.

## Design (fixed)

- Pairs: FUTURE misses (pDockQ < 0.10, first solved with direct contact 2022-26) whose interface is
  >= 20% bridged by a third chain (43 eligible); the first 20 by UniProt-pair ID.
- Per pair, three AF Server (AF3) jobs, default settings, 5 samples:
  **pair** (A + B), **bridge** (A + B + up to 3 bridging accessions: chains with >= 5 CB within 8 A of
  the A-B interface in the reference structure, by contact count, total <= 5,000 tokens),
  **ctrl** (A + B + one accession from the same entry with no contact to the A-B interface, closest in
  length to the bridge set).
- AF Server's template cutoff (2021-09-30) and AF3's training cutoff predate every reference structure.
- Outcome per job: the A-B interface (CB 8 A) in model 0, and the mean over the 5 samples, scored as
  FUTURE F2 (interface F1 against the reference structure, observed residues). Correct = F1 >= 0.5.
  Also A-B chain-pair ipTM.

## Tests

- **R1 (primary)**: correct in **bridge** vs **pair**, paired over the 20 pairs, one-sided exact sign
  test on discordant pairs, p < 0.05, and at least 6 of 20 correct in bridge.
- **R2 (specificity)**: bridge vs ctrl, same test. The principle predicts R1 and R2 both pass.
- Reported: A-B ipTM in each arm, and the pair-arm correct rate (AF3 baseline for these misses).

## Notes

- Submitting uses Braxton's AF Server account (30 jobs a day, shared with the Vibrio pilot). Nothing
  has been submitted.
