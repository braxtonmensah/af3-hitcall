# Pre-registration 29: the expanded small-molecule screen against the RNase J interface (VSCREEN)

Written 2026-09-25, **before any Boltz-2 affinity score exists**. No GPU has run for this screen on
any machine. The library, the arms, the gate and the decision rules below are fixed by this commit;
the compound identities are fixed by `cleanroom/library_master.tsv` and the selection written by
`libgen.py --select`, both committed with or before this file.

## Why this replaces the staged screen rather than extending it

650 jobs were already staged. They are being rebuilt, not run, because checking the staged set by
molecule rather than by filename found three defects (commit `b3bfd15`): four molecules sat in both
the screen arm and the decoy null, one molecule was paid for twice in each of two arms, and the two
arms named two different MSA directories so one of them would have died at run time. Those are
mechanical and now guarded.

The fourth problem is not mechanical and is the reason this pre-registration exists.

### The old decision rule fires on noise about 86% of the time

`vscreen.py --rank` reports "N real compounds beat every decoy" and treats N > 0 as the signal to
buy compounds. With 300 screen compounds and 50 decoys, under a **pure null in which nothing binds
and the two arms are drawn from the same distribution**, the expected number of compounds beating
every decoy is `300 / 51 = 5.88`, and the probability of at least one is **0.86** (4,000
simulations, `libgen.py` design notes). The rule was not a test. It was a near-certainty dressed as
a finding, attached to a decision that costs $250 to $1,800 in compound purchases.

The fix is not a different threshold. It is that the max-statistic has no multiplicity control, and
one cannot be bolted on at this scale:

| Screen size | Decoys needed for the TOP compound to reach BH q < 0.10 |
|---|---|
| 300 | 2,999 |
| 1,000 | 9,999 |
| 2,000 | 19,999 |
| 3,273 | 32,729 |

The smallest empirical p-value obtainable is `1/(n_decoys + 1)`, so per-compound significance needs
a null roughly ten times the screen. That is more GPU than the screen itself and it is not going to
be bought. **So this screen will never establish that any individual compound is a binder, and this
pre-registration states that in advance rather than discovering it at the point of writing up.**

What the design *can* support is a distributional question, and it supports it well. Mann-Whitney
of the screen set against a property-matched null, at 300 per arm, has power 0.84 to detect
AUC 0.57 and 0.99 to detect AUC 0.60.

## Arms

| Arm | Protein | Compounds | Purpose |
|---|---|---|---|
| **S** (screen) | RNase J, P75497, pocket-steered to the PPI interface | the selection | the question |
| **N** (null) | same | property-matched, same size as S | what "high" means |
| **P** (positive control) | see below | 3-8 known binders | whether the instrument can detect binding at all |
| **O** (off-target) | human CPSF73, Q9UKF6, no pocket constraint | same compounds as S | selectivity |

**The null is matched, not random.** Boltz-2's affinity head responds to ligand size, so a randomly
drawn null can be beaten by molecular weight rather than by binding. `libgen.match_decoys` bins on
molecular weight and cLogP and samples the null from the screen set's own bins, leaving scaffolds
free. The Kolmogorov-Smirnov statistic per property is printed at selection time and **is reported
with the result**; a D above 0.15 on `mw` or `heavy` means the match failed and the null is still
distinguishable by size.

**The null is the same size as the screen set.** At a 1:1 ratio the expected number of compounds
beating the whole null under the pure null is exactly 1.0 at any scale, which makes the top of the
list interpretable as "about one of these is expected for free".

## The gate, read before anything else

**G1.** Arm P must place its known binders above the null. Concretely: the median empirical
percentile of the positive-control compounds against arm N must exceed **0.80**, and at least
**half** of them must fall in the top decile of the null.

**If G1 fails, arms S and O are reported and NOT interpreted.** A screen whose instrument cannot
rank known binders above random compounds at this kind of site cannot distinguish "nothing binds
this interface" from "this method cannot see binding here", and the entire compound route is then
closed for the price of the gate rather than the price of a compound order.

