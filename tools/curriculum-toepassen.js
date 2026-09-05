#!/usr/bin/env node
// curriculum-toepassen.js (5 sep, v23.239) — de lading van de nacht op VERSE main leggen.
//
// WAAROM DIT BESTAAT
//
// Stefan, 5 september: "nee het mag autonoom live gaan."
//
// Dat mag pas als de laatste stap klopt, en die klopte niet. De stap "Reparatie direct live" deed
// dit:
//
//     git add index.html versie.txt ... && git commit && git push
//
// Die index.html is de main van het moment dat de run begon, plús wat de bot erbij schreef. En op
// deze main publiceren drie schrijvers: de logboek-Action (die GitHub steeds later inplant, van
// 02:30 naar 13:01), de avondrun zelf, en Stefan. Verschuift main tijdens het venster van de
// avondrun, dan gebeurt er één van twee dingen:
//
//   - de push wordt geweigerd en de nacht valt weg (dat is wat er nu gebeurt, en het is de
//     veilige helft);
//   - of iemand "repareert" dat door het bestand op verse main te kopiëren, en dan verdwijnt alles
//     wat er tussendoor op main is gezet, zonder dat iemand het ziet.
//
// De hartslagstap heeft die reparatie op 31 augustus al gekregen (avondrun-leveren.sh: verse main
// pakken, bestanden erop, opnieuw bij een botsing). Alleen mag je dat trucje niet op index.html
// toepassen, want die is niet van de avondrun alleen. Wat de avondrun eraan toevoegde wél.
//
// DUS: NIET HET BESTAND AFLEVEREN MAAR DE LADING
//
// Dit is dezelfde keuze als bij tools/nachtpatch.py van 3 september: wat de nacht maakt is geen
// bestand maar een stapelbare toevoeging. Deze aanroep legt de zinnen en toetsjes van vannacht op
// de index.html die er op dat moment ligt, wat die ook is.
//
// EN DE VERSIE WORDT PAS DAN GEKOZEN
//
// pasToe() hoogt APP_VERSIE op vanaf wat het in het bestand vindt. Doe je dat aan het begin van de
// nacht, dan kies je een nummer op grond van een main die er straks niet meer is. Vannacht liep dat
// zo: de avondrun stond op v23.237 terwijl er hier v23.236, v23.237 en v23.238 werden gemaakt. Twee
// schrijvers die uit dezelfde teller nummers uitdelen, en niets dat dat merkt.
//
// Door de lading pas op verse main toe te passen wordt het nummer als laatste gekozen, van wat er
// dan echt staat. Botsen kan dan niet meer: er is één plek waar het volgende nummer vandaan komt en
// dat is het bestand zelf, op het moment van publiceren.
//
// GEBRUIK
//
//   node tools/curriculum-toepassen.js [pad]     lading toepassen (standaard tools/curriculum-lading.json)
//   node tools/curriculum-toepassen.js --zelftest
//
// Eindigt op 0 als het is toegepast, op 2 als er niets te doen viel (lege of ontbrekende lading, en
// dat is geen fout: niet elke nacht levert iets), en op 1 als de lading is afgekeurd. Die derde
// uitkomst is het hele punt van deze stap: dezelfde controles van content-lib draaien opnieuw, nu
// tegen de main waarop het écht terechtkomt. Een id dat vanochtend nog vrij was kan inmiddels
// vergeven zijn, en dan hoort dit hier te stranden en niet op de site.
const fs = require("fs");
const path = require("path");

const LADING = path.join(__dirname, "curriculum-lading.json");

function lees(pad) {
  let ruw;
  try {
    ruw = fs.readFileSync(pad, "utf8");
  } catch (e) {
    return null;
  }
  let d;
  try {
    d = JSON.parse(ruw);
  } catch (e) {
    throw new Error("de lading is geen leesbare JSON: " + (e && e.message));
  }
  return d;
}

/* Wat pasToe() verwacht. De lading wordt geschreven door curriculum.js en heeft precies deze vorm,
   maar een bestand op schijf is data en geen belofte: een ontbrekende sleutel hoort hier een lege
   lijst te worden en geen uitzondering drie functies verderop. */
function normaliseer(d) {
  const uit = {
    words: (d && d.words) || [],
    sentences: (d && d.sentences) || [],
    quizzes: (d && d.quizzes) || [],
    cheat: (d && d.cheat) || [],
    lessen: (d && d.lessen) || {},
    nieuweLessen: (d && d.nieuweLessen) || []
  };
  return uit;
}

function leeg(l) {
  return !l.words.length && !l.sentences.length && !l.quizzes.length &&
         !l.cheat.length && !l.nieuweLessen.length && !Object.keys(l.lessen).length;
}

function toepassen(pad, opties) {
  opties = opties || {};
  const lib = require("./content-lib.js");
  const d = lees(pad);
  if (d === null) return { status: "niets", reden: "er ligt geen lading op " + pad };
  const lading = normaliseer(d.reparatie && d.reparatie.sentences ? d.reparatie : d);
  if (leeg(lading)) return { status: "niets", reden: "de lading is leeg" };

  const res = lib.pasToe(lading, { droog: !!opties.droog });
  if (!res.ok) return { status: "afgekeurd", fouten: res.fouten, waarschuwingen: res.waarschuwingen };
  return {
    status: "toegepast",
    versie: res.versie,
    aantallen: {
      zinnen: lading.sentences.length,
      toetsjes: lading.quizzes.length,
      woorden: lading.words.length
    },
    waarschuwingen: res.waarschuwingen
  };
}

