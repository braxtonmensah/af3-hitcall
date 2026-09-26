# Audit of the public files, 2026-09-26

Scope: every public `.md` in the repository root, plus `registry/`, `new_biology/`, `cleanroom/`
and `vibrio_pilot/`. `outreach/` was not read. Nothing was edited. Line numbers are as of this date.

Governing assumption, per instruction: `STATE.md` is current and supersedes the four handoffs. Where
`STATE.md` itself is wrong, that is reported, because it is the file `README.md` tells every reader to
open first.

Summary of what a hostile reader would find: **12 critical items**. The three worst are not stale
prose. They are (1) `IP_RECORD.md`, a document whose stated purpose is to be a truthful
contemporaneous record, asserting in the past tense that a screen was run which was not run;
(2) `STATE.md` calling RNAP3 "the only outstanding test" when RNAP3 has run and is reported
SUPPORTED, and separately claiming "no committed pre-registration is now without a reported result"
when at least four are; and (3) three funder and drug-target retractions that were applied to
`README.md` and `COSTS.md` and never propagated to `COMMERCIAL.md`, `VIRTUAL_LAB.md`,
`PREPRINT_DRAFT.md`, `new_biology/RNASEJ_MG423.md` or `cleanroom/TARGET_EXPANSION.md`.

Also flagged: the pre-registration count is stated three different ways and none is right, two
pre-registration numbers are used twice, and the compound library size is stated five different ways
with the governing document holding the wrong one.

---

## 1. CRITICAL

Retracted or withdrawn claims asserted as live, and hard contradictions.

### C-1. `IP_RECORD.md:7-8` says the Quartz screen "was run". It was not.

> "The Boltz-2 virtual screen of the RNase J (MPN280 / P75497) : MPN621 interface **was run** on **IU
> Quartz**"

`IP_RECORD.md:3` frames the whole file as "Written 2026-09-25, before the screen was run, so it is a
record and not a reconstruction." Contradicted by, in the same repository:

- `cleanroom/quartz/PUSH.md:63` table row: "Runs so far | **none**, `logs/` is empty"
- `cleanroom/quartz/PUSH.md:72` "all 350 jobs failed as 'not pod-side' on Quartz"
- `cleanroom/RUN_SCREENS.md:3` "Two screens are built and **neither has been run**"
- `COSTS.md:46` "The screen has not run, so **there is no drug list yet**"
- `README.md:186` "The planned virtual screen has not produced results"
- `STATE.md:99` "rebuilt, pre-registered, and NOT run"

This is the most damaging single item in the audit. The repository's pitch is that its timestamps and
its records are honest. A file titled "Contemporaneous record" that states an event which did not
happen hands a critic the strongest possible counterexample, and it is also the file `README.md:187`
points readers to for provenance.

**Fix:** a dated header stating the screen has not run, and change every past-tense verb in
"What was used" to the conditional. Do not delete the file; its value is that it predates the run.

### C-2. `IP_RECORD.md:10-16` premise contradicted by `STATE.md:239`

The entire UA-24 argument rests on Quartz being outside "University Resources" because it is
"**self-service**: an account is created at `access.iu.edu/Accounts/Create` with **no proposal, no
faculty sponsor, and no granted allocation**", and on Big Red 200 being off limits "because it
requires both" via `projects.rt.iu.edu`.

`STATE.md:239` lists the blocker for the Quartz screen as: "**RT Project join at
`projects.rt.iu.edu`, PI `lamhuber`, 'HPC for Students'**". `cleanroom/quartz/PUSH.md` also records
"Slurm association: **none.** `sacctmgr show assoc user=bmensah` returns nothing".

If GPU time on Quartz requires an RT project with a named PI, that is the same mechanism
`IP_RECORD.md:15-16` uses to disqualify Big Red 200, and the IP reading loses its stated basis. This
is load-bearing: `COSTS.md:33-39` and `COMMERCIAL.md:57-58` both defer to it.

**Fix:** reconcile in `IP_RECORD.md` before any GPU runs, or record the RT-project requirement as a
change of facts since 2026-09-25.

### C-3. `STATE.md:224-232` calls RNAP3 "The only outstanding test". RNAP3 has run and is SUPPORTED.

`STATE.md:224` heading "## The only outstanding test", `:226-227` "does a three-chain model ... bring
the five crosslinks within reach? Pre-registered, job files and scorer ready", `:230-231` "Path A:
RunPod ... Blocked on account balance. Path B: AlphaFold Server, free, needs your browser",
`:238` "RNAP3 structure | Two clicks (AF Server) or about $8 (RunPod)".

Contradicted by:

- `RESULTS.md:103` "**SUPPORTED.** AlphaFold Server, MPN_530 + RpoB + RpoC, 2,817 residues, 5
  samples, **run 2026-09-25**"
- `new_biology/MG354_RNAP.md:3` "**RNAP3 has now run and SUPPORTS the claim.**"

`STATE.md` reports the RNAP3 result nowhere. Its "What was closed on 2026-09-25" table
(`:53-61`) omits RNAP3 entirely. `cleanroom/rnap3/RUN.md:1-16` likewise still presents both paths as
pending ("blocked on balance", "needs your browser").

Separately, "**the only** outstanding test" is false on `STATE.md`'s own evidence: BRIDGE (`:61`),
the VSCREEN gate (`:99`, `:148`), MPN621 (`:163`) and VIBRIO are all outstanding.

**Fix:** move RNAP3 into the closed table with its result, delete the blockers row, and retitle the
section. Add a two-line header to `cleanroom/rnap3/RUN.md`.

### C-4. `STATE.md:96` "No committed pre-registration is now without a reported result." False.

`STATE.md:96-97`: "**No committed pre-registration is now without a reported result.** That was the
one thing in this repo that looked bad, and it is fixed."

No result is reported anywhere for:

| Pre-registration | Status, per the repo's own files |
|---|---|
| `PREREG_VSCREEN.md` | `STATE.md:99` "NOT run"; no Boltz score exists |
| `PREREG_MPN621.md` | `STATE.md:163` "stage 1 built, not run" |
| `PREREG_VIBRIO.md` | `PREREG_VIBRIO.md:4-5` "designed, not run"; `RESULTS.md:172-173` "needs GPU time" |
| `PREREG_BRIDGE.md` | `STATE.md:61` "not run", but arm P **has** run (see C-5) and `RESULTS.md` has no BRIDGE row |
| `PREREG_RESCUE.md` | `RESULTS.md:89` "Interim only, verdict waits for n = 20" |

