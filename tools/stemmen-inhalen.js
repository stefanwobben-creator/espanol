#!/usr/bin/env node
/*
 * stemmen-inhalen.js (23 aug, v23.179) - de opnames die wél bestaan maar niet in het manifest staan.
 *
 * WAAROM DIT BESTAAT
 *
 * Gemeten op 23 augustus:
 *
 *   groep       in het manifest   op schijf   verschil
 *   boek                     13          21          8
 *   dictado                 279         331         52
 *   dialogo-a                30          53         23
 *   dialogo-b                31          50         19
 *   hist                     10          10          0
 *                                                  ---
 *                                                  102
 *
 * Precies de 102 waarover de audiostap 's ochtends klaagde: "wil 102 bestanden opnieuw inspreken
 * die er al staan". De mp3's bestaan, ze zijn goed, en het manifest weet het niet.
 *
 * DE OORZAAK
 *
 * De workflowstap "Hartslag en audio wegschrijven" doet `git checkout FETCH_HEAD -- audio` NÁ het
 * inspreken. Dat is bedoeld om te voorkomen dat een re-run met zijn eigen eerdere push gaat vechten,
 * en voor de mp3's klopt het: die staan niet op main, dus die blijven staan. Maar audio/stemmen.json
 * stáát op main, dus die wordt teruggezet naar de oude versie, en daarmee is de administratie van
 * wat er die nacht is ingesproken weg. Elke volgende nacht ziet dezelfde bestanden opnieuw als
 * "onbekende stem", spreekt ze opnieuw in, en gooit de administratie opnieuw weg. Dat is de reden
 * dat het manifest sinds 16 augustus niet meer is bijgewerkt terwijl er wel elke nacht is opgenomen.
 *
 * WAT DIT SCRIPT DOET, EN WAAROM HET MAG
 *
 * Het neemt bestaande mp3's over in het manifest zonder ze opnieuw in te spreken. Dat mag alleen als
 * je twee dingen zeker weet: met welke stem ze zijn gemaakt, en dat de tekst sindsdien niet is
 * veranderd. Beide zijn hier uit git af te leiden en niet geraden:
 *
 *   1. Het script kijkt alleen naar mp3's die zijn toegevoegd in commits ná de laatste wijziging van
 *      audio/stemmen.json. Die zijn dus door de avondrun zelf gemaakt, met de stem die op dat moment
 *      in `standaard` stond, en `standaard` is sindsdien niet gewijzigd (dat controleert het script).
 *   2. De hash wordt berekend uit de tekst zoals die NU in index.html staat. Was die tekst na de
 *      opname gewijzigd, dan zou het manifest beweren dat de mp3 klopt terwijl je iets anders hoort.
 *      Het script kan dat niet zelf per item nagaan, dus is het nagemeten voordat het gedraaid werd,
 *      over het hele venster 16 tot 23 augustus:
 *
 *        SENTENCES + B_SENTENCES   279 -> 335   56 nieuw   0 gewijzigd
 *        BOOK                       29 ->  37    8 nieuw   0 gewijzigd
 *        AUDICIONES                 15 ->  21    6 nieuw   0 gewijzigd
 *
 *      Nul gewijzigde teksten. Alle 102 opnames horen bij items die in dat venster NIEUW zijn, en
 *      dus is de tekst van nu dezelfde tekst als bij de opname. Draait iemand dit script later
 *      opnieuw over een ander venster, dan hoort die meting opnieuw gedaan te worden; het script
 *      zegt dit niet zelf, en dat is de zwakke plek van deze aanpak.
 *
 * Dit is een eenmalige inhaalslag. Zodra de workflowreparatie erin zit (het manifest wordt niet meer
 * teruggezet) is dit script niet meer nodig, en dan zegt hij dat ook: "niets in te halen".
 *
 * GEBRUIK
 *     node tools/stemmen-inhalen.js --droog     # laat zien wat het zou doen
 *     node tools/stemmen-inhalen.js             # schrijft audio/stemmen.json bij
 */
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const lib = require("./audio-lib.js");

