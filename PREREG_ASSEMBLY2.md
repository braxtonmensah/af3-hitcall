# Pre-registration 30: co-dependency assemblies, with the gate fixed (ASSEMBLY2)

Written 2026-09-25, **after `PREREG_ASSEMBLY` failed its own gate and before any clustering was run
under the design below.** The outcome section of that file records why it failed and is the reason
this one exists.

## What went wrong last time, in one paragraph

`PREREG_ASSEMBLY` capped clusters at 60 members and then measured recovery of CORUM complexes. Most
of the graph formed communities larger than 60, so only 332 of 3,527 genes reached a kept cluster and
**70% of the complexes in the gate's denominator had zero members in any kept cluster**. A0 measured
the size cap, not the clustering, and a correct method would have failed it too. The "CORUM
complexes" were also reconstructed from Burke S1's pairwise annotation column, 21% of which are a
single pair, so the denominator was not CORUM either.

**This is a new test, not a rescue.** The previous result stands as recorded: failed, uninterpreted,
nothing claimed.

## The three fixes, fixed now

1. **Real CORUM.** CORUM 5.0 human complexes, `corum_humanComplexes.txt`, Zenodo record
   **10.5281/zenodo.17419058** (deposited 2025-01-21), 5,366 complexes with explicit
   `subunits_gene_name` lists. Not a projection through one screen's pairs.
2. **No size cap anywhere in the gate.** Clusters of any size are eligible for recovery. A size window
   applies only to the A2 *output* list, because a 400-protein cluster is not a folding target, and
   that window is declared below rather than being allowed to affect the gate.
3. **A coverage-aware gate.** A complex enters the denominator only if at least 3 of its subunits are
   in the gene universe, and per-complex coverage is reported so the gate cannot silently measure
   something else again.

## Data and universe (fixed now)

- **DepMap 24Q4 Public** `CRISPRGeneEffect.csv`, figshare DOI `10.25452/figshare.plus.27993248.v1`.
- **Universe:** every gene passing the CODEP variance floor (gene-effect SD at or above the 25th
  percentile of all genes). Roughly 13,400 genes. Unlike ASSEMBLY, the universe is **not** restricted
  by essentiality, because that restriction is part of what starved the last denominator.
- Pearson correlation on complete cases, minimum 300 shared cell lines.

## Graph and clustering (fixed now)

- Edges at **r >= 0.30**, as before.
- **Louvain** (`networkx.louvain_communities`, seed 30) at resolutions **0.5, 1.0, 2.0, 4.0**.
- **The reported partition is the one with the highest modularity.** Modularity is an intrinsic
  property of the graph and the partition; it does not see CORUM, so choosing on it is not choosing on
  the outcome. All four resolutions' results are reported in full regardless.

## Tests

**A0 (gate, read first).** Over CORUM complexes with at least 3 subunits in the universe: the fraction
whose in-universe subunits are **majority-contained in a single cluster** (more than half).
- Computed identically on a **degree-preserving edge-shuffled null** (seed 30) to give the chance
  floor.
- **Sensitive** if A0 >= **0.35** *and* A0 is at least **3x** the null's A0.
- **If A0 fails, everything below is reported and NOT interpreted, and the co-dependency-clustering
  route is closed for this project.** No third attempt. Two failed gates on the same idea is an
  answer.

**A1 (purity, descriptive).** For each cluster, the largest fraction of its members belonging to one
CORUM complex. Distribution reported.

**A2 (output, conditional on A0).** Clusters of size **3 to 40** in which **no pair of members appears
together in any CORUM complex** and **fewer than 25%** of member pairs carry BioGRID or IntAct
evidence in Burke S1. Reported with size, mean internal r, and members.

**A3 (null for A2).** The same A2 count on the degree-preserving null. **A2 must exceed it** or there
is no result.

**A4 (the confound that cannot be removed, so it is measured).** For each A2 cluster, the median
number of PubMed citations across its members is not available here; instead report the median number
of Burke S1 rows each member appears in, as a proxy for how well studied it is, alongside the same
figure for A1 clusters with purity >= 0.5. **If A2 clusters are systematically less studied, they may
be unannotated because nobody looked, not because the assembly is new.** That reading is stated with
any result.

