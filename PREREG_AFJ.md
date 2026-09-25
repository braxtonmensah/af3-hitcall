# Pre-registration 21: dedicated AF3 runs of the Mycoplasma RNase J : MG423 complex (AFJ)

Written 2026-09-25 before submitting any job. Jobs: `rnasej/afserver_rnasej.json` (AlphaFold Server,
default settings, 5 samples each).

## Jobs

| Job | Chains | Purpose |
|---|---|---|
| rnasej_mpn_2x2 | M. pneumoniae RNase J (P75497) x2 + MG423 homolog (P75174) x2 | primary: crosslinks were measured in this organism, so no ortholog mapping |
| rnasej_mg_2x2 | MG139 x2 + MG423 x2 | same in M. genitalium |
| rnasej_mpn_1x1 | P75497 + P75174 | heterodimer only |
| rnasej_mpn_decoy_2x2 | P75497 x2 + P75168 x2 (PtsI, 572 aa; seeded length-matched decoy) | specificity control |

## Crosslinks (M. pneumoniae numbering, RNase J residue : P75174 residue)

(120, 502) DSSO+DSS; (120, 546) DSSO+DSS; (409, 322) DSS; (225, 224) DSSO; (257, 224) DSSO; (228, 224) DSS.
Distance per link = minimum CA-CA over all RNase J copy x partner copy combinations; satisfied <= 30 A.

## Outcomes

- **O1 (primary):** in rnasej_mpn_2x2, in at least 3 of 5 samples, all 6 links satisfied, AND the
  RNase J : P75174 chain-pair ipTM (best RNase J-partner pair) >= 0.5.
- **O2:** rnasej_mg_2x2 gives the same (links scored by the same residue numbers; the orthologs align
  1:1 at these sites).
- **O3:** rnasej_mpn_1x1 satisfies the near links and not all far links (as in the pooled screen).
- **O4 (specificity):** in the decoy job the best RNase J : decoy chain-pair ipTM < 0.3.
- Reported: ipTM / pTM, chain-pair ipTM matrix, per-link distances, and whether AF3's tetramer matches the
  3ZQ4-templated model (CA RMSD after superposition).

**"Computationally solved"** = O1 and O4 pass. This still is not an experimental structure.
Note: AF Server may use PDB templates up to 2021-09-30 (for example B. subtilis RNase J1, 3ZQ4); the
crosslinks are not used by AF3 in any way, so the crosslink test stays independent.
