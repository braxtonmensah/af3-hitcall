# When is a confident AI prediction of a protein complex actually right?

Genome-scale AI structure prediction proposes protein interactions far faster than anyone can test
them, and the confidence scores do not come with an interpretation. This repository measures how often
a confident prediction about a **never-before-solved** complex turns out to be correct, using
predictions that were frozen before the answers existed.

**The test is a time split that cannot be arranged after the fact.** The predictions were published
by other groups in 2021. They are scored here against complexes the PDB released between 2022 and
2026, so the answers did not exist anywhere when the predictions were made. That separation is
external to this repository and does not depend on trusting anything inside it.

**Headline:** among confident never-solved pairs that were later solved, the interface was correct in
**81% of 146 human cases** and **89% of 84 yeast cases**, against **2%** for low-confidence human
cases. Two things qualify that number and both belong in the same breath as it.

- **It is conditional on the pair later being solved**, which is 2.7% of confident calls. It is not
  the probability that an arbitrary confident pair interacts in cells.
- **Read it as the top of a range.** Most 2022-2026 entries are cryo-EM, and cryo-EM models are
  sometimes built starting from AlphaFold, which would let a model agree with itself. On the
  X-ray-only subset the rate is **53% (n = 19, CI [0.32, 0.74])**. The defensible claim is **53% to
  81%**, and that spread is the honest measure of how much circularity cannot be excluded.

Applying the method to *Mycoplasma pneumoniae* produced a **2:2 RNase J : MPN621 assembly
hypothesis** consistent with published crosslinks and co-elution. The interaction and MPN621 paralog
assignment were previously reported; the proposed stoichiometry has not been directly measured here.

Braxton Mensah, Indiana University Bloomington. bsmensah@iu.edu

---

## Why you should believe any of this

**First, the time split above.** It is the load-bearing control, and it is external. The ground truth
was deposited in the PDB by other groups, years after the 2021 predictions were published. Nothing in
this repository can move those dates, and no choice made here can reach back and change them.

**Second, pre-registration.** Every hypothesis was written into a `PREREG*.md` file and committed
before the corresponding data were joined. There are **33** of them, and you can count them with
`ls PREREG*.md`.

- **Ten returned a negative, inconclusive, or failed-gate result** and are reported rather than
  dropped: CLINVAR, CLINVAR2, LITJEV, CONTEXT, STRUCT, COMPOSE, ASSEMBLY, ASSEMBLY2, CODEP_R, OMEGA.
- **Three claims were withdrawn** after later checks contradicted them. The withdrawals are in the
  history, not edited away.
- Post hoc analyses are labelled as post hoc, in `POSTHOC.md`.

**About the commit history, plainly:** it is compressed. Most of this was committed across a small
number of days, so the gap between a registration and its result is often hours rather than weeks.
The ordering is real and you can check it with `git log --oneline`, but read it as bookkeeping, not
as the evidence. The evidence is that predictions frozen in 2021 could not have been tuned against
structures released from 2022 onward.

## The result in one table

| Test | Confident | Low confidence |
|---|---|---|
| Human, interface correct (F1 >= 0.5) | **81%** (n = 146) | 2% (n = 110) |
| Yeast, interface correct | **89%** (n = 84) | shuffled null 1% |

**Selection limit:** all evaluated pairs in this table had a structure solved after the predictions
were recorded. Solving is not random, and these fractions are not calibrated probabilities for
unsolved candidates.

Survived five pre-registered attacks:

| Attack | Result |
|---|---|
| Remove all homologous structural precedent | 81% human, 92% yeast |
| Shuffle interfaces to random positions | 2% human, 1% yeast |
| Entry-level cluster bootstrap | CIs unchanged |
| Independent metric (Fnat from raw coordinates, separate code) | 80% human, 87-90% yeast |
| Threshold grid (6/8/10 A x F1 0.3/0.5/0.7) | 57% to 88%; 81% at the registered setting |

## Three claims this repository retracted about itself

