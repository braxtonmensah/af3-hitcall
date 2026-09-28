# OMEGAREGION: the confirmatory test passes on all four registered conditions. MPN555 crosslinks to the omega region; MG354 is excluded from it

> # RETRACTED 2026-09-28, SAME DAY. DO NOT CITE THIS FILE.
> **See `RETRACTION_OMEGAREGION.md`.** Four things here are wrong:
> **(1) MPN266 is SpxA**, a known factor O'Reilly's main text names; its `Description` field in our own
> copy of their data literally reads `spxA`. **(2) MPN555 is not uncharacterized** - PDB 1ZXJ, InterPro
> IPR054820 "MPN555 chaperone-like", identified as an essential truncated trigger factor.
> **(3) There is no omega subunit in M. pneumoniae** (UniProt rpoZ, taxid 272634: 0 hits, with B. subtilis
> as a working positive control), so "omega region" is a label for a subunit that does not exist here.
> **(4) The "convergent hub" is promiscuity**: all three lysines reaching RpoB K1319 also reach EF-Tu
> and/or a transporter, and 3 of MPN555's 5 crosslinked lysines are promiscuous.
> Also: **Yus et al. 2019 explicitly call MPN555 non-RNAP-associated.**
> The geometric numbers and the 91.7% gate are real; the interpretation is withdrawn.



Run 2026-09-28. Registered in `PREREG_OMEGAREGION.md` at commit `b5fda68`, with the confirmatory template
and all four readings fixed **before the confirmatory ran**. Zero GPU.

**STATUS: NOT YET CLAIMABLE.** The pre-registration makes a prior-art kill check on MPN555 and MPN266
**binding before any claim**. That check is running. **If either protein's RNAP binding site is already
published, this is a recovery and must be framed as method validation**, exactly as
`RETRACTION_MG354_NOVELTY.md` now does for MG354.

---

## 0. The result

Gate first: the 20 RpoB-RpoC control crosslinks on 6WVK give **11 of 12 = 91.7%**, above the registered
70%, so the mapping is interpretable.

| protein | 6WVJ elongation complex | 6WVK HelD complex | difference | registered reading |
|---|---|---|---|---|
| **MPN555** (MG_377, 193 aa) | 34.3 A, null 67.3, **P = 0.021** | 34.6 A, null 69.0, **P = 0.025** | **0.3 A** | **reading 1: SUPPORTED** |
| MPN266 (MG_127, 145 aa) | 23.9 A, **P = 0.016** | 24.9 A, **P = 0.022** | 1.0 A | reading 3: **lead only, n = 1 site** |
| MG354 (MPN530, 136 aa) | 69.5 A, **P = 0.971** | 69.3 A, **P = 0.978** | 0.2 A | **reading 4: instrument stable** |

**All three reproduce to within 1 A across a 26 A conformational change.** HelD widens the primary channel
from 21 A to 47 A (Newing et al. *Nat Commun* 2020;11:6420), so this is the largest conformational
perturbation available in this organism's RNAP structures. **The partition is not a conformational
artefact.**

**Registered condition 4 is the one that makes the rest trustworthy:** MG354 had to stay farther than its
null, and it did (P = 0.978). The instrument therefore distinguishes "near omega" from "far from omega"
on the same structures in the same run, rather than calling everything near.

## 1. The convergent hub, which is what led here

From this project's own crosslink tables (`rnap_partner_links.json`):

    MPN555 K45  <-> RpoB K1319   [DSS]
    MPN555 K158 <-> RpoB K1319   [DSS]
    MPN555 K160 <-> RpoB K1319   [DSSO]
    MPN555 K116 <-> RpoB K1269   [DSS]
    MPN266 K139 <-> RpoB K1319   [DSS]
    MPN266 K139 <-> RpoB K1326   [DSS]

**Three separate MPN555 lysines and one MPN266 lysine all reach RpoB K1319, across both crosslinkers.**
Convergence from three different positions in one small protein onto one partner residue is not the
pattern of scattered false positives.

**The mapping validates at that exact residue:** RpoB K1319 maps to 6WVJ chain C 1108 and sits **22.1 A
from RpoC K10**, which is itself one of the 20 control crosslinks, so it is satisfied.

## 2. There are THREE uncharacterized RNAP partners, not two

Reconstructing the RNAP crosslink interactome from our own tables independently recovers O'Reilly et al.
Fig 1B: **SigA** (MG_249), **GreA** (MG_282), **NusG** (MG_054), **NusA** (MG_141), **RNAP delta / RpoE**
(MG_022), plus the core subunits.

It also returns **three** uncharacterized proteins where O'Reilly's sentence names two:

| M. genitalium | UniProt | M. pneumoniae | length | links to RNAP core |
|---|---|---|---|---|
| MG_354 | P75248 | MPN_530 | 136 aa | 5 |
| MG_377 | P75223 | **MPN_555** | 193 aa | 4, all to RpoB |
| MG_127 | P75509 | **MPN_266** | 145 aa | 6 (4 RpoA, 2 RpoB) |

**MPN_266 is not named in O'Reilly's sentence.** Whether it appears in their supplementary data, or fails
their essentiality filter, is part of the running kill check. **Do not describe it as unreported until
that returns.**

## 3. What this does NOT show

1. **"Near the omega region" is not "binds the omega site".** A 24-35 A centroid distance says the
   crosslinked beta-subunit residues lie in that region, not that the protein occupies omega's pocket.
   **Omega is present in both structures, so its pocket is occupied.**
2. **MPN266 rests on ONE mappable site.** The prereg explicitly forbids treating it as a claim, and its
   P = 0.016 / 0.022 is not dressed up here. It is a lead.
3. **MPN555 rests on 2 mappable sites from 4 crosslinks.** Small.
4. **Cross-species mapping** (Mycoplasma onto *B. subtilis*) carries alignment error. The 91.7% control
   gate is what makes it tolerable, and that gate is itself a coin-flip instrument at n = 12: published
   in-cell satisfaction runs 71-75% (O'Reilly et al. *Mol Syst Biol* 2023;19:e11544), so a 70% bar rejects
   a correct model about 20% of the time at this n.
5. **Nothing here measures function, stoichiometry, or essentiality.**
6. Unaudited per G6.

## 4. Why this is worth finishing

**MG354 cost weeks and its headline was already published.** MPN555 was named in the same sentence of the
same paper and **nobody here had touched it**; MPN266 was not named at all. Both fell out of one query
against data already on disk.

**The specific, testable thing this produces is a site: RpoB K1319.** O'Reilly's own bacterial two-hybrid
already exists as the assay format that validated MPN530, so a collaborator could mutate RpoB K1319 and
test both proteins with a method already published for this system. **That is the form a fundable claim
needs: a named residue, an existing assay, and a pre-registered replicate behind it.**
