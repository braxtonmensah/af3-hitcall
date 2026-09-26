# Post-hoc analyses (NOT pre-registered)

Written after H1-H3 results were seen. Anything here is a lead, not a claim, until tested on
held-out data.

- **PH1.** Split H1 positives into: co-complex precedent / both proteins have PDB homologs but no
  joint entry / at least one protein has none. Question: is the H1 gap about the co-complex or
  about the proteins being structurally known?
- **PH2.** The pool-size experiment (paper Fig. 3, MOESM8) ran each pool size on a *disjoint*
  ~95-protein section (verified: zero shared proteins between conditions). Each condition is
  compared with the genome-wide screen on the same pairs, so section difficulty cancels.

---

## PH-DRUG (2026-09-25, descriptive join, not a hypothesis test)

**Question:** how many interfaces in the forward registry sit inside a protein complex that already has
drug annotation? CORUM 5.0 ships a drug table (`corum_drugs.txt`, Zenodo `10.5281/zenodo.17419058`),
which is what its 2024 paper "protein complexes as drug targets" is built on.

**Result: 92 unique registry interfaces**, out of 6,009, lie inside at least one human CORUM complex
carrying drug annotation. Table: `drugged_unsolved_interfaces.csv`.

*(6,009 and not the 6,010 quoted elsewhere: the registry holds 6,010 distinct accession pairs but 6,009 distinct gene-symbol pairs, because TADA3-TADA2A appears under two accessions for TADA2A. CORUM is keyed on gene symbols, so this join is gene-level. See `registry/README.md`.)*

Highest-confidence examples: TADA2B-TADA3 (SAGA, pDockQ 0.731), HDAC1-SIN3A (0.728, in 29 distinct
CORUM complexes), NCAPD2-NCAPH (condensin I, 0.728), GUCY1A2-GUCY1B1 (soluble guanylate cyclase, the
nitrate target, 0.712), the SMARCC/SMARCD SWI-SNF pairs (0.688-0.720), PDE1A-PDE1C (dipyridamole,
0.694), DTX3L-PARP9 (androgen receptor complex, 0.666).

**What this is NOT, and the distinction is the whole point.** CORUM's `subunits_drugs` field means *a
subunit of the complex is targeted by these drugs*, not that the interface is. Vorinostat targets
HDAC1's catalytic site; it says nothing about the HDAC1-SIN3A interface. So this is **a list of
structural blind spots inside complexes of existing pharmacological interest**, not a list of
druggable interfaces, and it must never be presented as the latter.

**Three further caveats.**
1. The registry's "unsolved" means no *direct* co-complex in SIFTS as of 2026-09-20. Homologous or
   paralogous structures often exist, and for the 14-3-3 pairs (YWHAB/G/H/Z) homodimer structures
   certainly do, so several entries are less novel than the row suggests.
2. CORUM lists heavily overlapping complexes, which is why the raw complex-level count was 131 and the
   deduplicated interface count is 92. Always count unique pairs.
3. An earlier version of this join used Burke's 2021 `int3D_model_structure` flag and was wrong,
   because five years of structures have been deposited since. The registry is the correct denominator.

**Status: descriptive.** No gate, no null, no claim about accuracy or druggability. It is a lookup that
says where this project's confident models overlap with complexes the pharmaceutical literature already
annotates, and it is useful for choosing which interface to model next, nothing more.

### PH-DRUG addendum, 2026-09-26: the join is dominated by one signal, quantified

The caveat above says CORUM's `subunits_drugs` means a subunit is drugged, not the interface. That is
correct but it understates how concentrated the effect is. Counted:

- **46 of the 92 rows carry the identical five-drug HDAC-inhibitor string**, and 51 carry vorinostat
  at all. Those rows say "HDAC1 or HDAC2 is somewhere in this complex" and nothing about an interface.
- Rows like TUBA1C-TUBB with 18 drugs, or H2AC20-H2BC18 with 14, are the join misfiring on
  promiscuously-annotated complexes rather than finding druggable interfaces.

So the 92 should not be described as 92 independent observations. **Cite this table only as a lookup
for which interface to model next, never as a count of druggable interfaces**, and if a number is
quoted, quote it after removing the HDAC block.

Separately, and for the same reason of not double-counting: the **MMV Pathogen Box is not an
independent compound prior** from CO-ADD. 397 of its 398 compounds are already inside CO-ADD's ChEMBL
deposit, so any staging plan listing them as two priors (including the table in
`cleanroom/LIBRARIES.md`) is counting one set twice.