This is the first claim an auditor will test, and `STATE.md:97` draws attention to it. As written it
converts a defensible position ("three screens are pre-registered and not yet run, which is why no
result is claimed") into a falsifiable overstatement.

**Fix:** replace with "Every pre-registration that has been *executed* has a reported result. Four are
pre-registered and not yet run: VSCREEN, MPN621, VIBRIO, and BRIDGE arms BR/CT. RESCUE is interim at
n = 10 of 20."

### C-5. `STATE.md:61` "BRIDGE ... not run" contradicts `PREREG_BRIDGE.md:171-198` and `cleanroom/bridge/RUN.md:101`

- `STATE.md:61` "**BRIDGE** | Pre-registered, 60 jobs built, **not run**."
- `PREREG_BRIDGE.md:171` "# Arm P result, 2026-09-25: **GATE G' PASSES**"
- `cleanroom/bridge/RUN.md:101` "**State:** arm P 20/20 run (19 read, gate passes). Arm BR 5 of 20
  submitted. Arm CT 0 of 20. **Remaining: 35 jobs.**"

So 25 of 60 jobs have run and a pre-registered gate has been read and passed. `RESULTS.md` has no
BRIDGE row at all, which also falsifies `README.md:151` ("`RESULTS.md` | every test and its
numbers").

**Fix:** `STATE.md:61` to "arm P run, gate G' passes (2 of 20, bar 4); arms BR/CT 5 of 40 submitted,
unscored", and add a BRIDGE row to `RESULTS.md`.

### C-6. `PREREG_VSCREEN.md:135` asserts "five independent published lines", which the file it cites retracts

> "The model's support is **five independent published lines**
> (`new_biology/RNASEJ_MG423.md`) but it remains a model."

`new_biology/RNASEJ_MG423.md:48` is headed: "**How many independent lines this is, stated exactly,
because 'five independent' overstates it.**" `:63-65` "the accurate phrasing is **'five published
lines from three independent studies'** ... claiming five independent lines was not supportable and
this table is the reason." `STATE.md:34` uses the correct phrasing.

The citation points at the retraction and states the retracted version. Note the same phrasing also
survives unqualified at `HANDOFF_2026-09-25_v2.md:87` and `HANDOFF_2026-09-25.md:28`; those files
carry SUPERSEDED headers, but the headers name only RpoC-RpoB, omega and XLHUMAN, not this.

**Fix:** the pre-registration body must not be rewritten. Append one line to Amendment 4 or a new
Amendment 5: "Correction to the Limitations section: 'five independent published lines' should read
'five published lines from three independent studies', per `new_biology/RNASEJ_MG423.md`." Extend the
handoff headers by one clause.

### C-7. `PREREG_BRIDGE.md:11-21` cites the withdrawn CODEP result as live support

> ":14 **CODEP** (today): the functional signal behaves identically. Confident predictions beat
> low-confidence ones inside annotated complexes (+0.0585) and not at all outside them (+0.0047)."

Presented at `:11` as one of "Three results in this repository [that] say the same thing from three
directions". Withdrawn by `PREREG_CODEP_R`: `RESULTS.md:102` "R2, the pre-registered CORUM split,
**holds in neither half** (CORUM -0.0021; non-CORUM -0.0009), so CODEP's post hoc confinement finding
is unsupported." `STATE.md:72-74` "**Do not cite CODEP without CODEP_R.** ... The CORUM-confinement
finding was post hoc and also failed to reproduce, so it should not be cited either."

`PREREG_BRIDGE.md` has an Amendment 1 (`:113`) but no CODEP_R note. `STATE.md:61` says BRIDGE "starts
from a lower prior"; that statement appears nowhere in `PREREG_BRIDGE.md` itself.

Same pattern, lower severity because the test is closed and reported: `PREREG_ASSEMBLY.md:8`, `:10`
and `:22` assert the CODEP result and the 96.3% figure as live premises.

**Fix:** append an amendment to `PREREG_BRIDGE.md` recording that the CODEP premise was withdrawn on
2026-09-25, that the design is unaffected, and that the prior is lower.

### C-8. PACE and CARB-X are still presented as funders for this work, in three files

The correction exists at `COSTS.md:95-115`, `README.md:126-129` and `STATE.md:217-219`. It was not
propagated:

| File:line | Text |
|---|---|
| `VIRTUAL_LAB.md:78-81` | "that is measured antibacterial activity against an essential, **structurally validated target**. That is the entry criterion for **PACE (up to GBP 1M, open worldwide to academia and SMEs)** and **CARB-X**. This is **the only route on the board that reaches seven figures**" |
| `VIRTUAL_LAB.md:21` | "PACE and CARB-X both require measured activity" (framed as the gate, i.e. as eligibility) |
| `COMMERCIAL.md:82` | "Converting the target into even a weak compound moves us from 'no eligible programmes' to '**eligible for PACE (£1M) and CARB-X**'" |
| `COMMERCIAL.md:92` | "If any compound shows activity, **PACE and CARB-X open**, and both are an order of magnitude above SBIR" |
| `COMMERCIAL.md:18, 25, 37, 52, 73-74` | CARB-X as route 2 in the ranked table; "the real gate on CARB-X and SBIR money" |
| `COSTS.md:127` | step 7 "**If activity: apply to PACE and CARB-X**", twenty lines below the same file's own correction |
| `PLAN_100K.md:25, 49` | CARB-X as stack item 5 (mitigated by the SUPERSEDED header at `:1-3`) |

`COSTS.md:127` is the worst of these because it is a self-contradiction inside one file: `:95-96`
says the claim "is wrong and **it must not be repeated in an application**", and `:127` is the
application step.

**Fix:** delete or annotate `COSTS.md:127`; header on `VIRTUAL_LAB.md` and `COMMERCIAL.md` (see §5).

### C-9. `COMMERCIAL.md:80` "We have a validated target"

> ":80 **The implication.** We have a validated target and no compound, which is the one thing almost
> nobody funds."

Contradicted by the same file 60 lines earlier: `:18` "We have **no wet-lab validation** and no
compounds", `:26` "The routes that reach $100k+ (SBIR, CARB-X) need ... a **wet-lab-validated
target**". And by `TARGETS.md:14` and `:111` ("It is not a validated target list and must never be
presented as one"), by `README.md:121` ("None of this establishes selective inhibition or
antibacterial activity"), and by `PREREG_VSCREEN` Amendment 4.

### C-10. The RNase J : MPN621 interface is still presented as a drug target or screen target in seven places

`PREREG_VSCREEN` Amendment 4 (`:426-468`) measured it: 26 and 27 A^3 of non-catalytic cavity across
two ortholog models against 76 A^3 for the shallowest drugged reference; `:466` "**the interface is
not ligandable on either side**"; `STATE.md:183` "**THE INTERFACE IS NOT LIGANDABLE ON EITHER SIDE.
Do not run the interface screen.**" Still live:

| File:line | Text |
|---|---|
| `new_biology/RNASEJ_MG423.md:83-84` | "An essential protein whose only apparent job is holding RNase J together is a **protein-protein-interface target by definition**." No ligandability qualifier anywhere in the file |
| `PREPRINT_DRAFT.md:32` | "The interface **merits experimental study** but is not a validated antibacterial target" |
| `PREPRINT_DRAFT.md:179-182` | "For drug discovery, **the interface could be investigated experimentally**" |
| `COMMERCIAL.md:43` | "Only then: Boltz-2 **virtual screen against the interface**, then compounds" |
| `COMMERCIAL.md:85` | "Boltz-2 virtual screen **against the interface**" as step 1 of the $1-3k conversion |
| `VIRTUAL_LAB.md:12` | "Rank purchasable compounds **against the interface** | Boltz-2 affinity | **built**" |
| `COSTS.md:72` | "Buy only after the screen's decoy null and CPSF73 selectivity check" (also the retracted decision rule, see A-note below) |
| `cleanroom/POSITIVE_CONTROLS.md:1, 7-11` | Entire file scoped to "the RNase J (P75497) : MPN621 (P75174) **interface screen**", no cancellation header |
| `cleanroom/LIBRARIES.md:2` | "Target: *Mycoplasma pneumoniae* RNase J, an oligomerisation / **protein-protein interface**" |

`PREPRINT_DRAFT.md` is the most consequential of these: it contains no ligandability number at all,
while `README.md:106` leads with "the interface itself is **not** ligandable". The preprint is the
document intended for a preprint server.

Note on `COSTS.md:15` and `:72-73`: these describe the **300 compounds + 50 decoys** design and the
"beat every decoy" rule that `PREREG_VSCREEN:18-25` retracted as firing on noise "about 86% of the
time" under a pure null. `COSTS.md` presents it as the purchase gate.

### C-11. `cleanroom/TARGET_EXPANSION.md` has no correction header, and its live recommendation was rejected by a later pre-registered measurement

- `:36` "**Single recommendation for the next target to stand up: MPN621 (P75174) as the receptor
  chain**" at the interface. `STATE.md:195-196` "that recommendation **is not adopted**";
  `PREREG_VSCREEN:463-464` "**The re-aiming recommendation is not adopted.**"
- `:38-41` "**Confidence: moderate-high (about 0.75)** that this ordering is right ... The pocket
  asymmetry between the two chains **reproduces across two independent AF3 models of two orthologs**,
  which is why I am fairly confident in it". Amendment 4 falsified exactly this.
- `:22-24` and `:92` present the ortholog check as supporting the 273 A^3 cavity: "273 A^3
  non-catalytic cavity at the interface ... **419 and 470 A^3 in the *M. genitalium* ortholog
  model**", graded "**Yes, modestly**" ligandable, "Between the MDM2 and KEAP1 references".

The 419/470 comparison is a substantive error, not just staleness. From
`cleanroom/results_ligandability.json`, both the 419 and the 470 A^3 cavities in the *M. genitalium*
partner chain are **catalytic-proximal** (`dist_to_catalytic` 3.2 and 2.9 A). The ortholog's largest
**non-catalytic** interface cavity, the actual counterpart of the 273, is
`largest_non_catalytic["M_genitalium/partner"] = 82.0`. So the file's confidence rests on comparing
two different kinds of cavity, which is precisely why Amendment 4 could write "The one that does not
[reproduce] is exactly the one the recommendation rested on."

A reader arriving at this file from a search engine gets a confident, unqualified recommendation to
aim a screen at a pocket the project has since measured as a one-model artefact.

### C-12. Pre-registration numbers collide, and all three published counts are wrong

Numbering collisions:

- "**Pre-registration 29**" is both `PREREG_ASSEMBLY.md:1` and `PREREG_VSCREEN.md:1`
- "**Pre-registration 30**" is both `PREREG_ASSEMBLY2.md:1` and `PREREG_MPN621.md:1`

Counts. There are **33** `PREREG*.md` files; the highest number used is **31**.

| Claim | File:line |
|---|---|
| "**21 hypotheses** pre-registered" | `README.md:32` |
| "the **26** pre-registrations" | `README.md:150` |
| "**Twenty-one** hypotheses were pre-registered" | `PREPRINT_DRAFT.md:294` |
| "the **21** pre-registrations" | `HANDOFF_2026-09-25_v2.md:170` |

Three different numbers in two of the most-read documents, and `README.md` contradicts itself 118
lines apart. For a repository whose entire argument is "count the pre-registrations and check their
commit dates yourself", this is the first thing a reader verifies and the cheapest possible own goal.

**Fix:** one authoritative count derived from the file list, used in both places; renumber the two
collisions to 32 and 33 (or annotate them as "29b"/"30b" so existing commit references still
resolve).

---

## 2. CONTRADICTIONS BETWEEN FILES

### X-1. Compound library size: five different numbers, and `STATE.md` holds the wrong one

Ground truth, measured directly: `cleanroom/library_master.tsv` has **36,267** data rows and
**36,267** distinct InChIKeys.

| Value | File:line | Verdict |
|---|---|---|
| **36,267** distinct molecules | `cleanroom/RUN_SCREENS.md:110`, `PREREG_MPN621.md:282` | correct |
| **13,293** distinct molecules "(was 2,297)" | `STATE.md:212` | wrong, off by 2.7x |
| **10,547** unique compounds (approved 2,297 + phase 3 885 + phase 2 6,497 + phase 1 868) | `cleanroom/LIBRARIES.md:14-15` | stale; sums correctly to 10,547 |
| **3,273** approved drugs | `COSTS.md:49`, `VIRTUAL_LAB.md:12`, `cleanroom/TARGET_EXPANSION.md:81`, `cleanroom/LIBRARIES.md:28, 104`, `HANDOFF_2026-09-25.md:54` | raw count of the approved subset only |
| "3,273 raw, **2,297** distinct and Boltz-usable" | `PREREG_VSCREEN.md:151` | correct for the approved subset at that date |

Aggravating: `PREREG_VSCREEN.md:148-151` sets the rule that "**the number quoted anywhere must be the
distinct-molecule count from that table**, never the raw line count of a download", and
`cleanroom/RUN_SCREENS.md:108` has a section headed "**What the numbers are, so nobody quotes the
wrong one**". `STATE.md` and `cleanroom/LIBRARIES.md` violate the repo's own written rule for this
exact number.

### X-2. HIGHER_CAL denominator: 54 or 55, and `README.md` mislabels what the 54 is

From `results_higher_cal.json`: `n_pairs_with_strict_cocomplex` 62, `n_labelled` 55,
`n_ambiguous` 1, `n_higher` 12, `n_one_to_one` 42. So 54 pairs enter the tests.

| File:line | Text | Verdict |
|---|---|---|
| `STATE.md:36` | "HIGHER_CAL, **n=54** labelled pairs" | correct |
| `README.md:71-72` | "**n = 54** pairs **with a solved homologous co-complex**" | number right, description wrong. 62 pairs have a solved homologous co-complex |
| `new_biology/MG354_RNAP.md:41` | "Against PDB-derived labels on **55 pairs**, ... sensitivity 75% (9 of 12), a false-positive rate of 12% (5 of 42)" | 12 + 42 = 54, not 55 |
| `RESULTS.md:97` | "62 of 236 pairs have a strict homologous co-complex; **55 got a label** from 1,724 RCSB assemblies (**23 unparseable**, 1 ambiguous). 12 higher-order, 42 one-to-one" | 55 never reconciles to 12 + 42; and the 23 are unparseable *entries* out of 1,724, not pairs, so a reader computes 62 - 23 - 1 = 38 |

### X-3. Quartz, run or blocked

`IP_RECORD.md:7` ("was run") against `cleanroom/quartz/PUSH.md:63` ("Runs so far | none, `logs/` is
empty"), `PUSH.md:3` ("One blocker left, and it is a web click"), `COSTS.md:46`,
`cleanroom/RUN_SCREENS.md:3`, `README.md:186`, `STATE.md:99`. See C-1.

### X-4. Quartz, permitted or forbidden

- `COSTS.md:25-42` records the reversal: "This section used to say 'do not use Quartz, pay the $10 on
  RunPod'. **The screen was subsequently moved onto Quartz.**" Flagged "Superseded on 2026-09-25.
  Read `IP_RECORD.md`, which is the contemporaneous record and governs."
- `COMMERCIAL.md:35` "**Do not run this on Big Red 200 or Quartz** - IU policy UA-24 would then claim
  the IP."
- `PLAN_100K.md:33` "**Rented GPU only, never IU hardware.**"

`COSTS.md` flags its own supersession; `COMMERCIAL.md` does not, and a reader landing on
`COMMERCIAL.md` gets the opposite instruction with no signal that it is stale.

### X-5. Essentiality: resolved in one file, an open item in two

- `RESULTS.md:106` and `new_biology/RNASEJ_MG423.md:75-80`: resolved from Lluch-Senar Table S2.
  MPN280 E/E, MPN621 E/E plus E by colony isolation, 0 transposon insertions each.
- `COMMERCIAL.md:38-39` "**Open item** - the gene-level tables are in supplementary files I could not
  parse"; `:51` "**Resolve essentiality** from the two supplements."
- `PLAN_100K.md:51-61` "## The one open data item, and why it matters most" (mitigated by the
  SUPERSEDED header).

### X-6. `STATE.md` says the MPN621 cleft both is and is not pre-registered

- `STATE.md:163` "## The MPN621 cleft screen: **pre-registered**, stage 1 built, not run", `:165`
  "Four arms: S (MPN621 cleft), N (matched null), O1 (*M. pneumoniae* RNase J ...), O2 (human
  CPSF73 ...)"
- `STATE.md:202-210`, of the same pocket: "**It is not pre-registered and needs its own prereg**,
  whose selectivity arm must compare against *M. pneumoniae* RNase J as well as human CPSF73"

`PREREG_MPN621.md:1` is titled "a small-molecule screen against the MPN621 degenerate cleft" and
`:56-57` are exactly arms O1 (*M. pneumoniae* RNase J) and O2 (human CPSF73). The second paragraph is
`PREREG_VSCREEN` Amendment 4 `:494-498` copied into `STATE.md` and not updated once
`PREREG_MPN621.md` existed. Two paragraphs of the governing document, 40 lines apart, contradict each
other on whether the project's only live screen target has a pre-registration.

### X-7. `new_biology/MG354_RNAP.md` advocates the omega hypothesis before retracting it

- `:18` "That is **the leading hypothesis** and it is stated as a hypothesis below."
- `:58` section heading "## The hypothesis: an unrecognised omega-type subunit"
- `:74-76` "**Consistent with omega:** the size (137 aa), the binding partners (beta and
  beta-prime), and being otherwise functionless in annotation."
- `:85` "The better-supported reading is now **an RNA polymerase-associated protein of unknown
  function, not a missing omega**."

The OMEGA retraction is at `:78`, after 20 lines of advocacy. A reader who stops at `:76`, or who
lands on the section heading from a search result, gets the retracted framing. The document header
(`:3-6`) does say "it is not shown to be omega", which is why this is a contradiction rather than a
live unqualified claim.

### X-8. MMV Pathogen Box: 398 or 400, and the double-count was not fixed

- `cleanroom/RUN_SCREENS.md:112` and `POSTHOC.md:65-66`: "397 of its **398** compounds are already
  inside CO-ADD's ChEMBL deposit"
- `cleanroom/LIBRARIES.md:112` "MMV_PBOX | 1,574 | **400 distinct molecules** (verified by full
  pagination)"; `:252` "returns exactly **400** distinct molecules"

