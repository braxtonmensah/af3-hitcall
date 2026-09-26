# Compound libraries for the RNase J screen

Target: *Mycoplasma pneumoniae* RNase J, an oligomerisation / protein-protein interface.
Docking engine: Boltz-2, hard reject above **128 atoms counting heavy atoms AND hydrogens**
(`libgen.MAX_TOTAL_ATOMS`). Compute: **30-60 s GPU per compound**, so **60-120 compounds per
GPU-hour**, call it **80/h** at 45 s. A 10-20 GPU-hour budget buys **~800-1,600 compounds**.

All checks in this document were run **2026-09-25**. Every URL marked CONFIRMED was actually
fetched from this machine and returned the stated status and byte count. Anything not confirmed is
labelled as such. Nothing here is an invented endpoint.

## Status of what is already built

`library_master.tsv` already holds **10,547 unique compounds** (InChIKey-deduped) from ChEMBL
phases 1-4: approved 2,297, phase 3 885, phase 2 6,497, phase 1 868. All 10,547 already pass the
128-atom Boltz-2 bound; 10,410 are at or under 55 heavy atoms; 1,401 are flagged `is_fragment`;
557 carry a PAINS flag. **Item 1 of the brief is therefore already done.** The value left on the
table is antibacterial-specific, PPI-specific, fragment and natural-product space, plus a
purchasability join.

---

## Comparison table

| Library | Size | Download URL / API | Licence | Purchasable? | Typical mg price | Relevance to an antibacterial PPI target |
|---|---|---|---|---|---|---|
| **ChEMBL phase 1-3** | 9,267 SM (978/7,115/1,174); 8,720 at heavy<=55 | `https://www.ebi.ac.uk/chembl/api/data/molecule.json` CONFIRMED | CC BY-SA 3.0 | Partly, case by case | n/a | Medium. Generic clinical space. **Already fetched.** |
| **ChEMBL ATC J01** (antibacterials, systemic) | 229 molecules | same API, `atc_classifications__level2=J01` CONFIRMED | CC BY-SA 3.0 | Yes, mostly generic | $10-100/g | High prior, but ~all already inside the approved 3,273 |
| **ChEMBL src_id=40 (CO-ADD deposit)** | 24,205 distinct molecules | `compound_record.json?src_id=40` CONFIRMED | CC BY-SA 3.0 | Mostly **no** (donated academic compounds) | n/a | Very high chemotype prior; clean licence route to CO-ADD |
| **CO-ADD bulk dump** | 100,523 screened; **1,403 with a real bacterial MIC**; 523 at MIC<=8 | `https://db.co-add.org/javax.faces.resource/CO-ADD_r03.02-2020_CSV.zip.xhtml?ln=files` CONFIRMED 13,391,761 B | UQ site notice says **personal, non-commercial**; ambiguous. See note | Mostly **no** | n/a | **Highest antibacterial prior of any free set.** Weak on purchasability |
| **SPARK** | ~160,000 compounds, >120,000 datapoints | `https://www.collaborativedrug.com/hubfs/SPARKDataDownload.zip` CONFIRMED 73,527,970 B | **R&D use only** (terms PDF). Flag for commercial | Mixed; much is pharma legacy | n/a | High. Gram-negative permeability + MIC data. Licence is the catch |
| **MMV Pathogen Box** | 400 | via ChEMBL `compound_record.json?src_id=34` CONFIRMED (400 distinct) | Data CC BY 4.0 on publication | **Yes, free plates** | $0 (free, 10 uL of 10 mM DMSO) | High. Anti-infective-validated, physically obtainable |
| **MMV Pandemic Response Box** | 400 (201 antibacterial) | `.../Pandemic_Response_Box_list_of%20compounds_0.xlsx` CONFIRMED 2,590,861 B, 404 rows, SMILES + ChEMBL ID | Data CC BY 4.0 on publication | **Yes, free plates** | $0 | **Best size:prior:obtainability ratio in the whole table** |
| **Open Source Antibiotics** | Tens-to-hundreds, in project spreadsheets | `github.com/opensourceantibiotics` CONFIRMED (5 repos) | **No licence declared on any repo** | Some, synthesised on request | n/a | Niche. Mur ligase series, not a screening library |
| **COCONUT 2.0** | 695,133 NPs (Sep-2024 paper); monthly releases | `https://coconut.s3.uni-jena.de/prod/downloads/2026-09/coconut_csv_lite-09-2026.zip` CONFIRMED 199,089,109 B | **CC0** (cleanest licence here) | Rarely | high, NP-dependent | Medium. Antibiotics are NP-derived, but most of it is unbuyable |
| **LOTUS** | 750,000+ structure-organism pairs | Zenodo `19360665` CONFIRMED (20,594,507 B + 90,298,678 B) | CC BY 4.0 | Rarely | n/a | Medium-low. Taxonomy-linked, not activity-linked |
| **NPASS 3.0** | 204,023 NPs, 1,048,756 activities | `https://bidd.group/NPASS/downloadFiles/NPASS3.0_naturalproducts_structure.txt` CONFIRMED 64,734,351 B | **Not stated** on the download page | Rarely | n/a | Medium. Activity records make it filterable to antibacterials |
| **SuperNatural 3.0** | 449,058 (per paper) | `bioinf-applied.charite.de` — **DNS does not resolve**, unreachable | n/a | n/a | n/a | **Dead. Do not plan around it** |
| **ZINC22** | 230M+ purchasable (not independently verified) | `https://files.docking.org/zinc22/zinc-22{a-z}/H{NN}/...` CONFIRMED | Use freely; **no redistribution** of major portions | Yes, make-on-demand | ~$100-150 / 5-10 mg typical for REAL-space | Medium. **Organised by heavy-atom count**, which maps exactly onto the Boltz-2 bound |
| **ZINC20 2D tranches** | tranche files ~5k molecules each | `https://files.docking.org/2D/HC/HCAA.smi` CONFIRMED 5,616 lines | same | Yes | as above | Medium |
| **Enamine Antibacterial ABAC-30** | 30,000 (~20% pass eNTRy rules) | `enamine.net/component/download/?view=file&f=1002` — **302 to login page**, CONFIRMED gated | Proprietary; free account to download | Yes | Quote only, not published | **Best antibacterial design prior that is also buyable.** Needs a free account |
| **Enamine PPI Fragment PPIF-3600** | 3,600 | `?view=file&f=` (login-gated) | Proprietary | Yes | Quote only | **Directly on-target: PPI hot-spot-mimetic fragments** |
| **Enamine fragment collection** | 330,020 total; ESS-320, HFF-1920, DSI-860, MiniFrags-80, 3DF-1200, NPL-4160, SPF-1500, CAF-4000 | login-gated | Proprietary | Yes | Quote only | High for a PPI interface |
| **Mcule in-stock** | 7,174,166 | `https://dl.mcule.com/database/mcule_purchasable_in_stock_260802.smi.gz` CONFIRMED 110,009,557 B | Free download, 2D + Mcule IDs; purchase via quote | **Yes, in stock** | Quote; see MolPort benchmark | Purchasability join for anything else |
| **Mcule RNA-binding in-stock** | 389,179 (783,323 full) | `https://dl.mcule.com/libraries/mcule_rna_binding_instock_library_260801.zip` CONFIRMED 43,450,511 B | as above | Yes | as above | **Underrated: the target is a ribonuclease** |
| **Mcule fragment economy in-stock** | 12,262 (197,577 in-stock) | `.../mcule_fragment_instock_library_260801.zip` CONFIRMED 2,554,922 B | as above | Yes, cheap tier | cheapest tier | High. Free, buyable, fragment-sized |
| **Mcule bioactivity economy in-stock** | 9,339 (26,121 in-stock) | `.../mcule_bioactivity_instock_library_260801.zip` CONFIRMED 4,546,021 B | as above | Yes | cheap tier | Medium-high |
| **Mcule natural products in-stock** | 127,578 | `.../mcule_natural_products_instock_library_260801.zip` CONFIRMED 9,075,102 B | as above | Yes | as above | The buyable slice of NP space |
| **DSI-poised fragment library** | 768 in the XChem deployment (Enamine sells DSI-860) | `https://xchem.github.io/oxxchem/DSI_poised_fragment_library.xlsx` CONFIRMED 8,244,839 B, no login | Not stated on the file; academic-published | **Yes, from Enamine** | Quote | **The conventional first move on a hard PPI interface** |
| **iPPI-DB** | **2,426** compounds | `https://ippidb.pasteur.fr/compounds/?format=csv` CONFIRMED 217,134 B, 2,426 rows w/ SMILES | Not stated; Institut Pasteur, academic-open | Some | n/a | **The single most on-target chemotype prior available free** |
| **TIMBAL** | 6,896 small molecules (v2, 2013) | all three legacy Cambridge URLs **dead** | n/a | n/a | n/a | **Offline. Cite the paper, do not plan around it** |
| **2P2I / 2P2Idb** | 242 unique inhibitors | `2p2idb.cnrs-mrs.fr` **dead** | n/a | n/a | n/a | **Offline** |