## Consequences fixed in advance

- A0 fails: route closed, recorded in `RESULTS.md`, no third pre-registration.
- A0 passes and A2 exceeds A3: the A2 clusters become pre-registered multi-chain folding targets,
  built as jobs in the form of `cleanroom/bridge/`. They are called **candidate assemblies**, never
  complexes, and A4's confound is quoted in the same paragraph.
- **No cluster is a discovery until a structure or an experiment says so.** Co-dependency is
  correlational and clusters contain pathway modules that never touch.

## Limitations, stated before the result

- Louvain is stochastic; the seed is fixed and the four resolutions are all reported.
- Shared pathway and physical complex are not separable by this data.
- DepMap is cancer cell lines; assemblies with no fitness phenotype in culture are invisible.
- CORUM is itself incomplete, so an "unannotated" cluster may be annotated elsewhere. A2 is therefore
  a candidate list, and its false-positive rate against the wider literature is unmeasured here.


---

# OUTCOME, recorded 2026-09-25: A0 FAILED. The route is closed, as this file committed.

**A0 = 27.6% (540 of 1,955 CORUM complexes majority-recovered), against a 35% bar.** It fails on the
absolute criterion at every resolution tested: 27.6% at 0.5, 27.5% at 1.0, 23.6% at 2.0, 22.7% at 4.0.
This is not a tuning artifact. Universe 13,437 genes, 62,332 edges, real CORUM 5.0, coverage-aware
denominator with median coverage 3 subunits per complex. The gate was fair this time and the method
did not clear it.

**Per the rule written above, the co-dependency-clustering route is closed. There is no third
pre-registration.**

## The ratio criterion was also mis-designed, and that is recorded rather than quietly dropped

A0 on the degree-preserving null came out at **51.9%**, higher than the real graph. That is not the
null beating the method; it is a degenerate null. Louvain on the shuffled graph returns **one
community of 4,777 nodes, 35.6% of the graph**, with the next largest being size 3. A single blob
trivially contains a majority of every complex's subunits. So the "3x the null" criterion could never
have been informative, and it was my specification error for the second time in this pair of
pre-registrations. It changes nothing here because the absolute bar failed independently.

## Why it failed, and this part is worth keeping

The A2 clusters show the reason plainly. They are **pathways, not physical assemblies**:

- `LZTR1 NF1 RASA2 SPRED1 SPRED2` - negative regulators of RAS. A real, tight functional module whose
  members largely do not touch each other.
- `CMAS GNE NANS SLC35A1` - sialic acid biosynthesis. Enzymes acting in series, not a complex.
- `ASNS ATF4 EIF2AK4 GCN1` - the integrated stress response.
- `RAB18 RAB3GAP1 RAB3GAP2 TBC1D20` - the Warburg Micro syndrome module.

**Co-dependency partitions the genome into functional modules, and a functional module is usually a
pathway rather than a complex.** That is exactly why it cannot serve as a "what to fold together"
oracle: folding a pathway together predicts nothing. A0 is a test of *physical complex* recovery, and
the instrument measures something adjacent to but different from that.

The A4 confound also came in against the A2 list: the median number of Burke S1 appearances for an A2
cluster member is **1**. These proteins are unannotated in large part because few people have studied
them, not because a new assembly has been found.

## What this failure does for BRIDGE, which is the useful part

It sharpens why `PREREG_BRIDGE` is designed the way it is. BRIDGE does not partition anything. It asks
a **local** question: given a pair that already has independent physical support and a failed pairwise
model, which single gene is most co-dependent with **both**? That question stays inside the
neighbourhood of a known-real physical interaction, so it does not sweep in the pathway members that
sink a global partition. The two results are consistent: co-dependency is informative about physical
assembly *locally, conditioned on a real pair*, and not informative *globally, unconditioned*.

BRIDGE remains open and its jobs remain built. This file closes only the clustering route.