`POSTHOC.md:64-67` explicitly says "any staging plan listing them as two priors (**including the
table in `cleanroom/LIBRARIES.md`**) is counting one set twice." `cleanroom/LIBRARIES.md` was not
corrected.

### X-9. Arm-P job count inside BRIDGE

`PREREG_BRIDGE.md:173` "**18 of 20** arm-P jobs read (`washc5_washc3_p` and **`pard3_pard6b_p`** still
running)". But `cleanroom/bridge/armP_iptm.json` contains **19** entries including
`pard3_pard6b_p` = 0.39, and `cleanroom/bridge/RUN.md:80` and `:101` both say 19. See A-4 for the
knock-on arithmetic.

### X-10. `cleanroom/bridge/results_bridge.json` reports BR/CT scores that the documents say do not exist

The committed file reports `n_pairs` 10, and under `amended`: `B1_prime` BR_only 5, delta 5,
mcnemar_p 0.0625; `B2_prime` BR_only 5, CT_only 0, mcnemar_p 0.0625. Per-pair rows give
`P_iptm_max` 0.145 to 0.178, `BR_iptm_max` 0.816 to 0.830, `CT_iptm_max` 0.217 to 0.249.

- `PREREG_BRIDGE.md:197-198` "B1 and B2 compare arms BR and CT against P, and **neither has been
  run**."