Price benchmark, sourced: MolPort's own write-up of a published cluster-search study describes
targeting "the smallest library that could be purchased in reasonable quantities for **< 100 US$
per 5 mg**" across their 7.6M+ in-stock compounds. Neither Enamine nor Mcule publishes per-mg
prices; both are quote-only, and I could not open Mcule's individual compound pages (Cloudflare).
Treat **$50-100 per 5-10 mg** as the planning figure for a catalogue compound and verify by quote.

---

## Per-library fetch recipes

### 1. ChEMBL beyond approved

API root `https://www.ebi.ac.uk/chembl/api/data/`. Live version at time of check:
**ChEMBL_37, released 2026-05-01**, 2,921,148 distinct compounds, 24,527,044 activities
(from `/status.json`, CONFIRMED). Licence **CC BY-SA 3.0** — commercial use is permitted with
attribution, but share-alike applies to redistributed derivatives. Flag that for the commercial
angle: it does not stop you using it, it constrains how you redistribute a derived dataset.

Clinical-phase counts, each CONFIRMED by reading `page_meta.total_count`:

| Query | `total_count` |
|---|---|
| `molecule.json?max_phase=1&molecule_type=Small molecule` | 978 |
| `molecule.json?max_phase=2&molecule_type=Small molecule` | 7,115 |
| `molecule.json?max_phase=3&molecule_type=Small molecule` | 1,174 |
| `molecule.json?max_phase=4&molecule_type=Small molecule` | 3,475 |
| phases 1-3 with `molecule_properties__heavy_atoms__lte=55` | **8,720** |

Push the Boltz-2 size bound into the query instead of discovering it locally:

