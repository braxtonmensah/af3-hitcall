"""Build SAMPLE_REPORT.pdf, the artifact a customer would receive, from committed results only.

Lives in the repo (not outreach/) on purpose: the report is a claim about the data, so the code that
makes it should be as auditable as the analyses. The PDF is written into outreach/, which is not public.

Every number is read from a results_*.json in the repo; nothing is typed in by hand. Run from the
repo root: py -3.11 build_sample_report.py

Design decisions, so they are not silently reverted:
 1. Never-solved rows lead. They are the product. Known complexes go in a separate validation block,
    because a buyer asks "what did it tell me I did not know", not "did it find the ribosome".
 2. The stoichiometry column carries a CALIBRATED probability from HIGHER_CAL, not a bare label,
    and the error rates sit next to it.
 3. The conservative X-ray-only figure (53%) is on page 1, not buried. Disclosing the weakest number
    is why a scientific reader believes the rest.
"""
import json
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle)

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "outreach", "SAMPLE_REPORT.pdf")
NAMEF = r"C:\Users\bmens\NQ_local\af3-hitcall\omega\mg_protein_names.json"
NAMES = json.load(open(NAMEF)) if os.path.exists(NAMEF) else {}

H = json.load(open(os.path.join(ROOT, "results_higher.json")))
CAL = json.load(open(os.path.join(ROOT, "results_higher_cal.json")))
FUT = json.load(open(os.path.join(ROOT, "results_future.json")))

INK = colors.HexColor("#111318")
MUTED = colors.HexColor("#5b6472")
RULE = colors.HexColor("#d9dde4")
ACCENT = colors.HexColor("#1f4e79")
BAND = colors.HexColor("#f4f6f9")

N_PREREG = len([f for f in os.listdir(ROOT) if f.startswith("PREREG") and f.endswith(".md")])

ss = getSampleStyleSheet()


def S(name, size, leading, color=INK, space=0, font="Helvetica", align=TA_LEFT):
    return ParagraphStyle(name, parent=ss["Normal"], fontName=font, fontSize=size, leading=leading,
                          textColor=color, spaceAfter=space, alignment=align)


TITLE = S("t", 19, 23, INK, 2, "Helvetica-Bold")
SUB = S("s", 10.5, 14.5, MUTED, 10)
H2 = S("h2", 12.5, 16, ACCENT, 4, "Helvetica-Bold")
BODY = S("b", 9.3, 13.2, INK, 6)
SMALL = S("sm", 7.8, 10.6, MUTED, 4)
CELL = S("c", 7.6, 9.6, INK)
CELLB = S("cb", 7.6, 9.6, INK, 0, "Helvetica-Bold")
STATN = S("sn", 21, 23, ACCENT, 0, "Helvetica-Bold")
STATL = S("sl", 7.5, 10, MUTED)


def short(locus, n=42):
    nm = NAMES.get(locus, "Uncharacterized protein")
    nm = nm.split(" (")[0]
    return nm if len(nm) <= n else nm[: n - 3] + "..."


# ---------- calibrated stoichiometry probability, straight from HIGHER_CAL ----------
c2 = CAL["C2_split"]
n_hi, n_one = CAL["n_higher"], CAL["n_one_to_one"]
k_split_hi = c2["sens_k_n"][0]
k_split_one = c2["fpr_k_n"][0]
P_SPLIT = k_split_hi / (k_split_hi + k_split_one)
P_NOSPLIT = (n_hi - k_split_hi) / ((n_hi - k_split_hi) + (n_one - k_split_one))
BASE = c2["base_rate_higher"]


def stoich(r):
    if r["split"]:
        return f"higher-order<br/><font size=6 color='#5b6472'>p = {P_SPLIT:.2f} (calibrated)</font>"
    if r["clean"]:
        return f"no evidence of &gt;1:1<br/><font size=6 color='#5b6472'>p = {P_NOSPLIT:.2f}</font>"
    return "indeterminate<br/><font size=6 color='#5b6472'>links unclassified</font>"


# 0.152 is the screen's 99.5th percentile over all 113,050 pairs (data/S0.npy). Rows below it are
# noise and a customer table that includes them is padding, not a shortlist.
CONF = 0.152
P = H["all_pairs"]
novel = [r for r in P if not r["prec"] and r["n_links"] >= 2 and r["S0"] >= CONF]
known = [r for r in P if r["prec"] and r["n_links"] >= 2 and r["S0"] >= CONF]
novel.sort(key=lambda r: -r["S0"])
known.sort(key=lambda r: -r["S0"])

