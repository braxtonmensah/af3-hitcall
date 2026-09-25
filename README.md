# When is a confident AI prediction of a protein complex actually right?

Genome-scale AI structure prediction proposes protein interactions far faster than anyone can test
them, and the confidence scores do not come with an interpretation. This repository measures how often
a confident prediction about a **never-before-solved** complex turns out to be correct, using
predictions that were frozen before the answers existed.

**Headline:** Among predicted pairs that were subsequently solved, the interface was correct in 81%
of 146 confident human cases and 89% of 84 confident yeast cases, against 2% for low-confidence human
cases. This is conditional on later structure solving; it does not estimate the chance that an
arbitrary unsolved pair interacts in cells.

Applying the method to *Mycoplasma pneumoniae* produced a **2:2 RNase J : MPN621 assembly
hypothesis** consistent with published crosslinks and co-elution. The interaction and MPN621 paralog
assignment were previously reported; the proposed stoichiometry has not been directly measured here.

Braxton Mensah, Indiana University Bloomington. bsmensah@iu.edu

---

## Why you should believe any of this

Every hypothesis was written down in a `PREREG_*.md` file and committed to version control **before**
the corresponding data were joined. `git log` preserves the order, and that ordering is the point:
it is externally checkable rather than asserted.

- **21 hypotheses pre-registered.** 8 returned negative or inconclusive and are reported, not dropped.
- **Claims were retracted when checks failed**, and the retractions are in the history.
- Post hoc analyses are labelled as post hoc, in `POSTHOC.md`.

If you want to audit this, start with `git log --oneline` and compare commit dates against the
deposition dates of the structures used as ground truth.

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

**Drug-development status:** the RNase J : MPN621 interface is a possible target to investigate, not
a validated drug target. The closest human relative, CPSF73, retains three of four aligned catalytic
residues; the compared interface residues are 24.6% identical. Neither observation establishes
selective inhibition or antibacterial activity.

### What is *not* claimed

RNase J is a **known** metallo-beta-lactamase fold. The contribution here is a computational 2:2
architecture consistent with published crosslinks, a sequence-based catalytic-residue comparison,
the SEC-based stoichiometry argument, and an interface map. The interaction itself appears in
O'Reilly et al. 2020's PPI table and supplementary discussion, which also identifies MPN621 as the
missing paralog. Lluch-Senar et al. 2015 annotate MPN621 as "probably non-catalytic". See
`new_biology/RNASEJ_MG423.md` for the evidence and prior-work limits.

**Species caveat:** MG423 is non-essential in *M. genitalium* though MPN621 is essential in
*M. pneumoniae*. The essentiality observation supporting further target investigation comes from
*M. pneumoniae*.

## Layout

| Path | Contents |
|---|---|
| `PREPRINT_DRAFT.md` | the full write-up |
| `PREREG_*.md` | the 21 pre-registrations, committed before data were joined |
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
planned virtual screen has not produced results; university compute access is still being arranged
(see `IP_RECORD.md` for provenance notes).

The RNase J complex is computational plus published orthogonal data. **No new experiment has been
performed.** The obvious next step is a wet-lab test, and I am looking for a group that wants to run
one.
