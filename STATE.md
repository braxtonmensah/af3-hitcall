# State of af3-hitcall, 2026-09-25

**Read this first.** Supersedes `HANDOFF_2026-09-22.md`, `HANDOFF_2026-09-25.md`,
`HANDOFF_2026-09-25_v2.md` and `HANDOFF_2026-09-25_evening.md`. Four handoffs for two days of work
is how a repo becomes unreadable; there is one of these from now on and it gets edited, not
duplicated.

Repo is public: https://github.com/braxtonmensah/af3-hitcall

## Standing instructions

- Pre-register every test in a `PREREG_*.md` committed **before** the data are joined. The commit
  dates are public and are the entire reason anyone believes the numbers. Do not break this.
- **Send no emails, submit no applications, spend no money without Braxton's explicit OK.**
- Writing for Braxton: no em dashes, plain, short.
- Do not undersell and do not overclaim. Lead with the strongest *true* framing.
- Never write "new protein fold". Never cite "141 novel topologies" (it is ~108). Never cite the
  foldnovelty p=0.028 result (it is p=0.110 and retracted).

## What is claimable right now

**Strong, survives scrutiny:**

- Confident predictions of never-solved complexes had the right interface **81% of the time in human
  (n=146) and 89% in yeast (n=84)** against structures released 2022-2026, versus **2%** for
  low-confidence calls. Five pre-registered attacks survived.
- **Always pair that with the conservative figure.** Most of those entries are cryo-EM, which is
  sometimes built from AlphaFold models. X-ray-only gives **53% (n=19, CI [0.32, 0.74])**. The honest
  headline is "53% to 81% depending on how hard you control for circularity". Leading with 81% alone
  is the one place this project has been doing the thing it tells everyone else not to do.
- The 81% is **conditional on later being solved**, which is 2.7% of confident calls. It is not the
  probability that an arbitrary confident pair interacts. Say so before someone else does.
- What screens miss is **non-autonomous contacts**; six recovery routes all failed.
- *M. pneumoniae* RNase J + MPN621 **2:2 heterotetramer**, five independent published lines.
- The **stoichiometry rule is calibrated**: sensitivity 75%, false-positive rate 12%, precision 64%
  against a 22% base rate (HIGHER_CAL, n=54 labelled pairs).

**Not claimable:**

- ~~"RNA polymerase beta/beta-prime was recovered blind"~~ **Retracted 2026-09-25.** The PDB says
  that pair is 1:1 in 367 of 370 assemblies. HIGHER_CAL's pre-registration required its removal.
  Verified recoveries are RpoA-RpoB and the three pyruvate dehydrogenase pairs; the Nap adhesin is
  ambiguous.
- ~~"MG354 is the missing omega subunit"~~ The fold argument is **gone** (OMEGA: no omega-family hit
  in either direction). What stands is that MG354 binds RNA polymerase in cells. Note also that its
  structure is already solved: **PDB 1TM9**, an NMR structure. It is uncharacterized in *function*,
  not in structure.
- Any claim that XLHUMAN found new biology. It found seven supported pairs and **all seven are
  already in the literature**.

## What was closed on 2026-09-25

| Test | Result |
|---|---|
| **OMEGA** | Inconclusive under the registered rule; no omega-like fold either direction. `analysis_omega.py` |
| **HIGHER_CAL** | Calibrated (delta +0.63, CI [0.076, 0.964]); forced the RpoC-RpoB retraction. `analysis_higher_cal.py` |
| **XLHUMAN** | Closed. Controls 0/10, 7 of 15 supported, 0 new. `analysis_xlhuman.py`, `analysis_xlhuman_novelty.py` |
| **CODEP** | D1 supported in CRISPR, **then WITHDRAWN**: did not replicate in RNAi. See CODEP_R. `analysis_codep.py` |
| **CODEP_R** | **CODEP does not replicate.** RNAi gate passes (+0.0486), primary -0.0042 [-0.0129, 0.0047]. Functional-coupling claim withdrawn. `analysis_codep_r.py` |
| **ASSEMBLY / ASSEMBLY2** | Both gates failed; clustering route **closed**. Co-dependency clusters are pathways, not assemblies. `analysis_assembly2.py` |
| **BRIDGE** | Pre-registered, 60 jobs built, **not run**. Unaffected in design but starts from a lower prior. `cleanroom/bridge/` |

### CODEP: claimed, then withdrawn the same day. Read this whole section before citing it.

