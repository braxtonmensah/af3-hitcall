# Pre-registration 15: does FUTURE replicate in yeast with a different AI pipeline? (FUTURE-Y)

Written 2026-09-23, before downloading any model or computing any outcome. Nothing about the
yeast data has been examined except that ModelArchive serves the models one entry at a time.

## Why

FUTURE (human, AF2/FoldDock, Burke 2021) found that 81% of confident never-solved models that were
solved later had the right interface. One organism and one pipeline is a finding; two is a pattern.
Humphreys et al. (Science, November 2021) released confident yeast complex models from a
RoseTTAFold + AF2 screen (ModelArchive `ma-bak-cepc`). Structures released from 2022 on could not have
informed them.

## Population and outcome (same rules as FUTURE)

- Every `ma-bak-cepc` model. Chains mapped to *S. cerevisiae* S288c UniProt (reference proteome
  UP000002311) by exact sequence, or, if not exact, by the best global alignment with >= 95% identity
  over >= 90% of the model chain. Residue positions are mapped through the alignment.
- Co-complex, release dates, "newly solved" (earliest co-complex released on or after 2022-01-01),
  exclusion of pairs with an earlier co-complex, direct contact (>= 5 CB pairs < 8 A), and the
  reference structure (most contacts) are all defined exactly as in PREREG_FUTURE.
- Predicted interface = residues with CB (CA for Gly) within 8 A of the other chain in the model.

## Tests

- **Y1 (primary)**: among newly solved, direct pairs, the fraction whose model interface F1 >= 0.5
  (as FUTURE F2). **Replicates** if the 95% bootstrap CI lower bound is above 0.5 (most confident
  novel models right).
- **Y2 (null)**: for each pair, 200 random circular shifts of the predicted interface positions along
  each chain (keeping interface size and contiguity), scored the same way. Reported: the null correct
  fraction; Y1 must exceed the null's 99th percentile.
- Reported: counts at every step, excluded earlier co-complexes, release-year spread, and the same
  circularity strata as the FUTURE post hoc (in-silico start recorded, resolution <= 3 A, X-ray).
- **Y3 (anticipation, descriptive)**: fraction of models newly solved (no low-confidence contrast is
  available in this dataset).
