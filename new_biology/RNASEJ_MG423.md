# New biology hypothesis: Mycoplasma RNase J is an (RNase J1 : MG423)x2 heterotetramer

Status: **computationally solved (PREREG_AFJ, all 4 pre-registered outcomes passed); supported by two independent
in-cell crosslink datasets; not yet tested at the bench.**

## Dedicated AlphaFold 3 runs (AlphaFold Server, 2026-09-25)

| Job | ipTM | Crosslinks within 30 A |
|---|---|---|
| *M. pneumoniae* RNase J (P75497) x2 + MG423 homolog (P75174) x2 | **0.83-0.84** (RNase J : partner 0.81-0.82) | **6/6 in 5/5 samples** (14-23 A) |
| *M. genitalium* MG139 x2 + MG423 x2 | 0.82 | 6/6 in 5/5 samples |
| Heterodimer only (P75497 + P75174) | 0.81 | 3 near links yes, 3 far links no (51-63 A), as predicted |
| Decoy: RNase J x2 + PtsI (P75168, length-matched) x2 | 0.31 overall; RNase J : decoy **0.12-0.17** | n/a |

AF3 received no crosslink information. It builds a confident heterotetramer that satisfies every in-cell
crosslink, and it does not pair RNase J confidently with an unrelated protein. The RNase J : RNase J
interface scores ipTM ~0.50 without MG423 and ~0.81 with it, suggesting MG423 stabilizes the assembly.
Models: `rnasej_mpn_2x2_AF3_model_0.cif`, `rnasej_mg_2x2_AF3_model_0.cif`. AF Server may use PDB templates up
to 2021-09-30 (e.g. B. subtilis RNase J1, 3ZQ4); the crosslinks were never an input.
Every step was pre-registered (PREREG_XLVAL, PREREG_XLDSS, PREREG_TETRA); post hoc steps are marked.

## Claim

In *Mycoplasma genitalium* (and *M. pneumoniae*), the uncharacterized protein **MG423** (UniProt P47662;
*M. pneumoniae* ortholog P75174) is the partner of the essential RNA-degrading enzyme **RNase J (MG139,
P47385)**. The two form a J1/J2-type heterodimer, and two heterodimers assemble into a
**heterotetramer** in the same dimer-of-dimers arrangement as the *B. subtilis* RNase J1 tetramer (3ZQ4).

## Evidence

