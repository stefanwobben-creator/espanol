#!/usr/bin/env node
/*
 * curriculum.js — de avondrun die het leerpad onderhoudt.
 *
 * Stefans doel (3 augustus): binnen drie maanden stevig A2, daarna door naar B1, met elke dag een
 * afgestemde les. Twee dingen kunnen dat blokkeren: gaten (dingen die je blijft fout doen zonder dat
 * er genoeg oefenmateriaal voor is) en een leeg pad (geen nieuwe woorden meer op de plank). Deze run
 * kijkt elke nacht naar beide.
 *
 * Gekozen strategie (Stefan): eerst gaten dichten uit het foutenlog, en pas als er geen gaten meer
 * zijn een nieuw thema. Aanvullen van bestaande lessen gaat direct live; een compleet nieuwe les
 * (zeker op B1-niveau) komt als pull request, want dat is curriculum-uitbreiding en geen reparatie.
 *
 * Het foutenlog kent drie soorten fouten, en die vragen elk om ander materiaal:
 *   type "zin"/"dictado" → een taalverschijnsel (tag "costar", "indefinido") → extra oefenzinnen
 *   type "woord"         → losse woorden die niet blijven plakken → zinnen die díe woorden gebruiken
 *   type "quiz"          → een grammaticaregel → een nieuw toetsje bij dezelfde spiekbriefkaart
 * Ze door elkaar halen levert onzin op: "les6" is een woordgroep, geen grammaticaregel.
 *
 *   node tools/curriculum.js --analyse       alleen kijken en rapporteren (geen sleutel nodig)
 *   node tools/curriculum.js --droog         hele run, maar niets wegschrijven
 *   node tools/curriculum.js --stub          pijplijn testen met nepcontent (geen LLM)
 *   node tools/curriculum.js                 echt uitvoeren
 *   node tools/curriculum.js --nieuwe-les    het pad verlengen, ook als de voorraad nog niet krap is
 *   node tools/curriculum.js --max 3         hoogstens 3 gaten aanpakken (default 2)
 *
 * Wat de run NOOIT doet: een hand-geschreven lesregel aanpassen. Zie content-lib.js.
 */
"use strict";
const fs = require("fs");
const path = require("path");
const lib = require("./content-lib");

const LOGS = path.join(__dirname, "logs-latest.json");
const PLAN = path.join(__dirname, "curriculum-laatste.json");
const HART_PAD = path.join(__dirname, "avondrun-hart.json");   // elke nacht een regel, ook als er niets kwam

/* Wat de run vannacht deed, in een bestand. Zonder dit is de enige manier om te zien of de avondrun
   ooit iets heeft geleverd: commits van de bot tellen. Dat is geen meting, dat is archeologie. */
const HART = { staat: { wanneer: null, gelukt: false, ladder: null, voorraadDagen: null,
                        beloofd: null, geleverd: null, versie: null, klachten: [],
                        reden: "de run is niet afgemaakt" } };

/* Elke klacht ging naar stderr en daarmee naar een log dat niemand opent. Nu komt hij er ook in het
   bestand te staan, zonder dat er ergens anders in dit script iets voor hoeft te veranderen. */
const stderrEcht = console.error.bind(console);
console.error = function () {
  const regel = Array.prototype.map.call(arguments, a => (a && a.stack) ? a.message : String(a)).join(" ").trim();
  if (regel && HART.staat.klachten.length < 40) HART.staat.klachten.push(regel);
  stderrEcht.apply(console, arguments);
};
const VOORRAAD_DREMPEL_DAGEN = 14;   // minder dan twee weken nieuwe woorden op de plank? pad verlengen
const MAX_ZINNEN_PER_GAT = 4;        // kleine dagelijkse aanvullingen leveren betere content dan een dump

const args = process.argv.slice(2);
const heeft = v => args.includes(v);
const getal = (v, d) => { const i = args.indexOf(v); return i >= 0 ? +args[i + 1] : d; };
const OPT = { analyse: heeft("--analyse"), droog: heeft("--droog"), stub: heeft("--stub"),
              nieuweLes: heeft("--nieuwe-les"), max: getal("--max", 2) };

/* ================= 1. analyse ================= */

function leesLogs() {
  if (!fs.existsSync(LOGS)) return { logs: [], profielen: [] };
  try { return JSON.parse(fs.readFileSync(LOGS, "utf8")); } catch (e) { return { logs: [], profielen: [] }; }
}

// Elke dagdoel-log stuurt de héle foutenmap mee, dus dezelfde fout staat in meerdere logregels.
// We nemen per item de hoogste stand in plaats van alles op te tellen.
function foutenSamenvatten(logboek) {
  const perItem = {};
  (logboek.logs || []).forEach(l => {
    const f = (l.payload && l.payload.fouten) || {};
    Object.keys(f).forEach(k => {
      const e = f[k];
      if (!e || !e.type) return;
      const b = perItem[k];
      if (!b || (e.count || 0) > b.count) perItem[k] = { id: e.id, type: e.type, tag: e.tag || "", count: e.count || 0 };
    });
  });
  return Object.values(perItem);
}

function groepeer(items, sleutel) {
  const uit = {};
  items.forEach(it => {
    const k = sleutel(it);
    if (!k) return;
    const g = uit[k] || (uit[k] = { sleutel: k, fouten: 0, items: [] });
    g.fouten += it.count;
    g.items.push(it);
  });
  return Object.values(uit);
}

/* Wanneer is een onderwerp verzadigd? Als er al ruim materiaal ligt én er ruim materiaal is per
   verse fout. Twee eisen, want één is te grof: een onderwerp met twee zinnen en één fout haalt de
   verhouding wel maar heeft alsnog te weinig om mee te oefenen. */
const VERZADIGD_ZINNEN = 10;      // zoveel oefenzinnen liggen er al
const VERZADIGD_PER_FOUT = 3;     // en zoveel per verse fout
/* Delen door het aantal oefenzinnen geeft rare uitschieters zodra dat aantal klein is: een
   onderwerp met één zin en drie fouten kwam boven een onderwerp met zes zinnen en zeventien fouten.
   Vandaar een demping in de noemer. Twee is geen magisch getal, het is "doe alsof er altijd al een
   paar zinnen liggen", en dat haalt de scherpste rand van de deling af. */
const DEMPING = 2;

function verzadigd(g) {
  return g.zinnen >= VERZADIGD_ZINNEN && g.zinnen / Math.max(1, g.fouten) >= VERZADIGD_PER_FOUT;
}

