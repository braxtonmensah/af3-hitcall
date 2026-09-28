# RETRACTION: `RESULT_OMEGAREGION.md` is withdrawn. MPN266 is SpxA, MPN555 is a known chaperone, there is no omega in Mycoplasma, and the "convergent hub" is promiscuity

Written 2026-09-28, the same day as the result it retracts, after the prior-art kill check that
`PREREG_OMEGAREGION.md` made **binding before any claim**. **Every correction below was verified by me
against local data or UniProt with a working positive control, not taken on report.**

**The pre-registration worked. The result did not survive it. That is the system functioning, not failing.**

---

## 1. RETRACTED: "MPN_266 is a third uncharacterized RNAP partner O'Reilly does not name"

**MPN266 / MG_127 / P75509 is SpxA**, and O'Reilly's main text names it explicitly, in the list of
**known** auxiliary factors: "SigA, GreA, NusG, NusA, **SpxA**, and RpoE".

**Verified in our own copy of their data.** In
`xlms2020*/Myco_InCell_{DSSO,DSS}_dataset_5link_5PPI_Links_*.csv`, accession **P75509 carries
`Description` = `spxA`** on all 30 matching rows. **The disproof was in the file the whole time.**

**Root cause, and it is a pipeline bug worth fixing:** I read protein names from
`omega/mg_protein_names.json`, which stores **UniProt RecNames**. UniProt still calls this record
"Uncharacterized protein MG127 homolog" while annotating **Spx/MgsR (IPR006504)** on the same entry.
**Prefer the source table's own annotation over a UniProt RecName.** Independent confirmations the check
found: Yus et al. 2019 (*Cell Systems* 9:143-158, PMID 31445891) name "SpxA, MPN266", ChIP-seq it, and
call it essential; RefSeq calls it "Spx/MgsR family RNA polymerase-binding regulatory protein"; KEGG
K16509; and **its binding site is already solved** on alphaCTD plus sigma-A (PDB 1Z3E, 3GFK, 3IHQ, and
7F75 on the intact holoenzyme). Its crosslinks go to RpoA **K266** and **K324**, and M. pneumoniae
alphaCTD is residues **258-320**. **Already published, at the published site.**

## 2. RETRACTED: "uncharacterized" for MPN555, and the novelty framing

**MPN555 / MG_377 / P75223 has a solved structure and a family.** PDB **1ZXJ** at 2.8 A, with a paper:
Schulze-Gahmen et al. 2005, *Acta Cryst D* 61:1343, PMID 16204885, which already "suggests a chaperone
function" from fold homology to *E. coli* trigger factor C-domain and SurA. **InterPro IPR054820,
"MPN555 chaperone-like"**; NCBIfam NF045756. Todor et al. 2026 (PMID 41559189, a data source this project
already uses) identify it as an **essential truncated trigger factor**, C-domain only, paralog of
full-length Tig, with a predicted SecA interaction.

So "uncharacterized" and "nobody had touched it" are both wrong, and `RESULT_OMEGAREGION.md` section 4 is
withdrawn.

## 3. RETRACTED: "omega region". Mycoplasma has no omega subunit

**Verified against UniProt with a positive control.** Searching taxid **272634** (*M. pneumoniae*) for
`gene:rpoZ` returns **0 hits**; for "RNA polymerase subunit omega" **0 hits**. The same query against
*B. subtilis* (224308) returns **O35011**. Todor et al. describe the enzyme as
alpha-alpha-beta-beta-prime-delta-sigmaA.

**So "distance to omega" was a coordinate label on a *B. subtilis* template for a subunit that does not
exist in the organism the crosslinks came from.** The measurement is still a real spatial fact about a
region of the beta subunit, but **it must be named by the residues, RpoB K1319 / K1269 / K1326, never by
omega.** The MG354 "not at the omega site" results (`RESULT_XLGEO2.md`, `RESULT_XLGEO3.md`) need the same
renaming; their numbers stand, their label does not.

## 4. RETRACTED, and this is the scientific core: the "convergent hub" is promiscuity

I argued that three MPN555 lysines reaching one RpoB residue "is not the pattern of scattered false
positives". **Measured against our own data, all three of those lysines are promiscuous:**

    MPN555 K45  -> RpoB K1319   AND  EF-Tu K57, EF-Tu K285
    MPN555 K158 -> RpoB K1319   AND  EF-Tu K57, EF-Tu K314, MG_119 K415
    MPN555 K160 -> RpoB K1319   AND  MG_119 K415
    MPN555 K6   -> GroEL K352
    MPN555 K116 -> RpoB K1269

**3 of MPN555's 5 crosslinked lysines reach more than one partner protein.** Its full inter-protein
partner list, FDR <= 0.05, is **rpoB 5 rows, EF-Tu 4, DHFR 3, MglA 2, GroEL 1, MG_119 1**. RpoB is 5 of
16 inter-protein link rows, not a dominant partner.

**So the convergence on RpoB K1319 is a property of MPN555's own exposed, reactive lysines, not evidence
of a specific RpoB interface.** That is exactly the behaviour expected of a trigger-factor-like chaperone
with a peptide-binding groove, which is what its published structure says it is.

**And there is a targeted published negative:** Yus et al. 2019 explicitly call MPN555
**non-RNAP-associated** and dismiss its RNAP-like ChIP profile as "artifactual or phantom" - from the same
consortium that produced the crosslinks. **Any future claim must cite and answer this.**

## 5. What actually survives

1. **MPN555 crosslinks to RpoB. That is O'Reilly's published observation, not ours.**
2. **Its binding site on RNAP is genuinely unpublished**: O'Reilly could not place it in the expressome
   density, and Todor et al. never co-folded it with RNAP.
3. **The geometric measurement is reproducible**: the mapped RpoB sites sit in one region, stable to within
   1 A across a 26 A conformational change (6WVJ elongation vs 6WVK HelD), with the control gate at 91.7%.
   **Reproducible is not the same as specific**, and section 4 shows it is not specific.
4. **The honest open question is now a different one, and better posed:** is MPN555 a chaperone that
   samples RpoB among other clients, or a dedicated RNAP factor? **Its partner spectrum favours the
   chaperone reading**, which is also what its fold, its Tig paralogy, and Yus 2019 all say.

## 6. What this cost, and the rule that would have prevented it

The whole MPN555 line took about an hour and produced no claim. **The prior-art check would have killed
MPN266 in one grep of a file already on disk** (`Description` = `spxA`), and would have killed
"uncharacterized" for MPN555 with one UniProt lookup.

**`research-throughput-rules` says run the kill check FIRST. I ran it second, again, on the same day I
wrote up having learned that lesson from MG354.** The prereg's binding clause is the only reason nothing
false was published.
