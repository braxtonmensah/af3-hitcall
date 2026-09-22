// Literature evidence table for the V. cholerae pilot (DESCRIPTIVE, not part of PREREG_VIBRIO).
// For each pair of system proteins: Europe PMC abstracts mentioning both (+ Vibrio), then Jev judges
// each abstract: does it report a direct physical interaction between the two, and what evidence type.
import { writeFileSync } from "node:fs";
import { decide } from "../../jev/src/jev.js";

const NAMES: Record<string, string[]> = {
  PilT: ["PilT"], PilU: ["PilU"], CBP: ["CBP", "chitin-binding protein", "chitin oligosaccharide-binding protein"],
  ChiS: ["ChiS"], DprA: ["DprA"], ComM: ["ComM"], PilA: ["PilA"], PilB: ["PilB"], PilC: ["PilC"], PilD: ["PilD"],
  PilQ: ["PilQ"], PilP: ["PilP"], PilO: ["PilO"], PilN: ["PilN"], PilM: ["PilM"], ComEA: ["ComEA"], ComEC: ["ComEC"],
  TfoX: ["TfoX"], QstR: ["QstR"], TfoS: ["TfoS"], FimT: ["FimT"], PilW: ["PilW"], PilV: ["PilV"], HapR: ["HapR"],
};
const names = Object.keys(NAMES);
const q = (xs: string[]) => "(" + xs.map((x) => `"${x}"`).join(" OR ") + ")";

async function abstracts(a: string, b: string) {
  const query = `${q(NAMES[a])} AND ${q(NAMES[b])} AND (Vibrio OR cholerae) AND HAS_ABSTRACT:y`;
  const url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" +
    new URLSearchParams({ query, format: "json", resultType: "core", pageSize: "6" });
  for (let i = 0; i < 4; i++) {
    try {
      const r = await fetch(url, { signal: AbortSignal.timeout(60000) });
      if (r.ok) {
        const j: any = await r.json();
        return (j.resultList?.result ?? []).map((x: any) => ({ id: x.pmid ?? x.id, year: x.pubYear, title: x.title, abstract: x.abstractText ?? "" }));
      }
    } catch {}
    await new Promise((s) => setTimeout(s, 1500 * (i + 1)));
  }
  return [];
}

const rows: any[] = [];
let spent = 0;
for (let i = 0; i < names.length; i++) {
  for (let k = i + 1; k < names.length; k++) {
    const a = names[i], b = names[k];
    const docs = await abstracts(a, b);
    let best = { direct: 0, evidence: "none", id: "", year: "" } as any;
    for (const d of docs) {
      const r = await decide({ protein_a: a, protein_b: b, title: d.title, abstract: d.abstract.replace(/<[^>]+>/g, "") }, {
        direct: { type: "noul", instructions: "Does `abstract` report evidence that `protein_a` and `protein_b` physically interact with each other directly (bind each other), in Vibrio cholerae or a close relative?" },
        evidence: { type: "choice", instructions: "What is the strongest evidence in `abstract` for a direct `protein_a`-`protein_b` interaction?",
          criteria: { none: "no claim that these two proteins interact", prediction_only: "only computational prediction, modelling or homology", genetic: "genetic, localisation or cell-biology evidence without a binding assay", biochemical_or_structural: "purified-protein binding, pulldown, two-hybrid, crosslinking or a structure" } },
      });
      spent += r.usage.cost_usd ?? 0;
      const dir = r.answers.direct.noul ?? 0;
      if (dir > best.direct) best = { direct: dir, evidence: r.answers.evidence.choice, id: d.id, year: d.year };
    }
    rows.push({ pair: `${a}-${b}`, n_abstracts: docs.length, ...best });
    if (docs.length) console.log(`${a}-${b}: ${docs.length} abstracts, best direct=${best.direct} (${best.evidence}) PMID ${best.id}`);
  }
}
writeFileSync(new URL("./lit_evidence.json", import.meta.url), JSON.stringify(rows, null, 1));
const strong = rows.filter((r) => r.direct >= 0.8);
console.log(`\npairs ${rows.length}, with abstracts ${rows.filter((r) => r.n_abstracts).length}, direct>=0.8: ${strong.length}`);
console.log(strong.map((r) => `${r.pair} ${r.direct} ${r.evidence} PMID${r.id}`).join("\n"));
console.log(`Jev spend: $${spent.toFixed(4)}`);