- `STATE.md:61` "BRIDGE | ... **not run**."

The arm-P values in this file (0.145-0.178) do not match the real arm-P values in `armP_iptm.json`
(0.06 to 0.73), and the three arms are implausibly uniform, so the file is almost certainly output
from a test or synthetic run. But `cleanroom/bridge/score_bridge.py` has no `--selftest` flag (it
writes `results_bridge.json` unconditionally at line 323 from whatever directory it is given), and no
`.md` in the repository mentions `results_bridge.json` at all. A reader who opens a file named
`results_bridge.json` in a repository built on the premise "the results files are real" will read it
as a result showing a near-significant bridge effect.

**Fix:** delete it, or rename to `results_bridge_SELFTEST.json` and say so in
`cleanroom/bridge/RUN.md`.

### X-11. The VSCREEN "four defects" are enumerated differently in two places

- `STATE.md:106-119` lists: (1) the decision rule, (2) four molecules in both arms, (3) two MSA
  directories, (4) `pocket[:20]`.
- `PREREG_VSCREEN.md:9-16` lists three mechanical defects (four molecules in both arms; one molecule
  paid for twice in each of two arms; two arms naming two different MSA directories) plus "the fourth
  problem", the decision rule. `pocket[:20]` is not among them; it arrives in Amendment 3.

Both say "four". They are not the same four.

---

## 3. ARITHMETIC AND INTERNAL CONSISTENCY

### A-1. `PREPRINT_DRAFT.md` claims eight negative results and lists nine

`:292-295` and again at `:254-259`: "per-protein normalisation, interface PAE, pool context,
structure-level rescue scores, disease-variant enrichment (twice), literature labels, rigid
composition, and pooled shared partners."

