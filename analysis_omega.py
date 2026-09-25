"""PREREG_OMEGA readout: does MG354 (MPN_530, AF-P75248) have the fold of an RNA polymerase omega subunit?
Applies the committed rule (PREREG_OMEGA.md, commit 9900012) to the Foldseek results already on disk
(NQ_local/af3-hitcall/omega/O1_mg354.json, O2_ecoli_omega.json). No new search is run here."""
import json
import os
import re

import numpy as np

D = r"C:\Users\bmens\NQ_local\af3-hitcall\omega"
OMEGA = re.compile(r"omega|rpoZ|\bRPB6\b|RPABC2|\bRpoK\b", re.I)
MOLLICUTES = re.compile(r"Mycoplasma|Mycoplasmoides|Ureaplasma|Spiroplasma|Acholeplasma|Mesoplasma", re.I)
CHLAMYDIA = re.compile(r"Chlamydia|Chlamydophila|Waddlia|Parachlamydia|Simkania", re.I)


def hits(path):
    d = json.load(open(os.path.join(D, path)))
    out = []
    for block in d["results"]:
        al = block["alignments"]
        al = al[0] if al and isinstance(al[0], list) else al
        for rank, h in enumerate(al, 1):
            out.append({"db": block["db"], "rank": rank, "target": h["target"][:110], "eval": h["eval"],
                        "prob": h["prob"], "seqId": h["seqId"], "taxName": h.get("taxName", ""),
                        "qcov": round((h["qEndPos"] - h["qStartPos"] + 1) / h["qLen"], 2)})
    return out


def plddt(pdb):
    b = [float(l[60:66]) for l in open(os.path.join(D, pdb)) if l.startswith("ATOM") and l[12:16].strip() == "CA"]
    return float(np.mean(b))


res = {"Q_mean_plddt": round(plddt("P75248.pdb"), 1)}
res["Q_passes"] = res["Q_mean_plddt"] >= 60

o1 = hits("O1_mg354.json")
o1_omega = [h for h in o1 if OMEGA.search(h["target"])]
res["O1_n_hits"] = {db: sum(h["db"] == db for h in o1) for db in sorted({h["db"] for h in o1})}
res["O1_top10"] = {db: [h for h in o1 if h["db"] == db][:10] for db in res["O1_n_hits"]}
res["O1_best_omega_hit"] = min(o1_omega, key=lambda h: h["eval"]) if o1_omega else None
res["O1_chlamydial_hits"] = [h for h in o1 if CHLAMYDIA.search(h["taxName"] + " " + h["target"])]
best = res["O1_best_omega_hit"]
res["O1_verdict"] = ("SUPPORTS" if best and best["eval"] <= 0.01 else
                     "WEAK SUPPORT" if best and best["eval"] <= 1 else "NO OMEGA-FAMILY HIT")

o2 = hits("O2_ecoli_omega.json")
o2_moll = [h for h in o2 if MOLLICUTES.search(h["taxName"] + " " + h["target"])]
res["O2_n_hits"] = len(o2)
res["O2_top10"] = o2[:10]
res["O2_mollicutes_hits"] = o2_moll
top_moll = o2_moll[0] if o2_moll else None
res["O2_verdict"] = ("SUPPORTS" if top_moll and "P75248" in top_moll["target"] and top_moll["eval"] <= 1 else
                     "NO MOLLICUTES HIT" if not top_moll else "DOES NOT SUPPORT (top Mollicutes hit is not P75248)")

# "Weakened": confident hits (E <= 1e-3) all in one clearly unrelated, well-annotated family, and no omega hit at
# E <= 1. Orthologs of the query itself (>= 30% identity) are the same protein, not an unrelated family.
conf = [h for h in o1 if h["eval"] <= 1e-3 and "P75248" not in h["target"]]
unrelated = [h for h in conf if h["seqId"] < 30]
res["O1_confident_hits_excluding_self"] = conf
res["O1_confident_unrelated_hits"] = unrelated
supported = res["O1_verdict"] == "SUPPORTS" or res["O2_verdict"] == "SUPPORTS"
weak_omega = [h for h in o1_omega if h["eval"] <= 1]
res["verdict"] = ("SUPPORTED" if supported else
                  "WEAKENED" if unrelated and not weak_omega else "INCONCLUSIVE")

print(json.dumps({k: v for k, v in res.items() if not k.endswith("top10")}, indent=1)[:6000])
for db, rows in res["O1_top10"].items():
    print(f"\nO1 top hits, {db}:")
    for h in rows:
        print(f"  {h['rank']:>3} E={h['eval']:<9.3g} id={h['seqId']:<5} cov={h['qcov']:<4} {h['taxName'][:28]:28s} {h['target'][:70]}")
print("\nO2 top hits (E. coli omega vs afdb-swissprot):")
for h in res["O2_top10"]:
    print(f"  {h['rank']:>3} E={h['eval']:<9.3g} {h['taxName'][:28]:28s} {h['target'][:70]}")
json.dump(res, open("results_omega.json", "w"), indent=1)
