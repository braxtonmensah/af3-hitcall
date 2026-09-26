# Boltz-2 input schema: metals, affinity, pocket constraints

Verified 2026-09-25 against primary sources only.

Sources used (nothing here rests on blog posts, wrappers, or secondary summaries):

- `jwohlwend/boltz` cloned at commit `b1ebfc46ecf57f5414e0d1a6f9027bbb122c53bc` (2026-05-29), `pyproject.toml` version `2.2.1`.
  - `docs/prediction.md` -> https://github.com/jwohlwend/boltz/blob/main/docs/prediction.md
  - `src/boltz/data/parse/schema.py`, `src/boltz/data/feature/featurizerv2.py`, `src/boltz/data/crop/affinity.py`, `src/boltz/data/module/inferencev2.py`, `src/boltz/data/tokenize/boltz2.py`, `src/boltz/model/models/boltz2.py`, `src/boltz/model/modules/affinity.py`, `src/boltz/model/modules/trunkv2.py`, `src/boltz/data/write/writer.py`, `src/boltz/data/write/pdb.py`, `src/boltz/data/const.py`, `src/boltz/main.py`
- Boltz-2 technical report, bioRxiv doi 10.1101/2025.06.14.659707. bioRxiv itself returns Cloudflare `error code: 1015` to scripted fetches, so the text was obtained from Europe PMC: main text JATS XML `https://www.ebi.ac.uk/europepmc/webservices/rest/PPR1039145/fullTextXML`, and the full preprint-with-appendices PDF from the Europe PMC/PMC supplementary bundle for `PMC12262699` (`NIHPP2025.06.14.659707v1-supplement-1.pdf`, v1 posted June 18 2025). Appendix quotes below are from that PDF (pdftotext, `-layout`), which carries Appendices A-E.
- Boltz CCD molecule store: `https://huggingface.co/boltz-community/boltz-2/resolve/main/mols.tar` (1,855,662,080 bytes), streamed and scanned for member names.
- RCSB chemical component definition for `ZN`: https://files.rcsb.org/ligands/view/ZN.cif
- Maintainer statements in repo issues (author `gcorso` = Gabriele Corso, Boltz-2 co-author, GitHub `author_association: COLLABORATOR`).

Method note: everything below was verified by reading released code, released docs, the paper, and the CCD store. The parser was **not executed** (no boltz install on this machine). Anywhere that matters, it is flagged in "Still unverified".

---

## Decisions this settles

1. **Metal ion syntax.** A metal is an ordinary non-polymer chain: `- ligand: {id: Z1, ccd: ZN}`. `ccd` is verified to resolve: `mols/ZN.pkl` exists in Boltz-2's CCD store, the parser has an explicit single-heavy-atom CCD branch, and the CCD atom name is `ZN`. Use `ccd: ZN`, not `smiles: '[Zn+2]'`. The SMILES form is what users in the issue tracker do and it does place ions, but the CCD form is the one the writer labels correctly for 2-character elements and the only one that gives you a predictable atom name (`ZN`) for constraints.

2. **Affinity with more than one non-polymer: allowed.** The only restriction is **one affinity binder**, not one ligand. `len(affinity_ligands) > 1` raises `"Only one affinity ligand is currently supported!"`; there is no check on the number of ligand chains. A job with 2 Zn chains plus `affinity: binder: L` parses and runs. No workaround needed. The real cost is scientific, not syntactic: the affinity head pools only protein-to-binder and binder-to-binder pairs (`rec_mask = mol_type == 0`, i.e. PROTEIN only), so the metals never enter the affinity readout directly. They act on the score only through the pose and the trunk representation.

3. **128-atom limit counts the binder only.** Both 128-atom checks sit inside `if affinity:` blocks in the per-entity parse loop, and `affinity` is True only for the designated binder chain. Zn atoms, cofactor atoms, and any other ligand's atoms do not count. Separate budget to watch: the affinity crop is capped at `max_tokens=256, max_atoms=2048`, and non-binder non-polymers do consume that.

