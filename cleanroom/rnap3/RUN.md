# RNAP3: how to run it, both paths ready

Pre-registration: `PREREG_RNAP3.md` (committed d605b06, before any prediction).
Scoring is automated: `python score_rnap3.py <model.cif|model.pdb>`.

## Path A: RunPod, Boltz-2, commercially unrestricted (blocked on balance)

The pod create was attempted and returned HTTP 402, account balance too low. Add funds and it runs.

- **Cost: about $4 to $8.** H200 (141 GB) at $3.59/hr, one to two hours. 2,817 residues needs
  headroom above 80 GB, which is why not the cheaper A100 at $1.19/hr.
- Job file: `rnap3_mg354_rpoB_rpoC.yaml`
- On the pod: `pip install boltz -U && boltz predict rnap3_mg354_rpoB_rpoC.yaml --use_msa_server --diffusion_samples 5 --out_dir out`
- Keeps the result MIT-licensed and outside IU policy UA-24. This is the path `COSTS.md` recommends.

## Path B: AlphaFold Server, free, today (needs your browser)

- Go to alphafoldserver.com, sign in, then **Upload JSON** and pick
  `cleanroom/rnap3/afserver_rnap3.json`.
- Same format as the RNase J job that produced TETRA, so it is known to work.
- **Free.** Output is non-commercial and barred from ligand/docking use, which is fine for answering
  the scientific question and not fine for building a commercial asset later.
- 2,817 residues is within the server's limit.

## Path C: Quartz, free, with the UA-24 reading recorded in IP_RECORD.md

Needs the RT Project click at `projects.rt.iu.edu` (PI `lamhuber`, "HPC for Students"), still
outstanding. This is the path the virtual screen took, relying on UA-24's exclusion for resources
routinely made available to all students; the reasoning and its open question are in `IP_RECORD.md`
and `COSTS.md`. For RNAP3 specifically the IP question barely arises, because the output is a
structure of a natural complex and is not patentable subject matter either way.

## What the answer looks like

`score_rnap3.py` reads the model and prints:
- **Control first:** fraction of the 23 RpoB-RpoC crosslinks within 30 A. Below 0.7 and the MG354
  numbers are not interpreted, per the pre-registration.
- **Primary:** how many of the 5 MG354 links are within 30 A, against a random-lysine null.
- 4 or 5 of 5 supports "MG354 binds the assembled core". 0 or 1 refutes it.