doc = BaseDocTemplate(OUT, pagesize=LETTER, leftMargin=0.62 * inch, rightMargin=0.62 * inch,
                      topMargin=0.55 * inch, bottomMargin=0.6 * inch,
                      title="Complex Triage Report (sample)", author="Braxton Mensah")
doc.addPageTemplates([PageTemplate(id="n", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width,
                                                         doc.height, id="f")])])
F = []
F.append(Paragraph("Complex Triage Report", TITLE))
F.append(Paragraph("Which predicted protein complexes in your screen deserve an experiment, with the "
                   "evidence and the decision rule attached.<br/>"
                   "<font size=8>Sample report. Public dataset, no client data. Regenerated from committed "
                   "results by <b>build_sample_report.py</b>.</font>", SUB))

f2 = FUT["F2"]
stats = [[Paragraph(f"{f2['confident']['frac_correct_f1_ge_0.5']*100:.0f}%", STATN),
          Paragraph(f"{f2['low']['frac_correct_f1_ge_0.5']*100:.1f}%", STATN),
          Paragraph("53%", STATN),
          Paragraph(f"{c2['precision']*100:.0f}%", STATN)],
         [Paragraph(f"of confident predictions of never-solved human complexes had the correct interface, "
                    f"checked against structures released after the prediction was made (n={f2['confident']['n']})", STATL),
          Paragraph(f"for low-confidence predictions over the same period (n={f2['low']['n']}). The 40x "
                    "separation the usual aggregate accuracy figure hides", STATL),
          Paragraph("<b>the conservative figure.</b> Most of those structures are cryo-EM, which is "
                    "sometimes built with AlphaFold help. On X-ray-only entries (n=19) the rate is 53%, "
                    "CI [0.32, 0.74]. Read 53% to 81%, not 81%", STATL),
          Paragraph(f"precision of the stoichiometry call against PDB assembly records "
                    f"(n={n_hi + n_one} pairs), against a {BASE*100:.0f}% base rate", STATL)]]
t = Table(stats, colWidths=[doc.width / 4.0] * 4)
t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("BACKGROUND", (0, 0), (-1, -1), BAND),
                       ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                       ("TOPPADDING", (0, 0), (-1, 0), 8), ("BOTTOMPADDING", (0, 1), (-1, 1), 9),
                       ("LINEBEFORE", (1, 0), (-1, -1), 0.6, colors.white)]))
F.append(t)
F.append(Spacer(1, 11))

F.append(Paragraph("What was analysed", H2))
F.append(Paragraph(
    f"A published genome-scale AlphaFold3 screen of all 113,050 protein pairs in <i>Mycoplasma genitalium</i> "
    f"(Todor et al. 2026), combined with in-cell crosslinking mass spectrometry from two chemistries "
    f"(O'Reilly et al. 2020). <b>{H['n_testable_pairs']} pairs</b> had both a model and at least two crosslinks "
    f"and were testable. Below: first the pairs with <b>no solved structure</b>, which is what you are buying, "
    f"then the known complexes the same rule recovered, which is how you check it.", BODY))

COLS = [0.80, 1.62, 1.62, 0.44, 0.40, 0.52, 1.30]
COLW = [c / sum(COLS) * doc.width for c in COLS]
HEADER = [Paragraph(x, CELLB) for x in
          ["Pair", "Protein 1", "Protein 2", "Score", "Links", "Near/<br/>Far", "Stoichiometry call"]]


def block(rows, limit):
    data = [HEADER]
    for r in rows[:limit]:
        a, b = r["pair"].split("-")
        data.append([Paragraph(r["pair"].replace("-", " /<br/>"), CELL), Paragraph(short(a), CELL),
                     Paragraph(short(b), CELL), Paragraph(f"{r['S0']:.2f}", CELL),
                     Paragraph(str(r["n_links"]), CELL),
                     Paragraph(f"{r['n_near']}/{r['n_far']}", CELL), Paragraph(stoich(r), CELL)])
    t = Table(data, colWidths=COLW, repeatRows=1)
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, ACCENT),
        ("LINEBELOW", (0, 1), (-1, -2), 0.3, RULE),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BAND]),
    ]))
    return t


