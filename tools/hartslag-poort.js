#!/usr/bin/env node
// hartslag-poort.js (5 sep, v23.241) — zeggen WELKE proef dichtging, niet dat er een dichtging.
//
// WAAROM DIT BESTAAT
//
// Drie nachten op rij stond er in de hartslag:
//
//     "reden": "de poort ging dicht op wat de bot schreef, in alle pogingen; niets gepusht"
//
// Drie keer exact dezelfde zin. Dat is een categorie en geen diagnose: je weet dat er iets misging en
// je weet niets over wát. De echte informatie stond wel in het poortlogboek, maar dat zit in een
// artefact op de runpagina, en dat moet iemand met de hand downloaden. Stefan heeft dat op 5
// september gedaan, en toen was het binnen twee minuten duidelijk:
//
//     ROOD  pw-lesgat.js
//     ✗ het aantal onverklaarde kaarten loopt niet op (1 van maximaal 0)
//
// Twee regels. Die hadden er drie nachten eerder in kunnen staan.
//
// Dit is dezelfde fout als v23.216 ("telling klopt niet: sentences") en als v23.217 ("rebase
// mislukt"): een controle die wel afgaat maar niet vertelt wat hij zag. De hartslag is het enige
// kanaal waarlangs de nacht vertelt wat er gebeurde, en hij hield precies het stuk achter dat je
// nodig had.
//
// GEBRUIK
//
//   node tools/hartslag-poort.js <poort.log> [pad-naar-hartslag]
//   node tools/hartslag-poort.js --zelftest
//
// Zet in de hartslag een veld "poortRood": de rode suites met per suite de regels die afgingen.
// Ontbreekt het logboek of staat er niets roods in, dan verandert er niets: nul is geen bericht.
const fs = require("fs");
const path = require("path");

const HART = path.join(__dirname, "avondrun-hart.json");
const MAX_SUITES = 8;
const MAX_REGELS = 6;

/* Het formaat van poort.js: eerst een regelblok per suite ("  ROOD   pw-lesgat.js   2s"), daarna een
   kop "wat er rood is" met per suite "--- naam ---" en de regels die met een kruisje beginnen.
   Sommige suites (die met de playwright-runner) printen "FAIL <regel>" in plaats van een kruisje;
   allebei tellen mee, want allebei zijn het een proef die afging. */
function lees(tekst) {
  const uit = [];
  const regels = String(tekst || "").split("\n");
  let nu = null;
  for (let i = 0; i < regels.length; i++) {
    const r = regels[i];
    const kop = /^---\s+(\S+)\s+---\s*$/.exec(r);
    if (kop) { nu = { suite: kop[1], regels: [] }; uit.push(nu); continue; }
    if (!nu) continue;
    const stuk = r.trim();
    if (!stuk) continue;
    if (/^\d+\/\d+ groen/.test(stuk) || /^POORT/.test(stuk)) { nu = null; continue; }
    if (stuk.indexOf("✗") === 0 || /^FAIL\b/.test(stuk)) {
      if (nu.regels.length < MAX_REGELS) nu.regels.push(stuk.replace(/^✗\s*/, "").replace(/^FAIL\s*/, ""));
    }
  }
  return uit.slice(0, MAX_SUITES);
}

function schrijf(logPad, hartPad) {
  let tekst = "";
  try { tekst = fs.readFileSync(logPad, "utf8"); } catch (e) { return { status: "geen-log" }; }
  const rood = lees(tekst);
  if (!rood.length) return { status: "niets-roods" };
  let h = {};
  try { h = JSON.parse(fs.readFileSync(hartPad, "utf8")); } catch (e) { h = {}; }
  h.poortRood = rood;
  /* En in de reden zelf, want dat is het veld dat mensen lezen. De categorie blijft staan (die zegt
     wat er met de push is gebeurd) en de diagnose komt erachter. */
  const kort = rood.map(x => x.suite + (x.regels[0] ? ": " + x.regels[0] : "")).join(" · ");
  h.poortReden = kort;
  fs.writeFileSync(hartPad, JSON.stringify(h, null, 1) + "\n");
  return { status: "geschreven", suites: rood.length, kort };
}

