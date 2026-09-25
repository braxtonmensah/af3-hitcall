"""Write the TETRA model (3ZQ4 template, AF3 sample 1, pairing CA+DE) as a CA-only PDB for inspection."""
import os, sys
import numpy as np
sys.argv = [sys.argv[0]]
src = open("analysis_tetra.py", encoding="utf-8").read()
src = src.split("res = {}\nfor pid in TEMPLATES:")[0]  # definitions only
exec(src)
T = template("3ZQ4")
xyz = z["xyz1"].astype(float)
x139, x423 = xyz[ch == loci.index("MG_139")], xyz[ch == loci.index("MG_423")]
a1, b1, _ = place(x139, x423, T, "C")
a2, b2, _ = place(x139, x423, T, "D")
lines, n = [], 1
for cid, (co, seqname) in zip("ABCD", [(a1, "MG_139"), (b1, "MG_423"), (a2, "MG_139"), (b2, "MG_423")]):
    three = {v: k for k, v in AA.items() if k != "MSE"}
    for i, p in enumerate(co):
        lines.append("ATOM  %5d  CA  %3s %s%4d    %8.3f%8.3f%8.3f  1.00  0.00           C" % (n, three.get(SEQ[seqname][i], "UNK"), cid, i + 1, *p)); n += 1
    lines.append("TER")
hdr = ["REMARK  Mycoplasma genitalium RNase J heterotetramer model (MG139 = chains A,C; MG423 = chains B,D)",
       "REMARK  AF3 heterodimer (Todor et al. 2026, pool 1052, sample 1) placed twice on the B. subtilis RNase J1",
       "REMARK  tetramer 3ZQ4. CA only. Hypothesis model consistent with 6/6 in-cell crosslinks (DSSO+DSS)."]
open("new_biology/rnaseJ_MG139_MG423_heterotetramer_CA.pdb", "w").write("\n".join(hdr + lines + ["END"]) + "\n")
print("atoms", n - 1)