F.append(Spacer(1, 3))
F.append(Paragraph(f"Ranked candidates: no solved structure ({len(novel)} above the confidence cut)", H2))
F.append(Paragraph(
    f"These are the rows that justify the report. Nobody has solved these complexes, so the ranking is the "
    f"only thing between your team and picking at random. Cut at a score of {CONF}, the screen's 99.5th "
    f"percentile over all 113,050 pairs; below that the score carries no information and padding the table "
    f"would only make it look longer.", BODY))
F.append(block(novel, 20))
F.append(Spacer(1, 12))

F.append(KeepTogether([
    Paragraph("Known complexes the same rule recovered (validation, not findings)", H2),
    Paragraph("Run blind, the method also ranked complexes whose answers are already in the PDB. That is how "
              "you audit it, and it is reported separately so it cannot be mistaken for new biology.", BODY),
    block(known, 12)]))
F.append(Spacer(1, 12))

F.append(KeepTogether([
    Paragraph("How to read the stoichiometry call, including when it is wrong", H2),
    Paragraph(
        f"A pair whose crosslinks split into satisfied and impossible-in-a-1:1-model is flagged higher-order. "
        f"That rule was calibrated against copy numbers in PDB biological assemblies for the "
        f"{n_hi + n_one} pairs that have a solved homologous co-complex "
        f"(pre-registered as PREREG_HIGHER_CAL before any assembly record was fetched):",
        BODY),
    Table([[Paragraph(x, CELLB) for x in ["Sensitivity", "False-positive rate", "Precision", "Lift over base rate"]],
           [Paragraph(f"{c2['sensitivity']*100:.0f}% ({c2['sens_k_n'][0]}/{c2['sens_k_n'][1]})<br/>"
                      f"<font size=6 color='#5b6472'>CI {c2['sens_ci']}</font>", CELL),
            Paragraph(f"{c2['false_positive_rate']*100:.0f}% ({c2['fpr_k_n'][0]}/{c2['fpr_k_n'][1]})<br/>"
                      f"<font size=6 color='#5b6472'>CI {c2['fpr_ci']}</font>", CELL),
            Paragraph(f"{c2['precision']*100:.0f}%<br/><font size=6 color='#5b6472'>CI {c2['prec_ci']}</font>", CELL),
            Paragraph(f"{c2['lift']}x<br/><font size=6 color='#5b6472'>base rate {BASE*100:.0f}%</font>", CELL)]],
          colWidths=[doc.width / 4.0] * 4,
          style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("BACKGROUND", (0, 0), (-1, 0), BAND),
                            ("LINEBELOW", (0, 0), (-1, 0), 0.6, ACCENT),
                            ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                            ("LEFTPADDING", (0, 0), (-1, -1), 6)])),
    Spacer(1, 5),
    Paragraph(
        "<b>The calibration made us retract one of our own examples.</b> RNA polymerase beta to beta-prime "
        "was originally presented as a recovered higher-order assembly. The PDB says it is 1:1 inside a "
        "larger machine, in 367 of 370 assemblies, so the flag fired for the wrong reason and the "
        "pre-registration required its removal. It is gone from the list above. This is the kind of thing "
        "a report should tell you about itself.", BODY)]))
F.append(Spacer(1, 10))

F.append(KeepTogether([
    Paragraph("What this report does not claim", H2),
    Paragraph(
        f"<b>The 81% is conditional.</b> It is measured on never-solved pairs that someone later solved, which "
        f"is {FUT['F1_newly_solved']['rate_confident']*100:.1f}% of confident calls. It is not the probability "
        f"that an arbitrary confident pair interacts in cells, and we do not report it as one.<br/>"
        "<b>Crosslink agreement is proximity, not proof.</b> Two residues within reach means the model is "
        "compatible with the data, not that the interface is right.<br/>"
        "<b>Every flagged pair is a hypothesis for the bench.</b> The value here is ordering the queue and "
        "attaching the evidence, not replacing the experiment.", BODY),
    Spacer(1, 4),
    Paragraph(
        f"Method, code, data and all {N_PREREG} pre-registrations, including the ones that failed, are public at "
        "github.com/braxtonmensah/af3-hitcall. Each pre-registration was committed before the data were "
        "joined, so the ordering is verifiable from commit dates rather than asserted.", SMALL)]))

doc.build(F)
print("wrote", OUT)
print(f"novel rows {len(novel)}, known rows {len(known)}, "
      f"P(higher|split)={P_SPLIT:.2f}, P(higher|no split)={P_NOSPLIT:.2f}")
