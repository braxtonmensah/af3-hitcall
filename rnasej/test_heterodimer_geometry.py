"""Search alternative rigid 1:1 placements against all six RNase J XL restraints.

An exploratory falsification check of the claim that a 2:2 complex is required.
Monomer folds come from the saved 2:2 M. pneumoniae AF3 model 0. A successful
rigid placement is not itself evidence that such a complex exists in cells.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares, minimize
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation

from audit_link_specificity import A_SITES, B_SITES, MODEL, ca_coordinates


HERE = Path(__file__).resolve().parent
RNG = np.random.default_rng(251)


def main() -> None:
    chains = ca_coordinates(MODEL)
    a = np.array(list(chains["A"].values()))
    b = np.array(list(chains["C"].values()))
    a_sites = np.array([chains["A"][i] for i in A_SITES])
    b_sites = np.array([chains["C"][i] for i in B_SITES])
    center = b.mean(axis=0)
    a_tree = cKDTree(a)

    def place(points, vector):
        return Rotation.from_rotvec(vector[:3]).apply(points - center) + center + vector[3:]

    def link_distances(vector):
        return np.linalg.norm(a_sites - place(b_sites, vector), axis=1)

    def geometry(vector):
        placed = place(b, vector)
        b_tree = cKDTree(placed)
        pairs = a_tree.query_ball_tree(b_tree, 4)
        distances = [np.linalg.norm(a[i] - placed[j])
                     for i, neighbors in enumerate(pairs) for j in neighbors]
        contacts = sum(len(neighbors) for neighbors in a_tree.query_ball_tree(b_tree, 8))
        return distances, contacts

    def score(vector):
        links = np.maximum(link_distances(vector) - 29, 0)
        close, _ = geometry(vector)
        clash = np.maximum(3.5 - np.array(close), 0)
        return 100 * float(links @ links) + 10 * float(clash @ clash)

    candidates = []
    for seed in range(40):
        start = (np.zeros(6) if seed == 0 else
                 np.r_[Rotation.random(random_state=RNG).as_rotvec(), RNG.normal(0, 25, 3)])
        fit = least_squares(lambda v: np.maximum(link_distances(v)-27, 0), start,
                            max_nfev=200)
        if max(link_distances(fit.x)) > 30:
            continue
        close, contacts = geometry(fit.x)
        candidates.append((sum(d < 3 for d in close), -contacts, seed, fit.x))
    candidates.sort(key=lambda item: item[:3])

    results = []
    for _, _, seed, vector in candidates[:8]:
        fit = minimize(score, vector, method="L-BFGS-B", options={"maxiter": 180})
        close, contacts = geometry(fit.x)
        distances = link_distances(fit.x)
        results.append({"seed": seed, "optimizer_success": bool(fit.success),
                        "score": round(float(fit.fun), 3),
                        "link_distances_angstrom": [round(float(x), 2) for x in distances],
                        "all_links_within_30": bool(np.all(distances <= 30)),
                        "ca_pairs_under_3_angstrom": int(sum(x < 3 for x in close)),
                        "ca_pairs_under_3p5_angstrom": int(sum(x < 3.5 for x in close)),
                        "ca_contacts_under_8_angstrom": contacts})
    output = {"source_model": str(MODEL), "initial_feasible": len(candidates),
              "random_starts": 40, "refined": results,
              "scope": "Rigid monomer search on one AF3 model, no side-chain packing or binding-energy evaluation; a failed search cannot prove no 1:1 structure exists."}
    (HERE / "heterodimer_geometry_search.json").write_text(json.dumps(output, indent=2))
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
