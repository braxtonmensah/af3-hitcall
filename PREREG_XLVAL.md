# Pre-registration 18: new Mycoplasma complexes supported by AF3 and in-cell crosslinks (XLVAL)

Written 2026-09-24, before any AF3 coordinate for these pairs was extracted and before any crosslink
distance was computed.

## Aim

Find protein complexes in *M. genitalium* that (1) have never been solved, (2) AF3 predicts
confidently, and (3) are independently supported by residue-level in-cell crosslinks, with the
crosslinks landing within reach across the predicted interface. FUTURE showed confident novel
predictions are right about 80% of the time; crosslink agreement is a second, independent line of
evidence. This is computational evidence, not proof: each supported complex is a hypothesis for the
bench.

## Candidates (fixed; only label-level data were used to pick them)

Pairs with no strict pre-2021 precedent, S0 >= 0.2 (above the screen's 99.5th percentile, 0.152), and
at least one inter-protein crosslink between their *M. pneumoniae* orthologs (O'Reilly 2020, DSSO,
5% link FDR): MG139-MG423, MG098-MG099, MG014-MG015, MG411-MG412, MG179-MG180, MG027-MG150,
MG119-MG121, MG241-MG242, MG098-MG181, MG078-MG080, MG127-MG249, MG001-MG419, MG409-MG410, MG098-MG179.

**Controls:** up to 20 crosslinked never-solved pairs with S0 < 0.05 (seed 18, among those whose pools
are extracted). These should fail the structural test.

## Structural test

- Coordinates: CA atoms of every AF3 model (5 samples) of every pool containing the pair, from the
  Todor Zenodo archive.
- Crosslinked residues are mapped *M. pneumoniae* -> *M. genitalium* by global alignment of the
  ortholog pair (Biopython, BLOSUM62). Links whose residues do not align are dropped and counted.
- A link is **satisfied** if CA-CA <= 30 A (DSSO). Per pair: satisfied fraction over all links x all
  models.
- **Null:** random pairs of lysines, one from each chain, evaluated in the same models (1,000 draws).
- **Supported** = satisfied fraction >= 0.5 AND above the random-lysine null's 95th percentile.

## Novelty checks (reported per pair)

- Current PDB (no date limit): homologous co-complex at E <= 1e-3, any identity, strict rule.
- Europe PMC: papers naming both genes/proteins in a Mycoplasma context.
- Todor 2026 text: whether the pair is reported there.
A pair counts as **new** only if it is supported, has no homologous co-complex in the current PDB, and no
paper describes the interaction.

## Reported whatever the outcome

Every candidate and control with its numbers. Controls must mostly fail, or the test is not
discriminating and no candidate is called supported.