function analyseer(logboek, inv) {
  const fouten = foutenSamenvatten(logboek);
  const zinnenPerTag = {};
  inv.sentences.forEach(s => { zinnenPerTag[s.tag] = (zinnenPerTag[s.tag] || 0) + 1; });

  // (a) taalverschijnselen: fouten op zinnen en dictado, gewogen tegen hoeveel oefenzinnen er al zijn
  const zinGaten = groepeer(fouten.filter(f => f.type === "zin" || f.type === "dictado"), f => f.tag)
    .map(g => {
      const zinnen = zinnenPerTag[g.sleutel] || 0;
      return { soort: "verschijnsel", tag: g.sleutel, fouten: g.fouten, items: g.items.length,
               zinnen, score: g.fouten / (zinnen + DEMPING) };
    })
    .filter(g => g.fouten >= 2 && g.tag)
    .sort((a, b) => b.score - a.score);

  // (b) losse woorden die niet blijven plakken: die verdienen zinnen waarin ze voorkomen
  const woordGaten = groepeer(fouten.filter(f => f.type === "woord"), f => f.tag)
    .map(g => {
      const woorden = g.items.map(i => inv.words.find(w => w.id === i.id)).filter(Boolean);
      return { soort: "woorden", tag: g.sleutel, fouten: g.fouten, items: g.items.length, woorden,
               zinnen: zinnenPerTag[g.sleutel] || 0, score: g.fouten / Math.max(1, g.items.length) };
    })
    .filter(g => g.woorden.length >= 2)
    .sort((a, b) => b.fouten - a.fouten);

  // (c) grammatica-toetsjes waar je op blijft struikelen: een nieuw toetsje bij dezelfde spiekkaart
  const toetsGaten = groepeer(fouten.filter(f => f.type === "quiz"), f => f.tag)
    .map(g => {
      const qz = inv.quizzes.find(q => q.id === g.sleutel);
      return { soort: "toets", tag: g.sleutel, fouten: g.fouten, items: g.items.length,
               spiek: qz ? qz.spiek : null, titel: qz ? qz.titel : null, score: g.fouten / Math.max(1, g.items.length) };
    })
    .filter(g => g.spiek && g.spiek.length)
    .sort((a, b) => b.fouten - a.fouten);

  /* Eerst kijken of er al genoeg ligt, dan pas maken. De overgeslagen onderwerpen blijven wel in
     het rapport staan: "er is niets te doen" en "hier lag al genoeg" zijn niet hetzelfde, en dat
     verschil hoort zichtbaar te zijn. */
  const vol = zinGaten.filter(verzadigd).concat(woordGaten.filter(verzadigd));
  return { zinGaten: zinGaten.filter(g => !verzadigd(g)),
           woordGaten: woordGaten.filter(g => !verzadigd(g)),
           toetsGaten, verzadigd: vol };
}

// Hoeveel dagen nieuwe woorden liggen er nog op de plank? De app stuurt geleerd/minuten mee in het
// logboek (zie logServer), dus dit is een meting en geen aanname. Boekwoorden (tag boek-N) horen
// bewust bij geen enkele les: die komen binnen zodra je een hoofdstuk uitleest.
function voorraad(logboek, inv) {
  const inPad = new Set();
  inv.perLes.forEach(l => l.words.forEach(id => inPad.add(id)));
  const boekWoorden = inv.words.filter(w => /^boek-\d+$/.test(w.tag || "")).length;
  const totaal = inPad.size;
  const perProfiel = {};
  (logboek.logs || []).forEach(l => {
    const p = l.payload || {};
    if (p.geleerd === undefined) return;
    const b = perProfiel[l.code];
    if (!b || l.created_at > b.wanneer) {
      perProfiel[l.code] = { geleerd: p.geleerd, minuten: p.minuten || 20, wanneer: l.created_at };
    }
  });
  const rijen = Object.keys(perProfiel).map(code => {
    const b = perProfiel[code];
    const nieuwPerDag = Math.max(2, Math.round((b.minuten || 20) * 0.65)); // zelfde formule als maxNieuw()
    const over = Math.max(0, totaal - b.geleerd);
    return { code, geleerd: b.geleerd, minuten: b.minuten, nieuwPerDag, over, dagen: Math.floor(over / nieuwPerDag) };
  }).sort((a, b) => a.dagen - b.dagen);
  return { totaalInPad: totaal, boekWoorden, profielen: rijen, krapsteDagen: rijen.length ? rijen[0].dagen : null };
}

function rapport(inv, an, vrd) {
  console.log("— inventaris —");
  console.log(`  ${inv.words.length} leswoorden · ${(inv.kern || []).length} kernwoorden (buiten de lessen) · ` +
              `${inv.sentences.length} zinnen · ${inv.quizzes.length} toetsjes · ${inv.cheat.length} spiekkaarten · ` +
              `${inv.perLes.length} lessen`);
  console.log(`  ${vrd.totaalInPad} woorden in het lespad, ${vrd.boekWoorden} via de boekhoofdstukken`);
  console.log("— voorraad —");
  if (!vrd.profielen.length) console.log("  nog geen profiel met voortgangsgegevens in het logboek (komt na de eerste les op de nieuwe versie)");
  vrd.profielen.forEach(p => console.log(
    `  ${p.code}: ${p.geleerd} geleerd · ${p.minuten} min/dag → ${p.nieuwPerDag} nieuw/dag → ${p.dagen} dagen voorraad`));
  console.log("— gaten uit het foutenlog —");
  const toon = (kop, rij, fmt) => {
    console.log(`  ${kop}: ${rij.length ? "" : "geen"}`);
    rij.slice(0, 6).forEach(g => console.log("    " + fmt(g)));
  };
  toon("taalverschijnselen", an.zinGaten, g => `${g.tag}: ${g.fouten} fouten · ${g.zinnen} oefenzinnen · score ${g.score.toFixed(1)}`);
  toon("woorden die niet plakken", an.woordGaten, g => `${g.tag}: ${g.fouten} fouten over ${g.items} woorden (${g.woorden.slice(0,4).map(w=>w.es).join(", ")}…)`);
  toon("grammatica-toetsjes", an.toetsGaten, g => `${g.tag} (${g.titel}): ${g.fouten} fouten · spiekkaart ${JSON.stringify(g.spiek)}`);
  if ((an.verzadigd || []).length) {
    console.log("  overgeslagen, hier ligt al genoeg:");
    an.verzadigd.forEach(g => console.log(
      `    ${g.tag}: ${g.fouten} fouten · ${g.zinnen} oefenzinnen · dat is ` +
      `${(g.zinnen / Math.max(1, g.fouten)).toFixed(1)} zin per fout, dus herhalen en niet bijmaken`));
  }
}

/* ================= 2. genereren ================= */

/* De ladder zit al in dit project — maar op de server, want daar liggen de sleutels (Render-env).
   Deze run draait op GitHub Actions, een andere machine. Dezelfde sleutels op een tweede plek zetten is
   vragen om een sleutel die niemand meer roteert, dus lenen we de server: POST /api/admin/llm met de
   ADMIN_KEY die er voor het logboek al is. Draai je de run op je eigen machine mét sleutels in de
   omgeving, dan pakt hij llm.js direct — dat is handig voor uitproberen zonder de server te storen. */
const API = process.env.VAMOS_API || "https://espanol-qbm8.onrender.com";

/* De ladder van de app staat op "goedkoop eerst, duur als vangnet", en dat klopt daar: elke actie van
   een leerling gaat er langs. Voor deze run klopt het niet. Hij doet tien aanroepen per etmaal en
   schrijft materiaal dat maanden blijft staan, dus hier gaat het beste model voorop en is goedkoop
   het vangnet. Een trede met een onbekende modelnaam levert een fout op en de ladder zakt door naar
   de volgende, dus deze lijst kan niet stuk; hij kan hoogstens duurder of goedkoper uitpakken.
   Overschrijven kan met AVONDRUN_LADDER, leegmaken zet hem terug op de gewone ladder van de app. */
const ZWARE_LADDER = process.env.AVONDRUN_LADDER !== undefined ? process.env.AVONDRUN_LADDER :
  "anthropic:claude-sonnet-4-5,gemini:gemini-2.5-pro,gemini:gemini-2.5-flash,anthropic:claude-haiku-4-5";

/* De reden waarom de ladder niet antwoordde. Stond eerst alleen in de logregels van een groene run,
   waar niemand hem las; nu gaat hij mee in de hartslag en in de exit. */
let LADDERFOUT = null;

function ladderLokaal() {
  const heeftSleutel = ["GEMINI_API_KEY", "GOOGLE_API_KEY", "MISTRAL_API_KEY", "ANTHROPIC_API_KEY",
                        "OPENAI_API_KEY", "OPENROUTER_API_KEY"].some(k => process.env[k]);
  if (!heeftSleutel) return null;
  try {
    const { reason } = require("../server/llm.js");
    return { bron: "llm.js (sleutel in je omgeving)",
             reason: (prompt, opts) => reason(prompt, Object.assign({ ladder: ZWARE_LADDER || null }, opts))
               .then(r => (r ? r.text : null)) };
  } catch (e) { console.error("server/llm.js niet te laden:", e.message); return null; }
}

