# Getting the screen onto Quartz

Data and jobs live locally at `af3-hitcall/cleanroom/`. Quartz login node is `quartz.uits.iu.edu`.
Replace `USERNAME` with your IU username.

## 1. Push (from Git Bash on the laptop)

    cd "/c/Users/bmens/OneDrive - Indiana University/NQ_Project/af3-hitcall/cleanroom"
    ssh USERNAME@quartz.uits.iu.edu 'mkdir -p ~/af3screen/{yaml,msa,quartz,logs}'
    scp vscreen_yaml/*.yaml  USERNAME@quartz.uits.iu.edu:~/af3screen/yaml/
    scp msa/P75497.a3m       USERNAME@quartz.uits.iu.edu:~/af3screen/msa/
    scp quartz/*             USERNAME@quartz.uits.iu.edu:~/af3screen/quartz/

The YAMLs already point at `/workspace/screen/msa/P75497.a3m`, which is the **pod** path, not the
Quartz path. Fix it on the remote in one line:

    ssh USERNAME@quartz.uits.iu.edu "sed -i \"s|/workspace/screen/msa|\$HOME/af3screen/msa|\" ~/af3screen/yaml/*.yaml"

Or regenerate locally before pushing, which is cleaner:

    py vscreen.py --write --limit 300 --msa-prefix /N/u/USERNAME/Quartz/af3screen/msa
    py vscreen.py --write --limit 300 --decoys 50 --msa-prefix /N/u/USERNAME/Quartz/af3screen/msa
    py validate_jobs.py

## 2. Set up (on the login node, once)

    cd ~/af3screen && bash quartz/setup_login.sh

Login nodes have internet, compute nodes do not. This stages the venv, boltz, and the model weights.
If it exits with "no model checkpoint landed in the cache", stop: the batch job cannot recover from
that offline.

## 3. Confirm the partition before submitting

The `#SBATCH` lines in `screen.slurm` guess `--partition=gpu` and `--gres=gpu:v100:1`. Verify:

    sinfo -o '%P %G %N' | sort -u
    slurm-list-accounts 2>/dev/null || sacctmgr -n show assoc user=$USER format=account

Edit the header if either differs, and add `#SBATCH --account=...` if Quartz requires one.

## 4. Probe, then run

    cd ~/af3screen
    sbatch --export=ALL,PROBE=1 --array=0 quartz/screen.slurm
    # read logs/af3screen_*_0.out: bf16 support, seconds per job, projected wall clock
    sbatch --array=0-7 quartz/screen.slurm

**The thing most likely to go wrong:** V100 is Volta (sm_70) with no hardware bfloat16. The probe
prints `bf16 supported:` and tries all three dtypes before any real work. If boltz then fails on
bf16, the fix is to force fp32 and accept roughly 2-3x the runtime, which is still fine because
eight V100s in parallel are doing the work.

## 5. Collect

    ssh USERNAME@quartz.uits.iu.edu "cd ~/af3screen && find out \( -name 'affinity_*.json' -o -name 'confidence_*.json' \) | tar czf screen_results.tar.gz -T -"
    scp USERNAME@quartz.uits.iu.edu:~/af3screen/screen_results.tar.gz .
    tar xzf screen_results.tar.gz -C vscreen_out --strip-components=0
    py vscreen.py --rank
