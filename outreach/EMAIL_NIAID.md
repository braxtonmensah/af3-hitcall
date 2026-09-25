# NIAID Preclinical Services inquiry (DRAFT v2 — not sent)

## Research done to check this is a sensible ask, not a waste of their time

| Question | Answer |
|---|---|
| Is the service real and free? | Yes. *"NIAID's free preclinical services... Product developers from academia, nonprofit organizations, industry, and government can request preclinical services. You need not be a grantee."* |
| Does it cover bacteria like ours? | Yes. Therapeutic Development Services covers *"the full range of pathogens, including bacteria"*, and the In Vitro Assessment for Antimicrobial Activity Program evaluates candidates *"against microbial pathogens and vectors, including clinical isolates"*. |
| Is *M. pneumoniae* in a DMID portfolio? | Yes. **Respiratory Diseases Branch** covers *"other bacterial respiratory diseases including... community acquired pneumonia"*. M. pneumoniae is the classic atypical CAP pathogen. |
| Is *M. genitalium* in a DMID portfolio? | Yes, explicitly. **Enteric and Sexually Transmitted Infections Branch** lists *"infections caused by Ureaplasma urealyticum and Mycoplasma genitalium"*. |
| Who is the right preclinical-services contact? | **Christian Gonzalez** — listed as "preclinical services: respiratory viruses, **respiratory bacteria**". For M. genitalium it would be **Kimberly Murphy** (STI preclinical services). |
| Will they assay compounds now? | **No, and the email does not ask them to.** Their published review criteria require "sufficient quality and/or quantity of product available" and "preliminary data adequate to support the request". We have no compound yet. This is an eligibility inquiry, which is the point: it tells us whether to spend money on compounds at all. |

**Verdict: the ask is sound.** It is scoped as a question about eligibility and requirements, which is exactly the confirmation step you asked for before spending anything.

**Addresses:** the contacts page lists names without emails, so I am not going to invent any. Send to the
published service mailbox and name the officer; ask them to redirect. Staff addresses can be looked up at
niaid.nih.gov/about/find-niaid-staff if you want to add him directly.

**To:** invitro@mail.nih.gov
**Subject:** Eligibility question — in vitro antimicrobial assessment against *Mycoplasma pneumoniae*

---

Dear NIAID Preclinical Services team,

I have a question about eligibility for the In Vitro Assessment for Antimicrobial Activity Program,
before I invest in compounds. If this is better directed to Christian Gonzalez in the Respiratory
Diseases Branch, who is listed for respiratory bacteria preclinical services, I would be grateful if you
could forward it.

**The target.** *M. pneumoniae* RNase J (MPN280) appears to form a 2:2 heterotetramer with MPN621, a
paralog that has lost all four catalytic residues of the metallo-beta-lactamase nuclease active site.
Both genes are essential by transposon mutagenesis (Lluch-Senar et al. 2015, *Mol Syst Biol*), and
MPN621 is essential by colony isolation as well. So the catalytically dead subunit is itself required
for viability, which points to the protein-protein interface as the functional dependency.

The architecture is supported by AlphaFold3 (interface ipTM 0.84), by in-cell crosslinks from two
independent crosslinking chemistries (all six inter-protein crosslinks satisfied in every model sampled,
where a 1:1 heterodimer leaves three of them at 51-63 A), and by published size-exclusion proteomics
placing both subunits in the same 298 kDa fraction, which matches the 2:2 prediction and excludes the
127 kDa heterodimer.

**Selectivity.** The nearest human relative is CPSF73, which retains three of the four catalytic
residues, so an active-site inhibitor would carry real cross-reactivity risk. The interface itself is
only 24.6% identical to CPSF73, so an interface-directed agent is the selective option. That is the
approach I am pursuing.

**My questions, in order of importance.**
1. Is *M. pneumoniae* within the scope of the current In Vitro Assessment of Antimicrobial Activity
   contract, and would MIC determination against it be feasible?
2. **What preliminary data would you consider adequate** to support a request? I have structural and
   genetic target validation but **no compound activity data**, which I recognise is the gap. I would
   rather learn what you need now than submit something premature.
3. Is a Nonclinical Evaluation Agreement required before submitting, and can one be executed with a
   single-member LLC rather than a university?
4. What compound quantity and purity would you need?

I am selecting candidate compounds by structure-based virtual screening against that interface, using an
openly licensed model, and would supply them myself. I am an undergraduate at Indiana University doing
this work independently. Everything is pre-registered and reproducible, and I am happy to share the full
analysis record and the structural models.

Thank you for any guidance, even if the answer is that this is premature.

Braxton Mensah
bsmensah@iu.edu

---

## A second, separate question worth asking later

*M. genitalium* has rising macrolide resistance and is explicitly named in the STI branch portfolio, so
it may attract more interest than *M. pneumoniae*. **But our own data argues against leading with it:**
MG_423 is **non-essential** in *M. genitalium* while MPN621 is essential in *M. pneumoniae*. Lead with
the organism where the evidence holds. Mention M. genitalium only as a follow-up question to Kimberly
Murphy once the M. pneumoniae route is established.
