#!/usr/bin/env bash
# Runs the virtual screen on a rented GPU pod. Assumes vscreen_yaml/ and msa/ have been copied to
# /workspace/screen. Boltz reads the precomputed MSA from the YAML, so no internet is needed at run time.
set -euo pipefail
cd /workspace/screen
echo "== installing boltz"
pip install -q --upgrade pip
pip install -q boltz
echo "== gpu"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
echo "== jobs: $(ls yaml/*.yaml | wc -l)"
# one warm-up job first: fail fast on a config error instead of 6 hours in
FIRST=$(ls yaml/*.yaml | head -1)
mkdir -p out
boltz predict "$FIRST" --out_dir out --diffusion_samples 1 --output_format pdb 2>&1 | tail -20
echo "== warm-up done, running the rest"
boltz predict yaml --out_dir out --diffusion_samples 1 --output_format pdb 2>&1 | tail -40
echo "== packaging affinity results only (small)"
find out -name 'affinity_*.json' | tar czf affinity_results.tar.gz -T -
ls -la affinity_results.tar.gz
echo "== DONE. Copy affinity_results.tar.gz back, then terminate the pod."
