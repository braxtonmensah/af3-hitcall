# New biology hypothesis: Mycoplasma RNase J is an (RNase J1 : MG423)x2 heterotetramer

Status: **computational, supported by two independent in-cell datasets; not yet tested at the bench.**
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

## What is new and what is not

- **Known:** RNase J forms dimers and tetramers (for example 3ZQ4). *B. subtilis* RNase J1 and J2 form a
  heterocomplex (Mathy et al. 2010; integrative crosslink + deep-learning model, Stahl et al. 2024,
  *Nat. Commun.*, PDB-IHM 9A5V).
- **New here:** that *Mycoplasma* has a J1/J2-type RNase J heterocomplex at all, that its J2-type subunit
  is the uncharacterized MG423, and in-cell evidence for a heterotetrameric (J1:J2)x2 assembly. Not in
  Todor et al. 2026 (checked text and supplements), not in the literature (Europe PMC), no solved
  homologous heterocomplex in the current PDB.

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
