"""POST HOC (after FUTURE results): is F2 inflated because new structures were built from AlphaFold
models? Stratify F2 by (1) recorded in-silico starting model, (2) resolution, (3) deposition before
AlphaFold-Multimer was public (2021-10-04), when no predicted complex could seed the model."""
import json
import os

import numpy as np
import pandas as pd
import requests

from metrics import ci

F = r"C:\Users\bmens\NQ_local\af3-hitcall\future"
rng = np.random.default_rng(7)
R = pd.read_csv(os.path.join(F, "f2_pairs.csv"))
R = R[R.status == "ok"].copy()
ids = sorted(set(R.entry))
Q = """query($ids:[String!]!){entries(entry_ids:$ids){rcsb_id exptl{method} rcsb_entry_info{resolution_combined}
 rcsb_accession_info{deposit_date} pdbx_initial_refinement_model{source_name type details}
 em_3d_fitting_list{details} em_3d_fitting{details}}}"""
meta = {}
for k in range(0, len(ids), 200):
    r = requests.post("https://data.rcsb.org/graphql", json={"query": Q, "variables": {"ids": [i.upper() for i in ids[k:k + 200]]}}, timeout=120).json()
    for x in r["data"]["entries"]:
        txt = json.dumps([x.get("pdbx_initial_refinement_model"), x.get("em_3d_fitting_list"), x.get("em_3d_fitting")]).lower()
        insil = any(w in txt for w in ("alphafold", "in silico", "colabfold", "rosettafold", "predicted", "af2", "af3"))
        res = (x["rcsb_entry_info"] or {}).get("resolution_combined") or [None]
        meta[x["rcsb_id"].lower()] = dict(method=x["exptl"][0]["method"], res=res[0],
                                          deposit=x["rcsb_accession_info"]["deposit_date"][:10], insilico=insil)
M = pd.DataFrame.from_dict(meta, orient="index")
R = R.join(M, on="entry")
R["correct"] = R.f1 >= 0.5
R["pre_multimer"] = R.deposit < "2021-10-04"
R["hires"] = R.res <= 3.0


def summ(df):
    out = {}
    for g in ("confident", "low"):
        v = df[df.group == g].correct.to_numpy()
        if len(v):
            bs = [rng.choice(v, len(v)).mean() for _ in range(2000)]
            out[g] = {"n": len(v), "frac_correct": float(v.mean()), "ci95": ci(np.array(bs), 0.95).tolist()}
    return out


res = {"all": summ(R),
       "no_insilico_start_recorded": summ(R[~R.insilico]),
       "insilico_start_recorded": summ(R[R.insilico]),
       "resolution_le_3A": summ(R[R.hires]),
       "xray_only": summ(R[R.method == "X-RAY DIFFRACTION"]),
       "deposited_before_AF_multimer_2021-10-04": summ(R[R.pre_multimer]),
       "strictest_pre_multimer_and_no_insilico": summ(R[R.pre_multimer & ~R.insilico]),
       "method_counts": R.groupby(["group", "method"]).size().rename(lambda x: str(x)).to_dict()}
res["method_counts"] = {str(k): int(v) for k, v in R.groupby(["group", "method"]).size().items()}
print(json.dumps(res, indent=1, default=float))
json.dump(res, open("results_posthoc_future.json", "w"), indent=1, default=float)
R.to_csv(os.path.join(F, "f2_pairs_meta.csv"), index=False)
