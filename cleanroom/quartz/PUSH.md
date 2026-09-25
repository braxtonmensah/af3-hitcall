# Running the screen on Quartz

**Status 2026-09-25: everything is staged and validated on Quartz. One blocker left, and it is a
web click, not a command.** See "The one blocker" below.

## Facts about the account, corrected 2026-09-25

Verified by logging in, not assumed:

| | Value |
|---|---|
| SSH login user | **`bmensah`** (every earlier doc said `bsmensah`, which is the *group*) |
| Home | `/N/u/bsmensah/Quartz` = `/geode3/home/u015/bsmensah/Quartz` (same place, two mounts) |
| Login node | `h1.quartz.uits.iu.edu` |
| GPU partitions | `h100-single` (50 nodes), `h100-multi` (12), `h100-debug` (2), `v100` (24) |
| Slurm association | **none.** `sacctmgr show assoc user=bmensah` returns nothing |

The old "no association" diagnosis was run against the wrong username. It was re-checked with the
right one and the blocker is real either way.

## The one blocker

    sbatch: error: You must include an RT Project with the -A flag to this command.
                   Please see https://kb.iu.edu/d/bihc

`AccountingStorageEnforce = associations,limits,qos`, so no association means no job on any
partition, including `debug`. Groups already include `iu-entlmt-app-rt-quartz-users`, so the Quartz
entitlement is there; what is missing is a Slurm account.

**Fix, and it is a click not a form:** at `projects.rt.iu.edu`, log in, search PI **`lamhuber`**,
find **"HPC and AI for Students"** (the exact title; earlier notes said "HPC for Students"), click
**Request Access**. Laura Huber runs five projects and only this one is the student project, so check
the title before clicking. Creating a *new* project would require naming a PI; joining this one does not.

**Requested 2026-09-25, awaiting Laura Huber's approval.** The button now reads "Sent!".

**There is a second step after approval.** The RT Projects home page says "Users must be added to an
allocation in order to gain access to its resource", and `/allocation/` is still empty. Being added to
the project may not by itself create the Slurm association. After the approval email arrives, check:

    sacctmgr -n show assoc user=$USER format=account%30

If that is still empty while the project shows up under My Projects, the missing piece is the compute
allocation, which is requested from inside the project page and may also need the PI to approve.

Then:

    sacctmgr -n show assoc user=$USER format=account%30      # get the account name
    cd ~/af3screen && sbatch -A <account> --array=0-7 quartz/screen.slurm

Add `#SBATCH --account=<account>` to `quartz/screen.slurm` so it is not needed on the command line.

## What is already done (verified, not assumed)

| Piece | State |
|---|---|
| Bundle | pushed and unpacked at `~/af3screen` |
| venv | boltz **2.2.1**, torch **2.14.0+cu130** |
| Model weights | **12 GB cached** in `boltz_cache/` (`boltz2_conf.ckpt`, `boltz2_aff.ckpt`) |
| Jobs | **650 validated**: 300 screen, 50 decoy, 300 off-target |
| MSAs | `P75497.a3m` (target), `Q9UKF6.a3m` (human CPSF73) |
| MSA paths | resolve on Quartz; no CR corruption |
| Runs so far | none, `logs/` is empty |

`scp` and `ssh` both ride the WSL master socket, so Claude can transfer files and run commands for
12 hours after one `ssh quartz` login. The old note that scp needs its own Duo prompt predates that.

## Two bugs found and fixed on 2026-09-25

**1. `validate_jobs.py` could not run on Quartz, and `--prune` would have emptied the run
directory.** `YDIR` was hardcoded to `vscreen_yaml`, but the bundle ships the jobs as `yaml/`; and
the MSA check required the hardcoded RunPod prefix `/workspace/screen/msa/`, so all 350 jobs failed
as "not pod-side" on Quartz. **Never run `--prune` without reading the unpruned report first.** Now
the directory is auto-detected (or set `YAML_DIR`), and the MSA check resolves the path instead of
matching one host's layout.

**2. The selectivity arm did not exist.** The CPSF73 MSA was staged and `vscreen.py --offtarget`
existed, but zero off-target jobs had ever been generated, so `--rank`'s selectivity check would
have printed nothing. 300 off-target jobs now exist, over the same 300 compounds.

**Generate them with `MSYS_NO_PATHCONV=1`.** Without it, Git Bash rewrites the `--msa-prefix`
argument from `/N/u/...` to `N:/u/...` and every job gets an MSA path that cannot resolve on Linux:

    MSYS_NO_PATHCONV=1 py -3.11 vscreen.py --write --offtarget --limit 300       --msa-prefix "/N/u/bsmensah/Quartz/af3screen/msa"

