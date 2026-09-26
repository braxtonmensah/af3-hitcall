#!/usr/bin/env bash
# Run a Boltz-2 job set on a GPU. Supersedes pod_run.sh, which is hardcoded to the interface screen
# that PREREG_VSCREEN Amendment 4 says not to run.
#
#   ./run_screen.sh gate_jobs preflight     checks only, spends nothing
#   ./run_screen.sh gate_jobs bench         3 jobs, then project time and cost for the rest
#   ./run_screen.sh gate_jobs               the whole set
#
# Env: ROOT (default .), MSA_DIR (default $ROOT/msa), RATE (USD/hr, projection only),
#      CHUNK (default 25), SAMPLES (default 1).
#
# Three things this checks that pod_run.sh did not, each of which has cost a run somewhere:
#
#   1. Every MSA path named inside the YAMLs must resolve ON THIS MACHINE, before any GPU time is
#      spent. The jobs carry absolute pod-side paths, so a set built for a different layout fails at
#      job zero after the install is already paid for.
#   2. No carriage returns in the YAMLs. A CR inside a quoted msa: path reports a file that exists as
#      missing; this is recorded in STATE.md as having cost a cycle.
#   3. Resume handles BOTH output layouts Boltz has used (affinity_<name>.json and <name>/affinity.json).
#      pod_run.sh only knew the first, so on the other layout it would find nothing done and re-run
#      the entire set from scratch after any interruption.
set -uo pipefail

JOBS="${1:-}"
MODE="${2:-full}"
ROOT="${ROOT:-$(pwd)}"
MSA_DIR="${MSA_DIR:-$ROOT/msa}"
CHUNK="${CHUNK:-25}"
SAMPLES="${SAMPLES:-1}"
RATE="${RATE:-0.34}"
export BOLTZ_CACHE="${BOLTZ_CACHE:-$ROOT/boltz_cache}"

[ -z "$JOBS" ] && { echo "usage: $0 <job-dir> [preflight|bench|full]"; exit 2; }
[ -d "$JOBS" ] || { echo "FATAL: no such job directory: $JOBS"; exit 1; }
OUT="${OUT:-$ROOT/out_$(basename "$JOBS")}"
mkdir -p "$OUT" "$BOLTZ_CACHE"
LOG="$OUT/run.log"
log() { echo "[$(date -u +%H:%M:%S)] $*" | tee -a "$LOG"; }

TOTAL=$(find "$JOBS" -maxdepth 1 -name '*.yaml' | wc -l)
[ "$TOTAL" -eq 0 ] && { echo "FATAL: no .yaml in $JOBS"; exit 1; }
log "job dir=$JOBS jobs=$TOTAL out=$OUT mode=$MODE samples=$SAMPLES chunk=$CHUNK"

# ---------------------------------------------------------------- preflight
fail=0

# (2) carriage returns. The -U (binary) flag is REQUIRED, not defensive: Git Bash grep opens
# files in text mode and strips CRs before matching, so WITHOUT -U this check silently passes
# on a CRLF file. It did exactly that when first written, which is the failure it exists to catch.
if grep -rlqU $'\r' "$JOBS" 2>/dev/null; then
  log "FATAL: CR characters in job files. A CR inside a quoted msa: path makes a present file look"
  log "       missing. Fix with: sed -i 's/\r$//' $JOBS/*.yaml"
  fail=1
fi

# (1) every referenced MSA must resolve here. Delegated to check_msa_paths.py, which is a real file
# with real exit codes: 0 resolves, 3 relinkable, 4 absent. The previous version embedded this as a
# heredoc, the heredoc had a quoting bug, it died with a SyntaxError, and because only its OUTPUT was
# inspected an empty report read as "everything fine" and the preflight printed OK. A check that
# fails open is worse than no check, so this one is judged by its status, not its chatter.
CHECKER="$(dirname "$0")/check_msa_paths.py"
if [ ! -f "$CHECKER" ]; then
  log "FATAL: cannot find check_msa_paths.py next to this script"
  fail=1
else
  RELINK_FLAG=""
  [ "${RELINK:-0}" = "1" ] && RELINK_FLAG="--relink"
  python "$CHECKER" "$JOBS" --msa-dir "$MSA_DIR" $RELINK_FLAG 2>&1 | tee -a "$LOG"
  msa_rc=${PIPESTATUS[0]}
  case "$msa_rc" in
    0) log "MSA paths resolve as written." ;;
    3) log "MSA paths do not resolve as written but the files are present in $MSA_DIR."
       log "Expected when checking away from the machine that will run the jobs. Re-run with"
       log "RELINK=1 to rewrite them for THIS machine; not the default, because the pod-side"
       log "paths are deliberate and the job files are a committed artifact."
       [ "$MODE" != "preflight" ] && { log "Cannot run with unresolved MSAs."; fail=1; } ;;
    4) log "FATAL: MSA files named in the jobs exist nowhere on this machine."; fail=1 ;;
    *) log "FATAL: the MSA check itself failed (exit $msa_rc). Not proceeding on an unknown state."
       fail=1 ;;
  esac