function ladderViaServer() {
  const key = process.env.ADMIN_KEY;
  if (!key) return null;
  return {
    bron: "server (" + API + "/api/admin/llm)",
    reason: async (prompt, opts) => {
      const r = await fetch(API + "/api/admin/llm?key=" + encodeURIComponent(key), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, maxTokens: (opts && opts.maxTokens) || 4000, jsonMode: !!(opts && opts.jsonMode),
                               ladder: ZWARE_LADDER || undefined })
      });
      if (!r.ok) { LADDERFOUT = "server gaf " + r.status + " op /api/admin/llm"; console.error("  " + LADDERFOUT); return null; }
      const j = await r.json().catch(() => null);
      return j && j.ok ? j.tekst : null;
    }
  };
}

function llm() {
  const motor = ladderLokaal() || ladderViaServer();
  if (motor) console.log("  taalmodel via: " + motor.bron);
  else console.error("geen taalmodel bereikbaar: zet ADMIN_KEY (dan gaat het via de server) of een " +
                     "LLM-sleutel in je omgeving");
  return motor;
}

/* Eerst even kloppen. Een ladder die niet antwoordt leverde tot nu toe per gat een aparte, stille
   klacht halverwege het log; nu staat de status meteen bovenaan en stopt de run erop. */
async function ladderProef(motor) {
  let t = null;
  try { t = await motor.reason("Antwoord met precies het woord: ja", { maxTokens: 10 }); }
  catch (e) { LADDERFOUT = "de aanroep klapte: " + (e && e.message ? e.message : e); }
  if (t && String(t).trim()) return true;
  console.error("de LLM-ladder antwoordt niet" + (LADDERFOUT ? " (" + LADDERFOUT + ")" : "") +
                "; er valt vannacht dus niets te genereren");
  return false;
}