/* ---------------------------------------------------------------- zelftest ----
   Vier gevallen, en drie ervan zijn er om te bewijzen dat deze stap kán stranden. Een
   publicatiestap die alles doorlaat is geen stap. */
function zelftest() {
  let fout = 0;
  function ok(c, m) { if (!c) { fout++; console.log("  ✗ " + m); } else console.log("  ✓ " + m); }

  const tmp = fs.mkdtempSync(path.join(require("os").tmpdir(), "lading-"));

  // 1. geen bestand: geen fout, gewoon niets te doen
  const geen = toepassen(path.join(tmp, "bestaat-niet.json"));
  ok(geen.status === "niets", "een ontbrekende lading is geen fout maar niets te doen");

  // 2. een leeg blok: idem
  const legePad = path.join(tmp, "leeg.json");
  fs.writeFileSync(legePad, JSON.stringify({ sentences: [], quizzes: [] }));
  ok(toepassen(legePad).status === "niets", "een lege lading levert niets te doen op");

  // 3. onleesbaar: dat is wél een fout, en hij hoort hier op te vallen
  const stukPad = path.join(tmp, "stuk.json");
  fs.writeFileSync(stukPad, "{dit is geen json");
  let stuk = null;
  try { toepassen(stukPad); } catch (e) { stuk = e.message; }
  ok(!!stuk && /leesbare JSON/.test(stuk), "een onleesbare lading valt op in plaats van stil door te gaan");

  // 4. een zin die niet deugt hoort afgekeurd te worden, droog, zonder iets te schrijven
  const slechtPad = path.join(tmp, "slecht.json");
  fs.writeFileSync(slechtPad, JSON.stringify({
    sentences: [{ id: "s1", lvl: 2, nl: "x", en: "x", es: "x", alt: ["x"], uitleg: "x", ue: "x", tag: "t" }],
    quizzes: []
  }));
  const slecht = toepassen(slechtPad, { droog: true });
  ok(slecht.status === "afgekeurd",
    "een id dat al bestaat wordt afgekeurd, ook als hij vanochtend nog vrij was" +
      (slecht.status === "afgekeurd" ? " (" + (slecht.fouten || [])[0] + ")" : " — kreeg: " + slecht.status));

  // 5. en de goede weg: een verse id, droog toegepast, met een versie erbij
  const lib = require("./content-lib.js");
  const inv = lib.inventaris();
  const versId = lib.volgendeId(inv.sentences, "s")(1);
  const goedPad = path.join(tmp, "goed.json");
  fs.writeFileSync(goedPad, JSON.stringify({
    sentences: [{ id: versId, lvl: 2, nl: "Dit is een test.", en: "This is a test.",
                  es: "Esto es una prueba.", alt: ["esto es una prueba"],
                  uitleg: "Una prueba = een test. Esto verwijst naar iets dat je aanwijst.",
                  ue: "Una prueba = a test. Esto refers to something you point at.",
                  tag: "zelftest" }],
    quizzes: []
  }));
  const goed = toepassen(goedPad, { droog: true });
  ok(goed.status === "toegepast",
    "een verse lading wordt toegepast" + (goed.status === "toegepast" ? " → " + goed.versie
      : " — kreeg: " + goed.status + " " + JSON.stringify(goed.fouten || [])));
  ok(goed.status === "toegepast" && /^v\d+\.\d+$/.test(goed.versie || ""),
    "en het versienummer komt uit het bestand dat er op dát moment ligt (" + goed.versie + ")");

  // 6. en er is niets echt weggeschreven: droog is droog
  const na = lib.inventaris();
  ok(na.sentences.length === inv.sentences.length,
    "CONTROLE: droog schrijft niets weg (" + inv.sentences.length + " zinnen, nog steeds " + na.sentences.length + ")");

  try { fs.rmSync(tmp, { recursive: true, force: true }); } catch (e) {}
  if (fout) { console.log("\n" + fout + " fout"); process.exit(1); }
  console.log("\nzelftest curriculum-toepassen: alles goed");
}

if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.indexOf("--zelftest") !== -1) { zelftest(); process.exit(0); }
  const pad = args.filter(a => a.indexOf("--") !== 0)[0] || LADING;
  const droog = args.indexOf("--droog") !== -1;
  let res;
  try {
    res = toepassen(pad, { droog });
  } catch (e) {
    console.error("de lading kon niet worden gelezen: " + (e && e.message));
    process.exit(1);
  }
  if (res.status === "niets") { console.log("niets toe te passen: " + res.reden); process.exit(2); }
  if (res.status === "afgekeurd") {
    console.error("AFGEKEURD op verse main:\n - " + (res.fouten || []).join("\n - "));
    process.exit(1);
  }
  (res.waarschuwingen || []).forEach(w => console.log("let op: " + w));
  console.log("toegepast op verse main: " + res.aantallen.zinnen + " zinnen, " +
    res.aantallen.toetsjes + " toetsjes → " + res.versie);
  process.exit(0);
}

module.exports = { toepassen, normaliseer, leeg };
