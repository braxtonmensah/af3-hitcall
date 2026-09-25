# Pre-registration 22: never-solved human complexes supported by 2021 predictions and in-cell crosslinks (XLHUMAN)

Written 2026-09-25, before downloading or viewing any row of either crosslink dataset, and before any
Burke model coordinate for a candidate pair was fetched for this purpose.

## Aim

Apply the XLVAL design (PREREG_XLVAL, XLDSS) to the human forward registry: find human protein pairs
that (1) have no co-complex structure in the PDB as of SIFTS 2026-09-20 (the registry guarantees this),
(2) were predicted confidently in 2021 (Burke et al. AF2/FoldDock, pDockQ > 0.23), and (3) are
independently supported by residue-level in-cell crosslinks, with the links landing within reach on the
2021 model. FUTURE showed confident never-solved predictions are right about 80% of the time; crosslink
agreement is a second, independent, cell-derived line. Each supported pair is a hypothesis for the bench,
not proof.

## Data (fixed before viewing)

- **Primary:** Bartolec et al. 2023 PNAS (Rappsilber lab), HEK293, three chemistries (DSSO, DHSO,
  DMTMM), PXD035844. Dataset S1 (`pnas.2219418120.sd01.xlsx`), all unique residue pairs; Dataset S5
  for the paper's own PPI evidence classification. Inter-protein rows only, at the FDR the file reports
  (no re-filtering beyond the paper's own).
- **Replication:** Wheat et al. 2021 PNAS (Huang lab), HEK293, DSSO in vivo, Dataset S1. Separate
  experiments, separate lab.
- **Models:** the 2021 FoldDock model for each pair, streamed from `archive.bioinfo.se/huintaf2`
  (HuRI.zip, humap.zip) with the existing `human_extract.parse`. One model per pair, as published.
- **Candidates:** every registry pair (`registry/open_confident_human_pairs_2026-09-23.csv`, n=6,010)
  with at least one inter-protein residue pair in the primary dataset.
- **Controls:** crosslinked pairs in Burke S1 with pDockQ < 0.10 and a stored model, up to 30, seed 22.
  These should fail the structural test.

## Site check (learned from XLVAL Amendment 1)

Each crosslinked residue must match the model chain's sequence at the stated position: K for DSSO
and for the K side of DMTMM; D or E for DHSO and for the acid side of DMTMM; protein N-terminus
allowed. Links that fail are dropped and counted per pair. If more than 30% of all links fail, the
positions are re-derived from the peptides as in Amendment 1 and that is reported as an amendment.

## Structural test

- Distance: CA-CA between the two crosslinked residues on the 2021 model.
- Reach: **<= 30 A** for DSSO and DHSO; **<= 25 A** for DMTMM (zero-length). If the file does not give
  the chemistry per link, 30 A for all, and that is reported.
- Per pair: satisfied fraction over usable links.
- **Null:** random residue pairs drawn from the same residue classes across the two chains (K-K for
  DSSO, D/E-D/E for DHSO, K-D/E for DMTMM), 1,000 draws, same model, same reach.
- **Supported** = at least 2 usable links AND satisfied fraction >= 0.5 AND above the null's 95th
  percentile. Single-link pairs are reported with their distance but not called.

## Discrimination check (must pass before any candidate is called)

Controls must be supported at most 10% of the time (at most 3 of 30). If more, the test does not
discriminate and no candidate is called supported.

## Novelty (reported per supported pair)

- PDB: none by construction (registry definition, SIFTS 2026-09-20); additionally, a current RCSB
  check for any homologous co-complex at E <= 1e-3 with the strict rule from XLVAL.
- Bartolec Dataset S5 evidence class for the PPI (whether the pair had prior interaction evidence).
- STRING experimental channel score (data/string_exp where available, else the STRING API).
- Europe PMC: papers naming both gene symbols.
A pair counts as **new** only if supported, no homologous co-complex, and no paper describes a direct
interaction. "Previously reported as interacting but never modelled" is reported as such and is not
called new.

## Pre-specified outcomes

- **O1.** The number of supported registry pairs and the supported fraction among testable
  candidates, against the control rate.
- **O2.** For each supported pair, whether it replicates in the Wheat 2021 dataset (any usable link;
  rule as above), reported whatever the answer.
- **O3.** The list of pairs that meet "new", with all numbers, or the statement that none did.

Reported whatever the outcome. Negative results go in RESULTS.md next to the positives.

## What this is not

Not a re-run of AF3 or Boltz on the pairs (no compute available under the IP constraints in
`COMMERCIAL.md`); the models are the published 2021 ones. A supported pair here says: a 2021 model,
made before the crosslink data existed, places two in-cell crosslinks within reach across an
interface that has never been solved.