Count: per-protein normalisation (1), interface PAE (2), pool context (3), structure-level rescue (4),
disease-variant enrichment twice (5, 6), literature labels (7), rigid composition (8), pooled shared
partners (9). Nine items, stated as eight.

### A-2. The "8 negatives" figure is now stale by a factor of nearly two

`README.md:32` and `PREPRINT_DRAFT.md:254, 292` both say 8. `RESULTS.md` reports as rejected,
inconclusive, failed-control or closed: H2 (`:71`), H3 (`:72`), HH2 (`:77`), CLINVAR (`:78`),
CLINVAR2 (`:79`/`:81`), LITJEV (`:80`/`:82`), CONTEXT (`:83`), STRUCT (`:84`), COOP arm P (`:86`),
COMPOSE (`:87`), ASSEMBLY (`:100`), ASSEMBLY2 (`:101`), CODEP_R (`:102`), OMEGA (`:104`). That is 14
at minimum, before counting the CODEP withdrawal and XLHUMAN's "0 of 7 are new".

Understating the negative count runs against the repo's own thesis, but it is still a wrong number in
the two most-read files, and an auditor who recounts will find the document undersells by six.

### A-3. `RESULTS.md` duplicates two test rows with different supporting numbers

The "What was tested" table lists CLINVAR2 at both `:79` and `:81`, and LITJEV at both `:80` and
`:82`. The duplicates are not identical:

- `:79` CLINVAR2 reports "control 0.65 [0.14, 1.77]"; `:81` CLINVAR2 reports "Control group had 15
  interface variants" and "13,359/13,359 wild-types matched"
- `:78` CLINVAR reports "the control group had too few ordered interface residues (28 variants)" and
  "37,215/37,215 variant wild-types matched"

A reader counting rows in this table counts 38 tests where there are 36 distinct ones.

### A-4. `PREREG_BRIDGE.md:173-180` has three numbers that disagree with its own cited data file

Against `cleanroom/bridge/armP_iptm.json` (19 entries, 2 at or above 0.50, 17 below, median 0.13,
range 0.06 to 0.73):

| Stated | Actual |
|---|---|
| ":173 **18 of 20** arm-P jobs read" | 19 |
| ":179 ipTM < 0.50, original failure reproduced | **16**" | 17 |
| ":180 median / range | **0.12** / 0.06 to 0.73" | median 0.13 |

The gate verdict is unaffected (2 of 20 against a bar of 4, and `:182-184`'s argument that the gate is
decided before the last data arrive still holds). But this is a reported result inside a
pre-registration, and its three headline counts do not match the JSON it cites.

### A-5. `TARGETS.md` names 14 CORUM pairs for a stated 15

- `:53` "15 are annotated in CORUM. **17 are not**"
- The Not-in-CORUM table (`:60-76`) has exactly 17 rows. Verified.
- The In-CORUM paragraph (`:80-82`) names: TADA2B-TADA1, SUPT7L-TADA1, TADA3-TADA2B, TADA3-TADA1,
  COMMD3-CCDC22, COMMD3-COMMD8, CCDC22-VPS35L, COG5-COG7, SMARCC1-SMARCD2, SMARCC2-SMARCD2,
  NFKB2-RELB, CTBP1-ZEB1, RMND5A-MAEA, AP1G1-AP1M1. That is **14**, then pads with "ISL1-adjacent
  LDB1 pairs", which is vague and appears to re-point at ISL1-LDB1 already listed as non-CORUM at
  `:61`.

`codep_selective_targets.csv` confirms the totals (32 rows; `corum` True 15, False 17), so the
counts are right and the 15th CORUM pair is simply never named. Given the file's own standard, name it.

### A-6. `TARGETS.md:45-49` attributes the 707-to-32 drop to pan-essentiality

"241 of the 707 co-dependent pairs (34%) are pan-essential and are excluded here for that reason."
241/707 = 34.1%, correct. But 707 - 241 = 466 and only 32 survive, so 434 pairs are removed by the
other two thresholds in filter 3 (mean gene effect and dependency fraction). As written the paragraph
reads as if pan-essentiality is the filter that does the work.

### A-7. The "26 and 27 A^3, ratio 1.04" pairing compares two different pockets

From `cleanroom/results_ligandability.json`:

| Model / chain | Cavity | dist to catalytic | fraction of lining at the interface |
|---|---|---|---|
| *M. pneumoniae* RNase J | 26.0 | 14.9 A | 0.20 |
| *M. genitalium* RNase J | **27.0** | **39.5 A** | **0.75** |
| *M. genitalium* RNase J | 26.0 | 15.1 A | 0.222 |

The 27 A^3 cavity quoted as the *M. genitalium* counterpart of the 26 sits 39.5 A from the catalytic
site with 75% of its lining at the interface; the structural counterpart of the 26 is the *other*
*M. genitalium* cavity, also 26.0 A^3, at 15.1 A with 22% interface lining. The conclusion survives
either way, and in fact improves (26/26 = 1.00 rather than 1.04), but the reported pairing makes the
agreement look better-matched than the underlying rows support. Appears at `STATE.md:191`,
`PREREG_VSCREEN.md:444`, `README.md:109`, `cleanroom/RUN_SCREENS.md:7`, `PREREG_MPN621.md:15`.

### A-8. The "four catalytic residues" are not the same four in every file

| File:line | B. subtilis J1 | RNase J | MPN621 | CPSF73 |
|---|---|---|---|---|
| `new_biology/RNASEJ_MG423.md:117-123` | H76, D78, H79, **H368** | H83, D85, H86, **H377** | V71, E73, N74, **N365** | 3/4 |
| `PREREG_VSCREEN.md:475-476` | H76, D78, H79, **H368** | keeps all four | V71, E73, N74, **N365** | keeps three |
| `PREREG_MPN621.md:43-44` | not cited | **H81**, H83, D85, H86 | **N69**, V71, E73, N74 | H71, H73, D75, H76 |

`PREREG_MPN621.md` replaces the fourth, C-terminal position with an extra N-terminal one in both
proteins. "0 of 4 catalytic positions are conserved" is load-bearing for the MPN621 selectivity case
(`README.md:116-118`, `STATE.md:203-204`, `PREREG_MPN621.md:41-48`), so the four positions should be
the same four everywhere it is quoted. Relatedly, `STATE.md:175` describes MPN621's cleft as having
"only E73, D162, D163" as potential metal ligands, a third list used interchangeably with the others.

### A-9. Minor: `RESULTS.md:97` conflates unparseable entries with unparseable pairs

"55 got a label from 1,724 RCSB assemblies (**23 unparseable**, 1 ambiguous)". Per
`results_higher_cal.json`, `n_entries_unparseable` = 23 out of 1,724 **entries**. The 7 pairs lost
between 62 and 55 are pairs for which every entry failed. As written, a reader computes
62 - 23 - 1 = 38.

### Arithmetic that checks out

Verified by recomputation and against the JSON and CSV files:

