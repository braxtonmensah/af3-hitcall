#!/usr/bin/env bash
# Check whether the installed torch can actually target Quartz's V100s, and fix it if not.
#
# Why this exists: `pip install boltz` pulls the newest torch, which now ships against CUDA 13.
# CUDA 13 dropped Maxwell, Pascal and Volta. Quartz's GPUs are V100 (Volta, sm_70), so a cu13 torch
# has no kernels for them and every job dies with "no kernel image is available for execution on the
# device" - after the job has queued and started, which wastes an allocation to learn something
# checkable in one second on a login node.
#
# torch.cuda.get_arch_list() reports the compiled architectures and needs no GPU, so this runs here.
#
#   bash quartz/fix_torch_volta.sh
set -uo pipefail
BASE="${BASE:-$HOME/af3screen}"
cd "$BASE" || exit 1
module load python/gpu/3.11.5 >/dev/null 2>&1
source venv/bin/activate

echo "== what torch was built for"
python - <<'PY'
import torch
archs = torch.cuda.get_arch_list()
print("torch   :", torch.__version__)
print("cuda    :", torch.version.cuda)
print("arch    :", " ".join(archs))
print("sm_70   :", "PRESENT" if any("70" in a for a in archs) else "MISSING  <-- V100 unusable")
PY

if python -c "import torch,sys; sys.exit(0 if any('70' in a for a in torch.cuda.get_arch_list()) else 1)"; then
  echo
  echo "OK: this torch supports V100. Nothing to do."
  exit 0
fi

echo
echo "== reinstalling torch against CUDA 12.6, which still has Volta kernels"
# boltz only requires torch>=2.2, so dropping to the last cu12 line costs nothing here
pip install --force-reinstall --index-url https://download.pytorch.org/whl/cu126 \
    "torch==2.6.0" 2>&1 | tail -8

echo
echo "== re-checking"
python - <<'PY'
import torch
archs = torch.cuda.get_arch_list()
print("torch   :", torch.__version__)
print("cuda    :", torch.version.cuda)
print("arch    :", " ".join(archs))
ok = any("70" in a for a in archs)
print("sm_70   :", "PRESENT - V100 will work" if ok else "STILL MISSING")
raise SystemExit(0 if ok else 1)
PY
rc=$?
if [ $rc -ne 0 ]; then
  echo
  echo "FATAL: could not get a Volta-capable torch. Options, in order:"
  echo "  1. try an even older line:  pip install --force-reinstall --index-url https://download.pytorch.org/whl/cu121 torch==2.4.1"
  echo "  2. ask for a non-Volta GPU if Quartz has one:  sinfo -o '%P %G %N' | sort -u"
  exit 1
fi
echo
echo "Fixed. Now run the probe:"
echo "  sbatch --export=ALL,PROBE=1 --array=0 quartz/screen.slurm"