**WITHDRAWN 2026-09-25 by CODEP_R. It did not replicate in RNAi.** DEMETER2 (shRNA, a different
perturbation technology, different labs, predating the CRISPR data) gives -0.0042, CI [-0.0129,
0.0047], while its gate passes at +0.0486, so the instrument was sensitive and simply did not see the
effect. That is not an underpowering excuse: the gates put RNAi at 0.47x CRISPR sensitivity, so a real
+0.0203 implies about +0.0095 in RNAi, and the observed upper bound of +0.0047 sits below it.

**Do not cite CODEP without CODEP_R.** The claim that confident never-solved predictions are
functionally coupled is not established. The CORUM-confinement finding was post hoc and also failed to
reproduce, so it should not be cited either. What survives is only that known complexes are detectably
co-dependent in both technologies, which describes the instruments rather than AlphaFold.

**What it looked like before the replication**, kept so the reasoning is legible: the gate passed at
+0.103, D1 came in at +0.0203 [0.0098, 0.0317] and survived essentiality matching, and it was the
first validation that was not structure-adjacent.

**Why it constrains the pitch.** The gap disappears outside CORUM-annotated complexes, where 3,027 of
the 3,441 confident pairs live. That is H1 again in a functional register: informative on the class the
field already recognises, near-chance on the rest. And **96.3% of confident never-solved pairs already
have BioGRID or IntAct evidence**, so "never solved" has always meant *no structure*, never *no
evidence of interaction*.

**Never say the registry is a list of novel interactions or novel targets.** The pre-registration
committed to that consequence in advance and it is now in force.

**`TARGETS.md` survives but is weaker than it reads.** Its 32 pairs are built on CRISPR
co-dependency, which CODEP_R shows does not carry the AlphaFold-related signal across technologies.
The list is still a defensible intersection of public evidence (confident model, co-dependent,
selectively essential, unsolved) and NFE2L2-MAFG, ISL1-LDB1, CCNC-PAX5, AP1M1-IKZF1 and TMCO6-ZNF511
remain worth a look, but it must not be presented as resting on a validated functional claim. Read its
limits section, and add the non-replication to it before showing it to anyone.

**No committed pre-registration is now without a reported result.** That was the one thing in this
repo that looked bad, and it is fixed.

## The compound screen, 2026-09-25 late: rebuilt, pre-registered, and NOT run

`PREREG_VSCREEN.md` plus three amendments, all committed before any Boltz-2 score exists. Read the
amendments, not just the body: each one corrects something the previous one got wrong, including two
defects in code committed the same day.

**The old staged screen must not be run.** 650 jobs were staged and validated. Checking them by
molecule rather than by filename found four defects:

1. Its decision rule, "compounds that beat every decoy", returns **5.88 compounds in expectation and
   fires at all with probability 0.86 under a pure null where nothing binds** (300 screen vs 50
   decoys). It was a near-certainty attached to a $650-1,800 purchase. `cleanroom/screen_power.py`.
2. Four molecules sat in both the screen arm and the decoy null under different ChEMBL ids, each
   capping its own null. Same defect as the one caught once before; the earlier fix was applied to
   the job set, never to the cause, which is deduplicating on the SMILES string before desalting.
3. The arms named two different MSA directories, so on either machine one arm dies at run time.
4. **`pocket[:20]` is not a geometric choice.** On this interface it keeps residues 25-357 and
   discards 358-569 entirely. Independently measured, the kept 20 sit a median 15 A from the
   catalytic site and the dropped 45 at 33 A, so the constraint was aimed at the catalytic-proximal
   half, which is the least selective part of the interface. `build_screen_jobs.py` now refuses to
   truncate; `build_gate.py` ranks contacts by distance to the ligand.

**Per-compound significance is unreachable here and that is stated in advance.** The floor on an
empirical p-value is 1/(decoys+1), so the top of 300 needs 2,999 decoys to clear BH q<0.10. The
primary test is therefore distributional (Mann-Whitney vs a matched null, power 0.84 at AUC 0.57
with 300/arm) and the shortlist is labelled hypotheses.

**Two things about Boltz-2 that constrain everything** (`cleanroom/BOLTZ_SCHEMA.md`, read from source
at v2.2.1):

- **The affinity head cannot see ions.** It pools protein-to-binder and binder-to-binder pairs only.
  Supplying the metals fixes the pose, not the score, so a metal-chelating ligand cannot be scored
  for what makes it bind. This demoted three of five Tier A gate rungs to diagnostics.
- **`affinity_pred_value` is log10 IC50 in uM, so LOWER is stronger.** Rank on
  `affinity_probability_binary`, where higher is binder. `vscreen.py --rank` prints the first with no
  direction stated; do not read that column without labelling it.

