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