- FUTURE: 75/84 = 89.3% yeast; 2/110 = 1.8% low-confidence human; 116 + 30 = 146 circularity strata.
- HIGHER_CAL: 9/12 = 75% sensitivity, 5/42 = 11.9% FPR, 9/14 = 64.3% precision, 12/54 = 22.2% base
  rate, 64/22 = 2.9x lift. The C3 variant: 5/12 = 41.7%, 2/42 = 4.8%. All match
  `results_higher_cal.json`.
- HIGHER P1: 0.89 - 0.55 = +0.34.
- Decoy arithmetic: 300/51 = 5.88 expected false winners (`STATE.md:110`, `PREREG_VSCREEN.md:22`);
  BH q<0.10 at the top of 300 needs 2,999 decoys, and at the top of 400 needs about 4,000
  (`STATE.md:123`, `cleanroom/RUN_SCREENS.md:114`). Both correct.
- Gate size: 4 receptors x 60 matched decoys + 10 gate compounds = 250 jobs
  (`PREREG_VSCREEN.md:315-316`). The "five MSAs" at `STATE.md:148` reconciles with four receptors
  because nsp10-nsp14 is two chains (`cleanroom/RUN_SCREENS.md:52`).
- MPN621 staging: 400 compounds x 4 arms = 1,600 jobs; 250 + 800 + 800 + 50 (`PREREG_MPN621.md:255-265`,
  `cleanroom/RUN_SCREENS.md:13-18`).
- `cleanroom/LIBRARIES.md:15`: 2,297 + 885 + 6,497 + 868 = 10,547. Internally consistent, externally
  stale (X-1).
- `TARGETS.md` 15 + 17 = 32, confirmed row-by-row against `codep_selective_targets.csv`.
- Registry 6,010 accession pairs vs 6,009 gene-symbol pairs: reconciled and documented
  (`registry/README.md:31-51`, `POSTHOC.md:24`).
- SEC-MS: 297.8 kDa, 4.7x monomer, 64 + 63 = 127 kDa heterodimer excluded, 254 kDa 2:2 consistent,
  5% of 437 proteins, r = 0.947 at the 97.7th percentile. Identical in `README.md:97`,
  `PREPRINT_DRAFT.md:125`, `RESULTS.md:106`, `new_biology/RNASEJ_MG423.md:98-103`.
- All ligandability figures in `README.md:106-119`, `STATE.md:186-204` and Amendment 4 match
  `cleanroom/results_ligandability.json` (1262/1155, 26/27, 491/470, 273/82, 28% lining,
  calibration 575/76/0).
- `cleanroom/library_master.tsv`: 36,267 rows, 36,267 distinct InChIKeys, 36,267 distinct SMILES.

---

## 4. OVERCLAIMS

### O-1. `PREPRINT_DRAFT.md` abstract gives 81% and 89% with no conservative figure

`:22-24` "Among pairs subsequently solved, their interfaces were correct in **81% of 146 human cases**
and **89% of 84 yeast cases**, against **2%** for low-confidence predictions."

`STATE.md:27-30` makes pairing mandatory: "**Always pair that with the conservative figure.** ...
The honest headline is '53% to 81% depending on how hard you control for circularity'. **Leading with
81% alone is the one place this project has been doing the thing it tells everyone else not to do.**"

In `PREPRINT_DRAFT.md` the 53% appears at `:106` (a table cell), `:187` and `:196-198`
(Limitations). It is absent from the abstract, absent from the results headline at `:84-95`, and
absent from the Discussion's opening restatement at `:137-141`. The abstract is what gets indexed,
quoted and pasted into emails.

`README.md:8-16` does this correctly and is the model to copy: headline, then "**Read that as a
range, not a number**", then 53%, then "The defensible claim is **53% to 81%**".

### O-2. `PREPRINT_DRAFT.md:32` and `:179-182` still recommend the interface for drug work

`:32` "The interface **merits experimental study** but is not a validated antibacterial target."
`:179` "For drug discovery, **the interface could be investigated experimentally**." The preprint
contains no cavity measurement anywhere, so a reader has no way to know that the project's own
pre-registered scan puts that interface at 26 and 27 A^3 against 76 for the shallowest drugged
reference. See C-10.

### O-3. `new_biology/RNASEJ_MG423.md:83-84` "a protein-protein-interface target by definition"

Stated without qualification, as the takeaway of the essentiality section, in the file `README.md:138`
and `README.md:155` point readers to for the biology. Amendment 4 measured that interface as flat on
both sides. The rest of this file is the most carefully hedged document in the repository, which makes
the one unhedged sentence stand out more, not less.

### O-4. `COMMERCIAL.md:80` "We have a validated target". See C-9.

### O-5. `VIRTUAL_LAB.md:78-81`

"measured antibacterial activity against an essential, **structurally validated target**. That is the
entry criterion for **PACE** ... and **CARB-X**. **This is the only route on the board that reaches
seven figures.**" Three claims, all unsupported: the target is not validated, neither funder is open
to this organism, and the "seven figures" conclusion depends on both.

### O-6. `VIRTUAL_LAB.md:12` lists the interface compound-ranking step as "built"

"**built** (`cleanroom/vscreen.py`, 3,273 approved drugs, decoy null, CPSF73 selectivity arm)". The
target is cancelled, the library count is stale by an order of magnitude (X-1), the decoy null's
decision rule was retracted as firing on noise 86% of the time, and
`cleanroom/quartz/PUSH.md:78-80` records that the selectivity arm "**did not exist**" until
2026-09-25. The file's own honest framing at `:24-25` ("a virtual lab produces **ranked hypotheses**")
is undercut by its own table.

### O-7. `CONCEPT.md:3-8` headline unpaired, and the file is undated

"the predicted interface is right about **80-90% of the time**". The conservative bound is at `:18`
(an evidence-table row) and `:58` ("the human X-ray subset gives about half, not 80%"), both below the
Claim. `CONCEPT.md` carries no date and no pointer to `STATE.md`, so a reader arriving directly reads
it as the project's current thesis statement.

### O-8. `cleanroom/TARGET_EXPANSION.md:38-41` states 0.75 confidence in a recommendation since rejected

See C-11. The stated reason for the confidence is the cross-ortholog reproduction that Amendment 4
measured and falsified, using a comparison of non-comparable cavities.

### O-9. `README.md:33` "Claims were retracted when checks failed, and the retractions are in the history"

True for RpoC-RpoB, MG354/omega, CODEP, the 141 folds and the p=0.028 result. Not true for the
PACE/CARB-X retraction (C-8), the interface-as-drug-target retraction (C-10), or
`cleanroom/TARGET_EXPANSION.md`'s recommendation (C-11). This sentence is the repository's central
promise, which means every unpropagated retraction falsifies it directly rather than merely leaving
a stale file behind.

### O-10. `README.md:151` "`RESULTS.md` | every test and its numbers"

`RESULTS.md` has no row for BRIDGE (arm P run, gate passed, reported only inside
`PREREG_BRIDGE.md`), no row for the ligandability measurement (the most decision-relevant result of
the last two days, reported only in `PREREG_VSCREEN` Amendment 4 and `STATE.md`), and no row for
VSCREEN, MPN621 or VIBRIO.