| Line of evidence | Result |
|---|---|
| AF3 genome-wide pooled screen (Todor et al. 2026) | MG139-MG423 size-corrected ipTM 0.65, top 0.1% of 113,050 pairs; never solved |
| Our validation of such predictions | Confident never-solved AF predictions have the right interface ~80-90% of the time (FUTURE, VERIFY) |
| In-cell crosslinks, DSSO (O'Reilly 2020, PXD017711) | 4 MG139-MG423 links; 2 within 30 A of the AF3 heterodimer interface (post hoc sequence fix) |
| In-cell crosslinks, DSS (PXD017695), independent | 4 links; 3 within 30 A (null 95th pct 0.35). The two near links are the **same residue pairs** as with DSSO (MG139 K120 to MG423 502 and 546) |
| Far links, both datasets | MG139 225/228/257 to MG423 224: 51-63 A in the dimer, i.e. not explained by one heterodimer |
| Heterotetramer on the 3ZQ4 template | **All 6 distinct links within 30 A in 5/5 AF3 samples** (far links 12.5-15 A across copies; random-lysine null 95th pct 0.33); 1-7 minor CA clashes. Copy placement used structural fit only, never the crosslinks |
| Controls | 0/20 crosslinked low-confidence pairs pass the same test (both datasets) |

Model: `rnaseJ_MG139_MG423_heterotetramer_CA.pdb` (MG139 = chains A, C; MG423 = chains B, D; CA only).

## Interface map and target assessment (post hoc, `rnasej/interface_map.py`, 2026-09-25)

**Architecture is a dimer of heterodimers.** All-atom contacts (<= 5 A) in the M. pneumoniae AF3 model:
RNase J(A)-partner(C) 178 contacts and B-D 178, but A-D only 9 and B-C only 7. The two heterodimers are
joined by a RNase J : RNase J interface (60 contacts) and a partner : partner interface (64).
The main interface buries 65 RNase J residues and 66 partner residues.

**MG423/MPN_621 is a catalytically dead pseudo-nuclease (measured here).** Against *B. subtilis* RNase J1
(Q45493), whose catalytic/Zn-ligand residues are H76, D78, H79, H368:

| Protein | Identity to BsJ1 | Catalytic residues kept |
|---|---|---|
| RNase J, MPN_280 (P75497) | 39.9% | **4/4** (H83, D85, H86, H377) |
| MG423 homolog, MPN_621 (P75174) | 25.1% | **0/4** (V71, E73, N74, N365) |
| Human CPSF73 (Q9UKF6) | 25.2% | 3/4 at aligned positions |

So the partner keeps the fold and loses the chemistry: consistent with a structural/regulatory subunit
rather than a second nuclease.

**Human off-target.** The nearest human relative is CPSF73 (CPSF3), itself a drug target. RNase J is 25%
identical to it overall, and the 65 interface residues are only **24.6% identical** to CPSF73 (16.9% to
CPSF100). Read-out for a drug-discovery programme: the **interface** is much less human-like than the
active site, so an interface-directed agent is the selective option, while an active-site nuclease
inhibitor would risk CPSF73 cross-reactivity.

Interface residue lists: `rnasej/results_interface.json`.

## What is new and what is not

**Corrected 2026-09-25 after a deeper prior-art check. Two earlier claims were too strong:**

- **The interaction itself is already in published data.** RNase J (P75497) - P75174 is listed in
  O'Reilly et al. 2020's own PPI table at 5% PPI FDR (fdr = 0.0), i.e. their published dataset already
  contains this interaction; their paper does not discuss it. We did not discover the interaction, we
  noticed it in their supplement and asked what its architecture is.
- **MG423 being an RNase J paralog that may be inactive is published.** Chilamakuri et al. 2011,
  *Comparative and Functional Genomics* 2011:878973, one sentence: "It has been documented that presence
  of paralogs in Mycoplasma genitalium (MG139 and MG423) and Mycoplasma pneumoniae (MPN280 and MPN261)
  along with other bacteria could be as inactive forms." No structure, no interaction data, no complex.
  (That sentence also has a locus error: MPN_261 is DNA topoisomerase 1; the real MG423 ortholog is
  **MPN_621**.)
- **Closest methodological prior art:** *B. subtilis* RNase J1-J2 is a known heterocomplex (Mathy et al.
  2010) and was modelled from crosslinks + deep learning in 2024 (Stahl et al., *Nat. Commun.*, PDB-IHM
  9A5V). Our approach is the same idea applied to a different organism and an uncharacterized subunit.

**What is new here, stated narrowly:**
1. The **architecture**: a 2:2 dimer-of-heterodimers, with the far crosslinks explained only by the
   tetramer (the heterodimer leaves them at 51-63 A).
2. A **crosslink-validated 3D model** of it (6/6 links, two independent crosslinkers, 5/5 AF3 samples).
3. **Measured loss of all four catalytic residues** in MPN_621/MG423, making the "inactive paralog"
   suggestion concrete.
4. **MG423 stabilizes RNase J self-association** (RNase J : RNase J ipTM 0.50 alone vs 0.81 with MG423).
5. An **interface map** with human-selectivity numbers.
Not in Todor et al. 2026 (text and supplements checked), no homologous heterocomplex in the current PDB.

## Retracted during checking

- **"MG423 is membrane-anchored."** UniProt predicts two transmembrane helices (29-49, 80-100), but both
  align without insertion to MG139's catalytic core (41-61, 92-112), and AF3 folds the first as a
  beta-strand. This is a sequence-prediction artefact; the claim was dropped.

## Limitations

- Crosslinks are from *M. pneumoniae*, mapped to *M. genitalium* by orthology.
- The DSSO support needed a post hoc fix for corrupted sequences in the crosslink study's FASTA; the DSS
  result was pre-registered before the data were seen.
- The tetramer is template-based (3ZQ4, *B. subtilis* J1). One other template (8CGL) is ambiguous; four
  could not be tested (only two chains deposited).
- ~7 links in total; structure prediction and crosslinks are both indirect.

## How a lab could test it (cheapest first)

1. Co-purification: tagged MG139 (or MPN ortholog) pulls down MG423, and vice versa, from cell lysate.
2. Size-exclusion / mass photometry of the purified pair: ~250 kDa heterotetramer vs ~125 kDa heterodimer.
3. Disrupt the predicted tetramer interface (residues around MG139 225-257 / MG423 224) and check assembly
   state; disrupt the K120 region of the heterodimer interface and check co-purification.
4. Cryo-EM of the co-expressed complex.

## Other, weaker findings from the same search

- **MG241-MG242**, a heterodimer of two uncharacterized paralogs (Pfam MPN337 family): 4 in-cell links
  (3 DSSO + 1 DSS) all 12-16 A, but all from one MG241 lysine (K35); consistent, not decisive.
- **MG121 as the permease of the MG119 sugar ABC transporter**: 3/3 DSSO links ~15 A and a replicated DSS
  link; expected from gene neighbourhood.
