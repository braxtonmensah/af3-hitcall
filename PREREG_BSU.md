# Pre-registration 4: replication in another organism and model (B. subtilis, AlphaFold-Multimer)

Written 2026-09-22. Committed before any B. subtilis sequence was fetched or any precedent computed.
The dataset's own columns have been viewed (value counts only), not cross-tabulated.

## Data

O'Reilly et al. 2023 (Mol Syst Biol, PMC10090944), Dataset EV5: 1,977 *B. subtilis* heterodimers
modelled with AlphaFold-Multimer. Each row is the top-ipTM model, with evidence flags (crosslinking
MS, co-fractionation MS, SubtiWiki, STRING). Every pair was chosen because some evidence suggested an
interaction, so there are no random negatives.

## Definitions

- **XL+** = `crosslinking MS` true (232 pairs): direct in-cell proximity, as in PREREG_XL.
- **Comparator** = co-fractionation true AND crosslinking false: co-migrating candidates without
  direct proximity evidence.
- **Precedent** = the H1 primary definition (RCSB mmseqs2, E <= 1e-3, identity >= 0.25, entries
  released <= 2021-09-30, two distinct entities in one entry). Sequences come from UniProt.
  Sensitivity: the same with no date limit.
- **Score**: ipTM as reported.

## Primary test

Recall at ipTM >= 0.5 among XL+ pairs: precedented minus unprecedented. Node bootstrap over
proteins, 2,000 reps, 95% CI.

- **Replicates** if the difference >= 0.20 and the CI excludes 0.
- **Fails to replicate** if the CI includes 0.
- Otherwise partial.
- **Underpowered** if either stratum has fewer than 25 XL+ pairs.

Secondary (reported, not decisive): AUROC of XL+ vs the comparator within each precedent stratum.