### O-11. Minor: `TARGETS.md:110` priority claim

"as far as I can tell, **nobody has produced this particular intersection before**." Hedged, and the
file's retraction header is the best in the repository. Noted only because it is an unfalsifiable
priority claim in a file that otherwise sets the standard.

---

## 5. STALE FILES AND THE MINIMAL HEADER EACH NEEDS

Ordered by how much damage a direct arrival from a search engine does.

### 1. `IP_RECORD.md`

```
> **CORRECTION 2026-09-26: the screen described below has NOT been run.** No Boltz-2 job has executed
> on Quartz or anywhere else (`cleanroom/quartz/PUSH.md` records "Runs so far: none";
> `cleanroom/RUN_SCREENS.md` records "neither has been run"). This file records the compute decision
> and the UA-24 reading made in advance of a run, so read every past-tense verb below as a plan.
> Note also that `STATE.md` now lists an RT Project join with a named PI as a blocker on Quartz GPU
> access, which bears on the "self-service, no sponsor" premise this reading rests on.
```

### 2. `VIRTUAL_LAB.md` (no header of any kind at present)

```
> **SUPERSEDED IN PART, 2026-09-26.** PACE and CARB-X are both scoped to Gram-negative priority
> pathogens and *M. pneumoniae* is on neither list, so step 5 and the "only route to seven figures"
> line do not hold (`COSTS.md`, `README.md`). The target is **not** validated. The RNase J : MPN621
> interface is measured non-ligandable and its screen is cancelled (`PREREG_VSCREEN` Amendment 4), so
> the "built" row in the first table points at a cancelled target and a stale library count. Read
> `STATE.md`.
```

### 3. `COMMERCIAL.md`

```
> **SUPERSEDED IN PART, 2026-09-26.** "We have a validated target" is wrong: there is no wet-lab
> validation and the interface is measured non-ligandable (`PREREG_VSCREEN` Amendment 4). PACE and
> CARB-X are not open to this organism (`COSTS.md`). Essentiality is no longer an open item
> (`RESULTS.md`, row ESSENTIAL + SEC). The Quartz guidance here is the opposite of `COSTS.md` and
> `IP_RECORD.md`. Read `STATE.md`.
```

### 4. `cleanroom/TARGET_EXPANSION.md`

```
> **ITS MAIN RECOMMENDATION WAS REJECTED, 2026-09-26.** `PREREG_VSCREEN` Amendment 4 re-measured
> MPN621's 273 A^3 interface cavity on the second ortholog model and got 82 A^3, so the
> recommendation to re-aim the screen at that cavity is **not adopted**. The "419 and 470 A^3 in the
> *M. genitalium* ortholog model" quoted below are both catalytic-proximal cavities and are not the
> counterpart of the 273. Read Amendment 4 before anything in this file.
```

### 5. `cleanroom/POSITIVE_CONTROLS.md`

```
> **The interface screen this survey was written for is cancelled** (`PREREG_VSCREEN` Amendment 4).
> The gate survives unchanged and this file is still its source, but the Tier A/B accounting is now
> Amendment 3 plus its addendum: two representable rungs, not five.
```

### 6. `cleanroom/LIBRARIES.md`

```
> **Numbers superseded.** `library_master.tsv` now holds **36,267** distinct molecules, not 10,547;
> quote `cleanroom/RUN_SCREENS.md`. The MMV Pathogen Box is **not** an independent prior (397 of 398
> are inside CO-ADD, `POSTHOC.md`) and its count is 398, not 400. The target is no longer the RNase J
> interface.
```

### 7. `COSTS.md`

Has a partial self-correction at `:95-115`, but `:127` still instructs applying to PACE and CARB-X,
and `:15`, `:49`, `:72-73` describe the cancelled interface screen with the retracted decision rule
and a stale library. Minimum: delete or strike `:127`, and add above §2:

```
> Section 2 and the step list describe the RNase J **interface** screen, which is cancelled
> (`PREREG_VSCREEN` Amendment 4). The current plan is the gate plus the MPN621 cleft
> (`cleanroom/RUN_SCREENS.md`), and the "beats every decoy" purchase rule below was retracted as
> firing on noise about 86% of the time.
```

### 8. `cleanroom/rnap3/RUN.md`

```
> **RNAP3 has run** (AlphaFold Server, 2026-09-25) and is reported SUPPORTED in `RESULTS.md`. This
> file is kept as the recipe for a Boltz-2 re-run under an unrestricted licence.
```

### 9. `CONCEPT.md` (undated, no pointer to `STATE.md`)

```
> Written 2026-09-23. For current status and retractions see `STATE.md`. The 80-90% figure is
> conditional on the pair later being solved (2.7% of confident calls) and is **53% (n = 19)** on the
> X-ray-only subset.
```

### 10. `new_biology/MG354_RNAP.md`

No header needed; the header at `:3-6` is already correct. The minimal fix is ordering: move the
OMEGA update from `:78-85` to directly under `:18`, or change `:18` from "That is the leading
hypothesis" to "That was the leading hypothesis; its fold argument is gone, see the OMEGA update
below." Also correct `:41` from 55 pairs to 54.

### 11. `PREREG_VSCREEN.md` and `PREREG_BRIDGE.md`

Bodies must not be rewritten; that is the point of a pre-registration. Each needs one appended
amendment:

- VSCREEN: "Correction to Limitations: 'five independent published lines' should read 'five published
  lines from three independent studies' (`new_biology/RNASEJ_MG423.md`)."
- BRIDGE: "The CODEP premise in the Why section was withdrawn on 2026-09-25 by `PREREG_CODEP_R`;
  BRIDGE's design is unaffected but its prior is lower. Arm P arithmetic correction: 19 of 20 read,
  17 below 0.50, median 0.13; the gate verdict is unchanged."

### 12. `PLAN_100K.md`

Header is adequate, but it points to `../MONEY.md`, which is outside the repository and unreachable
to any public reader. Add one clause: "(`MONEY.md` is not public; see `STATE.md` for current
status.)"

### 13. `vibrio_pilot/README.md:15`

A mangled uppercase duplicate of line 14, apparently a copy-paste artefact. Cosmetic, but it is a
public file in a repository whose credibility argument is "we are careful."

### 14. The four `HANDOFF_*.md`

All carry SUPERSEDED headers, which is correct and is why they are not in §1. But every header names
the same three stale items (RpoC-RpoB, omega, XLHUMAN) and none names the CODEP withdrawal, the
PACE/CARB-X correction, the ligandability result or "five independent lines". One clause would cover
it: "Also stale: the CODEP functional claim (withdrawn), PACE/CARB-X eligibility (retracted), the
interface as a drug target (measured non-ligandable), and 'five independent published lines' (it is
five lines from three studies)."

---

## 6. VERIFIED

Checked and found sound. This section is as important as the others; most of the repository holds up.