## A methodological asymmetry to state, not to hide

Target jobs carry a `pocket` constraint steering the ligand to the PPI interface. **Off-target
(CPSF73) jobs carry no pocket constraint**, because CPSF73 is the monomeric human relative and has no
corresponding interface to constrain to. So the two arms are not scored under identical conditions:
the target is restricted to one site while the off-target search is free to find its best site
anywhere. Read the selectivity column as indicative, and say so in anything published from it.

## Why the original runbook said Claude could not do this

Quartz offers these SSH auth methods today:

    gssapi-keyex, gssapi-with-mic, password, keyboard-interactive

No `publickey`. Key authentication is off until you submit IU's **"SSH public-key authentication to
HPS systems"** user agreement. Until then every login and every `scp` needs your passphrase plus a
Duo push, which Claude cannot do. So the three commands below are yours.

Worth doing once if this becomes recurring: submitting that agreement enables key auth **and**
exempts you from Duo on these systems, because a passphrase-protected key already counts as two
factors. Note the agreement requires a passphrase on the private key, so your existing
`~/.ssh/id_ed25519` (no passphrase, used for Runpod) does not qualify. It would need a new key.

## The three commands

Everything is packaged into one 2.6 MB tarball so this is a single transfer, not 351 files.

**1. Push** (Git Bash on the laptop, one Duo prompt):

    scp "/c/Users/bmens/OneDrive - Indiana University/NQ_Project/af3-hitcall/cleanroom/af3screen_bundle.tar.gz" bsmensah@quartz.uits.iu.edu:~/

**2. Set up** (on the login node, one Duo prompt):

    ssh bsmensah@quartz.uits.iu.edu
    tar xzf af3screen_bundle.tar.gz && cd af3screen && bash quartz/setup_login.sh

That builds the venv, installs boltz, pre-downloads the model weights, and rewrites every job's MSA
path from `$HOME` so there is no guessing about IU's home directory convention. It hard-fails if the
weights do not land, because compute nodes have no internet and the batch job could not recover.

**3. Probe one job, then launch:**

    sinfo -o '%P %G %N' | sort -u          # confirm the partition and gres syntax first
    sbatch --export=ALL,PROBE=1 --array=0 quartz/screen.slurm
    cat logs/af3screen_*_0.out             # bf16 support, seconds/job, projected wall clock
    sbatch --array=0-7 quartz/screen.slurm

Paste me the probe output and I will take it from there.

## What the probe is checking

V100 is Volta (sm_70) with **no hardware bfloat16**, and Boltz-2 reaches for bf16. The probe prints
`bf16 supported:` and tries fp32/fp16/bf16 on the GPU before any real work, so this surfaces in one
job instead of eight hours in. If bf16 fails the fix is to force fp32 and accept roughly 2-3x per
job, which is still fine across eight GPUs in parallel.

The `#SBATCH` header guesses `--partition=gpu` and `--gres=gpu:v100:1`. `sinfo` above confirms or
corrects it. Add `#SBATCH --account=...` if Quartz requires one:

    sacctmgr -n show assoc user=$USER format=account

## Collecting results

    cd ~/af3screen && find out \( -name 'affinity_*.json' -o -name 'confidence_*.json' \) | tar czf screen_results.tar.gz -T -

then from the laptop:

    scp bsmensah@quartz.uits.iu.edu:~/af3screen/screen_results.tar.gz "/c/Users/bmens/OneDrive - Indiana University/NQ_Project/af3-hitcall/cleanroom/"
    cd "/c/Users/bmens/OneDrive - Indiana University/NQ_Project/af3-hitcall/cleanroom"
    mkdir -p vscreen_out && tar xzf screen_results.tar.gz -C vscreen_out
    py vscreen.py --rank

`--rank` reports the decoy null first. If no real compound beats every decoy, the screen found
nothing, and that is a valid cheap answer that closes the compound route rather than a failure.

## Rebuilding the bundle

If the jobs are regenerated, rebuild before pushing:

    cd "/c/Users/bmens/OneDrive - Indiana University/NQ_Project/af3-hitcall/cleanroom"
    mkdir -p .bundle/af3screen && cp -r vscreen_yaml .bundle/af3screen/yaml \
      && mkdir -p .bundle/af3screen/msa && cp msa/*.a3m .bundle/af3screen/msa/ \
      && cp -r quartz .bundle/af3screen/quartz && cp vscreen.py validate_jobs.py .bundle/af3screen/ \
      && (cd .bundle && tar czf ../af3screen_bundle.tar.gz af3screen) && rm -rf .bundle
