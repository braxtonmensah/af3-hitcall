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

---

## Run log: arm P submitted 2026-09-25 on AlphaFold Server

All **20 arm-P jobs submitted**, engine = AlphaFold Server (not Boltz-2). Recorded because the
pre-registration allows either engine but requires the engine be recorded per pair, and because
AF Server output is non-commercial, which is fine for answering the question and not for a commercial
asset.

**Retrieval:** each finished job downloads as `fold_<name>.zip` containing 5 `*_model_N.cif` files.
Unzip them all into one directory and run:

    py -3.11 score_bridge.py <dir>

The scorer reads the gate first and refuses to interpret BR when arm P shows more than 4 interfaces.

**Deviation to record when scoring:** AF Server returns 5 samples per job, so the "3 of 5 samples"
rule in the interface definition is satisfiable as written. No deviation expected.

**An error worth not repeating.** The first submission attempt looped over "the first draft row in the
table" without waiting for the table to re-render, so it re-submitted the same job
(`taf6l_tada2b_p`) **six times** and burned 5 of the day's 30 job slots. The working method is to
search for each job by exact name, confirm the row is still a draft, then submit, and to re-navigate
to the list between jobs because the app leaves the list view after each submission. The six
duplicates are harmless to the analysis (the scorer keys on pair and arm, and identical inputs give
consistent answers) but they are five wasted slots.

**Arms BR and CT are still unrun**, 40 jobs, and the daily quota is 30. They need either two more
days on AF Server or a funded GPU. Run them only after the gate passes.

---

## Scoring note, 2026-09-25: the page ipTM is valid for arm P and NOT for arms BR/CT

The AlphaFold Server result page prints a single `ipTM = x` for a job.

- **Arm P has two chains, so that number IS the A-B chain-pair ipTM.** Reading it off the page is a
  valid screen and is how the 19 arm-P values in `armP_iptm.json` were collected. A value below 0.5
  is the best of five samples and so cannot meet the amended "3 of 5" rule; it fails outright.
- **Arms BR and CT have three chains, so the page number is the WHOLE-COMPLEX ipTM**, averaging all
  three chain pairs. It is **not** the A-B value the amended criterion asks for and must not be used
  as one. RNAP3 is the proof: its page ipTM was **0.87** while the MG354-RpoB chain pair was **0.57**
  and MG354-RpoC was **0.43**.

**So BR and CT must be scored from `*_summary_confidences_*.json` inside each downloaded zip, using
`chain_pair_iptm[0][1]`** (chains are written A, B, then the bridge or control as C). Do not shortcut
this with the page value.

First BR job back, `taf6l_tada2b_br`, shows a page ipTM of 0.13 against the same pair's arm-P value of
0.13. That is suggestive of no rescue, and it is **not** a result: it is the wrong quantity, n = 1,
and the pre-registered comparison is over 20 pairs with a McNemar test.