/* ---------------------------------------------------------------- zelftest ----
   Met een echt poortlogboek van de nacht van 5 september, want een verzonnen formaat bewijst
   alleen dat de functie zichzelf begrijpt. */
const PROEFLOG = [
  "poort :: 153 suites, 2 tegelijk",
  "",
  "  groen  pw-taal.js                4s",
  "  ROOD   pw-lesgat.js              2s",
  "",
  "================ wat er rood is ================",
  "",
  "--- pw-lesgat.js ---",
  "  ✗ het aantal onverklaarde kaarten loopt niet op (1 van maximaal 0)",
  "",
  "152/153 groen, 971s rekentijd",
  "POORT DICHT: pw-lesgat.js"
].join("\n");

function zelftest() {
  let fout = 0;
  function ok(c, m) { if (!c) { fout++; console.log("  ✗ " + m); } else console.log("  ✓ " + m); }

  const tmp = fs.mkdtempSync(path.join(require("os").tmpdir(), "hartpoort-"));
  const logPad = path.join(tmp, "poort.log");
  const hartPad = path.join(tmp, "hart.json");

  // 1. het echte formaat van 5 september
  fs.writeFileSync(logPad, PROEFLOG);
  fs.writeFileSync(hartPad, JSON.stringify({ reden: "iets", gelukt: false }));
  const r = schrijf(logPad, hartPad);
  const h = JSON.parse(fs.readFileSync(hartPad, "utf8"));
  ok(r.status === "geschreven" && h.poortRood && h.poortRood.length === 1,
    "de rode suite komt in de hartslag");
  ok(h.poortRood[0].suite === "pw-lesgat.js", "met zijn naam (" + (h.poortRood[0] || {}).suite + ")");
  ok(/onverklaarde kaarten/.test((h.poortRood[0].regels || [])[0] || ""),
    "en met de regel die afging (\"" + ((h.poortRood[0].regels || [])[0] || "") + "\")");
  ok(/pw-lesgat/.test(h.poortReden || ""), "en in één regel die je zo kunt lezen");
  ok(h.reden === "iets", "CONTROLE: de rest van de hartslag blijft staan");

  // 2. de FAIL-vorm van de playwright-suites telt ook mee
  fs.writeFileSync(logPad, ["--- pw-leermachine.js ---", "FAIL en bovenaan staat de fout van net", ""].join("\n"));
  fs.writeFileSync(hartPad, "{}");
  schrijf(logPad, hartPad);
  const h2 = JSON.parse(fs.readFileSync(hartPad, "utf8"));
  ok(h2.poortRood && h2.poortRood[0] && /bovenaan staat de fout/.test((h2.poortRood[0].regels || [])[0] || ""),
    "ook een suite die FAIL print in plaats van een kruisje");

  // 3. nul is geen bericht: een groene poort schrijft niets
  fs.writeFileSync(logPad, ["poort :: 153 suites", "153/153 groen, 900s rekentijd", "POORT OPEN"].join("\n"));
  fs.writeFileSync(hartPad, JSON.stringify({ reden: "niets aan de hand" }));
  const g = schrijf(logPad, hartPad);
  const h3 = JSON.parse(fs.readFileSync(hartPad, "utf8"));
  ok(g.status === "niets-roods" && !h3.poortRood,
    "CONTROLE: een groene poort zet geen leeg veld neer");

  // 4. geen logboek is geen klapper
  ok(schrijf(path.join(tmp, "bestaat-niet.log"), hartPad).status === "geen-log",
    "CONTROLE: een ontbrekend logboek levert geen uitzondering op");

  try { fs.rmSync(tmp, { recursive: true, force: true }); } catch (e) {}
  if (fout) { console.log("\n" + fout + " fout"); process.exit(1); }
  console.log("\nzelftest hartslag-poort: alles goed");
}

if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.indexOf("--zelftest") !== -1) { zelftest(); process.exit(0); }
  const logPad = args[0];
  if (!logPad) { console.error("gebruik: node tools/hartslag-poort.js <poort.log> [hartslag]"); process.exit(1); }
  const r = schrijf(logPad, args[1] || HART);
  console.log("hartslag-poort :: " + r.status + (r.kort ? " :: " + r.kort : ""));
  process.exit(0);
}

module.exports = { lees, schrijf };
