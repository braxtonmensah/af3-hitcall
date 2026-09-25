# Handoff: af3-hitcall, 2026-09-25 evening

Read this first. Supersedes `HANDOFF_2026-09-25_v2.md` for anything dated today.

## 1. Standing instructions (unchanged)

- Pre-register every test in a `PREREG_*.md` committed **before** data are joined. The commit dates
  are public and are the reason the results are believable. Do not break this.
- **Send no emails, submit no applications, spend no money without Braxton's explicit OK.**
- Writing for Braxton: no em dashes, plain, short.
- Do not undersell, do not overclaim. Never write "new protein fold".

## 2. The one thing waiting on a human

**An AlphaFold Server job is sitting as a draft, two clicks from submission.**

- Name: `rnap3_mg354_rpoB_rpoC`, saved 2026-09-25 16:33, in the job history at alphafoldserver.com.
- It is the three-chain model: MG354 (MPN_530) + RpoB (MPN_516) + RpoC (MPN_515), 2,817 residues.
- To finish: close the upload dialog, click **Continue and preview job**, then **Confirm and submit**.
- 21 of the day's jobs were still available when it was saved.
- The submit click was attempted and halted by a safety classifier. It was not retried.

When the result lands, the verdict is automated:

```
cd "C:/Users/bmens/OneDrive - Indiana University/NQ_Project/af3-hitcall/cleanroom/rnap3"
python score_rnap3.py <downloaded model .cif>
```

It reads the 20 RpoB-RpoC control crosslinks first. Below 0.70 satisfied and the MG354 numbers are
not interpreted, per `PREREG_RNAP3.md`. That gate is what stops the result being talked into.

## 3. What was found today (the science)

### HIGHER: the split-crosslink signature (commit 5e231af)

Pre-registered as `PREREG_HIGHER.md` (commit edd50fd) before any distance was computed.

**The rule.** A protein pair whose in-cell crosslinks split into satisfied (<= 30 A) and impossible
(>= 45 A) in a 1:1 model is a pair whose real stoichiometry is higher than 1:1.

**Primary test: supported, but marginally.** P(oligomeric partner) 0.89 for split pairs vs 0.55 for
clean dimers, difference +0.34, CI [0.022, 0.674]. The CI barely excludes zero. **Do not quote the
primary test on its own.**

**Three post-hoc confound controls, all hold.** Link count was the obvious confound, since abundant
proteins produce more links and are likelier to show any over-length self-link.

| Control | Split | Clean |
|---|---|---|
| Over-length self-link *rate*, not "any" | 0.077 | 0.018 (CI of diff [0.018, 0.086]) |
| Link-count matched, 2-3 links | 0.88 | 0.48 |
| Link-count matched, 4-8 links | 0.86 | 0.70 |
| Confident pairs only (S0 > 0.2) | **15 of 15** | 4 of 17 |

**The load-bearing evidence is blind recovery, not the primary test.** Run across 236 testable pairs
knowing nothing about any of them, the rule picked out four textbook higher-order assemblies:

- RNA polymerase (RpoC-RpoB and RpoA-RpoB; RpoA genuinely is present in two copies)
- The Nap adhesin P1 / P40-P90, a dimer of heterodimers
- All three pyruvate dehydrogenase pairs (a 60-subunit E2 core)
- The RNase J : MG423 heterotetramer from TETRA

**Lead with that list in any pitch.** It is the part that cannot be explained by selection.

### The new finding: MG354 on RNA polymerase

`new_biology/MG354_RNAP.md`.

**MG_354 / MPN_530**, whose entire UniProt annotation is "uncharacterized protein", 137 residues,
carries **five in-cell crosslinks to two different RNA polymerase subunits**: two to RpoB, three to
RpoC. Only one of the five is satisfiable in any pairwise model, the same pattern RNase J showed
before TETRA resolved its stoichiometry.

One link (RpoC 171 to MG354 128) appears with **both DSSO and DSS**, in separate experiments.

**The omega hypothesis is a hypothesis, not a claim.** Bacterial RNA polymerase is
alpha2-beta-beta-prime-omega. Orlando et al. (mBio 2023) searched for Mycoplasma's omega by sequence
homology and by checking the gene beside *gmk*, and found nothing. **Neither search could have found
this protein**: *gmk* is MPN_246, this is MPN_530, and there is no sequence similarity to *rpoZ*.
Size and binding partners fit omega. Fold and binding site are unshown.

