# RETRACTION: the MG354 / RNA polymerase interaction is ALREADY PUBLISHED, in the paper our own crosslinks came from

Written 2026-09-28 after a prior-art kill check that should have been run before any compute.

## 0. The finding

**O'Reilly et al. 2020, *Science* 369(6503):554-557, DOI 10.1126/science.abb3758, PMID 32732422.**
Verified verbatim by me from the NCBI PMC XML (PMC7115962), not from a search snippet:

> "The *M. pneumoniae* RNAP core consisting of the conserved subunits alpha, beta and beta', was found to
> interact with the known auxiliary factors SigA, GreA, NusG, NusA, SpxA, and RpoE (firmicute-specific
> RNAP delta subunit) (20) (Fig. 1B). **Additionally, two uncharacterized essential proteins, MPN555 and
> MPN530 (21), were found and the interaction of MPN530 with beta/beta' subunits was independently
> validated by a bacterial two-hybrid screen (fig. S4).**"

MPN530 is the *M. pneumoniae* ortholog of MG354. beta/beta' are RpoB/RpoC.

**So the interaction is (a) published, (b) published in the SAME paper that produced the crosslinks this
project analysed, and (c) independently validated by an orthogonal method we did not use.**

## 1. What must be retracted

**Any framing of the form "we found/discovered that MG354 binds RNA polymerase" is retracted.** That
includes the title of `new_biology/MG354_RNAP.md` as a discovery claim, and the phrase in
`RESULT_HIGHER`-lineage files that the signature "finds MG354 on RNA polymerase" **as though the finding
were new**. The signature did recover it; it was not new.

**The correct framing:** *a blind method recovered a published, orthogonally validated interaction.*
That is a **method-validation** result, and it is a perfectly good one. It is not a discovery.

## 2. What was NOT known, and still is not

From the same paper: O'Reilly et al. **could not place MPN530 in the elongating expressome density.**
Neither "MG354" nor "1TM9" appears anywhere in their text, so **the solved structure (PDB 1TM9, Pelton et
al. 2005, *Proteins* 61:666-668, PMID 16184596) and the interaction have never been connected in print.**

Genuinely open:
1. **Where** on RpoB/RpoC it binds.
2. Whether the *M. genitalium* ortholog behaves like the *pneumoniae* one (published evidence is
   *pneumoniae* only).
3. Any functional consequence.
4. Family: **Pfam PF09188 (DUF1951)**, InterPro IPR015271 / IPR035947, Gene3D 1.10.3960.10,
   SUPFAM SSF110009. No GO terms. So it has a named domain family, and "uncharacterized" means
   uncharacterized in *function*, not unplaced in family or structure.

## 3. A SECOND error, and it is mine: RNAP3 had already run

`STATE.md`, `cleanroom/rnap3/RUN.md`, and the project memory all describe RNAP3 as "the only outstanding
test". **It is not. It ran on 2026-09-25 on AlphaFold Server** and is recorded as SUPPORTED in
`new_biology/MG354_RNAP.md` (4 of 5 crosslinks within reach, RpoB-RpoC control 0.95, chain-pair
ipTM 0.910), commit `de313f4`.

**The repo's own audit already caught this** (`cleanroom/AUDIT_PUBLIC.md` C-3: "STATE.md:224-232 calls
RNAP3 'The only outstanding test'. RNAP3 has run and is SUPPORTED"). **I read STATE.md and the memory and
did not read the audit**, and spent a long session re-running it. **Read AUDIT_PUBLIC.md before trusting
STATE.md.**

## 4. A real observation that falls out of re-reading the old result

The RNAP3 model satisfied **0.95** of the RpoB-RpoC control crosslinks.

**Today's XLGEO work measured the same control crosslinks against REAL SOLVED STRUCTURES:**

| structure | control crosslinks satisfied |
|---|---|
| *E. coli* 4YG2 crystal | 11 of 17 = **64.7%** |
| *B. subtilis* 6WVK | 11 of 12 = **91.7%** |
| **AlphaFold Server RNAP3 model** | **0.95** |

**The model satisfies the in-cell crosslinks BETTER than real crystal structures of the same complex
do.** That is not automatically wrong, but it is the wrong direction for comfort: a predicted model that
explains noisy in-cell restraints better than crystallography of the real machine is a candidate for
being too compact, or for having been pulled toward satisfying them. **This deserves a registered check
before the 0.95 is quoted again**, and it is the strongest reason to finish the independent Boltz-2
replicate now running on Quartz, which is a different engine with no shared failure mode.

## 5. Status of claims

- **RETRACTED:** MG354-RNAP as a discovery.
- **STANDS, and is worth more than people think:** the HIGHER signature blind-recovered a published,
  two-hybrid-validated interaction. That is method validation against ground truth.
- **STANDS:** omega is dead by fold (`PREREG_OMEGA`) and by site (`RESULT_XLGEO2.md`, P = 0.994 wrong
  direction). YkzG is dead by fold (`RESULT_UPF0356_REFUTED.md`, TM 0.373 vs a 0.333 null).
- **OPEN:** where MG354 binds, and whether 0.95 is too good.