**The gate.** Nothing is known to bind bacterial RNase J from any organism (all 27 PDB entries carry
only metals, RNA or UMP; the RnpA candidates were refuted as aggregators, PMID 33972249). So the gate
is a surrogate on related folds and rests on **two** representable Tier A rungs, not five: the
JTE-607 acid on CPSF73 (Kd 370 nM, 6M8Q, does not coordinate metals) and ceftriaxone on Artemis
(7APV, and measured from the coordinates it sits 14.1 A from the only Zn, which is structural). Tier
B rests on a single rung, the nsp10-nsp14 fragment, whose pocket is confirmed from coordinates to
span both chains. 250 jobs, 3-6 GPU-hours, built and staged in `cleanroom/gate_jobs/`.

**Staging rule: the gate runs first and alone.** The gate's most likely outcome (Tier A passes, Tier
B fails) is the one that makes a null at an interface *uninformative* rather than a negative about
the target.

**THE GATE IS RUNNABLE. 250 jobs in `cleanroom/gate_jobs/`, all five MSAs present and verified.**
Nothing is blocking it but a GPU. Two things were fixed to get there, both the kind that fail
silently:

- **6M8Q's CPSF3 construct carries a His6 tag** (`GSSHHHHHHSSGLVPRGSH`). That is the receptor for the
  JTE-607 acid, one of only two rungs whose mode the affinity head can represent, and **a His tag
  chelates metals** in a job that deliberately supplies a Zn. Tags are now stripped, anchored to the
  UniProt sequence rather than to a regex (a regex over-trimmed by 3 and ate the native `MSA`).
- **Trimming shifts every pocket index**, since they come from `label_seq_id` on the untrimmed
  sequence. Offsets now flow through, contacts inside a trimmed region are dropped, and the builder
  refuses to write an index outside its chain. Verified: the 6M8Q pocket shifts by exactly 19 with
  residue identities preserved.
- Each MSA is keyed to its **construct**, not an accession, and the query row is checked against the
  job sequence before the file is accepted. A full-length MSA would have had the wrong columns.

## The MPN621 cleft screen: pre-registered, stage 1 built, not run

`PREREG_MPN621.md` + 2 amendments. Four arms: S (MPN621 cleft), N (matched null), O1 (*M. pneumoniae*
RNase J, **the paralogue arm the old design never had**), O2 (human CPSF73, using the real 6M8Q
co-crystal pocket). 1,600 jobs at 20-40 GPU-hours if run whole, so it is staged: gate, then S+N (800
jobs, built and validated in `cleanroom/mpn621_jobs/`), then O1+O2 **only if M1 enriches**, then arm Z.

**Two confounds found in the selectivity arm, one real and one cleared:**

- **Real: the metal.** MPN621's cleft has **no histidine at all** (only E73, D162, D163) while RNase
  J's keeps H373 and H377. So the target may hold no catalytic zinc and its comparator does. Built
  metal-free with the comparators zinc-bearing, which is a **declared deviation** from VSCREEN
  Amendment 2's uniform rule, plus **arm Z**: 50 compounds re-run on MPN621 *with* a zinc. If
  Spearman(S, Z) < 0.8 the selectivity margin is metal-dependent and cannot justify a purchase.
- **Cleared: MSA depth.** MPN621 has **464** sequences against 4,623 for RNase J and 6,000 for
  CPSF73, a tenfold gap in exactly the comparison that would justify buying. Measured at the pocket:
  pLDDT **92.0 vs 92.5**, minima 83.6 and 84.4, all 20 residues resolved in each. A 0.4-point gap,
  both very high, so receptor quality cannot explain a cross-arm difference.
  `cleanroom/pocket_confidence.py`.

**THE INTERFACE IS NOT LIGANDABLE ON EITHER SIDE. Do not run the interface screen.** Amendment 4,
`cleanroom/analysis_ligandability.py`, `results_ligandability.json`. Largest cavity per chain across
both ortholog models, calibrated against KEAP1:p62 575 A^3 (drugged), MDM2:p53 76 (drugged but
shallow), c-Fos:c-Jun 0 (flat):

| Cavity | *M. pneumoniae* | *M. genitalium* | ratio |
|---|---|---|---|
| RNase J catalytic cleft | 1262 | 1155 | 1.09 |
| **RNase J largest non-catalytic interface cavity** | **26** | **27** | **1.04** |
| **MPN621 degenerate cleft** | **491** | **470** | **1.04** |
| MPN621 largest non-catalytic interface cavity | 273 | 82 | **3.33** |

