# Running the screens

Two screens are built and neither has been run. Read `../STATE.md` first, then this. Everything below
costs nothing until the `run_screen.sh` step, which is the only one that touches a GPU.

**The interface screen is cancelled.** `PREREG_VSCREEN` Amendment 4 measured the RNase J : MPN621
interface and found it flat on both sides (26 and 27 A^3 of non-catalytic cavity across two ortholog
models, against 76 for the shallowest drugged reference). `cleanroom/vscreen_yaml/` and
`pod_run.sh` belong to that screen. Do not run them.

## Order, and why it is this order

| # | Stage | Jobs | GPU-hours | Gate on the next stage |
|---|---|---|---|---|
| 1 | **Gate** | 250 | 3-6 | Tier A must pass or nothing else is interpreted |
| 2 | **MPN621 arms S + N** | 800 | 10-20 | M1 must enrich or there is no shortlist |
| 3 | **MPN621 arms O1 + O2** | 800 | 10-20 | M2/M3 gate any purchase |
| 4 | **MPN621 arm Z** | 50 | <1 | metal sensitivity; M2/M3 conditional without it |

Stage 1 decides whether the method can recover known ligands of related folds at all. Its most likely
outcome (Tier A passes, Tier B fails) means the method finds active sites and not interfaces, which is
fine here because stage 2 targets a cleft, not an interface. Stage 3 is held back because it answers a
per-compound purchase question and a null M1 deletes the question.

## 1. Check everything without spending anything

    cd cleanroom
    py -3.11 test_pipeline.py                       # 20 checks, end to end, seconds
    py -3.11 score_gate.py --selftest               # 4 checks
    py -3.11 score_mpn621.py --selftest --selection selection_v2.tsv   # 8 checks

All three must pass. The scorers are self-testing because this repo has shipped a scorer whose
filename regex matched nothing and reported a passing gate over zero pairs.

## 2. Ship a job set to the GPU

Both job sets carry pod-side MSA paths (`/workspace/gate/msa`, `/workspace/mpn621/msa`). Stage the
matching MSAs next to them.

    # what each set needs
    py -3.11 check_msa_paths.py gate_jobs --msa-dir msa
    py -3.11 check_msa_paths.py mpn621_jobs --msa-dir msa

Exit codes: `0` paths resolve here, `3` files present but written for another host (normal before
shipping), `4` files absent anywhere, `5` carriage returns in the jobs. Anything but 0 or 3 must be
fixed before shipping.

MSAs required:

| Set | MSA files |
|---|---|
| gate | `cpsf73_A.a3m`, `snm1a_A.a3m`, `artemis_A.a3m`, `nsp1014_A.a3m`, `nsp1014_B.a3m` |
| mpn621 S/N | `P75174.a3m` |
| mpn621 O1/O2 | `P75497.a3m`, `Q9UKF6.a3m` |

All seven are already in `cleanroom/msa/`. The gate's five are keyed to the **trimmed constructs**,
not to UniProt accessions, and each was verified to match the sequence in its job. Do not substitute
a full-length MSA: 6M8Q's construct is 459 residues against Q9UKF6's 684, so the columns would not
correspond.

Then, on the pod, with `msa/` and the job directory both present:

    RATE=0.34 bash run_screen.sh gate_jobs preflight   # checks only
    RELINK=1 bash run_screen.sh gate_jobs preflight    # rewrite paths for THIS host
    bash run_screen.sh gate_jobs bench                 # 3 jobs, then project time and cost
    bash run_screen.sh gate_jobs                       # the rest; resumable

`bench` prints a projection before committing to the full set. The run is resumable: an interruption
costs one chunk, not the run, and resume understands both output layouts Boltz has used.

## 3. Score

    py -3.11 score_gate.py --out-dir out_gate_jobs --json results_gate.json

Read the gate's verdict before anything else. Then, only if Tier A passed:

    py -3.11 score_mpn621.py --jobs mpn621_jobs --out-dir out_mpn621_jobs \
        --selection selection_v2.tsv --json results_mpn621.json

## 4. If M1 enriches, build stage 3 and 4

    MSYS_NO_PATHCONV=1 py -3.11 build_mpn621.py --selection selection_v2.tsv \
        --msa-prefix /workspace/mpn621/msa --arms O1,O2 --out-dir mpn621_jobs
    # after arm S is scored, with its shortlist as CSV:
    MSYS_NO_PATHCONV=1 py -3.11 build_mpn621.py --selection selection_v2.tsv \
        --msa-prefix /workspace/mpn621/msa --arm-z shortlist.csv --out-dir mpn621_jobs

## Things that have cost a cycle here

- **`MSYS_NO_PATHCONV=1`** before any command taking a POSIX `--msa-prefix`. Git Bash rewrites
  `/workspace/...` into `C:/Program Files/Git/workspace/...` silently; it once got baked into 1,200
  job files. The builders now refuse a Windows-looking prefix, but the env var is still the fix.
- **Never truncate a pocket by residue number.** `pocket[:20]` on the interface kept residues 25-357
  and discarded 358-569, aiming the constraint at the catalytic-proximal half.
  `build_screen_jobs.require_pocket` refuses rather than truncating; supply a geometric list from
  `cavity_residues.py`.
- **grep cannot find carriage returns in Git Bash** without `-U`; it opens files in text mode and
  strips them. The CR check lives in `check_msa_paths.py` for this reason.
- **`manifest.json` legitimately has CRLF** (Windows text-mode output) and Boltz never reads it, so
  CR checks are scoped to `*.yaml`.
- **Score direction inverts easily.** `affinity_probability_binary` is higher for a binder and is what
  ranks. `affinity_pred_value` is log10 IC50 in micromolar, so **lower is stronger**. `vscreen.py
  --rank` prints the latter with no direction stated.
- **The affinity head cannot see ions.** Supplying metals fixes the pose, not the score, so a
  metal-chelating ligand cannot be scored for what makes it bind. Three gate rungs are diagnostics
  for this reason.

## What the numbers are, so nobody quotes the wrong one

- Library: **36,267 distinct molecules**, deduplicated on InChIKey after desalting. Not the raw row
  count of any download; on the approved set alone those differ by 30%.
- The MMV Pathogen Box is **not** an independent prior: 397 of its 398 compounds are inside CO-ADD.
- Per-compound significance is **unreachable** at this null size. The floor on an empirical p is
  1/(n_null+1), so the top of 400 compounds would need about 4,000 decoys for BH q<0.10. The
  shortlist is hypotheses, never hits.
- Boltz-2's own blinded out-of-distribution ceiling is **mean Pearson R 0.39**. This target is out of
  distribution on every axis.
