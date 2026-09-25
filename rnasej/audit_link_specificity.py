"""Stress-test whether the reported 2:2 geometry fits specific XL residue pairings.

This reuses the published M. pneumoniae links and saved AF Server model 0.
It does not prove a 2:2 complex or provide an experimental stoichiometry.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "new_biology" / "rnasej_mpn_2x2_AF3_model_0.cif"
J_CHAINS = ("A", "B")
P_CHAINS = ("C", "D")
A_SITES = (120, 120, 409, 225, 257, 228)
B_SITES = (502, 546, 322, 224, 224, 224)


def ca_coordinates(path: Path) -> dict[str, dict[int, np.ndarray]]:
    fields = []
    chains: dict[str, dict[int, np.ndarray]] = {}
    for line in path.read_text().splitlines():
        if line.startswith("_atom_site."):
            fields.append(line.strip().split(".", 1)[1])
        elif line.startswith("ATOM"):
            atom = dict(zip(fields, line.split()))
            if atom["label_atom_id"] == "CA":
                chains.setdefault(atom["label_asym_id"], {})[int(atom["label_seq_id"])] = np.array(
                    [float(atom[axis]) for axis in ("Cartn_x", "Cartn_y", "Cartn_z")]
                )
    return chains


def nearest_distance(chains, a, b):
    return min(float(np.linalg.norm(chains[j][a] - chains[p][b]))
               for j in J_CHAINS for p in P_CHAINS)


def main() -> None:
    chains = ca_coordinates(MODEL)
    observed = [nearest_distance(chains, a, b) for a, b in zip(A_SITES, B_SITES)]
    graphs = {frozenset(zip(A_SITES, b_assignment))
              for b_assignment in set(itertools.permutations(B_SITES))
              if len(set(zip(A_SITES, b_assignment))) == len(A_SITES)}
    rewired = []
    for graph in graphs:
        distances = [nearest_distance(chains, a, b) for a, b in graph]
        rewired.append({"all_within_30": all(x <= 30 for x in distances),
                        "mean_distance": float(np.mean(distances))})
    result = {
        "model": str(MODEL),
        "observed_distances_angstrom": [round(x, 2) for x in observed],
        "observed_all_within_30": all(x <= 30 for x in observed),
        "observed_mean_distance": round(float(np.mean(observed)), 2),
        "degree_preserving_simple_graph_rewirings": len(rewired),
        "rewirings_all_within_30": sum(x["all_within_30"] for x in rewired),
        "rewirings_mean_at_most_observed": int(sum(
            x["mean_distance"] <= float(np.mean(observed)) + 1e-9 for x in rewired
        )),
        "note": "Exact reassignment of observed partner lysine sites to observed RNase J lysine sites; hotspot multiplicities fixed, duplicate edges excluded, equivalent graphs collapsed. Rewiring is exploratory and not a sampling model for XL-MS.",
    }
    (ROOT / "rnasej" / "audit_link_specificity.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
