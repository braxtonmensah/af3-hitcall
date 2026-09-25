# Structurally unsolved, functionally coupled, selectively essential interfaces

Produced 2026-09-25 from `PREREG_CODEP` (committed `0da2677` before any DepMap data was downloaded)
plus two post hoc filters that are labelled as post hoc below. Everything here is computed from public
data: Burke et al. 2021 predictions, DepMap 24Q4 Public gene effect, CORUM and BioGRID/IntAct flags as
carried in Burke's supplementary table.

**Read the limits section before using this list for anything.**

## What the list is

Three independent filters, applied in this order:

1. **Structurally confident and unsolved.** pDockQ > 0.23 in Burke's 2021 AF2/FoldDock screen, with no
   co-complex structure (`int3D_model_structure == 0`). n = 3,441 after the pre-registered variance,
   line-count and paralog filters.
2. **Functionally coupled.** Pearson r of the two genes' CRISPR gene-effect profiles across 1,178
   cancer cell lines above the pre-registered null 95th percentile (r > 0.105). n = 707.
3. **Selectively essential, not pan-essential** (post hoc). Both genes must have mean gene effect
   > -0.35, at least 15 cell lines with gene effect < -0.6, and dependency in no more than 25% of
   lines. n = **32**.

Step 3 is the one that matters commercially and it is the one nobody runs. A pan-essential complex is
not a drug target: the ribosome and the proteasome are co-dependent in every line and killing them
kills everything. 241 of the 707 co-dependent pairs (34%) are pan-essential and are excluded here for
that reason. What survives is dispensable in most cells and required in a definable subset, which is
the shape of a genetic dependency a drug can exploit.

## The 32

15 are annotated in CORUM. **17 are not**, and those are listed first because they are the ones where
the structural model is doing the most work.

### Not in CORUM

| Pair | r | pDockQ | Dep. lines | Why it is interesting |
|---|---|---|---|---|
| **NFE2L2 – MAFG** | 0.113 | 0.70 | 73 / 15 | NRF2 with its small MAF partner. NRF2 pathway activation is one of the most common events in lung and liver cancer, and this heterodimer is what binds the antioxidant response element |
| **ISL1 – LDB1** | 0.370 | 0.63 | 26 / 118 | LIM-homeodomain transcription factor with its canonical bridging partner; lineage-restricted dependency |
| **CCNC – PAX5** | 0.127 | 0.24 | 173 / 41 | PAX5 is a B-lineage dependency; cyclin C is the Mediator kinase module |
| **AP1M1 – IKZF1** | 0.149 | 0.27 | 16 / 22 | IKZF1 is the degron target of lenalidomide and the CELMoD series |
| **TMCO6 – ZNF511** | 0.647 | 0.71 | 53 / 83 | Two poorly characterised proteins with the third-highest co-dependency in the whole set and a confident interface. The most genuinely unexplored entry |
| **VPS45 – RBSN** | 0.645 | 0.72 | 169 / 153 | Endosomal tethering; both broadly but not universally required |
| **GATC – GATB** | 0.678 | 0.68 | 47 / 143 | Mitochondrial GatCAB amidotransferase |
| **UQCC1 – UQCC2** | 0.568 | 0.68 | 67 / 46 | Complex III assembly factors |
| **DNAJC2 – HSPA14** | 0.504 | 0.57 | 28 / 181 | Ribosome-associated chaperone complex |
| **ADAT3 – ADAT2** | 0.483 | 0.68 | 65 / 85 | tRNA adenosine deaminase heterodimer |
| **MRPL13 – MRPL19** | 0.586 | 0.26 | 62 / 134 | Mitoribosome large subunit |
| **MRPL11 – MRPL54** | 0.448 | 0.44 | 51 / 110 | Mitoribosome large subunit |
| **NME6 – RCC1L** | 0.376 | 0.66 | 30 / 98 | Mitochondrial nucleotide metabolism |
| **DDRGK1 – CDK5RAP3** | 0.264 | 0.46 | 26 / 83 | UFMylation pathway |
| **HSBP1 – BRK1** | 0.250 | 0.60 | 29 / 105 | BRK1 is a WAVE regulatory complex subunit |
| **FBXO7 – PSMF1** | 0.249 | 0.59 | 33 / 65 | F-box protein with the proteasome inhibitor PI31 |
| **CSNK2A1 – NKAPD1** | 0.132 | 0.25 | 25 / 46 | CK2 catalytic subunit with an uncharacterised partner |

### In CORUM

TADA2B–TADA1, SUPT7L–TADA1, TADA3–TADA2B, TADA3–TADA1 (SAGA/ATAC); COMMD3–CCDC22, COMMD3–COMMD8,
CCDC22–VPS35L (Commander/CCC); COG5–COG7; SMARCC1–SMARCD2, SMARCC2–SMARCD2 (SWI-SNF); NFKB2–RELB
(non-canonical NF-kB); CTBP1–ZEB1; RMND5A–MAEA (CTLH); AP1G1–AP1M1; ISL1-adjacent LDB1 pairs.

Full machine-readable list with all statistics: `codep_selective_targets.csv`.

## Limits, and they are severe enough to state before the list is used

- **Co-dependency is correlational.** Two proteins in the same pathway correlate without ever
  touching. The structural model is what argues for physical contact, and it is a prediction.
- **"Not in CORUM" does not mean "unknown interaction."** A post hoc check found **96.3%** of confident
  never-solved pairs already carry BioGRID or IntAct experimental evidence. Almost nothing here is a
  newly discovered interaction. What is new is the combination: a confident interface model, a
  functional dependency signal, a selectivity profile, and no solved structure.
- **The pre-registered effect does not hold outside annotated complexes.** Within CORUM-annotated
  pairs, confident predictions beat low-confidence ones by +0.0585 (CI [0.0178, 0.1002]); outside
  CORUM the gap is +0.0047 (CI [-0.0042, 0.0137]) and does not clear zero. Most of this list's
  non-CORUM entries therefore rest on the co-dependency and selectivity evidence, not on a
  demonstrated structural advantage for unannotated pairs.
- **Selectivity thresholds are post hoc** and were not pre-registered. They are a crude stand-in for
  DepMap's own strongly-selective classification. Changing them changes the list.
- **DepMap is cancer cell lines.** Tissue-restricted, post-mitotic and in-vivo-only biology is
  underrepresented, and a real complex with no fitness phenotype is invisible here.
- **No wet-lab experiment supports any entry.** Every row is a hypothesis for the bench.

## What this list is actually good for

Not "here are 32 drug targets". The honest framing is: **these are protein-protein interfaces that a
structural biologist could justify solving, and that an oncology group could justify testing, because
three independent public signals agree and no structure exists yet.** That is a real, defensible
research output and, as far as I can tell, nobody has produced this particular intersection before.
It is not a validated target list and must never be presented as one.