```
https://www.ebi.ac.uk/chembl/api/data/molecule.json
  ?max_phase__gte=1&max_phase__lte=3
  &molecule_type=Small%20molecule
  &molecule_properties__heavy_atoms__lte=55
  &limit=1000
  &only=molecule_chembl_id,molecule_structures
```

Page by following `page_meta.next` and prefixing `https://www.ebi.ac.uk`.

Note the small deltas against `library_sources.json` (950 vs 978, 7,016 vs 7,115, 1,113 vs 1,174).
That is consistent with your fetch dropping records without structures, but it is worth one line in
`provenance.json` saying which, so the counts in a write-up are defensible.

**Antibacterial-annotated subsets.** Two routes, both CONFIRMED.

*ATC classification.* `atc_class.json?level2=J01` resolves the WHO antibacterial class.
`molecule.json?atc_classifications__level2=J01` returns **229** molecules;
`atc_classifications__level1=J` (all systemic anti-infectives) returns **394**. These are approved
drugs, so expect near-total overlap with your existing 3,273. Useful as a **positive-control set**,
not as an expansion.

*Deposited screening datasets.* `source.json?limit=1000` lists them. The antibacterially relevant
ones, with `compound_record.json?src_id=N&limit=1` counts, all CONFIRMED:

| src_id | short name | compound_records | notes |
|---|---|---|---|
| 34 | MMV_PBOX | 1,574 | **400 distinct molecules** (verified by full pagination) |
| 40 | COADD | 24,315 | **24,205 distinct molecules** (verified by full pagination) |
| 22 | GSK_TB | 826 | *M. tuberculosis* whole-cell |
| 23 | OSM | 211 | Open Source Malaria |
| 55 | EUBOPEN_CGL | 8,929 | chemogenomic library |
| 68 | EU-OPENSCREEN | 1,813 | |
| 14 | DNDI | 7,070 | |
| 60 | MMV_MALARIA_HGL | 147,472 | too big and off-pathogen |

```
# Pathogen Box structures, licence-clean, no registration. CONFIRMED to return exactly 400.
https://www.ebi.ac.uk/chembl/api/data/compound_record.json?src_id=34&limit=1000&only=molecule_chembl_id
# then molecule.json?molecule_chembl_id__in=<comma list, <=~200 per call> for SMILES
```

*Measured activity against bacteria.* The obvious query fails and it is worth knowing why:
`pchembl_value__gte=5` combined with `standard_type=MIC` returns **0** rows, because MIC records
largely have no pChEMBL value. Against *S. aureus*, `pchembl_value__gte=6` alone yields 1,808 rows
while `standard_type=MIC` yields 160,956. **Filter on `standard_value` + `standard_units`, not on
pChEMBL.** All CONFIRMED:

```
https://www.ebi.ac.uk/chembl/api/data/activity.json
  ?target_organism=Staphylococcus%20aureus
  &standard_type=MIC&standard_units=ug.mL-1&standard_value__lte=1
  &limit=1000&only=molecule_chembl_id,standard_value,target_organism
```

| organism | MIC rows | <=8 ug/mL | <=1 | <=0.5 |
|---|---|---|---|---|
| *S. aureus* | 160,956 | 77,616 | 38,681 | 26,899 |
| *E. coli* | — | — | 18,740 | 15,144 |
| *M. tuberculosis* | — | — | 6,251 | 4,657 |

Those are **activity rows, not distinct molecules**; de-duplicate after pagination.
`assay.json?assay_organism=Staphylococcus aureus` returns 38,786 assays if you want to slice by
assay instead.

**Finding that matters for this project:** ChEMBL has **no *Mycoplasma pneumoniae* target**.
`target.json?organism__icontains=Mycoplasma` returns exactly **7** organism-level targets —
*M. mycoides*, *M. putrefaciens*, *Metamycoplasma hominis*, *Mesomycoplasma hyopneumoniae*,
*M. hyorhinis*, *Mycoplasma* (genus), *M. capricolum* — and none is *M. pneumoniae*. There is no
pathogen-matched activity prior to be had from ChEMBL. Any antibacterial enrichment you build is a
proxy through other species.

### 2. CO-ADD

Browse UI `https://db.co-add.org/screening-data` currently reports **101,010 entries**, filterable
by activity against S. aureus / E. coli / K. pneumoniae / P. aeruginosa / A. baumannii / fungi, plus
HEK293 cytotoxicity and hRBC haemolysis. The **bulk download is older than the UI** — the newest
CSV release is `r03.02-2020`.

```
# CONFIRMED: HTTP 200, application/zip, 13,391,761 bytes. Downloaded and parsed.
curl -L -o coadd.zip \
  "https://db.co-add.org/javax.faces.resource/CO-ADD_r03.02-2020_CSV.zip.xhtml?ln=files"
# contains:
#   CO-ADD_InhibitionData_r03_01-02-2020_CSV.csv    163,499,407 B
#   CO-ADD_DoseResponseData_r03_01-02-2020_CSV.csv    8,521,909 B
```

Also available separately and CONFIRMED: inhibition-only CSV zip (12,839,818 B) and
dose-response-only CSV zip (551,965 B) at the same `javax.faces.resource/<name>.xhtml?ln=files`
pattern. The **SDF link on their own downloads page is broken** —
`CO-ADD_r02.11-2019_SDF.zip` returns **404**. Use the CSV.

What is actually in it, measured by parsing the files rather than quoted from a page:

- Inhibition (single-concentration): 802,918 rows, **100,523 unique compounds**.
- Dose-response: 42,209 rows, **4,803 unique compounds**. `DRVAL_TYPE` is MIC (35,008), CC50
  (4,598) or HC10 (2,603); units are `ug/mL` (33,808) or `uM` (8,379).
- **1,403 unique compounds carry an uncensored MIC (no `>`) against a Gram-positive or
  Gram-negative bacterium.** Of those, **1,397 pass the Boltz-2 128-atom bound** and 1,372 are at
  or under 55 heavy atoms.
- At MIC <= 8 (units as reported): **523 compounds, 518 Boltz-2-feasible, 500 at heavy<=55**.
- At MIC <= 2: 159 compounds, 156 feasible, 145 at heavy<=55.
- Largest contributing libraries: Russian Academy of Science, MMV Pandemic Response Box, NIH/NCI
  Diversity Set V, NIH Clinical Collection, MMV Pathogen Box, MMV Small Polar Library.

**Licence caution.** CO-ADD publishes no data licence. The UQ site notice at
`https://www.co-add.org/content/privacy-copyright` (CONFIRMED) reads: "For personal,
**non-commercial** purposes, you may view or make copies of the material contained on the site.
Content may **not be systematically downloaded**, retrieved or stored." That is a generic website
copyright notice rather than a dataset licence, and it sits awkwardly beside a page whose entire
purpose is a bulk download. Given the commercial angle, **do not rely on it**. Two clean options:

1. **Use ChEMBL src_id=40 instead** — 24,205 of the same CO-ADD molecules, under CC BY-SA 3.0.
   This is the recommended path and it costs you nothing.
2. Email `info@co-add.org` and get the terms in writing.

### 3. SPARK

Pew's SPARK transferred to CO-ADD/UQ in Nov 2021; `https://spark.co-add.org/` (CONFIRMED) states
**~160,000 compounds and >120,000 associated data points** and points at CDD Vault for the archive.

```
# CONFIRMED: HTTP 200, application/zip, 73,527,970 bytes. No login, no registration.
curl -L -O "https://www.collaborativedrug.com/hubfs/SPARKDataDownload.zip"
# terms, CONFIRMED: HTTP 200, application/pdf, 160,848 bytes
curl -L -O "https://www.collaborativedrug.com/hubfs/SPARK-data-terms-of-use.pdf"
```

Nine datasets: compounds + physicochemical properties, MIC assays, IC50 assays, intracellular
accumulation assays, and contributions from Achaogen, Novartis, Merck & Kyorin, CO-ADD and the
Quave Lab. CSV and SDF.

**Licence flag, read from the terms PDF directly.** Section 2.a, in the document's own bold:
"You may access and/or export SPARK Public Projects Data owned by third parties **ONLY FOR RESEARCH
AND DEVELOPMENT PURPOSES**", and it is your responsibility to "obtain any and all necessary rights,
including ... copyrights, trademarks, patents ... if and when disseminating, commercializing, or
otherwise creating new intellectual property rights from and in the SPARK Public Projects Data."
There is also an export-control clause and a broad indemnity. This is **usable for the screen and
risky as a basis for a commercial claim.** Much of it is donated pharma legacy chemistry with live
patent families behind it.

### 4. MMV open boxes

**Pandemic Response Box** — the best-value entry in this whole document.

```
# CONFIRMED: HTTP 200, xlsx, 2,590,861 bytes, 404 data rows.
# Needs a browser User-Agent; curl's default UA gets 403 from mmv.org.
curl -L -A "Mozilla/5.0" -O \
  "https://www.mmv.org/sites/default/files/uploads/docs/mmv_open/Pandemic_Response_Box_list_of%20compounds_0.xlsx"
```

Sheet 1 (`A1:P405`) carries `MMV ID`, `DISEASE AREA`, `SMILES`, `ChEMBL ID`, `MW`, `FORMULA`,
`PSA`, `ALOGP`, `RULEOF5`. Sheet 2 adds cytotoxicity, PAMPA permeability and mouse microsomal
clearance. Filter `DISEASE AREA == "ANTIBACTERIALS"` for the **201** antibacterial compounds
(composition 201 antibacterial / 153 antiviral / 46 antifungal). A plate-map xlsx sits at
`.../MMV%20PandemicResponseBox_plate%20map.xlsx`.

Physical plates are **free on request** from MMV: 96-well, 10 uL of 10 mM DMSO per compound. The
consideration is open access — you deposit screening data in a public repository such as ChEMBL
within two years and publish under CC BY 4.0 or equivalent with no embargo. For an academic project
that is not a cost. **For a commercial angle it is a real constraint, so read the request form
before you accept plates.**

**Pathogen Box** — 400 compounds, same free-plate model and the same open-access consideration.
I found **no SMILES/SDF file on the MMV supporting-information page**; the structures come from
ChEMBL `src_id=34`, which I paginated in full and which returns exactly **400** distinct molecules.

### 5. Open Source Antibiotics

`https://github.com/opensourceantibiotics` — CONFIRMED, five repositories:

| repo | last push | licence |
|---|---|---|
| `murligase` | 2025-03-10 | **none declared** |
| `Series3-TB_MurLigase` | 2024-11-12 | **none declared** |
| `Series-2-Diarylimidazoles` | 2023-01-23 | **none declared** |
| `OSA_Tech_Ops` | 2022-11-24 | **none declared** |
| `GeneralTopics` | 2022-08-09 | **none declared** |