fi

# (3) GPU, verified with a real matmul rather than by is_available()
if [ "$MODE" != "preflight" ] || [ "${CHECK_GPU:-1}" = "1" ]; then
  if command -v python >/dev/null 2>&1; then
    python - <<'PY' 2>&1 | tee -a "$LOG" | grep -q '^gpu ok' || { echo "GPU CHECK FAILED"; fail=1; }
import sys
try:
    import torch
except ImportError:
    print("torch not installed yet (will be installed with boltz)"); sys.exit(0)
if not torch.cuda.is_available():
    print("FATAL: no CUDA device visible to torch"); sys.exit(1)
p = torch.cuda.get_device_properties(0)
try:
    a = torch.randn(2048, 2048, device="cuda", dtype=torch.bfloat16)
    (a @ a); torch.cuda.synchronize()
except Exception as e:
    print("FATAL: this torch build has no working kernels for %s: %s" % (p.name, e)); sys.exit(1)
print("gpu ok: %s, %.0f GB, sm_%d%d" % (p.name, p.total_memory / 1e9, p.major, p.minor))
PY
  fi
fi

if [ "$fail" -ne 0 ]; then
  log "PREFLIGHT FAILED. Nothing was run and nothing was spent."
  exit 1
fi
if [ "${msa_rc:-0}" = "3" ]; then
  log "preflight OK for this machine's purposes: $TOTAL jobs, no CRs, MSA files all PRESENT but"
  log "their paths are written for another host. This set is ready to ship, not to run here."
else
  log "preflight OK: $TOTAL jobs, MSA paths resolve as written, no CRs. Ready to run here."
fi
if [ "$MODE" = "preflight" ]; then
  log "preflight only. Re-run with 'bench' to measure, or with no mode to run everything."
  exit 0
fi

# ---------------------------------------------------------------- setup
if ! command -v boltz >/dev/null 2>&1; then
  log "installing boltz"
  pip install -q --upgrade pip >/dev/null 2>&1
  pip install -q boltz || { log "FATAL: boltz install failed"; exit 1; }
fi

# Both layouts, so an interrupted run resumes instead of restarting.
done_ids() {
  { find "$OUT" -name 'affinity_*.json' -printf '%f\n' 2>/dev/null | sed 's/^affinity_//;s/\.json$//'
    find "$OUT" -name 'affinity.json' -printf '%h\n' 2>/dev/null | xargs -r -n1 basename
  } | sort -u
}

[ "$MODE" = "bench" ] && CHUNK=3
START=$(date +%s); RAN=0; i=0
while :; do
  done_ids > "$OUT/.done"
  rm -rf "$OUT/chunk" && mkdir -p "$OUT/chunk"
  n=0
  for f in "$JOBS"/*.yaml; do
    b=$(basename "$f" .yaml)
    grep -qxF "$b" "$OUT/.done" && continue
    cp "$f" "$OUT/chunk/$b.yaml"; n=$((n + 1))
    [ "$n" -ge "$CHUNK" ] && break
  done
  [ "$n" -eq 0 ] && { log "nothing left to run"; break; }

  i=$((i + 1)); t0=$(date +%s)
  boltz predict "$OUT/chunk" --out_dir "$OUT/c$i" --diffusion_samples "$SAMPLES" \
      --output_format pdb --cache "$BOLTZ_CACHE" >> "$LOG" 2>&1
  rc=$?; took=$(( $(date +%s) - t0 )); RAN=$((RAN + n))
  peak=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1)
  d=$(done_ids | wc -l)
  log "chunk $i: $n jobs in ${took}s ($((took / n))s/job, rc=$rc, vram ${peak:-?}MiB) | done $d/$TOTAL"

  if [ "$rc" -ne 0 ] && [ "$d" -eq 0 ]; then
    log "FATAL: the first chunk produced no results. Last 30 log lines:"
    tail -30 "$LOG"; exit 1
  fi
  if [ "$MODE" = "bench" ]; then
    per=$((took / n))
    log "PROJECTION: ${per}s/job x $TOTAL = $((per * TOTAL / 3600))h $(((per * TOTAL % 3600) / 60))m"
    log "PROJECTION: about \$$(python -c "print(round($per*$TOTAL/3600*$RATE,2))") at \$$RATE/hr"
    log "If that fits the budget, re-run with no mode argument to finish."
    exit 0
  fi
done

ELAPSED=$(( $(date +%s) - START ))
log "ran $RAN jobs in ${ELAPSED}s"
find "$OUT" \( -name 'affinity*.json' -o -name 'confidence*.json' -o -name '*.pdb' \) \
  | tar czf "$OUT/results_$(basename "$JOBS").tar.gz" -T -
ls -la "$OUT/results_$(basename "$JOBS").tar.gz" | tee -a "$LOG"
log "DONE: $(done_ids | wc -l)/$TOTAL have affinity results."
log "Copy the tarball back, score it, THEN terminate the pod."
