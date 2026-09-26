# Target expansion for the compound screen

Written 2026-09-25. Question: which additional targets should this project stand up a small-molecule
screen against, and in what order.

**Status: analysis, not a claim.** Nothing here is pre-registered. The pocket numbers below are from a
scan I ran for this document (method and calibration in the next section); the literature checks are
cited. No screen has run yet, on any target, so every statement about what a screen would find is a
prediction.

---

## Bottom line

**Do not stand up a second organism or a second complex yet.** Two cheaper things come first, and both
live inside the target you already have.

1. **The receptor chain is probably the wrong one.** `vscreen.py` sets `TARGET_ACC = "P75497"` and
   constrains ligands to RNase J's interface residues. A buried-cavity scan of the AF3 model says the
   RNase J side of that interface has **no small-molecule pocket**: the largest non-catalytic cavity
   touching the interface is **26 A^3**, against **76 A^3** for MDM2:p53 and **575 A^3** for
   KEAP1:p62 measured the same way, and **0 A^3** for a flat bZIP coiled coil. The only real cavity on
   that side (1,262 A^3) is the **catalytic cleft**, 2.9 to 3.0 A from H83, D85 and H377. The partner,
   MPN621 (P75174), carries a **273 A^3 non-catalytic cavity** at the same interface (419 and 470 A^3
   in the independent *M. genitalium* ortholog model). MPN621 is also the subunit with the stronger
   essentiality evidence and the one that has lost 4 of 4 catalytic residues, so it is the more
   selective side as well.
2. **The screen has a null but no positive control.** It has a decoy arm and a CPSF73 off-target arm,
   and neither one can tell you whether the ranking works. The published evaluation of Boltz-2 reports
   "complete absence of correlation on top-100 compounds" and affinity predictions "largely independent
   of the final ligand pose" on the two targets it examined, and it examined no protein-protein
   interfaces at all. A screen whose instrument has not been shown to rank a known binder correctly
   produces a shortlist you cannot spend $650 to $1,800 on.

**Single recommendation for the next target to stand up: MPN621 (P75174) as the receptor chain, run in
the same batch as a three-interface positive-control panel drawn from this project's own
`drugged_unsolved_interfaces.csv`.** Marginal cost is about $3 of GPU and one MSA. No new organism, no
new prior-art exposure, no new biology to defend.

**Confidence: moderate-high (about 0.75) that this ordering is right; high (about 0.9) that standing up
a new organism before the positive control returns is premature.** The pocket asymmetry between the two
chains reproduces across two independent AF3 models of two orthologs, which is why I am fairly confident
in it; it is still two models of the same complex and no experimental structure exists.

