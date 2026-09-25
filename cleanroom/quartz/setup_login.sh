#!/usr/bin/env bash
# Run ONCE on a Quartz LOGIN node (quartz.uits.iu.edu), never in a batch job.
#
# The whole point of this script: Quartz login nodes have internet and compute nodes do not. Anything
# that needs to be downloaded has to be pulled here, or the batch job dies at hour zero. That means
# the python env, boltz itself, and boltz's model weights and CCD dictionary, which boltz otherwise
# fetches lazily on first prediction.
#
#   bash setup_login.sh
set -euo pipefail

BASE="${BASE:-$HOME/af3screen}"
export BOLTZ_CACHE="$BASE/boltz_cache"
mkdir -p "$BASE" "$BOLTZ_CACHE" "$BASE/logs"
cd "$BASE"

echo "== modules"
module load python 2>/dev/null || true
python3 -V

echo "== venv"
[ -d venv ] || python3 -m venv venv
source venv/bin/activate
pip install -q --upgrade pip
pip install -q boltz
echo "boltz: $(command -v boltz)"

echo "== pre-downloading model weights and CCD into $BOLTZ_CACHE"
# A compute node cannot fetch these. Forcing one tiny CPU prediction here is the only reliable way
# to make boltz populate the cache, because it downloads lazily at first use rather than at install.
cat > .warm.yaml <<'YAML'
version: 1
sequences:
  - protein:
      id: A
      sequence: MKTAYIAKQRQISFVK
      msa: empty
YAML
mkdir -p .warm_out
boltz predict .warm.yaml --out_dir .warm_out --accelerator cpu --diffusion_samples 1 \
    --sampling_steps 10 --cache "$BOLTZ_CACHE" 2>&1 | tail -15 || true

echo "== pointing the job YAMLs at this account's MSA directory"
# The YAMLs ship with a placeholder MSA path. Rewrite it from $HOME rather than guessing IU's home
# convention, so this is correct whatever the account's real path turns out to be.
if [ -d "$BASE/yaml" ]; then
  n=$(ls "$BASE/yaml"/*.yaml 2>/dev/null | wc -l)
  sed -i "s|msa: \".*/msa/|msa: \"$BASE/msa/|" "$BASE/yaml"/*.yaml
  echo "  rewrote $n job files -> $BASE/msa/"
  grep -h 'msa:' "$BASE/yaml"/*.yaml | sort -u | sed 's/^/  /'
  missing=0
  for a in $(grep -h 'msa:' "$BASE/yaml"/*.yaml | sed 's/.*msa: "//;s/"$//' | sort -u); do
    [ -f "$a" ] || { echo "  MISSING: $a"; missing=1; }
  done
  [ "$missing" -eq 1 ] && { echo "FATAL: an MSA referenced by the jobs is not on disk."; exit 1; }
else
  echo "  WARNING: $BASE/yaml not found. Push the jobs before submitting (see PUSH.md)."
fi

echo "== cache contents"
du -sh "$BOLTZ_CACHE" 2>/dev/null
find "$BOLTZ_CACHE" -maxdepth 1 -printf '  %f\n' 2>/dev/null | head -20

if [ -z "$(find "$BOLTZ_CACHE" -name '*.ckpt' -o -name '*.pt' 2>/dev/null | head -1)" ]; then
  echo
  echo "WARNING: no model checkpoint landed in the cache. The batch job will fail offline."
  echo "Check the boltz output above for the download URL and fetch it here by hand."
  exit 1
fi

echo
echo "Setup complete. Next:"
echo "  1. confirm the GPU partition name and gres syntax:  sinfo -o '%P %G %N' | sort -u"
echo "  2. put yaml/ and msa/ under $BASE  (see PUSH.md)"
echo "  3. probe one job:   sbatch --export=ALL,PROBE=1 --array=0 quartz/screen.slurm"
