# Pre-registration 26: does the split-crosslink signature track stoichiometry? (HIGHER_CAL)

Written 2026-09-25, before any assembly or stoichiometry record was fetched for this test. Uses the
per-pair split/clean calls already committed in `results_higher.json` (commit 5e231af); those calls
are not recomputed or changed here.

## Why

HIGHER's primary test (P1) compared the split signature against an *indirect* label (does either
protein show an over-length self-link) and passed with a CI of [0.022, 0.674]. Its strongest support
was presented as "blind recovery": the signature picked out RNA polymerase, the Nap adhesin,
pyruvate dehydrogenase and RNase J. A list of successes has no denominator. It does not say how many
known higher-order complexes the signature missed, or how often it fires on complexes that are
strictly 1:1. Without those two numbers nobody, including a paying customer, can tell what a "split"
call is worth.

The PDB can supply a direct label for the pairs that have a solved homologous co-complex: count the
copies of each protein in the biological assembly.

## Declared prior knowledge

The analyst knows from textbooks that bacterial RNA polymerase is alpha2-beta-beta'-omega (so
RpoB-RpoC is 1:1 while RpoA-RpoB is not), that pyruvate dehydrogenase E1 is alpha2-beta2 on a
multimeric E2 core, that gyrase is A2B2, and that most ribosomal proteins are single-copy. Labels are
computed mechanically from PDB records by the rule below, never from this knowledge. Where the two
disagree, the PDB-derived label is used and the disagreement is reported.

## Population and truth set (fixed now)

- **Pairs:** the 236 testable pairs in `results_higher.json` (`all_pairs`), with their committed
  `split` and `clean` calls and link counts.
- **Co-complex entries:** for a pair (A, B), every PDB entry in `data/pdb_hits.json` (RCSB mmseqs2,
  E <= 1e-3, identity >= 0.25, released <= 2021-09-30; the same precedent search H1 used) that
  satisfies the **strict rule**: A matches some entity that B does not match, and B matches some
  entity that A does not match.
- **Copies:** from RCSB assembly 1 of each entry, the number of instances of each polymer entity
  (asym chains in `pdbx_struct_assembly_gen` times the number of operators in each
  `oper_expression`). copies(A) = the largest copy number among the entities A matches and B does not;
  copies(B) likewise.
- **Entry label:** **higher** if copies(A) >= 2 or copies(B) >= 2; **one-to-one** if both equal 1.
  An entry whose assembly record cannot be fetched or parsed is dropped and counted.
- **Pair label:** the majority of its entries' labels. An exact tie is **ambiguous**, excluded from
  the tests and listed.

## Tests

**C1 (primary).** Delta = P(split | higher) - P(split | one-to-one), among labelled pairs. Bootstrap
over proteins (the HIGHER scheme: resample proteins, weight each pair by the product of its two
proteins' counts), 2,000 replicates, seed 26, 95% CI.
- **Calibrated** if Delta > 0 and the CI excludes 0.
- **Not calibrated** otherwise.
- **Underpowered** (descriptive only, no verdict) if either group has fewer than 8 pairs, or fewer
  than 3 split pairs in total.

**C2 (reported, the numbers a user needs).** Sensitivity P(split | higher) and false-positive rate
P(split | one-to-one), each with a Wilson 95% interval; precision P(higher | split) against the base
rate P(higher) in the labelled set, and the lift (precision / base rate). The same four numbers for
`clean` as a call of one-to-one.

**C3 (secondary, FDR-aware variant).** At 5% link FDR a pair with n links is expected to carry
0.05 n false identifications, and a false link will usually be "far". A split resting on a single far
link among many is therefore consistent with one bad identification. Define **split2** = at least one
near link AND at least two far links. Report C1 and C2 for split2. This is secondary: it cannot
rescue a failed C1, and a pass here is labelled as the variant.

## Consequences fixed in advance

- The per-pair label of every pair in the "blind recovery" list (MG_340-MG_341, MG_177-MG_341,
  MG_191-MG_192, the three PDH pairs) is reported. **Any of them labelled one-to-one is removed from
  every recovery list in RESULTS.md, the preprint, the sample report and the outreach material**,
  whatever C1 says.
- If C1 is not calibrated, "blind recovery" stops being presented as validation of the signature,
  and the split call is described in customer-facing material as a flag for manual review, not as a
  stoichiometry call.
- If C1 is calibrated, the sample report's stoichiometry column carries C2's sensitivity,
  false-positive rate and precision next to it.

## Limitations, stated before the result

- Only pairs with a solved homologous co-complex can be labelled, so this calibrates the signature
  on precedented complexes. Whether it transfers to never-solved pairs (the ones that matter) is not
  shown here.
- Stoichiometry is inferred from homologs at >= 25% identity, and assembly 1 is the depositor's or
  software's biological assembly, which is occasionally wrong or a sub-complex.
- "Higher" here means more than one copy of either protein in the assembly containing both. A pair
  inside a large assembly at 1:1 (most ribosomal pairs, RpoB-RpoC) is labelled one-to-one even though
  it is part of something bigger. That is the question HIGHER's pre-registration asked ("real
  stoichiometry is higher than 1:1"), so it is the right label for this test.