**The pre-registration discipline is visibly real in the files.** Every `PREREG_*.md` opened states
its write date and what had not yet been looked at, in specific terms ("committed `0da2677` before
any DepMap file was downloaded", "before any assembly record was fetched", "before any Boltz-2
affinity score exists"). Amendments are appended rather than edited into the body, and
`PREREG_BRIDGE.md:113-119` explicitly justifies an amendment as prospective. `PREREG_HIGHER_CAL.md`
goes further and declares the analyst's textbook prior knowledge at `:20-26` before the test. This is
the repository's strongest asset and it survives inspection.

**The retractions that were propagated were propagated well.**

- RpoC-RpoB: correct and consistent at `README.md:67`, `STATE.md:40-43`, `RESULTS.md:97`,
  `new_biology/MG354_RNAP.md:32` (struck through, with "Removed from this list"),
  `HANDOFF_2026-09-25_evening.md:64`. The 367-of-370 figure matches
  `results_higher_cal.json` exactly, as does RpoA-RpoB at 352 of 356. The Nap adhesin is demoted to
  ambiguous everywhere it appears (1 vs 1 in the JSON).
- MG354's ipTM: the 0.910 is correctly attributed to the RpoB-RpoC control at
  `new_biology/MG354_RNAP.md:96`, `RESULTS.md:103`, `cleanroom/TARGET_EXPANSION.md:98` and
  `cleanroom/bridge/RUN.md:84`, and MG354's own 0.57/0.43 is stated alongside it in each. The
  `STATE.md:221` correction is in force. 1TM9 is cited as MG354's existing NMR structure at
  `STATE.md:46`, `README.md:68`, `new_biology/MG354_RNAP.md:87-90` and `RESULTS.md:104`, with
  "uncharacterized in function, not in structure" stated in all four.
- CODEP: the withdrawal is thorough. `RESULTS.md:99` and `:102` cross-reference each other and
  `:99` ends with "Read the two rows together and **cite neither alone**". `TARGETS.md:3-23` leads
  with a five-paragraph retraction block before the list. `STATE.md:63-94` includes the
  sensitivity-scaling argument that forecloses the underpowering excuse. This is a model for how the
  other retractions should have been handled.
- "141 novel folds", "new protein fold" and the foldnovelty p=0.028 result: **no live assertion
  anywhere.** All occurrences are inside explicit do-not-claim lists (`STATE.md:17-18`,
  `HANDOFF_2026-09-25_evening.md:15`, `HANDOFF_2026-09-25_v2.md:93-108`). The only other "141" in the
  repository is an H200's VRAM at `cleanroom/rnap3/RUN.md:10`.

**The 81% / 53% pairing is done correctly in `README.md`.** `:8-16` is the right template: headline,
explicit instruction to read it as a range, the 53% with its CI, and the conditionality on later
solving at `:10-11`. `:46-48` adds the selection limit directly under the results table. `README.md`
is the strongest document in the repository.

**The conditionality caveat is stated wherever the 81% appears** except the preprint abstract:
`README.md:10-11`, `:46-48`, `PREPRINT_DRAFT.md:94-95`, `:140-141`, `RESULTS.md:54-60`,
`CONCEPT.md:55-56`, `STATE.md:31-32`.

**Numbers that reconcile across every file that quotes them:** the AUROC splits (0.806 and 0.877
reproduction; 0.85 n=1,806 vs 0.71 n=827; 0.95 n=65 vs 0.57 n=171; 0.917 vs 0.636 human), the five
VERIFY attacks and their results, the COOP-H miss characterisation (27% vs 11%, 10.5 vs 6 entities,
30 vs 85 contacts), the threshold grid (57% to 88%, 81% at the registered setting), the AFJ ipTM
values (0.83-0.84 tetramer, 0.81-0.82 J-partner, 0.12-0.17 decoy, 0.50 vs 0.81 self-association), and
the SEC-MS block.

**The "five published lines from three independent studies" accounting** at
`new_biology/RNASEJ_MG423.md:48-65` is exemplary: it names the two collisions, explains why the second
crosslinker rules out an artefact rather than adding an observation, and says outright "claiming five
independent lines was not supportable and this table is the reason." `STATE.md:34` uses it correctly.
Only `PREREG_VSCREEN.md:135` and the two superseded handoffs still carry the old phrasing.

**`POSTHOC.md` is scrupulous throughout.** The PH-DRUG join is labelled descriptive, self-limits at
`:31-35` ("it must never be presented as the latter"), documents the 131-to-92 dedup, quantifies its
own dominant confound at `:50-62` (46 of 92 rows carry one HDAC string, 51 carry vorinostat), and
catches a separate double-count in `cleanroom/LIBRARIES.md` at `:64-67`.

**`registry/README.md` resolves the 6,010 / 6,009 discrepancy properly** at `:31-51`, naming the
single responsible gene pair and its two accessions, and gives a rule for which number to quote.

**`cleanroom/RUN_SCREENS.md` is clean, current and correct**, including the cancellation notice at
`:6-9`, the correct library figure, and a "What the numbers are, so nobody quotes the wrong one"
section. `cleanroom/BOLTZ_SCHEMA.md` is verified against named source files at a pinned commit and
flags what it could not execute.

**Amendment 4 of `PREREG_VSCREEN` is the best piece of self-correction in the repository.** It
measures the thing, ranks its three conclusions by how well supported each is, refuses to adopt the
recommendation it came from, declines to authorise the replacement screen without its own
pre-registration, and lists four limits on itself. Every number in it matches
`cleanroom/results_ligandability.json` apart from the pocket-pairing detail in A-7.

**Pre-registration to result coverage:** 28 of the 33 pre-registrations have a reported result in
`RESULTS.md` or an in-file result section. The five exceptions are named in C-4. No pre-registration
was found whose result had been quietly dropped, which is the failure mode that would actually matter.

---

## Appendix: the shortest path to fixing this

In order of damage per minute of work:

1. `IP_RECORD.md` header and tense (C-1, C-2).
2. `STATE.md`: RNAP3 into the closed table (C-3); soften the no-prereg-without-result claim (C-4);
   BRIDGE status (C-5); delete the stale "not pre-registered" paragraph at `:202-210` (X-6); library
   figure to 36,267 (X-1).
3. Headers on `VIRTUAL_LAB.md`, `COMMERCIAL.md`, `cleanroom/TARGET_EXPANSION.md` (C-8, C-9, C-10,
   C-11). Strike `COSTS.md:127`.
4. One authoritative pre-registration count, used in `README.md:32`, `README.md:150` and
   `PREPRINT_DRAFT.md:294`; renumber the two collisions (C-12). Fix the negatives count in the same
   pass (A-1, A-2).
5. `PREPRINT_DRAFT.md`: the 53% into the abstract; drop or qualify the drug-development sentences
   (O-1, O-2).
6. Two appended amendments, to `PREREG_VSCREEN.md` and `PREREG_BRIDGE.md` (C-6, C-7, A-4).
7. Delete or rename `cleanroom/bridge/results_bridge.json` (X-10).
8. De-duplicate the four repeated rows in `RESULTS.md` and add rows for BRIDGE and ligandability
   (A-3, O-10).
