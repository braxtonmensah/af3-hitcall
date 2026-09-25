#!/bin/bash
# Virtual screen of the RNase J : MPN621 interface, sharded across Quartz V100s.
#
#   sbatch --export=ALL,PROBE=1 --array=0 quartz/screen.slurm     one job, measure, then stop
#   sbatch --array=0-7 quartz/screen.slurm                        the full 350
#
# Each array task owns an interleaved shard (task i takes every Nth job), so shards finish at about
# the same time even if some ligands are slower. Re-running is safe and resumes: a job that already
# has an affinity result is skipped, so a walltime kill costs one chunk, not the shard.
#
# Partition is h100-single, NOT the v100 partition. Quartz has both (h100-single: g[39-88],
# v100: g[1-24]). H100 is Hopper (sm_90) with native bfloat16, which is what Boltz-2 wants, and is
# supported by the torch that `pip install boltz` pulls. The V100s are Volta (sm_70): no hardware
# bf16, and dropped entirely by CUDA 13, so that torch has no kernels for them at all. Choosing the
# H100 partition removes both problems instead of working around them.
#SBATCH --job-name=af3screen
#SBATCH --partition=h100-single
#SBATCH --gres=gpu:h100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=12:00:00
#SBATCH --output=logs/%x_%A_%a.out
#SBATCH --error=logs/%x_%A_%a.out

set -uo pipefail
BASE="${BASE:-$HOME/af3screen}"
cd "$BASE" || exit 1
export BOLTZ_CACHE="$BASE/boltz_cache"
# compute nodes have no internet; fail loudly rather than hanging on a download attempt
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
source venv/bin/activate

I="${SLURM_ARRAY_TASK_ID:-0}"
N="${SLURM_ARRAY_TASK_COUNT:-1}"
PROBE="${PROBE:-0}"
CHUNK=10
mkdir -p out logs

echo "[$(date -u +%H:%M:%S)] shard $I of $N on $(hostname)"
nvidia-smi --query-gpu=name,memory.total,compute_cap --format=csv,noheader

# ---------------------------------------------------------------- precision probe
# On H100 this should all pass. Kept because it costs one second and catches a partition mistake:
# if a job lands on a V100 instead, bf16 will fail here rather than 8 hours in.
python - <<'PY'
import torch
p = torch.cuda.get_device_properties(0)
print("torch %s | %s | sm_%d%d" % (torch.__version__, p.name, p.major, p.minor))
print("bf16 supported:", torch.cuda.is_bf16_supported())
for dt in (torch.float32, torch.float16, torch.bfloat16):
    try:
        a = torch.randn(1024, 1024, device="cuda", dtype=dt)
        (a @ a); torch.cuda.synchronize()
        print("  %-10s ok" % str(dt).split(".")[-1])
    except Exception as e:
        print("  %-10s FAILED: %s" % (str(dt).split(".")[-1], str(e)[:80]))
PY

# ---------------------------------------------------------------- shard
mapfile -t ALL < <(ls yaml/*.yaml | sort)
TOTAL=${#ALL[@]}
[ "$TOTAL" -eq 0 ] && { echo "FATAL: no jobs in $BASE/yaml"; exit 1; }

done_ids() { find out -name 'affinity_*.json' -printf '%f\n' 2>/dev/null | sed 's/^affinity_//;s/\.json$//' | sort -u; }

run=0
while :; do
  done_ids > ".done_$I"
  rm -rf "shard_$I" && mkdir -p "shard_$I"
  n=0
  for idx in "${!ALL[@]}"; do
    [ $((idx % N)) -eq "$I" ] || continue
    b=$(basename "${ALL[$idx]}" .yaml)
    grep -qxF "$b" ".done_$I" && continue
    cp "${ALL[$idx]}" "shard_$I/$b.yaml"; n=$((n + 1))
    [ "$n" -ge "$CHUNK" ] && break
  done
  [ "$n" -eq 0 ] && { echo "[$(date -u +%H:%M:%S)] shard $I complete"; break; }
  [ "$PROBE" = "1" ] && { ls "shard_$I" | tail -n +2 | xargs -r -I{} rm "shard_$I/{}"; n=1; }

  t0=$(date +%s)
  boltz predict "shard_$I" --out_dir "out/s$I" --diffusion_samples 1 --output_format pdb \
      --cache "$BOLTZ_CACHE" --num_workers 2
  rc=$?; took=$(( $(date +%s) - t0 )); run=$((run + n))
  echo "[$(date -u +%H:%M:%S)] shard $I: $n jobs in ${took}s ($((took / n))s/job, rc=$rc) | done $(done_ids | wc -l)/$TOTAL"

  if [ "$PROBE" = "1" ]; then
    per=$((took / n))
    echo "PROBE: ${per}s/job. 350 jobs on 8 V100s = $((per * 350 / 8 / 60)) min wall clock."
    echo "PROBE: if that is sane, launch: sbatch --array=0-7 quartz/screen.slurm"
    exit 0
  fi
  if [ "$rc" -ne 0 ] && [ "$run" -le "$CHUNK" ]; then
    echo "FATAL: first chunk failed on shard $I"; exit 1
  fi
done
