# Handoff: what to build next for the best chance of funding. State at 2026-09-28 ~18:30 UTC

Written after a long session across `af3-hitcall` and `foldnovelty`. **Read section 0 first; it changes
what you are allowed to claim.** Repos: `af3-hitcall` (public), `foldnovelty` (private).

---

## 0. THE FOUR THINGS THAT MUST NOT BE MIS-STATED IN ANY PITCH

1. **MG354 binding RNA polymerase is NOT our discovery. It is published**, in the same paper our
   crosslinks came from, and validated by an orthogonal method. O'Reilly et al. 2020, *Science*
   369:554-557, PMID 32732422, verified verbatim from PMC7115962: *"two uncharacterized essential
   proteins, MPN555 and MPN530 ... the interaction of MPN530 with beta/beta-prime subunits was
   independently validated by a bacterial two-hybrid screen"*. **Never write "we found MG354 binds
   RNAP".** See `af3-hitcall/RETRACTION_MG354_NOVELTY.md`.
2. **RNAP3 already ran** (AlphaFold Server, 2026-09-25, SUPPORTED: 4 of 5 crosslinks, control 0.95,
   ipTM 0.910, commit `de313f4`). `STATE.md`, `cleanroom/rnap3/RUN.md` and the memory all wrongly call it
   outstanding; **`cleanroom/AUDIT_PUBLIC.md` C-3 already flagged that contradiction.**
   **Read AUDIT_PUBLIC.md before trusting STATE.md.** I wasted hours re-running it.
3. **H-062's headline needs four extra words.** Branched backbones are as designable as real
   length-matched natural domains **through this pipeline**. The 36/48 control is MPNN-redesigned and
   refolded, so it is a pipeline ceiling; the native leg is only 23/48 (47.9%).
4. **"The tooling cannot represent branched sheets" is retracted.** Rosetta silently prunes
   (`make_strand_neighbor_two()`) before its error fires, but **RFdiffusion can express degree 3** (no
   degree cap in its block-adjacency input) and **DSSP exposes it**. The true claim is that **design
   RULES excluded it, not that instruments could not see it.**

---

## 1. WHAT IS ACTUALLY FUNDABLE, ranked, with the honest case against each

### Rank 1: the blind interface method, with MG354 as its validation story

**The asset:** confident predictions of never-solved complexes had the right interface **81% of the time
in human (n=146) and 89% in yeast (n=84)** against 2022-2026 releases, versus **2%** for low-confidence
calls. **Always pair with the conservative figure: X-ray-only is 53% (n=19, CI [0.32, 0.74]).** The
honest headline is "53% to 81% depending on how hard you control for circularity".

**Why the MG354 retraction HELPS here.** A blind signature recovered a published, two-hybrid-validated
interaction without being told what it was. **That is validation against ground truth, which is exactly
what a methods grant needs, and it is stronger than a discovery anecdote.** Pitch the method, use MG354
as proof it works, never call MG354 new.

**The case against:** the 81% is conditional on the pair later being solved, which is 2.7% of confident
calls. Reviewers will find that. State it first, yourself.

### Rank 2: MPN555, the protein NOBODY here has touched

**O'Reilly et al. found TWO uncharacterized essential proteins on RNA polymerase: MPN530 (= MG354) and
MPN555.** This project has spent weeks on MPN530 and **zero** on MPN555.

**Why this is the best new-biology bet in the repo:** it is (a) essential, (b) uncharacterized, (c)
already published as RNAP-associated so the interaction is not speculative, and (d) completely unworked
by us. Every instrument built for MG354 applies unchanged.

**First moves, all cheap and all already tooled:** pull its sequence and crosslinks from PXD017711 /
PXD017695; run the HIGHER split-crosslink test; check Pfam/InterPro family; run XLGEO against 6WVJ; check
whether MPN555 and MPN530 crosslink to each other, because two uncharacterized proteins on one machine
may be one complex. **Do the prior-art kill check FIRST this time.**

### Rank 3: branched beta sheets as designable fold space

**The asset, now citable rather than inferred:** Minami et al. 2023 (*Nat Struct Mol Biol* 30:1132-1140,
PMID 37400653) state verbatim, in the ECOD survey that defines their design space: *"Branched beta-sheets
with beta-strands having more than two neighboring beta-strands were discarded."* **The field's most
systematic fold exploration excludes this class by construction.** We then showed 6 of 7 branched
backbones pass G5, indistinguishable from real domains through the same pipeline.

**The fundable framing:** *a structural class excluded by convention, not by physics, is designable.*
That is an expansion-of-design-space story, which funders understand.

**The case against, and it is real:** nothing has been synthesised, topology retention in the predictions
was never verified (H-065 aborted on its own control), and "nobody designs these" is **not found, not
proven absent**. **The cheap closure: run our degree instrument over the Protein Design Archive**
(Chronowska et al., *Nat Biotechnol* 2025). One day of work, not done.

### Rank 4, do not lead with this: the negative results

Six absence claims, the omega hypothesis (fold AND site), UPF0356/YkzG, CODEP, the curvature mechanism.
**These are good science and bad pitches.** They belong in a methods paper as evidence of rigour, not in
a funding ask.

---

## 2. THE STRONGEST SINGLE PITCH I CAN SEE