Both came from tests that were pre-registered specifically to attack earlier results, and both are
reported here rather than quietly dropped.

| Retracted | Why |
|---|---|
| "The stoichiometry rule recovered RNA polymerase beta/beta-prime blind" | PDB assembly records label that pair 1:1 in 367 of 370 assemblies. HIGHER_CAL's pre-registration required its removal. Verified recoveries are RpoA-RpoB and three pyruvate dehydrogenase pairs |
| "MG354 may be the missing omega subunit" | OMEGA found no omega-family fold in either search direction. MG354 binds RNA polymerase; it does not look like omega. Its structure is already solved (PDB 1TM9); it is uncharacterized in function, not structure |
| "Confident never-solved predictions are functionally coupled" (CRISPR co-dependency) | Claimed from DepMap CRISPR, then **withdrawn the same day** when CODEP_R failed to replicate it in RNAi. The RNAi gate passed at +0.0486, so the instrument was sensitive; the primary came back -0.0042, CI [-0.0129, 0.0047]. Do not cite CODEP without CODEP_R |

The stoichiometry rule now ships with measured error rates instead of a list of successes:
**sensitivity 75%, false-positive rate 12%, precision 64% against a 22% base rate** (n = 54 pairs
with a solved homologous co-complex).

**Conservative bound:** the X-ray-only subset gives 53% (n = 19). Stated up front because most recent
depositions are cryo-EM and some are built with AlphaFold assistance.

## What the screens miss

Not random. Missed interactions have roughly one third the interface area of recovered ones (30 vs 85
residue-pair contacts), come from larger assemblies, and are far more likely to have their interface
also touching a third chain. These are **non-autonomous contacts**: interfaces that do not form in
isolation. Six attempts to recover them from information already in the model output all failed, which
suggests the information is absent from a pairwise calculation rather than discarded by the scoring.

## The biology

Models of *M. pneumoniae* RNase J (MPN280) and MPN621 favor a 2:2 heterotetramer over the modeled
1:1 alternative. This is a structural hypothesis, not an experimentally established stoichiometry.

| Evidence | Result |
|---|---|
| Pooled AF3 screen | top 0.1% of 113,050 pairs, never solved |
| Dedicated AF3 of the tetramer | ipTM 0.84; **6/6 in-cell crosslinks under 30 A in 5/5 samples** |
| Heterodimer alone | 3 crosslinks stranded at 51-63 A |
| Specificity control | length-matched decoy, ipTM 0.12-0.17 |
| Crosslinks, two chemistries | DSSO and DSS agree on the same residue pairs |
| SEC-MS (published) | both peak at apparent mass 297.8 kDa; favors a larger assembly over 1:1 but cannot establish stoichiometry alone |
| Essentiality (published) | both subunits essential in *M. pneumoniae* |
| Catalytic residues | RNase J 4/4 retained; MPN621 **0/4** |

MPN621 retains the fold but not four aligned catalytic residues; catalytic inactivity has not been
directly measured here. Changing chain composition drops the predicted RNase J self-association
confidence from ipTM 0.81 to 0.50, which motivates a structural-role hypothesis but does not measure
stabilization in cells.

**Drug-development status, corrected 2026-09-26: the interface itself is not ligandable, and no
screen against it will be run.** A buried-cavity scan of both ortholog models
(`cleanroom/analysis_ligandability.py`) puts the largest non-catalytic cavity at the interface at
**26 and 27 A^3** on the RNase J side, against 76 A^3 for the shallowest *drugged* reference in the
calibration set and 575 for a comfortably drugged one. MPN621's side looked better at 273 A^3 but
**does not replicate**: the ortholog gives 82, a ratio of 3.3, while the three other cavities measured
agree within 9%. So the flat reading is the reproducible one.

What survives is a different site: **MPN621's own degenerate cleft**, 491 and 470 A^3 across the two
models (ratio 1.04), on residues where **0 of 4 catalytic positions are conserved** while RNase J
keeps all four and human CPSF73 keeps three. Its cleft is 25% identical to its paralogue's and 20% to
CPSF73's, which is no more than background identity, i.e. it carries no active-site conservation
constraint. That is a selectivity *prospect* and not a measured margin. Pre-registered as
`PREREG_MPN621.md`; **not run**.

