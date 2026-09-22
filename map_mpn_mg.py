"""Map M. pneumoniae proteins (O'Reilly 2020 XL-MS search FASTA) to M. genitalium loci by
reciprocal best hit. Sequence-only; touches no score or truth label.
3-mer prefilter (top 5 candidates) then Smith-Waterman (BLOSUM62, gap -11/-1)."""
import os
from collections import Counter

import pandas as pd
from Bio import SeqIO
from Bio.Align import PairwiseAligner, substitution_matrices

D = r"C:\Users\bmens\NQ_local\af3-hitcall"
mg = pd.read_csv(os.path.join(D, "data", "proteins.csv"))
OK = set("ARNDCQEGHILKMFPSTWYVBZX")


def clean(s):
    return "".join(c if c in OK else "X" for c in s.upper().rstrip("*"))


mg_seq = {l: clean(s) for l, s in zip(mg.locus_tag, mg.aa_sequence)}
mpn_seq = {}
for r in SeqIO.parse(os.path.join(D, "xlms2020", "Full_database_combined.fasta"), "fasta"):
    acc = r.id.split("|")[1] if "|" in r.id else r.id
    mpn_seq[acc] = clean(str(r.seq))

al = PairwiseAligner(mode="local", open_gap_score=-11, extend_gap_score=-1)
al.substitution_matrix = substitution_matrices.load("BLOSUM62")


def kmers(s, k=3):
    return Counter(s[i:i + k] for i in range(len(s) - k + 1))


mgk = {l: kmers(s) for l, s in mg_seq.items()}
mpk = {a: kmers(s) for a, s in mpn_seq.items()}


def best(query_k, query_s, db_k, db_s):
    cand = sorted(db_k, key=lambda t: -sum((query_k & db_k[t]).values()))[:5]
    sc = {t: al.score(query_s, db_s[t]) for t in cand}
    t = max(sc, key=sc.get)
    return t, sc[t]


fwd = {a: best(mpk[a], mpn_seq[a], mgk, mg_seq) for a in mpn_seq}
rev = {l: best(mgk[l], mg_seq[l], mpk, mpn_seq) for l in mg_seq}
rows = []
for a, (l, s) in fwd.items():
    # self-score normalised bit-like ratio as a sanity filter
    self_s = al.score(mpn_seq[a], mpn_seq[a])
    rows.append(dict(mpn=a, mg=l, score=s, norm=s / self_s, rbh=rev[l][0] == a))
m = pd.DataFrame(rows)
m = m[m.rbh & (m.norm > 0.15)]
m.to_csv(os.path.join(D, "data", "mpn_to_mg.csv"), index=False)
print("MPN proteins", len(mpn_seq), " RBH mapped", len(m), " MG loci covered", m.mg.nunique())
print(m.norm.describe())
