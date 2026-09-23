# Pre-registration 13: are AlphaFold screen misses cooperative interfaces? (COOP)

Written 2026-09-23, after FUTURE and before computing any outcome below. Only availability counts were
looked at: in the Todor pools, 328 STRING-positive pairs (107 never-solved) were folded both in a
pool containing a shared STRING partner and in a pool without one.

## Idea

FUTURE showed that AF's confident novel predictions are right, but most real novel interactions get
low scores, and nothing in the output recovers them (CONTEXT, STRUCT). If the misses are
**cooperative** interfaces (stable only when a third subunit holds the pair), then every pairwise
screen, and every randomly pooled one, is blind to them by design, and the fix is in the input:
fold the pair together with its shared partner.

## Arm P: natural experiment in the pooled M. genitalium screen

- Bridge = a third protein C in the same pool with STRING experimental > 800 to both A and B.
  Single = C is a > 800 partner of exactly one of A, B (and no bridge). None = neither.
- Paired unit: a pair with at least one bridged and one unbridged pool.
  delta_bridge = mean S0 over bridged pools - mean S0 over unbridged pools.
- **P1 (primary)**: never-solved positive pairs (strict precedent rule as in H1): mean delta_bridge > 0,
  node bootstrap 2,000 reps, 95% CI lower bound > 0.
- **P2 (specificity)**: DiD versus negatives (non-positive pairs A-B that share a > 800 partner C,
  same paired design): delta_pos_never - delta_neg > 0 with CI lower bound > 0. Rules out "any complex
  member in the pool lifts every score".
- **P3 (it is the bridge, not a partner)**: delta_single = mean S0 in single pools - mean S0 in none
  pools, never-solved positives. Cooperativity predicts delta_bridge > delta_single (CI of the
  difference above 0).
- Reported: precedented positives.

## Arm H: the real structures of AF's hits and misses (human, FUTURE set)

Population: FUTURE pairs newly solved with direct contact (confident = hits, low = misses). For each
pair's reference entry (the FUTURE reference structure), from its mmCIF with all polymer chains:
- **bridged fraction** = fraction of the pair's interface residues (both chains, CB/CA 8 A) that are
  also within 8 A of a third polymer chain;
- **n_entities** = distinct polymer entities in the entry;
- **pair interface size** = residue pairs in contact between the two chains.
- **H1 (primary)**: median bridged fraction, misses minus hits > 0, bootstrap over pairs, 95% CI
  lower bound > 0.
- H2: misses have more entities; H3: misses have smaller pair interfaces (both reported with CIs).

## Verdict

"Cooperative misses" is supported only if **P1 and H1 both pass** (two organisms, two model
generations, one observational and one quasi-experimental). If only one passes it is reported as
partial.

## Known weaknesses

- STRING > 800 partners are co-complex members, not necessarily direct bridges; "shared partner" is a
  proxy for the third subunit.
- Arm H is observational: large assemblies may be harder for AF for other reasons (for example,
  induced fit); H3 is there to show whether interface size alone explains it.
