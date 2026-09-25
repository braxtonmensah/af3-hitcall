# Running the screen on Quartz

Account `bsmensah` requested 2026-09-25, provisioning takes up to 24 hours. Quartz is reachable now
(`quartz.uits.iu.edu` answers), so the only wait is provisioning.

## Why you have to run these and not Claude

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