`opensourceantibiotics.org` does not resolve. The repos hold project material, not a screening
library: `murligase` contains `MurD and MurE fragments_Joe and Becca_summary of screening.xlsx`,
`Microbiology evaluation of WYH compounds.xlsx`, and directories for synthesis, fragments and
reports. Scale is tens to low hundreds of compounds. **Not worth GPU time as a library.** It is
worth reading if you ever want a Mur-ligase comparator, and no GitHub repo without a LICENSE file
should be treated as open for commercial reuse.

### 6. Natural products

**COCONUT 2.0** — the paper states **695,133 unique NP structures** at the Sept-2024 release;
releases are monthly and the current one is 2026-09. Licence **CC0**, no attribution required,
which is the cleanest licence anywhere in this document.

```
# All three CONFIRMED by HEAD: HTTP 200, application/zip, exact content-length shown.
https://coconut.s3.uni-jena.de/prod/downloads/2026-09/coconut_csv_lite-09-2026.zip     # 199,089,109 B
https://coconut.s3.uni-jena.de/prod/downloads/2026-09/coconut_sdf_2d_lite-09-2026.zip  # 315,998,382 B
https://coconut.s3.uni-jena.de/prod/downloads/2026-09/coconut_sdf_3d-09-2026.zip       # 375,162,653 B
```

A full SQL dump (~31.9 GB) also exists. Take `csv_lite`. Substitute the current `YYYY-MM` after
checking `https://coconut.naturalproducts.net/download`; the site is a JS SPA, so read the download
page rather than probing the bucket. Note the REST API paths I tried (`/api/statistics`,
`/api/v1/molecules`) returned 404 or HTML — there is no documented JSON endpoint I could confirm.

**LOTUS** — Wikidata-backed, mirrored at `lotus.naturalproducts.net` (a SPA, no scriptable download).
Canonical bulk download is Zenodo, CONFIRMED via the Zenodo API:

```
# record 19360665, published 2026-04-13, licence cc-by-4.0, DOI 10.5281/zenodo.19360665
https://zenodo.org/api/records/19360665/files/260413_frozen.csv.gz/content           # 20,594,507 B
https://zenodo.org/api/records/19360665/files/260413_frozen_metadata.csv.gz/content  # 90,298,678 B
```

The older `zenodo.org/records/5794106` is the concept DOI and resolves to the same current record.
750,000+ referenced structure-organism pairs; the metadata file carries InChI, SMILES, formula,
exact mass, NPClassifier and ClassyFire classes, and Open Tree of Life taxonomy.

**NPASS 3.0** — version 3.0, released 15 Jun 2025, update paper 2026. Site reports **204,023
natural products**, 48,940 source organisms, 8,764 targets, **1,048,756 activity records**. Plain
HTTP files, no login, all three CONFIRMED by HEAD:

```
https://bidd.group/NPASS/downloadFiles/NPASS3.0_naturalproducts_structure.txt     # 64,734,351 B
https://bidd.group/NPASS/downloadFiles/NPASS3.0_activities.txt                    # 105,252,592 B
https://bidd.group/NPASS/downloadFiles/NPASS3.0_naturalproducts_generalinfo.txt   #  48,379,276 B
```

Index page `https://bidd.group/NPASS/downloadnpass.html` (the `download.php` path is a 404).
**No licence is stated anywhere on the download page** — flag it, and ask before commercial use.
The activity file is what makes NPASS worth more than COCONUT here: you can filter to compounds
with measured antibacterial activity rather than screening all 204k.

**SuperNatural 3.0** — 449,058 compounds per the NAR paper, documented at
`http://bioinf-applied.charite.de/supernatural_3`. **The host does not resolve**: three curl
attempts returned HTTP 000 and a direct fetch returned `getaddrinfo ENOTFOUND
bioinf-applied.charite.de`. Treat as **dead** as of 2026-09-25. Do not budget for it.

### 7. Purchasable space

**ZINC (files.docking.org)** — the web UIs at `zinc.docking.org` and `zinc20.docking.org` are
**CAPTCHA-gated** (302 to `/captcha`), so they cannot be scripted. `cartblanche22.docking.org` is a
JS SPA; its `POST /substance/random.txt` returns `{"task": "<uuid>"}` and I **could not get results
back** from the polling form documented on the wiki (it kept answering `count parameter required`).
The file server is the reliable route and needs no login.

**Licence, read off `https://files.docking.org/` itself:** "Whereas you are free to share results
derived from the use of these files, you may **not redistribute major portions** without the
express written permission of John Irwin". Screening is fine; redistributing the tranches is not.
There is also an explicit no-warranty *caveat emptor*.

ZINC22 is organised **by heavy-atom count**, which lines up exactly with your Boltz-2 bound:

```
https://files.docking.org/zinc22/zinc-22{a..z}/H{NN}/H{NN}{P|M}{logP*10}/H{NN}{P|M}{logP*10}-{K..O}.h.smi.gz
```

CONFIRMED end to end: `zinc-22h/` lists `H11/` through `H29/`; `H17/` lists `H17M000/`..`H17P130/`
plus `H17.txt` index files; and
`https://files.docking.org/zinc22/zinc-22h/H17/H17P020/H17P020-M.h.smi.gz` downloads (5,267 bytes)
and unpacks to **507 lines** of tab-separated `SMILES<TAB>ZINC22_ID`, e.g.
`COC[C@@H](CNc1nccc(C(=O)O)n1)OC   ZINCh800000kFq07`.

