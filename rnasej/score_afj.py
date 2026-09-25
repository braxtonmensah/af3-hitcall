"""PREREG_AFJ scorer. Usage: python score_afj.py <folder with fold_rnasej_*.zip>
AF Server chain order: entity 1 copies first (A, B...), then entity 2 copies."""
import glob
import io
import json
import os
import re
import sys
import zipfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LINKS = [(120, 502), (120, 546), (409, 322), (225, 224), (257, 224), (228, 224)]
NEAR, FAR = LINKS[:3], LINKS[3:]
LAYOUT = {"rnasej_mpn_2x2": (["A", "B"], ["C", "D"]), "rnasej_mg_2x2": (["A", "B"], ["C", "D"]),
          "rnasej_mpn_1x1": (["A"], ["B"]), "rnasej_mpn_decoy_2x2": (["A", "B"], ["C", "D"])}


def ca(cif):
    cols, out = [], {}
    for line in cif.splitlines():
        if line.startswith("_atom_site."):
            cols.append(line.strip().split(".", 1)[1]); continue
        if not line.startswith("ATOM"):
            continue
        f = dict(zip(cols, line.split()))
        if f["label_atom_id"] == "CA":
            out.setdefault(f["label_asym_id"], {})[int(f["label_seq_id"])] = np.array([float(f["Cartn_x"]), float(f["Cartn_y"]), float(f["Cartn_z"])])
    return out


def files(root):
    for z in glob.glob(os.path.join(root, "**", "fold_rnasej_*.zip"), recursive=True):
        with zipfile.ZipFile(z) as f:
            for m in f.namelist():
                yield os.path.basename(m), f.read(m)


data = {}
for name, b in files(sys.argv[1]):
    m = re.match(r"fold_(rnasej_\w+?)_(model|summary_confidences)_(\d)\.(cif|json)$", name)
    if not m:
        continue
    job, kind, k = m.group(1), m.group(2), int(m.group(3))
    d = data.setdefault(job, {}).setdefault(k, {})
    if kind == "model":
        d["ca"] = ca(b.decode())
    else:
        d["conf"] = json.loads(b)
res = {}
for job, samples in sorted(data.items()):
    J, X = LAYOUT[job]
    rows = []
    for k, s in sorted(samples.items()):
        c, conf = s["ca"], s["conf"]
        ids = sorted(c)
        cp = np.array(conf["chain_pair_iptm"])
        best_jx = max(cp[ids.index(j)][ids.index(x)] for j in J for x in X)
        row = {"sample": k, "iptm": conf.get("iptm"), "ptm": conf.get("ptm"), "best_J_partner_iptm": float(best_jx),
               "J_J_iptm": float(cp[ids.index(J[0])][ids.index(J[1])]) if len(J) > 1 else None}
        if "decoy" not in job:
            dist = [min(np.linalg.norm(c[j][a] - c[x][b]) for j in J for x in X) for a, b in LINKS]
            sat = [dd <= 30 for dd in dist]
            row.update(dist=[round(float(v), 1) for v in dist], near_ok=all(sat[:3]), far_ok=all(sat[3:]), all_ok=all(sat))
        rows.append(row)
    res[job] = rows
    print(job)
    for r in rows:
        print("  ", {k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()})


def n_ok(job, key):
    return sum(r.get(key, False) for r in res.get(job, []))


mpn = res.get("rnasej_mpn_2x2", [])
o1 = sum(r["all_ok"] and r["best_J_partner_iptm"] >= 0.5 for r in mpn) >= 3 if mpn else None
o4 = max(r["best_J_partner_iptm"] for r in res["rnasej_mpn_decoy_2x2"]) < 0.3 if "rnasej_mpn_decoy_2x2" in res else None
res["O1_primary"] = o1
res["O2_mg_all_ok_samples"] = n_ok("rnasej_mg_2x2", "all_ok")
res["O3_dimer_near_ok_far_ok"] = [n_ok("rnasej_mpn_1x1", "near_ok"), n_ok("rnasej_mpn_1x1", "far_ok")]
res["O4_decoy_specific"] = o4
res["COMPUTATIONALLY_SOLVED"] = bool(o1 and o4)
print({k: v for k, v in res.items() if k.startswith(("O", "COMP"))})
json.dump(res, open(os.path.join(HERE, "results_afj.json"), "w"), indent=1, default=float)
