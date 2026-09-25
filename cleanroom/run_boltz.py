"""Clean-room rebuild of the RNase J : MG423 complex with Boltz-2 (MIT licence, commercial use allowed).

Why: AlphaFold Server output is non-commercial only and explicitly bars ligand-binding/docking use, so
every AF3 file in this repo is unusable for any commercial route. Boltz-2 (MIT) + CC0 crosslink data +
CC-BY UniProt sequences give an asset with no such restriction.

Inputs used and their licences (all commercial-safe):
  sequences  UniProt P75497 / P75174 / P47385 / P47662        CC-BY 4.0
  crosslinks PRIDE PXD017711 + PXD017695                      CC0 (public domain)
  model      Boltz-2 code + weights                           MIT
NOT used: any AlphaFold Server output, any file from the Todor Zenodo archive.

Run on rented or owned GPU only. Do NOT run on IU hardware (Big Red 200, Quartz): IU policy UA-24
claims patentable IP created with significant use of university resources.

Usage (on a GPU box):
    pip install boltz -U
    python run_boltz.py --write-only      # emit YAMLs locally, no GPU needed
    boltz predict cleanroom/yaml --use_msa_server --diffusion_samples 5 --out_dir cleanroom/out
"""
import argparse
import json
import os

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ACC = {"rnasej_mpn": "P75497", "partner_mpn": "P75174", "rnasej_mg": "P47385", "partner_mg": "P47662",
       "decoy_ptsi_mpn": "P75168"}
# jobs: name -> [(accession key, copies), ...]   mirrors PREREG_AFJ so results are directly comparable
JOBS = {
    "cr_rnasej_mpn_2x2": [("rnasej_mpn", 2), ("partner_mpn", 2)],
    "cr_rnasej_mg_2x2": [("rnasej_mg", 2), ("partner_mg", 2)],
    "cr_rnasej_mpn_1x1": [("rnasej_mpn", 1), ("partner_mpn", 1)],
    "cr_rnasej_mpn_decoy_2x2": [("rnasej_mpn", 2), ("decoy_ptsi_mpn", 2)],
}


def seq(acc):
    t = requests.get(f"https://rest.uniprot.org/uniprotkb/{acc}.fasta", timeout=60).text
    return t.split("\n", 1)[1].replace("\n", "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-only", action="store_true")
    ap.parse_args()
    seqs = {k: seq(v) for k, v in ACC.items()}
    ydir = os.path.join(HERE, "yaml")
    os.makedirs(ydir, exist_ok=True)
    letters = "ABCDEFGH"
    for job, spec in JOBS.items():
        lines = ["version: 1", "sequences:"]
        i = 0
        for key, n in spec:
            for _ in range(n):
                lines += [f"  - protein:", f"      id: {letters[i]}", f"      sequence: {seqs[key]}"]
                i += 1
        open(os.path.join(ydir, job + ".yaml"), "w").write("\n".join(lines) + "\n")
        print(job, "chains", i, "tokens", sum(len(seqs[k]) * n for k, n in spec))
    json.dump({"accessions": ACC, "jobs": {k: [list(x) for x in v] for k, v in JOBS.items()},
               "licences": {"boltz2": "MIT", "crosslinks": "CC0", "sequences": "CC-BY 4.0",
                            "alphafold_server_output": "NOT USED (non-commercial)"}},
              open(os.path.join(HERE, "provenance.json"), "w"), indent=1)
    print("\nYAMLs in", ydir, "\nNext (GPU box):")
    print("  pip install boltz -U && boltz predict", ydir, "--use_msa_server --diffusion_samples 5 --out_dir", os.path.join(HERE, "out"))


if __name__ == "__main__":
    main()