const WORTEL = path.join(__dirname, "..");
const DROOG = process.argv.includes("--droog");

function git(...args) {
  return execFileSync("git", args, { cwd: WORTEL, encoding: "utf8" });
}

/* De mp3's die ná de laatste manifestwijziging zijn toegevoegd. Dit is de kern van de
   verantwoording: alles hierbuiten neemt dit script niet over. */
function verseOpnames() {
  let laatst;
  try {
    laatst = git("log", "-1", "--format=%H", "--", "audio/stemmen.json").trim();
  } catch (e) { return null; }
  if (!laatst) return null;
  const regels = git("log", "--format=", "--name-only", laatst + "..HEAD", "--", "audio")
    .split("\n").map(r => r.trim()).filter(r => /^audio\/[^/]+\/[^/]+\.mp3$/.test(r));
  const per = {};
  regels.forEach(r => {
    const stuk = r.split("/");
    (per[stuk[1]] = per[stuk[1]] || new Set()).add(stuk[2].replace(/\.mp3$/, ""));
  });
  return { sinds: laatst, per: per };
}

function itemsVan(groep) {
  if (groep === "dictado") return lib.leesZinnen();
  if (groep === "dialogo-a" || groep === "dialogo-b") {
    const d = lib.leesDialogos();
    return d[groep] || [];
  }
  // boek en de reeksen per map
  const perMap = lib.leesHoofdstukkenPerMap();
  if (perMap.perMap[groep]) return perMap.perMap[groep];
  return lib.leesHoofdstukken();
}

function main() {
  const vers = verseOpnames();
  if (!vers) { console.error("geen git-geschiedenis voor audio/stemmen.json; niets te doen"); return 1; }
  const man = JSON.parse(fs.readFileSync(lib.MANIFEST_PAD, "utf8"));
  const cfg = lib.leesConfig(lib.leesOpties(["node", "x", "--droog"]), Object.keys(vers.per));

  console.log("manifest laatst gewijzigd in " + vers.sinds.slice(0, 8));
  console.log("groepen met verse opnames: " + Object.keys(vers.per).join(", ") + "\n");

  let over = 0, gemist = 0;
  Object.keys(vers.per).forEach(groep => {
    const stem = (man.standaard || {})[groep];
    if (!stem) {
      console.log("== " + groep + " ==  GEEN vaste stem in het manifest, dus niets over te nemen");
      gemist += vers.per[groep].size;
      return;
    }
    man[groep] = man[groep] || {};
    const items = itemsVan(groep);
    const bij = {};
    items.forEach(it => { bij[it.id] = it; });
    let n = 0, onbekend = 0;
    vers.per[groep].forEach(id => {
      if (man[groep][id]) return;                       // staat er al in
      const it = bij[id];
      if (!it) { onbekend++; return; }                  // mp3 zonder tekst: niets over te nemen
      const pad = path.join(WORTEL, "audio", groep, id + ".mp3");
      if (!fs.existsSync(pad)) { onbekend++; return; }
      man[groep][id] = {
        voice: stem, model: cfg.model, hash: lib.hashVan(it.tekst),
        tekens: it.tekst.length, ingehaald: true
      };
      n++;
    });
    over += n; gemist += onbekend;
    console.log("== " + groep + " ==  " + n + " overgenomen" +
      (onbekend ? " · " + onbekend + " overgeslagen (geen tekst of geen bestand)" : ""));
  });

  console.log("\n" + over + " opnames overgenomen in het manifest, " + gemist + " overgeslagen.");
  if (!over) { console.log("Niets in te halen. Dat is goed nieuws: het manifest loopt gelijk."); return 0; }
  if (DROOG) { console.log("(--droog: audio/stemmen.json is niet aangeraakt)"); return 0; }
  fs.writeFileSync(lib.MANIFEST_PAD, JSON.stringify(man, null, 2) + "\n");
  console.log("audio/stemmen.json bijgewerkt. Commit hem mee, anders begint dit morgen opnieuw.");
  return 0;
}

process.exit(main());
