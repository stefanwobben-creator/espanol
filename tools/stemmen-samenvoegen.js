#!/usr/bin/env node
/*
 * stemmen-samenvoegen.js (23 aug, v23.179) - het manifest van deze run bij dat van main leggen.
 *
 * WAAROM DIT BESTAAT
 *
 * De workflowstap die de opnames publiceert doet `git checkout FETCH_HEAD -- audio`, zodat een
 * re-run niet met zijn eigen eerdere push gaat vechten. Voor de mp3's klopt dat: die staan niet op
 * main, dus die blijven staan. Voor audio/stemmen.json niet: dat bestand stáát op main, dus het werd
 * teruggezet en daarmee was de administratie van wat deze run zojuist insprak weg.
 *
 * Gemeten op 23 augustus: 102 mp3's op schijf zonder regel in het manifest. Elke nacht zag de
 * audiostap dezelfde 102 als "onbekende stem", sprak ze opnieuw in, en gooide de administratie
 * opnieuw weg. Toen het aantal boven de alarmgrens van 80 kwam, werd er helemaal niets meer
 * ingesproken. Een lus die zichzelf voedt en daarna zichzelf blokkeert.
 *
 * DE SAMENVOEGREGEL, EN WAAROM DIE ZO IS
 *
 * Wat op main staat wint. Dat lijkt achterstevoren, want onze regels zijn nieuwer. Het klopt toch,
 * en de reden is de checkout zelf: die zet main's mp3 over de onze heen voor elk bestand dat main
 * ook heeft. Voor zo'n bestand is main's regel de juiste beschrijving van de mp3 die er nu ligt.
 * Alleen waar main geen regel heeft, ligt er een bestand van ons, en daar vullen we aan.
 *
 * Dit script raakt `standaard` niet aan als main die al heeft: welke stem een groep heeft is een
 * besluit, geen waarneming, en dat besluit hoort niet per nacht te verschuiven.
 *
 * GEBRUIK
 *     node tools/stemmen-samenvoegen.js <pad-naar-het-manifest-van-deze-run>
 *
 * Ontbreekt dat bestand, dan gebeurt er niets en is dat geen fout: dan heeft deze run niets
 * ingesproken.
 */
const fs = require("fs");
const path = require("path");

const MANIFEST = path.join(__dirname, "..", "audio", "stemmen.json");
const MIJN = process.argv[2];

function lees(p) {
  try { return JSON.parse(fs.readFileSync(p, "utf8")); } catch (e) { return null; }
}

function samenvoegen(pad, stil, manifest) {
  const mijn = pad ? lees(pad) : null;
  if (!mijn) {
    if (!stil) console.log("stemmen-samenvoegen: niets van deze run om samen te voegen");
    return 0;
  }
  const doel = manifest || MANIFEST;
  const opMain = lees(doel) || {};
  let erbij = 0;
  const groepen = new Set(Object.keys(mijn).concat(Object.keys(opMain)));
  groepen.delete("standaard");
  groepen.forEach(g => {
    const a = opMain[g] || {}, b = mijn[g] || {};
    Object.keys(b).forEach(id => {
      if (a[id]) return;            // main heeft een regel: die hoort bij de mp3 die er nu ligt
      a[id] = b[id];
      erbij++;
    });
    opMain[g] = a;
  });
  /* standaard: alleen aanvullen, nooit overschrijven. Welke stem een groep heeft is een besluit,
     geen waarneming, en een besluit hoort niet per nacht te verschuiven. */
  opMain.standaard = opMain.standaard || {};
  Object.keys(mijn.standaard || {}).forEach(g => {
    if (!opMain.standaard[g]) { opMain.standaard[g] = mijn.standaard[g]; erbij++; }
  });
  if (!erbij) {
    if (!stil) console.log("stemmen-samenvoegen: niets toe te voegen, het manifest liep al gelijk");
    return 0;
  }
  fs.writeFileSync(doel, JSON.stringify(opMain, null, 2) + "\n");
  if (!stil) console.log("stemmen-samenvoegen: " + erbij + " regel(s) van deze run bewaard in audio/stemmen.json");
  return 0;
}

/* ---------- zelftest ----------
   Op een KOPIE in een tijdelijke map. De eerste versie hiervan werkte op audio/stemmen.json zelf en
   zette hem aan het eind "terug" met JSON.stringify zonder inspringing: 2197 regels verschil in git,
   uit een test die zei dat alles goed was. Een controle die de werkelijkheid aanraakt is geen
   controle maar een tweede bewerking.

   Drie gevallen, en het middelste is het controlegeval: dit script is triviaal groen te maken door
   altijd alles van deze run over te nemen, en dan overschrijft het de regel die hoort bij de mp3 die
   de checkout net heeft teruggezet. */
if (process.argv.includes("--zelftest")) {
  const os = require("os");
  const werk = fs.mkdtempSync(path.join(os.tmpdir(), "stemmen-"));
  const kopie = path.join(werk, "manifest.json");
  const echt = lees(MANIFEST) || { standaard: { dictado: "x" }, dictado: { s1: { hash: "a" }, s2: { hash: "b" } } };
  const bewaard = JSON.stringify(echt);
  const voorGit = fs.existsSync(MANIFEST) ? fs.readFileSync(MANIFEST, "utf8") : null;
  let mis = 0;
  const proef = (goed, wat) => { console.log((goed ? "  ok   " : "  FOUT ") + wat); if (!goed) mis++; };
  const eenId = Object.keys(echt.dictado || {})[0];

  // 1. main mist twee regels die deze run wel heeft
  const zonder = JSON.parse(bewaard);
  const missen = Object.keys(zonder.dictado).slice(-2);
  missen.forEach(id => delete zonder.dictado[id]);
  fs.writeFileSync(kopie, JSON.stringify(zonder, null, 2));
  fs.writeFileSync(path.join(werk, "mijn.json"), bewaard);
  samenvoegen(path.join(werk, "mijn.json"), true, kopie);
  let na = lees(kopie);
  proef(missen.every(id => !!na.dictado[id]), "de regels van deze run worden bewaard (" + missen.join(", ") + ")");

  // 2. HET CONTROLEGEVAL: main wint waar main al een regel heeft
  const vanMain = JSON.parse(bewaard); vanMain.dictado[eenId].hash = "VAN_MAIN";
  const vanRun = JSON.parse(bewaard); vanRun.dictado[eenId].hash = "VAN_DEZE_RUN";
  fs.writeFileSync(kopie, JSON.stringify(vanMain, null, 2));
  fs.writeFileSync(path.join(werk, "mijn2.json"), JSON.stringify(vanRun));
  samenvoegen(path.join(werk, "mijn2.json"), true, kopie);
  na = lees(kopie);
  proef(na.dictado[eenId].hash === "VAN_MAIN",
    "CONTROLE: main wint waar main al een regel heeft (nu: " + na.dictado[eenId].hash + ")");

  // 3. geen bestand van deze run is geen fout
  proef(samenvoegen(path.join(werk, "bestaat-niet.json"), true, kopie) === 0,
    "een ontbrekend runmanifest is geen fout");

  // 4. en het echte manifest is niet aangeraakt
  const naGit = fs.existsSync(MANIFEST) ? fs.readFileSync(MANIFEST, "utf8") : null;
  proef(naGit === voorGit, "CONTROLE: audio/stemmen.json is geen byte veranderd door deze test");

  console.log(mis ? "\nsamenvoegen: " + mis + " fout" : "\nsamenvoegen: alles goed");
  process.exit(mis ? 1 : 0);
}

process.exit(samenvoegen(MIJN, false));