`H{NN}` is heavy atoms; `P`/`M` is the sign of logP and the digits are logP x 100. **The trailing
`-K/-L/-M/-N/-O` letter is not explained on the `ZINC22:Numbering` or `Zinc22:Searching` wiki pages
I read** — do not guess at it; pull every suffix in a tranche and de-duplicate on InChIKey.
Some combinations 404 (`H17P020-K` did), which is normal for sparse tranches.

ZINC20 2D tranches use a different, MW-and-logP scheme, also CONFIRMED:
`https://files.docking.org/2D/HC/HCAA.smi` returns 5,616 lines with a `smiles zinc_id` header.
The letter-to-bin mapping lives only in the CAPTCHA-gated tranche browser, so **filter heavy atoms
locally with RDKit after download** rather than trusting the filename.

Curated ZINC subsets worth knowing, directory structure CONFIRMED under
`https://files.docking.org/special/current/`: `world/`, `fda/`, `in-vitro/`, `in-vivo/`,
`biogenic/`, `endogenous/`, `metabolites/`, each with a `tranches/` tree and an `.info.txt.gz`.

**Enamine.** Sizes CONFIRMED from their own catalogue pages.

- **Antibacterial Library ABAC-30**: 30,000 compounds, version 12 Dec 2023. Knowledge-based design,
  physicochemical distribution matched to known antibiotics, **~20% satisfy the eNTRy rules** for
  Gram-negative accumulation (ionisable nitrogen, low three-dimensionality, few rotatable bonds).
- **PPI Fragment Library PPIF-3600**: 3,600 fragments, described as mimicking protein structural
  motifs and hot-spot residues. **This is the most on-target commercial set in the document.**
- Fragment collection 330,020 total, with focused sets ESS-320 (320), HFF-1920 (1,920),
  DSI-860 (860), MiniFrags-80 (80), CFL-8480 (8,480), FDS-1000 (1,000), FFL-d6 (1,280), FFP-800
  (800), NPL-4160 (4,160), 3DF-1200 (1,200), SPF-1500 (1,500), CAF-4000 (4,000).
- Diversity: HLL-460 (460,160), HLL-300 (300,160), HLL-200 (200,000), HLL-100 (100,160),
  DDS-50 (50,240), DDS-10 (10,240), PSL-5760, CSL-11760, E-ASMS-12673, PAINS-320, CONS (83),
  MCR-500.

**The downloads are not anonymous.** `https://enamine.net/component/download/?view=file&f=1002`
(the ABAC SD file) and `?f=1008` both **302 to `https://enamine.net/login-page?return=...`** —
CONFIRMED, I followed the redirect. You need a free Enamine account. Once you have one the `f=NNNN`
ids are stable and scriptable; the ids for the fragment page are 2002, 2006-2008, 2013, 2027-2029,
2038-2043, 2061-2063, 2068, 2071-2074, 2212 and 1066. No pricing is published; everything is
"Request a quote". Screening compounds are stocked at 10+ mg, with 50-150 mg available for hit
resupply from the same batch.

**Mcule.** Free, anonymous, direct download, stated on their page as "You can freely download the
following collections of the high quality Mcule database including 2D structures and Mcule IDs."
Every URL below CONFIRMED by HEAD with the byte count shown.

| Subset | Full | In stock | File | Bytes |
|---|---|---|---|---|
| Purchasable full | 140,523,943 | — | `mcule_purchasable_full_260801.smi.gz` | 2.4 GB |
| In stock | — | 7,174,166 | `mcule_purchasable_in_stock_260802.smi.gz` | 110,009,557 |
| Building blocks | — | 7,341,168 | `mcule_purchasable_building_blocks_260802.smi.gz` | 100,266,699 |
| RNA binding | 783,323 | 389,179 | `libraries/mcule_rna_binding_instock_library_260801.zip` | 43,450,511 |
| Fragment | 473,606 | 197,577 (economy 12,262) | `libraries/mcule_fragment_instock_library_260801.zip` | 2,554,922 |
| Natural products | 136,434 | 127,578 | `libraries/mcule_natural_products_instock_library_260801.zip` | 9,075,102 |
| Bioactivity | 36,028 | 26,121 (economy 9,339) | `libraries/mcule_bioactivity_instock_library_260801.zip` | 4,546,021 |
| HTS | 2,056,106 | 635,956 | `libraries/mcule_HTS_instock_library_260801.smi.gz` | 9,212,719 |
| Covalent | 1,101,716 | 192,107 | `libraries/mcule_covalent_instock_library_260801.zip` | 3,150,475 |
| Macrocycle | 159,808 | 56,621 | `libraries/mcule_macrocycle_instock_library_260801.smi.gz` | 1,049,900 |

Base is `https://dl.mcule.com/database/` for the first three and `https://dl.mcule.com/libraries/`
for the rest. **Dates are in the filenames and they roll monthly** — scrape the current names from
`https://mcule.com/database/` rather than hard-coding. SHA-256 checksums are published per file.
The **"economy" tiers are the cheap in-stock slices** and are the right target given the buy budget.
Prices need an account or an Instant Quote.

### 8. Fragments

The conventional move on a protein-protein interface, and cheap in GPU terms because fragments are
small.

