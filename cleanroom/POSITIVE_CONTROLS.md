# Positive controls for the RNase J (P75497) : MPN621 (P75174) interface screen

Literature and database survey, compiled 2026-09-25. Every factual claim below carries a
PMID / DOI / PDB ID / ChEMBL ID / URL. Where something is not established, it is stated
as not established rather than guessed.

Scope of the question: the Boltz-2 screen has a decoy null and a human CPSF3 (Q9UKF6)
off-target arm but no positive control, so a null result is currently uninterpretable.
This file lists experimentally validated small-molecule binders of MBL-beta-CASP-fold
nucleases and adjacent targets that can serve as a sensitivity gate.

---

## 1. Short summary of what actually exists

**CPSF73 / CPSF3 is the only MBL-beta-CASP nuclease with potent, structurally
characterised small-molecule ligands.** There are two independent chemical series with
human co-crystal structures:

- **The JTE-607 series.** JTE-607 (a Japan Tobacco anti-cytokine compound from the 1990s
  with a target unknown for ~20 years) is a **prodrug**. Cellular carboxylesterase 1
  (CES1) hydrolyses its ethyl ester to a free carboxylic acid, and that acid is the
  species that binds CPSF3. Target ID was published twice, independently, in 2019-2020:
  Kakegawa et al. by compound-immobilised affinity chromatography
  ([PMID 31399191](https://pubmed.ncbi.nlm.nih.gov/31399191/), Biochem Biophys Res Commun),
  and Ross et al. by phenotypic screening plus chemical genetics
  ([PMID 31819276](https://pubmed.ncbi.nlm.nih.gov/31819276/), Nat Chem Biol 2020;16:50-59,
  doi:10.1038/s41589-019-0424-1). Ross et al. deposited a 2.49 A co-crystal of the human
  CPSF3 catalytic segment with the compound under the Novartis code **NVP-LTM531**:
  **[PDB 6M8Q](https://www.rcsb.org/structure/6M8Q)**, ligand code **JBG**. The deposited
  JBG chemical component is
  `N-{3,5-dichloro-2-hydroxy-4-[2-(4-methylpiperazin-1-yl)ethoxy]benzene-1-carbonyl}-L-phenylalanine`,
  which is exactly the de-esterified (free acid) form of JTE-607 (compare JTE-607,
  PubChem CID 9938545, the ethyl ester of the same acid). So 6M8Q is, structurally, the
  JTE-607 active metabolite bound to human CPSF73.

- **The benzoxaborole series.** Tao et al. 2024 (Nijhawan / Tong / De Brabander labs),
  *Anticancer benzoxaboroles block pre-mRNA processing by directly inhibiting CPSF3*,
  Cell Chem Biol 2024;31(1):139-149.e14, doi:10.1016/j.chembiol.2023.10.019,
  [PMID 37967558](https://pubmed.ncbi.nlm.nih.gov/37967558/), PMC10841686. Two 1.7 A and
  2.2 A co-crystals of human CPSF3 residues 1-460 with novel benzoxaboroles:
  **[8T1Q](https://www.rcsb.org/structure/8T1Q)** (ligand **XYX**) and
  **[8T1R](https://www.rcsb.org/structure/8T1R)** (ligand **XZC**). Direct binding was
  shown by photoaffinity labelling with a diazirine/alkyne probe plus probe-displacement
  competition, not only by enzyme inhibition. Critically, the paper reports that the
  benzoxaborole boron is **hydrated and all three boron oxygens coordinate the active-site
  metals**, whereas **the JTE-607 active form does not coordinate the metals**. Two
  distinct recognition modes in the same pocket.

**The antiparasitic benzoxaborole CPSF3 story is real but is genetic, not biophysical.**
AN3661 (Plasmodium, Toxoplasma), acoziborole / SCYX-7158 (Trypanosoma), AN7973 and
AN11736 (veterinary trypanosomiasis, Cryptosporidium) are all assigned to CPSF3 by
resistance-mutation selection, CRISPR knock-in, overexpression-mediated resistance, and
docking. **No purified-CPSF3 binding measurement and no co-crystal structure exists for
any of them, in any organism.** There is no experimental structure of a parasite CPSF3 at
all, benzoxaborole-bound or otherwise.

**Other MBL-beta-CASP nucleases with genuine ligand co-crystals: SNM1A (DCLRE1A) and
Artemis (SNM1C / DCLRE1C).** The Schofield / Newman group at Oxford ran a real HTS
campaign against SNM1A and delivered a structure-guided series of quinazoline-hydroxamic
acids with sub-10 uM turnover IC50s and multiple co-crystals (Chem Sci 2024;15:8227-8241,
doi:10.1039/d4sc00367e, [PMID 38817593](https://pubmed.ncbi.nlm.nih.gov/38817593/)). For
Artemis there is a ceftriaxone co-crystal (NAR 2021;49:9310-9326,
doi:10.1093/nar/gkab693, [PMID 34387696](https://pubmed.ncbi.nlm.nih.gov/34387696/)).
These are the best-characterised MBL-beta-CASP ligand complexes after CPSF73, and unlike
CPSF73 they are *nucleases the compounds were designed against*, so the potency numbers
are on purified enzyme.

**Bacterial RNase J: essentially nothing. Confirmed negative.** See section 5.

**Small molecules bound at a protein-protein interface of a nuclease: two documented
precedents, one of them in this exact fold family.** IP6 sits at the INTS4-INTS9-INTS11
interface of the Integrator cleavage module, 55 A from the INTS11 active site
([PDB 7SN8](https://www.rcsb.org/structure/7SN8)); and an X-ray fragment screen on the
SARS-CoV-2 nsp10-nsp14 ExoN heterodimer found five sites including interface sites
(PDB 9FWH-9FWT). Details in section 6.

---

## 2. Candidate positive-control compound table

SMILES marked "(PDB)" are transcribed verbatim from the RCSB chemical-component
dictionary, i.e. they describe the ligand **as modelled in the deposited structure**
(for benzoxaboroles that is the anionic tetrahedral boronate, `[B-](O)(O)`, not the
neutral cyclic boronic ester). Regenerate the neutral form from the IUPAC name before
using as a docking input if your pipeline needs it.

| # | Name | ChEMBL ID | SMILES | Target shown to bind | Potency (assay) | Direct binding? | PDB | Citation |
|---|------|-----------|--------|----------------------|-----------------|-----------------|-----|----------|
| 1 | **JTE-607 active metabolite** (free acid; deposited as **NVP-LTM531**; PDB ligand **JBG**; PubChem CID 58647174) | none (not in ChEMBL) | `CN1CCN(CC1)CCOc2c(cc(c(c2Cl)O)C(=O)N[C@@H](Cc3ccccc3)C(=O)O)Cl` (PDB) | Human CPSF3 / CPSF73 (Q9UKF6) | **Kd = 370 nM** to human CPSF3 (reported in Ross et al. 2020; see caveat in section 7) | **YES** (Kd reported; affinity-chromatography pulldown in Kakegawa; co-crystal) | **6M8Q** (2.49 A, Zn) | Ross et al., Nat Chem Biol 2020;16:50-59, doi:10.1038/s41589-019-0424-1, PMID 31819276; Kakegawa et al., PMID 31399191 |
| 2 | **JTE-607** (parent prodrug, ethyl ester; free base PubChem CID 9938545; 2HCl salt CID 9938544, CAS 188791-09-5) | **CHEMBL4303719** (unnamed in ChEMBL; matched by InChIKey `IPSSXIMJJXSJQB-FQEVSTJZSA-N` via UniChem) | `CCOC(=O)[C@H](Cc1ccccc1)NC(=O)c1cc(Cl)c(OCCN2CCN(C)CC2)c(Cl)c1O` | **Not a direct CPSF3 binder.** Requires CES1 hydrolysis | Cytokine release IC50 5.9-11 nM in LPS-stimulated human PBMC (cellular, downstream) | **NO** for the parent ester | none | Ross et al. 2020, PMID 31819276; Kakegawa et al., PMID 31399191 |
| 3 | **Tao compound 1**: N-(4'-acetyl-1,1'-biphenyl-3-yl)-3-(1-hydroxy-1,3-dihydrobenzo[c][1,2]oxaborol-7-yl)propanamide (PDB ligand **XYX**) | none | `[B-]1(c2c(cccc2CCC(=O)Nc3cccc(c3)c4ccc(cc4)C(=O)C)CO1)(O)O` (PDB) | Human CPSF3 | Cellular IC50 **0.858 uM** (HeLa); 96% inhibition of histone pre-mRNA cleavage at 0.2 mM in mouse nuclear extract | **YES** (photoaffinity crosslink + probe displacement + co-crystal) | **8T1Q** (1.70 A, **Fe**) | Tao et al., Cell Chem Biol 2024;31:139-149.e14, doi:10.1016/j.chembiol.2023.10.019, PMID 37967558 |
| 4 | **Tao compound 2**: 3-(1-hydroxy-1,3-dihydrobenzo[c][1,2]oxaborol-7-yl)-N-(3'-methoxy-[1,1'-biphenyl]-3-yl)propanamide (PDB ligand **XZC**) | none | `[B-]1(c2c(cccc2CCC(=O)Nc3cccc(c3)c4cccc(c4)OC)CO1)(O)O` (PDB) | Human CPSF3 | Cellular IC50 **1.05 uM** (HeLa) | **YES** (same evidence chain as #3) | **8T1R** (2.20 A, **Fe**) | Tao et al. 2024, PMID 37967558 |
| 5 | **AN3661** (CAS 1268335-33-6; PubChem CID 50898347) | **CHEMBL1643740** | `B1(C2=C(CO1)C=CC=C2CCC(=O)O)O` (PubChem) | *P. falciparum* CPSF3 (**inferred**); *T. gondii* CPSF3 (**inferred**) | *Pf* IC50 **32 nM** (mean, 3D7/W2/Dd2/K1/HB3, [3H]-hypoxanthine); **64 nM** ex vivo Ugandan isolates; *Tg* IC50 **0.9 uM** (HFF); human cytotox CC50 60.5 uM (Jurkat), >100 uM (HeLa, HCT-116, MDA-MB-231, SK-OV-3, WI-38) | **NO.** Target from resistance mutations in *pfcpsf3* + CRISPR-Cas9 knock-in + homology-model docking only. No purified-enzyme assay, no structure | none | Sonoiki et al., Nat Commun 2017;8:14574, doi:10.1038/ncomms14574, PMID 28262680; Palencia et al., EMBO Mol Med 2017;9:385-394, doi:10.15252/emmm.201607370, PMID 28148555 |
| 6 | **Acoziborole / SCYX-7158 / AN5568** (CAS 1266084-51-8) | **CHEMBL2347704** | `CC1(C)OB(O)c2cc(NC(=O)c3ccc(F)cc3C(F)(F)F)ccc21` (ChEMBL) | *T. brucei* CPSF3 (**inferred**) | EC50 **0.38 uM** *T. brucei* bloodstream form; shifts to 2.19 uM on CPSF3-GFP overexpression; N232H CRISPR edit gives 5.1-fold resistance; N232H/Y383F/N448Q triple mutant >40-fold | **NO.** Gain-of-function overexpression screen, RNAi essentiality, CRISPR editing, docking. No purified-CPSF3 assay, no structure | none | Wall et al., PNAS 2018;115:9616-9621, doi:10.1073/pnas.1807915115, PMID 30185555; resistance mapping PLOS Pathog 2025, PMID 41774758 |
| 7 | **AN7973** (6-carboxamide benzoxaborole) | not retrieved | not retrieved (MCE catalogue item) | *T. brucei* / *C. parvum* CPSF3 (**inferred, and see dispute note**) | Trypanocidal and anti-*Cryptosporidium* activity; disrupts mRNA processing | **NO** | none | PLOS Pathog 2018;14:e1007315 (PMC6173450; PMID not verified in this survey); mechanism complication: Giordani et al., PLOS Pathog 2020;16:e1008932, doi:10.1371/journal.ppat.1008932, PMID 33079941 |
| 8 | **SNM1A inhibitor, quinazoline-hydroxamic acid** (PDB ligand **U2O**, deposited as "compound 21") | none | `C[C@H](Cc1c2cc(ccc2nc(n1)NCC=C)Cl)C(=O)NO` (PDB) | Human **SNM1A / DCLRE1A** (MBL-beta-CASP) | Series best-in-class IC50 **0.8 uM**; other series members 2-3 uM (fluorescence turnover on 20-nt FITC/BHQ-1 ssDNA; gel-based confirmation on 3'-labelled 51-mer) | **YES** (co-crystal; hydroxamate displaces the hydrolytic water and chelates both metals) | **8C8S** (1.80 A, Zn) | Bielinski, Henderson, Yosaatmadja et al., Chem Sci 2024;15:8227-8241, doi:10.1039/d4sc00367e, PMID 38817593 |
| 9 | **SNM1A inhibitor, quinazoline-hydroxamic acid** (PDB ligand **U2C**, "compound 44") | none | `C[C@H](Cc1c2cc(ccc2nc(n1)NCc3ccco3)Cl)C(=O)NO` (PDB) | Human SNM1A / DCLRE1A | same series, low-uM | **YES** (co-crystal) | **8C8D** (1.46 A, Zn) | Chem Sci 2024, PMID 38817593 |
| 10 | **SNM1A inhibitor, quinazoline-2-carboxamide hydroxamate** (PDB ligand **U1L**, "compound 48") | none | `C[C@@H](C(=O)NO)Nc1c2ccccc2nc(n1)C(=O)NCC=C` (PDB) | Human SNM1A / DCLRE1A | same series, low-uM | **YES** (co-crystal) | **8C8B** (1.46 A, Zn) | Chem Sci 2024, PMID 38817593 |
| 11 | **SNM1A N-hydroxyimide "H1"** (PDB ligand **UFI**; 6-methoxy-2-hydroxy-benzo[de]isoquinoline-1,3-dione) | none | `COc1ccc2c3c1cccc3C(=O)N(C2=O)O` (PDB) | Human SNM1A / DCLRE1A | HTS hit class, IC50 ~2.0-2.9 uM (fluorescence turnover) | **YES** (co-crystal; oxygens ligate the metal(s)) | **8CEW** (1.53 A, Zn + Ni) | Chem Sci 2024, PMID 38817593 |
| 12 | **SNM1A quinoxalinedione "H2"** (PDB ligand **UF3**; 9-chloro-1,4-dihydropyrazino[2,3-c]quinoline-2,3-dione) | none | `c1cc2c(cc1Cl)c3c(cn2)NC(=O)C(=O)N3` (PDB) | Human SNM1A / DCLRE1A | HTS hit class, low-uM | **YES** (co-crystal) | **8CF0** (1.76 A, Ni) | Chem Sci 2024, PMID 38817593 |
| 13 | **Ceftriaxone** (cephalosporin; PDB ligand **9F2**) | CHEMBL161 (ceftriaxone) | `CN1C(=NC(=O)C(=O)N1)SCC2=C(N3C([C@@H](C3=O)NC(=O)C(=NOC)c4csc(n4)N)SC2)C(=O)O` (PDB) | Human **Artemis / SNM1C / DCLRE1C**; also inhibits SNM1A and SNM1B | Artemis IC50 **65 uM** (fluorescence nuclease assay); SNM1A IC50 **12.2 mM** (very weak) | **YES for Artemis** (co-crystal) | **7APV** (1.95 A) | Yosaatmadja et al., NAR 2021;49:9310-9326, doi:10.1093/nar/gkab693, PMID 34387696; cephalosporin/SNM1 series: Chem Commun 2016;52:6727, PMC5063058 |
| 14 | **Inositol hexakisphosphate (IP6 / phytic acid)** (PDB ligand **IHP**) | CHEMBL1235461 (phytic acid) | `C1(C(C(C(C(C1OP(=O)(O)O)OP(=O)(O)O)OP(=O)(O)O)OP(=O)(O)O)OP(=O)(O)O)OP(=O)(O)O` (PDB) | **INTS4-INTS9-INTS11 Integrator cleavage module** (INTS11 is the CPSF73 paralogue, MBL-beta-CASP) | Not a potency measurement. Structurally ordered, functionally required: mutation of the pocket or disruption of IP6 biosynthesis reduces snRNA 3'-end processing and transcription attenuation | **YES, and at a protein-protein INTERFACE**, 55 A from the INTS11 active site, contacting all three subunits (INTS4 K189; INTS9 R2/R504/K508/R509; INTS11 K462) | **7SN8** (2.74 A cryo-EM, *Drosophila*); same site confirmed in human ICM | Lin, Jia et al., Nat Commun 2022;13:5742, doi:10.1038/s41467-022-33506-3, PMID 36180473 |
| 15 | **nsp10-nsp14 ExoN fragment hits** (e.g. VT00019, VT00180, VT00259) | none | not retrieved (XChem/Vitas-M fragment codes; ligand codes are in the individual PDB entries) | **SARS-CoV-2 nsp14 3'-5' exoribonuclease : nsp10 heterodimer** (a ribonuclease, but **not** MBL fold) | Affinities measured by microscale thermophoresis (fragment-range); nine related hits at one site | **YES, and at/near the nsp10-nsp14 interface**; five novel fragment sites total, explicitly assessed for PPI disruption potential | **9FWH, 9FWI, 9FWJ, 9FWK, 9FWL, 9FWM, 9FWN, 9FWO, 9FWP, 9FWQ, 9FWR, 9FWS, 9FWT** | Kozielski, Fisher, Ma et al., NAR 2025;53(14):gkaf753, doi:10.1093/nar/gkaf753, PMID 40794865 |
| 16 | **UMP** (uridine 5'-monophosphate) | CHEMBL231685 | `O[C@@H]1[C@H](O)[C@@H](COP(O)(O)=O)O[C@H]1N1C=CC(=O)NC1=O` | **RNase J** (*Thermus thermophilus*), soaked into the 5'-monophosphate sensing pocket | Substrate-fragment complex. No potency. Not an inhibitor | Structural only | **3BK2**, **4XWT** | Li de la Sierra-Gallay et al. (3BK1/3BK2); Dorleans et al./Zhao et al. (4XWT/4XWW) |

---

## 3. Which MBL-beta-CASP family members have a ligand-bound structure at all

Systematic RCSB check, done by full-text and entity queries:

| Family member | Small-molecule co-structure? | Entries |
|---|---|---|
| **CPSF73 / CPSF3** | **Yes, 3** | 6M8Q (JBG, JTE-607 acid / NVP-LTM531); 8T1Q (XYX); 8T1R (XZC). Apo/other: 2I7T, 2I7V, 6V4X (histone cleavage complex, Zn only), 8B7T, 8BA1, 9NGO/9NB1/9NH5/9NH6/9N96 (U7 snRNP cryo-EM, Zn only) |
| **SNM1A / DCLRE1A** | **Yes, 6+** | 8C8B, 8C8D, 8C8S, 8CEW, 8CF0, 8CG9 (ligands U1L, U2C, U2O, UFI, UF3, R3Z/XOB). Plus a large 5Q1x/5Q2x crystallographic fragment-screen series (318 DCLRE1A entries in total by text search) |
| **Artemis / SNM1C / DCLRE1C** | **Yes, 1** | 7APV (ceftriaxone, 9F2). Apo/variants: 6TT5, 7AF1, 7AFS, 7AFU, 7AGI; DNA complex 7ABS |
| **SNM1B / Apollo / DCLRE1B** | Not found in this survey | Cephalosporin inhibition reported biochemically (Chem Commun 2016, PMC5063058) but no ligand co-crystal located |
| **INTS11** | **Interface ligand only** | 7SN8 (IP6 at the INTS4/9/11 interface). No active-site inhibitor. 8UIB/8UIC (INTS9-INTS11-BRAT1) carry Zn only |
| **ELAC2 / RNase Z** | **No** | Recent structures are tRNA/complex only, e.g. 8RR4 (ELAC2-D550N + TRMT10C + SDR5C1 + pre-tRNA-Tyr; EMBO J 2024, doi:10.1038/s44318-024-00297-w, PMID 39516281). No small-molecule inhibitor located in the literature |
| **RNase J (bacterial/archaeal)** | **No. Zero.** | All 27 RNase J entries carry only metals (Zn/Mn/Ca), UMP, or RNA: 9A5V, 8YYF-8YYK (*S. epidermidis*/RNase J2 variants), 8CGL and 7PCR (*H. pylori*), 7WNT/7WNU (*M. tuberculosis*), 6K6S/6K6W (*S. epidermidis* J1/J2), 3ZQ4 (*B. subtilis*-type degradosome), 5A0T/5A0V, 4XWT/4XWW, 3T3N/3T3O, 3BK1/3BK2, 5HAA/5HAB/5WS2/6LLB (archaeal), 2AZ4 |

---

## 4. Human CPSF3 as the off-target arm: a correction worth making

The off-target arm as currently framed assumes human CPSF3 is the thing you do *not*
want to hit. That is the right selectivity goal, but note that **human CPSF3 is a
genuinely ligandable, potently drugged protein**: Kd 370 nM for the JTE-607 acid and
low-micromolar cellular potency for the benzoxaboroles, with three co-crystals. So a hit
scoring well against human CPSF3 in the screen is not automatically evidence of an
artifact; it may be a real ligand of a real pocket. This cuts both ways and it is also
exactly why human CPSF3 is the best available positive-control protein in the whole
survey.

Two practical setup facts from 8T1Q/8T1R that affect co-folding and scoring:

- The crystallised construct is **human CPSF3 residues 1-460** (the catalytic segment).
- The metals in 8T1Q/8T1R are modelled as **Fe**, not Zn. Tao et al. state the site is
  "predominantly iron when CPSF3 is expressed in bacteria and insect cells, but more
  zinc is incorporated when it is expressed in human cells." 6M8Q has Zn. If your
  pipeline assigns metal identity, that inconsistency is real and documented, not a
  deposition error.
- **Isolated recombinant CPSF73 is only weakly and non-specifically active.** Tao et al.
  ran their cleavage assays in mouse nuclear extract, not on purified protein. Symplekin
  NTD and the U7/HDE duplex are needed to open the catalytic site (EMBO Rep 2008,
  doi:10.1038/embor.2008.146; RNA 2020;26:1345). Consequence: a purified-protein
  wet-lab validation of any screen hit against CPSF73 alone is harder than it looks.

---

## 5. Priority item 3: inhibitors of bacterial RNase J. Confirmed negative.

**Conclusion: there are no published small-molecule inhibitors of bacterial RNase J from
any organism (B. subtilis J1/J2, S. aureus, S. epidermidis, M. tuberculosis, H. pylori,
Mycoplasma, Streptococcus).** Not one compound with a name, a potency, and an assay.

How hard I looked:

1. Structural: exhaustive RCSB check of all 27 RNase J entries (section 3). Zero
   drug-like ligands. The only non-metal, non-RNA ligand in the entire family is UMP,
   soaked into the 5'-phosphate sensing pocket (3BK2, 4XWT).
2. Targeted literature searches combining "RNase J" with inhibitor / small molecule /
   high-throughput screen / antibacterial / drug target, and with each of *Bacillus
   subtilis*, *Staphylococcus aureus*, *Mycoplasma*, *Helicobacter*, *Streptococcus*,
   *Mycobacterium tuberculosis*, across 2024-2026.
3. What actually comes back instead, and why it is not what you need:
   - **RnpA (RNase P protein) inhibitors in *S. aureus***: RNPA2000 and derivatives,
     originally reported to inhibit mRNA turnover and tRNA processing (PLOS Pathog
     2011;7:e1001287; AAC 2015, doi:10.1128/aac.04352-14; Antibiotics 2019;8:48). These
     came from screens against the *S. aureus* degradosome-like complex that also contains
     RNase J1/J2, so they are the nearest neighbour in the literature. **Mechanism
     disputed.** Schmitz et al., *RNase P Inhibitors Identified as Aggregators*, AAC 2021,
     doi:10.1128/aac.00300-21, [PMID 33972249](https://pubmed.ncbi.nlm.nih.gov/33972249/),
     showed by microscopy, HPLC solubility, co-pulldown, detergent rescue and enzyme
     titration that **RNPA2000, iriginol hexaacetate and purpurin act by forming insoluble
     RnpA aggregates**, i.e. they are colloidal aggregators, not specific inhibitors. Do
     not use any of these as a positive control.
   - **RNase II / PNPase / RNase R inhibitors in *E. coli***: SEW04027, HTS05225,
     HTS06218, HTS08348, HTS08350 (RNase II) and CD06144, SPB04215, SPB04462 (PNPase),
     from in-silico screening with gel-based and cell-viability validation. Matos,
     Simmons, Fishwick, McDowall, Arraiano, Int J Mol Sci 2024;25:8048,
     doi:10.3390/ijms25158048, PMID 39125622. **RNase J was explicitly not a target of
     that study**, no IC50 values were reported (qualitative gel + viability only), and
     RNase II is an RNB-family enzyme, not MBL fold. Not usable as a fold-level control.
   - **RNase E inhibitors** (Sci Rep 2015;5:8028; Kime et al. 2020, PMC7284133). Different
     fold, different family.
   - **M. tuberculosis RNase J** is argued to be an attractive target (structures 7WNT /
     7WNU, and a 2024 perspective piece, PMC11060219), but this is target-validation
     advocacy. No inhibitor is reported.

So: your suspicion was right, and it is a strong negative, not an absence of searching.
The practical consequence is that **no positive control specific to RNase J exists**,
and any gate you build must be a fold-level or family-level surrogate.

---

## 6. Priority item 4: small molecules at a protein-protein interface of a ribonuclease or MBL-fold enzyme

This is the item that matters most for your screen, because the screen steers ligands to
the interface rather than the catalytic site. Two documented precedents:

### 6a. IP6 at the Integrator cleavage module interface. Same fold family as your target.

PDB **7SN8**, 2.74 A cryo-EM, *Drosophila* INTS4-INTS9-INTS11. INTS11 is the direct
CPSF73 paralogue and an MBL-beta-CASP endonuclease; INTS9 is its catalytically dead
paralogue partner (the INTS9-INTS11 pair is architecturally analogous to
CPSF73-CPSF100). IP6 is ordered in a highly electropositive pocket **at the interface
among all three subunits**, contacting INTS4 Lys189, INTS9 Arg2/Arg504/Lys508/Arg509 and
INTS11 Lys462, and it sits **55 A from the INTS11 active site**. The same site was
confirmed in the human ICM. Functional validation: pocket mutations and disruption of IP6
biosynthesis both reduce Integrator function in snRNA 3'-end processing and mRNA
transcription attenuation. Nat Commun 2022;13:5742, doi:10.1038/s41467-022-33506-3,
PMID 36180473.

This is, as far as this survey found, **the only published case of a small molecule bound
at a protein-protein interface in an MBL-beta-CASP nuclease complex.**

Caveat that limits its value as a gate: IP6 is a hexa-anionic natural metabolite binding
a strongly electropositive pocket. That is the easiest possible case for any scoring
function that has any electrostatic term at all. Recovering IP6 proves very little about
whether the method can find a neutral, drug-like ligand at a flatter interface.

### 6b. Fragment hits at the nsp10-nsp14 ExoN interface. A ribonuclease, but not MBL fold.

Kozielski et al., NAR 2025;53(14):gkaf753, doi:10.1093/nar/gkaf753, PMID 40794865. X-ray
fragment screening on the SARS-CoV-2 nsp14 3'-5' exoribonuclease in complex with its
obligate activator nsp10 identified **five novel fragment binding sites, including sites
in the nsp10-nsp14 interface**, with nine structurally related hits clustering at one
site and affinities measured by microscale thermophoresis. The authors explicitly frame
these as starting points for **protein-protein interaction inhibitors** of the nuclease
/ cofactor pair. Deposited entries include 9FWH (VT00019), 9FWM (VT00180) and 9FWT
(VT00259), through 9FWH-9FWT.

This is the closest published analogue to what your screen is trying to do: a
small-molecule-at-the-interface campaign on a nuclease that only works when bound to a
partner protein. nsp14 is a DEDDh exonuclease, so it is a functional analogue
(nuclease + essential partner), not a fold analogue.

### 6c. What is not there

No small molecule has been reported at the **CPSF73-CPSF100-symplekin** interface
(the CTD heterodimer structures 8B7T and 8BA1 are ligand-free; the histone cleavage
complex 6V4X carries only Zn), nor at the **INTS9-INTS11** interface itself, nor at any
**RNase J dimer** interface, nor at a metallo-beta-lactamase (NDM-1 / VIM / IMP / L1)
oligomerisation interface. MBL inhibitor chemistry (captopril, taniborbactam/VNRX-5133
in 6RMF and 6TD1, xeruborbactam/QPX7728) is entirely active-site, zinc-directed
chemistry. Toxin-antitoxin PPI disruptors exist for MazEF (Antibiotics 2024;13:398,
doi:10.3390/antibiotics13050398) but MazF is a ribbon-helix-helix family RNase, the
compounds came from docking, and the reported validation is cell killing by flow
cytometry, not structure or affinity. Not a usable gate.

---

## 7. What is NOT established

These are the gaps I could not close. Treat each as an open item, not as a fact.

1. **The assay behind "Kd = 370 nM" for the JTE-607 metabolite against human CPSF3.**
   The number is attributed to Ross et al. 2020 and is repeated consistently across
   supplier datasheets (Tocris/Bio-Techne 5185) and downstream reviews. The Nat Chem Biol
   full text is paywalled and I could not read the methods, so **whether that Kd came from
   SPR, ITC, MST or a competition assay is unverified here**, as is the exact protein
   construct used. It is the single most load-bearing number in this file. Verify from the
   PDF before quoting it in anything external.
2. **Whether "NVP-LTM531" is literally the JTE-607 CES1 metabolite or a Novartis
   re-synthesis of the same acid.** The identity argument here is structural and it is
   solid (PDB component JBG is the exact de-esterified JTE-607 acid, L-Phe / (2S)
   stereochemistry, C23H27Cl2N3O5, InChIKey `XEBIFCYTYHBFTB-SFHVURJKSA-N`, PubChem CID
   58647174), but Novartis's own naming intent is not stated in any source I could read.
3. **No IC50 for the JTE-607 metabolite on purified CPSF73.** All published potencies are
   either cellular or nuclear-extract based. Liu et al., Nat Struct Mol Biol
   2023;30:1947-1957, doi:10.1038/s41594-023-01161-x, PMID 38087090, PMC11663416, report
   nuclear-extract cleavage IC50s that span **0.8 uM (L3 PAS) to >100 uM (SVL PAS)** for
   the same compound depending purely on the RNA sequence flanking the cleavage site.
   That 100-fold sequence dependence means "the IC50 of Compound 2" is not a single number.
4. **ChEMBL is essentially empty for CPSF3.** Human CPSF3 is CHEMBL5724779 and carries
   **6 activities total**, all from a single 2011 chemoproteomics paper, all fold-change
   or `IC50 > 10000 nM`. *T. brucei equiperdum* CPSF is CHEMBL4665581 with **0 activities**.
   Do not expect to mine a CPSF3 actives set out of ChEMBL. The JTE-607 acid is not in
   ChEMBL at all; Tao compounds 1 and 2 are not in ChEMBL; AN3661 (CHEMBL1643740) has 24
   activities but **every one is a whole-cell or whole-animal readout**, none against
   CPSF3 as a target.
5. **No direct binding measurement exists for any antiparasitic benzoxaborole against any
   CPSF3.** AN3661, acoziborole, AN7973 and AN11736 are all genetics-plus-docking
   assignments. If the screen is meant to be gated on "this compound demonstrably binds
   this protein", none of them qualifies.
6. **No experimental structure of any parasite CPSF3.** Palencia et al. used an I-TASSER
   homology model (templates 3AF5, 2I7V, 3A4Y, 3IEM, 5A0T); the acoziborole work used a
   3IEM-based model. If you need a parasite CPSF3 receptor you will be predicting it.
7. **No inhibitor of ELAC2 / RNase Z.** Searched; nothing found.
8. **No active-site inhibitor of INTS11.** Only the IP6 interface ligand.
9. **No SNM1B / Apollo ligand co-crystal** located, despite biochemical cephalosporin
   inhibition being reported.
10. **Exact compound-number to PDB-ID mapping in the SNM1A paper.** The Chem Sci 2024
    deposition titles name "compound 21 / 44 / 48" and "H1 / H2", and the paper's own text
    numbers its best compounds 13, 19, 20. I have reported the PDB-authoritative
    ligand/entry pairing and the paper-reported IC50 range (0.8 uM best, 2-3 uM for the
    N-hydroxyimide hits, 44 uM down to ~8 uM gel-based for compound 19), but I did not
    verify which paper-numbered compound corresponds to which deposited ligand code.
    Resolve from the paper's SI before using a specific number/structure pair.
11. **Commercial pricing for most items** (section 8). Several vendors serve prices via
    JavaScript or block automated fetch, so some entries are catalogue-number-only.
12. **MPN621 (P75174) is annotated in UniProt as "Uncharacterized protein MG423
    homolog", 561 aa, with no function, no subunit/interaction annotation, no family
    assignment and no PDB entries.** *M. pneumoniae* RNase J (P75497, MPN_280, 569 aa,
    *rnj*) is annotated as a homodimer and possible degradosome subunit, also with **no
    PDB entries**. So the receptor for this screen is a prediction on both chains, and the
    interface itself is not experimentally determined in any deposited structure.

### Mechanism disputes and retraction-adjacent flags

- **RNPA2000, iriginol hexaacetate, purpurin: mechanism refuted.** Shown to be RnpA
  aggregators, not specific RNase P inhibitors. AAC 2021, doi:10.1128/aac.00300-21,
  PMID 33972249. **Excluded** from all recommendations below.
- **AN7973 / AN11736: mechanism complicated.** Giordani et al. showed these veterinary
  benzoxaboroles are **peptidase-activated prodrugs**; trypanosomal serine
  carboxypeptidases cleave AN11736 to the carboxylate AN14667, and the resulting
  accumulation gradient, not differential CPSF3 engagement, explains AN11736's
  sub-nanomolar potency. PLOS Pathog 2020;16:e1008932, doi:10.1371/journal.ppat.1008932,
  PMID 33079941. CPSF3 remains the proposed target but the potency numbers do not report
  target engagement.
- **JTE-607 itself is a prodrug** and the parent ester is not the CPSF3 binder. Screening
  the parent will look like a negative result for reasons that have nothing to do with
  your scoring function.
- **Ebselen (8.5 uM), disulfiram (10.8 uM) and auranofin (46 uM) vs Artemis**
  (NAR 2021, PMID 34387696) are all thiol-reactive / metal-scavenging frequent hitters
  with no co-crystal in that paper. Do **not** use them as positive controls; they are
  better used as *negative* controls for a scoring function that should not be able to
  rationalise them.

---

## 8. Commercial availability and rough cost

Prices retrieved 2026-09-25 where a vendor served them statically; otherwise catalogue
number only. Treat as indicative, not as quotes.

| Compound | Vendor / catalogue | Pack sizes and price | Notes |
|---|---|---|---|
| **JTE-607 dihydrochloride** | MedKoo 11800 | 5 mg $90 / 10 mg $150 / 25 mg $250 / 50 mg $450 / 100 mg $750 / 200 mg $1,350, all in stock | Also Selleck E0314 (in stock, 99.17% purity), MedChemExpress (HY-13610 family; MCE flags territory restrictions), Cayman (5/10/25/50 mg), Tocris 5185, AdooQ, Focus Biomolecules, Probechem. **Cheap and easy.** Remember it is the prodrug |
| **JTE-607 active metabolite (free acid / NVP-LTM531)** | Not found as a catalogue item | n/a | **Not commercially available.** Would need custom synthesis (one-step ester hydrolysis of JTE-607) or in-situ CES1 treatment. This is the compound with the Kd, so this matters |
| **Acoziborole (SCYX-7158)** | MedKoo 10814 | 50 mg $450 / 100 mg $750 / 200 mg $1,250 / 1 g $3,650, ~2-week lead time | Recently approved (Drugs 2026, doi:10.1007/s40265-026-02358-2). Available |
| **AN3661** | MedChemExpress HY-128204; TargetMol T36649 (1 mg listed) | Price not publicly displayed | CAS 1268335-33-6. In catalogue at both vendors; quote needed |
| **AN7973** | MedChemExpress (AN7973 product page, "Parasite Inhibitor") | Price not publicly displayed | Available for research use |
| **Tao compounds 1 and 2 (CPSF3 benzoxaboroles)** | None | n/a | **Not commercial.** Custom synthesis; routes are in the Cell Chem Biol 2024 SI |
| **SNM1A quinazoline-hydroxamic acids (U2O / U2C / U1L)** | None | n/a | **Not commercial.** Bespoke Oxford compounds; synthesis in the Chem Sci 2024 SI |
| **Ceftriaxone** | Every major supplier; also a generic injectable drug | < $50 for grams | Trivially available and cheap |
| **Ebselen, disulfiram, auranofin** | Cayman, MCE, Selleck, Sigma | tens of dollars per 10-50 mg | Cheap, but see the frequent-hitter flag above |
| **Phytic acid / IP6 (sodium salt)** | Sigma-Aldrich, TCI, Cayman | a few tens of dollars per gram | Trivially available |
| **UMP (uridine 5'-monophosphate)** | Sigma, TCI | tens of dollars per gram | Trivially available |
| **Taniborbactam / xeruborbactam** (fold-level MBL controls, not beta-CASP) | MCE, TargetMol | quote | Only relevant if you want a non-nuclease MBL-fold rung |

**Cost-of-goods conclusion:** an entirely purchasable wet-lab follow-up arm exists
(JTE-607, acoziborole, AN3661, AN7973, ceftriaxone, IP6) for well under $1,000. The two
best-validated compounds for the purposes of a *computational* gate (the JTE-607 free acid
and the Tao benzoxaboroles) are not purchasable, which does not matter for an in-silico
gate since you only need the SMILES, but does matter if the gate ever needs wet-lab
confirmation.

---

## 9. Recommended gate

The screen cannot be gated against RNase J, because nothing is known to bind RNase J.
Any gate is therefore a **surrogate**, and the honest framing is: this gate measures
whether the method can recover known ligands of homologous folds under the same
protocol. Build it as two tiers, because they license two different claims.

### Tier A: fold-level active-site sensitivity (5 compounds, 2 proteins)

Purpose: does Boltz-2 + your scoring pipeline recover known, co-crystallised ligands of
an MBL-beta-CASP nuclease at all? If Tier A fails, a null on RNase J means nothing.

| Compound | Run against | Why this rung |
|---|---|---|
| **JTE-607 free acid** (PDB ligand JBG) | **Human CPSF73/CPSF3 catalytic segment, residues 1-460**; receptor from **6M8Q** (Zn) | The strongest single control in the whole survey: a reported sub-micromolar Kd plus a 2.49 A co-crystal. **Boron-free**, so it will not trip any boron-support problem in the ligand featuriser. It also **does not coordinate the metals**, so it tests genuine pocket recognition rather than metal chelation |
| **Tao compound 1** (XYX) | Same receptor; co-crystal **8T1Q** (note: **Fe**, 1.70 A) | Independent chemotype, independent lab, direct-binding evidence by photoaffinity labelling |
| **Tao compound 2** (XZC) | Same receptor; co-crystal **8T1R** (Fe, 2.20 A) | Near-analogue of compound 1, so it doubles as a mild selectivity/SAR probe (0.86 vs 1.05 uM cellular) |
| **SNM1A hydroxamate U2O** (and optionally U2C, U1L) | **Human SNM1A / DCLRE1A**, receptor from **8C8S** (Zn, 1.80 A) | A *second* MBL-beta-CASP protein, with potencies measured on **purified enzyme** (0.8-3 uM) rather than in extract. Gives the gate a second, independent fold data point |
| **Ceftriaxone** (9F2) | **Human Artemis / SNM1C / DCLRE1C**, receptor from **7APV** (1.95 A) | Deliberately the **weak rung**: a real co-crystal at only 65 uM. Useful for calibrating where your score stops being able to tell a true weak binder from noise |

Pass criterion to state in advance: all five should score above the 95th percentile of
your existing decoy null when run against their *own* cognate receptor. Publish that
threshold before running, not after.

### Tier B: interface-mode sensitivity (the rung that actually matters, 2 systems)

Purpose: Tier A only licenses "the method finds active-site ligands." Your screen steers
to an interface. This tier is the only thing that licenses an interface claim, and it is
thin, which is itself the finding.

| Compound | Run against | Why |
|---|---|---|
| **IP6 / inositol hexakisphosphate** (IHP) | **INTS4-INTS9-INTS11 Integrator cleavage module**, receptor from **7SN8** (2.74 A cryo-EM) | The **only** documented small molecule at a protein-protein interface in an MBL-beta-CASP nuclease complex, 55 A from the active site, in a three-subunit pocket. Structurally and functionally validated. Closest possible analogue to your setup |
| **nsp10-nsp14 ExoN interface fragments** (VT00019 / VT00180 / VT00259) | **SARS-CoV-2 nsp10-nsp14 ExoN heterodimer**, receptors from **9FWH / 9FWM / 9FWT** | A published nuclease-plus-obligate-partner interface fragment campaign with MST affinities. Not MBL fold, but functionally the same problem you are solving. Also the only case where *drug-like fragments*, not a charged metabolite, are documented at a nuclease interface |

Honest caveat to record alongside Tier B: passing the IP6 rung is a **weak** result,
because a hexa-anion in an electropositive pocket is the easiest interface case imaginable.
Recovering IP6 does not establish that the pipeline can find a neutral drug-like ligand at
a flat interface. The nsp14 fragment rung is the harder and more informative of the two,
and I would weight it accordingly.

### Negative controls to run alongside (cheap, and they sharpen Tier A)

- **JTE-607 parent ester** against human CPSF3. It should score *worse* than its free
  acid. If it scores better, the pipeline is rewarding lipophilicity, not recognition.
- **AN3661** against human CPSF3. It is a potent antiparasitic with human cytotoxicity
  CC50 60.5 uM to >100 uM across six human lines, i.e. no evidence of engaging human
  CPSF3. A high human-CPSF3 score for AN3661 is a red flag for the scoring function.
- **Ebselen, disulfiram, auranofin** against Artemis. These inhibit the enzyme at 8-46 uM
  by thiol/metal reactivity with no co-crystal. A structure-based score *should not* be
  able to rationalise them. If it does, the score is not measuring what you think.
- **Do not include** RNPA2000, purpurin or iriginol hexaacetate anywhere. Refuted as
  aggregators (PMID 33972249).

### What a pass and a fail each license you to say

- **Tier A passes, Tier B passes, RNase J screen is null:** you may write "the method
  recovers known MBL-beta-CASP active-site ligands and the one known MBL-beta-CASP
  interface ligand under this protocol; no ligand was found at the RNase J : MPN621
  interface." That is a publishable negative.
- **Tier A passes, Tier B fails:** the method detects active sites, not interfaces.
  A null at the RNase J interface is then **uninformative** and should be reported as
  such. This is the most likely outcome and the one worth planning for.
- **Tier A fails:** stop. The screen has no measured sensitivity and no result from it
  means anything, positive or negative.

### One structural point to settle before the gate is run

Because the two human CPSF3 benzoxaborole structures model **Fe** and the JTE-607-acid
structure models **Zn**, and because your RNase J receptor is an unvalidated prediction
with two metals of its own, decide and document the metal assignment policy once, up
front, and apply it identically to gate receptors and to the RNase J receptor. Otherwise
a Tier A pass and an RNase J null are not comparable measurements.

---

## Sources

- Kakegawa J, et al. JTE-607, a multiple cytokine production inhibitor, targets CPSF3 and inhibits pre-mRNA processing. Biochem Biophys Res Commun. 2019. [PMID 31399191](https://pubmed.ncbi.nlm.nih.gov/31399191/)
- Ross NT, et al. CPSF3-dependent pre-mRNA processing as a druggable node in AML and Ewing's sarcoma. Nat Chem Biol. 2020;16:50-59. doi:10.1038/s41589-019-0424-1. [PMID 31819276](https://pubmed.ncbi.nlm.nih.gov/31819276/). PDB [6M8Q](https://www.rcsb.org/structure/6M8Q)
- Tao Y, et al. Anticancer benzoxaboroles block pre-mRNA processing by directly inhibiting CPSF3. Cell Chem Biol. 2024;31:139-149.e14. doi:10.1016/j.chembiol.2023.10.019. [PMID 37967558](https://pubmed.ncbi.nlm.nih.gov/37967558/). PDB [8T1Q](https://www.rcsb.org/structure/8T1Q), [8T1R](https://www.rcsb.org/structure/8T1R)
- Liu L, et al. The anticancer compound JTE-607 reveals hidden sequence specificity of the mRNA 3' processing machinery. Nat Struct Mol Biol. 2023;30:1947-1957. doi:10.1038/s41594-023-01161-x. [PMID 38087090](https://pubmed.ncbi.nlm.nih.gov/37090613/), PMC11663416
- Sonoiki E, et al. A potent antimalarial benzoxaborole targets a Plasmodium falciparum cleavage and polyadenylation specificity factor homologue. Nat Commun. 2017;8:14574. doi:10.1038/ncomms14574. [PMID 28262680](https://pubmed.ncbi.nlm.nih.gov/28262680/)
- Palencia A, et al. Targeting Toxoplasma gondii CPSF3 as a new approach to control toxoplasmosis. EMBO Mol Med. 2017;9:385-394. doi:10.15252/emmm.201607370. [PMID 28148555](https://www.embopress.org/doi/abs/10.15252/emmm.201607370)
- Wall RJ, et al. Clinical and veterinary trypanocidal benzoxaboroles target CPSF3. PNAS. 2018;115:9616-9621. doi:10.1073/pnas.1807915115. [PMID 30185555](https://pubmed.ncbi.nlm.nih.gov/30185555/)
- Giordani F, et al. Veterinary trypanocidal benzoxaboroles are peptidase-activated prodrugs. PLoS Pathog. 2020;16:e1008932. doi:10.1371/journal.ppat.1008932. [PMID 33079941](https://journals.plos.org/plospathogens/article?id=10.1371%2Fjournal.ppat.1008932)
- Acoziborole resistance associated mutations in Trypanosoma brucei CPSF3. PLOS Pathog. 2025. [PMID 41774758](https://journals.plos.org/plospathogens/article?id=10.1371%2Fjournal.ppat.1013764)
- Bielinski M, Henderson LR, Yosaatmadja Y, et al. Cell-active small molecule inhibitors validate the SNM1A DNA repair nuclease as a cancer target. Chem Sci. 2024;15:8227-8241. doi:10.1039/d4sc00367e. [PMID 38817593](https://pubmed.ncbi.nlm.nih.gov/38817593/)
- Yosaatmadja Y, Baddock HT, Newman JA, et al. Structural and mechanistic insights into the Artemis endonuclease and strategies for its inhibition. Nucleic Acids Res. 2021;49:9310-9326. doi:10.1093/nar/gkab693. [PMID 34387696](https://academic.oup.com/nar/article/49/16/9310/6350767)
- Cephalosporins inhibit human metallo beta-lactamase fold DNA repair nucleases SNM1A and SNM1B/apollo. Chem Commun. 2016;52:6727. [PMC5063058](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5063058/)
- Inositol hexakisphosphate is required for Integrator function. Nat Commun. 2022;13:5742. doi:10.1038/s41467-022-33506-3. [PMID 36180473](https://pmc.ncbi.nlm.nih.gov/articles/PMC9525679/). PDB [7SN8](https://www.rcsb.org/structure/7SN8)
- Kozielski F, et al. Structural basis for small molecule binding to the SARS-CoV-2 nsp10-nsp14 ExoN complex. Nucleic Acids Res. 2025;53(14):gkaf753. doi:10.1093/nar/gkaf753. [PMID 40794865](https://pubmed.ncbi.nlm.nih.gov/40794865/)
- Schmitz A, et al. RNase P Inhibitors Identified as Aggregators. Antimicrob Agents Chemother. 2021. doi:10.1128/aac.00300-21. [PMID 33972249](https://pubmed.ncbi.nlm.nih.gov/33972249/)
- Matos RG, Simmons KJ, Fishwick CWG, McDowall KJ, Arraiano CM. Identification of ribonuclease inhibitors for the control of pathogenic bacteria. Int J Mol Sci. 2024;25:8048. doi:10.3390/ijms25158048. [PMID 39125622](https://pmc.ncbi.nlm.nih.gov/articles/PMC11311990)
- Structural basis of 3'-tRNA maturation by the human mitochondrial RNase Z complex. EMBO J. 2024. doi:10.1038/s44318-024-00297-w. [PMID 39516281](https://pubmed.ncbi.nlm.nih.gov/39516281/)
- Conserved motifs in both CPSF73 and CPSF100 are required to assemble the active endonuclease for histone mRNA 3'-end maturation. EMBO Rep. 2008. doi:10.1038/embor.2008.146
- UniProt [P75497](https://rest.uniprot.org/uniprotkb/P75497.json) (M. pneumoniae RNase J), [P75174](https://rest.uniprot.org/uniprotkb/P75174.json) (MPN621, uncharacterized MG423 homolog)
- ChEMBL targets CHEMBL5724779 (human CPSF3, 6 activities), CHEMBL4665581 (T. brucei equiperdum CPSF, 0 activities); molecules CHEMBL4303719 (JTE-607), CHEMBL1643740 (AN3661), CHEMBL2347704 (acoziborole)
- RCSB PDB chemical components JBG, XYX, XZC, IHP, U2O, U2C, U1L, UFI, UF3, 9F2 (data.rcsb.org)
- Vendor pages: MedKoo 11800 (JTE-607), MedKoo 10814 (acoziborole), Selleck E0314, MedChemExpress HY-128204 (AN3661), TargetMol T36649 (AN3661), Tocris 5185