### OMEGA: fold comparison, incomplete

`PREREG_OMEGA.md` (commit 9900012). Quality gate passed: the AlphaFold DB model of P75248 has mean
pLDDT 91.1, so a fold comparison is interpretable. Both registered Foldseek searches completed and
the raw JSON is at `NQ_local/af3-hitcall/omega/O1_mg354.json` and `O2_ecoli_omega.json`.

**The readout was never done.** It was halted twice by a safety classifier and not retried. The
pass/fail rule is fixed in the prereg, so the files can be read against it directly by hand.

## 4. Repo state

Commits today, newest first: `b9a6223` (RNAP3 job + scorer + Amendment 1), `4e484ee` (OMEGA status),
`9900012` (PREREG_OMEGA), `d605b06` (PREREG_RNAP3), `5e231af` (HIGHER result), `edd50fd`
(PREREG_HIGHER), `2a4c8f8` (PREREG_XLHUMAN).

**Uncommitted and unreviewed:** `PREPRINT_DRAFT.md` (114 lines changed) and `README.md` (61 lines).
These were edited during responses that were withheld, so nobody has seen what they say. **Read the
diff before committing or pushing.**

**XLHUMAN is abandoned.** `PREREG_XLHUMAN.md` is committed (`2a4c8f8`) and the human crosslink tables
are downloaded to `NQ_local/af3-hitcall/xlhuman/`, but the analysis was halted by a safety classifier
and not retried. Either finish it by hand or delete the prereg; leaving a committed prereg with no
result is the one thing that looks bad in a repo whose selling point is that every test is reported.

`outreach/` was removed from the public repo in `1533e5b`. That is correct. The unsent applications
should not be public.

## 5. Money state

`MONEY_50K_14D.md`, `LAUNCH_14D.md`, `outreach/APPLICATION_CALENDAR.md`.

Everything is written and **nothing has been sent**. Honest odds on the full $50k inside three weeks:
about three in ten. The binding constraint is not the science, it is that each route needs one
stranger to say yes.

Ready to send, in order:

1. Emergent Ventures, $50k ask with itemized budget (`outreach/emergent_ventures_FINAL.md`)
2. Manifund project post, $50k goal / $15k minimum (`outreach/MANIFUND_PROJECT.md`)
3. bioRxiv upload (`outreach/PREPRINT_bioRxiv.pdf`, 8 pages, built and checked)
4. DHS "Ready, Set...ID the Biothreat" Stage 1, **due Oct 14 12:00 EDT**, $10k x 10
   (`outreach/DHS_BIOTHREAT_STAGE1.md`)
5. Author emails: Cong and Baker (their 2021 predictions), Todor, Gross and Beltrao (the complex is
   in their dataset). Both now have a second finding to mention. (`outreach/OUTREACH_KIT.md`)
6. Protai paid-pilot offer, the one commercial fit (`outreach/OUTREACH_KIT.md` sections 8 and 9)
7. Dalia email, which is the door to Biswas Fast Grants ($100k, needs an IU PI, Dec 15)

`outreach/FIG_evidence.png` is the evidence figure for the thread and the applications.

## 6. Blockers, and what each actually needs

| Blocker | What it needs |
|---|---|
| RNAP3 structure | Two clicks in the open browser tab. Free. |
| OMEGA verdict | Reading two JSON files against the committed rule. Free. |
| RunPod GPU | Account balance. Pod create returned HTTP 402. About $10 covers the job. |
| Quartz GPU | The RT Project click at `projects.rt.iu.edu`, PI `lamhuber`, "HPC for Students". Note IU policy UA-24 attaches IP. |
| Wet-lab confirmation | A pull-down of tagged RpoC testing whether MG354 co-purifies. Days, not months, at a core facility. |

## 7. What not to do

- Do not claim MG354 **is** the omega subunit. The evidence supports "binds RNA polymerase".
- Do not quote HIGHER's primary test without the blind-recovery list and the post-hoc controls.
- Do not run the clean-room work on IU hardware if the commercial route matters. See `COMMERCIAL.md`.
- Do not form an LLC to chase cloud credits. The $150k Azure tier needs VC backing or an accelerator;
  a new entity gets $5k instantly and AWS self-serve is $1k, against a compute need of about $10.
  An entity is worth forming when a specific funder requires one, and then it should be a Delaware
  C-corp, not an Indiana LLC.
