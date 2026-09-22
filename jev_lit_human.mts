// PREREG_LITJEV: literature truth labels for sampled human pairs, judged by Jev. Resumable (JSONL).
import { readFileSync, appendFileSync, existsSync } from "node:fs";
import { decide } from "../jev/src/jev.js";

const B = "C:/Users/bmens/NQ_local/af3-hitcall/burke";
const OUT = `${B}/litjev.jsonl`;

// --- sample (seeded) ---
function rng(seed: number) { return () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 2 ** 32); }
const rand = rng(20260922);
function sample<T>(xs: T[], k: number) { const a = [...xs]; for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(rand() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a.slice(0, k); }

const lines = readFileSync(`${B}/S1.csv`, "utf8").split(/\r?\n/);
const hdr = lines[0].split(",");
const col = (n: string) => hdr.indexOf(n);
const rows = lines.slice(1).filter(Boolean).map((l) => l.split(","));
const pick = (r: string[]) => ({ id: r[col("unique_ID")], g1: r[col("Gen.id1")], g2: r[col("Gen.id2")], p: +r[col("pDockQ")],
  prec: r[col("int3D_model_structure")] === "1", huri: r[col("Dataset")].includes("HURI") });
const all = rows.map(pick).filter((x) => x.huri && x.g1 && x.g2 && x.g1 !== "NA" && x.g2 !== "NA" && x.g1 !== x.g2);
const groups: Record<string, any[]> = {
  confident: sample(all.filter((x) => !x.prec && x.p > 0.23), 350),
  low: sample(all.filter((x) => !x.prec && x.p < 0.10), 350),
  prec_ref: sample(all.filter((x) => x.prec && x.p > 0.23), 150),
};

const done = new Set<string>();
if (existsSync(OUT)) for (const l of readFileSync(OUT, "utf8").split("\n").filter(Boolean)) done.add(JSON.parse(l).key);

async function abstracts(a: string, b: string) {
  const url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" +
    new URLSearchParams({ query: `"${a}" AND "${b}" AND HAS_ABSTRACT:y`, format: "json", resultType: "core", pageSize: "5" });
  for (let i = 0; i < 4; i++) {
    try {
      const r = await fetch(url, { signal: AbortSignal.timeout(60000) });
      if (r.ok) { const j: any = await r.json(); return (j.resultList?.result ?? []).map((x: any) => ({ id: x.pmid ?? x.id, title: x.title ?? "", abstract: (x.abstractText ?? "").replace(/<[^>]+>/g, "") })); }
    } catch {}
    await new Promise((s) => setTimeout(s, 1500 * (i + 1)));
  }
  return null;
}

let spent = 0;
for (const [g, items] of Object.entries(groups)) {
  for (const x of items) {
    const key = `${g}|${x.id}`;
    if (done.has(key)) continue;
    const docs = await abstracts(x.g1, x.g2);
    if (docs === null) continue; // network failure: resume later
    let best = 0, ev = "none", pmid = "";
    for (const d of docs) {
      try {
        const r = await decide({ protein_a: x.g1, protein_b: x.g2, title: d.title, abstract: d.abstract.slice(0, 6000) }, {
          direct: { type: "noul", instructions: "Does `abstract` report evidence that the human proteins `protein_a` and `protein_b` physically interact with each other directly (bind each other)?" },
          evidence: { type: "choice", instructions: "What is the strongest evidence in `abstract` for a direct `protein_a`-`protein_b` interaction?",
            criteria: { none: "no claim that these two proteins interact", prediction_only: "only computational prediction, modelling or homology", genetic: "genetic, co-localisation or cell-biology evidence without a binding assay", biochemical_or_structural: "co-immunoprecipitation, pulldown, two-hybrid, purified-protein binding, crosslinking or a structure" } },
        });
        spent += r.usage.cost_usd ?? 0;
        const n = r.answers.direct.noul ?? 0;
        if (n > best) { best = n; ev = r.answers.evidence.choice ?? "none"; pmid = String(d.id); }
      } catch (e) { console.error("jev error", (e as Error).message); }
    }
    appendFileSync(OUT, JSON.stringify({ key, group: g, id: x.id, g1: x.g1, g2: x.g2, pDockQ: x.p, n_abstracts: docs.length, best, evidence: ev, pmid }) + "\n");
  }
  console.log(`group ${g} done; spend so far $${spent.toFixed(3)}`);
}
console.log(`total spend $${spent.toFixed(3)}`);
