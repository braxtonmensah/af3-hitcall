# Running Boltz-2 on IU Quartz: the four traps, and the one that cost three jobs

Written 2026-09-28 from `h100-single` runs under RT Project "HPC and AI for Students" (PI Laura Huber,
project 197, Slurm account `students`). Every item here was paid for with a failed job.

## 1. THE EXPENSIVE ONE: Triton cannot compile, and the error is NOT what it says

**Symptom:** `boltz predict` dies inside
`triton/backends/nvidia/driver.py -> compile_module_from_file` with

    subprocess.CalledProcessError: Command '[... gcc ... -l:libcuda.so.1 -L/lib64 ...]'
    returned non-zero exit status 1

**The `-l:libcuda.so.1` in that command is a red herring.** I lost three jobs (10743648, 10743672,
10743727) chasing it: exporting `TRITON_LIBCUDA_PATH`, `LIBRARY_PATH`, `LD_LIBRARY_PATH`, and probing a
compute node to confirm `libcuda.so.1` is present in `/usr/lib64` and `/usr/lib` and links fine
(`LINK_OK`). **All of that was wasted, because `check_call` hides gcc's stderr behind a bare exit code.**

**Re-running the exact gcc command by hand gives the real error:**

    fatal error: Python.h: No such file or directory

**The compute nodes have `/usr/include/python3.11/pyconfig-64.h` but no `Python.h`.** The multilib config
header is installed; `python3-devel` is not. Only `/usr/include/python3.6m/Python.h` exists, wrong version.

**THE FIX, one line:**

    export CPATH=/N/soft/rhel8/python/gnu/3.11.4/include/python3.11:${CPATH:-}

3.11.4 headers against a 3.11.13 venv; the shim uses stable C API. **Verified on g37: `COMPILE_OK` and
`cuequivariance triangle import OK`.**

**Lesson worth more than the fix: when a build dies behind `check_call`, re-run the command by hand
before believing any flag in it.**

## 2. Compute nodes have NO internet

`--use_msa_server` cannot work there, and `cleanroom/rnap3/RUN.md` Path A recommends exactly that command.
Precompute MSAs on the **login** node and reference them from the YAML:

    msa: "/N/u/bsmensah/Quartz/af3screen/msa/<CHAIN>.a3m"

`gen_msa.py` does this. Note `run_mmseqs2` is annotated `-> tuple[list, list]` but returns a **bare list**
when `use_pairing=False`; handle both.

## 3. `boltz predict` EXITS 0 AFTER FAILING EVERY EXAMPLE

    Number of failed examples: 1
    BOLTZ_RC=0

**Never test the exit code. Test for the artefact:**

    find out_dir -name '*.pdb' | head -1

## 4. 2,817 tokens does NOT fit one 80 GB H100 without the fused kernels

The pair representation is `2817^2 x 128 x 4 B = 4.06 GB` per tensor and the triangle ops need several.
Observed OOMs requested 8.13 GB and 12.19 GB with under 7 GB free of 85 GB.

**`--subsample_msa --num_subsampled_msa 512` does NOT help**, because the bottleneck is N-squared in
*tokens*, not MSA depth. Either fix Triton (item 1) and use the fused kernels, or use a bigger card.

**Small jobs are unaffected:** BRIDGE at ~957 tokens median runs fine with `--no_kernels`, which bypasses
Triton entirely. **Use `--no_kernels` for anything that fits; it removes a whole failure class.**

## 5. Assorted

- `sbatch` requires `-A <account>`; `sacctmgr -nP show assoc user=$USER` gives it (`students`).
- SSH ControlMaster from WSL dies when the WSL VM shuts down. Hold the VM open with a foreground
  process, or expect to re-authenticate (passphrase + Duo) every time.
- `srun -p h100-debug --gres=gpu:h100:1 -t 00:08:00 ./probe.sh` is the cheap way to test a node
  assumption before spending a real job on it. **Use it earlier than I did.**