- **DSI-poised library** (Diamond / SGC / iNEXT), 768 fragments as deployed at XChem, designed so
  every fragment carries a handle for fast, robust follow-up chemistry. **Free, anonymous:**
  `https://xchem.github.io/oxxchem/DSI_poised_fragment_library.xlsx` — CONFIRMED HTTP 200, 8,244,839
  bytes, xlsx. Purchasable from Enamine as **DSI-860** (860 compounds). No licence statement on the
  file itself. Diamond's own fragment-libraries page is Cloudflare-protected and I could not read it
  (403 to a fetch, "Just a moment..." to curl), so the per-library counts there are unverified;
  the EUbOPEN DSiP extension is documented elsewhere as 108 compounds.
- **Mcule fragment economy in-stock, 12,262** — free download, in stock, cheapest price tier. The
  most practical free-and-buyable fragment set here.
- **Enamine** ESS-320, HFF-1920, MiniFrags-80, 3DF-1200, NPL-4160, SPF-1500, PPIF-3600 — all behind
  the free-account wall.

One caution worth stating before you spend GPU hours: Boltz-2's affinity head is trained on
drug-like potency data, and fragment binding sits at the bottom of that range. Fragment scores will
compress. Rank fragments **against each other**, not against the drug-like sets, and keep the
property-matched decoy null that `libgen.match_decoys` already builds.

### 9. PPI-inhibitor-curated libraries

**iPPI-DB** (Institut Pasteur) is alive and is the best of the three.

```
# CONFIRMED: HTTP 200, text/csv, 217,134 bytes, 2,427 lines = 2,426 compounds.
curl -L -o ippidb.csv "https://ippidb.pasteur.fr/compounds/?format=csv"
# columns: id,canonical_smile,common_name,molecular_weight,a_log_p,ligand_id,pubs
```

The browse page reports **2,426 compounds found**. I parsed the CSV with RDKit: all 2,426 SMILES
parse, **2,420 pass the Boltz-2 128-atom bound**, and 2,322 are at or under 55 heavy atoms. There is
also a REST API at `https://ippidb.pasteur.fr/api/` exposing `pdb`, `protein`, `chain`, `hotspot`,
`ligand`, `cavity`, `partner` and `summary` — structural rather than compound-centric, and there is
**no `/api/compounds/` endpoint** (404). The `?format=csv` export is the compound route. No licence
statement; academic, Institut Pasteur.

**TIMBAL** — 6,896 distinct small molecules across 50 PPI targets in v2 (2013). All three legacy
hosts are **dead**: `www-cryst.bioc.cam.ac.uk/timbal`, `www.cryst.bioc.cam.ac.uk/timbal` and
`www-cryst.bioc.cam.ac.uk/databases/timbal` all return HTTP 000 / no DNS. The compound list exists
only in the paper's supplementary material now.

**2P2I / 2P2Idb** — 27 protein-protein complexes, 274 protein-inhibitor complexes, **242 unique
small molecule inhibitors** as of the 2016 v2 update. `http://2p2idb.cnrs-mrs.fr/` and the INSERM
Marseille mirror both return HTTP 000. **Dead.**

