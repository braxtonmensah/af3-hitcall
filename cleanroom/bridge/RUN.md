# BRIDGE: how to run it

Pre-registration: `PREREG_BRIDGE.md`. Design table: `bridge_design.csv`. Jobs: `jobs.json` + 60 YAMLs.

**60 jobs, 20 pairs x 3 arms.** Median 940 tokens, max 2,723, so every job fits an 80 GB card and
also fits AlphaFold Server. No job needs an MSA server call if you precompute MSAs as the virtual
screen does.

## Read the gate first, before looking at anything else

Arm **P** (pair alone) must reproduce the original AlphaFold failure: **at most 4 of 20** pairs may
show an A-B interface. If more do, the engine has simply solved what AF2/FoldDock could not, and the
whole premise is void. Score P first and stop there if the gate fails.

## Order of work

1. Run the 20 **P** jobs. Score. Check the gate.
2. Only if the gate passes, run the 20 **BR** and 20 **CT** jobs.
3. B1 = BR vs P (McNemar). B2 = BR vs CT (McNemar). **B2 is what licenses any claim about
   co-dependency**; without it the result is only "a third chain helps".

## Quartz (Boltz-2, free, IP position recorded in IP_RECORD.md)

    cd ~/af3screen && mkdir -p bridge && cp <these yamls> bridge/
    sbatch -A <account> --array=0-5 quartz/screen.slurm      # after editing BASE/yaml dir

## AlphaFold Server (free, non-commercial output)

30 jobs a day, so this is three days. Fine for arm P on its own (20 jobs, one day).

## Controls were chosen by rule, not by taste

`bridge_design.csv` records, per pair, the bridge and its `min r` (0.22 to 0.82) against the control
and its `min r` (0.0000 to 0.0081). The control is a selectively essential protein of similar length
that co-dependency says is uncoupled to the pair. That separation is the point of the design: if BR
beats CT, coupling is doing the work rather than chain count.

## Known weakness, already in the prereg

8 of the 20 pairs are mitoribosomal. If more than half the successes are mitoribosomal, no general
claim is made and the result is reported as a statement about one assembly.
