# Prior-Art Kill Check: MPN555 and MPN266 "on RNA polymerase"

Date: 2026-09-28. Binding check required by `PREREG_OMEGAREGION.md` section 3.
Scope: MPN_555 (UniProt P75223, 193 aa, *M. pneumoniae* M129; ortholog MG_377 / P47373-adjacent, see note)
and MPN_266 (UniProt P75509, 145 aa; ortholog MG_127 / P47373).
This file touches no other file in the repo.

---

## VERDICTS (read these first)

### MPN_266 / MG_127: **ALREADY PUBLISHED. KILLED, comprehensively.**

**MPN266 is SpxA.** It is not an uncharacterized protein, it is not unnamed by O'Reilly, and its binding
site on RNA polymerase is solved at 4.2 A resolution.

Four independent kills, any one of which is sufficient:

1. **O'Reilly's own published crosslink table names P75509 as `spxA`** and reports exactly the links the
   prereg attributes to "MPN266". So MPN266 **is** the "SpxA" in the sentence
   "the known auxiliary factors SigA, GreA, NusG, NusA, **SpxA**, and RpoE". The prereg's premise that
   "O'Reilly's sentence does not name it" is **false**.
2. **Yus et al. 2019** (one year before O'Reilly) name it verbatim as **"SpxA, MPN266"**, call it
   "the associated to the component of the RNA polymerase, SpxA", ChIP-seq it, and state
   "**SpxA is an essential protein in *M. pneumoniae*.**"
3. **Lluch-Senar et al. 2015** Table S2 already annotates MPN266 as `spxA` /
   "Transcriptional regulatory protein Spx".
4. **The binding site is published**: Spx binds the RNAP alpha subunit C-terminal domain and sigma-A.
   Four crystal/cryo-EM structures (1Z3E, 3GFK, 3IHQ, 7F75). O'Reilly's own published crosslinks place
   SpxA on RpoA **K266 and K324**, and M. pneumoniae RpoA's alphaCTD is InterPro IPR011260 at
   **residues 258-320**. The published data already localises it to the published site.

### MPN_555 / MG_377: **PARTLY PUBLISHED.** The protein, its fold, its family, its essentiality, its
RNAP association and a proposed function are all published. **The RNAP binding site is NOT published.**

- Solved crystal structure exists: **PDB 1ZXJ**, 2.8 A, with a peer-reviewed paper.
- Family exists: **InterPro IPR054820 "MPN555 chaperone-like"**, NCBIfam NF045756.
- It is a **truncated trigger factor**: C-terminal chaperone domain only, paralog of full-length Tig
  (MPN_331 / P75454, 444 aa). Published in 2026.
- RNAP association: published by O'Reilly et al. 2020 main text (same sentence as MPN530).
- Essential: published (Lluch-Senar 2015, Glass 2006).
- **Not published: where on RNAP it sits.** No structure, no model, no residue-level site claim.
  O'Reilly explicitly could not place it in the expressome density.

**A NEW COLLISION was found that the repo's OMEGAREGION lineage does not account for:** Yus et al. 2019
tested MPN555 by ChIP-seq and classified it as **"non-RNAP-associated"**, dismissing its RNAP-like profile
as artifactual. This must be cited. It cuts both ways and is discussed in section 6.

---

## 1. MPN_555 / MG_377

### 1a. Identity: matches the brief, no contradiction

UniProt **P75223** (Y555_MYCPN), **193 aa**, 22,434 Da, `OrderedLocusNames=MPN_555`,
ORFNames `H03_orf193o`, `MP287`. RecName "Uncharacterized protein MG377 homolog".
**Protein existence level 1 (evidence at protein level).** Retrieved from
`https://rest.uniprot.org/uniprotkb/P75223.txt`, entry version 93, 2026-06-10.

**Nothing contradicts the brief.** One note: the brief says the M. genitalium ortholog is "MG_377
(Uncharacterized protein MG377 homolog)". Strictly, "MG377 homolog" is the name of the *M. pneumoniae*
entry; the *M. genitalium* protein is MG_377 itself. The repo's own `data/proteins.csv` carries MG_377 at
193 aa with the M. genitalium sequence, consistent.

### 1b. Structure: SOLVED. This is EXPERIMENTAL and PUBLISHED.

**PDB 1ZXJ** "Crystal structure of the hypthetical Mycoplasma protein, MPN555". X-ray, **2.80 A**,
chains A/B/C/D = residues 1-193. Deposited 2005-06-08, released 2005-07-26. Berkeley Structural Genomics
Center / PSI. Retrieved from `https://data.rcsb.org/rest/v1/core/entry/1ZXJ`.

**Peer-reviewed structure paper:**
Schulze-Gahmen U., Aono S., Chen S., Yokota H., Kim R., Kim S.-H. (2005)
"Structure of the hypothetical Mycoplasma protein MPN555 suggests a chaperone function."
*Acta Crystallographica Section D* 61(Pt 10):1343-1347. DOI 10.1107/S090744490502264X. **PMID 16204885.**

Verbatim from the abstract (fetched from eutils efetch, db=pubmed, id=16204885):

> "Structure determination revealed a mostly alpha-helical protein with a three-lobed shape. The three
> lobes or fingers delineate a central binding groove and additional grooves between lobes 1 and 3 and
> between lobes 2 and 3. For one of the molecules in the asymmetric unit, the central binding pocket was
> filled with a peptide from the uncleaved N-terminal affinity tag. The MPN555 structure has structural
> homology to two bacterial chaperone proteins: SurA and trigger factor from Escherichia coli."

UniProt records the secondary structure from 1ZXJ: strands 8-11, 21-23, 77-80, 183-185; helices 30-41,
49-73, 74-76, 83-95, 104-127, 133-146, 152-155, 158-179.

**Important for the write-up:** the published structure's central binding groove was found occupied by a
peptide. The protein has a known, characterised peptide-binding groove.

### 1c. Family and fold assignments: DATABASE ANNOTATION, computational

| Resource | Accession | Name |
|---|---|---|
| InterPro (family) | **IPR054820** | MPN555 chaperone-like |
| InterPro | IPR037041 | Trigger factor, C-terminal domain superfamily |
| InterPro | IPR027304 | Trigger factor / SurA domain superfamily |
| NCBIfam | **NF045756** | MPN555 family protein chaperone |
| Gene3D | **1.10.3120.10** | Trigger factor, C-terminal domain |
| SUPFAM | **SSF109998** | Trigger factor / SurA peptide-binding domain-like |
| PDBsum | 1ZXJ | - |
| HOGENOM | CLU_110277_0_0_14 | - |
| OrthoDB | 398943at2 | - |
| EvolutionaryTrace | P75223 | - |

**There is NO Pfam entry and NO DUF number for MPN555.** UniProt P75223 lists no Pfam cross-reference.
(Contrast MG354/MPN530, which has Pfam PF09188 / DUF1951. Do not carry that assumption across.)
KEGG's motif line for MPN_555 reports weak Pfam hits (`Trigger_C`, `Endotoxin_N`, `Chordopox_G2`, `PriC`);
`Trigger_C` is the real one, the rest are noise and must not be cited as family assignments.

InterPro IPR054820 description, verbatim:

> "This entry includes MNP55 from Mycoplasma pneumoniae, also known as MG377 homolog. According to
> structural homology, this protein may be involved in protein folding as a molecular chaperone"

(the typo "MNP55" is InterPro's). IPR054820 cites three papers: PMID 16204885, PMID 22373819
(van Noort et al. 2012), and **PMID 32732422 (O'Reilly et al. 2020)**. So InterPro itself already links
this family to the O'Reilly paper.

GO terms on P75223: **GO:0006457 protein folding** and **GO:0015031 protein transport**, both
**IEA:InterPro**, i.e. electronically inferred, not experimental.

### 1d. Homologs outside Mollicutes: NONE at family level. Fold homologs are chaperones, not RNAP factors.

InterPro IPR054820 taxonomy, retrieved live
(`https://www.ebi.ac.uk/interpro/api/taxonomy/uniprot/entry/interpro/IPR054820/`):
**25 proteins, 56 taxa, all Mollicutes.** The full genus list is *Mycoplasmoides*, *Mycoplasma*,
*Ureaplasma*, *Malacoplasma*. No Firmicute, no *Bacillus*, no *Escherichia*, no *Streptococcus*.
One experimental structure in the family (1ZXJ), 18 AlphaFold models.

**The fold homologs outside Mollicutes are named and characterised, and they are chaperones:**

- ***E. coli* trigger factor (Tig)** C-terminal domain, and **SurA** (Schulze-Gahmen 2005, above).
- Merz F., Hoffmann A., Rutkowska A., Zachmann-Brand B., Bukau B., Deuerling E. (2006)
  "The C-terminal domain of Escherichia coli trigger factor represents the central module of its
  chaperone activity." *J Biol Chem* 281(42):31963-31971. DOI 10.1074/jbc.M605164200. **PMID 16926148.**
  Verbatim: "Intriguingly, a structurally similar module is found in the periplasmic chaperone SurA and in
  MPN555, a protein of unknown function."

**Against the specific list in the brief: NO resemblance to omega/RpoZ, delta/RpoE, epsilon, YkzG/UPF0356,
HelD, Spx, CarD, RbpA, Gfh1, or DksA.** MPN555's fold is the trigger factor C-terminal / SurA
peptide-binding module (SSF109998, Gene3D 1.10.3960.10 is MG354's, MPN555's is 1.10.3120.10). None of the
listed RNAP-binding factors carries that fold. **Novelty is not killed by homology for MPN555.**

### 1e. It is a truncated trigger factor. PUBLISHED 2026, and this is the biggest thing the repo is missing.

Todor H. et al. (2026) "Predicting the protein interaction landscape of a free-living bacterium with
pooled-AlphaFold3." *Molecular Systems Biology* 22(4):497-518. DOI 10.1038/s44320-026-00189-7.
**PMID 41559189, PMC13047044.** This is the same paper the repo's `PREREG.md` uses as its data source.

Verbatim from the full text (read directly from the PMC XML via eutils efetch, db=pmc, id=13047044):

> "M. genitalium and the related M. pneumoniae each encode a full-length non-essential Tig and an
> **essential Tig homolog containing only the C-terminal chaperone domain (MG_377/MPN555**, Fig. 6C)
> (O'Reilly et al, 2020; Glass et al, 2006). Our data suggest a role for MG_377/MPN555 in protein
> secretion: both M. genitalium MG_377 and M. pneumoniae MPN555, but not their canonical Tigs, have strong
> predicted interactions with **SecA**, the membrane subunit of the bacterial Sec apparatus (Datasets EV4
> and EV6; Fig. 6C). This predicted interaction may be essential for SecA function due to the lack of
> other secretory chaperones such as SecB or CsaA (Linde et al, 2003) in Mycoplasma."

Evidence class: the essentiality and the domain architecture are **experimental/published**; the SecA
interaction is a **computational prediction** (AlphaFold3).

The full-length paralog is **Tig, MPN_331, UniProt P75454, 444 aa** (verified live from UniProt).
MPN555 at 193 aa is the C-domain-only paralog.

**Todor et al. also did exactly the RNAP analysis this project is doing, in the same organism**, and their
Fig 5 RNAP cluster names GreA, NusG, UvrD, **Spx**, and MG_354 (citing O'Reilly for MG_354). **MG_377 is
not in their RNAP figure.** In the repo's local copy of their pair table (`data/moesm8_pairs.csv`), no
MG_377 x RNAP-subunit pair was co-folded at all, so their dataset does not speak to MPN555 on RNAP either
way. The only target x RNAP pair present is **MG_127 x MG_177 (rpoA), flagged `y=True`**, i.e. already a
positive in STRING's experimental truth set.

### 1f. RNAP association: PUBLISHED (O'Reilly 2020), experimental, and the residue-level links are theirs

O'Reilly F.J., Xue L., Graziadei A., Sinn L., Lenz S., Tegunov D., Blotz C., Singh N., Hagen W.J.H.,
Cramer P., Stulke J., Mahamid J., Rappsilber J. (2020) "In-cell architecture of an actively
transcribing-translating expressome." *Science* 369(6503):554-557. DOI 10.1126/science.abb3758.
**PMID 32732422, PMC7115962.** Verbatim (read by me from the PMC XML, not from a snippet):

> "Additionally, two uncharacterized essential proteins, MPN555 and MPN530 (21), were found and the
> interaction of MPN530 with beta/beta' subunits was independently validated by a bacterial two-hybrid
> screen (fig. S4)."

**The four "MPN555 to RpoB" links the prereg uses are O'Reilly's own published supplementary data.**
From their released link table (`Myco_InCell_DSS_dataset_5link_5PPI_Links_xiFDR1.2.30.59dev.csv`, held
locally at `C:\Users\bmens\NQ_local\af3-hitcall\xlms2020_dss\`), where P75223 is labelled `mpn555`:

    rpoB 1319 <-> mpn555 45     [BS3/DSS]
    rpoB 1319 <-> mpn555 158    [BS3/DSS]
    rpoB 1319 <-> mpn555 160    [DSSO, in the DSSO table]
    rpoB 1269 <-> mpn555 116    [BS3/DSS]

O'Reilly's data also records MPN555 crosslinks to **groEL** (352 <-> 6), **tuf** (57 <-> 45, 314 <-> 158),
**dhfr** (25 <-> 116), **mglA**, and mpn474a. The groEL and tuf partners are consistent with the published
chaperone assignment and should be mentioned, because they are an alternative reading of the same protein.

**Note the residue collision:** MPN555 K116 crosslinks to BOTH rpoB 1269 and dhfr 25; MPN555 K158
crosslinks to BOTH rpoB 1319 and tuf 314; MPN555 K45 to BOTH rpoB 1319 and tuf 57. In the published data
the same MPN555 lysines reach RNAP and abundant cytosolic proteins. That is what a promiscuous
peptide-binding chaperone groove looks like, and it is a live alternative explanation for the
"convergent hub at RpoB K1319" in `RESULT_OMEGAREGION.md` section 1.

### 1g. Is the BINDING SITE on RNAP published? **NO. This is the one thing still open.**

Checked and found nothing:

- **No co-complex structure.** InterPro reports exactly **one** PDB structure for IPR054820: 1ZXJ, MPN555
  alone. No MPN555-RNAP entry exists.
- **O'Reilly could not place it.** Verbatim from PMC7115962: "All other proteins found interacting with
  RNAP by CLMS did not fit in the elongating expressome density".
- **Todor et al. 2026 did not model it on RNAP** (section 1e).
- Europe PMC full-text search for `"MPN555"` returns **9 hits total**, all accounted for: Schulze-Gahmen
  2005, Merz 2006, O'Reilly 2020, Todor 2026, Yus 2019 (section 6), two M. pneumoniae phosphoproteome
  papers (PMID 17605819, PMID 20097688), and two trigger-factor papers (PMID 19737520, PMID 20595383).
  None reports a binding site on RNAP.
- PubMed search for `"MPN_555"`: **0 hits.** For `"MPN555"`: 10 hits, 8 false positives
  (myeloproliferative neoplasms etc.).
- Europe PMC preprint search (`SRC:PPR`) for MPN555 / MG_377: no relevant preprint.

**So the site is genuinely unpublished.** But see section 3 for what "the omega region" can and cannot be
called given that *M. pneumoniae* has no omega subunit.

### 1h. Essentiality: PUBLISHED, experimental, both organisms

From **Lluch-Senar M. et al. (2015)** "Defining a minimal cell: essentiality of small ORFs and ncRNAs in a
genome-reduced bacterium." *Mol Syst Biol* 11:780. DOI 10.15252/msb.20145558. **PMID 25609650,
PMC4332154.** This is O'Reilly's reference 21 for the word "essential". I read their supplementary
workbook directly (local copy `essential/msb_suppl.zip`, file `msb0011-0780-sd20.xlsx`, sheet
"Table S11", panel B "Comparative between M. genitalium and M. pneumoniae"):

    MPN555   MG_377   E   E

i.e. **essential in both *M. pneumoniae* (transposon mutagenesis, this paper) and *M. genitalium*
(Glass et al. 2006, the comparison column)**. Their Table S2 (`msb0011-0780-sd11.xlsx`) annotates MPN555
functional category `O` with the free-text annotation "DNA/RNA binding".

Also in that supplement, Table S6 (`msb0011-0780-sd15.xlsx`), SEC-MS of cell extract: MPN555 elutes at an
apparent **22-29 kDa** across fractions, against a monomer mass of 22.4 kDa and an RNAP core of roughly
400 kDa. **Published size-exclusion data therefore do not show MPN555 in a stable large complex.** Report
this as a caveat, not as a refutation; SEC-MS in a lysate readily loses transient interactions.

Glass J.I. et al. (2006) "Essential genes of a minimal bacterium." *PNAS* 103(2):425-430
(cited by both O'Reilly and Todor for MG_377 essentiality). I did not read Glass's own table; the
essentiality call above rests on the Lluch-Senar comparison column and on Todor's and O'Reilly's citations
of Glass. Flagging that as second-hand.

### 1i. Other published facts about MPN555

- **Phosphorylation / acetylation**: van Noort V. et al. (2012) "Cross-talk between phosphorylation and
  lysine acetylation in a genome-reduced bacterium." *Mol Syst Biol* 8:571. DOI 10.1038/msb.2012.4.
  **PMID 22373819.** Cited by InterPro IPR054820 for this protein. Also PMID 17605819 (Mapping
  phosphoproteins in M. genitalium and M. pneumoniae) and PMID 20097688 (M. pneumoniae phosphoproteome)
  both return MPN555 in Europe PMC full text. I did not read these three to confirm which modification
  site; treat as "MPN555 appears in M. pneumoniae phospho/acetyl proteome studies" and verify the site
  before citing one.
- **IntAct** (retrieved live, `findInteractions/P75223`): 3 non-self interactions, all from
  **PMID 19965468** (Kuhner S. et al. 2009, "Proteome organization in a genome-reduced bacterium,"
  *Science* 326:1235-1240, DOI 10.1126/science.1176343), detection method **TAP**:
  **nrdE** (P78027) and **hprK** (P75548), plus a self-association. **No RNAP subunit.**
- **STRING v12** (species 272634, retrieved live): MPN_555's top 15 partners are **all genomic-neighborhood
  edges to MPN_545 through MPN_559** plus one textmining edge to MPN_530 (0.753). **STRING contains no
  rpo edge for MPN_555 at all** (no experimental, no coexpression). So unlike MPN266, MPN555's RNAP
  association is *not* encoded in STRING, only in O'Reilly's text and data.

---

## 2. MPN_266 / MG_127: this protein is SpxA

### 2a. Identity: matches the brief, with one thing the brief gets wrong by omission

UniProt **P75509** (Y266_MYCPN), **145 aa**, 16,809 Da, `OrderedLocusNames=MPN_266`, ORFNames
`A65_orf145`, `MP567`. RecName "Uncharacterized protein MG127 homolog". PE 3 (inferred from homology).
Entry version 115, 2026-09-02.

**The brief's accession and length are correct. The brief's framing "uncharacterized" is not.**
The SAME UniProt entry that carries the name "Uncharacterized protein MG127 homolog" also carries:

    CC   -!- SIMILARITY: Belongs to the ArsC family. {ECO:0000305}.
    DR   InterPro; IPR006504; Tscrpt_reg_Spx/MgsR.
    DR   Pfam; PF03960; ArsC; 1.
    DR   PANTHER; PTHR30041:SF7; GLOBAL TRANSCRIPTIONAL REGULATOR SPX; 1.
    DR   NCBIfam; TIGR01617; arsC_related; 1.
    DR   PROSITE; PS51353; ARSC; 1.
    FT   DISULFID  21..24  /note="Redox-active"
    KW   Disulfide bond; Oxidoreductase; Redox-active center;

**This is the trap the project fell into.** `omega/mg_protein_names.json` and the repo's protein table
take UniProt's *RecName* ("Uncharacterized protein MG127 homolog") and ignore the family annotation on the
same record. Every other resource names it:

| Resource | What it calls MPN_266 / P75509 |
|---|---|
| **NCBI RefSeq WP_010874623.1** | "**Spx/MgsR family RNA polymerase-binding regulatory protein**" |
| **KEGG mpn:MPN_266** | SYMBOL `ygl1`; ORTHOLOGY **K16509 regulatory protein spx**; BRITE category "Transcription" |
| **InterPro IPR006504** | Transcriptional regulator Spx/MgsR |
| **NCBIfam TIGR01617** | Spx/MgsR family RNA polymerase-binding regulatory protein |
| **PANTHER PTHR30041:SF7** | Global transcriptional regulator Spx |
| **Lluch-Senar 2015 Table S2** | `spxA` / "Transcriptional regulatory protein Spx" |
| **O'Reilly 2020 crosslink tables** | `spxA` |
| **Yus 2019** | "SpxA, MPN266" |

**The RefSeq name of this protein contains the phrase "RNA polymerase-binding".**

**MPN_266 is the only Spx/ArsC-family protein in *M. pneumoniae*.** UniProt search over organism 272634
for `IPR006504 OR gene:spx OR gene:spxA OR PF03960` returns **exactly one entry: P75509**. Same query over
*M. genitalium* (243273) returns exactly one: **P47373 (MG127, 145 aa)**. So there is no other candidate
for "SpxA" in this organism, and O'Reilly's SpxA must be MPN_266. That inference is then confirmed
directly in 2b.

### 2b. O'Reilly DOES name it. Verbatim from their own released data file.

From `Myco_InCell_DSSO_dataset_5link_5PPI_ppi_xiFDR1.2.30.59dev.csv` (O'Reilly's published supplementary
crosslink tables, local copy at `C:\Users\bmens\NQ_local\af3-hitcall\xlms2020\`), the protein-name column
for accession **P75509 is literally `spxA`**:

    P75509  spxA  <->  P75509  spxA   DSSO   (6 links, self)
    P75509  spxA  <->  P78022  sigA   DSSO   (1 link)
    Q50295  rpoA  <->  P75509  spxA   DSSO   (1 link)

And from their DSS/BS3 link table, residue level:

    rpoA 266 <-> spxA 5       rpoA 324 <-> spxA 5
    rpoA 266 <-> spxA 51      rpoA 324 <-> spxA 46
    sigA 466 <-> spxA 129     sigA 473 <-> spxA 129
    rpoB 1319 <-> spxA 139    rpoB 1326 <-> spxA 139

So the six links that `PREREG_OMEGAREGION.md` lists as "MPN_266 ... 6 (4 to RpoA, 2 to RpoB)" are
**O'Reilly's published spxA links**, and O'Reilly additionally report two sigA links that the prereg's
extraction dropped.

**Answer to question 4, unambiguously: YES.** MPN266 appears in O'Reilly's supplementary data, under the
name `spxA`, and it is named in their main-text sentence as one of "the known auxiliary factors". It was
never one of the "two uncharacterized essential proteins"; it was in the *known* list.

### 2c. And it was published a year earlier, with ChIP-seq

**Yus E., Llorens-Rico V., Martinez S., Gallo C., Eilers H., Blotz C., Stulke J., Lluch-Senar M.,
Serrano L. (2019)** "Determination of the Gene Regulatory Network of a Genome-Reduced Bacterium Highlights
Alternative Regulation Independent of Transcription Factors." *Cell Systems* 9(2):143-158.e13.
DOI 10.1016/j.cels.2019.07.001. **PMID 31445891, PMC6721554.**

Verbatim, read by me from the PMC XML:

> "Sequence analysis suggests the existence of 10 putative TFs (HcrA, MPN124; GntR, MPN239; WhiA-like,
> MPN241; **SpxA, MPN266**; MraZ, MPN314; Fur, MPN329; YlxM, MPN424, YebC, MPN478; alternative sigma
> MPN626; and DnaA, MPN686)."

> "**SpxA is an essential protein in M. pneumoniae.** In B. subtilis it directs the RNAP to specific
> promoters upon oxidative stress or redox changes (Nakano et al., 2003)."

> "peaks associated to proteins from the core RNAP complex (RpoB MPN516 and RpoA MPN191 TAP-tagged; and
> SigA MPN352 FLAG-tagged) as well as **the associated to the component of the RNA polymerase, SpxA**
> (FLAG-tagged), were found at promoter sites. ... we found **167 common peaks between the SpxA and the
> RNAP subunits**. In both cases, more than 91% of these common peaks corresponded to annotated promoters"

> "Addition of diamide to M. pneumoniae revealed that SpxA regulates itself and a regulon involved in the
> oxidative stress response (mpn607, msrA; mpn625, osmC; and mpn662, msrB) (Zhang and Baseman, 2014) as
> well as other genes (Table S5)."

Evidence class: **experimental** (ChIP-seq, FLAG and TAP tagging, diamide induction, transcriptomics).
Note Yus used SpxA (MPN266) alongside SigA as the reproducibility benchmark for the entire ChIP-seq
dataset, so it is not a marginal entry in that paper.

(The Zhang and Baseman 2014 citation resolves to: Zhang W., Baseman J.B. "Functional characterization of
osmotically inducible protein C (MG_427) from Mycoplasma genitalium." *J Bacteriol* 196:1012-1019.
PMID 24363346, PMC3957695. It is the source for the regulon members, not an Spx paper. Do not cite it as
evidence about SpxA itself.)

### 2d. Family / accessions for MPN266

| Resource | Accession | Name |
|---|---|---|
| **Pfam** | **PF03960** | ArsC |
| **InterPro (family)** | **IPR006504** | Transcriptional regulator Spx/MgsR |
| InterPro | IPR006660 | Arsenate reductase-like |
| InterPro | IPR036249 | Thioredoxin-like superfamily |
| **NCBIfam** | **TIGR01617** | Spx/MgsR family RNA polymerase-binding regulatory protein |
| PANTHER | PTHR30041 / :SF7 | Arsenate reductase / Global transcriptional regulator Spx |
| Gene3D | 3.40.30.10 | Glutaredoxin |
| SUPFAM | SSF52833 | Thioredoxin-like |
| PROSITE | PS51353 | ARSC |
| KEGG KO | **K16509** | regulatory protein spx |
| HOGENOM | CLU_116644_1_1_14 | - |
| OrthoDB | 9794155at2 | - |

**No DUF number.** It is not a DUF; it is a named family.

InterPro IPR006504 description, verbatim:

> "Characterised members of this family include Spx and MgsR from Bacillus subtilis. Spx is a global
> transcription regulator that plays a key role in stress response and exerts either positive or negative
> regulation of genes. ... **It interacts with RNA polymerase**"

**11,331 proteins, 12,445 taxa, 12 solved structures.** This is a large, well-studied, cross-phylum family.

### 2e. Homologs outside Mollicutes: YES, and they are the exact proteins the brief asked about

**Spx (spxA, BSU11500) and MgsR (BSU24770) from *Bacillus subtilis*** (verified live from KEGG
`find/genes/spx`). The brief listed "Spx" among the factors to check. **That is a direct hit.**
MPN266 is a Spx. This kills novelty on family, on function class, and on RNAP association.

### 2f. Is the BINDING SITE published? **YES. Four structures, and O'Reilly's own data already localises it.**

Published Spx-RNAP structures (retrieved live from InterPro's structure list for IPR006504, citations from
the RCSB data API):

| PDB | What it is | Method / res | Paper |
|---|---|---|---|
| **1Z3E** | Spx in complex with the C-terminal domain of the RNAP alpha subunit | X-ray **1.5 A** | Newberry K.J., Nakano S., Zuber P., Brennan R.G. (2005) *PNAS* 102:15839. DOI 10.1073/pnas.0506592102 |
| **3GFK** | *B. subtilis* Spx / RNAP alpha subunit CTD, in vivo assembled | X-ray **2.3 A** | Lamour V., Westblade L.F., Campbell E.A., Darst S.A. (2009) *J Struct Biol* 168:352. DOI 10.1016/j.jsb.2009.07.001 |
| **3IHQ** | Reduced C10S Spx with alphaCTD | X-ray **1.9 A** | Nakano M.M. et al. (2010) *PLoS ONE* 5:e8664. DOI 10.1371/journal.pone.0008664 |
| **7F75** | **Intact Spx-dependent transcription activation complex** | cryo-EM **4.2 A** | Shi J. et al. (2021) *Nucleic Acids Res* 49(18):10756-10769. DOI 10.1093/nar/gkab790. **PMID 34530448, PMC8501982** |

7F75's ten polymer entities are RNAP alpha (x3 chains), beta, beta', **omega**, sigma-A, **epsilon**,
**Spx**, delta, and both trxA promoter strands. Verbatim from Shi et al.'s abstract:

> "an oxidized Spx monomer engages RNAP by simultaneously interacting with the C-terminal domain of RNAP
> alpha subunit (alphaCTD) and sigma-A. The interface between Spx and alphaCTD is distinct from those
> previously reported activators"

**And O'Reilly's published crosslinks already place MPN266's SpxA at that same site.** *M. pneumoniae*
RpoA (Q50295) is **327 aa**, and its alphaCTD is **InterPro IPR011260 at residues 258-320** (retrieved
live from the InterPro API). O'Reilly's spxA crosslinks go to **rpoA K266** (inside the alphaCTD) and
**rpoA K324** (the C-terminal tail just past it), plus **sigA K466 and K473**. That is the alphaCTD +
sigma-A double interface of 7F75, recovered in published crosslinking data, in this organism.

**Note for the write-up:** O'Reilly's data ALSO has `rpoB 1319/1326 <-> spxA 139`, which is the single link
`PREREG_OMEGAREGION.md` uses for its MPN266 reading. Those two links are in the published data too. What
is NOT published is any interpretation of them. But the project's MPN266 reading was obtained by keeping
that one beta link and dropping the four rpoA links and two sigA links that point at the published site.
**That is a selection the write-up must disclose.**

### 2g. Essentiality: PUBLISHED, both organisms, two independent statements

- **Lluch-Senar 2015 Table S11(B)** (read from the local supplement): `MPN266  MG_127  E  E`.
  **Essential in *M. pneumoniae* (transposon mutagenesis) and in *M. genitalium*.**
- **Yus 2019**, verbatim: "SpxA is an essential protein in *M. pneumoniae*."

Same SEC-MS caveat as MPN555: Lluch-Senar's Table S6 shows MPN266 eluting at an apparent **21-27 kDa**
against a 16.8 kDa monomer, not at RNAP-complex size.

### 2h. Other published interaction evidence for MPN266

- **IntAct** (`findInteractions/P75509`): **sigA (P78022) by TAP**, plus dnaJ-like (Q50312), from
  **PMID 19965468 (Kuhner et al. 2009, *Science* 326:1235-1240)**. So an experimental RNAP-machinery
  association for MPN266 has been in the public interaction databases since **2009**.
- **STRING v12** (species 272634, retrieved live), MPN_266 = `ygl1`, **experimental-channel** scores:

  | Partner | combined | experimental |
  |---|---|---|
  | **sigA** | 0.875 | **0.850** |
  | **rpoA** | 0.869 | **0.857** |
  | **rpoC** | 0.825 | **0.825** |
  | **rpoE** | 0.604 | 0.596 |
  | **rpoB** | 0.596 | 0.596 |

  **STRING's experimental channel already contains MPN266 to rpoA, rpoB, rpoC, rpoE and sigA at high
  confidence.** Independently confirmed inside this project's own files: in the local copy of Todor's pair
  table, MG_127 x MG_177 (rpoA) carries `y = True`, i.e. it is a positive in the STRING experimental truth
  set this project uses as ground truth.

**So MPN266-RNAP was already a labelled positive in the project's own truth set.**

---

## 3. A separate problem the kill check turned up: *M. pneumoniae* has no omega subunit

This is not prior art, but it bears directly on how `RESULT_OMEGAREGION.md` may be worded.

- **UniProt search over organism 272634 for `gene:rpoZ OR protein_name:omega`** returns only P78032,
  DNA topoisomerase 1 (whose alias is "Omega-protein"). **No RpoZ.**
- **KEGG `link/mpn/ko:K03060` (rpoZ) returns empty.** The positive control
  `link/bsu/ko:K03060` returns `bsu:BSU15690`, so the query works.
- **Todor et al. 2026**, verbatim: "RNA polymerase is a multisubunit enzyme composed of
  alpha-alpha-beta'-beta-delta-sigmaA".

So the "omega region" in `RESULT_OMEGAREGION.md` is a region defined on a *B. subtilis* template (6WVJ,
6WVK) for a subunit that **does not exist in the organism the crosslinks came from**. The prereg's own
section 4 says "Omega is present in these structures, so its pocket is occupied", which is the right
caveat for *B. subtilis*. The stronger and more accurate statement is that *M. pneumoniae* RNAP has no
omega at all, so the measurement is "distance to where omega sits in *B. subtilis*", i.e. a coordinate
label on the beta subunit, not a biological pocket in the target organism. **Phrase it as a beta-subunit
location, and name the RpoB residues.** That is also the more useful claim, because RpoB K1319 is testable.

---

## 4. What I searched, including where I found nothing

Resources queried live on 2026-09-28, with the result:

| Resource | MPN555 / MG_377 | MPN266 / MG_127 |
|---|---|---|
| UniProt REST (flat file + JSON) | full record read | full record read |
| UniProt family/organism searches | 25-member Mollicute family | only Spx-family protein in either organism |
| InterPro API (entry, taxonomy, structures) | IPR054820, 1 structure, Mollicutes only | IPR006504, 12 structures, 12,445 taxa |
| Pfam | **none** | PF03960 |
| PDB / RCSB data API | **1ZXJ** (alone) | family: 1Z3E, 3GFK, 3IHQ, 7F75 (all with RNAP alphaCTD) |
| KEGG REST | conserved hypothetical, `Trigger_C` motif | **K16509 spx**, symbol ygl1 |
| NCBI RefSeq (efetch) | "MPN555 family protein chaperone" | "**Spx/MgsR family RNA polymerase-binding regulatory protein**" |
| STRING v12 API | **no rpo edge** | rpoA/B/C/E + sigA, experimental channel |
| IntAct REST | nrdE, hprK (TAP, 2009) | **sigA (TAP, 2009)** |
| PubMed esearch/efetch | 2 real papers | phrase `"MPN266"` and `"MG127"` **not found in PubMed** |
| Europe PMC full text | 9 hits, all accounted for | 3 hits: Yus 2019, Trussart 2017, 1 false positive |
| Europe PMC preprints (SRC:PPR) | nothing relevant | nothing relevant |
| O'Reilly 2020 PMC XML (eutils) | named in main text | **not in main text by locus tag; named as SpxA** |
| O'Reilly supplementary link tables (local) | 4 rpoB links, labelled `mpn555` | **8 links, labelled `spxA`** |
| Todor 2026 PMC XML (eutils) | essential truncated Tig, SecA | "Spx" in RNAP figure |
| Lluch-Senar 2015 supplement (local xlsx) | Table S11: E / E | Table S2 `spxA`; Table S11: E / E |
| Glass 2006 | **not read directly** (second-hand via Todor and Lluch-Senar) | same |
| **MycoWiki (mycowiki.uni-goettingen.de)** | **UNREACHABLE**, connection refused (134.76.18.60:443) on both http and https. **Not checked. This is a gap.** | same gap |
| bioRxiv API | no relevant hit | no relevant hit |

Explicit "not found" statements:

- **Not found:** any Pfam or DUF accession for MPN555.
- **Not found:** any structure, model, docking, or residue-level claim placing MPN555 on RNA polymerase.
- **Not found:** any paper reporting MPN555 near the omega position or at RpoB K1319.
- **Not found:** any homolog of MPN555 outside Mollicutes at the InterPro family level.
- **Not found:** the strings `"MPN266"`, `"MG127"`, `"MG_127"`, `"MPN_266"`, `"MPN_555"` as PubMed-indexed
  phrases; this protein's literature is all under the name **SpxA**, which is exactly why a locus-tag
  search missed it.
- **Not checked:** MycoWiki (server down), Glass et al. 2006 primary tables, the three
  phospho/acetyl-proteome papers' specific MPN555 sites, and O'Reilly's fig. S4 / table S2 as rendered
  documents (I used their released machine-readable link tables instead, which is stronger).

---

## 5. Answers to the six questions, compactly

**1. Published function, family, structure, interaction?**
MPN555: structure **published** (1ZXJ, Schulze-Gahmen 2005, experimental); function **proposed** as
molecular chaperone from fold homology to *E. coli* trigger factor C-domain and SurA (published
prediction, twice: Schulze-Gahmen 2005 and Merz 2006); identified in 2026 as an **essential truncated
trigger factor paralog** with a **predicted** SecA interaction (Todor 2026); RNAP interaction
**published experimentally** (O'Reilly 2020 crosslinking MS); TAP interactions with nrdE and hprK
(Kuhner 2009, experimental).
MPN266: it is **SpxA**, a global redox-responsive transcriptional regulator; family **published**
(Spx/MgsR, IPR006504); RNAP association **published experimentally** three times over (Kuhner 2009 TAP to
sigA; Yus 2019 ChIP-seq co-occupancy, 167 shared peaks; O'Reilly 2020 crosslinks to rpoA, rpoB, sigA);
regulon **published** (Yus 2019 diamide experiment); redox-active disulfide Cys21-Cys24 annotated.

**2. Exact accessions; solved structure?**
MPN555: InterPro **IPR054820** (+ IPR037041, IPR027304), NCBIfam **NF045756**, Gene3D **1.10.3120.10**,
SUPFAM **SSF109998**. **No Pfam, no DUF.** Solved structure: **PDB 1ZXJ**, 2.8 A, the only one in the
family.
MPN266: Pfam **PF03960**, InterPro **IPR006504** (+ IPR006660, IPR036249), NCBIfam **TIGR01617**,
PROSITE **PS51353**, KEGG KO **K16509**. No structure of MPN266 itself; **12 structures in the family**,
including four of a homolog bound to RNAP.

**3. Is the binding site on RNAP published?**
MPN555: **NO.** MPN266: **YES** (alphaCTD + sigma-A; 1Z3E, 3GFK, 3IHQ, 7F75; and O'Reilly's own rpoA
K266/K324 and sigA K466/K473 crosslinks land there).

**4. Is MPN266 mentioned anywhere as RNAP-associated, and is it essential?**
**YES to both, emphatically.** It is in O'Reilly's main-text list of *known* auxiliary factors as "SpxA",
and in their supplementary crosslink tables under the protein name `spxA` with links to rpoA, rpoB and
sigA. It is in Yus 2019 as "SpxA, MPN266", RNAP-associated, ChIP-seq'd, **essential**. It is in
Lluch-Senar 2015 as `spxA`, **essential in both organisms**. It has been in IntAct since 2009 and is in
STRING's experimental channel against rpoA/B/C/E and sigA today.

**5. Homologs outside Mollicutes / resemblance to known RNAP factors?**
MPN555: **no family homolog outside Mollicutes**; fold homologs are *E. coli* **trigger factor** C-domain
and **SurA**, both chaperones. **No resemblance to omega/RpoZ, delta/RpoE, epsilon, YkzG/UPF0356, HelD,
Spx, CarD, RbpA, Gfh1, or DksA.** Novelty survives on this axis.
MPN266: **yes, it IS Spx.** *B. subtilis* **Spx (spxA, BSU11500)** and **MgsR (BSU24770)** are the named,
well-characterised homologs. Novelty dies on this axis.

**6. Essential, and by what evidence?**
Both **essential in both organisms**. Evidence: Lluch-Senar et al. 2015 transposon mutagenesis
(*M. pneumoniae*), Table S11 panel B, `E / E` for both; the *M. genitalium* column derives from
Glass et al. 2006. Independently for MPN266: Yus et al. 2019 state it outright.

---

## 6. The complication that is not a kill, and must not be dressed up as support

**Yus et al. 2019 classified MPN555 as NOT RNAP-associated.** Verbatim:

> "Other **non-RNAP-associated** proteins (e.g., MPN555) mimicked the RNAP profile, but with only a few
> peaks in promoters of highly expressed genes, likely to be **artifactual or phantom** (Jain et al.,
> 2015)."

So MPN555 was FLAG-tagged, ChIP-seq'd, produced an RNAP-like binding profile, and the authors concluded
the profile was an artifact. One year later O'Reilly's in-cell crosslinking put four links from MPN555 onto
RpoB and named it in the RNAP interaction set.

**How to use this honestly.** It is a real, citable tension in the literature, and it is the strongest
argument that MPN555-on-RNAP is still an open question rather than settled prior art. But it is also
**evidence against the interaction**, from the same consortium, from a targeted assay. It cannot be
presented only as "nobody had looked". Someone looked, with a direct method, and concluded it was not
there. Note also that O'Reilly validated **MPN530** by bacterial two-hybrid and **did not** do so for
MPN555, so MPN555's RNAP association rests on crosslinking MS alone.

Combined with section 1f (the same MPN555 lysines K45, K116 and K158 also crosslink to tuf, dhfr and
groEL), the honest reading is: **MPN555's RNAP crosslinks are published, unvalidated, contested by a
targeted assay, and share lysines with abundant-cytosolic-protein links, in a protein whose published
structure has a promiscuous peptide-binding groove.**

---

## 7. VERDICT and exactly what must change in the write-up

### MPN_266 / MG_127: **ALREADY PUBLISHED**

Required changes, all of them mandatory:

1. **Stop calling it MPN266 or "uncharacterized". Call it SpxA (MPN_266 / MG_127).**
2. **Delete the claim that O'Reilly's sentence does not name it.** It does, as SpxA. Correct the
   `PREREG_OMEGAREGION.md` section 0 heading "It also recovers THREE uncharacterized proteins, not two"
   and the `RESULT_OMEGAREGION.md` section 2 table and the sentence "**MPN_266 is not named in O'Reilly's
   sentence.**" There are **two** uncharacterized RNAP partners, exactly as O'Reilly wrote. The third hit
   is a known factor whose UniProt RecName is stale.
3. **Name the root cause:** the repo's `omega/mg_protein_names.json` uses UniProt RecNames, and UniProt
   still calls P75509 "Uncharacterized protein MG127 homolog" while annotating it into the Spx/MgsR family
   on the same record. RefSeq, KEGG, InterPro, Lluch-Senar, Yus and O'Reilly's own data files all name it
   SpxA. **This is a reusable lesson for the project's whole pipeline: a UniProt RecName is not an
   annotation state.** Any future "uncharacterized protein" hit must be re-checked against RefSeq, KEGG
   and InterPro before the word "uncharacterized" is used.
4. **Report the omega-proximity number for SpxA as a recovery at best, and disclose the selection.**
   The published crosslinks put SpxA on the alphaCTD and sigma-A, the published binding mode. The
   project's single-site reading kept the one rpoB link and dropped the six links pointing at the known
   site. Say that in the open.
5. Registered reading 3 in the prereg already forbids treating MPN266 as a claim. **That was the right
   call and it saved the project.** Say so; it is the process working.

### MPN_555 / MG_377: **PARTLY PUBLISHED**

The RNAP association is published prior art. The **site** is not. Required changes:

1. **Retract any framing of "MPN555 interacts with RNA polymerase" as new.** O'Reilly 2020 published it,
   named it in the main text, and **the four crosslinks the project uses are their own released data.**
   Same correction `RETRACTION_MG354_NOVELTY.md` applies to MG354.
2. **Retract "uncharacterized" and "nobody here had touched it" as a novelty argument.** Correct
   `RESULT_OMEGAREGION.md` section 4. MPN555 has: a 2005 crystal structure with a peer-reviewed paper
   (1ZXJ / PMID 16204885), its own InterPro family (IPR054820) and NCBIfam (NF045756), a 2006 JBC paper
   naming it as a trigger-factor-C-module protein, and a **2026 identification as an essential truncated
   trigger factor with a predicted SecA role (Todor et al., the project's own data source)**.
   "Uncharacterized" here means uncharacterized in *function*, and even that is now contested.
3. **Cite the Yus 2019 "non-RNAP-associated" sentence.** Not citing a direct, targeted negative result on
   the exact claim would be the kind of omission that sinks a submission. Section 6 above gives the
   framing.
4. **Cite the shared-lysine problem** (section 1f). K45, K116, K158 each crosslink to both RNAP and an
   abundant cytosolic protein. The "convergent hub" argument in `RESULT_OMEGAREGION.md` section 1 needs
   this stated next to it.
5. **Reframe the claim to what is actually unpublished, and it is a decent claim:**
   *the residue-level location of the MPN555-RpoB contact.* Specifically: **published crosslinks converge
   from three MPN555 lysines onto RpoB K1319, and that position maps to the same beta-subunit region
   across two RNAP conformations 26 A apart.** That is new, it is small, it names a testable residue, and
   O'Reilly's own bacterial two-hybrid is the existing assay. Frame the rest as **method validation on a
   published interaction**, which is what it is.
6. **Drop "omega region" as the primary framing** (section 3): *M. pneumoniae* RNAP has no omega subunit.
   Say "the beta-subunit region that omega occupies in *B. subtilis*", or better, just name RpoB K1319 and
   K1269.
7. **Add the published-context sentence that makes the finding interesting rather than thin:**
   a protein whose only published structure is a chaperone-like peptide-binding groove, and which is now
   called an essential truncated trigger factor with a predicted SecA role, crosslinks to a specific site
   on RNAP beta. Chaperone-at-RNAP is a real hypothesis (cf. HelD, and trigger factor's own
   ribosome-adjacent role), and it is not in the literature for this protein. **That** is the honest
   novelty, and it is more interesting than "an uncharacterized protein binds RNAP".

### One thing the project should not lose

**The prior-art check worked this time.** The prereg bound the claim to this check, the check ran before
anything was published, and it caught a full kill on one of the two proteins and a major reframing on the
other. `MG354` cost weeks because the check ran last. This one cost hours because it ran in the right
order.

---

## 8. Full citation list

1. Himmelreich R., Hilbert H., Plagens H., Pirkl E., Li B.-C., Herrmann R. (1996) "Complete sequence analysis of the genome of the bacterium Mycoplasma pneumoniae." *Nucleic Acids Res* 24(22):4420-4449. DOI 10.1093/nar/24.22.4420. PMID 8948633.
2. Newberry K.J., Nakano S., Zuber P., Brennan R.G. (2005) "Crystal structure of the Bacillus subtilis anti-alpha, global transcriptional regulator, Spx, in complex with the alpha C-terminal domain of RNA polymerase." *PNAS* 102:15839. DOI 10.1073/pnas.0506592102. **PDB 1Z3E.**
3. **Schulze-Gahmen U., Aono S., Chen S., Yokota H., Kim R., Kim S.-H. (2005) "Structure of the hypothetical Mycoplasma protein MPN555 suggests a chaperone function." *Acta Crystallogr D* 61(Pt 10):1343-1347. DOI 10.1107/S090744490502264X. PMID 16204885. PDB 1ZXJ.**
4. Glass J.I., Assad-Garcia N., Alperovich N., Yooseph S., Lewis M.R., Maruf M., Hutchison C.A. 3rd, Smith H.O., Venter J.C. (2006) "Essential genes of a minimal bacterium." *PNAS* 103(2):425-430. (Cited second-hand via refs 8 and 12.)
5. Merz F., Hoffmann A., Rutkowska A., Zachmann-Brand B., Bukau B., Deuerling E. (2006) "The C-terminal domain of Escherichia coli trigger factor represents the central module of its chaperone activity." *J Biol Chem* 281(42):31963-31971. DOI 10.1074/jbc.M605164200. PMID 16926148.
6. Lamour V., Westblade L.F., Campbell E.A., Darst S.A. (2009) "Crystal structure of the in vivo-assembled Bacillus subtilis Spx/RNA polymerase alpha subunit C-terminal domain complex." *J Struct Biol* 168:352-356. DOI 10.1016/j.jsb.2009.07.001. PMID 19580872. PMC2757488. **PDB 3GFK.**
7. Kuhner S., van Noort V., Betts M.J., Leo-Macias A., Batisse C., Rode M., Yamada T., Maier T., et al. (2009) "Proteome organization in a genome-reduced bacterium." *Science* 326(5957):1235-1240. DOI 10.1126/science.1176343. PMID 19965468.
8. Nakano M.M., Lin A., Zuber C.S., Newberry K.J., Brennan R.G., Zuber P. (2010) "Promoter recognition by a complex of Spx and the C-terminal domain of the RNA polymerase alpha subunit." *PLoS ONE* 5:e8664. DOI 10.1371/journal.pone.0008664. **PDB 3IHQ.**
9. van Noort V., Seebacher J., Bader S., Mohammed S., Vonkova I., Betts M.J., Kuhner S., Kumar R., Maier T., O'Flaherty M., et al. (2012) "Cross-talk between phosphorylation and lysine acetylation in a genome-reduced bacterium." *Mol Syst Biol* 8:571. DOI 10.1038/msb.2012.4. PMID 22373819.
10. Zhang W., Baseman J.B. (2014) "Functional characterization of osmotically inducible protein C (MG_427) from Mycoplasma genitalium." *J Bacteriol* 196:1012-1019. DOI 10.1128/JB.00954-13. PMID 24363346. PMC3957695.
11. **Lluch-Senar M., Delgado J., Chen W., Llorens-Rico V., O'Reilly F.J., Wodke J.A.H., Besray Unal E., Yus E., Martinez S., Nichols R.J., Ferrar T., et al. (2015) "Defining a minimal cell: essentiality of small ORFs and ncRNAs in a genome-reduced bacterium." *Mol Syst Biol* 11:780. DOI 10.15252/msb.20145558. PMID 25609650. PMC4332154.** (Essentiality E/E for both; Table S2 names MPN266 `spxA`.)
12. Trussart M., Yus E., Martinez S., Bau D., Tahara Y.O., Pengo T., Widjaja M., Kretschmer S., Swoger J., Djordjevic S., et al. (2017) "Defined chromosome structure in the genome-reduced bacterium Mycoplasma pneumoniae." *Nat Commun*. PMID 28272414. PMC5344976. (MPN266 appears in full text; not read in detail.)
13. **Yus E., Llorens-Rico V., Martinez S., Gallo C., Eilers H., Blotz C., Stulke J., Lluch-Senar M., Serrano L. (2019) "Determination of the Gene Regulatory Network of a Genome-Reduced Bacterium Highlights Alternative Regulation Independent of Transcription Factors." *Cell Systems* 9(2):143-158.e13. DOI 10.1016/j.cels.2019.07.001. PMID 31445891. PMC6721554.** (Names "SpxA, MPN266"; essential; RNAP-associated; classifies MPN555 as non-RNAP-associated.)
14. **O'Reilly F.J., Xue L., Graziadei A., Sinn L., Lenz S., Tegunov D., Blotz C., Singh N., Hagen W.J.H., Cramer P., Stulke J., Mahamid J., Rappsilber J. (2020) "In-cell architecture of an actively transcribing-translating expressome." *Science* 369(6503):554-557. DOI 10.1126/science.abb3758. PMID 32732422. PMC7115962.** (Names MPN555 and SpxA; the crosslink tables label P75509 `spxA`.)
15. Newing T.P., Oakley A.J., Miller M., Dawson C.J., Brown S.H.J., Bouwer J.C., Tolun G., Lewis P.J. (2020) "Molecular basis for RNA polymerase-dependent transcription complex recycling by the helicase-like motor protein HelD." *Nat Commun* 11:6420. (Template source for 6WVJ/6WVK; cited by the prereg.)
16. **Shi J., Li F., Wen A., Yu L., Wang L., Wang F., Jin Y., Jin S., Feng Y., Lin W. (2021) "Structural basis of transcription activation by the global regulator Spx." *Nucleic Acids Res* 49(18):10756-10769. DOI 10.1093/nar/gkab790. PMID 34530448. PMC8501982. PDB 7F75.** (Spx on the intact RNAP holoenzyme: alphaCTD + sigma-A.)
17. O'Reilly F.J. et al. (2023) *Mol Syst Biol* 19:e11544. (Crosslink-satisfaction rates, cited by `RESULT_OMEGAREGION.md`; not re-verified here.)
18. **Todor H. et al. (2026) "Predicting the protein interaction landscape of a free-living bacterium with pooled-AlphaFold3." *Molecular Systems Biology* 22(4):497-518. DOI 10.1038/s44320-026-00189-7. PMID 41559189. PMC13047044.** (MG_377/MPN555 = essential truncated trigger factor, predicted SecA partner; Spx in their RNAP figure.)

Database records retrieved live 2026-09-28: UniProt P75223, P75509, Q50295, P75454, P47373;
InterPro IPR054820, IPR006504, IPR011260; PDB 1ZXJ, 1Z3E, 3GFK, 3IHQ, 7F75; KEGG mpn:MPN_266,
mpn:MPN_555, ko:K03060, ko:K16509; RefSeq WP_010874623.1, WP_010874912.1; STRING v12 species 272634;
IntAct REST.

*Unaudited per G6. MycoWiki was unreachable and is an acknowledged gap.*