**Commercial alternatives that are alive:** Enamine **PPIF-3600** (login-gated) and MolPort's
catalogue "PPI Library" and "RNA Binder Set" (I could not open the individual library pages to get
counts — the URL I tried 404'd, so those sizes are unverified).

---

## Recommended staging

Binding constraint is GPU hours, not disk and not download effort. At 80 compounds/GPU-hour a
**10-20 GPU-hour** first tranche is **800-1,600 compounds**. Spend it where the prior per compound
is highest and where a hit can actually be bought or requested.

Everything below feeds `libgen.py --add-file <file>.smi --source-name <name> --licence <lic>`
then `--build`, so InChIKey dedup against the existing 10,547 happens for free. Expect real overlap:
the MMV boxes and CO-ADD actives contain approved drugs you already have.

### Stage 1 — ~11 GPU-hours, ~870 compounds. Do this first.

| Set | n (post-filter) | GPU-h @80/h | Why it earns the slot |
|---|---|---|---|
| **MMV Pandemic Response Box, antibacterials only** | 201 | 2.5 | Highest obtainability of anything here: free plates, SMILES already in hand, every compound pre-selected as antibacterial |
| **MMV Pathogen Box** | 400 | 5.0 | Free plates, anti-infective-validated, licence-clean via ChEMBL src_id=34 |
| **CO-ADD confirmed actives at MIC<=2** | 156 | 2.0 | Strongest measured antibacterial prior per compound in the document. Small enough to be nearly free |
| **iPPI-DB, fragment-sized slice** | ~100 | 1.3 | Cheap probe of whether PPI chemotypes score at all on this interface |

Rationale: Stage 1 is deliberately *not* a diversity screen. It is four small sets with orthogonal
priors — free-and-obtainable, antibacterial-measured, and PPI-chemotype — run cheaply enough that
the result tells you which prior is worth scaling. Dedup will shave perhaps 10-15% off these counts
against your existing 10,547, so budget ~10 GPU-hours actual.

### Stage 2 — ~30 GPU-hours. Conditional on Stage 1.

- **Full iPPI-DB** (2,420 feasible, ~30 GPU-h). Run this **only if the Stage 1 iPPI-DB slice
  enriches**. If PPI chemotypes score no better than your property-matched decoys, this is 30 hours
  bought for nothing, and that negative is worth knowing after 1.3 hours rather than after 30.
- **DSI-poised fragments** (768, ~9.6 GPU-h). The conventional first move on a hard interface, free
  to download, buyable from Enamine. Run as its own ranked cohort, not pooled.
- **CO-ADD actives MIC<=8** (518 feasible, ~6.5 GPU-h) — the widening of the Stage 1 MIC<=2 set.

### Stage 3 — only with a bigger budget or a Stage 1/2 signal.

- **Enamine ABAC-30** (30,000, ~375 GPU-h). The best antibacterial-designed *and* purchasable space
  there is, and unaffordable whole. Register the free account, download the SDF, then **subset**:
  the ~20% that pass the eNTRy rules is ~6,000 (~75 GPU-h), and a diverse 2,000-compound cluster
  sample is ~25 GPU-h. Do this rather than screening the set.
- **Enamine PPIF-3600** (3,600, ~45 GPU-h) — most on-target commercial set, same free-account gate.
- **Mcule RNA-binding in-stock** (389,179). Far too large whole, but the target is a **ribonuclease**
  and this is the only library in the document built around RNA-binding chemotypes. Cluster down to
  1,000-2,000 and treat it as a hypothesis test about the RNA-binding groove, distinct from the
  oligomerisation interface.
- **Mcule fragment / bioactivity economy in-stock** (12,262 / 9,339) — cheap, in stock, free to
  download. Good third-stage diversity that you can actually buy.

### Deprioritise, with reasons

- **ZINC22 / ZINC20 / Mcule full.** Millions of compounds against a 20-GPU-hour budget is a
  rounding error of coverage, and a random slice of make-on-demand space has no antibacterial prior.
  **Use Mcule in-stock as a purchasability join instead** — take your ranked hits, InChIKey-match
  them against `mcule_purchasable_in_stock_260802.smi.gz`, and you learn which hits you can buy
  without spending a single GPU-hour.
- **COCONUT / LOTUS / NPASS whole.** 200k-700k compounds, mostly unbuyable. If you want NP space,
  take **Mcule natural products in-stock (127,578)** and cluster, or filter NPASS by its activity
  records to compounds with measured antibacterial data.
- **SPARK for anything downstream of the screen.** Download it for the Gram-negative permeability
  data, which is genuinely useful context, but the R&D-only terms and live pharma patent families
  make it the wrong provenance for a compound you intend to commercialise.
- **Open Source Antibiotics, SuperNatural 3, TIMBAL, 2P2I.** Too small, dead, dead, dead.

### Three things to settle before Stage 1

1. **Licence.** If the commercial angle is real, build the master library from **CC BY-SA 3.0
   (ChEMBL), CC0 (COCONUT) and CC BY 4.0 (LOTUS)** sources, and pull CO-ADD **through ChEMBL
   src_id=40** rather than from `db.co-add.org`. Keep SPARK and any MMV-plate-derived data in a
   separate, clearly-labelled R&D-only lane. `library_master.tsv` already has a `licence` column;
   that is the right place to enforce this, and it is worth adding a `commercial_ok` boolean.
2. **The MMV open-access consideration.** Free plates come with a published obligation to deposit
   data openly within two years and publish CC BY 4.0 with no embargo. That is free for the academic
   paper and is a genuine constraint on a commercial angle. Read the request form before accepting
   plates; the screen itself is unaffected either way, since the structures are public.
3. **There is no pathogen-matched prior.** ChEMBL has no *M. pneumoniae* target at all. Every
   antibacterial enrichment above is a cross-species proxy, and *M. pneumoniae* has no cell wall,
   which prunes the largest single class of antibacterial chemotypes (beta-lactams, glycopeptides,
   fosfomycin) from relevance. It is worth **filtering cell-wall-targeting chemotypes out** of the
   antibacterial sets before spending GPU time on them, and saying so in the write-up.

---

### Verification log

Confirmed live by direct fetch on 2026-09-25: ChEMBL REST (status, molecule, activity, assay,
target, source, compound_record, atc_class); CO-ADD downloads page, complete CSV zip (downloaded
and parsed), inhibition zip, dose-response zip, screening-data page, privacy-copyright page;
SPARK zip and terms PDF (downloaded and read); spark.co-add.org; MMV Pandemic Response Box xlsx
(downloaded and parsed) and plate map; MMV Pathogen Box structures via ChEMBL (paginated to 400);
Open Source Antibiotics org and repo list via GitHub API; COCONUT download page and three S3
objects; LOTUS via Zenodo API; NPASS download page and three data files; files.docking.org root,
`/2D`, `/special`, `/catalogs`, `/zinc22` trees, one ZINC20 tranche and one ZINC22 tranche
(both downloaded and parsed); Enamine antibacterial, diversity and fragment catalogue pages and the
login redirect on two download ids; mcule database page and ten download objects; DSI-poised xlsx;
iPPI-DB compounds page, API root and CSV export (downloaded and parsed with RDKit); MolPort blog.

Confirmed **dead or inaccessible**: `bioinf-applied.charite.de` (SuperNatural 3, no DNS);
`2p2idb.cnrs-mrs.fr` and the INSERM mirror; all three TIMBAL hosts; `opensourceantibiotics.org`;
CO-ADD's own `CO-ADD_r02.11-2019_SDF.zip` link (404); ZINC web UIs (CAPTCHA);
`cartblanche22.docking.org` async result polling; Diamond and mcule compound pages (Cloudflare).

Stated but **not independently verified**: ZINC22's 230M-purchasable and 37.2-billion tranche
figures; COCONUT's 695,133 count (from the NAR paper, not from the current dump); Enamine and
MolPort per-compound pricing; MolPort PPI Library and RNA Binder Set sizes; XChem per-library
fragment counts other than DSI-poised.