None of this establishes selective inhibition or antibacterial activity, and MPN621 has no known
function, so a ligand in its cleft may do nothing. Its essentiality is the only functional handle and
it is species-split: essential in *M. pneumoniae*, annotated non-essential for the *M. genitalium*
ortholog.

**A funding claim previously made here does not hold.** PACE's 2025 call is
restricted to drug-resistant Gram-negatives and CARB-X runs off the CDC 2013 and WHO 2017 lists;
*M. pneumoniae* is on none of them, and it cannot be fixed by changing organism because RNase J is
absent from *E. coli* and most Gammaproteobacteria.

### What is *not* claimed

RNase J is a **known** metallo-beta-lactamase fold. The contribution here is a computational 2:2
architecture consistent with published crosslinks, a sequence-based catalytic-residue comparison,
the SEC-based stoichiometry argument, and an interface map. The interaction itself appears in
O'Reilly et al. 2020's PPI table and supplementary discussion, which also identifies MPN621 as the
missing paralog. Lluch-Senar et al. 2015 annotate MPN621 as "probably non-catalytic". See
`new_biology/RNASEJ_MG423.md` for the evidence and prior-work limits.

**Species caveat:** MG423 is non-essential in *M. genitalium* though MPN621 is essential in
*M. pneumoniae*. Any argument resting on essentiality rests on the *M. pneumoniae* observation only.

## Layout

| Path | Contents |
|---|---|
| `STATE.md` | **read first**: current status, what is claimable, what was retracted |
| `PREPRINT_DRAFT.md` | the full write-up |
| `PREREG*.md` | the 33 pre-registrations, committed before data were joined |
| `RESULTS.md` | every test and its numbers |
| `POSTHOC.md` | analyses that were not pre-registered, labelled |
| `analysis_*.py`, `verify_*.py` | the analysis code; these are the authoritative record |
| `rnasej/` | AFJ scorer, interface map, SEC stoichiometry |
| `new_biology/` | the RNase J write-up and models (**non-commercial, see LICENSE**) |
| `cleanroom/` | prepared Boltz-2 screen inputs and scripts; no completed screen result claimed |
| `registry/` | 6,010 confident-pair candidates, sha256 in `SHA256.txt` |

## Reproducing

Python 3.11 (not 3.13: `biopython`, `dm-tree` and `gemmi` have no 3.13 wheels).

```bash
pip install -r requirements.txt
python analysis_future.py        # the prospective human test
python analysis_future_yeast.py  # yeast
python verify_v4.py              # independent Fnat recomputation + threshold grid
python rnasej/score_afj.py       # the RNase J tetramer scorer
```

All inputs are public: Todor et al. 2026 (Zenodo 15499631), Burke et al. 2023, Humphreys et al. 2021
(ModelArchive ma-bak-cepc), O'Reilly et al. 2020 (PRIDE PXD017711/PXD017695, CC0), Lluch-Senar et al.
2015, RCSB PDB, SIFTS, UniProt.

## Licence, and one thing to be careful about

**This repository is not under a single licence.** Code and analysis are MIT. The six AlphaFold Server
model files in `new_biology/` and `rnasej/` are **non-commercial only** under the AF Server Output
Terms, which also forbid using that output in ligand-binding prediction. That prohibition is why the
planned virtual screen in `cleanroom/` uses Boltz-2 (MIT) from public sequences with no AlphaFold input
anywhere. Read `LICENSE` before reusing anything.

## Status

No lab, no faculty sponsor, no institutional funding, no grant. The analyses use public data. The
planned virtual screen has not produced results.

The RNase J complex is computational plus published orthogonal data. **No new experiment has been
performed.** The obvious next step is a wet-lab test, and I am looking for a group that wants to run
one.