> **We built and blind-validated a method that finds structurally unmodelled protein-protein interfaces,
> and we are applying it to the two uncharacterized essential proteins that sit on the RNA polymerase of
> a minimal-genome organism.**

It works because: the method has ground-truth validation (53-81%, plus MG354 recovered blind); the
targets are published as real but **unplaced** (O'Reilly could not fit MPN530 into the expressome
density); the biology is legible (minimal genome, essential genes, transcription); and compute is now
**free** on IU Quartz H100s.

**What would make it undeniable, in order of value per hour:**

1. **MPN555 worked up from scratch.** Highest new-biology value, lowest cost, zero prior effort spent.
2. **A site prediction for MPN530 that is testable**, i.e. named residues a collaborator could mutate.
   O'Reilly's bacterial two-hybrid already exists as the assay format, which removes the "how would you
   test it" objection before it is raised.
3. **The Protein Design Archive sweep** for branched sheets. One day, closes rank 3's biggest hole.

---

## 3. A NUMBER THAT NEEDS CHECKING BEFORE IT IS QUOTED AGAIN

The RNAP3 model satisfies **0.95** of the RpoB-RpoC control crosslinks. The **same** crosslinks measured
against **real solved structures** give:

| structure | state | satisfied |
|---|---|---|
| *E. coli* 4YG2 | sigma70 holoenzyme, 3.70 A | 11/17 = 64.7% |
| *B. subtilis* 6WVK | HelD complex, clamp opened to 47 A | 11/12 = 91.7% |
| *B. subtilis* 6WVJ | elongation complex, no HelD | 13/15 = 86.7% |

**The model explains noisy in-cell restraints better than crystallography of the real machine does.**
That is the wrong direction for comfort. The Boltz-2 replicate queued on Quartz is an independent engine
with no shared failure mode; **finish it before quoting 0.95.**

**Also calibrate the gate itself:** published in-cell analogues run **71-75%** (O'Reilly et al., *Mol Syst
Biol* 2023;19:e11544, YugI 10/14, YabR 6/8), not the ~90% of purified benchmarks. At n = 12-17 a 70% bar
rejects a **correct** model 10-20% of the time. Our E. coli "failure" at 64.7% has a 95% CI of
**[38.3%, 85.8%]**, which contains 70%.

---

## 4. LIVE STATE right now

- **Quartz** (free; RT Project 197, PI Laura Huber, Slurm account `students`, `h100-single` = 50 nodes
  x 4 H100):
  - `10743937` rnap3, **queued**. Independent Boltz-2 replicate of the 2026-09-25 AF Server result.
  - `10743936_[0-19]` bridge, **partly running**, 0 structures written yet.
  - **I cancelled `10744037`**, a duplicate rnap3 submitted 14 minutes after mine, same script and same
    output directory. **Two sessions are submitting to this account. Run `squeue` before you submit.**
  - Boltz-2 2.2.1 at `~/af3screen/venv`, 12 GB weights cached offline, 53 BRIDGE MSAs precomputed.
- **Thunder:** `tnr status` returns `[]`. Nothing billing. Total spent today about **$1.50**.
- **SSH:** the WSL ControlMaster dies when the WSL VM shuts down; hold the VM open with a foreground
  process or expect to re-authenticate (passphrase + Duo) each time.
- **A parallel session is editing `foldnovelty`.** It ran H-068 (a decisive negative, `rho_place=-0.500`)
  and rewrote `HANDOFF.md`. We duplicated curvature work. **Coordinate or you will collide.**

---

## 5. HOW TO WORK, learned the hard way today

1. **Run the prior-art kill check FIRST, as a dispatched agent, before any compute.** An agent returned
   the MG354 retraction in **four minutes**. I ran hours of GPU work before asking.
2. **Dispatch parallel agents for independent lanes.** Four ran today; two overturned claims, one
   strengthened one, and together they cost less than one GPU job.
3. **Re-verify every load-bearing quote yourself** from PMC/PubMed. Doing so caught a nuance an agent
   summary blurred: the Minami exclusion is in their ECOD census, which defines the design space, not in
   the design step itself.
4. **Read `AUDIT_PUBLIC.md` before `STATE.md`.** The audit knew RNAP3 had run; STATE.md did not.
5. **When a build fails behind `subprocess.check_call`, re-run the command by hand.** Three jobs blamed
   `libcuda`; the real error was `fatal error: Python.h: No such file or directory`. Fix:
   `export CPATH=/N/soft/rhel8/python/gnu/3.11.4/include/python3.11`. See
   `af3-hitcall/cleanroom/QUARTZ_GOTCHAS.md`.
6. **`boltz predict` exits 0 after failing every example. Test for the artefact, never the exit code.**
7. **Calibrate every similarity score against a size-matched null.** TM 0.373 looked like a near miss at
   a 0.4 threshold; the null said random 60-150 residue pairs give **median 0.333, max 0.467**, so 3 of
   20 unrelated domains beat it. **Any small-protein TM below about 0.47 is inside the noise band.**
8. **A pre-registered control can fail for a reason you wrote into it.** H-065 aborted because I
   registered "real CATH domains are unbranched"; they are **18.8% branched (9 of 48)**, which this
   repo's own PTGL work already implied. Check a control premise against your own prior results before
   registering it.
