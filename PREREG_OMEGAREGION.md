# PREREG OMEGAREGION: do the OTHER two uncharacterized RNAP partners sit at the omega region, where MG354 does not?

Written 2026-09-28. **Sections 1 and 2 are EXPLORATORY and were computed before this document existed.
Section 3 is the confirmatory test and is registered BEFORE it runs.** That split is the whole point of
this file and is stated first so nothing here can be presented as confirmatory later.

## 0. How this was found, stated plainly

While working up MPN555 I extracted, from this project's own crosslink tables, **every protein that
crosslinks to an RNA polymerase core subunit**. That recovers O'Reilly et al. 2020 Fig 1B independently:
SigA (MG_249), GreA (MG_282), NusG (MG_054), NusA (MG_141), RNAP delta / RpoE (MG_022), plus the core
subunits.

**It also recovers THREE uncharacterized proteins, not two.** O'Reilly's text names two
("MPN555 and MPN530"):

| M. genitalium | UniProt | M. pneumoniae | length | links to RNAP core |
|---|---|---|---|---|
| MG_354 | P75248 | **MPN_530** | 136 aa | 5 |
| MG_377 | P75223 | **MPN_555** | 193 aa | 4, all to RpoB |
| MG_127 | P75509 | **MPN_266** | 145 aa | 6 (4 to RpoA, 2 to RpoB) |

**MPN_266 / MG_127 is a third uncharacterized RNAP-crosslinked protein that O'Reilly's sentence does not
name.** Whether their supplementary data contains it, or whether it fails their essentiality filter, is
**not yet checked** and is a required kill check before any claim.

## 1. EXPLORATORY observation A: a convergent hub at RpoB K1319

Residue-level links, from `rnap_partner_links.json`:

    MPN555 K45  <-> RpoB K1319   [DSS]
    MPN555 K158 <-> RpoB K1319   [DSS]
    MPN555 K160 <-> RpoB K1319   [DSSO]
    MPN555 K116 <-> RpoB K1269   [DSS]
    MPN266 K139 <-> RpoB K1319   [DSS]
    MPN266 K139 <-> RpoB K1326   [DSS]

**Three different MPN555 lysines and one MPN266 lysine all reach RpoB K1319**, across both crosslinkers.
RpoB K1319 also appears in the control set crosslinking to RpoC K10.

**Mapping validates at that exact residue:** on 6WVJ, RpoB K1319 maps to chain C 1108 and sits **22.1 A
from RpoC K10**, satisfying that control crosslink.

## 2. EXPLORATORY observation B: the three partners split on omega proximity

6WVJ (*B. subtilis* elongation complex, no HelD), omega = chain F, null = same number of sites drawn from
the same chains, 2,000 draws:

| protein | n mapped sites | observed | null median | P(null <= obs) | reading |
|---|---|---|---|---|---|
| **MPN555** | 2 | **34.3 A** | 67.3 A | **0.021** | closer than null |
| **MPN266** | 1 | **23.9 A** | 72.1 A | **0.016** | closer than null |
| MPN530 (MG354) | 3 | 69.5 A | 47.4 A | 0.971 | farther than null |

**So the omega-region hypothesis that died for MG354 is alive for the two proteins nobody here has
studied**, and MG354's exclusion from that region is not a property shared by all three.

**These numbers are EXPLORATORY. They were computed before this file was written, on data chosen after
looking. They may not be quoted as a confirmed result.**

## 3. THE CONFIRMATORY TEST, registered before it runs

**Replicate on 6WVK**, the *B. subtilis* RNAP-HelD complex: same organism and lab, but a **radically
different conformation** (primary channel widened from 21 A to 47 A, Newing et al. *Nat Commun*
2020;11:6420). This is the same held-out design that validated the MG354 result, where the omega distance
reproduced to within 0.2 A across the two states.

**Registered predictions, written now:**

1. **MPN555 stays CLOSER than its null (P < 0.05) on 6WVK: SUPPORTED as a conformation-independent
   observation.**
2. **MPN555 becomes indistinguishable or farther: NOT SUPPORTED**, and the exploratory result is reported
   as conformation-dependent and set aside. **I do not then go looking for a third template.**
3. **MPN266 is reported but NOT tested as a claim**, because it rests on **one** mapped site. One site has
   no internal replication and I will not dress it up. It is listed as a lead only.
4. **MG354 must stay FARTHER than null** on 6WVK, which it already did (P = 0.994). If it does not, the
   instrument is unstable and **neither MPN555 nor MG354 may be reported.**

**Also required, and binding:** a **prior-art kill check on MPN555 and MPN266 before any further compute**.
If either protein's RNAP association or binding site is already published, the finding is a recovery and
must be framed as method validation, exactly as `RETRACTION_MG354_NOVELTY.md` now does for MG354.

## 4. What this could NOT show, whatever the numbers

- **Proximity to omega's centroid is not "binds the omega site".** A 24-34 A centroid distance means the
  crosslinked residues lie in that region of the beta subunit, not that the protein occupies omega's
  pocket. Omega is present in these structures, so its pocket is occupied.
- **n is tiny**: 4 links for MPN555, 6 for MPN266, and 1-2 mappable sites after cross-species mapping.
- **Cross-species mapping error is real** (Mycoplasma onto *B. subtilis*), which is why the gate on the 20
  RpoB-RpoC control crosslinks must pass on each template before anything else is read.
- Nothing here measures function, stoichiometry, or essentiality.
- Unaudited per G6.
