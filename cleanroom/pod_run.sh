#!/usr/bin/env bash
# Runs the virtual screen on a rented GPU pod. Expects yaml/ and msa/ under /workspace/screen.
# Boltz reads the precomputed MSA from each YAML, so no internet is needed once boltz is installed.
#
#   ./pod_run.sh bench     3 jobs, report seconds-per-job, peak VRAM and the projected full cost
#   ./pod_run.sh           the full screen
#
# Resumable by design: work is done in small chunks and a re-run skips every job that already has an
# affinity result. A crash, a preemption or a dropped SSH session costs one chunk, not the whole run.
set -uo pipefail

ROOT=/workspace/screen
CHUNK=25
RATE="${RATE:-0.69}"            # USD/hr, for the cost projection only
export BOLTZ_CACHE="${BOLTZ_CACHE:-/workspace/boltz_cache}"
cd "$ROOT" || exit 1
mkdir -p out "$BOLTZ_CACHE"

MODE="${1:-full}"
[ "$MODE" = "bench" ] && CHUNK=3

log() { echo "[$(date -u +%H:%M:%S)] $*" | tee -a run.log; }

# ---------------------------------------------------------------- setup
if ! command -v boltz >/dev/null 2>&1; then
  log "installing boltz"
  pip install -q --upgrade pip >/dev/null 2>&1
  pip install -q boltz || { log "FATAL: boltz install failed"; exit 1; }
fi

python - <<'PY' || { echo "FATAL: torch cannot use this GPU"; exit 1; }
import torch, sys
if not torch.cuda.is_available():
    sys.exit("no CUDA device visible to torch")
p = torch.cuda.get_device_properties(0)
# a real matmul, because torch.cuda.is_available() is true on cards whose arch this build lacks
torch.randn(2048, 2048, device="cuda", dtype=torch.bfloat16) @ torch.randn(2048, 2048, device="cuda", dtype=torch.bfloat16)
torch.cuda.synchronize()
print("gpu ok: %s, %.0f GB, sm_%d%d" % (p.name, p.total_memory / 1e9, p.major, p.minor))
PY

TOTAL=$(ls yaml/*.yaml 2>/dev/null | wc -l)
[ "$TOTAL" -eq 0 ] && { log "FATAL: no jobs in $ROOT/yaml"; exit 1; }
log "mode=$MODE jobs=$TOTAL chunk=$CHUNK rate=\$$RATE/hr"

done_ids() { find out -name 'affinity_*.json' -printf '%f\n' 2>/dev/null | sed 's/^affinity_//;s/\.json$//' | sort -u; }
done_n()   { done_ids | wc -l; }

# ---------------------------------------------------------------- run
START=$(date +%s); RAN=0; i=0
while :; do
  done_ids > .done
  rm -rf chunk && mkdir -p chunk
  n=0
  for f in yaml/*.yaml; do
    b=$(basename "$f" .yaml)
    grep -qxF "$b" .done && continue
    cp "$f" "chunk/$b.yaml"; n=$((n + 1))
    [ "$n" -ge "$CHUNK" ] && break
  done
  [ "$n" -eq 0 ] && { log "nothing left to run"; break; }

  i=$((i + 1)); t0=$(date +%s)
  boltz predict chunk --out_dir "out/c$i" --diffusion_samples 1 --output_format pdb \
      --cache "$BOLTZ_CACHE" >> run.log 2>&1
  rc=$?; t1=$(date +%s); took=$((t1 - t0)); RAN=$((RAN + n))
  peak=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1)
  d=$(done_n)
  log "chunk $i: $n jobs in ${took}s ($((took / n))s/job, rc=$rc, vram ${peak}MiB) | done $d/$TOTAL"

  if [ "$rc" -ne 0 ] && [ "$d" -eq 0 ]; then
    log "FATAL: first chunk produced no results. Last 30 lines:"; tail -30 run.log; exit 1
  fi
  if [ "$MODE" = "bench" ]; then
    per=$((took / n))
    log "PROJECTION: ${per}s/job x $TOTAL jobs = $((per * TOTAL / 3600))h $(((per * TOTAL % 3600) / 60))m"
    log "PROJECTION: approx \$$(python -c "print(round($per*$TOTAL/3600*$RATE,2))") at \$$RATE/hr"
    log "If that fits the budget, re-run without 'bench' to do the rest."
    exit 0
  fi
done

# ---------------------------------------------------------------- package
ELAPSED=$(( $(date +%s) - START ))
log "ran $RAN jobs in ${ELAPSED}s. Packaging."
# JSONs carry the scores, PDBs the poses; the .npz arrays are large and not needed off-pod
find out \( -name 'affinity_*.json' -o -name 'confidence_*.json' -o -name '*.pdb' \) \
  | tar czf screen_results.tar.gz -T -
ls -la screen_results.tar.gz
log "DONE: $(done_n)/$TOTAL jobs have affinity results."
log "Copy screen_results.tar.gz back, THEN terminate the pod."