**If and only if the positive-control panel passes**, the first genuinely new complex worth standing up
is the ***H. pylori* RNase J C-terminal-domain self-interface** (shortlist #3). It is the only candidate
I found with an experimental structure of the interface, a druggable-sized non-catalytic cavity in it, a
documented functional switch at that cavity, an essential gene, and no prior inhibitor work.

---

## How the pocket numbers were produced, and what they are worth

Script: `cleanroom/iface_pocket.py`, written for this analysis and left in the repo so the numbers can be
re-run. It needs only Biopython and scipy, both already in the 3.11 stack. For a
chain pair it computes buried surface area with Biopython's Shrake-Rupley, then **removes the partner**
and runs a LIGSITE-style grid scan over the remaining chain (1.0 A grid, 1.4 A probe, protein required
within 10 A along at least 5 of 7 directions), clusters the pocket points, and keeps clusters within
4 A of the interface residues. Removing the partner is the point: the question is whether the surface
the partner covers is a groove a compound could occupy, not whether there is leftover void in the
complex.

Calibration, same method, same parameters:

| Reference | BSA total | Pocket at interface |
|---|---|---|
| KEAP1 Kelch : p62 (3ADE), a classic drugged PPI pocket | 814 A^2 | **575 A^3** |
| MDM2 : p53 (1YCR), a shallow but successfully drugged groove | 1,450 A^2 | **76 A^3** |
| c-Fos : c-Jun bZIP (1FOS chains E,F), a flat coiled coil | 2,352 A^2 | **0 A^3** |

**Limits, stated before the numbers are used.** This is not fpocket, SiteMap or FTMap. Absolute volumes
are conformation- and resolution-sensitive: the same H. pylori catalytic cleft measures 415 A^3 in the
2.75 A crystal and 5,463 A^3 in the 4.1 A cryo-EM structure, a 13-fold spread. Only large qualitative
differences should be read, and the three references above are the scale. A large BSA with no pocket
(1FOS) is the signature of an undruggable PPI and is the single most useful thing the scan reports.

Cost model throughout: the repo's own 30 to 60 s per compound with a cached MSA, at RunPod's $0.34/hr
RTX 4090 from `COSTS.md`. The current job set is 650 YAMLs (300 screen, 50 decoy, 300 off-target), which
is 5.4 to 10.8 h, so **$2 to $4 per target-arm-set**. One caveat the repo does not state: those figures
are for a **single-chain** receptor of about 570 residues. A two-chain receptor of about 1,130 residues
is not 30 to 60 s per compound; budget 2 to 4x, so $7 to $15. The full 3,273-compound approved library
on one arm is 27 to 55 h, $9 to $19.

---

## Ranked shortlist

Seven candidate screens. Only the top three are things I would actually spend a cycle on now.

| # | Candidate | 1. Structure / model confidence | 2. Ligandable? | 3. Tool compound / positive control | 4. Biology worth it? | 5. GPU cost | 6. Prior art |
|---|---|---|---|---|---|---|---|
| **1** | **MPN621 (P75174) as receptor, RNase J : MPN621 interface, *M. pneumoniae*** | AF3 model, ipTM 0.83-0.84 for the 2:2, 0.81-0.82 for the J:partner pair. No experimental structure of this complex in any organism | **Yes, modestly.** 273 A^3 non-catalytic cavity at the interface (491 A^3 vestigial active-site cleft separately); 419 and 470 A^3 in the *M. genitalium* ortholog model. Between the MDM2 and KEAP1 references | **None direct.** JTE-607 binds human CPSF73, the nearest human relative, same MBL/beta-CASP fold, co-crystal published. Fold-level control only | MPN621 essential in *M. pneumoniae* (0 insertions both thresholds, plus colony isolation). Organism is a real and rising clinical problem but is on no funder's priority list | **~$3** for 300+50+300 jobs, plus one MSA. ~$10 if both chains are in the receptor | **None.** No RNase J inhibitor of any kind found in the literature, for any organism |
| **2** | **In-registry positive-control panel: KEAP1-SQSTM1, MTA1/2/3-RBBP4/7, NFE2L2-MAFG** | All three are in `drugged_unsolved_interfaces.csv` (pDockQ 0.373, 0.619-0.658, and the TARGETS.md entry at 0.70). Experimental structures exist for all three, which is the point | KEAP1 Kelch 575 A^3 (measured); RBBP4 top pocket published; MAFG-NRF2 bZIP is flat | **Yes, that is why they are here.** KEAP1: dozens of Kelch co-crystals (6ZF0, 6ZF1, 9F2Q, K67/4ZY3). RBBP4: small-molecule top-pocket antagonists and bicyclic peptide inhibitors of the RbAp48-MTA1 interaction. NRF2: ML385 | Not a drug hunt. This is the instrument check the project's own standards require | **~$4** for 3 receptors x (50 knowns + 100 shared decoys) | Extensive, deliberately. A benchmark needs prior art |
| **3** | ***H. pylori* RNase J CTD self-interface (P56185)** | **Experimental.** 7PCR crystal 2.75 A, 8CGL cryo-EM 4.1 A, dimer-of-dimers. No model needed | **Best of any candidate.** 679 A^3 non-catalytic cavity at the dimer interface, 42 A from the catalytic site, 5.7 A from K649. Present in both structures independently (321 + 145 A^3 in the crystal) and in both protomers | **None direct.** Same JTE-607/CPSF73 fold-level control. K649Q vs K649R is a genetic positive control for the mechanism: it stabilises the tetramer and raises exo activity 2.5-4x | RNase J is **essential** in *H. pylori*. Group I carcinogen, very high global prevalence. But clarithromycin-resistant *H. pylori* was **removed** from the WHO BPPL in the 2024 update | **~$4**, receptor is one 553-residue chain from a deposited structure | **None found.** The 2023 Nat Commun structure paper contains no drug-target discussion at all |
| **4** | ***M. pneumoniae* RNase J catalytic site (P75497), with the CPSF73 arm used as a real selectivity test** | Same AF3 model, plus a 39.9%-identity template (3ZQ4) | **Yes, 1,262 A^3.** It is the only genuine pocket in the incumbent system | **Yes, the strongest available.** JTE-607 binds the equivalent site in CPSF73, which is already wired as the off-target arm. Note it is not approved, so it is **not** in a `max_phase=4` library and must be added by hand | Same organism as #1. RNase J (MPN280) is essential | **~$3**, arms already written | **None** for bacterial RNase J. The human counterpart site is worked (JTE-607, YT-II-100) |
| **5** | ***S. pyogenes* RNase J1 : J2 interface** | **None.** No structure, no model. Nearest precedent is *B. subtilis* J1 (3ZQ4), *S. epidermidis* J1 and J2, and the crosslink+DL integrative model of the *B. subtilis* J1-J2 pair (PDB-IHM 9A5V) | **Unknown, and the prior is bad.** Every catalytic-subunit RNase J interface measured here has no pocket | Same fold-level JTE-607 control only | **Best pathogen fit of the bacterial set.** Both rnjA and rnjB are essential in GAS, and macrolide-resistant Group A *Streptococcus* is on the **WHO BPPL 2024, medium tier** | Model first (1 Boltz job, ~1,100 residues, $1-2, or free on AF Server with non-commercial output), then ~$10 | **None found** |
| **6** | **The RNase J : RNase J and MPN621 : MPN621 sub-interfaces of the same tetramer** | Same AF3 model. BSA 989 and 862 A^2 per side, small enough to be plausible PPI targets | **Weak.** 111 and 107 A^3 at the partner:partner contact; the J:J contact's apparent cavity is the catalytic cleft again | Same as #1 | Same as #1. Disrupting the dimer-of-dimers is a different mechanism from disrupting the heterodimer | **$0 extra** if run as extra pocket constraints in the #1 batch | None |
| **7** | **MG354 : RpoB / RpoC, *Mycoplasma*** | **Weak.** The 0.910 chain-pair ipTM in `MG354_RNAP.md` is the **RpoB-RpoC control**, not MG354. MG354's own ipTM is 0.57 / 0.43 in the samples that satisfy 4 of 5 crosslinks, and 0.17 / 0.15 in the two that do not. No model file is in the repo | **Unknown.** Not measurable: no coordinates to scan | Bacterial RNAP has excellent tool compounds (rifampicin, myxopyronin, corallopyronin, fidaxomicin at the switch region), but none of them binds where MG354 binds | MG354 is uncharacterised in function; no essentiality data cited in the repo. Solved alone as PDB 1TM9 | n/a | RNAP inhibitor space is crowded; this specific site is not |

---

## Per-target detail

### 1. MPN621 (P75174) as the receptor chain

**What the measurement says.** On the *M. pneumoniae* AF3 2:2 model (`rnasej_mpn_2x2_AF3_model_0.cif`),
the RNase J : MPN621 interface buries 4,941 A^2 total, 2,470 A^2 per side, 61 + 69 interface residues,
46% apolar. That is a very large interface, and large interfaces with no pocket are the classic
undruggable case (compare the 1FOS reference: 1,176 A^2 per side, 0 A^3).

Cavity clusters touching the interface:

| Chain | Cluster | Nearest catalytic position | Reading |
|---|---|---|---|
| RNase J (A) | **1,262 A^3** | 3.0 A to H83, 2.9 A to D85, 3.0 A to H377 | the catalytic cleft |
| RNase J (A) | 26, 24 A^3 | 15 to 20 A | the actual PPI surface, and it is flat |
| MPN621 (C) | **491 A^3** | 2.9 to 3.1 A to V71, E73, N74, N365 | the **vestigial** active-site cleft |
| MPN621 (C) | **273 A^3** | 10 to 18 A | a real non-catalytic pocket at the interface |

Cross-check on the independent *M. genitalium* ortholog model (`rnasej_mg_2x2_AF3_model_0.cif`): MG139
gives one large cavity (1,155 A^3, catalytic by analogy, not separately verified) and then nothing above
30 A^3; MG423 gives 470 and 419 A^3. The asymmetry holds in both orthologs.

**Why this matters more than it first looks.** Three things line up on MPN621 and none of them line up
on RNase J:

- It is the side with a pocket.
- It is the side with **0 of 4** catalytic residues conserved against *B. subtilis* RNase J1, while
  human CPSF73 keeps **3 of 4**. Selectivity against the nearest human relative is structurally easiest
  on the dead subunit.
- It is the side with the stronger essentiality evidence: Lluch-Senar 2015 Table S2 gives MPN621 zero
  transposon insertions at both thresholds **plus** confirmation by colony isolation, which MPN280 does
  not have.

**The current job files are aimed at the flat side, and the constraint makes it worse.**
`vscreen.py:161` passes `pocket[:20]`, which is a numeric truncation of the 65 interface residues, not a
spatial cluster. I measured it: the 20 residues actually used sit a median of **15.0 A** from the
catalytic site; the 45 that are dropped sit a median of **33.2 A** away. So the constraint, by accident,
steers ligands toward the catalytic-proximal half of an interface whose only cavity is the catalytic
cleft. The likely outcomes are that the screen finds nothing, or that it finds active-site binders and
mislabels them interface binders, which carries exactly the human off-target liability the design was
built to avoid.

**What standing it up costs.** One MSA (`fetch_msa.py` for P75174; `cleanroom/msa/` currently holds only
P75497 and Q9UKF6), one interface-residue list for the MPN621 side (already in
`rnasej/results_interface.json` under `MG423_MPN621`), and about 650 jobs. $3, or about $10 if you put
both chains in the receptor, which would be the better experiment and which I would do.

**Prior art: none.** No RNase J inhibitor exists for any organism, by any method, as far as I can find.
Bacterial RNase E, RNase P and RnpA have all been screened; RNase J has not. A 2024 editorial in the TB
literature proposes RNase J as a target and explicitly reports that no compounds have been identified.
Sources: [RNase E inhibitors](https://www.nature.com/articles/srep08028),
[RnpA inhibitors](https://journals.plos.org/plospathogens/article?id=10.1371/journal.ppat.1001287),
[RNase J TB editorial](https://pmc.ncbi.nlm.nih.gov/articles/PMC11060219/).

### 2. The in-registry positive-control panel

Not a drug hunt. The purpose is to answer one question before any shortlist is trusted: **can this
pipeline rank a known binder above its own decoys?**

Three interfaces, all already in this project's `drugged_unsolved_interfaces.csv` or `TARGETS.md`, so
the file formats, the registry provenance and the pDockQ values all come from the repo:

| Interface | Known binder to use | What a pass looks like |
|---|---|---|
| KEAP1 - SQSTM1 (pDockQ 0.373) | KEAP1 Kelch-domain PPI inhibitors; many co-crystals, e.g. 6ZF0, 6ZF1, 9F2Q, K67 (4ZY3) | the knowns beat every decoy |
| MTA1/2/3 - RBBP4/7 (pDockQ 0.619 to 0.658) | published small-molecule antagonists of the RBBP4 top pocket; bicyclic peptide inhibitors of the RbAp48-MTA1 interaction | the knowns beat every decoy |
| NFE2L2 - MAFG (pDockQ 0.70) | ML385, which binds the NRF2 Neh1 CNC-bZIP | the hardest of the three; a fail here is informative, not disqualifying |

This is worth doing **because the repo's own standards demand it.** Every other claim in this project is
gated against a null and a control. The screen is the one place where the instrument itself has never
been checked. The external evidence makes that gap concrete: the independent evaluation of Boltz-2
reports weak global correlation (r = 0.24 and 0.45 on its two targets), **no** correlation on the top
100 compounds, predictions clustered in a narrow -5 to -8 kcal/mol band, affinity "largely independent of
the final ligand pose", and it evaluated **no protein-protein interfaces and no out-of-distribution
targets**. Boltz-2's own paper reports strong CASP16 affinity results, so the picture is mixed, which is
precisely the situation where you run your own control.
Sources: [Boltz-2](https://www.biorxiv.org/content/10.1101/2025.06.14.659707v1),
[independent evaluation](https://arxiv.org/html/2603.05532v1),
[RBBP4 antagonists](https://www.biorxiv.org/content/10.1101/2022.01.05.475077v1.full.pdf),
[RbAp48-MTA1 bicyclic peptides](https://onlinelibrary.wiley.com/doi/10.1002/anie.202009749),
[ML385](https://pubs.acs.org/doi/10.1021/acschembio.6b00651).

**Pre-register the gate before running it**, in the repo's usual form: state the pass criterion, the
decoy set and the number of knowns in a `PREREG_VSCREEN.md` committed first. Otherwise the panel becomes
a post hoc excuse for whatever the screen does.

Cost: about $4. Three receptors, roughly 50 knowns each plus a shared 100-compound decoy set.

### 3. *H. pylori* RNase J CTD self-interface (UniProt P56185)

**Structure: experimental, and there are two of them.** PDB **7PCR**, crystal, 2.75 A, residues 139-691.
PDB **8CGL**, cryo-EM, 4.1 A, the full dimer-of-dimers. This is the only candidate on the list where the
interface itself is solved rather than modelled, which matters more for this project than for most: the
central finding of the repo is that these methods are strong where structural precedent exists and
near-chance where it does not, so screening against a solved interface is the one option that does not
put the project's own thesis at risk.

**Ligandability: the best measured.** At the dimer interface (chains A-D in 8CGL, BSA 1,247 A^2 total,
624 A^2 per side, 42 + 42 interface residues, 47% apolar) there is a **679 A^3 cavity that is not the
active site**: 42 A from H210/D212/H213, 5.7 A from K649, 3.0 A from interface atoms. It appears in both
protomers (679 and 688 A^3) and, independently, in the 2.75 A crystal assembly as 321 + 145 A^3 clusters
at 8.9 and 4.5 A from K649. It is 60.6 A from the first modelled residue, so it is not an artifact of the
unmodelled N-terminal 138 residues.

**Mechanism, which is the unusual part.** K649 is the residue whose acetylation state switches the
oligomer: K649Q, the acetyl mimic, stabilises the tetramer and raises exoribonuclease activity 2.5 to
4-fold over K649R. So there is a documented functional lever sitting inside the cavity, and a built-in
genetic positive control for any compound that claims to act there. That is rare for a PPI site.

**Biology.** RNase J is **essential** in *H. pylori* and is the organism's major ribonuclease. Against
that: clarithromycin-resistant *H. pylori* was on the WHO 2017 High-priority list and was **removed** in
the 2024 update on the grounds of falling global resistance, a removal that drew a published open letter
of objection. So the pathogen is clinically enormous and the formal priority listing has just gone the
wrong way.

**Prior art: none.** The 2023 structure paper contains no drug-target discussion, no inhibitors and no
screening. The structures are deposited and free.

Sources: [H. pylori RNase J acetylation and oligomerisation](https://pmc.ncbi.nlm.nih.gov/articles/PMC10700544/),
[WHO BPPL 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC12367593/),
[open letter on the removals](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12452171/).

Note for the repo: `RNASEJ_MG423.md` already lists 8CGL as "one other template, ambiguous". It is the
*H. pylori* tetramer. That is the same structure being proposed here as a target in its own right.

### 4. *M. pneumoniae* RNase J catalytic site, with CPSF73 as a genuine selectivity test

This is the honest version of the incumbent target. The only pocket in the whole complex on the catalytic
subunit is the active site, and the project already has the off-target receptor wired
(`OFFTARGET_ACC = "Q9UKF6"`, MSA cached). Screening the active site and demanding a margin over CPSF73 is
a defensible experiment with a clear failure mode.

The reason it ranks below #1 and #3 is that it is the least selective site by construction: RNase J keeps
4 of 4 catalytic residues, CPSF73 keeps 3 of 4, and CPSF73's equivalent site is **already drugged** by
JTE-607, whose active form binds there with a published co-crystal. A compound that binds one is a good
candidate to bind the other. The 24.6% interface identity figure in `RNASEJ_MG423.md` is a statement
about the PPI surface and does **not** transfer to the active site.

Useful side effect: JTE-607 is the best available positive control for this entire fold family. It never
reached approval, so it is absent from a `max_phase=4` ChEMBL library and has to be added to
`library_approved.smi` by hand.

Source: [JTE-607 targets CPSF3](https://pubmed.ncbi.nlm.nih.gov/31399191/).

### 5. *S. pyogenes* RNase J1 : J2

Best pathogen story in the set and the weakest structural position. Both rnjA and rnjB are **essential
for growth** in GAS, unlike *B. subtilis* where only J1 is, and macrolide-resistant Group A
*Streptococcus* is on the **WHO BPPL 2024 medium tier**, which is more than can be said for any other
organism here. But there is no structure of the pair and no model, and the pocket scan gives a bad prior:
in all three RNase J systems measured, the catalytic subunit's PPI surface has no pocket.

If it is pursued, model first and scan before screening. The cost of finding out is one Boltz job.

Sources: [Bugrysheva & Scott 2010](https://pubmed.ncbi.nlm.nih.gov/20025665/),
[WHO BPPL 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC12367593/).

### 6. The two sub-interfaces inside the same tetramer

The 2:2 assembly has three distinct interfaces, and the screen currently addresses one. The J:J contact
buries 989 A^2 per side and the partner:partner contact 862 A^2 per side, both small enough to be
plausible PPI targets in principle; the partner:partner contact shows 111 and 107 A^3 cavities, below the
KEAP1 reference but above MDM2. Disrupting the dimer-of-dimers is mechanistically different from
disrupting the heterodimer, and SEC-MS says the cellular species is the 2:2, so it is a real alternative
hypothesis. Cost is zero if run as extra pocket constraints in the same batch.

### 7. MG354 : RpoB / RpoC

**Hold.** The headline number in `MG354_RNAP.md` is the control's, not the target's. MG354's own chain-pair
ipTM is 0.57 and 0.43 in the three samples that satisfy 4 of 5 crosslinks, and 0.17 and 0.15 in the two
that fail. No coordinates are in the repo, so the interface cannot be scanned. This is exactly the class
of prediction the project's own H1 result says is near-chance: an interface with no structural precedent.
Screening it would contradict the project's central finding.

---

## Rejected and why

**The whole human oncology lane, as a screening target, for now.** Individually checked:

| Candidate | Why rejected |
|---|---|
| **KEAP1 - SQSTM1** (PH-DRUG, pDockQ 0.373) | Excellent pocket, and that is the problem. PDB **3ADE** is KEAP1 Kelch with p62, and the Kelch domain is one of the most heavily worked PPI sites in oncology, with many inhibitor co-crystals. Nothing to add. Reclassified as a **positive control** in shortlist #2 |
| **MTA1/2/3 - RBBP4/7** (PH-DRUG, pDockQ 0.619 to 0.658) | The registry's "unsolved" flag is a paralog artifact, exactly caveat 1 in `POSTHOC.md`: MTA1-RBBP4 structures exist (4PBY, 5FXY, 6G16, 2,837 A^2 interface) and both small-molecule antagonists and bicyclic peptide inhibitors of that interaction are published. Reclassified as a **positive control** |
| **NFE2L2 - MAFG** (TARGETS.md, pDockQ 0.70) | bZIP leucine zipper, the archetypal flat PPI; the 1FOS reference measures 0 A^3. ML385 exists but binds Neh1 and blocks DNA binding rather than the dimer, and its selectivity across bZIPs is openly questioned. Massively worked. Reclassified as a **positive control** |
| **FBXO7 - PSMF1 (PI31)** (TARGETS.md, pDockQ 0.59) | Solved and worked. Both FP domains have crystal structures, the heterodimerisation mode is published, and 2026 cryo-EM structures of 20S with PI31 and FBXO7 are out. Also Parkinsonian rather than oncology biology |
| **DTX3L - PARP9** (PH-DRUG, pDockQ 0.666) | Reconstituted and structurally characterised: high-affinity heterodimerisation determinants published in 2022, DTX3L D2 tetramer solved (8R79), multiple 2023-24 papers. Not unworked |
| **GUCY1A2 - GUCY1B1** (PH-DRUG, pDockQ 0.712) | Soluble guanylate cyclase is a commercial drug target with two approved stimulators (riociguat, vericiguat). Nothing a $5 screen adds |
| **GATC - GATB** (TARGETS.md, pDockQ 0.68) | Two problems. The human pair is the mitochondrial GatCAB homolog, which makes it an anti-target rather than a target. The bacterial GatCAB is a genuine antibacterial target and is **already worked**: transition-state mimic inhibitors have been synthesised and tested against *H. pylori* GatCAB |
| **CSNK2A1 - NKAPD1** (TARGETS.md, pDockQ 0.25) | pDockQ 0.25 is at the bottom of the confident range, and CK2 chemical space is crowded (CX-4945, SGC-CK2-1, CAM4066 at the alphaD pocket). The NKAPD1 partner is uncharacterised and the interface model is weak |
| **TMCO6 - ZNF511** (TARGETS.md, r 0.647, pDockQ 0.71) | The most genuinely unexplored entry in the repo, and that is exactly why it fails as a *screening* target. No pocket data, no tool compound, no positive control, no biology, no assay, and ZNF511 is a predicted C2H2 transcription factor, which is the least tractable protein class there is. A hit would be uninterpretable. This is a structural-biology target, not a chemistry target |
| **The remaining ~85 rows of `drugged_unsolved_interfaces.csv`** | Rejected as a **class**, on `POSTHOC.md`'s own grounds. CORUM's `subunits_drugs` means a subunit of the complex is drugged, not the interface. The list is dominated by one signal: **46 of the 92 rows carry the identical five-drug HDAC-inhibitor string**, and 51 carry vorinostat at all, which says HDAC1 or HDAC2 is in the complex and nothing about the interface. Entries like TUBA1C-TUBB carrying 18 drugs, or H2AC20-H2BC18 carrying 14, are the join misfiring, not druggable interfaces. `POSTHOC.md` says this already; it should be cited, not re-derived |

**Rejected bacterial candidates:**

| Candidate | Why rejected |
|---|---|
| ***M. tuberculosis* RNase J (P9WGZ9, Rv2752c)** | This one looked like the best target on the list until the essentiality check. It has everything else: crystal structures at 2.445 A (7WNT) and an RNA complex at 3.2 A (7WNU), an active homodimer via beta-CASP/beta-lactamase contacts, MDR-TB as the funding environment, no inhibitors, and a 2024 editorial calling for exactly this. But **rnj is not essential in Mtb**, and deleting it **increases multi-drug tolerance**. A chemical inhibitor would phenocopy a lesion that makes the organism harder to kill. Decisive. I also measured the interface: BSA 2,576 A^2 per side, 72 + 67 residues, and the only cavity is the catalytic cleft (1,048 A^3, 3.1 to 5.3 A from all six catalytic residues); non-catalytic interfacial cavities are 51 and 42 A^3. Large interface, no pocket, wrong phenotype. Source: [loss of RNase J causes multi-drug tolerance](https://pmc.ncbi.nlm.nih.gov/articles/PMC9312406/), [Mtb RNase J structures](https://pmc.ncbi.nlm.nih.gov/articles/PMC10119312/) |
| **MG241 - MG242 and MG121 - MG119** (the "other, weaker findings" in `RNASEJ_MG423.md`) | Both rest on single-lysine crosslink evidence, both are explicitly labelled weak in the repo, neither has a pocket scan, neither has essentiality data, and the second is described in the repo as "expected from gene neighbourhood" |
| **Retargeting the whole RNase J idea at a PACE or CARB-X priority pathogen** | Not possible. **RNase J is absent from *E. coli* and most Gammaproteobacteria**, which is the entire PACE 2025 target list (Enterobacteriaceae, *A. baumannii*, *P. aeruginosa*). See the funding note below |

**A funding claim in `COSTS.md` that does not survive checking, and it affects the ordering.** `COSTS.md`
says measured antibacterial activity is "the evidence that PACE (up to GBP 1M, open worldwide) and CARB-X
require". Checked today: PACE's 2025 antibacterial therapeutics call is restricted to drug-resistant
**Gram-negative** priority pathogens (Enterobacteriaceae prioritising *E. coli* and *K. pneumoniae*,
*A. baumannii*, *P. aeruginosa*) and explicitly excludes Gram-positive pathogens, mycobacteria, and
Gram-negatives outside its target product profiles. CARB-X's stated eligibility runs off the CDC 2013 and
WHO 2017 lists, and its 2026 round is scoped to priority Gram-negatives plus neonatal sepsis.
*M. pneumoniae* is on none of those lists. *H. pylori* was High priority on WHO 2017, which CARB-X still
references, and is Gram-negative, so it is the only candidate here with even a plausible route. This does
not make the science worse, but the funding sentence in `COSTS.md` should be corrected before it appears
in an application, and "which funder" should not be the reason to pick a target.
Sources: [PACE 2025 call](https://iuk-business-connect.org.uk/opportunities/pace-pathways-to-antimicrobial-clinical-ef%EF%AC%81cacy-2025-antibacterial-therapeutics/),
[CARB-X 2026 round](https://carb-x.org/carb-x-news/carb-x-launches-2026-funding-round-to-address-global-burden-of-amr/).

**On *M. pneumoniae* as an organism, since it is the incumbent.** The clinical case is real and got
stronger: a worldwide resurgence from late 2023, with macrolide resistance at 54.1% of Japanese isolates
in 2024 and 83.8% in a 2024 South Korean series, against 0 to 8.7% in Ohio and under 2% in Denmark. So
this is a genuine and geographically concentrated problem. It is also on no priority list, which
constrains the funding story rather than the science.
Source: [Japan 2008-2024](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12566372/),
[Ohio](https://wwwnc.cdc.gov/eid/article/31/12/25-1008_article).

---

## What I could not determine

- **Whether the 273 A^3 MPN621 pocket survives across AF3 samples.** Only `model_0` is in the repo for
  each job. The *M. genitalium* ortholog model is an independent check and agrees, but that is two
  models, not five. Re-running the scan across all five samples of each job is free and should be done
  before the pocket is quoted anywhere.
- **Whether that pocket exists at all in the real protein.** There is no experimental structure of
  MPN621, of RNase J from *M. pneumoniae*, or of any RNase J J1:J2 heterocomplex in any organism. The
  only J1-J2 pair with published coordinates is the *B. subtilis* integrative model (PDB-IHM 9A5V),
  which is itself crosslinks plus deep learning, not an experiment.
- **How much to trust the absolute cavity volumes.** The same H. pylori catalytic cleft measures 415 A^3
  at 2.75 A and 5,463 A^3 at 4.1 A. I have calibrated the scan against three references and used only
  rank order, but a real pocket-detection run (fpocket, SiteMap, FTMap, or a druggability score such as
  DoGSiteScorer) would settle it and costs nothing. Do that before any of these numbers leave the repo.
- **Whether Boltz-2 can rank a known PPI-site binder at all.** This is the central unknown and it is the
  reason for shortlist #2. No published benchmark I found evaluates cofolding-based affinity prediction
  specifically on protein-protein interface inhibitors.
- **The *S. pyogenes* RNase J accessions.** Neither rnjA nor rnjB returns a reviewed Swiss-Prot entry for
  *S. pyogenes*; they are in TrEMBL and need to be pulled by strain before anything is modelled.
- **A residue-numbering discrepancy in *H. pylori* RNase J.** UniProt P56185 (strain 26695) is 689
  residues; 7PCR and 8CGL number to 691. Probably a strain difference, not checked. It matters for K649
  and for any interface residue list.
- **Whether MPN621 has a distinct functional role that a compound could exploit.** The repo establishes
  that it is essential and catalytically dead. It does not establish what it does. A compound that binds
  the 273 A^3 pocket has no predicted phenotype, which is a gap no amount of GPU fixes.
- **Assay availability for *H. pylori* and *S. pyogenes*.** `COSTS.md` works this out for
  *M. pneumoniae* only. CO-ADD's ESKAPE panel covers neither; NIAID would need asking separately. Worth
  resolving before switching organisms, since an unassayable hit is worth nothing.
- **Whether JTE-607 or its active metabolite is tractable for Boltz-2.** It must be added to the library
  manually, and it needs an atom count check against the 128-atom limit including hydrogens.

---

## If you do one thing

Add MPN621 (P75174) as a receptor, add the three positive-control interfaces from your own registry, and
run all of it in one batch for about $7. Pre-register the positive-control gate first. If the knowns do
not beat the decoys, you have learned that the compound route is closed for the price of a coffee, which
is a better outcome than a shortlist you cannot interpret and would not buy.
