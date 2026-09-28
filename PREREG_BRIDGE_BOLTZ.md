# PREREG BRIDGE-BOLTZ: run all three arms on ONE engine, and pre-commit to the gate on that engine

Written 2026-09-28 **before any BRIDGE job was run on Boltz-2**. Amends `PREREG_BRIDGE.md`; everything
not restated here is inherited unchanged.

## 0. The problem this fixes

`cleanroom/bridge/RUN.md` records that **arm P was run on AlphaFold Server** on 2026-09-25 and passed its
gate (2 of 20 against a bar of at most 4). Arms **BR and CT were never run**, 40 jobs outstanding.

`PREREG_BRIDGE.md` allows either engine but requires the engine be recorded per pair. **It does not
address running different ARMS on different engines, which is worse than either choice alone:**

- **B1 = BR vs P** would compare a Boltz arm against an AlphaFold Server arm. Any difference is then
  **engine-confounded** and uninterpretable.
- **B2 = BR vs CT**, the comparison that `RUN.md` says "licenses any claim about co-dependency", would be
  clean, since both would be Boltz.

**Decision, registered now: all 60 jobs, all three arms, are run on Boltz-2 on Quartz H100s.** IU RT
Project access arrived 2026-09-28, so the compute is free and there is no reason to accept an engine
confound to save it.

## 1. The gate is re-run on Boltz and is binding on Boltz

`PREREG_BRIDGE.md`: arm **P** must reproduce the original AlphaFold failure, **at most 4 of 20** pairs
showing an A-B interface, or "the engine has simply solved what AF2/FoldDock could not, and the whole
premise is void".

**Registered, and this is the part that must not be renegotiated later:**

- **The gate is evaluated on the BOLTZ arm P, not inherited from the AlphaFold Server run.**
- **If Boltz arm P shows more than 4 of 20 interfaces, BRIDGE-on-Boltz is VOID.** I report that Boltz
  solves these pairs, which is itself a finding about Boltz, and **I do not fall back to the AlphaFold
  Server P in order to rescue B1 or B2.** Falling back would be choosing the engine that gives the
  answer I want, after seeing both.
- The AlphaFold Server P result (2 of 20) is reported alongside as an independent engine's answer, never
  merged with the Boltz arms.

## 2. Unchanged from PREREG_BRIDGE.md

Interface definition, the 3-of-5-samples rule, `score_bridge.py`, the design table `bridge_design.csv`
with its bridge/control `min r` separation, B1 and B2 as McNemar tests, and the pre-registered weakness
that **8 of the 20 pairs are mitoribosomal**, with no general claim made if more than half the successes
are mitoribosomal.

## 3. Execution facts, recorded so the run is reproducible

- Engine **Boltz-2 v2.2.1**, weights from `~/af3screen/boltz_cache` (12 GB, offline).
- **MSAs precomputed on the Quartz login node** for all **53 unique chains**, because compute nodes have
  no internet and `--use_msa_server` cannot work there. Written to `~/af3screen/msa/<CHAIN>.a3m` and
  referenced from each YAML, the same convention the virtual screen used.
- `--diffusion_samples 5`, matching the 5 samples AlphaFold Server returns, so the 3-of-5 rule is
  satisfiable identically on both engines.
- Jobs: 60, max 2,723 tokens, median 957.
- Any job producing no structure is **counted and reported as attrition**, never silently dropped, and
  the arm is aborted rather than reported short if attrition exceeds 2 of 20 in any arm.