Three of four reproduce within 9%. **The one that does not is the 273 A^3 cavity that
`TARGET_EXPANSION.md` recommended re-aiming the screen at**, so that recommendation is not adopted:
by the standard that validates the other three it is a one-model artefact, and even at its largest
only 28% of its lining residues are interface residues. RNase J's interface face is flat at 26 and
27 A^3 and that now counts as established. **So the screen's expected null was structurally
predetermined, not merely a low prior.**

**The one pocket worth pursuing is MPN621's degenerate cleft**: 491 / 470 A^3 at ratio 1.04,
comparable to the drugged KEAP1 reference, and sitting on residues where **0 of 4 catalytic
positions are conserved** while RNase J keeps all four and human CPSF73 keeps three. That inverts
the reason the screen went to the interface: the catalytic cleft is non-selective **on RNase J**
because it is conserved, and MPN621 has lost exactly the machinery that makes those clefts resemble
each other. It also puts the problem back in-distribution for a tool with no protein-protein
affinity module. **It is not pre-registered and needs its own prereg**, whose selectivity arm must
compare against *M. pneumoniae* RNase J as well as human CPSF73, because a compound hitting both
paralogues says nothing about which one matters.

**Library: 13,293 distinct molecules** (was 2,297), from ChEMBL phases 1-4, iPPI-DB and the MMV
Pathogen Box, deduplicated on InChIKey after desalting, property-annotated, PAINS-flagged, with
licence and date per compound. `cleanroom/libgen.py`, `cleanroom/LIBRARIES.md`. The null is now
property-matched and 1:1 with the screen, because the affinity head tracks ligand size.

**Corrected: the PACE/CARB-X claim in `COSTS.md` was wrong.** Both funders are scoped to
Gram-negatives and *M. pneumoniae* is on neither list, and it cannot be fixed by changing organism
because RNase J is absent from *E. coli* and most Gammaproteobacteria. Fixed in place with sources.

**Corrected: MG354's ipTM.** The 0.910 in `new_biology/MG354_RNAP.md` is the **RpoB-RpoC control**,
not MG354's own chain pair, which is 0.57/0.43. Do not quote 0.910 for MG354.

## The only outstanding test

**RNAP3**: does a three-chain model of MG354 + RpoB + RpoC bring the five crosslinks within reach?
Pre-registered (`PREREG_RNAP3.md`), job files and scorer ready in `cleanroom/rnap3/`.

- Read the RpoB-RpoC control first. Below 0.70 satisfied and the MG354 numbers are not interpreted.
- Path A: RunPod Boltz-2, about $4 to $8, commercially unrestricted. Blocked on account balance.
- Path B: AlphaFold Server, free, needs your browser, output is non-commercial.
- Scoring is automated: `python score_rnap3.py <model.cif>`.

## Blockers, and what each actually needs

| Blocker | Needs |
|---|---|
| RNAP3 structure | Two clicks (AF Server) or about $8 (RunPod) |
| Virtual screen on Quartz | RT Project join at `projects.rt.iu.edu`, PI `lamhuber`, "HPC for Students" |
| Quartz SSH | One `ssh quartz` login in WSL per 12h. Multiplexing works in WSL, never in Git Bash |
| IP certainty | A free written opinion from IU's commercialization office. See `IP_RECORD.md` and `COSTS.md` |
| Wet-lab confirmation | A pull-down of tagged RpoC. Days, not months, at a core facility |

## Operational facts that cost a cycle each

- `MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc 'ssh quartz "<cmd>"'` — the env var matters,
  Git Bash rewrites `/mnt/c/...` otherwise.
- The O'Reilly crosslink FASTA has corrupted residues. Use current UniProt sequences plus peptide
  location (XLVAL Amendment 2).
- `human_extract.parse` returns interfaces and drops coordinates, and uses CB with a CA fallback.
  Anything needing CA-CA distances needs its own parser (see `analysis_xlhuman.py`).
- Burke models live in two archives; the `Dataset` column says which, **not** the filename.
- Boltz-2 rejects ligands over 128 atoms *including hydrogens*.
- `.gitattributes` pins yaml/sh/slurm to LF. A CR inside an MSA path reports a file that exists as
  missing.
- `outreach/` is gitignored on purpose. `build_sample_report.py` lives in the repo root instead,
  because the report is a claim about the data and its code should be auditable.

## Money

One file: `../MONEY.md`. One tracking file: `../LEDGER.md`. Everything else is superseded.
P($100k by Dec 31) is about 2%; expected new money is about $4.6k. Nothing has been sent.
