# NIH SBIR Phase I — Specific Aims (DRAFT, not submitted)

**Framing decision, and why it matters.** Two SBIRs are possible from this work:

- *(a) The drug target.* Develop inhibitors of the RNase J : MPN621 interface. **Weak for Phase I**:
  no wet lab, no chemistry, no compounds. Reviewers would reject on feasibility.
- *(b) The platform, with the target as proof.* Software that tells a drug-discovery team which
  AI-predicted protein complexes are real and worth bench time. **This is the fundable one**: it needs
  no wet lab, NIH funds research tools, and we have prospective, pre-registered performance data plus a
  worked discovery.

Aims below are written for (b). The RNase J complex appears as the demonstration that it works.

---

## Specific Aims

AI structure predictors now generate protein-interaction maps for entire genomes, but users cannot tell
which predictions deserve an experiment. Our own audit quantifies the problem: across a genome-wide
screen, size-corrected confidence separates known complexes well (AUROC 0.85) and is close to chance
on interactions never previously solved (0.57-0.71). Teams therefore either trust everything, wasting
bench resources, or trust nothing, discarding real biology.

We established that the discarded class is mostly recoverable. Taking predictions frozen in 2021 and
scoring them against structures released in 2022-2026, which no model had seen, confident predictions of
never-solved complexes had the correct interface **81% of the time in human (n=146) and 89% in yeast
(n=84)**, against 2% for low-confidence predictions. Every test was pre-registered before the outcome
was examined, and the result survived removal of homologous precedent, a shuffled-interface null, an
entry-level cluster bootstrap, and an independent contact-based metric.

Applying the method to *Mycoplasma pneumoniae* produced a previously undescribed complex architecture:
the essential RNase J (MPN280) and the essential, catalytically dead paralog MPN621 form a 2:2
heterotetramer. Five independent lines agree, and only the tetramer explains all six in-cell crosslinks.

**Aim 1. Build the triage engine on an unencumbered model.** Re-implement the pipeline on Boltz-2
(MIT-licensed, commercial use permitted) so outputs carry no third-party use restriction. Deliverable:
a tool that ingests predicted complexes and returns a calibrated probability the interface is correct,
with per-residue confidence.
*Milestone:* reproduce the human and yeast prospective accuracies within 5 percentage points.

**Aim 2. Add orthogonal-evidence scoring.** Integrate public in-cell crosslinking (PRIDE, CC0) and
size-exclusion proteomics as automatic tests: crosslink satisfaction against the model, and apparent-mass
consistency with the predicted stoichiometry. Both discriminated in our hands (controls 0/20 supported;
SEC peak fraction shared by only 5% of proteins).
*Milestone:* on a held-out organism, rank true complexes above decoys with AUROC >= 0.85.

**Aim 3. Demonstrate prospective value on the RNase J target.** Deliver a validation dossier for the
RNase J : MPN621 interface: interface map, druggability assessment, and human off-target analysis (the
interface is 24.6% identical to human CPSF73 versus 3/4 catalytic residues conserved, so an
interface-directed agent is the selective option). Confirm the 2:2 stoichiometry by mass photometry
through a fee-for-service provider.
*Milestone:* experimental confirmation of the predicted stoichiometry.

**Commercial outcome.** Drug-discovery and target-discovery groups pay to avoid dead-end experiments.
Phase I delivers the validated engine and one worked target; Phase II scales to full proteomes and
packages it as a service.

---

## Notes for whoever finalises this

- Institute fit: NIAID (antibacterial resistance) or NIGMS/NLM (research tools and informatics).
- Aim 3's mass photometry is the only outsourced wet work and is cheap; get a quote before submitting.
- Do not cite or reuse AlphaFold Server output in the commercial product. Aim 1 exists to remove it.
- Every number above traces to `RESULTS.md` and is reproducible from the repo.
