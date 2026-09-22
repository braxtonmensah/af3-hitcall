"""POST HOC: precedent gap within the paper's independent local runs (MOESM8), per condition."""
import os, json
import numpy as np, pandas as pd
from analysis_h1_h2_lib import precedent_matrix_strict
from metrics import Ranked
D = r"C:\Users\bmens\NQ_local\af3-hitcall\data"
df = pd.read_csv(os.path.join(D, "moesm8_pairs.csv"))
PRE = precedent_matrix_strict("") | precedent_matrix_strict("_id0")
res = {}
for g, s in df.groupby("group"):
    y = s.y.to_numpy(); p = PRE[s.i, s.j]; r = Ranked(s.I.to_numpy()); one = np.ones(len(s))
    res[g] = dict(n_prec=int((y & p).sum()), n_never=int((y & ~p).sum()),
                  auroc_prec=round(r.auroc(one * (y & p), one * ~y), 3), auroc_never=round(r.auroc(one * (y & ~p), one * ~y), 3))
    print(g, res[g])
json.dump(res, open("results_posthoc_local_runs.json", "w"), indent=1)
