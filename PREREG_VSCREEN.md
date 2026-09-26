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

---

# Amendment 1, 2026-09-25: the gate is fixed, and it runs before the screen is built

Written **before any Boltz-2 score exists for any arm of this screen**, on any machine. What has been
seen at this point: a literature and PDB survey of known ligands of this fold family
(`cleanroom/POSITIVE_CONTROLS.md`, committed with this amendment), and nothing else. No prediction
has been run.

## What the survey changed, and it is not a detail

**No small molecule is known to bind bacterial RNase J, from any organism.** All 27 RNase J entries
in the PDB carry only metals, RNA, or UMP as a substrate fragment. The nearest literature
candidates, the RnpA inhibitors from *S. aureus* degradosome screens, were refuted as colloidal
aggregators (PMID 33972249) and are excluded by name below.

So **the gate cannot be run against the target.** Any gate here is a surrogate on homologous folds,
and it therefore measures something narrower than "this pipeline works": it measures whether the
pipeline recovers known ligands of related proteins under the same protocol. That distinction is
written into the claim table below rather than left for the discussion section.

## The gate is two tiers, because they license two different claims

### Tier A: does the method recover known active-site ligands of this fold?

| Compound | PDB ligand | Run against | Evidence it binds |
|---|---|---|---|
| JTE-607 free acid (NVP-LTM531) | JBG | human CPSF73, Q9UKF6 | Kd 370 nM reported, 2.49 A co-crystal 6M8Q, PMID 31819276. Boron-free and does **not** coordinate the metals, so it tests pocket recognition rather than chelation |
| Tao compound 1 | XYX | human CPSF73 | photoaffinity label + probe displacement + co-crystal 8T1Q, PMID 37967558 |
| Tao compound 2 | XZC | human CPSF73 | same evidence chain, co-crystal 8T1R |
| SNM1A quinazoline-hydroxamate | U2O | human SNM1A, DCLRE1A | IC50 0.8 uM on **purified enzyme**, co-crystal 8C8S, PMID 38817593 |
| Ceftriaxone | 9F2 | human Artemis, DCLRE1C | co-crystal 7APV at IC50 65 uM. Deliberately the weak rung, to locate where the score stops separating a true weak binder from noise |

### Tier B: does it recover a ligand at an interface, which is what this screen asks?

| Compound | PDB ligand | Run against | Why |
|---|---|---|---|
| Inositol hexakisphosphate | IHP | INTS4-INTS9-INTS11 Integrator cleavage module | The **only** documented small molecule at a protein-protein interface in this fold family: 55 A from the INTS11 active site, contacting all three subunits, 7SN8, PMID 36180473. INTS11 is the CPSF73 paralogue |
| nsp10-nsp14 ExoN interface fragments | see 9FWH / 9FWM / 9FWT | SARS-CoV-2 nsp14 : nsp10 | A published nuclease-plus-obligate-partner interface fragment campaign with measured affinities, PMID 40794865. Not this fold, but the same problem shape, and the only case of drug-like **fragments** at a nuclease interface |

### Negative controls, run in the same batch

- **JTE-607 parent ethyl ester** against CPSF73. It is a prodrug and is not the binding species, so it
  must score **below** its own free acid. If it scores above, the pipeline is rewarding
  lipophilicity rather than recognition, and that finding invalidates Tier A whatever else passes.
- **AN3661** against human CPSF73. A potent antiparasitic whose human cytotoxicity is 60 to >100 uM
  across six human lines, i.e. no evidence of engaging the human protein. A high score here is a
  red flag on the scoring function.
- **Ebselen, disulfiram, auranofin** against Artemis. These inhibit by thiol and metal reactivity
  with no co-crystal. A structure-based score should **not** rationalise them.
- **Excluded by name: RNPA2000, purpurin, iriginol hexaacetate.** Refuted as aggregators.

## Pass criteria, fixed now

- **A1.** All five Tier A compounds score above the **95th percentile** of the matched null
  (arm N, same protocol) when run against their own cognate protein.
- **A2.** The JTE-607 free acid scores above the JTE-607 parent ester.
- **A3.** At most one of the three reactive negative controls reaches the Tier A compounds range.
- **B1.** IP6 scores above the 95th percentile of the matched null against the Integrator module.
- **B2.** At least one nsp14 interface fragment does the same.

