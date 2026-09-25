#!/usr/bin/env bash
# Restore a consistent torch, then ask an ACTUAL GPU what it can do.
#
# Why this replaces fix_torch_volta.sh: that script decided whether torch supported Volta by reading
# torch.cuda.get_arch_list() on a login node. That call returns an empty list whenever CUDA cannot
# initialise, which is always true on a node with no GPU. So it reported "CPU-only build" for
# 2.6.0+cu126, 2.5.1+cu121, 2.4.1+cu121 and 2.3.1+cu121 in a row - builds that unquestionably ship
# sm_70. The instrument was broken, not the builds, and four reinstalls were spent on it.
#
# The only test that settles this runs on the hardware. srun gets a real V100 in seconds.
#
#   bash quartz/gpu_truth.sh
set -uo pipefail
BASE="${BASE:-$HOME/af3screen}"
cd "$BASE" || exit 1
module load python/gpu/3.11.5 >/dev/null 2>&1
source venv/bin/activate

echo "== what GPUs exist here"
sinfo -o "%P %G %N" | sort -u | head -25
echo

echo "== restoring a consistent torch (whatever boltz pins)"
# the repeated --force-reinstall of bare torch may have left it mismatched with its nvidia-* libs,
# which is itself enough to make CUDA fail to initialise
pip install --force-reinstall --no-cache-dir boltz 2>&1 | tail -3
python -c "import torch; print('  torch', torch.__version__, '| cuda', torch.version.cuda)"
echo

echo "== asking a real GPU (srun, a few seconds)"
srun --partition=gpu --gres=gpu:1 --time=00:05:00 --mem=16G python - <<'PY'
import torch
print("device        :", torch.cuda.get_device_name(0))
cc = torch.cuda.get_device_capability(0)
print("compute cap   : sm_%d%d" % cc)
print("arch list     :", " ".join(torch.cuda.get_arch_list()) or "(empty)")
print("bf16 supported:", torch.cuda.is_bf16_supported())
for dt in (torch.float32, torch.float16, torch.bfloat16):
    name = str(dt).split(".")[-1]
    try:
        a = torch.randn(1024, 1024, device="cuda", dtype=dt)
        (a @ a); torch.cuda.synchronize()
        print("  %-9s OK" % name)
    except Exception as e:
        print("  %-9s FAILED: %s" % (name, str(e)[:90]))
PY
rc=$?
echo
if [ $rc -ne 0 ]; then
  echo "The GPU test itself failed to run (queue, partition name, or gres syntax)."
  echo "Check the partition and gres names against the sinfo output above and edit quartz/screen.slurm."
  exit 1
fi
echo "If fp32 is OK above, the screen can run. bf16 failing only costs speed, not correctness."
echo "Next:"
echo "  sbatch --export=ALL,PROBE=1 --array=0 quartz/screen.slurm"
