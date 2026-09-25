# Pre-registration 29: can co-dependency alone reconstruct protein assemblies? (ASSEMBLY)

Written 2026-09-25, **before any clustering has been run** and before any cluster has been compared to
any complex annotation.

## Why

Today's CODEP result put a hard limit on the pairwise approach: AlphaFold confidence predicts
functional coupling **inside complexes the field has already annotated** (+0.0585, CI [0.0178, 0.1002])
and **not outside them** (+0.0047, CI [-0.0042, 0.0137]). The BRIDGE blind-spot cut showed why: the
pairs it misses sit inside large assemblies and cannot be seen two chains at a time.

The obvious response is to fold proteins together in groups rather than in pairs. The obstacle is
combinatorial: 17,916 genes give about 160 million pairs and vastly more triples, so **the binding
constraint is not folding, it is knowing which proteins to fold together.**

This test asks whether CRISPR co-dependency can supply that list with no curation at all. If
clustering the dependency matrix reconstructs known complexes, then the same clustering applied where
nothing is annotated produces candidate assemblies, and those are exactly the objects the pairwise
screen is blind to.

**This is the discovery list the registry turned out not to be.** CODEP showed 96.3% of the registry's
confident pairs already carry interaction evidence. A cluster with strong internal co-dependency and
no annotation is a different kind of object, and it is what this test is for.

## Data (fixed now)

- **DepMap 24Q4 Public** `CRISPRGeneEffect.csv`, figshare DOI `10.25452/figshare.plus.27993248.v1`.
  Same file and same variance floor as CODEP (gene-effect SD at or above the 25th percentile).
- **Gene universe:** genes passing the variance floor that are **selectively essential** by the CODEP
  definition (mean gene effect > -0.35, at least 15 lines below -0.6, at most 25% of lines), **union**
  genes with mean gene effect < -0.35 that pass the variance floor. Pan-essential genes are kept here,
  unlike in `TARGETS.md`, because the ribosome and proteasome are the positive controls for whether
  clustering works at all.
- **Annotation:** CORUM membership as carried in Burke S1 (`CORUM_ID_selection`), and BioGRID/IntAct
  evidence columns, both already in the repository.

## Method (fixed now, no free parameters chosen after seeing output)

1. Pearson correlation between every pair of genes in the universe, complete cases, minimum 300
   shared cell lines.
2. Build an undirected graph keeping edges with **r >= 0.30**. That threshold is roughly three times
   the CODEP null 95th percentile (0.105) and is fixed now.
3. Community detection with **`networkx.louvain_communities`, resolution 1.0, seed 29**.
4. Keep communities of size **3 to 60**. Smaller is a pair (already covered by CODEP), larger is not
   an assembly.

## Tests

**A0 (instrument gate, read first).** Of the CORUM complexes that have at least 3 members inside the
gene universe, what fraction have a majority of those members landing in a single cluster?
- **Sensitive** if at least **40%** of such complexes are majority-recovered.
- **If A0 fails, everything below is reported but NOT interpreted.** A clustering that cannot find the
  proteasome has nothing to say about unannotated assemblies.

**A1 (purity).** For each cluster, the fraction of its members that belong to the single most common
CORUM complex among them. Report the distribution, and the number of clusters at or above 0.5 purity.

**A2 (the output).** Clusters of size 3 to 60 in which **no member pair is CORUM-annotated** and
**fewer than 25% of member pairs have any BioGRID or IntAct evidence**. These are the candidate
unannotated assemblies. Report every one with its size, mean internal r, and member list.

**A3 (null).** Repeat steps 1 to 4 on a degree-preserving edge-shuffled graph (same number of edges,
same degree sequence, seed 29), and report how many size-3-to-60 clusters and how many A2-qualifying
clusters it produces. **An A2 count that does not exceed the null count is not a result.**

## Consequences fixed in advance

- If A0 fails, the approach is abandoned and this file records that.
- If A0 passes and A2 exceeds A3's null, the qualifying clusters become the pre-registered target list
  for multi-chain structure prediction, and the top ones by internal co-dependency are built as jobs
  in the same form as `cleanroom/bridge/`.
- **No cluster is called a complex on this evidence.** Co-dependency is correlational; a cluster is a
  hypothesis about which proteins to fold together, nothing more. Any write-up says so in the same
  paragraph as the result.

## Limitations, stated before the result

- Louvain is stochastic and resolution-dependent. The seed and resolution are fixed here, but a
  different resolution gives a different partition, and that sensitivity is reported, not hidden.
- Co-dependency cannot distinguish physical complex membership from shared pathway. Clusters will
  contain pathway modules that never touch.
- DepMap is cancer cell lines, so assemblies without a fitness phenotype in culture are invisible.
- An unannotated cluster may be unannotated because its members are poorly studied rather than because
  the assembly is new. That confound cannot be removed with this data and is stated with any result.


---

# OUTCOME, recorded 2026-09-25: A0 FAILED, and the fault is in this pre-registration

**A0 = 34 of 447 CORUM complexes majority-recovered, 7.6%, against a 40% bar. The gate fails, so by
the rule written above nothing downstream is interpreted.** A2's 37 unannotated clusters are reported
in `assembly_unannotated.csv` and are **not claimed**.

## Why it failed, diagnosed rather than explained away

The failure is **not** that co-dependency cannot group proteins. It is that this file specified a
size cap and then measured recovery against complexes the cap had already thrown away.

- Gene universe: 3,527. Genes actually placed in a size-3-to-60 cluster: **332**, under 10%.
- Louvain at resolution 1.0 put most of the graph into communities **larger than 60**, which step 4
  discarded.
- Of the 447 complexes in A0's denominator, **70% had zero members inside any kept cluster**. The
  median fraction of a complex's members landing in a kept cluster was **0.00**.

So A0 measured the size cap, not the clustering. A gate that a correct method would also fail is a
broken gate, and it was written here before the data was seen, which is where the fault belongs.

A second, smaller specification error: the "CORUM complexes" were reconstructed from Burke S1's
pairwise `CORUM_ID_selection` column, so 21% of them are a single pair and none are guaranteed
complete. That is not the CORUM complex list, it is a projection of CORUM onto one screen's pairs.

## What is NOT claimed

The A2 clusters include what look like the Fanconi anemia pathway, PBAF, the VHL-Elongin-EGLN1
complex, peroxisome biogenesis, UFMylation and the SKI complex. **Recognising them is not evidence.**
It is the same after-the-fact recognition that `PREREG_BRIDGE.md` explicitly refuses to count, and the
gate that was supposed to license the claim did not pass. Nothing from this run goes into the
preprint, a grant application, or any pitch.

One descriptive observation that does survive, because it needs no gate: the degree-preserving null
produced **zero** clusters in the 3-to-60 size range against 58 in the real graph. The dependency
graph is not random. That says the structure is real; it says nothing about whether this partition of
it is right.

## What a corrected test needs, and it is a NEW pre-registration

Re-running with a different cap after seeing this fail would be gate-shopping. A corrected version is
`PREREG_ASSEMBLY2` and must fix three things:

1. **Real CORUM**, downloaded from the CORUM resource, not projected from Burke pairs.
2. **No hard size cap.** Multi-resolution or hierarchical clustering, with the resolution chosen by a
   criterion fixed in advance, so no complex is discarded before it can be recovered.
3. **A0 computed only over complexes whose members are actually in the gene universe**, with the
   coverage reported per complex, so the gate cannot again measure something other than recovery.

Until that exists, the honest statement is: **co-dependency clustering was tried once, the test as
designed could not evaluate it, and the question is open.**