4. **Metals are never added for you, and there is no Boltz metalloprotein benchmark.** The parsed target contains exactly the chains you declare. The paper states the affinity module "does not explicitly handle such cofactors, including ions, water, or multimeric binding partners". The words metallo-, zinc, di-zinc, and metalloenzyme appear nowhere in the paper or supplement, and the one repo issue asking exactly your question (#321, "Affinity Prediction for Metalloenzyme") has zero replies. So: include the zincs on structural grounds, but do not expect the affinity head to read metal coordination. Whether omitting metals distorts an MBL active site is not answered by any Boltz primary source (see "Still unverified").

5. **Pocket plus affinity interact, and in a way that matters for a screen.** The pocket constraint is passed into the featurizer during the affinity pass too, and it is not a local edit: when any constraint is present, every unlisted pair is labeled `UNSELECTED` instead of `UNSPECIFIED`, so all protein-ligand pair features that the affinity head pools over change. Also, pocket `force` steering is explicitly disabled in the affinity pass (`contact_guidance_update = False`), while it is on by default in the structure pass. Practical rule: use an identical pocket-constraint policy for every compound including positive controls, or the scores are not comparable across the screen.

6. **Direction: LOWER `affinity_pred_value` = STRONGER binding.** It is `log10(IC50)` with IC50 in micromolar, so -3 is about 1 nM and +2 is about 100 uM. `affinity_probability_binary` is a 0-1 probability of being a binder, higher = more likely binder. A Boltz author confirmed in issue #552 that the docs are correct and that the value head must only be used among actives. Calibration: 90% of the regression loss is on intra-assay pairwise differences (`Ltotal = 0.9*Ldif + 0.1*Labs + Lbinary`), the value is trained on pooled Ki/Kd/IC50/EC50 in log-uM, and the paper's reported absolute-error numbers use a molecular-weight-corrected ensemble that the CLI leaves OFF by default (`--affinity_mw_correction` is a flag, default False). Treat the value as a ranking, not a measurement.

7. **Protein-protein affinity does not exist in this model, and out-of-distribution degradation is documented.** You cannot even request it: the binder must be a ligand chain (`"Chain {binder} is not a ligand! Affinity is currently only supported for ligands."`), and a Boltz author says "there is no module trained to predict protein-protein affinity currently in the repo". For unusual targets, the paper's own private-benchmark result is the honest ceiling: average Pearson R 0.39 across 8 blinded hit-to-lead assays with per-target R from 0.165 to 0.634, and centered MAE 1.36 kcal/mol versus 0.86 on their validation set.

---

## Evidence

### Q1. Exact YAML for a metal ion

`docs/prediction.md`, schema block:

```yaml
sequences:
    - ENTITY_TYPE:
        id: CHAIN_ID 
        sequence: SEQUENCE      # only for protein, dna, rna
        smiles: 'SMILES'        # only for ligand, exclusive with ccd
        ccd: CCD                # only for ligand, exclusive with smiles
        msa: MSA_PATH           # only for protein
```

and, under "Sequences and molecules":

> "Ligands (non-polymers): use `ENTITY_TYPE` equals `ligand`, and provide either a `smiles` string or a `ccd` code (but not both)."

There is no separate `ion`, `metal`, or `cofactor` entity type. `src/boltz/data/parse/schema.py` accepts exactly four entity types:

```python
        entity_type = next(iter(item.keys())).lower()
        if entity_type not in {"protein", "dna", "rna", "ligand"}:
            msg = f"Invalid entity type: {entity_type}"
            raise ValueError(msg)
```

Single-atom components are a first-class case in the parser (`parse_ccd_residue`):

```python
    # Check if this is a single heavy atom CCD residue
    if CalcNumHeavyAtoms(ref_mol) == 1:
        # Remove hydrogens
        ref_mol = AllChem.RemoveHs(ref_mol, sanitize=False)
        ...
```

The CCD code resolves. `get_mol` loads `mol_dir / f"{name}.pkl"` from the store downloaded from `MOL_URL = "https://huggingface.co/boltz-community/boltz-2/resolve/main/mols.tar"` (`src/boltz/main.py:37`). Streaming that 1.86 GB tar and scanning member names returned:

```
      1 mols/CA.pkl
      1 mols/CU.pkl
      1 mols/FE.pkl
      1 mols/MG.pkl
      1 mols/MN.pkl
      1 mols/NA.pkl
      1 mols/ZN.pkl
```

So `ccd: ZN` (and MG, MN, FE, CU, CA, NA) is present in the Boltz-2 component store.

Atom name for constraints: the RCSB definition of `ZN` has exactly one atom, `_chem_comp_atom.atom_id ZN`, `charge 2`. Boltz reads atom names off the component (`ref_atom.GetProp("name")`), and constraint lookups for non-polymer chains are by atom name:

```python
def token_spec_to_ids(
    chain_name, residue_index_or_atom_name, chain_to_idx, atom_idx_map, chains
):
    if chains[chain_name].type == const.chain_type_ids["NONPOLYMER"]:
        # Non-polymer chains are indexed by atom name
        _, _, atom_idx = atom_idx_map[(chain_name, 0, residue_index_or_atom_name)]
```

so a metal is addressable as `[Z1, ZN]` in `contacts` / `token1` / `token2`.

**Why CCD beats SMILES for metals.** In Boltz-2 output files the element symbol is re-derived from the *atom name*, not from the stored atomic number (`src/boltz/data/write/pdb.py`, same logic in `mmcif.py`):

```python
                if boltz2:
                    atom_name = str(atom["name"])
                    atom_key = re.sub(r"\d", "", atom_name)
                    if atom_key in const.ambiguous_atoms:
                        if isinstance(const.ambiguous_atoms[atom_key], str):
                            element = const.ambiguous_atoms[atom_key]
                        elif res_name in const.ambiguous_atoms[atom_key]:
                            element = const.ambiguous_atoms[atom_key][res_name]
                        else:
                            element = const.ambiguous_atoms[atom_key]["*"]
                    else:
                        element = atom_key[0]
```

Evaluating `const.ambiguous_atoms` for the metals of interest:

```
ZN -> 'ZN'                                   (unconditional, so ZN is safe either way)
MG -> 'MG'      MN -> 'MN'
CA -> {'*': 'C', 'CA': 'CA', 'OEX': 'CA', ...}
CU -> {'*': 'C', 'CU': 'CU', ...}   NA -> {'*': 'N', 'NA': 'NA', ...}
```

For a SMILES ligand the residue name is `LIG<n>`, so `CA`/`CU`/`NA` fall through to `'*'` and are written as C, C, N. With `ccd: CA` the residue name is `CA` and the element is correct. This is the user-reported bug in issue #458 ("Calcium ion reported as a Carbon in the generated pdb file", https://github.com/jwohlwend/boltz/issues/458), still open upstream. Zinc happens to be immune, but use the CCD form anyway so the rule holds if you add Mg/Mn/Ca/Fe targets later.

One more SMILES-path hazard, specific to the *binder*: when affinity is requested the binder SMILES is rewritten before use.

```python
        elif (entity_type == "ligand") and ("smiles" in items[0][entity_type]):
            seq = items[0][entity_type]["smiles"]

            if affinity:
                seq = standardize(seq)
```

`standardize` runs ChEMBL structure-pipeline `exclude_flag` + `LargestFragmentChooser` + `standardize_mol`, and raises `ValueError("Molecule is excluded")` on exclusion. From `chembl_structure_pipeline/exclude_flag.py`:

> "Rules to exclude structures. - Metallic or non metallic with more than 7 boron atoms will be excluded due to problems when depicting borane compounds."

with `METAL_LIST` containing Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Ga, Zr, Mo, Ru, Pd, Cd, Sn, Pt, Au, Hg, Ge, Sb and others (the source comment notes "Zn not in the list as we have some Zn containing compounds in ChEMBL"). Consequences for your controls: a benzoxaborole (1 boron) passes, a hydroxamic acid passes, but any organometallic *binder* would be rejected outright, and every binder is silently largest-fragment-selected and ChEMBL-normalized, so salts and counterions in the library SMILES are dropped and the scored species may not be the string you supplied. `standardize` is not applied to non-binder ligands, which is why `smiles: '[Ca+2]'` co-folds at all.

### Q2. Affinity with more than one non-polymer entity (the critical one)

The whole affinity validation block in `parse_boltz_schema` is:

```python
    # Check if any affinity ligand is present
    affinity_ligands = set()
    properties = schema.get("properties", [])
    if properties and not boltz_2:
        msg = "Affinity prediction is only supported for Boltz2!"
        raise ValueError(msg)

    for prop in properties:
        prop_type = next(iter(prop.keys())).lower()
        if prop_type == "affinity":
            binder = prop["affinity"]["binder"]
            if not isinstance(binder, str):
                # TODO: support multi residue ligands and ccd's
                msg = "Binder must be a single chain."
                raise ValueError(msg)

            if binder not in chain_name_to_entity_type:
                msg = f"Could not find binder with name {binder} in the input!"
                raise ValueError(msg)

            if chain_name_to_entity_type[binder] != "ligand":
                msg = (
                    f"Chain {binder} is not a ligand! "
                    "Affinity is currently only supported for ligands."
                )
                raise ValueError(msg)

            affinity_ligands.add(binder)

    # Check only one affinity ligand is present
    if len(affinity_ligands) > 1:
        msg = "Only one affinity ligand is currently supported!"
        raise ValueError(msg)
```

Read it carefully: the constraint is on the number of **affinity properties / binders**, not on the number of ligand chains. Nothing counts non-polymer entities. The remaining per-entity guards are:

```python
        if len(ids) == 1:
            affinity = ids[0] in affinity_ligands
        elif (len(ids) > 1) and any(x in affinity_ligands for x in ids):
            msg = "Cannot compute affinity for a ligand that has multiple copies!"
            raise ValueError(msg)
        else:
            affinity = False
```

and, later, `"Cannot compute affinity for multi residue ligands!"` (multi-CCD ligand chain) and, at record assembly, `"Cannot compute affinity for multiple ligands!"` which fires only if two chains carry `affinity=True`:

```python
        # Add affinity info
        if chain.affinity and affinity_info is not None:
            msg = "Cannot compute affinity for multiple ligands!"
            raise ValueError(msg)
```

So the two guards you could trip by accident are (a) giving the *binder* a list id, and (b) declaring your binder's SMILES twice, since entities are grouped by `(entity_type, seq)`:

```python
            if "smiles" in item[entity_type]:
                seq = str(item[entity_type]["smiles"])
            else:
                seq = str(item[entity_type]["ccd"])

        # Group items by entity
        items_to_group.setdefault((entity_type, seq), []).append(item)
```

Two `ccd: ZN` entries with different ids collapse into one entity with ids `[Z1, Z2]`, which is fine because that entity is not the binder. Writing `- ligand: {id: [Z1, Z2], ccd: ZN}` is exactly equivalent.

Corroboration from docs (`docs/prediction.md`, "Properties (affinity)"):

> "`properties` is an optional field that allows you to specify whether you want to compute the affinity. If enabled, you must also provide the chain_id corresponding to the small molecule against which the affinity will be computed. Only one single small molecule can be specified for affinity computation."

"Only one single small molecule can be specified **for affinity computation**" is about the binder, and the code confirms that reading.

**What the metals do and do not reach.** The affinity readout masks by molecular type. `src/boltz/data/const.py`:

```python
chain_types = [
    "PROTEIN",
    "DNA",
    "RNA",
    "NONPOLYMER",
]
chain_type_ids = {chain: i for i, chain in enumerate(chain_types)}
```

so PROTEIN = 0, NONPOLYMER = 3. In `src/boltz/model/models/boltz2.py`:

```python
        if self.affinity_prediction:
            pad_token_mask = feats["token_pad_mask"][0]
            rec_mask = feats["mol_type"][0] == 0
            rec_mask = rec_mask * pad_token_mask
            lig_mask = feats["affinity_token_mask"][0].to(torch.bool)
            lig_mask = lig_mask * pad_token_mask
            cross_pair_mask = (
                lig_mask[:, None] * rec_mask[None, :]
                + rec_mask[:, None] * lig_mask[None, :]
                + lig_mask[:, None] * lig_mask[None, :]
            )
            z_affinity = z * cross_pair_mask[None, :, :, None]
```

and `affinity_token_mask` is set for the binder chain only (`src/boltz/data/tokenize/boltz2.py`):

```python
        affinity_mask = (affinity is not None) and (
            int(chain["asym_id"]) == int(affinity.chain_id)
        )
```

The same masking is repeated inside the affinity module's PairFormer and in its mean pooling (`src/boltz/model/modules/affinity.py`). The paper's Algorithm 1 says the same thing:

> `z += PairFormerModule(z, pair mask=protein ligand mask + intra ligand mask)`
> `g = MeanPooling(z, mask = protein ligand mask + intra ligand mask * (1 - Id))`

and Appendix B.5.1:

> "At its core, the affinity architecture comprises a Pairformer model designed to process the interaction pair representations, masking out intra-protein interactions to focus exclusively on protein-ligand interface details."

Zn tokens are neither `mol_type == 0` nor in `affinity_token_mask`, so Zn-to-ligand and Zn-to-protein pair features are zeroed before the affinity heads see them. The zincs still influence the score indirectly, via the trunk representation of the protein and ligand tokens and via the coordinates the module conditions on (`distogram` over the cropped token set, then `z += PairwiseConditioner(...)`). They are retained in the affinity crop: the cropper walks tokens by distance to the binder and takes whole chains when `len(chain_tokens) <= neighborhood_size` (10), and all non-polymer tokens are exempt from the 200-protein-token budget:

```python
        ligand_ids = set(
            valid_tokens[
                valid_tokens["mol_type"] == const.chain_type_ids["NONPOLYMER"]
            ]["token_idx"]
        )
```

Matching training-side statement, Appendix C.2.2 Algorithm 3: `cropped tokens <- tokens[mol type = ligand]`, `max tokens = 256, max protein tokens = 200, neighborhood size = 10`.

**No workaround is required.** If you ever want a metal-aware *comparison* rather than a metal-aware score, the only lever inside Boltz-2 is the structure side (pose quality, pocket/contact constraints, ipTM, `ligand_iptm`), because the value head cannot see the metal contacts by construction.

### Q3. What the 128-atom limit counts

SMILES branch (`schema.py`), note the enclosing `if affinity:` and the `mol_no_h` subject:

```python
            mol_no_h = AllChem.RemoveHs(mol, sanitize=False)

            if affinity:
                # Add error and warning messaging when computing affinity with ligands too large
                if mol_no_h.GetNumAtoms() > 128:
                    msg = f"The ligand for affinity is too large, ligands with more than 128 atoms are not supported in the affinity prediction module"
                    raise ValueError(msg)
                elif mol_no_h.GetNumAtoms() > 56:
                    print("WARNING: the ligand used for affinity calculation is larger than 56 heavy-atoms, "
                          "which was the maximum during training, therefore the affinity output might be inaccurate.")

            affinity_mw = AllChem.Descriptors.MolWt(mol_no_h) if affinity else None
```

CCD branch, same limit but applied to the CCD reference mol as stored (`ref_mol.GetNumAtoms()`, i.e. including whatever hydrogens the component carries), and inside the per-residue loop of that one entity:

```python
                if affinity:
                    affinity_mw = AllChem.Descriptors.MolWt(ref_mol)

                    # Add error and warning messaging when computing affinity with ligands too large
                    if ref_mol.GetNumAtoms() > 128:
                        msg = f"The ligand for affinity is too large, ligands with more than 128 atoms are not " \
                              f"supported in the affinity prediction module"
                        raise ValueError(msg)
```

`affinity` is a per-entity boolean derived from `ids[0] in affinity_ligands`, so for every non-binder chain (your zincs) both checks are skipped entirely. The docs phrase the same limit as a property of the binder:

> "It must be a ligand chain (not a protein, DNA or RNA) and has to be at most 128 atoms counting heavy atoms and hydrogens kept by `RDKit RemoveHs`, however, we do not recommend running the affinity module with ligands significantly larger than 56 atoms (counted as above, limit set during training)."

Two filtering consequences for your library gate:

- Filter on the **binder** count, computed the same way the code does it: `RemoveHs(AddHs(MolFromSmiles(standardize(smi))), sanitize=False).GetNumAtoms()`. Note `standardize` comes first for affinity jobs, so a salt form shrinks before counting.
- The operative quality threshold is 56, not 128. Above 56 you get a warning and an out-of-training-range prediction, not an error.
- Separately, the affinity crop budget is shared: `self.cropper.crop(tokenized, max_tokens=256, max_atoms=2048)` in `inferencev2.py`. Zn tokens are cheap (1 atom each) but any large cofactor you add competes with pocket residues for those 256 tokens / 2048 atoms.

### Q4. Metals that are not given, and what the paper says about metalloproteins

Nothing is auto-added. `parse_boltz_schema` builds chains exclusively from `schema["sequences"]` (plus `extra_mols` for SMILES ligands you declared); no code path in the parser, tokenizer, or featurizer injects an undeclared non-polymer entity. Metal ions are not in the training-time exclusion set either (`const.ligand_exclusion`, the crystallization-aid list applied by `data/filter/static/ligand.py`, contains e.g. `CL`, `EDO`, `DMS` but not `ZN`), so Boltz-2's structure training did see zinc sites as explicit entities. Appendix A.1.5: structures "containing small-molecules or ions" are added to the validation set under cluster constraints.

The one direct statement, Limitations / "Accurate structures for affinity predictions":

> "Boltz-2 relies on predicted 3D protein–ligand structures and reliable trunk features as input to the affinity module. If the model fails to identify the correct pocket or inaccurately reconstructs the binding interface or conformational state of the protein, downstream affinity predictions are unlikely to be reliable. This is particularly relevant in biological contexts where cofactors are essential for binding, given that in its current form, the affinity module does not explicitly handle such cofactors, including ions, water, or multimeric binding partners. Finally, an insufficiently large affinity crop size could be limiting if important long-range interactions are truncated or if the crop does not include the corresponding pocket for each binder, e.g., in the case of both orthosteric and allosteric modulators."

The docs say the same for the target side:

> "At this point, Boltz only supports the computation of affinity of small molecules to protein targets, if ran with an RNA/DNA/co-factor target, the code will not crash but the output will be unreliable."

That sentence is mechanically explained by `rec_mask = mol_type == 0`: if the thing the ligand is really binding to is not protein, it contributes nothing to the pooled affinity representation.

Absent from the primary sources: any metalloprotein or metalloenzyme benchmark. Case-insensitive search of the main text and the appendix PDF for "metallo", "zinc", "hydroxamic", "boronic" returns zero hits. The only mentions of ions are the limitation above and the dataset-assembly line. The single repo issue asking your exact question, https://github.com/jwohlwend/boltz/issues/321 ("Affinity Prediction for Metalloenzyme", "I noticed that the affinity module does not handle cofactors. Does this mean that affinity prediction is only considers the interaction between the ligand and the protein... does that mean predictions for metalloenzymes may be unreliable"), was closed with **no replies** (verified via the GitHub API: zero comments).

So the defensible position for the run: declare the zincs so the structure pass builds a holo-like active site, and do not expect `affinity_pred_value` to reward metal chelation. Whether the *pose* degrades without metals is not settled by any Boltz source (see "Still unverified").

### Q5. Pocket constraint plus affinity request

Pocket syntax and ranges, `docs/prediction.md`:

> "The `pocket` constraint specifies the residues associated with binding interaction, where `binder` refers to the chain binding to the pocket (which can be a molecule, protein, DNA or RNA) and `contacts` is the list of chain and residue indices (starting from 1, or atom names if the chain is a molecule) that form the binding site for the `binder`. `max_distance` specifies the maximum distance (in Angstrom, supported between 4A and 20A with 6A as default) between any atom in the `binder` and any atom in each of the `contacts` elements. If `force` is set to true, a potential will be used to enforce the pocket constraint."

Multiple pocket constraints are allowed in Boltz-2 (the one-pocket restriction is Boltz-1 only):

```python
            if len(pocket_constraints) > 0 and not boltz_2:
                msg = f"Only one pocket binders is supported in Boltz-1!"
                raise ValueError(msg)
```

The constraint is live during the affinity pass. `src/boltz/data/module/inferencev2.py` uses one featurizer call for both passes, and passes the constraints through with `compute_affinity=self.affinity`:

```python
            features = self.featurizer.process(
                tokenized,
                ...
                inference_pocket_constraints=pocket_constraints,
                inference_contact_constraints=contact_constraints,
                compute_constraint_features=True,
                override_method=self.override_method,
                compute_affinity=self.affinity,
            )
```

and `main.py` gives the affinity data module `constraints_dir=processed.constraints_dir`. The conditioning enters the trunk (`boltz2.py`): `z_init = z_init + self.contact_conditioning(feats)`, and the affinity module consumes the trunk's `z`. So the pocket constraint is not merely a pose bias, it changes the representation the affinity heads read.

The non-local part, `featurizerv2.py`:

```python
    # Pocket conditioned feature
    contact_conditioning = (
        np.zeros((len(token_data), len(token_data)))
        + const.contact_conditioning_info["UNSELECTED"]
    )
```

```python
    if np.all(contact_conditioning == const.contact_conditioning_info["UNSELECTED"]):
        contact_conditioning = (
            contact_conditioning
            - const.contact_conditioning_info["UNSELECTED"]
            + const.contact_conditioning_info["UNSPECIFIED"]
        )
```

With no constraints, every pair is `UNSPECIFIED`. With one pocket constraint, the named pairs become `BINDER>POCKET` / `POCKET>BINDER` and **every other pair in the complex becomes `UNSELECTED`**. The paper's Appendix B.3.3 names these categories explicitly:

> "The contact type is selected among: no restraint was specified, some were specified but this was not selected, this pair has a pocket-to-binder relationship, this pair has a binder-to-pocket relationship, this pair has a contact relationship (takes precedence). The encoding of the distance d, constrained to be 4A <= d <= 20A, is encoded as a concatenation of the normalized distance (d - 4)/16 and its Fourier embedding..."

Confirmed in `trunkv2.py` with `cutoff_min=4.0, cutoff_max=20.0`: `contact_threshold_normalized = (contact_threshold - self.cutoff_min) / (self.cutoff_max - self.cutoff_min)`. Nothing validates the range at parse time, so `max_distance: 3` silently produces a negative normalized distance outside anything seen in training. Stay in 4-20.

Steering differs between passes. `BoltzSteeringParams` defaults to `contact_guidance_update: bool = True`, and the structure pass only overrides `fk_steering` / `physical_guidance_update` from `--use_potentials`. The affinity pass turns contact steering off:

```python
        steering_args = BoltzSteeringParams()
        steering_args.fk_steering = False
        steering_args.physical_guidance_update = False
        steering_args.contact_guidance_update = False
```

Two more affinity-pass facts worth knowing before you interpret scores: the affinity module's input single representation is built from a single-sequence profile (`process_msa_features(..., max_seqs_batch=1, max_seqs=1, ..., affinity=True)` -> `profile_affinity`, consumed by `input_embedder(feats, affinity=True)`), and templates are replaced by dummies when `compute_affinity` is set (`if data.templates and not compute_affinity:` ... `else: load_dummy_templates_features(...)`). The trunk itself still uses your full MSA.

On training-time pocket conditioning for the affinity heads: Appendix C.2 lists the five affinity-training components (pocket pre-processing, affinity cropper, feature pre-processing, sampler, losses) and C.2.3 says trunk features were pre-computed by running "Boltz-2 structure model with 5 recycling iterations, 200 diffusion steps" with no mention of user constraints. That is suggestive that the affinity heads were trained on `UNSPECIFIED`-conditioned trunk features, but the paper never states it and the Boltz-2 training code is not released ("Coming soon: updated training code for Boltz-2!"). Listed as unverified below.

### Q6. Output fields, units, direction, calibration

`docs/prediction.md`, output section, verbatim:

> ```
> {
>     "affinity_pred_value": 0.8367,             # Predicted binding affinity from the ensemble model
>     "affinity_probability_binary": 0.8425,     # Predicted binding likelihood from the ensemble model
>     "affinity_pred_value1": 0.8225,            # Predicted binding affinity from the first model of the ensemble
>     "affinity_probability_binary1": 0.0,       # Predicted binding likelihood from the first model in the ensemble
>     "affinity_pred_value2": 0.8225,            # Predicted binding affinity from the second model of the ensemble
>     "affinity_probability_binary2": 0.8402,    # Predicted binding likelihood from the second model in the ensemble
> }
> ```

> "There are two main predictions in the affinity output: `affinity_pred_value` and `affinity_probability_binary`. They are trained on largely different datasets, with different supervisions, and should be used in different contexts."

> "The `affinity_probability_binary` field should be used to detect binders from decoys, for example in a hit-discovery stage. It's value ranges from 0 to 1 and represents the predicted probability that the ligand is a binder."

> "The `affinity_pred_value` aims to measure the specific affinity of different binders and how this changes with small modifications of the molecule (*note that this implies that it should only be used when comparing different active molecules, not inactives*). This should be used in ligand optimization stages such as hit-to-lead and lead-optimization. It reports a binding affinity value as `log10(IC50)`, derived from an `IC50` measured in `μM`. Lower values indicate stronger predicted binding, for instance:
> - IC50 of $10^{-9}$ M $\longrightarrow$ our model outputs $-3$ (strong binder)
> - IC50 of $10^{-6}$ M $\longrightarrow$ our model outputs $0$ (moderate binder)
> - IC50 of $10^{-4}$ M $\longrightarrow$ our model outputs $2$ (weak binder / decoy)"

> "You can convert the model's output to pIC50 in `kcal/mol` by using `y --> (6 - y) * 1.364` where `y` is the model's prediction."

The direction question was raised upstream and answered by a Boltz-2 author. Issue #552 "Meaning of affinity_pred_value" (https://github.com/jwohlwend/boltz/issues/552); the reporter argued the docs were wrong, and `@gcorso` (COLLABORATOR) replied:

> "Hi @morgannprice , no the documentation is correct, but the affinity_pred_value should only be used when comparing different binders (e.g. in a hit / lead optimization setting) not when comparing different hit from decoys. So in your setting, I would use affinity_pred_value if trying to understand selectivity of a particular binder to similar proteins, affinity_probability_binary if trying to screen a ligand against many different proteins to see which could bind to it."

So for a hit-discovery screen, `affinity_probability_binary` (higher = better) is the intended ranking statistic, and `affinity_pred_value` (lower = stronger) is for ordering within a set of actives.

Writer confirms the JSON carries raw model outputs, no unit conversion (`BoltzAffinityWriter.write_on_batch_end` writes `pred_affinity_value.item()` and `pred_affinity_probability.item()` directly).

Calibration, from the paper. Main text, "Affinity module":

> "During training, we supervise the affinity value head using a mixture of related, but non-identical biochemical quantities (including Ki, Kd, and IC50) all converted to the logarithmic scale using µM as standardized unit. While some of these measures are related through the Cheng–Prusoff equation, they arise from different experimental contexts. As such, the predicted value should be viewed as a general measure of binding strength that supports ranking and can be approximately interpreted as an IC50-like value."

Appendix A hit-to-lead curation: "Convert all affinity values to logarithmic scale with 1 µM as the reference unit."

Appendix C.2.5, the loss that sets what "calibrated" means here:

> "To address this, we introduce a supervision strategy based on pairwise differences of affinity values within the same assay. This difference-based formulation implicitly cancels out assay-specific confounding factors, such as those corrected by the Cheng–Prusoff equation."

> "Overall loss. The final training objective is a weighted sum of the three components: Ltotal = 0.9 * Ldif + 0.1 * Labs + Lbinary"

Appendix B.5.2, the ensemble and the MW correction used for the paper's numbers:

> "For affinity regression, we apply a calibrated ensembling strategy. We first compute the mean predicted affinity between models and then apply a molecular weight correction of the form y^ = C0 * (y1 + y2) + C1 * MWbinder + C2, where y1 and y2 are the predictions of the two models, C0, C1, and C2 are fitted in the holdout validation set and MWbinder is the molecular weight of the binding small molecule."

The shipped implementation (`boltz2.py`) uses `MW**0.3`, not MW, and is gated off by default:

```python
                    if self.affinity_mw_correction:
                        model_coef = 1.03525938
                        mw_coef = -0.59992683
                        bias = 2.83288489
                        mw = feats["affinity_mw"][0] ** 0.3
                        dict_out_affinity_ensemble["affinity_pred_value"] = (
                            model_coef
                            * dict_out_affinity_ensemble["affinity_pred_value"]
                            + mw_coef * mw
                            + bias
                        )
```

`--affinity_mw_correction` is a click flag, so default False, and `main.py` passes it straight through. Note the sign: with the correction on, heavier binders are pushed toward lower (stronger) values by about 0.55 log units going from 300 to 500 Da. Decide once, per screen, and record it, because turning it on or off changes every cross-chemotype comparison. Their own evaluation also reports "centered" errors where per-assay predictions are shifted to the ground-truth mean, "to allow for a fair comparison with methods that only predict relative affinities" (Appendix D.2.2), which is a direct statement that the absolute offset is not the trustworthy part.

Reference settings for the affinity pass, from `main.py` (relevant if you tune GPU spend): `recycling_steps: 5`, `--sampling_steps_affinity` default 200, `--diffusion_samples_affinity` default 5, `max_parallel_samples: 1`, and the affinity checkpoint `boltz2_aff.ckpt` is a separate download from `boltz2_conf.ckpt`.

### Q7. Protein-protein interfaces, and targets unlike the training set

Hard block in code, already quoted: `"Chain {binder} is not a ligand! Affinity is currently only supported for ligands."` A protein, DNA, or RNA chain cannot be an affinity binder. Docs: "Boltz only supports the computation of affinity of small molecules to protein targets".

Maintainer statement, issue #359 "protein-protein interaction interface scoring" (https://github.com/jwohlwend/boltz/issues/359), `@gcorso` (COLLABORATOR):

> "Unfortunately, we there is no module trained to predict protein-protein affinity currently in the repo, but we are working on it!"

And for peptides, issue #151 (Boltz-1 era), same author: "Boltz-1 doesn't currently support binding affinity predictions although this is definitely something that we are interested in adding for the future. In the meantime, users have reported good correlations between Boltz-1's confidence_score or iptm and binding affinity".

Documented out-of-distribution behavior, Limitations / "Understanding the range of applicability of the affinity module":

> "Despite the progress on affinity predictions, we notice in Figures 12-14 that the performance varies strongly between assays. Further work is needed to determine the source of this variance in performance, whether it stems from, e.g., inaccuracies in predicted structures, limited generalization to distinct protein families, or insufficient robustness to out-of-distribution small molecules."

Appendix E.2.2, private blinded benchmark (the closest thing to a novel-target estimate):

> "As displayed in figure 14, the model achieves respectable performance on these assays, achieving an average Pearson R = 0.39, only slightly worse than in the validation set (R = 0.42). However, the centered MAE = 1.36kcal/mol is significantly worse compared to the validation set (MAE = 0.86kcal/mol). In addition, the performance varies noticably between targets, ranging from Person R = 0.165 to R = 0.634 and centered MAE from MAE = 0.855kcal/mol to MAE = 1.734kcal/mol, suggesting that performance in practice will strongly depend on the project at hand."

One encouraging data point on chemical novelty (Appendix, Figure 10 caption): binning FEP+ test compounds by maximum Tanimoto similarity to the affinity training set, "We observe no strong dependence between compound similarity and predictive performance." That is about ligand novelty, not target novelty.

For hit discovery specifically, the reported strength is enrichment, not absolute accuracy: MF-PCBA, "nearly doubling the average precision and achieving an enrichment factor of 18.4 at a 0.5% threshold".

---

## Copy-pasteable example: two-metal nuclease, one scored ligand

Residue indices are 1-based positions **in the sequence string you supply**, not UniProt or PDB numbering (`schema.py`: `return chain_to_idx[chain_name], residue_index_or_atom_name - 1`). Non-polymer contacts use CCD atom names, so a zinc is `[Z1, ZN]`.

```yaml
version: 1

sequences:
  - protein:
      id: A
      sequence: MIKDFDPSEF...                      # full target sequence, 1-based indexing below
      msa: /workspace/screen/msa/P75497.a3m

  # Active-site di-zinc. One entity, two chain copies. CCD form, not SMILES.
  - ligand:
      id: [Z1, Z2]
      ccd: ZN

  # The scored compound. Exactly one affinity binder in the whole file.
  - ligand:
      id: L
      smiles: 'CCCCC1C(=O)N(c2ccccc2)N(c2ccccc2)C1=O'

properties:
  - affinity:
      binder: L

constraints:
  # 1. Steer the compound into the di-zinc site, including the metals themselves
  #    as contacts so a chelator is asked to sit near both ions.
  - pocket:
      binder: L
      contacts: [[A, 25], [A, 51], [A, 208], [Z1, ZN], [Z2, ZN]]
      max_distance: 6          # default is 6; supported range is 4 to 20

  # 2. Put each zinc on its own coordinating residues. Use >= 4 A: the
  #    conditioning encodes (d - 4) / 16, so smaller values are out of range.
  - pocket:
      binder: Z1
      contacts: [[A, 25], [A, 27], [A, 92]]        # replace with the real His/Asp/Cys set
      max_distance: 4
  - pocket:
      binder: Z2
      contacts: [[A, 51], [A, 208], [A, 212]]      # replace with the real His/Asp/Cys set
      max_distance: 4
```

Run:

```
boltz predict jobs/ --out_dir out --use_potentials --diffusion_samples 5 --output_format mmcif
```

Notes on that command and file, all code-verified above:

- Do not pass `--use_msa_server` when `msa:` is a real path; the path form is the documented way to use a precomputed a3m, and `msa: empty` would force single-sequence mode.
- `--affinity_mw_correction` is off unless you pass it. Pick one setting for the entire screen, controls included.
- Constraint policy must be identical for every compound in the screen. Adding a pocket constraint relabels every pair in the complex from `UNSPECIFIED` to `UNSELECTED`, which changes the affinity module's inputs, so a control run without constraints is not comparable to a screen run with them.
- If you want a per-compound metal-contact restraint instead of a pocket one, `contact` constraints take `[CHAIN_ID, RES_IDX/ATOM_NAME]` pairs, but naming an atom inside a SMILES ligand requires reproducing Boltz's synthetic names: it runs `AddHs`, then `CanonicalRankAtoms`, then sets `name = atom.GetSymbol().upper() + str(can_idx + 1)`, and for affinity binders the SMILES is `standardize`d first. Easier to use the pocket form above, or give the control compounds as CCD codes where they exist.
- Expected outputs per job: `out/predictions/<job>/<job>_model_0.cif`, `confidence_<job>_model_0.json`, and `affinity_<job>.json`. The structure pass additionally writes `pre_affinity_<job>.npz` for any job with an `affinity` property (`writer.py`: `if self.boltz2 and record.affinity and idx_to_rank[model_idx] == 0`), and the affinity pass loads that file as its input structure and crops around the binder in it. If `pre_affinity_<job>.npz` is missing, the affinity pass had nothing to score.
- Sanity gate before spending GPU time on the full library: confirm `ligand_iptm` in the confidence JSON is non-zero and that the zincs land in the active site in the CIF. The affinity number is meaningless if the pose is wrong, which is exactly what the paper's limitation section says.

## Still unverified

Flagged deliberately. Each of these is a real gap, not a hedge.

1. **Not executed.** Every schema claim comes from reading `parse_boltz_schema` end to end at commit `b1ebfc46`, not from running `boltz predict`. There is no boltz install on this machine (rdkit 2026.03.6 is present, boltz is not). The first job you launch should be a single-compound smoke test of the exact YAML above, and you should confirm it emits `affinity_<job>.json` with a Zn present in the CIF before you launch the library.

2. **Whether the affinity heads were trained with pocket conditioning.** Appendix C.2 never says. Boltz-2 training code is not released. My reading of C.2.3 is that trunk features were pre-computed from unconstrained predictions, which would make a user-supplied pocket constraint an input-distribution shift for the value head, but that is inference from silence, not a documented fact. The mitigation (identical constraint policy across the whole screen) holds either way.

3. **Whether omitting the di-zinc distorts an MBL-fold active site.** No Boltz primary source addresses it. The paper contains no metalloprotein benchmark and no zinc-site geometry evaluation. The relevant external literature I found but did not verify in depth is "Predicting metal-protein interactions using cofolding methods: Status quo" (bioRxiv 2024.05.28.596236), which evaluates metal *placement* by co-folding methods and predates Boltz-2. If this matters to the gate, the cheap internal experiment is to fold the target with and without the zincs and compare active-site geometry and `ligand_iptm` for two or three known binders.

4. **Whether `mols/ZN.pkl` deserializes to a single-atom mol named `ZN` with charge +2.** The tar member exists (verified by streaming the 1.86 GB archive), the RCSB component has one atom named `ZN` with formal charge 2, and the parser reads `GetProp("name")`, but I did not extract and unpickle the file. If `[Z1, ZN]` in `contacts` raises a `KeyError` on `atom_idx_map`, that is the reason, and the fix is to print the atom name from the pickle.

5. **Numerical effect of the metals on the affinity score.** Mechanically the metals are excluded from the affinity pooling masks, so the only channels left are the pose and the trunk. How much score actually moves when you add or remove the zincs is an empirical question this document cannot answer. It is a two-run experiment on your positive controls.

6. **Whether `affinity_probability_binary` is calibrated in the probabilistic sense.** The docs call it "the predicted probability that the ligand is a binder", and it is a sigmoid over ensemble-averaged logits, but the paper evaluates it with AP, AUROC, and enrichment factor, never with a calibration curve or Brier score. Treat it as a ranking score, not a probability, and set your threshold from your own control distribution.

7. **CCD atom-count asymmetry.** For a CCD binder the 128-atom test is `ref_mol.GetNumAtoms()` on the stored component, which generally includes all hydrogens; for a SMILES binder it is `RemoveHs(...)`. That makes the effective limit stricter for CCD binders than for the SMILES form of the same molecule. I read both branches but did not measure the difference on a real component.

8. **Version drift.** All of this is `boltz` 2.2.1 at commit `b1ebfc46` (2026-05-29). The 128/56 thresholds, the MW-correction coefficients, the crop sizes (256 tokens / 2048 atoms / 200 protein tokens), and the `contact_guidance_update` defaults are code constants that have changed before and can change again. Pin the version in the run environment and re-check these constants if you upgrade.