function haalJson(tekst) {
  if (!tekst) return null;
  const schoon = String(tekst).replace(/^```(?:json)?/im, "").replace(/```\s*$/m, "").trim();
  try { return JSON.parse(schoon); } catch (e) { /* verder proberen */ }
  const eerste = schoon.search(/[[{]/);
  const laatste = Math.max(schoon.lastIndexOf("]"), schoon.lastIndexOf("}"));
  if (eerste < 0 || laatste <= eerste) return null;
  try { return JSON.parse(schoon.slice(eerste, laatste + 1)); } catch (e) { return null; }
}

const VOORBEELD_ZIN = {
  id: "s999", lvl: 2, nl: "Het kost me moeite om snel te praten.", en: "Speaking fast is hard for me.",
  es: "Me cuesta hablar rápido.", alt: ["me cuesta hablar rapido"],
  uitleg: "Bij costar is het onderwerp de activiteit (hablar), dus enkelvoud: cuesta.",
  ue: "With costar the subject is the activity (hablar), so it is singular: cuesta.", tag: "costar"
};
const VOORBEELD_VRAAG = {
  q: "Me ___ aprender los verbos.", nl: "Het kost me moeite om de werkwoorden te leren.",
  ne: "It's hard for me to learn the verbs.", opts: ["cuesta", "cuestan"], c: 0,
  u: "Aprender is een infinitief. Eén activiteit = enkelvoud = cuesta.",
  ue: "Aprender is an infinitive. One activity = singular = cuesta."
};

/* ---------- de vorm van een woordkaart (14 aug, v23.101) ----------
   Op 14 augustus bleek van de 1376 Cervantes-woorden dat er 80 het Spaanse antwoord al op de
   Nederlandse kant hadden staan en 295 meerdere betekenissen op elkaar stapelden ("vinger; teen:
   dedo del pie"). Dat kwam niet door slordigheid maar door herkomst: in een frequentielijst is het
   nl-veld een woordenboekvertaling en hoort het alles te vermelden, op een kaart is het een vraag.

   Die kaarten zijn in v23.100 gesplitst in `nl` (één betekenis) en `meer` (de rest, zichtbaar pas ná
   het antwoord). Als de avondrun dat niet weet, levert hij vanaf vannacht weer de oude vorm en begint
   het opnieuw. Vandaar dit blok, en de twee regels in valideer() die hetzelfde machinaal afdwingen:
   dit is geen advies aan het model maar een harde eis. */
const WOORDVORM = `De vorm van een woordkaart (dit wordt machinaal gecontroleerd; een fout hier laat de
levering afkeuren):
- "nl" is de VRAAG, niet een woordenboekregel. Precies één betekenis, geen puntkomma's.
  Fout:  "vinger; teen: dedo del pie"
  Goed:  "de vinger", en dan "meer": "teen is el dedo del pie"
- "nl" en "en" mogen het Spaanse antwoord niet verklappen. Staat er een woord uit "es" in de
  Nederlandse of Engelse kant, dan is de kaart geen vraag meer.
  Fout:  es "pesar", nl "a pesar de = ondanks; wegen"
  Goed:  es "pesar", nl "wegen", meer: "a pesar de betekent ondanks"
  (Een leenwoord dat in beide talen hetzelfde is, zoals el virus / virus, mag uiteraard wel.)
- "meer" is optioneel en is tekst, geen lijst. Daar hoort wat interessant is maar niet gevraagd wordt:
  een tweede betekenis, een vaste uitdrukking, een valkuil. Eén korte zin, Nederlands. Laat het veld
  weg als er niets te melden valt.`;

const STIJL = `Stijl-eisen (belangrijk):
- Alledaags, natuurlijk Spaans zoals in Spanje gesproken wordt. Geen letterlijk vertaald Nederlands.
- De zin moet ergens over gaan. Iets wat een mens op een gewone dag tegen een ander zegt. Grammaticaal
  kloppen is niet genoeg: "Las mesas son tímidas" (de tafels zijn verlegen) en "Busco las casas" (ik
  zoek de huizen) zijn correct Spaans en toch onbruikbaar, want niemand zegt dat. Kies liever een
  saaie ware zin dan een grammaticaal keurige onzinzin.
- A2-woordenschat, korte zinnen, geen literaire constructies.
- "uitleg" legt in het Nederlands uit WAAROM het antwoord zo is: twee zinnen, concreet, met de vorm erin.
  Geen verwijzingen naar regelnummers of naar "de spiekbrief".
  Harde eis, machinaal gecontroleerd: de uitleg noemt een Spaans woord dat in de zin zelf staat, of
  de regel bij naam (subjuntivo, imperfecto, vrouwelijk meervoud, en zo verder). Een uitleg die de
  zin navertelt ("de zin beschrijft een voordeel en een nadeel") wordt afgekeurd, ook als hij waar is.
- Zelfstandige naamwoorden krijgen hun lidwoord mee: "el coche", "la casa", nooit "coche" los. Het
  geslacht hoort bij het woord.
- "ue" is dezelfde uitleg in het Engels.
- "alt" hoeft alleen ANDERE goede formuleringen te bevatten (andere woordvolgorde, een synoniem).
  Het antwoord zelf zetten wij er machinaal bij; dat hoef jij niet over te typen. Laat "alt" gerust
  leeg als er geen echte varianten zijn.`;

function promptZinnenVerschijnsel(gat, ids, inv) {
  const bestaand = inv.sentences.filter(s => s.tag === gat.tag).slice(0, 8).map(s => `- ${s.es} — ${s.nl}`).join("\n");
  return `Je maakt oefenmateriaal voor een Nederlandstalige die Spaans leert (A2, AULA 2).

Onderwerp (tag): "${gat.tag}". Hier gaat het structureel mis: ${gat.fouten} fouten, en er zijn maar
${gat.zinnen} oefenzinnen voor. Maak ${ids.length} NIEUWE oefenzinnen die precies dit onderwerp toetsen.

Bestaande zinnen (niet herhalen, wel dezelfde soort):
${bestaand || "(nog geen)"}

${STIJL}
- Gebruik exact deze ids in deze volgorde: ${ids.join(", ")}
- "tag" is exact "${gat.tag}".

Antwoord met UITSLUITEND JSON: een object met precies een sleutel "zinnen", met daarin de lijst.
{"zinnen":[${JSON.stringify(VOORBEELD_ZIN)}]}`;
}

function promptZinnenWoorden(gat, ids) {
  const lijst = gat.woorden.slice(0, ids.length * 2).map(w => `- ${w.es} (${w.nl})`).join("\n");
  return `Je maakt oefenmateriaal voor een Nederlandstalige die Spaans leert (A2, AULA 2).

Deze woorden blijven niet plakken; de leerling maakt er steeds fouten mee:
${lijst}

Maak ${ids.length} NIEUWE oefenzinnen waarin deze woorden voorkomen — een woord in een zin blijft veel
beter hangen dan een los kaartje. Verdeel de woorden over de zinnen, elk woord minstens één keer.

${STIJL}
- Gebruik exact deze ids in deze volgorde: ${ids.join(", ")}
- "tag" is exact "${gat.tag}".

Antwoord met UITSLUITEND JSON: een object met precies een sleutel "zinnen", met daarin de lijst.
{"zinnen":[${JSON.stringify(VOORBEELD_ZIN)}]}`;
}

function promptToets(gat, id, inv) {
  const kaart = inv.cheat[gat.spiek[0]];
  const oud = inv.quizzes.find(q => q.id === gat.tag);
  const oudeVragen = oud ? oud.vragen.slice(0, 5).map(v => "- " + v.q).join("\n") : "";
  const uitleg = kaart ? String(kaart.html).replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").slice(0, 1200) : "";
  return `Je maakt een grammatica-toetsje voor een Nederlandstalige die Spaans leert (A2, AULA 2).

De leerling struikelt herhaaldelijk over het toetsje "${gat.titel}" (${gat.fouten} fouten). Maak een
NIEUW toetsje over dezelfde regel, met andere voorbeelden, zodat hij de regel opnieuw kan oefenen
zonder de antwoorden al te kennen.

De uitleg waar dit over gaat:
${uitleg}

Vragen die er al zijn (niet herhalen):
${oudeVragen || "(geen)"}

Eisen:
- 8 vragen, meerkeuze met 2 of 3 opties, precies één goed antwoord ("c" is de index, 0-gebaseerd).
- De opties van een vraag moeten onderling VERSCHILLEN. Twee keer hetzelfde woord in "opts" maakt de
  vraag onbeantwoordbaar. Dit is de fout die hier het vaakst gemaakt wordt, dus loop je vragen na.
- Opties mogen ook niet alleen in een ACCENT verschillen (ibamos tegenover íbamos). Die vraag wordt
  weggegooid: de app rekent een antwoord zonder accent overal goed, dus zo'n vraag toetst een regel
  die de app zelf niet hanteert. Laat de opties in verschillende woorden of vormen verschillen.
- Bij elke vraag een Nederlandse vertaling ("nl") en Engelse ("ne") van de bedoelde zin, zodat de vraag
  te maken is zonder gokken.
- "u" legt in het Nederlands uit waarom het goede antwoord goed is; "ue" is dezelfde uitleg in het Engels.
- Varieer de vormen; laat minstens twee vragen een valkuil bevatten die de leerling echt kan maken.
- id is exact "${id}", titel Nederlands, titelEn Engels, spiek is exact ${JSON.stringify(gat.spiek)}.

Antwoord met UITSLUITEND JSON:
{"id":"${id}","titel":"...","titelEn":"...","spiek":${JSON.stringify(gat.spiek)},"vragen":[${JSON.stringify(VOORBEELD_VRAAG)}]}`;
}

function promptTegenlezerZinnen(items) {
  return `Je bent corrector Spaans (Spanje, niveau A2/B1) voor een leerapp. Controleer per item:
(1) is het Spaans correct en natuurlijk, (2) klopt de Nederlandse vertaling, (3) klopt de uitleg,
(4) SLAAT DE ZIN ERGENS OP? Zou een mens dit op een gewone dag tegen een ander zeggen? Keur af als de
    zin grammaticaal klopt maar inhoudelijk onzin is. Voorbeelden die zijn doorgeglipt en dus af
    hadden gemoeten: "Las mesas son tímidas" (de tafels zijn verlegen), "Busco las casas" (ik zoek de
    huizen). Correct Spaans, maar niemand zegt dat.
Wees streng op fouten en op onzin, maar keur niets af om stijlvoorkeur.
Het veld "alt" hoef je niet te controleren: dat vullen wij machinaal aan.

${JSON.stringify(items, null, 1)}

Antwoord met UITSLUITEND JSON: {"oordelen":[{"id":"...","ok":true,"reden":""}]} — één oordeel per id,
bij ok:false in "reden" één zin over wat er mis is.`;
}

/* 14 AUGUSTUS: DE CORRECTOR OORDEELT PER VRAAG, EN HIJ KRIJGT DE REGEL ERBIJ

   Hier stond "Keur het hele toetsje af zodra één vraag fout is". Drie nachten op rij ging daar het
   toetsje op stuk, en steeds op de uitleg bij imperfecto tegenover indefinido. Kijk naar de nacht
   van 14 aug: poging 1 werd afgekeurd op alléén vraag 6, poging 2 op vraag 4, 6 en 7. Met een
   oordeel per vraag was poging 1 met zeven vragen doorgekomen; valideer() vraagt er minstens vier.
   Acht vragen ineens goedkeuren is bovendien een weddenschap die je bij elke poging opnieuw moet
   winnen, en een tweede poging is een compleet nieuw toetsje, dus acht verse kansen om één keer te
   struikelen.

   En hij krijgt nu dezelfde spiekbriefkaart als de schrijver. Zonder die kaart redeneerde de
   corrector de regel elke keer opnieuw uit het niets, en dat ging mis: zijn eigen bezwaar bij vraag
   6 van poging 2 luidde letterlijk "de uitleg zegt 'indefinido is de gebeurtenis die de scène
   onderbreekt' terwijl het juist 'indefinido' is". Dat is geen bezwaar, dat is een zin die zichzelf
   tegenspreekt. Op zo'n oordeel kun je geen enkele beslissing baseren. */
function promptTegenlezerToets(qz, kaart) {
  return `Je bent corrector Spaans (Spanje, A2/B1) voor een leerapp. Hieronder een grammatica-toetsje.
Controleer PER VRAAG: is het Spaans correct, is er precies één juist antwoord, wijst "c" naar dat
antwoord, klopt de uitleg, en SLAAT DE ZIN ERGENS OP? Een vraag als "Las mesas son ___ (de tafels zijn
verlegen)" is grammaticaal in orde en toch fout: niemand zegt dat. Ook: staan er geen twee identieke
opties tussen.
${kaart ? `
De regel waar dit toetsje over gaat, zoals de leerling hem in de app leest. Toets de uitleg hieraan;
een uitleg die hetzelfde zegt als deze kaart is goed, ook als jij het anders zou formuleren:
${kaart}
` : ""}
Keur alleen de vragen af die echt fout zijn. Een vraag die klopt maar die jij anders had geschreven,
is goed. Twijfel je, dan is de vraag goed: een onterechte afkeuring kost de leerling zijn oefening.

${JSON.stringify(qz, null, 1)}

Antwoord met UITSLUITEND JSON: {"oordelen":[{"n":1,"ok":true,"reden":""}]} — één oordeel per vraag,
"n" is het vraagnummer vanaf 1, en bij ok:false in "reden" één zin over wat er mis is.`;
}

/* De controlemeting, en de reden dat hij er is: op 13 augustus is er een halve dag verspild aan het
   repareren van iets dat niet stuk was, omdat de méting stuk was. Zie pw-gramvariatie.js, dat
   dezelfde truc gebruikt met serestar.

   Hier is het controlegeval het toetsje dat al maanden in de app staat en dat Stefan zelf heeft
   gemaakt. Keurt de corrector dáár twee of meer vragen van af, dan is niet de nieuwe content stuk
   maar de corrector, en dan mag zijn oordeel over het nieuwe toetsje niets beslissen. We publiceren
   dan niet (ongelezen grammatica-uitleg naar een leerling sturen is erger dan een nacht niets), maar
   de hartslag noemt wél de juiste reden. Dat scheelt de volgende ochtend een verkeerde reparatie. */
async function keurToets(qz, kaart, motor) {
  const uit = await vraagModel(motor, promptTegenlezerToets(qz, kaart), 2500);
  const oordelen = uit && Array.isArray(uit.oordelen) ? uit.oordelen : null;
  if (!oordelen) return null;
  const slecht = [];
  (qz.vragen || []).forEach((v, i) => {
    const o = oordelen.find(x => Number(x.n) === i + 1);
    if (o && o.ok === false) slecht.push({ n: i + 1, reden: o.reden || "geen reden" });
  });
  return slecht;
}

async function vraagModel(motor, prompt, maxTokens) {
  const tekst = await motor.reason(prompt, { maxTokens: maxTokens || 4000, jsonMode: true });
  const j = haalJson(tekst);
  // "geen bruikbare JSON" zonder te zeggen wat er dan wel kwam, kost een nacht om uit te zoeken.
  if (j === null) console.error("    niets bruikbaars uit het model; eerste 160 tekens: " +
    (tekst === null || tekst === undefined ? "(niets teruggekregen)" : JSON.stringify(String(tekst).slice(0, 160))));
  return j;
}
// (motor.reason geeft altijd tekst terug of null; llm.js' eigen {text}-envelop wordt hierboven
//  al afgepeld, zodat beide bronnen zich hetzelfde gedragen)

async function maakZinnen(gat, aantal, inv, alTeGaan, motor) {
  const volgende = lib.volgendeId(inv.sentences.concat(alTeGaan), "s");
  const ids = [];
  for (let i = 1; i <= aantal; i++) ids.push(volgende(i));
  if (OPT.stub) {
    return ids.map((id, i) => ({
      id, lvl: 1, nl: `Proefzin ${i + 1} (${gat.tag}).`, en: `Test sentence ${i + 1} (${gat.tag}).`,
      es: `Esta es la frase de prueba número ${i + 1}.`, alt: [`esta es la frase de prueba numero ${i + 1}`],
      uitleg: "Nepcontent uit --stub, alleen om de pijplijn te testen.",
      ue: "Stub content, only to test the pipeline.", tag: gat.tag
    }));
  }
  const prompt = gat.soort === "woorden" ? promptZinnenWoorden(gat, ids) : promptZinnenVerschijnsel(gat, ids, inv);
  const antw = await vraagModel(motor, prompt);
  // Zowel {zinnen:[...]} als een kale array wordt geaccepteerd: het model mag zich hier niet in vergissen.
  const rij = Array.isArray(antw) ? antw : (antw && Array.isArray(antw.zinnen) ? antw.zinnen : null);
  if (!rij) { console.error(`    geen bruikbare JSON voor ${gat.tag}`); return []; }
  /* ids, tag en alt dwingen we zelf af; daar mag het model zich niet in vergissen.
     alt kwam er op 9 aug bij, na twee nachten waarin de run al zijn eigen zinnen afkeurde op precies
     dat veld ("alt bevat het eigen antwoord niet", vijf van de vijf). alt is een normalisatie van es:
     kleine letters, leestekens weg, accenten weg. Dat is machinewerk. Het model mag nog wel extra
     varianten aandragen, en die blijven staan; herstelAlt zet alleen het antwoord zelf er gegarandeerd
     vooraan bij. Zie tools/content-lib.js. */
  return rij.slice(0, aantal)
    .map((z, i) => Object.assign({}, z, { id: ids[i], tag: gat.tag }))
    .map(lib.herstelAlt);
}

async function keurZinnen(items, motor) {
  if (!items.length || OPT.stub) return items;
  const uit = await vraagModel(motor, promptTegenlezerZinnen(items), 2500);
  const oordelen = uit && Array.isArray(uit.oordelen) ? uit.oordelen : null;
  if (!oordelen) { console.error("    tegenlezer gaf geen bruikbaar oordeel — levering afgekeurd"); return []; }
  return items.filter(it => {
    const o = oordelen.find(x => x.id === it.id);
    if (!o) { console.error(`    ${it.id}: geen oordeel → afgekeurd`); return false; }
    if (o.ok === false) { console.error(`    ${it.id}: afgekeurd — ${o.reden || "geen reden"}`); return false; }
    return true;
  });
}

/* Dubbele opties zijn mechanisch, dus repareren we ze mechanisch. Zie de kop van
   patch-toetspoort.py: het model erop aanspreken maakte het twee nachten op rij erger.

   Exacte tekst, niet accentloos: comia tegenover comía is hier een geldige vraag en die moet blijven
   kunnen. c verschuift mee naar de kopie die blijft staan, want anders wijst het juiste antwoord na
   het opschonen naar de verkeerde optie, en dat is erger dan het probleem dat we oplossen. */
function schoonToets(qz) {
  const gemeld = [];
  const vragen = ((qz && qz.vragen) || []).map((v, i) => {
    if (!Array.isArray(v.opts)) return v;
    const houd = [], heen = [];
    v.opts.forEach(o => {
      const al = houd.indexOf(String(o));
      if (al === -1) { heen.push(houd.length); houd.push(String(o)); } else heen.push(al);
    });
    /* Twee opties die alleen in een accent verschillen (ibamos tegenover íbamos) zijn geen vraag maar
       een valstrik, en ze zijn de reden dat er drie nachten op rij geen toetsje doorkwam: het model
       schrijft er een uitleg bij die zichzelf tegenspreekt en de corrector keurt het hele toetsje af.
       Er is ook een principiële reden: de app rekent overal een antwoord zonder accent goed, dus een
       vraag waarin het accent het hele antwoord is, spreekt de rest van de app tegen.

       Na het ontdubbelen en niet ervoor: era naast era is een dubbele optie en geen accentval, en een
       melding die de verkeerde reden noemt stuurt de volgende lezer het bos in. */
    const kaal = houd.map(o => o.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, ""));
    if (new Set(kaal).size !== kaal.length) {
      gemeld.push(`vraag ${i + 1}: opties verschillen alleen in een accent, valt weg`);
      return null;
    }
    if (houd.length === v.opts.length) return v;
    /* Alleen wegstrepen wat door het opschonen te mager wordt. Een vraag die zelf al met twee opties
       kwam blijft staan: die is niet stuk, en valideer() laat er twee toe. */
    if (houd.length < 3) { gemeld.push(`vraag ${i + 1}: te weinig opties over, valt weg`); return null; }
    gemeld.push(`vraag ${i + 1}: ${v.opts.length - houd.length} dubbele optie weg`);
    const c = typeof v.c === "number" && heen[v.c] !== undefined ? heen[v.c] : v.c;
    return Object.assign({}, v, { opts: houd, c });
  }).filter(Boolean);
  return { qz: Object.assign({}, qz, { vragen }), gemeld };
}

async function maakToets(gat, inv, motor) {
  const nr = inv.quizzes.filter(q => /-extra\d*$/.test(q.id)).length + 1;
  const id = gat.tag + "-extra" + nr;
  if (OPT.stub) {
    return { id, titel: "Proeftoetsje", titelEn: "Stub quiz", spiek: gat.spiek,
      vragen: [1, 2, 3, 4].map(i => ({ q: `Pregunta de prueba ${i} ___.`, nl: "Proefvraag.", ne: "Stub question.",
        opts: ["uno", "dos"], c: 0, u: "Nepcontent uit --stub.", ue: "Stub content." })) };
  }
  /* De corrector had gelijk toen hij dit toetsje afkeurde (drie keer "comía" tussen de opties), maar
     een terecht bezwaar was ook meteen het einde van de nacht. Nu krijgt het model zijn eigen bezwaar
     terug en mag het er nog een keer overheen. Twee pogingen, daarna is het klaar. */
  const kaart = inv.cheat[gat.spiek[0]]
    ? String(inv.cheat[gat.spiek[0]].html).replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").slice(0, 1200)
    : "";
  let bezwaren = null;
  for (let poging = 1; poging <= 2; poging++) {
    const extra = bezwaren
      ? "\n\nJe vorige poging is afgekeurd door de corrector. Herstel precies dit en lever opnieuw:\n- " +
        bezwaren.join("\n- ")
      : "";
    const qz = await vraagModel(motor, promptToets(gat, id, inv) + extra, 5000);
    if (!qz || !Array.isArray(qz.vragen)) { console.error(`    geen bruikbaar toetsje voor ${gat.tag} (poging ${poging})`); continue; }
    qz.id = id; qz.spiek = gat.spiek;
    const schoon = schoonToets(qz);
    if (schoon.gemeld.length) console.log("    opgeschoond: " + schoon.gemeld.join("; "));
    if (schoon.qz.vragen.length < 4) {
      console.error(`    te weinig vragen over na opschonen (poging ${poging})`);
      bezwaren = ["te veel vragen hadden dubbele opties; geef per vraag vier verschillende opties"];
      continue;
    }

    const slecht = await keurToets(schoon.qz, kaart, motor);
    if (!slecht) {
      bezwaren = ["de corrector gaf geen bruikbaar oordeel"];
      console.error(`    corrector onleesbaar (poging ${poging})`);
      continue;
    }
    if (!slecht.length) return schoon.qz;

    /* Er is iets afgekeurd. Vóórdat we dat geloven: ijk de corrector op het toetsje dat al in de app
       staat. Dat kost één modelaanroep, en alleen op de nachten waarop er iets af te keuren viel. */
    if (oud && Array.isArray(oud.vragen) && oud.vragen.length >= 4) {
      const controle = await keurToets(oud, kaart, motor);
      if (!controle || controle.length >= 2) {
        const hoeveel = controle ? controle.length : "onleesbaar";
        // console.error schrijft zichzelf al in de hartslag (zie boven), dus dit is meteen de reden
        // die Stefan 's ochtends leest.
        console.error(`CONTROLE MISLUKT: de corrector keurde ook ${hoeveel} vragen af van "${oud.id}", ` +
          `dat al in de app staat. Niet de nieuwe content is verdacht maar de corrector; ` +
          `er is vannacht met opzet geen toetsje geleverd.`);
        return null;
      }
      console.log(`    corrector geijkt op "${oud.id}": ${controle.length} van de ${oud.vragen.length} afgekeurd, dat is binnen de marge`);
    }

    /* De corrector is betrouwbaar bevonden, dus de afgekeurde vragen gaan eruit en de rest blijft.
       Alles-of-niets was hier de fout: zeven goede vragen weggooien om één slechte is duurder dan
       een toetsje van zeven vragen, en valideer() laat er vanaf vier door. */
    const houd = schoon.qz.vragen.filter((v, i) => !slecht.some(s => s.n === i + 1));
    console.error(`    ${slecht.length} vraag/vragen afgekeurd (poging ${poging}): ` +
      slecht.map(s => `vraag ${s.n}: ${s.reden}`).join("; "));
    if (houd.length >= 4) {
      console.error(`toetsje ${id}: ${houd.length} van de ${schoon.qz.vragen.length} vragen blijven staan, ` +
        `het toetsje gaat door zonder ${slecht.map(s => "vraag " + s.n).join(", ")}`);
      return Object.assign({}, schoon.qz, { vragen: houd });
    }
    bezwaren = slecht.map(s => `vraag ${s.n}: ${s.reden}`);
  }
  return null;
}

/* ================= 3. het pad verlengen ================= */

function volgendNiveau(inv) {
  // Zolang er A2-thema's uit AULA 2 ontbreken blijven we op A2; daarna gaat het pad door op B1.
  const a2 = inv.perLes.filter(l => (l.niveau || "A2") === "A2").length;
  return a2 >= 10 ? "B1" : "A2";
}

function promptNieuweLes(niveau, inv, ids) {
  const bestaande = inv.perLes.map(l => `${l.num}. ${l.titel} — ${l.niveau || "A2"}`).join("\n");
  return `Je breidt het leerpad van een Spaans-leerapp uit. De leerling is Nederlandstalig, volgt twee
keer per week echte les (AULA-methode) en werkt in de app dagelijks aan woorden, grammatica, lezen,
luisteren en schrijven.

Bestaande lessen:
${bestaande}

Maak ÉÉN nieuwe les op niveau ${niveau}, die logisch volgt op het bovenstaande en nog niet aan bod is
geweest. De les bestaat uit:
- 14 woorden (los vocabulaire rond het thema)
- 8 oefenzinnen
- 1 grammatica-toetsje van 8 meerkeuzevragen over het grammaticapunt van deze les
- 1 spiekbriefkaart: de uitleg van dat grammaticapunt, in het Nederlands, met HTML (<p>, <b>, <i>,
  eventueel een kleine <table>). Zelfde toon als een goede docent: eerst de regel, dan de valkuil,
  dan een ezelsbruggetje.

${STIJL}

${WOORDVORM}

Gebruik exact deze ids:
- woorden: ${ids.words.join(", ")}
- zinnen: ${ids.sents.join(", ")}
- toetsje: ${ids.quiz}

Antwoord met UITSLUITEND JSON in deze vorm:
{"titel":"Spaanse titel","doel":"Nederlands lesdoel","doelEn":"English lesson goal",
 "niveau":"${niveau}",
 "words":[{"id":"${ids.words[0]}","es":"el dedo","nl":"de vinger","en":"finger","tag":"<thema-slug>","meer":"teen is el dedo del pie"}],
 "sentences":[${JSON.stringify(VOORBEELD_ZIN)}],
 "quiz":{"id":"${ids.quiz}","titel":"...","titelEn":"...","vragen":[${JSON.stringify(VOORBEELD_VRAAG)}]},
 "cheat":{"titel":"...","titelEn":"...","html":"<p>…</p>","htmlEn":"<p>…</p>"}}`;
}

async function maakNieuweLes(inv, motor) {
  const niveau = volgendNiveau(inv);
  const vW = lib.volgendeId(inv.words, "w"), vS = lib.volgendeId(inv.sentences, "s");
  const ids = { words: [], sents: [], quiz: "q-" + niveau.toLowerCase() + "-" + (inv.perLes.length + 1) };
  for (let i = 1; i <= 14; i++) ids.words.push(vW(i));
  for (let i = 1; i <= 8; i++) ids.sents.push(vS(i));
  console.log(`  nieuwe les op niveau ${niveau} maken…`);
  let les;
  if (OPT.stub) {
    les = { titel: "Lección de prueba", doel: "Proefles uit --stub", doelEn: "Stub lesson", niveau,
      words: ids.words.map((id, i) => ({ id, es: "prueba" + (i + 1), nl: "proef" + (i + 1), en: "test" + (i + 1), tag: "stub" })),
      sentences: ids.sents.map((id, i) => ({ id, lvl: 1, nl: "Proef " + (i + 1) + ".", en: "Test " + (i + 1) + ".",
        es: "Prueba número " + (i + 1) + ".", alt: ["prueba numero " + (i + 1)], uitleg: "Stub.", ue: "Stub.", tag: "stub" })),
      quiz: { id: ids.quiz, titel: "Proeftoets", titelEn: "Stub quiz",
        vragen: [1, 2, 3, 4].map(i => ({ q: "Prueba " + i + " ___.", nl: "Proef.", ne: "Stub.", opts: ["a", "b"], c: 0, u: "Stub.", ue: "Stub." })) },
      cheat: { titel: "Proefkaart", titelEn: "Stub card", html: "<p>Stub.</p>", htmlEn: "<p>Stub.</p>" } };
  } else {
    les = await vraagModel(motor, promptNieuweLes(niveau, inv, ids), 8000);
    if (!les || !Array.isArray(les.words) || !Array.isArray(les.sentences)) {
      console.error("    geen bruikbare les van het model"); return null;
    }
    les.words = les.words.slice(0, 14).map((w, i) => Object.assign({}, w, { id: ids.words[i] }));
    les.sentences = les.sentences.slice(0, 8)
      .map((s, i) => Object.assign({}, s, { id: ids.sents[i] }))
      .map(lib.herstelAlt);   // zelfde reden als in maakZinnen: alt is machinewerk
    if (les.quiz) les.quiz.id = ids.quiz;
    /* Alles of niets was hier te streng: een hele B1-les met acht zinnen ging de prullenbak in omdat
       de corrector bij een ervan een verkeerde tag zag. Nu vallen de afgekeurde zinnen eruit en gaat de
       les door zolang er genoeg overblijft. Jij leest hem toch nog na, het gaat als pull request. */
    const keur = await keurZinnen(les.sentences, motor);
    if (keur.length < les.sentences.length)
      console.error(`    ${les.sentences.length - keur.length} van de ${les.sentences.length} zinnen afgekeurd, de rest gaat door`);
    if (keur.length < 6) { console.error("    te weinig zinnen over → les niet aangeboden"); return null; }
    les.sentences = keur;
    if (les.quiz) {
      const schoon = schoonToets(les.quiz);
      if (schoon.gemeld.length) console.log("    toetsje opgeschoond: " + schoon.gemeld.join("; "));
      les.quiz = schoon.qz.vragen.length >= 4 ? schoon.qz : null;
      /* Zelfde reden als bij de zinnen hierboven: alles of niets was te streng. Een afgekeurd
         toetsje kostte tot nu toe de hele les, veertien woorden en acht zinnen erbij. De
         lesindeling kan een les zonder toetsje aan, en jij leest de pull request toch na. */
      if (les.quiz) {
        // 14 aug: ook hier per vraag in plaats van alles-of-niets. De spiekbriefkaart van de nieuwe
        // les bestaat op dit moment nog niet in inv.cheat, dus die kan de corrector niet meekrijgen;
        // hij doet het hier zonder. Dat mag, want een nieuwe les komt als pull request en Stefan
        // leest hem na. Alleen bij het direct-live-pad moest de ijking erbij.
        const slecht = await keurToets(les.quiz, les.cheat && les.cheat.html
          ? String(les.cheat.html).replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").slice(0, 1200) : "", motor);
        if (!slecht) {
          console.error("    corrector gaf geen bruikbaar oordeel over het toetsje, de les gaat door zonder");
          les.quiz = null;
        } else if (slecht.length) {
          const houd = les.quiz.vragen.filter((v, i) => !slecht.some(s => s.n === i + 1));
          console.error(`    toetsje van de nieuwe les: ${slecht.length} vraag/vragen afgekeurd (` +
            slecht.map(s => `vraag ${s.n}: ${s.reden}`).join("; ") + ")");
          les.quiz = houd.length >= 4 ? Object.assign({}, les.quiz, { vragen: houd }) : null;
          if (!les.quiz) console.error("    te weinig vragen over, de les gaat door zonder toetsje");
        }
      }
    }
  }
  // de spiekkaart komt achter de bestaande, dus haar index is de huidige lengte
  const spiekIdx = inv.cheat.length;
  const lesId = (niveau === "B1" ? "b1-" : "a2-") + (inv.perLes.length + 1);
  return {
    words: les.words,
    sentences: les.sentences,
    quizzes: les.quiz ? [Object.assign({}, les.quiz, { spiek: [spiekIdx] })] : [],
    cheat: les.cheat ? [les.cheat] : [],
    nieuweLessen: [{
      id: lesId, num: inv.perLes.length + 1, niveau, titel: les.titel, doel: les.doel, doelEn: les.doelEn,
      spiek: [spiekIdx], words: les.words.map(w => w.id), sents: les.sentences.map(s => s.id),
      quizzes: les.quiz ? [les.quiz.id] : []
    }]
  };
}

/* ================= 4. uitvoeren ================= */

async function main() {
  const inv = lib.inventaris();
  const logboek = leesLogs();
  const an = analyseer(logboek, inv);
  const vrd = voorraad(logboek, inv);
  rapport(inv, an, vrd);

  /* Gaten op één stapel, verschijnselen eerst. Een regel die je niet snapt blijft tientallen items
     besmetten, een woord dat je mist is één woord; bovendien komen die woorden hoe dan ook terug via
     de herhaling, en een verschijnsel heeft geen tweede kanaal.

     Dit stond tot 11 aug wel in dit commentaar maar niet in de code: de twee soorten werden op één
     hoop gegooid en op score gesorteerd, terwijl hun scores uit twee verschillende sommen komen en
     dus niet op dezelfde schaal staan. De woordgaten wonnen daardoor stelselmatig. Uitkomst van
     11 aug: de run pakte les3 en les5 aan terwijl sentirse 20 fouten had op 6 oefenzinnen. Sorteren
     op soort en pas daarbinnen op score is botter dan één formule, maar het is wél wat er staat. */
  const gaten = [].concat(
    an.zinGaten.slice().sort((a, b) => b.score - a.score),
    an.woordGaten.slice().sort((a, b) => b.score - a.score));
  const padKrap = vrd.krapsteDagen !== null && vrd.krapsteDagen < VOORRAAD_DREMPEL_DAGEN;
  const verlengen = OPT.nieuweLes || padKrap;

  // Wat het besluit belooft, is vanaf hier een afspraak: leveren of falen. Zie het slot van main.
  HART.staat.beloofd = { gaten: Math.min(OPT.max, gaten.length), toetsje: an.toetsGaten.length ? 1 : 0,
                         nieuweLes: verlengen ? 1 : 0 };
  HART.staat.voorraadDagen = vrd.krapsteDagen;

  console.log("— besluit —");
  if (gaten.length) console.log(`  ${Math.min(OPT.max, gaten.length)} gat(en) aanpakken: ` +
    gaten.slice(0, OPT.max).map(g => `${g.tag} (${g.soort})`).join(", "));
  if (an.toetsGaten.length) console.log(`  nieuw toetsje bij: ${an.toetsGaten[0].tag}`);
  if (verlengen) console.log(`  pad verlengen met een nieuwe les op niveau ${volgendNiveau(inv)}` +
    (padKrap ? ` (voorraad ${vrd.krapsteDagen} dagen < drempel ${VOORRAAD_DREMPEL_DAGEN})` : " (--nieuwe-les)"));
  if (!gaten.length && !an.toetsGaten.length && !verlengen) console.log("  niets te doen");
  if (OPT.analyse) return 0;

  const motor = OPT.stub ? null : llm();
  if (!motor && !OPT.stub) { HART.staat.reden = "geen taalmodel bereikbaar"; console.error("geen LLM beschikbaar; stop"); return 1; }
  if (motor) HART.staat.ladder = motor.bron + (ZWARE_LADDER ? " · " + ZWARE_LADDER.split(",")[0] + " voorop" : "");
  if (motor && !(await ladderProef(motor))) {
    HART.staat.reden = "ladder onbereikbaar" + (LADDERFOUT ? ": " + LADDERFOUT : "");
    return 1;
  }

  /* --- deel 1: gaten dichten (gaat direct live) --- */
  const reparatie = { sentences: [], quizzes: [], lessen: {} };
  for (const gat of gaten.slice(0, OPT.max)) {
    const aantal = gat.soort === "woorden"
      ? Math.min(MAX_ZINNEN_PER_GAT, Math.max(2, Math.ceil(gat.woorden.length / 3)))
      : Math.min(MAX_ZINNEN_PER_GAT, Math.max(2, Math.ceil(gat.zinnen * 0.5) || 2));
    console.log(`  ${gat.tag}: ${aantal} zinnen maken…`);
    const ruw = await maakZinnen(gat, aantal, inv, reparatie.sentences, motor);
    const goed = await keurZinnen(ruw, motor);
    if (!goed.length) { console.error(`    ${gat.tag}: niets overgebleven`); continue; }
    const voorbeeld = inv.sentences.find(s => s.tag === gat.tag)
      || inv.words.find(w => w.tag === gat.tag);
    let les = null;
    if (voorbeeld) les = inv.perLes.find(l => l.sents.includes(voorbeeld.id) || l.words.includes(voorbeeld.id));
    const lesId = (les || inv.perLes[0]).id;
    reparatie.sentences = reparatie.sentences.concat(goed);
    const b = reparatie.lessen[lesId] = reparatie.lessen[lesId] || { sents: [] };
    b.sents = (b.sents || []).concat(goed.map(z => z.id));
    console.log(`    ${goed.length} zinnen goedgekeurd → les ${lesId}`);
  }
  if (an.toetsGaten.length) {
    const gat = an.toetsGaten[0];
    console.log(`  ${gat.tag}: nieuw toetsje maken…`);
    const qz = await maakToets(gat, inv, motor);
    if (qz) {
      reparatie.quizzes.push(qz);
      // NIET aan de les hangen: een extra toetsje in de lesindeling zou de eis voor het ontgrendelen
      // van de volgende les verhogen. Via de spiekkaart komt hij vanzelf in de grammatica-herhaling
      // (quizzenBijSpiek + checkLessonComplete in de app).
      console.log(`    toetsje ${qz.id} goedgekeurd met ${qz.vragen.length} vragen`);
    }
  }

  let versie = null;
  if (reparatie.sentences.length || reparatie.quizzes.length) {
    const res = lib.pasToe(reparatie, { droog: OPT.droog });
    meldAlt(res);
    if (!res.ok) { console.error("AFGEKEURD:\n - " + res.fouten.join("\n - ")); return 1; }
    versie = res.versie;
    if (OPT.droog) fs.writeFileSync("/tmp/vamos-curriculum-droog.html", res.src);
    console.log(`${OPT.droog ? "droog: zou toevoegen" : "toegevoegd"}: ` +
      `${reparatie.sentences.length} zinnen, ${reparatie.quizzes.length} toetsjes → ${res.versie}`);
  }

  /* --- deel 2: het pad verlengen (komt als pull request) --- */
  let nieuweLes = null;
  if (verlengen) {
    const inv2 = OPT.droog ? inv : lib.inventaris();   // na deel 1 opnieuw inlezen voor verse ids
    nieuweLes = await maakNieuweLes(inv2, motor);
    if (nieuweLes) {
      const res = lib.pasToe(nieuweLes, { droog: true });   // altijd eerst droog: dit gaat via een PR
      meldAlt(res);
      if (!res.ok) { console.error("nieuwe les AFGEKEURD:\n - " + res.fouten.join("\n - ")); nieuweLes = null; }
      else {
        fs.writeFileSync("/tmp/vamos-nieuwe-les.json", JSON.stringify(nieuweLes, null, 1));
        console.log(`  nieuwe les klaar: "${nieuweLes.nieuweLessen[0].titel}" ` +
          `(${nieuweLes.words.length} woorden, ${nieuweLes.sentences.length} zinnen) → /tmp/vamos-nieuwe-les.json`);
        if (!OPT.droog) {
          const echt = lib.pasToe(nieuweLes, {});
          if (!echt.ok) { console.error("nieuwe les alsnog afgekeurd bij schrijven:\n - " + echt.fouten.join("\n - ")); nieuweLes = null; }
          else { versie = echt.versie; console.log(`  nieuwe les weggeschreven → ${echt.versie} (zet dit in een pull request)`); }
        }
      }
    }
  }

  HART.staat.geleverd = { zinnen: reparatie.sentences.length, toetsjes: reparatie.quizzes.length,
                          nieuweLes: nieuweLes ? 1 : 0 };
  HART.staat.versie = versie;

  if (!OPT.droog && (versie || nieuweLes)) {
    fs.writeFileSync(PLAN, JSON.stringify({
      wanneer: new Date().toISOString(), versie,
      gaten: gaten.slice(0, OPT.max).map(g => ({ tag: g.tag, soort: g.soort, fouten: g.fouten })),
      reparatie: { zinnen: reparatie.sentences.map(s => s.id), toetsjes: reparatie.quizzes.map(q => q.id) },
      nieuweLes: nieuweLes ? nieuweLes.nieuweLessen[0] : null
    }, null, 1));
  }

  /* De afsluitregel. Hierboven kan van alles stilletjes op niets uitlopen: een model dat geen
     bruikbare JSON teruggeeft, een tegenlezer die niets oordeelt, een levering die de controles van
     content-lib niet haalt. Elk van die paden schreef een klacht naar stderr en liep door, en de run
     eindigde groen met "geen wijzigingen". Vanaf nu geldt: wat het besluit beloofde, moet er zijn.
     Nul geleverd op een gevulde belofte is een mislukte nacht en die hoort rood te zijn. */
  const b = HART.staat.beloofd || { gaten: 0, toetsje: 0, nieuweLes: 0 };
  const beloofd = b.gaten + b.toetsje + b.nieuweLes;
  const geleverd = reparatie.sentences.length + reparatie.quizzes.length + (nieuweLes ? 1 : 0);
  if (beloofd > 0 && geleverd === 0) {
    HART.staat.reden = "het besluit vroeg om " + beloofd + " stuk(ken) werk en er is niets van weggeschreven";
    console.error("MISLUKT: " + HART.staat.reden + ". Kijk hierboven welk onderdeel afhaakte.");
    return 1;
  }
  if (beloofd === 0) HART.staat.reden = "niets te doen: geen gaten, geen toetsgaten, voorraad ruim genoeg";
  return 0;
}

/* De alt-waarschuwingen uit pasToe op het scherm. Ze keuren niets af, dus ze horen niet bij de
   fouten, maar ze moeten wel in het verslag staan: dit is precies het soort ding dat niemand ooit
   meer terugvindt als het alleen in de code zit. Zie patch-altpoort.py voor de aanleiding. */
function meldAlt(res) {
  const w = (res && res.waarschuwingen) || [];
  if (!w.length) return;
  console.log("— alt om na te lezen —");
  w.forEach(r => console.log("  " + r));
}

/* Precies een plek waar de hartslag wordt weggeschreven, en die ligt buiten main, zodat ook een
   klapper er nog in komt. */
function hartslag(gelukt) {
  HART.staat.gelukt = !!gelukt;
  HART.staat.wanneer = new Date().toISOString();
  if (gelukt && !HART.staat.reden) HART.staat.reden = null;
  if (gelukt && HART.staat.reden === "de run is niet afgemaakt") HART.staat.reden = null;
  console.log("— hartslag —");
  console.log("  " + JSON.stringify(HART.staat));
  if (OPT.analyse || OPT.droog) return;                 // kijken verandert niets, ook niet hier
  try { fs.writeFileSync(HART_PAD, JSON.stringify(HART.staat, null, 1) + "\n"); }
  catch (e) { console.error("hartslag niet weg te schrijven: " + e.message); }
}

main()
  .then(code => { hartslag(code === 0); process.exit(code); })
  .catch(e => {
    console.error(e);
    HART.staat.reden = "de run klapte: " + (e && e.message ? e.message : e);
    hartslag(false);
    process.exit(1);
  });