## What each outcome licenses, fixed now

| Outcome | What may be claimed |
|---|---|
| A passes, B passes, RNase J screen null | "The method recovers known active-site ligands of this fold and the one known interface ligand in it, under this protocol, and found nothing at the RNase J : MPN621 interface." A publishable negative. |
| **A passes, B fails** | The method finds active sites, not interfaces. **A null at the RNase J interface is then uninformative and is reported as uninformative, not as a negative result about the target.** This is the most likely outcome and the screen is planned around it. |
| A fails | Stop. The screen has no measured sensitivity and nothing it outputs means anything in either direction. No compound purchase, and the 15 GPU-hours for the main screen are not spent. |

## The staging rule, which is the operational point of this amendment

**The gate runs first, alone, and the main screen is not built or submitted until the gate has been
read.** The gate is about 15 jobs, roughly ten minutes of GPU. The main screen as selected is 1,200
jobs, about 15 GPU-hours. Running them together would spend the 15 hours before knowing whether any
of it is interpretable, and the gate own most likely outcome is the one that makes the main screen
uninterpretable. Order matters more than throughput here.

## One open technical item that blocks the gate

The gate compounds include two chemotypes that bind **by chelating the active-site metals** (the
benzoxaborole boronates and the hydroxamate). The job files as currently written contain **no metal
ions at all**, and an MBL-fold nuclease is a two-metal hydrolase. Scoring a metal-chelating ligand
against a metal-free active site would fail those rungs for a reason that has nothing to do with the
pipeline ability to rank binders.

So before the gate runs: whether and how metal ions are supplied must be settled, and **the same
policy must apply to the gate receptors and to the RNase J receptor**, or a Tier A pass and an
RNase J null are not comparable. The source structures are themselves inconsistent (Zn in 6M8Q, Fe
in 8T1Q and 8T1R, which Tao et al. attribute to bacterial expression), so the policy is ours to fix
and to state. It is being resolved against Boltz-2 schema in `cleanroom/BOLTZ_SCHEMA.md` and will
be recorded in a further amendment **before any score exists**.

## Two caveats carried forward from the survey

- The **Kd of 370 nM** for the JTE-607 acid is the most load-bearing number in the gate and the
  assay behind it is **unverified**: the Nat Chem Biol methods are paywalled, so whether it came
  from SPR, ITC, MST or competition is not established. Do not quote it externally before reading
  the PDF. The co-crystal 6M8Q does not depend on it.
- **Both chains of the target are predictions.** P75497 and P75174 have zero PDB entries between
  them, and P75174 is annotated only as "uncharacterized MG423 homolog" with no function, family or
  subunit assignment. The interface this screen aims at is not in any deposited structure. That was
  already stated in the limitations above; the survey confirms it independently.

---

# Amendment 2, 2026-09-25: the metal policy, the pocket policy, and a correction to the gate's cost

Still **before any Boltz-2 score exists**. What has been read since Amendment 1: the deposited
structures themselves (sequences, ligands, metal stoichiometry, and ligand contact residues, all
fetched from RCSB and cached under `cleanroom/gate_cache/`). No prediction has been run.

Amendment 1 left one technical item open and made one estimate. Reading the structures settles the
item and shows the estimate was wrong. Both are recorded here.

## 1. The metal policy: one catalytic Zn per nuclease chain

The assumption going in was the canonical **di-zinc** metallo-beta-lactamase site. **The deposited
structures of this subfamily do not support it.** Counted from the entries themselves:

| Entry | Protein | Metals deposited | Per chain |
|---|---|---|---|
| 6M8Q | human CPSF3 + JTE-607 acid | 2 Zn, for 2 protein copies | 1 Zn |
| 8T1Q | human CPSF73 + benzoxaborole | 1 Fe | 1 |
| 8C8S | human SNM1A + hydroxamate | 1 Zn | 1 Zn |
| 7APV | human Artemis + ceftriaxone | 1 Zn + 1 Ni | 1 Zn |
| **3ZQ4** | ***B. subtilis* RNase J1 tetramer** | 4 Zn + 4 Ca, 4 chains | **1 Zn** |