**The positive-control compound set is not yet fixed.** It is being assembled from the literature
into `cleanroom/POSITIVE_CONTROLS.md`. It will be fixed by a **committed amendment to this file
before any Boltz-2 score exists**, so the ordering is checkable from the commit dates, which is the
only reason anyone should believe it. If no adequate positive control can be found, that is itself
a reportable result and G1 is recorded as unmeetable rather than quietly dropped.

**A known limitation of G1, stated now.** Any positive control will almost certainly be a binder at
a *catalytic or allosteric pocket*, because essentially no small molecule has a measured binding
site at a nuclease protein-protein interface. So G1 tests whether the method can rank a real binder
at a real pocket. It does not establish that the method works at the interface this screen targets.
That gap cannot be closed with existing data and is a limit on every conclusion below.

## Tests

**V1 (primary).** Mann-Whitney U of arm S against arm N on `affinity_probability_binary`, reported
as AUC with a bootstrap 95% CI.
- **Enriched** if the CI excludes 0.50 and AUC > 0.50.
- **Null** if the CI contains 0.50.
- **Anti-enriched** if the CI excludes 0.50 below, which would indicate the pocket constraint is
  actively hurting and is a real result about the method.

**V2 (selectivity, required for any compound purchase).** For each shortlisted compound, the
paired difference in score between arm S and arm O. A compound that scores as well or better
against human CPSF73 is a selectivity liability and is **not bought**, whatever its rank.

**V3 (shortlist, explicitly hypotheses and not hits).** The top 25 of arm S by score, each with its
empirical percentile against arm N, its arm-O score, its PAINS flag, and its purchase cost. This
table is labelled in the output as **hypotheses requiring experimental test** and no entry in it is
described as a hit, a binder or a candidate drug.

**V4 (reported, descriptive).** Whether the score correlates with molecular weight and heavy-atom
count within arm S. If it does strongly, the matching in V1 is carrying the entire result and that
is said plainly.

## Consequences fixed in advance

- **G1 fails** → the compound route closes. No purchase. The result is written up as a negative
  about method sensitivity at this target class, which is worth reporting and cost one gate.
- **G1 passes, V1 null** → the honest conclusion is that no enrichment was detected among the
  screened chemical space at this interface. **No compounds are bought.** A null here is a real
  answer and it is the outcome the screen's own author expects; see `vscreen.py`'s docstring, which
  said so before any of this ran.
- **G1 passes, V1 enriched** → the shortlist becomes worth an experiment. Even then, **no individual
  compound is claimed to be a binder**, because the table above shows this design cannot support
  that claim. The next step is a purchase of the top few plus negative controls, and the write-up
  says "enriched set, untested individually".
- **V1 enriched but V4 shows the score is mostly size** → the enrichment is attributed to residual
  property mismatch and V1 is downgraded to inconclusive regardless of its CI.

## Limitations, stated before the result

- Protein-protein interfaces are among the hardest small-molecule targets and most are not
  druggable by conventional compounds. The prior on finding anything is low and always was.
- Boltz-2's affinity head was trained largely on conventional pockets. Its scores at a PPI
  interface are a ranking, not an affinity, and are used only as a ranking here.
- The pocket constraint steers ligands to the interface using residues from
  `rnasej/results_interface.json`, which come from a **predicted** heterotetramer, not a solved
  structure. If the interface model is wrong, the screen is aimed at the wrong place and no result
  from it means anything. The model's support is five independent published lines
  (`new_biology/RNASEJ_MG423.md`) but it remains a model.
- The library is what is purchasable and downloadable for free, which is a biased sample of
  chemical space and under-represents the covalent, macrocyclic and peptidomimetic classes that
  most often work at interfaces.
- `M. pneumoniae` is slow and fastidious to culture. A positive here still needs an MIC quote
  before it means anything biological, and the quote is obtained **before** compounds are bought,
  not after.
- No wet-lab experiment supports any part of this. Every output is a hypothesis.

## What is being screened

Sources, counts and licences are in `cleanroom/library_sources.json` and the merged, deduplicated,
property-annotated table is `cleanroom/library_master.tsv`. Composition is regenerated by
`libgen.py --report` and the number quoted anywhere must be the distinct-molecule count from that
table, never the raw line count of a download: on the approved set alone those differ by 30%
(3,273 raw, 2,297 distinct and Boltz-usable).