3ZQ4 matters most: it is the template this project's own RNase J heterotetramer model was built and
validated against (`new_biology/RNASEJ_MG423.md`), and it carries one Zn per chain.

**Policy, applied identically to every MBL-beta-CASP receptor including the RNase J target: one Zn
per nuclease chain.** The Fe in 8T1Q and 8T1R is substituted with Zn, which Tao et al. attribute to
bacterial expression. Crystallisation additives (PO4, SO4, CL, EDO, DMS) and the idiosyncratic
second ions (the Ni in 7APV, the Ca in 3ZQ4) are not modelled, because including them for some
receptors and not others is the inconsistency Amendment 1 forbade.

**One receptor is exempt and the exemption is stated:** nsp10-nsp14 is not an MBL-fold protein. Its
2 Zn and 1 Mg are a structural zinc site and the ExoN catalytic metal, both real, so it is built as
deposited.

## 2. The pocket policy: every gate ligand is constrained to its own crystallographic site

A problem Amendment 1 did not catch. The screen steers each ligand to the RNase J interface with a
pocket constraint. The gate as described would have run **unconstrained**. A pocket constraint
changes the pose search and plausibly the score, so an unconstrained gate and a constrained screen
are **not the same protocol**, and a gate pass would not transfer.

So each gate ligand is constrained to the residues within 5 A of it **in its own co-crystal**,
computed from the deposited coordinates, truncated to the same 20 contacts the screen uses.
Compounds without their own structure, and every decoy, use their receptor's reference pocket, so
the null answers the right question: what an unrelated compound scores when forced into that same
pocket.

Contacts found: CPSF73/JBG 31, Artemis/ceftriaxone 19, SNM1A/U2O 12, **nsp10-nsp14/A1IGR 12 spanning
both chains**. That last one is worth stating plainly: the Tier B rung's pocket is confirmed by the
coordinates to sit across the protein-protein interface, which is what makes it the rung that
licenses an interface claim.

## 3. Correction: the gate is 250 jobs, not 15, and 3 to 6 GPU-hours, not ten minutes

Amendment 1 said "about 15 jobs, roughly ten minutes of GPU". **That was wrong**, and the error was
omitting the null. The pass criteria are stated as percentiles of a matched null, and scores are not
comparable across different proteins, so **each receptor needs its own null**. At 60 decoys per
receptor across 4 receptors that is 240 null jobs against 10 gate compounds: **250 jobs, 3.1
GPU-hours at 45 s and 6.2 at 90 s.**

The staging conclusion is unchanged and if anything is firmer. The gate is still one fifth to one
third of the main screen's 15 hours, and it still decides whether those 15 hours produce anything
interpretable. **Gate first, alone, unchanged.** But it is not free and the earlier figure should
not be quoted.

**A consequence for the criteria.** With 60 decoys, "above the 95th percentile" is estimated from
the top 3 and is noisy. The criteria in Amendment 1 are therefore restated as exact ranks, which
need no percentile estimate: **a gate compound passes if it outscores at least 57 of its receptor's
60 matched decoys** (empirical p = 3/61 = 0.049). A1, B1 and B2 are read this way. A2 and A3 are
unchanged, being direct comparisons.

## 4. Two receptor decisions recorded so they are not silently forgotten

- **Receptors are the crystallised constructs, not full-length UniProt.** 6M8Q's CPSF3 entity is 478
  residues against 684 in UniProt; 8C8S's SNM1A is 343 against 1,040. Full length would fold domains
  the co-crystal never contained and cost several times more.
- **The IP6 / Integrator rung of Tier B is declared and deliberately not built.** The *Drosophila*
  cleavage module is IntS4 1,032 + IntS11 597 + IntS9 654 = **2,283 residues**, an 80GB-class job per
  ligand costing more than the entire main screen. It stays in the code behind `--with-integrator`
  so the reason for its absence is in the repository rather than in anyone's memory. **Tier B
  therefore rests on the nsp10-nsp14 fragment rung alone**, which was already the harder and more
  informative of the two, but it means Tier B is a single rung and B2 carries it.
