#!/usr/bin/env python3
# v23.42 - de nachtrun kan geen lege uitleg meer leveren, en schrijven staat weer in de dagles.
#
# Draai dit NA de merge van curriculum/les-20260811, dus met index.html op v23.41.
#
# Vier dingen, alle vier op verzoek van Stefan (11 aug):
#   1. Uitleg moet iets uitleggen. valideer() eist dat een uitleg een Spaans woord uit de eigen zin
#      noemt of de regel bij naam. De les van vannacht kwam door de keuring met "De zin beschrijft
#      een voordeel en een nadeel": niet leeg, niet onwaar, en toch leert niemand er iets van. Van de
#      175 bestaande zinnen zouden er zes op deze regel afvallen; de zeven zinnen van de nieuwe
#      B1-les zijn hier herschreven en gaan nu over de vergrotende trap, waar die les over gaat.
#   2. Zelfstandige naamwoorden krijgen hun lidwoord (el of la). In de bestaande inhoud stond dit al
#      goed, 412 van de 422, maar er was geen regel die het afdwong. En Adivina liet het lidwoord
#      vallen: op het bord staat nog steeds coche, de oplossing heet weer el coche.
#   3. Geen accentvallen in toetsjes. Twee opties die alleen in een accent verschillen vallen weg.
#      Daar sneuvelden drie nachten op rij alle toetsjes op, en de app rekent overal een antwoord
#      zonder accent goed, dus zo'n vraag spreekt de rest van de app tegen.
#   4. Schrijven staat weer in de dagles, als vaste vierde stap van drie zinnen.
#
# Idempotent, met per bestand een eigen vlag (zie DEPLOY.md).
import pathlib, sys, re

WORTEL = pathlib.Path.home() / "espanol"
APP = WORTEL / "index.html"
VERSIE = WORTEL / "versie.txt"

LIB_TEKST = r"""/*
 * content-lib.js — lezen, valideren en wegschrijven van de content in index.html.
 *
 * Waarom dit bestaat: de app is één HTML-bestand met de lesinhoud als JS-arrays erin. De avondrun
 * (tools/curriculum.js) moet daar items aan toevoegen zonder ooit een hand-geschreven regel te
 * herschrijven. Dus:
 *   - lezen doen we door de array-literal uit te knippen op balans van blokhaken en te evalueren
 *     (het is ons eigen bestand, geen invoer van buiten),
 *   - schrijven doen we uitsluitend vóór de sluithaak van een array, plus het machine-blok
 *     EXTRA_CONTENT. Nooit ertussen.
 *
 * Elke wijziging wordt na het schrijven opnieuw ingelezen en geteld. Klopt de telling niet exact,
 * dan is er niets weggeschreven. Zelftest: node tools/content-lib.js --zelftest
 */
"use strict";
const fs = require("fs");
const path = require("path");

const INDEX = path.join(__dirname, "..", "index.html");
const VERSIE = path.join(__dirname, "..", "versie.txt");

/* ---------- lezen ---------- */

// Knipt `var NAAM = [ ... ];` uit op balans van [ en ], strings en commentaar overslaand.
function vindArray(src, naam) {
  const m = new RegExp("^var " + naam + " = \\[", "m").exec(src);
  if (!m) throw new Error("array niet gevonden: " + naam);
  const open = m.index + m[0].length - 1;
  let diepte = 0, i = open, inStr = null, esc = false;
  for (; i < src.length; i++) {
    const c = src[i];
    if (inStr) {
      if (esc) { esc = false; continue; }
      if (c === "\\") { esc = true; continue; }
      if (c === inStr) inStr = null;
      continue;
    }
    if (c === '"' || c === "'") { inStr = c; continue; }
    if (c === "/" && src[i + 1] === "/") { i = src.indexOf("\n", i); if (i < 0) break; continue; }
    if (c === "/" && src[i + 1] === "*") { i = src.indexOf("*/", i) + 1; continue; }
    if (c === "[") diepte++;
    else if (c === "]") { diepte--; if (diepte === 0) break; }
  }
  if (diepte !== 0) throw new Error("ongebalanceerde array: " + naam);
  return { open, sluit: i, tekst: src.slice(open, i + 1) };
}

function leesArray(src, naam) {
  const { tekst } = vindArray(src, naam);
  // rng() wordt in de lessen gebruikt; voor de vier contentarrays niet, maar we geven hem mee zodat
  // dezelfde functie ook lessenlijsten kan lezen.
  const rng = (p, a, b) => { const r = []; for (let i = a; i <= b; i++) r.push(p + i); return r; };
  // eslint-disable-next-line no-new-func
  return new Function("rng", "return " + tekst)(rng);
}

// De lessenlijst staat als toewijzing (TRACKS.a2.lessons = [...]), niet als var. Aparte lezer.
function leesLessen(src) {
  const m = /^TRACKS\.a2\.lessons = \[/m.exec(src);
  if (!m) throw new Error("lessenlijst niet gevonden");
  const open = m.index + m[0].length - 1;
  let diepte = 0, i = open, inStr = null, esc = false;
  for (; i < src.length; i++) {
    const c = src[i];
    if (inStr) { if (esc) { esc = false; continue; } if (c === "\\") { esc = true; continue; } if (c === inStr) inStr = null; continue; }
    if (c === '"' || c === "'") { inStr = c; continue; }
    if (c === "[") diepte++;
    else if (c === "]") { diepte--; if (diepte === 0) break; }
  }
  const rng = (p, a, b) => { const r = []; for (let k = a; k <= b; k++) r.push(p + k); return r; };
  // eslint-disable-next-line no-new-func
  return new Function("rng", "return " + src.slice(open, i + 1))(rng);
}

function leesExtra(src) {
  const m = /^var EXTRA_CONTENT = (\{[\s\S]*?\});$/m.exec(src);
  if (!m) throw new Error("EXTRA_CONTENT-blok niet gevonden");
  // eslint-disable-next-line no-new-func
  return { waarde: new Function("return " + m[1])(), start: m.index, eind: m.index + m[0].length };
}

function inventaris() {
  const src = fs.readFileSync(INDEX, "utf8");
  const words = leesArray(src, "WORDS");
  const sentences = leesArray(src, "SENTENCES");
  const quizzes = leesArray(src, "QUIZZES");
  const cheat = leesArray(src, "CHEATSHEET");
  // v19.91 voegde K_WORDS toe: 244 kernwoorden met eigen k-ids die bij geen enkele les horen (de brede
  // pool die de dagportie op niveau ordent). Ze doen niet mee in het lespad, maar hun ids moeten wel
  // meegeteld worden bij de uniekheidscontrole.
  let kern = [];
  try { kern = leesArray(src, "K_WORDS"); } catch (e) { /* oudere versie zonder kernpool */ }
  const lessen = leesLessen(src);
  const extra = leesExtra(src).waarde;
  // dezelfde samenvoeging als pasExtraContentToe() in de app
  const perLes = lessen.map(l => {
    const e = extra.lessen[l.id] || {};
    return { id: l.id, num: l.num, titel: l.titel, niveau: l.niveau || "A2",
             words: l.words.concat(e.words || []), sents: l.sents.concat(e.sents || []),
             quizzes: l.quizzes.concat(e.quizzes || []), spiek: l.spiek.concat(e.spiek || []) };
  }).concat(extra.nieuweLessen.map(l => ({ id:l.id, num:l.num, titel:l.titel, niveau:l.niveau || "B1",
             words:l.words, sents:l.sents, quizzes:l.quizzes, spiek:l.spiek || [] })));
  return { src, words, sentences, quizzes, cheat, kern, lessen, extra, perLes };
}

/* ---------- ids ---------- */

function volgendeId(bestaande, prefix) {
  let hoog = 0;
  const re = new RegExp("^" + prefix + "(\\d+)$");
  bestaande.forEach(x => { const m = re.exec(x.id || x); if (m) hoog = Math.max(hoog, +m[1]); });
  return n => prefix + (hoog + n);
}

/* ---------- valideren ---------- */

const NL_VELDEN = { woord: ["id", "es", "nl", "en", "tag"],
                    zin: ["id", "lvl", "nl", "en", "es", "alt", "uitleg", "ue", "tag"],
                    toets: ["id", "titel", "titelEn", "spiek", "vragen"] };

/* ---------- alt: mechanisch werk, geen modelwerk (9 aug) ----------
   De avondrun draaide twee nachten achter elkaar en keurde beide keren al zijn eigen zinnen af, alle
   vijf op dezelfde regel: "alt bevat het eigen antwoord niet". Het model kreeg de opdracht om het
   antwoord in kleine letters zonder accenten te herhalen, en deed dat net niet goed genoeg.

   Dat is de verkeerde taakverdeling. alt is een normalisatie van es: kleine letters, leestekens weg,
   accenten weg. Een machine doet dat foutloos en een taalmodel bij benadering. Het model mag nog wel
   extra varianten aandragen (andere woordvolgorde, synoniem), want dát is taalwerk.

   altNorm en altKaal zijn dezelfde functies die de poort hieronder gebruikt om te keuren. Bewust
   dezelfde: een reparatie die net iets anders normaliseert dan de keuring is een reparatie die je op
   een dag laat vallen zonder dat iemand het ziet. */
const altNorm = t => String(t).toLowerCase().trim().replace(/[¡!¿?.,;:]/g, "").replace(/\s+/g, " ");
const altKaal = t => altNorm(t).normalize("NFD").replace(/[\u0300-\u036f]/g, "");

function herstelAlt(zin) {
  if (!zin || typeof zin.es !== "string") return zin;
  const eigen = altKaal(zin.es);
  const uit = [eigen];
  (Array.isArray(zin.alt) ? zin.alt : []).forEach(a => {
    if (typeof a !== "string") return;
    const schoon = altNorm(a);
    if (schoon && !uit.map(altKaal).includes(altKaal(schoon))) uit.push(schoon);
  });
  return Object.assign({}, zin, { alt: uit });
}

/* De voornaamwoorden waar het om gaat: de wederkerende en persoonlijke. os staat er niet bij, dat
   botst met het meervoud op -eros (companeros zou anders een os opleveren). lo/la/los/las/le/les
   tellen ook niet mee, want dat zijn ook lidwoorden, maar ze mogen er wel afgepeld worden: in
   prestarmelo zit het me achter het lo verstopt. */
const ALT_CLIT = ["me", "te", "se", "nos"];
const ALT_PEEL = ["me", "te", "se", "nos", "os", "lo", "la", "los", "las", "le", "les"];
function altEnclitisch(w) {
  /* Pel de vastgeplakte voornaamwoorden er achteraan af, maximaal drie lagen (dandomelo). Wat
     overblijft moet een werkwoordsvorm zijn waar iets aan vast kán zitten: hele werkwoordsvorm of
     -ndo-vorm. De diepste peling die daaraan voldoet wint. */
  let beste = [], rest = w, mee = [];
  for (let laag = 0; laag < 3; laag++) {
    const hit = ALT_PEEL.filter(c => rest.length > c.length && rest.endsWith(c))
                        .sort((a, b) => b.length - a.length)[0];
    if (!hit) break;
    rest = rest.slice(0, -hit.length);
    if (ALT_CLIT.includes(hit)) mee = mee.concat([hit]);
    if (/(ar|er|ir|ando|iendo|yendo)$/.test(rest)) beste = mee.slice();
  }
  return beste;
}
function altVoornaamwoorden(zin) {
  let uit = [];
  altKaal(zin).split(/[^a-z]+/).filter(Boolean).forEach(w => {   // altKaal maakt van n met tilde al een n
    if (ALT_CLIT.includes(w)) { uit.push(w); return; }
    uit = uit.concat(altEnclitisch(w));
  });
  return uit.sort().join(" ");
}
/* De poort op de alternatieven. Zie de kop van patch-altpoort.py voor waarom dit er is: het
   machinaal vullen van alt (9 aug) maakte de poort blij, maar kon een fout antwoord goedkeuren.
   Dit keurt niet af maar waarschuwt, want een herformulering met een ander voornaamwoord kán
   kloppen (nos falta hacer la compra). Op de 356 varianten die nu in de app staan geeft hij
   precies een waarschuwing, en die is terecht om even naar te kijken. */
function altWaarschuwingen(nieuw) {
  const uit = [];
  (nieuw.sentences || []).forEach(z => {
    if (!z || typeof z.es !== "string") return;
    const eigen = altVoornaamwoorden(z.es);
    (Array.isArray(z.alt) ? z.alt : []).forEach(a => {
      if (typeof a !== "string") return;
      const hunne = altVoornaamwoorden(a);
      if (hunne !== eigen) {
        uit.push(`${z.id || "?"}: alternatief "${a}" heeft andere voornaamwoorden dan de zin ` +
                 `(${eigen || "geen"} tegenover ${hunne || "geen"}). Klopt dat, of drilt de zin ` +
                 `een regel die het alternatief overtreedt?`);
      }
    });
  });
  return uit;
}

/* ---------- legt deze uitleg iets uit? (11 aug) ----------
   De nachtrun leverde een hele les met uitleg in de vorm van "De zin beschrijft een voordeel en een
   nadeel. Het is een praktische uitspraak." Het veld was gevuld, de tekst was waar, en de tegenlezer
   keurde hem goed. Toch leert niemand er iets van.

   Het verschil tussen uitleg en beschrijving is machinaal te vinden: echte uitleg wijst naar iets in
   de zin. Ze noemt een Spaans woord dat er staat ("hay que + infinitief"), of ze noemt de regel bij
   naam ("subjuntivo", "vrouwelijk meervoud"). Een tekst die geen van beide doet, gaat over de zin in
   plaats van over het Spaans.

   Bewust een ondergrens en geen oordeel: hij haalt de lege huls eruit, hij belooft geen goede
   didactiek. Dat laatste kan een machine niet en daar hoort de tegenlezer voor te zijn. */
const GRAMTERMEN = ["indefinido", "imperfecto", "perfecto", "subjuntivo", "gerundio", "infinitief",
  "infinitive", "lidwoord", "meervoud", "enkelvoud", "vrouwelijk", "mannelijk", "wederkerend",
  "voornaamwoord", "vervoeging", "werkwoord", "bijvoeglijk", "zelfstandig", "onregelmatig", "accent",
  "verkleinwoord", "bijwoord", "voorzetsel", "vergrotende trap", "overtreffende trap", "gebiedende",
  "verleden tijd", "tegenwoordige tijd", "toekomende tijd", "onvoltooid", "voltooid", "stam",
  "uitgang", "geslacht", "klemtoon", "spelling"];
function woordenVan(tekst) {
  return String(tekst || "").toLowerCase()
    .normalize("NFD").replace(/[̀-ͯ]/g, "")
    .split(/[^a-z0-9]+/).filter(w => w.length >= 3);
}
function uitlegZegtIets(uitleg, es) {
  const u = String(uitleg || "");
  if (u.trim().length < 30) return false;
  const laag = u.toLowerCase();
  if (GRAMTERMEN.some(t => laag.indexOf(t) !== -1)) return true;
  // een Spaans woord uit de zin zelf, aangehaald in de uitleg
  const inZin = new Set(woordenVan(es));
  return woordenVan(u).some(w => inZin.has(w));
}

/* ---------- el of la hoort bij het woord (11 aug, verzoek van Stefan) ----------
   Een zelfstandig naamwoord zonder lidwoord leer je zonder geslacht, en dan moet je het er later
   alsnog bij leren. In de bestaande inhoud staat dit al goed (412 van de 422), maar dat was
   handwerk en geen regel, dus de nachtrun kon het zo weer stukmaken.

   De vraag "is dit een zelfstandig naamwoord" beantwoorden we aan de Nederlandse kant, want daar
   staat het lidwoord er altijd: "de angst" is er een, "de hoofdrol spelen in" niet (te veel woorden)
   en "het regent" ook niet (dat is een werkwoord, herkenbaar aan de Spaanse uitgang). Liever een
   controle die een enkel geval doorlaat dan een die goede woorden afkeurt. */
const WERKUIT = /(ar|er|ir|[aeiou]r|[aeiouáéíóú])$/;
function heeftLidwoordNodig(w) {
  const nl = String(w.nl || "").trim().toLowerCase();
  const es = String(w.es || "").trim();
  if (!/^(de|het) [a-zà-ÿ]+$/.test(nl)) return false;   // geen kaal zelfstandig naamwoord
  if (/\s/.test(es)) return false;                                 // uitdrukking: die heeft zijn eigen vorm
  if (/(ar|er|ir)$/.test(es.toLowerCase())) return false;          // infinitief
  if (/[áéíóú]$/.test(es.toLowerCase())) return false;  // vervoegde vorm (pasó)
  return true;
}
function heeftLidwoord(es) {
  return /^(el|la|los|las) /i.test(String(es || "").trim());
}

function valideer(nieuw, inv) {
  const fouten = [];
  const bestaandeIds = new Set([].concat(
    inv.words.map(w => w.id), (inv.kern || []).map(w => w.id),
    inv.sentences.map(s => s.id), inv.quizzes.map(q => q.id)));
  const gezien = new Set();

  const eisVelden = (obj, soort, waar) => {
    NL_VELDEN[soort].forEach(v => {
      if (obj[v] === undefined || obj[v] === null || obj[v] === "") fouten.push(`${waar}: veld "${v}" ontbreekt`);
    });
  };
  const eisUniek = (id, waar) => {
    if (!id) return fouten.push(`${waar}: id ontbreekt`);
    if (bestaandeIds.has(id)) fouten.push(`${waar}: id "${id}" bestaat al`);
    if (gezien.has(id)) fouten.push(`${waar}: id "${id}" dubbel in deze levering`);
    gezien.add(id);
  };

  (nieuw.words || []).forEach((w, i) => {
    const waar = `woord ${i + 1} (${w.id})`;
    eisUniek(w.id, waar); eisVelden(w, "woord", waar);
    if (!/^w\d+$/.test(w.id || "")) fouten.push(`${waar}: id moet w<nummer> zijn`);
    if (w.es && w.es.length > 60) fouten.push(`${waar}: es is verdacht lang`);
    if (heeftLidwoordNodig(w) && !heeftLidwoord(w.es))
      fouten.push(`${waar}: zelfstandig naamwoord zonder lidwoord ("${w.es}"); schrijf "el ${w.es}" of "la ${w.es}"`);
  });

  (nieuw.sentences || []).forEach((s, i) => {
    const waar = `zin ${i + 1} (${s.id})`;
    // altNorm/altKaal staan buiten deze lus (zie boven): herstelAlt() gebruikt dezelfde twee functies,
    // zodat de reparatie en de keuring niet uit elkaar kunnen lopen.
    eisUniek(s.id, waar); eisVelden(s, "zin", waar);
    if (!/^s\d+$/.test(s.id || "")) fouten.push(`${waar}: id moet s<nummer> zijn`);
    if (!Array.isArray(s.alt) || !s.alt.length) fouten.push(`${waar}: alt moet minstens één variant hebben`);
    else {
      // Zelfde vergelijking als checkSentence() in de app: normaliseren én accenten strippen (de app
      // rekent een antwoord met een missend accent goed). Strenger controleren dan de app zelf doet
      // levert alleen valse afkeuringen op.
      if (!s.alt.map(altKaal).includes(altKaal(s.es))) fouten.push(`${waar}: alt bevat het eigen antwoord niet (ook niet accentloos)`);
      if (s.alt.some(a => a !== String(a).toLowerCase())) fouten.push(`${waar}: alt hoort in kleine letters`);
    }
    if (typeof s.lvl !== "number" || s.lvl < 1 || s.lvl > 5) fouten.push(`${waar}: lvl moet 1-5 zijn`);
    if (!uitlegZegtIets(s.uitleg, s.es))
      fouten.push(`${waar}: uitleg legt niets uit; noem een Spaans woord uit de zin of de regel bij naam`);
  });

  (nieuw.quizzes || []).forEach((q, i) => {
    const waar = `toetsje ${i + 1} (${q.id})`;
    eisUniek(q.id, waar); eisVelden(q, "toets", waar);
    if (!/^q-[a-z0-9-]+$/.test(q.id || "")) fouten.push(`${waar}: id moet q-<slug> zijn`);
    if (!Array.isArray(q.spiek) || !q.spiek.length) fouten.push(`${waar}: spiek moet naar een spiekbriefkaart wijzen`);
    else q.spiek.forEach(idx => {
      if (typeof idx !== "number" || idx < 0 || idx >= inv.cheat.length + (nieuw.cheat || []).length)
        fouten.push(`${waar}: spiek-index ${idx} bestaat niet`);
    });
    if (!Array.isArray(q.vragen) || q.vragen.length < 4) fouten.push(`${waar}: minstens 4 vragen`);
    (q.vragen || []).forEach((v, j) => {
      const w2 = `${waar} vraag ${j + 1}`;
      if (!v.q) fouten.push(`${w2}: q ontbreekt`);
      if (!Array.isArray(v.opts) || v.opts.length < 2) fouten.push(`${w2}: minstens 2 opties`);
      else {
        if (new Set(v.opts.map(String)).size !== v.opts.length) fouten.push(`${w2}: dubbele opties`);
        if (typeof v.c !== "number" || v.c < 0 || v.c >= v.opts.length) fouten.push(`${w2}: c wijst niet naar een optie`);
      }
      if (!v.u) fouten.push(`${w2}: uitleg (u) ontbreekt`);
      if (!v.ue) fouten.push(`${w2}: Engelse uitleg (ue) ontbreekt`);
    });
  });

  (nieuw.cheat || []).forEach((c, i) => {
    const waar = `spiekkaart ${i + 1}`;
    ["titel", "titelEn", "html", "htmlEn"].forEach(v => { if (!c[v]) fouten.push(`${waar}: veld "${v}" ontbreekt`); });
  });

  // verwijzingen uit de lesindeling moeten bestaan
  const alleWoordIds = new Set(inv.words.map(w => w.id).concat((nieuw.words || []).map(w => w.id)));
  const alleZinIds = new Set(inv.sentences.map(s => s.id).concat((nieuw.sentences || []).map(s => s.id)));
  const alleToetsIds = new Set(inv.quizzes.map(q => q.id).concat((nieuw.quizzes || []).map(q => q.id)));
  const checkLes = (l, waar) => {
    (l.words || []).forEach(id => { if (!alleWoordIds.has(id)) fouten.push(`${waar}: onbekend woord-id ${id}`); });
    (l.sents || []).forEach(id => { if (!alleZinIds.has(id)) fouten.push(`${waar}: onbekend zin-id ${id}`); });
    (l.quizzes || []).forEach(id => { if (!alleToetsIds.has(id)) fouten.push(`${waar}: onbekend toets-id ${id}`); });
  };
  Object.keys(nieuw.lessen || {}).forEach(lid => {
    if (!inv.perLes.some(l => l.id === lid)) fouten.push(`lesindeling: les ${lid} bestaat niet`);
    checkLes(nieuw.lessen[lid], `lesindeling ${lid}`);
  });
  (nieuw.nieuweLessen || []).forEach((l, i) => {
    const waar = `nieuwe les ${i + 1} (${l.id})`;
    if (!l.id || !/^[a-z0-9-]+$/.test(l.id)) fouten.push(`${waar}: ongeldig id`);
    if (inv.perLes.some(x => x.id === l.id)) fouten.push(`${waar}: les-id bestaat al`);
    ["titel", "doel", "doelEn"].forEach(v => { if (!l[v]) fouten.push(`${waar}: veld "${v}" ontbreekt`); });
    if (!(l.words || []).length) fouten.push(`${waar}: geen woorden`);
    if (!(l.sents || []).length) fouten.push(`${waar}: geen zinnen`);
    checkLes(l, waar);
  });

  return fouten;
}

/* ---------- schrijven ---------- */

function jsonRegel(obj) { return " " + JSON.stringify(obj); }

function voegToeAanArray(src, naam, items) {
  if (!items || !items.length) return src;
  const { sluit } = vindArray(src, naam);
  // laatste item krijgt een komma, nieuwe items komen elk op een eigen regel vóór de sluithaak
  const voor = src.slice(0, sluit).replace(/\s*$/, "");
  const blok = items.map(jsonRegel).join(",\n");
  return voor + ",\n" + blok + "\n" + src.slice(sluit);
}

function schrijfExtra(src, extra) {
  const { start, eind } = leesExtra(src);
  const tekst = "var EXTRA_CONTENT = " + JSON.stringify(extra, null, 1) + ";";
  return src.slice(0, start) + tekst + src.slice(eind);
}

function bumpVersie(src) {
  const m = /^var APP_VERSIE = "v(\d+)\.(\d+)";$/m.exec(src);
  if (!m) throw new Error("APP_VERSIE niet gevonden");
  const nieuw = "v" + m[1] + "." + (+m[2] + 1);
  return { src: src.replace(m[0], 'var APP_VERSIE = "' + nieuw + '";'), versie: nieuw };
}

// Schrijft alles weg en controleert daarna door opnieuw in te lezen. Klopt de telling niet, dan
// blijft het bestand zoals het was.
function pasToe(nieuw, opties) {
  opties = opties || {};
  const voor = inventaris();
  const fouten = valideer(nieuw, voor);
  const waarschuwingen = altWaarschuwingen(nieuw);
  if (fouten.length) return { ok: false, fouten, waarschuwingen };

  let src = voor.src;
  src = voegToeAanArray(src, "WORDS", nieuw.words);
  src = voegToeAanArray(src, "SENTENCES", nieuw.sentences);
  src = voegToeAanArray(src, "QUIZZES", nieuw.quizzes);
  src = voegToeAanArray(src, "CHEATSHEET", nieuw.cheat);

  const extra = JSON.parse(JSON.stringify(voor.extra));
  Object.keys(nieuw.lessen || {}).forEach(lid => {
    const e = extra.lessen[lid] || (extra.lessen[lid] = { words: [], sents: [], quizzes: [] });
    ["words", "sents", "quizzes", "spiek"].forEach(k => {
      if (!(nieuw.lessen[lid][k] || []).length) return;
      e[k] = (e[k] || []).concat(nieuw.lessen[lid][k]);
    });
  });
  (nieuw.nieuweLessen || []).forEach(l => extra.nieuweLessen.push(l));
  src = schrijfExtra(src, extra);

  const bump = bumpVersie(src);
  src = bump.src;

  if (opties.droog) return { ok: true, droog: true, versie: bump.versie, src, waarschuwingen };

  fs.writeFileSync(INDEX, src);
  fs.writeFileSync(VERSIE, bump.versie + "\n");

  const na = inventaris();
  const verwacht = {
    words: voor.words.length + (nieuw.words || []).length,
    sentences: voor.sentences.length + (nieuw.sentences || []).length,
    quizzes: voor.quizzes.length + (nieuw.quizzes || []).length,
    cheat: voor.cheat.length + (nieuw.cheat || []).length
  };
  const mis = Object.keys(verwacht).filter(k => na[k].length !== verwacht[k]);
  if (mis.length) {
    fs.writeFileSync(INDEX, voor.src);            // terugdraaien
    return { ok: false, fouten: ["telling klopt niet na schrijven: " + mis.join(", ") + " — bestand teruggedraaid"] };
  }
  return { ok: true, versie: bump.versie, aantallen: verwacht, waarschuwingen };
}

module.exports = { altWaarschuwingen, altVoornaamwoorden,
                   INDEX, VERSIE, inventaris, leesArray, leesLessen, leesExtra,
                   valideer, pasToe, volgendeId, voegToeAanArray, bumpVersie,
                   altNorm, altKaal, herstelAlt };

/* ---------- zelftest ---------- */

if (require.main === module && process.argv.includes("--zelftest")) {
  const inv = inventaris();
  console.log("gelezen:", inv.words.length, "leswoorden,", (inv.kern||[]).length, "kernwoorden,", inv.sentences.length, "zinnen,",
              inv.quizzes.length, "toetsjes,", inv.cheat.length, "spiekkaarten,", inv.perLes.length, "lessen");
  const idW = volgendeId(inv.words, "w"), idS = volgendeId(inv.sentences, "s");
  const proef = {
    words: [{ id: idW(1), es: "la prueba", nl: "de proef", en: "the test", tag: "zelftest" }],
    sentences: [{ id: idS(1), lvl: 1, nl: "Dit is een proef.", en: "This is a test.", es: "Esta es una prueba.",
                  alt: ["esta es una prueba"], uitleg: "Proef.", ue: "Test.", tag: "zelftest" }],
    lessen: { [inv.perLes[0].id]: { words: [idW(1)], sents: [idS(1)] } }
  };
  const f = valideer(proef, inv);
  console.log("validatie van een correcte proeflevering:", f.length ? "FOUT: " + f.join("; ") : "schoon ✓");
  const stuk = JSON.parse(JSON.stringify(proef));
  stuk.sentences[0].alt = ["iets anders"];
  stuk.words[0].id = inv.words[0].id;
  const f2 = valideer(stuk, inv);
  console.log("validatie van een kapotte levering vindt", f2.length, "fouten:", f2.join(" | "));
  /* herstelAlt (9 aug). De avondrun keurde twee nachten op rij al zijn eigen zinnen af op het
     alt-veld. Deze vier gevallen zijn precies wat het model aanleverde: geen alt, hoofdletters,
     accenten laten staan, en een echte variant die moet blijven. */
  const altProef = [
    { es: "Me cuesta hablar rápido.", alt: [] },
    { es: "¿Puedo pedirte un favor?", alt: ["Puedo Pedirte un Favor"] },
    { es: "Antes no teníamos televisión en casa.", alt: ["antes no teníamos tele en casa"] },
    { es: "Los sábados salimos a cenar.", alt: undefined }
  ].map(herstelAlt);
  const altGoed = altProef.every(z => z.alt.map(altKaal).includes(altKaal(z.es)))
    && altProef.every(z => z.alt.every(a => a === a.toLowerCase()))
    && altProef[1].alt.length === 1            // de hoofdletter-variant is dezelfde zin, dus ontdubbeld
    && altProef[2].alt.length === 2;           // de echte variant blijft staan
  console.log("herstelAlt op de vier gevallen van 9 aug:", altGoed ? "schoon \u2713" : "FOUT: " + JSON.stringify(altProef.map(z => z.alt)));
  const alsZin = valideer({ sentences: [{ id: idS(2), lvl: 1, nl: "Proef twee.", en: "Test two.",
      uitleg: "Proef.", ue: "Test.", tag: "zelftest", ...herstelAlt({ es: "Me cuesta hablar rápido.", alt: [] }) }] }, inv);
  console.log("een herstelde zin komt door de poort:", alsZin.length ? "FOUT: " + alsZin.join("; ") : "ja \u2713");

  const altFout = altWaarschuwingen({ sentences: [{ id: "s158", es: "Mi hija se parece a mi.",
      alt: ["mi hija me parece pero es distinta"] }] });
  console.log("de fout van 10 aug (se wordt me):", altFout.length === 1 ? "gezien \u2713" : "GEMIST");
  const altStil = altWaarschuwingen({ sentences: [
    { id: "t1", es: "\u00bfMe lo puedes prestar?", alt: ["\u00bfpuedes prest\u00e1rmelo?"] },
    { id: "t2", es: "Se est\u00e1 duchando.", alt: ["est\u00e1 duch\u00e1ndose"] },
    { id: "t3", es: "Te lo voy a decir.", alt: ["voy a dec\u00edrtelo"] },
    { id: "t4", es: "Mis compa\u00f1eros llegan tarde.", alt: ["llegan tarde mis compa\u00f1eros"] },
    { id: "t5", es: "Quiero escribirlas hoy.", alt: ["hoy quiero escribirlas"] }
  ] });
  console.log("verplaatst voornaamwoord en -eros geven geen vals alarm:",
    altStil.length ? "FOUT: " + altStil.join("; ") : "klopt \u2713");
  console.log("op de inhoud van nu:", altWaarschuwingen(inv).length + " alt om na te lezen");

  const droog = pasToe(proef, { droog: true });
  console.log("droge schrijfbeurt:", droog.ok ? "ok, wordt " + droog.versie : "MISLUKT: " + droog.fouten);
  if (droog.ok) {
    fs.writeFileSync("/tmp/vamos-droog.html", droog.src);
    console.log("resultaat weggeschreven naar /tmp/vamos-droog.html (index.html is niet aangeraakt)");
  }
}
"""

CUR_TEKST = r"""#!/usr/bin/env node
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

function analyseer(logboek, inv) {
  const fouten = foutenSamenvatten(logboek);
  const zinnenPerTag = {};
  inv.sentences.forEach(s => { zinnenPerTag[s.tag] = (zinnenPerTag[s.tag] || 0) + 1; });

  // (a) taalverschijnselen: fouten op zinnen en dictado, gewogen tegen hoeveel oefenzinnen er al zijn
  const zinGaten = groepeer(fouten.filter(f => f.type === "zin" || f.type === "dictado"), f => f.tag)
    .map(g => {
      const zinnen = zinnenPerTag[g.sleutel] || 0;
      return { soort: "verschijnsel", tag: g.sleutel, fouten: g.fouten, items: g.items.length,
               zinnen, score: g.fouten / Math.max(1, zinnen) };
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

  return { zinGaten, woordGaten, toetsGaten };
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

function promptTegenlezerToets(qz) {
  return `Je bent corrector Spaans (Spanje, A2/B1) voor een leerapp. Hieronder een grammatica-toetsje.
Controleer per vraag: is het Spaans correct, is er precies één juist antwoord, wijst "c" naar dat
antwoord, klopt de uitleg, en SLAAT DE ZIN ERGENS OP? Een vraag als "Las mesas son ___ (de tafels zijn
verlegen)" is grammaticaal in orde en toch fout: niemand zegt dat. Ook: staan er geen twee identieke
opties tussen. Keur het hele toetsje af zodra één vraag fout is.

${JSON.stringify(qz, null, 1)}

Antwoord met UITSLUITEND JSON: {"ok":true,"problemen":["..."]}`;
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
    const uit = await vraagModel(motor, promptTegenlezerToets(schoon.qz), 2000);
    if (uit && uit.ok === true) return schoon.qz;
    bezwaren = (uit && uit.problemen) || ["de corrector gaf geen bruikbaar oordeel"];
    console.error(`    toetsje afgekeurd (poging ${poging}): ${bezwaren.join("; ")}`);
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

Gebruik exact deze ids:
- woorden: ${ids.words.join(", ")}
- zinnen: ${ids.sents.join(", ")}
- toetsje: ${ids.quiz}

Antwoord met UITSLUITEND JSON in deze vorm:
{"titel":"Spaanse titel","doel":"Nederlands lesdoel","doelEn":"English lesson goal",
 "niveau":"${niveau}",
 "words":[{"id":"${ids.words[0]}","es":"...","nl":"...","en":"...","tag":"<thema-slug>"}],
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
        const uit = await vraagModel(motor, promptTegenlezerToets(les.quiz), 2000);
        if (!uit || uit.ok !== true) {
          console.error("    toetsje van de nieuwe les afgekeurd, de les gaat door zonder");
          les.quiz = null;
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

  // gaten op één stapel, zwaarste eerst; verschijnselen wegen zwaarder dan losse woorden omdat een
  // regel die je niet snapt tientallen items blijft besmetten
  const gaten = [].concat(an.zinGaten, an.woordGaten).sort((a, b) => b.score - a.score);
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
"""

SCHRIJF_TEKST = r"""// v23.42: schrijven staat weer in de dagles, als vaste vierde stap van drie zinnen.
//
// Waarom hier een suite omheen: dit blok is er in v20.5 uitgehaald omdat Stefan erop afhaakte, en op
// 11 aug op zijn verzoek teruggezet in een kleinere vorm. Twee keer hetzelfde blok verplaatsen zonder
// dat iets de vorm bewaakt, en de derde keer staat het weer op tien zinnen achter het einde van de
// les. Wat hier vastligt is dus niet dat schrijven bestaat, maar dat het klein is en binnen de les.
const { chromium } = require('playwright');
let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }
const U = 'http://localhost:8321/espanol-stefan.html';

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 420, height: 1000 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));

  await page.goto(U); await page.waitForTimeout(300);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.goto(U); await page.waitForTimeout(700);
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'Schr' + Date.now());
  await page.click('button:has-text("A2 ·")');
  await page.click('#btnNewProf');
  await page.waitForTimeout(1100);
  await page.evaluate(() => {
    S.lang = 'nl'; S.tour = true;
    try { persist(); } catch (e) {}
    const w = document.getElementById('tourWrap'); if (w && w.remove) w.remove();
  });

  console.log('\n-- na de toetsjes komt schrijven, niet het einde --');
  const na = await page.evaluate(() => {
    lesFlow = { stap: 'toetsjes', quizzesTeDoen: [], gekozenSpel: null, vertalenTeGaan: 0 };
    lesFlowVolgendeKern();
    return { stap: lesFlow && lesFlow.stap, vaardigheid: lesFlow && lesFlow.vaardigheid,
             spel: lesFlow && lesFlow.gekozenSpel, teGaan: lesFlow && lesFlow.vertalenTeGaan,
             totaal: lesFlow && lesFlow.vertalenTotaal, vast: SCHRIJF_PER_LES,
             num: lesFlowStapNum(), naam: lesFlowStapNaam(),
             zichtbaar: !document.getElementById('tab-vertalen').classList.contains('hidden') };
  });
  ok(na.stap === 'produceren' && na.vaardigheid === 'schrijven', 'de les gaat door naar schrijven (' + na.stap + '/' + na.vaardigheid + ')');
  ok(na.zichtbaar, 'en het scherm staat open');
  ok(na.num === 4 && /Schrijven/.test(na.naam || ''), 'het is stap 4 en heet Schrijven (' + na.num + ' ' + na.naam + ')');

  console.log('\n-- drie zinnen, niet tien --');
  ok(na.vast === 3, 'SCHRIJF_PER_LES is 3 (' + na.vast + ')');
  ok(na.teGaan === 3 && na.totaal === 3, 'de teller begint op drie (' + na.teGaan + '/' + na.totaal + ')');
  const kop = await page.evaluate(() => {
    const k = document.querySelector('#tab-vertalen .kicker');
    return (k ? k.innerText : '').replace(/\s+/g, ' ');
  });
  ok(/1\/3/.test(kop) || /4\/4/.test(kop), 'de kop zegt waar je bent (' + kop + ')');

  console.log('\n-- na de derde zin is de les af --');
  const af = await page.evaluate(() => {
    for (let i = 0; i < 3; i++) {
      if (!lesFlow || lesFlow.stap !== 'produceren') break;
      lesFlow.vertalenTeGaan--;
      if (lesFlow.vertalenTeGaan <= 0) { S.lesFlowSpel.vertalen = today(); lesFlowVolgende(); }
    }
    return { flow: lesFlow ? lesFlow.stap : null, klaar: !!(S.lesFlow || {})[today()],
             schrijvenGehad: (S.lesFlowSpel || {}).schrijven === today() ||
                             (S.lesFlowSpel || {}).vertalen === today() };
  });
  ok(af.flow === null, 'de les is afgelopen na de derde zin');
  ok(af.klaar, 'en telt als afgemaakte dagles');
  ok(af.schrijvenGehad, 'schrijven staat vandaag afgevinkt, dus je krijgt het niet nog eens voorgesteld');

  console.log('\n-- zonder zinnen valt de les niet stil --');
  const leeg = await page.evaluate(() => {
    const echt = allowedSentIds;
    allowedSentIds = function () { return []; };
    try {
      lesFlow = { stap: 'toetsjes', quizzesTeDoen: [], gekozenSpel: null, vertalenTeGaan: 0 };
      lesFlowVolgendeKern();
      return { flow: lesFlow ? lesFlow.stap : null };
    } finally { allowedSentIds = echt; }
  });
  ok(leeg.flow === null, 'heb je nog geen zinnen vrijgespeeld, dan sluit de les gewoon af');

  console.log('\n-- Adivina laat het lidwoord zien --');
  const adiv = await page.evaluate(() => {
    const pool = adivPool();
    const met = pool.filter((w) => /^(el|la) /.test(w.es));
    const stuk = met.filter((w) => /^(el|la) /.test(w.plat) || /\s/.test(w.plat));
    return { n: pool.length, metLidwoord: met.length, stuk: stuk.length,
             vb: met.slice(0, 2).map((w) => w.es + ' -> ' + w.plat) };
  });
  ok(adiv.metLidwoord > 50, 'de vijver bevat woorden mét lidwoord (' + adiv.metLidwoord + ' van ' + adiv.n + ')');
  ok(adiv.stuk === 0, 'maar op het bord staat alleen de kern (' + adiv.vb.join(', ') + ')');

  ok(errors.length === 0, 'geen JS-fouten (' + errors.length + ')' + (errors[0] ? ' ' + errors[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' PLAYWRIGHT-TEST(S) GEFAALD'); process.exit(1); }
  console.log('\nALLE PLAYWRIGHT-TESTS GESLAAGD');
})();
"""

ADIV_TEKST = r"""// v23.39: Adivina, het negende spel. Lingo met je eigen woordenschat.
//
// Wat deze suite vastlegt, en waarom precies dit:
//   - de kleurregel. Een letter die twee keer in je gok staat en een keer in het doel mag een keer
//     oranje worden en niet twee keer. Dat is de enige regel in dit spel die je met blote ogen niet
//     ziet als hij fout is: het voelt gewoon "raar".
//   - de eerste letter krijg je en die kun je niet weggummen. Zonder die letter is een woord van
//     vijf letters in een vreemde taal geen puzzel maar een gok.
//   - een spel duwt een woord tot doosje 3 en niet verder. Dat is SPEL_PLAFOND en het is de afspraak
//     die dit spel eerlijk houdt tegenover de balk op je voortgangspagina.
//   - elke gok telt als beurt. Sinds v23.38 is dat de teller waar je week en je gemeten tijd op
//     staan; een spel dat trackPoging overslaat is een half uur dat nergens terugkomt.
const { chromium } = require('playwright');
let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }
const U = 'http://localhost:8321/espanol-stefan.html';

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 420, height: 1000 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));

  await page.goto(U); await page.waitForTimeout(300);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.goto(U); await page.waitForTimeout(700);
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'Adiv' + Date.now());
  await page.click('button:has-text("A2 ·")');
  await page.click('#btnNewProf');
  await page.waitForTimeout(1000);
  await page.evaluate(() => {
    S.lang = 'nl'; S.tour = true; S.speelAlles = true;
    try { persist(); } catch (e) {}
    const w = document.getElementById('tourWrap'); if (w && w.remove) w.remove();
  });

  console.log('\n-- de kleurregel --');
  const kleur = await page.evaluate(() => ({
    dubbelGok: adivKleur('sssss', 'casas'),   // twee s in het doel, vijf in de gok
    oranje: adivKleur('sacas', 'casas'),      // verschoven letters
    niets: adivKleur('mmmmm', 'casas')
  }));
  ok(JSON.stringify(kleur.dubbelGok) === JSON.stringify(['weg', 'weg', 'goed', 'weg', 'goed']),
    'vijf keer dezelfde letter levert alleen de twee juiste plekken op (' + kleur.dubbelGok.join(',') + ')');
  ok(JSON.stringify(kleur.oranje) === JSON.stringify(['bijna', 'goed', 'bijna', 'goed', 'goed']),
    'een letter op de verkeerde plek wordt oranje (' + kleur.oranje.join(',') + ')');
  ok(kleur.niets.every((k) => k === 'weg'), 'een letter die er niet in zit blijft grijs');

  console.log('\n-- de vijver --');
  const pool = await page.evaluate(() => {
    const l = adivPool();
    /* v23.42: es is wat je te zien krijgt en dat is "el coche", plat is wat op het bord staat en dat
       is "coche". De eis van losse letters geldt dus voor plat en niet voor es. */
    return { n: l.length, fout: l.filter((w) => [5, 6].indexOf(w.plat.length) === -1 || /[^a-z]/.test(w.plat)).length,
             zonderId: l.filter((w) => !w.id).length };
  });
  ok(pool.n >= 100, 'er zijn genoeg woorden om mee te spelen (' + pool.n + ')');
  ok(pool.fout === 0, 'alleen losse woorden van vijf of zes letters, zonder ñ');
  ok(pool.zonderId === 0, 'en allemaal met een id, want anders kan het spel je woordjes niet raken');

  console.log('\n-- het scherm is bereikbaar en speelt --');
  await page.evaluate(() => { funView = null; show('speeltuin'); });
  await page.waitForTimeout(400);
  const inMenu = await page.evaluate(() => !!document.getElementById('ftAdiv'));
  ok(inMenu, 'Adivina staat in de speeltuin');
  await page.evaluate(() => { document.getElementById('ftAdiv').click(); });
  await page.waitForTimeout(400);

  // een gecontroleerd doelwoord, anders hangt de test aan het toeval van adivKies()
  const doel = await page.evaluate(() => {
    const w = adivPool().filter((x) => x.plat.length === 5)[0];
    S.srs[w.id] = { box: 1, due: today(), n: 1 };
    S.dagStats = {};
    adivSpel = { id: w.id, es: w.es, nl: w.nl, doel: w.plat, len: 5, gok: [], nu: w.plat.charAt(0),
                 hint: false, klaar: 0, xp: 0 };
    adivBewaar(); renderFunAdivina();
    return { plat: w.plat, id: w.id, nl: w.nl };
  });

  const start = await page.evaluate(() => ({
    nu: adivSpel.nu,
    vakken: document.querySelectorAll('.adivVak').length,
    toetsen: document.querySelectorAll('[data-adivk]').length
  }));
  ok(start.nu.length === 1 && start.nu === doel.plat.charAt(0), 'de eerste letter staat er al');
  ok(start.vakken === 25, 'vijf rijen van vijf vakken (' + start.vakken + ')');
  ok(start.toetsen >= 28, 'er staat een toetsenbord (' + start.toetsen + ' toetsen)');

  console.log('\n-- de eerste letter kun je niet weghalen --');
  await page.evaluate(() => { adivWis(); adivWis(); adivWis(); });
  const naWis = await page.evaluate(() => adivSpel.nu);
  ok(naWis.length === 1, 'wissen stopt bij de eerste letter (' + naWis + ')');

  console.log('\n-- raden gaat via het toetsenbord --');
  // een foute gok van de goede lengte: de rest van het woord omgedraaid
  const gok1 = doel.plat.charAt(0) + doel.plat.slice(1).split('').reverse().join('');
  const anders = gok1 !== doel.plat ? gok1 : doel.plat.slice(0, 4) + (doel.plat.charAt(4) === 'a' ? 'o' : 'a');
  for (const c of anders.slice(1)) {
    await page.evaluate((k) => { document.querySelector("[data-adivk='" + k + "']").click(); }, c);
  }
  const voorRaden = await page.evaluate(() => adivSpel.nu);
  ok(voorRaden === anders, 'de letters komen in het vak terecht (' + voorRaden + ')');
  await page.evaluate(() => { document.querySelector("[data-adivk='@doe']").click(); });
  await page.waitForTimeout(200);
  const na1 = await page.evaluate(() => ({
    gok: adivSpel.gok.slice(), nu: adivSpel.nu, klaar: adivSpel.klaar,
    pog: (S.dagStats[today()] || {}).pogingen || 0, fouten: (S.dagStats[today()] || {}).fouten || 0
  }));
  ok(na1.gok.length === 1 && na1.gok[0] === anders, 'de gok staat op het bord');
  ok(na1.nu.length === 1, 'en de volgende rij begint weer met de eerste letter');
  ok(na1.pog === 1 && na1.fouten === 1, 'de gok telt als beurt, en als foute beurt (' + na1.pog + '/' + na1.fouten + ')');

  console.log('\n-- een gok van de verkeerde lengte doet niets --');
  await page.evaluate(() => { adivSpel.nu = adivSpel.doel.slice(0, 3); adivDoe(); });
  const naKort = await page.evaluate(() => adivSpel.gok.length);
  ok(naKort === 1, 'een half woord wordt niet ingediend');

  console.log('\n-- winnen: punten, doosje, reeks --');
  const win = await page.evaluate(() => {
    const xpVoor = S.txp || 0;
    adivSpel.nu = adivSpel.doel;
    adivDoe();
    return { klaar: adivSpel.klaar, xp: adivSpel.xp, xpErbij: (S.txp || 0) - xpVoor,
             box: (S.srs[adivSpel.id] || {}).box, reeks: S.adiv.reeks, best: S.adiv.best,
             gewonnen: S.adiv.gewonnen, gespeeld: S.adiv.gespeeld,
             pog: (S.dagStats[today()] || {}).pogingen || 0 };
  });
  ok(win.klaar === 1, 'het spel is gewonnen');
  ok(win.xp === 8 && win.xpErbij === 8, 'twee pogingen levert 8 punten op (' + win.xp + ')');
  ok(win.box === 2, 'het woord schuift een doosje op (' + win.box + ')');
  ok(win.reeks === 1 && win.best === 1, 'de reeks staat op 1');
  ok(win.gewonnen === 1 && win.gespeeld === 1, 'de teller klopt (' + win.gewonnen + '/' + win.gespeeld + ')');
  ok(win.pog === 2, 'ook de winnende gok telt als beurt (' + win.pog + ')');

  console.log('\n-- het plafond van doosje 3 geldt ook hier --');
  const plafond = await page.evaluate(() => {
    const w = adivPool().filter((x) => x.plat.length === 5)[1];
    S.srs[w.id] = { box: SPEL_PLAFOND, due: today(), n: 5 };
    adivSpel = { id: w.id, es: w.es, nl: w.nl, doel: w.plat, len: 5, gok: [], nu: w.plat.charAt(0),
                 hint: false, klaar: 0, xp: 0 };
    adivSpel.nu = adivSpel.doel; adivDoe();
    return { box: S.srs[w.id].box, plafond: SPEL_PLAFOND };
  });
  ok(plafond.box === plafond.plafond, 'een woord op het plafond blijft daar (' + plafond.box + ')');

  console.log('\n-- de hint kost de helft --');
  const hint = await page.evaluate(() => {
    const w = adivPool().filter((x) => x.plat.length === 5)[2];
    adivSpel = { id: w.id, es: w.es, nl: w.nl, doel: w.plat, len: 5, gok: [], nu: w.plat.charAt(0),
                 hint: true, klaar: 0, xp: 0 };
    adivSpel.nu = adivSpel.doel; adivDoe();
    return adivSpel.xp;
  });
  ok(hint === 5, 'in een poging met hint: 5 in plaats van 10 (' + hint + ')');

  console.log('\n-- verliezen laat het woord zien --');
  const verlies = await page.evaluate(() => {
    const w = adivPool().filter((x) => x.plat.length === 5)[3];
    adivSpel = { id: w.id, es: w.es, nl: w.nl, doel: w.plat, len: 5, gok: [], nu: w.plat.charAt(0),
                 hint: false, klaar: 0, xp: 0 };
    const mis = w.plat.charAt(0) + (w.plat.slice(1).split('').reverse().join('') === w.plat.slice(1)
      ? w.plat.slice(1, 4) + (w.plat.charAt(4) === 'a' ? 'o' : 'a')
      : w.plat.slice(1).split('').reverse().join(''));
    for (let i = 0; i < 5; i++) { adivSpel.nu = mis; adivDoe(); }
    renderFunAdivina();
    const t = document.getElementById('funCard').innerText;
    return { klaar: adivSpel.klaar, gokken: adivSpel.gok.length, es: w.es,
             toont: t.indexOf(w.es) !== -1, kbWeg: document.querySelectorAll('[data-adivk]').length };
  });
  ok(verlies.klaar === -1 && verlies.gokken === 5, 'na vijf pogingen is het klaar');
  ok(verlies.toont, 'en het woord staat er, met zijn accenten (' + verlies.es + ')');
  ok(verlies.kbWeg === 0, 'het toetsenbord is weg als er niets meer te raden valt');

  console.log('\n-- een half spel overleeft een herlading --');
  await page.evaluate(() => {
    const w = adivPool().filter((x) => x.plat.length === 6)[0];
    adivSpel = { id: w.id, es: w.es, nl: w.nl, doel: w.plat, len: 6, gok: [], nu: w.plat.charAt(0),
                 hint: false, klaar: 0, xp: 0 };
    adivSpel.nu = w.plat.charAt(0) + w.plat.slice(1).split('').reverse().join('');
    if (adivSpel.nu !== w.plat) adivDoe(); else { adivSpel.gok.push(adivSpel.nu); adivBewaar(); }
  });
  await page.reload(); await page.waitForTimeout(900);
  const herstel = await page.evaluate(() => {
    funView = 'adiv'; adivSpel = null; show('speeltuin'); renderFunAdivina();
    return { gokken: adivSpel ? adivSpel.gok.length : -1, len: adivSpel ? adivSpel.len : 0 };
  });
  ok(herstel.gokken === 1 && herstel.len === 6, 'de gedane gok staat er nog na een herlading');

  ok(errors.length === 0, 'geen JS-fouten (' + errors.length + ')' + (errors[0] ? ' ' + errors[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' PLAYWRIGHT-TEST(S) GEFAALD'); process.exit(1); }
  console.log('\nALLE PLAYWRIGHT-TESTS GESLAAGD');
})();
"""

LEER_TEKST = r"""// Playwright-test voor v20.5 - de leermachine.
//
// Stefan, 6 augustus, drie klachten in een adem:
//   "ik merk dat ik nu meer de toetsjes automatisch invul omdat ik geleerd heb wat een goede
//    antwoord is (dat is ook zo bij babbel) ipv dat echt het grammaticale concept wordt getest"
//   "drie woordjes is denk ik weinig toch? moet altijd en deel herhaling inzitten maar ook iedere
//    dag nieuwe woordjes"
//   "als je klaar bent met je minimale ja dan wil je een suggestie of meer suggesties waarom een
//    bepaald spel of oefening goed voor je is en alle fouten die maak moeten weer terug, mijn
//    leermachine is"
//
// Deze suite bewaakt de vier antwoorden daarop, in de volgorde waarin ze gebouwd zijn:
//   1. een concept heeft een geheugen (S.gram), gevoed door El Corrector, de toetsjes en de les zelf
//   2. de grammatica van de dag wordt gekozen door je eigen fout, niet door een vaste lijst
//   3. de voorbeelden worden per start gegenereerd, dus het antwoord onthouden kan niet meer
//   4. de les stopt na de toets; wat daarna komt is een voorstel met een reden, en stoppen kan altijd
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  page.on('console', (msg) => { if (msg.type() === 'error') errors.push('console.error: ' + msg.text()); });

  let fails = 0;
  function ok(cond, name) {
    if (cond) { console.log('PASS', name); }
    else { fails++; console.log('FAIL', name); }
  }

  await page.goto('http://localhost:8321/espanol-stefan.html');
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(400);

  await page.fill('input[placeholder="Name"]', 'PwLeer' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(400);

  /* ---------------- 1. het geheugen ---------------- */
  const geheugen = await page.evaluate(() => {
    return { erin: !!S.gram, leeg: Object.keys(S.gram || {}).length === 0, aantal: GC_CONCEPTEN.length };
  });
  ok(geheugen.erin === true, 'S.gram bestaat na een verse start');
  ok(geheugen.leeg === true, 'en hij begint leeg: niets wordt voor je ingevuld');
  ok(geheugen.aantal >= 9, 'er zijn minstens negen concepten (' + geheugen.aantal + ')');

  // El Corrector is de bron die Stefan zelf aanwees ("ik maakte deze fout, neem je dat nu mee?")
  const corr = await page.evaluate(() => {
    S.gram = {};
    corrSrsBij('muymucho', false);
    const st = S.gram.muymucho || {};
    return { fout: st.fout, box: st.box, due: st.due, morgen: addDays(today(), 1) };
  });
  ok(corr.fout === 1, 'een fout in El Corrector komt aan bij het concept muy/mucho');
  ok(corr.box === 0, 'en zet het doosje terug naar nul');
  ok(corr.due === corr.morgen, 'de fout komt morgen terug, niet over een week (' + corr.due + ')');

  // de toetsjes zijn de tweede bron: die kenden hun eigen concept niet
  const quiz = await page.evaluate(() => {
    S.gram = {};
    const qz = QUIZZES.filter((q) => gcConceptenVoorQuiz(q).length)[0];
    if (!qz) return { gevonden: false };
    const cids = gcConceptenVoorQuiz(qz);
    quizSrsBij(qz, 1);
    return { gevonden: true, cids: cids, box: (S.gram[cids[0]] || {}).box };
  });
  ok(quiz.gevonden === true, 'minstens een toetsje is aan een concept te koppelen');
  ok(quiz.box === 1, 'een gehaald toetsje schuift het concept een doosje op');

  // en goed blijven antwoorden schuift hem verder weg, precies volgens GRAM_BOX
  const dozen = await page.evaluate(() => {
    S.gram = {};
    gramBij('serestar', true); gramBij('serestar', true); gramBij('serestar', true);
    const st = S.gram.serestar;
    return { box: st.box, due: st.due, verwacht: addDays(today(), GRAM_BOX[3]) };
  });
  ok(dozen.box === 3, 'drie keer goed is doosje drie');
  ok(dozen.due === dozen.verwacht, 'en dan komt hij pas over ' + 'GRAM_BOX[3]' + ' dagen terug');

  /* ---------------- 2. de keuze volgt je fout ---------------- */
  const keuze = await page.evaluate(() => {
    S.gram = {};
    lesFlow = { stap: null, quizzesTeDoen: [] };
    const zonder = lesFlowGramId();
    corrSrsBij('muymucho', false);
    const met = lesFlowGramId();
    return { zonder: zonder, met: met };
  });
  ok(keuze.met === 'concept-muymucho', 'na die fout gaat de grammatica van vandaag over muy/mucho (' + keuze.met + ')');
  ok(keuze.zonder !== keuze.met, 'zonder fout had hij iets anders gekozen (' + keuze.zonder + ')');

  /* ---------------- 3. de voorbeelden worden gemaakt, niet opgeslagen ---------------- */
  const vers = await page.evaluate(() => {
    const a = gcVernieuw('concept-muymucho').stappen[0].vragen.map((q) => q.v).join('|');
    const b = gcVernieuw('concept-muymucho').stappen[0].vragen.map((q) => q.v).join('|');
    const les = gcOnderwerp('concept-muymucho');
    const vr = les.stappen[0].vragen;
    const stil = gcOnderwerp('concept-muymucho').stappen[0].vragen[1].v === vr[1].v;
    return {
      anders: a !== b,
      aantal: vr.length,
      begripEerst: vr[0].v === gcConcept('muymucho').begrip.v,
      uniek: vr.slice(1).map((q) => q.v).filter((v, i, arr) => arr.indexOf(v) === i).length,
      stil: stil,
      concept: les.concept,
      stappen: les.stappen.length
    };
  });
  ok(vers.anders === true, 'twee keer starten geeft twee keer andere voorbeelden');
  ok(vers.stil === true, 'maar binnen een sessie staat de vraag stil: hij verandert niet onder je handen');
  ok(vers.aantal === 1 + GC_VOORBEELDEN_VERWACHT(), 'een microles is een begripsvraag plus vier voorbeelden (' + vers.aantal + ')');
  ok(vers.begripEerst === true, 'en de eerste vraag gaat over de regel zelf, niet over een zin');
  ok(vers.uniek === vers.aantal - 1, 'de vier voorbeelden zijn onderling verschillend');
  ok(vers.concept === 'muymucho', 'de les weet bij welk concept hij hoort, dus de fout komt terug bij de bron');
  ok(vers.stappen === 1, 'het is een microles: een stap, geen wizard van zes');

  // de derde voeder: fout in de microles zelf
  const inLes = await page.evaluate(() => {
    S.gram = {};
    gwStart('concept-serestar');
    const q = gwOnderwerp(gwSess.id).stappen[0].vragen[0];
    const mis = q.g === 0 ? 1 : 0;
    gwKies(mis);
    const st = S.gram.serestar || {};
    gwSluit();
    return { fout: st.fout, due: st.due, morgen: addDays(today(), 1) };
  });
  ok(inLes.fout === 1, 'een fout in de microles zelf komt ook bij het concept aan');
  ok(inLes.due === inLes.morgen, 'en zet hem net zo goed op morgen');

  /* ---------------- 4. de dagportie ---------------- */
  const portie = await page.evaluate(() => {
    S.doelMin = 10;
    const basis = { nieuw: dagPortieNieuw(), herhaal: dagPortieHerhaal(), cap: dagPortieCap(), vloer: dagPortieVloer() };
    // veel fout: de regelaar mag knijpen, maar niet door de vloer
    S.tempo = null;
    const knijp = (function () {
      const echt = leerKpi;
      leerKpi = function () { return { recent: { pog: 100, pct: 40 } }; };
      const t = tempoVandaag();
      leerKpi = echt;
      return t;
    })();
    // en herstelmodus houdt nieuwe woorden overeind
    S.tempo = null;
    const herstel = (function () {
      const echt = herstelModus;
      herstelModus = function () { return true; };
      const t = tempoVandaag();
      herstelModus = echt;
      return t;
    })();
    S.tempo = null;
    return { basis: basis, knijp: knijp.n, herstel: herstel.n };
  });
  ok(portie.basis.nieuw >= 5, 'bij tien minuten zijn er minstens vijf nieuwe woorden per dag (' + portie.basis.nieuw + ')');
  ok(portie.basis.herhaal >= portie.basis.nieuw, 'en er zit altijd meer herhaling in dan nieuw (' + portie.basis.herhaal + ')');
  ok(portie.basis.cap === portie.basis.nieuw + portie.basis.herhaal, 'de dagportie is precies de som van die twee potten');
  ok(portie.knijp >= portie.basis.vloer, 'bij veel fouten knijpt de regelaar tot de vloer, niet eronder (' + portie.knijp + ')');
  ok(portie.herstel >= 3, 'zelfs in herstelmodus krijg je elke dag nieuwe woorden (' + portie.herstel + ')');

  /* ---------------- 5. na de toets: drie zinnen schrijven, en dan klaar ----------------
     v20.5 haalde het hele productieblok uit de verplichte les omdat Stefan erop afhaakte: vijf tot
     tien zinnen, achter het punt waarop je al klaar was. v23.42 zet er één stuk van terug, op zijn
     verzoek van 11 aug, maar klein: drie zinnen, binnen de les. Wat deze suite bewaakt is dus niet
     dat schrijven bestaat, maar dat het bij drie zinnen blijft en dat dictado er niet mee terugkomt.
     Zie ook pw-schrijven.js. */
  const stopt = await page.evaluate(() => {
    S.xp = {}; S.dag = {}; S.ritme = { wanneer: 'stil' }; S.lesFlow = {};
    lesFlow = { stap: 'toetsjes', quizzesTeDoen: [], gekozenSpel: null, vertalenTeGaan: 0 };
    lesFlowVolgende();
    const naToets = { stap: lesFlow && lesFlow.stap, spel: lesFlow && lesFlow.gekozenSpel,
                      zinnen: lesFlow && lesFlow.vertalenTotaal };
    // de drie zinnen afwerken
    for (let i = 0; i < 5 && lesFlow && lesFlow.stap === 'produceren'; i++) {
      lesFlow.vertalenTeGaan--;
      if (lesFlow.vertalenTeGaan <= 0) { S.lesFlowSpel.vertalen = today(); lesFlowVolgende(); }
    }
    const feest = document.getElementById('feestWrap');
    if (feest && feest.remove) feest.remove();
    return { naToets, flowWeg: lesFlow === null, tekst: document.getElementById('lessonList').innerText };
  });
  ok(stopt.naToets.spel === 'vertalen' && stopt.naToets.zinnen === 3,
    'na de toets volgen drie zinnen schrijven (' + stopt.naToets.spel + ', ' + stopt.naToets.zinnen + ')');
  ok(stopt.naToets.spel !== 'dictado', 'en geen verplicht dictado-blok');
  ok(stopt.flowWeg === true, 'daarna is de les klaar');
  // let op de /i: de kicker staat in CSS op text-transform, dus innerText leest hem in kapitalen
  ok(/les afgerond|session complete/i.test(stopt.tekst), 'en je krijgt het afgerond-scherm');

  /* ---------------- 6. de voorstellen, met een reden ---------------- */
  const voorstel = await page.evaluate(() => {
    S.gram = {}; S.xp = {}; S.dag = {}; S.ritme = { wanneer: 'stil' }; S.lesFlow = {};
    corrSrsBij('muymucho', false);
    lesFlow = { stap: 'produceren' };
    lesFlowKlaar();
    const feest = document.getElementById('feestWrap');
    if (feest && feest.remove) feest.remove();
    const knoppen = document.querySelectorAll('#lessonList [data-voorstel]');
    const kaarten = [].slice.call(knoppen).map((b) => b.closest('.card').innerText);
    return {
      aantal: knoppen.length,
      kaarten: kaarten,
      eerste: kaarten[0] || '',
      primair: (document.querySelector('#lessonList .card .row button.primary') || {}).textContent || ''
    };
  });
  ok(voorstel.aantal >= 1 && voorstel.aantal <= 2, 'na de les staan er hoogstens twee voorstellen (' + voorstel.aantal + ')');
  ok(/mucho/i.test(voorstel.eerste), 'het eerste voorstel is de fout van net, niet een willekeurig spel');
  ok(/de mist in|wrong/i.test(voorstel.eerste), 'en er staat bij waarom juist dit voorstel (Stefan: "waarom een bepaald spel goed voor je is")');
  ok(voorstel.kaarten.some((k) => /leuk|fun/i.test(k)), 'daarnaast staat er iets wat gewoon leuk is');
  ok(/Klaar voor vandaag|Done for today/.test(voorstel.primair), 'en stoppen blijft de hoofdknop, ook met voorstellen erbij');

  // het voorstel doet ook echt wat het belooft
  const gedrukt = await page.evaluate(() => {
    document.querySelector('#lessonList [data-voorstel]').click();
    return { id: gwSess ? gwSess.id : null };
  });
  ok(gedrukt.id === 'concept-muymucho', 'op het voorstel drukken opent die microles (' + gedrukt.id + ')');

  // en de opt-in op het productieblok bestaat nog, want de oefening zelf was niet het probleem
  const extra = await page.evaluate(() => {
    gwSluit();
    S.lesFlowSpel = {};
    lesFlowExtra('luisteren');
    return { stap: lesFlow.stap, extra: !!lesFlow.extra, v: lesFlow.vaardigheid };
  });
  ok(extra.stap === 'produceren' && extra.extra === true, 'lesFlowExtra() zet het productieblok aan als keuze');
  ok(extra.v === 'luisteren', 'met precies de vaardigheid die je gekozen hebt');

  /* ---------------- 7. de tweede lichting (v20.6) ----------------
     Stefan: "maar 9 concepten is dat niet veel te weinig voor stevig a0- a1 en a2 niveau?"
     Ja. Deze suite bewaakt dat het er nu drieentwintig zijn, dat elk concept ook echt werkt
     (uitleg, begripsvraag, vier verse voorbeelden zonder uitzondering) en dat geen enkele
     Corrector-regel nog in het niets verdwijnt. */
  const lichting = await page.evaluate(() => {
    const stuk = [];
    GC_CONCEPTEN.forEach((c) => {
      const o = gcVernieuw('concept-' + c.id);
      const vr = (o && o.stappen[0].vragen) || [];
      const heel = vr.length === 5 && vr.every((q) =>
        q.o && q.o.length >= 2 && q.g >= 0 && q.g < q.o.length && q.o[q.g] && q.w &&
        q.o.filter((x, i, a) => a.indexOf(x) === i).length === q.o.length);
      const uitleg = !!(c.uitleg && c.uitlegEn && c.naam && c.naamEn && c.icon);
      if (!heel || !uitleg) stuk.push(c.id + (heel ? '' : ' (vragen)') + (uitleg ? '' : ' (uitleg)'));
    });
    // een regel mag uitkomen bij een concept (met doosje) of bij een handgeschreven wizard;
    // wat bij geen van beide uitkomt, verdwijnt in het niets en dat mag niet
    const wees = CORR_REGELS.filter((r) => !gcConceptVoorCorr(r.id) && !r.gw).map((r) => r.id);
    const ids = GC_CONCEPTEN.map((c) => c.id);
    return {
      aantal: GC_CONCEPTEN.length,
      stuk: stuk,
      wees: wees,
      uniek: ids.filter((v, i, a) => a.indexOf(v) === i).length,
      reflexivo: ids.indexOf('reflexivo') !== -1,
      genero: ids.indexOf('genero') !== -1
    };
  });
  ok(lichting.aantal >= 23, 'er zijn nu minstens drieentwintig concepten (' + lichting.aantal + ')');
  ok(lichting.uniek === lichting.aantal, 'en geen enkel concept-id komt dubbel voor');
  ok(lichting.stuk.length === 0, 'elk concept levert een begripsvraag plus vier bruikbare voorbeelden (' + lichting.stuk.join(', ') + ')');
  ok(lichting.wees.length === 0, 'geen enkele Corrector-regel komt meer nergens uit (' + lichting.wees.join(', ') + ')');
  ok(lichting.reflexivo === true, 'reflexivo heeft nu een eigen concept');
  ok(lichting.genero === true, 'en el/la ook');

  // duizend keer trekken: geen enkel patroon mag een vraag maken waarvan het juiste
  // antwoord ook tussen de afleiders staat
  const trekken = await page.evaluate(() => {
    const fout = {};
    for (let r = 0; r < 40; r++) {
      GC_CONCEPTEN.forEach((c) => {
        const vr = gcVernieuw('concept-' + c.id).stappen[0].vragen;
        vr.forEach((q) => {
          if (q.o.filter((x) => x === q.o[q.g]).length !== 1) fout[c.id] = (fout[c.id] || 0) + 1;
        });
      });
    }
    return Object.keys(fout);
  });
  ok(trekken.length === 0, 'veertig rondes lang blijft het juiste antwoord het enige juiste (' + trekken.join(', ') + ')');

  /* ---------------- 8. los te lezen als grammatica ----------------
     Stefan: "ook los kunnen lezen als grammatica." */
  await page.evaluate(() => { gwSess = null; gcLeesId = null; scopeLesson = null; show('spiekbrief'); });
  await page.waitForTimeout(300);
  const lezen = await page.evaluate(() => {
    const kaart = document.querySelector('#cheat [data-gclees]');
    if (!kaart) return { kaart: false };
    kaart.click();
    const tekst = document.getElementById('cheat').innerText;
    return {
      kaart: true,
      id: gcLeesId,
      geenQuiz: gwSess === null,
      uitleg: !!document.getElementById('gcLeesUitleg'),
      lang: (document.getElementById('gcLeesUitleg') || {}).innerText.length,
      oefenknop: !!document.getElementById('gcOefen'),
      terug: !!document.getElementById('gcLeesTerug'),
      bladeren: document.querySelectorAll('#cheat [data-gclees]').length,
      tekst: tekst
    };
  });
  ok(lezen.kaart === true, 'de Grammatica-tab toont conceptkaartjes');
  ok(lezen.geenQuiz === true, 'klikken start niet meteen een toets: je krijgt eerst de uitleg');
  ok(lezen.uitleg === true && lezen.lang > 120, 'en dat is echte uitleg, geen zin of twee (' + lezen.lang + ' tekens)');
  ok(lezen.oefenknop === true, 'het oefenen zit een knop verderop');
  ok(lezen.terug === true, 'en terug naar de lijst kan altijd');
  ok(lezen.bladeren >= 1, 'je kunt doorbladeren naar een volgend onderwerp, als in een boekje');

  const oefenen = await page.evaluate(() => {
    document.getElementById('gcOefen').click();
    return { id: gwSess ? gwSess.id : null, lees: gcLeesId, fase: gwSess ? gwSess.fase : null };
  });
  ok(/^concept-/.test(oefenen.id || ''), 'op oefenen drukken start alsnog de microles (' + oefenen.id + ')');
  ok(oefenen.lees === null, 'en de leesmodus laat netjes los');

  // de dagelijkse les blijft rechtstreeks naar het oefenen gaan
  const inFlow = await page.evaluate(() => {
    gwSess = null; gcLeesId = null;
    S.gram = {};
    corrSrsBij('reflexivo', false);
    lesFlow = { stap: null, quizzesTeDoen: [] };
    const id = lesFlowGramId();
    gwStart(id);
    return { id: id, sess: gwSess ? gwSess.id : null, lees: gcLeesId };
  });
  ok(inFlow.id === 'concept-reflexivo', 'een fout op reflexivo kiest nu ook echt die les (' + inFlow.id + ')');
  ok(inFlow.sess === 'concept-reflexivo' && inFlow.lees === null, 'en in de dagelijkse les kom je nog steeds meteen in de oefening');
  await page.evaluate(() => { gwSluit(); });

  /* ---------------- 9. de tab opent kort (v20.7) ----------------
     Stefan: "kwestie van hoe je de info presenteert, of beide kan of niet." Beide dus. */
  const kort = await page.evaluate(() => {
    gwSess = null; gcLeesId = null; S.gcAlles = false;
    S.gram = {};
    corrSrsBij('muymucho', false);
    show('spiekbrief');
    const zichtbaar = document.querySelectorAll('#cheat [data-gclees]').length;
    const knop = document.getElementById('gcToggleAlles');
    const label = knop ? knop.textContent : '';
    const eerste = (document.querySelector('#cheat [data-gclees]') || {}).getAttribute
      ? document.querySelector('#cheat [data-gclees]').getAttribute('data-gclees') : null;
    return {
      zichtbaar: zichtbaar,
      knop: !!knop,
      label: label,
      eerste: eerste,
      reden: document.getElementById('cheat').innerText,
      totaal: GC_CONCEPTEN.length
    };
  });
  ok(kort.zichtbaar <= 3, 'de Grammatica-tab opent met hoogstens drie conceptkaartjes (' + kort.zichtbaar + ')');
  ok(kort.eerste === 'muymucho', 'en bovenaan staat de fout van net, niet het eerste concept uit de lijst');
  ok(kort.knop === true && new RegExp(kort.totaal).test(kort.label), 'met een knop die zegt hoeveel er nog meer zijn (' + kort.label.trim() + ')');
  ok(/nieuws|new/i.test(kort.reden), 'en er staat bij waarom juist deze drie er staan');

  const uitgeklapt = await page.evaluate(() => {
    document.getElementById('gcToggleAlles').click();
    const n = document.querySelectorAll('#cheat [data-gclees]').length;
    const bewaard = S.gcAlles;
    document.getElementById('gcToggleAlles').click();
    return { n: n, bewaard: bewaard, terug: document.querySelectorAll('#cheat [data-gclees]').length, uit: S.gcAlles };
  });
  ok(uitgeklapt.n === kort.totaal, 'de knop klapt alle onderwerpen uit (' + uitgeklapt.n + ')');
  ok(uitgeklapt.bewaard === true && uitgeklapt.uit === false, 'en die keuze wordt onthouden, dus je hoeft hem niet elke dag opnieuw te maken');
  ok(uitgeklapt.terug <= 3, 'terugklappen kan ook weer');

  const relevanteErrors = errors.filter((e) => !/Failed to load resource|Failed to fetch|ERR_TUNNEL_CONNECTION_FAILED|net::/.test(e));
  ok(relevanteErrors.length === 0, 'geen JS-fouten in eigen app-code tijdens hele test (' + relevanteErrors.length + ' gevonden)');
  if (relevanteErrors.length) relevanteErrors.forEach((e) => console.log('  ->', e));

  await browser.close();
  console.log(fails === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fails + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fails === 0 ? 0 : 1);
})();

function GC_VOORBEELDEN_VERWACHT() { return 4; }
"""

ZINNEN = {'s167': '{"id":"s167","lvl":2,"nl":"Mijn broer is heel slank, maar mijn neef is juist heel stevig.","en":"My brother is very slim, but my cousin is really strong.","es":"Mi hermano es muy delgado, pero mi primo es muy fuerte.","alt":["mi hermano es muy delgado pero mi primo es muy fuerte","mi hermano es delgado pero mi primo es fuerte"],"uitleg":"Delgado en fuerte horen allebei bij een man, dus mannelijk enkelvoud. Bij een zus wordt delgado wel delgada, maar fuerte verandert niet: bijvoeglijke naamwoorden op -e hebben maar één vorm.","ue":"Delgado and fuerte both describe a man here, so masculine singular. For a sister delgado becomes delgada, but fuerte does not change: adjectives ending in -e have one form only.","tag":"les3"}', 's168': '{"id":"s168","lvl":2,"nl":"In de stad is het openbaar vervoer beter, maar het verkeer is altijd druk.","en":"Public transport is better in the city, but traffic is always busy.","es":"En la ciudad el transporte público es mejor, pero el tráfico siempre está congestionado.","alt":["en la ciudad el transporte publico es mejor pero el trafico siempre esta congestionado","en la ciudad el transporte público es mejor pero siempre hay mucho tráfico"],"uitleg":"Mejor is de vergrotende trap van bueno: je zegt nooit más bueno maar mejor, net als peor voor slechter. En está congestionado gaat over hoe het nu is, dus estar en niet ser.","ue":"Mejor is the comparative of bueno: you never say más bueno, you say mejor, just like peor for worse. And está congestionado is about how things are right now, so estar and not ser.","tag":"ciudad"}', 's169': '{"id":"s169","lvl":2,"nl":"Op het platteland is de lucht schoner, maar je moet verder reizen voor werk.","en":"The air is cleaner in the countryside, but you have to travel further for work.","es":"En el campo el aire es más puro, pero hay que desplazarse más para ir al trabajo.","alt":["en el campo el aire es mas puro pero hay que desplazarse mas para ir al trabajo","en el campo se respira aire más puro pero para ir al trabajo hay que moverse mucho"],"uitleg":"Más puro is de gewone vergrotende trap: más plus het bijvoeglijk naamwoord. Hay que plus infinitief betekent dat het moet zonder te zeggen wie: hay que desplazarse geldt voor iedereen.","ue":"Más puro is the ordinary comparative: más plus the adjective. Hay que plus infinitive says something must be done without saying by whom: hay que desplazarse applies to everyone.","tag":"campo"}', 's170': '{"id":"s170","lvl":2,"nl":"Ik mis de rust van het platteland als ik in de stad woon.","en":"I miss the peace of the countryside when I live in the city.","es":"Echo de menos la tranquilidad del campo cuando vivo en la ciudad.","alt":["echo de menos la tranquilidad del campo cuando vivo en la ciudad","cuando vivo en la ciudad echo de menos la tranquilidad del campo"],"uitleg":"Echar de menos is één uitdrukking voor missen; alleen echar vervoeg je, de rest blijft staan: echo de menos. Del is de samentrekking van de en el, want de el campo bestaat niet.","ue":"Echar de menos is one fixed expression for to miss; you only conjugate echar, the rest stays put: echo de menos. Del is de plus el contracted, because de el campo does not exist.","tag":"general"}', 's171': '{"id":"s171","lvl":2,"nl":"In de stad is er meer te doen in je vrije tijd, maar het is duurder.","en":"There’s more to do in your free time in the city, but it’s more expensive.","es":"En la ciudad hay más planes para el ocio, pero es más caro.","alt":["en la ciudad hay mas planes para el ocio pero es mas caro","en la ciudad hay más opciones de ocio pero todo cuesta más"],"uitleg":"Twee keer más op dezelfde manier: más planes bij een zelfstandig naamwoord en más caro bij een bijvoeglijk naamwoord. Hay blijft hay, ook bij meervoud: hay más planes, nooit han.","ue":"Más twice in the same way: más planes with a noun and más caro with an adjective. Hay stays hay, also in the plural: hay más planes, never han.","tag":"general"}', 's172': '{"id":"s172","lvl":2,"nl":"Op het platteland is het levensritme rustiger, maar je hebt minder winkels.","en":"The pace of life is slower in the countryside, but there are fewer shops.","es":"En el campo el ritmo de vida es más tranquilo, pero hay menos tiendas.","alt":["en el campo el ritmo de vida es mas tranquilo pero hay menos tiendas","en el campo se vive más despacio pero hay menos comercios"],"uitleg":"Menos is het spiegelbeeld van más en werkt precies hetzelfde: menos tiendas. Vergelijk je met iets anders, dan komt er que achter: menos tiendas que en la ciudad.","ue":"Menos is the mirror image of más and works exactly the same: menos tiendas. If you compare with something else, que follows: menos tiendas que en la ciudad.","tag":"campo"}', 's173': '{"id":"s173","lvl":2,"nl":"Ik woon liever in de stad omdat ik van de sfeer hou.","en":"I prefer to live in the city because I love the atmosphere.","es":"Prefiero vivir en la ciudad porque me gusta el ambiente.","alt":["prefiero vivir en la ciudad porque me gusta el ambiente","me gusta más vivir en la ciudad por el ambiente"],"uitleg":"Preferir wordt in de ik-vorm prefiero: de e verandert in ie, net als bij quiero en pienso. Na preferir komt een infinitief: prefiero vivir, en niet prefiero que vivo.","ue":"Preferir becomes prefiero in the I-form: the e changes to ie, just like quiero and pienso. Preferir is followed by an infinitive: prefiero vivir, not prefiero que vivo.","tag":"general"}', 's174': '{"id":"s174","lvl":2,"nl":"Op het platteland is er meer ruimte, maar je moet zelf alles regelen.","en":"There’s more space in the countryside, but you have to arrange everything yourself.","es":"En el campo hay más espacio, pero tienes que organizar todo tú mismo.","alt":["en el campo hay mas espacio pero tienes que organizar todo tu mismo","en el campo hay más sitio pero todo depende de ti"],"uitleg":"Hay más espacio staat in het enkelvoud, want espacio is niet te tellen, ook niet met más ervoor. Tienes que plus infinitief zegt wél wie het moet doen, anders dan hay que in de zin hierboven.","ue":"Hay más espacio is singular, because espacio cannot be counted, not even with más in front. Tienes que plus infinitive does say who has to do it, unlike hay que in the sentence above.","tag":"campo"}'}

BESTANDEN = [(WORTEL / "tools" / "content-lib.js", LIB_TEKST, "content-lib.js"),
             (WORTEL / "tools" / "curriculum.js", CUR_TEKST, "curriculum.js"),
             (WORTEL / "test" / "suites" / "pw-schrijven.js", SCHRIJF_TEKST, "pw-schrijven.js"),
             (WORTEL / "test" / "suites" / "pw-adivina.js", ADIV_TEKST, "pw-adivina.js"),
             (WORTEL / "test" / "suites" / "pw-leermachine.js", LEER_TEKST, "pw-leermachine.js")]

# ---------------------------------------------------------------- 1. gereedschap en suites
# Deze vijf bestanden schrijft de nachtrun nooit; die gaan in hun geheel. Ankers doen alsof daar
# iets te botsen valt, en dat is hier niet waar.
for pad, tekst, naam in BESTANDEN:
    if pad.exists() and pad.read_text(encoding="utf-8") == tekst:
        print("  " + naam + " staat al bij")
    else:
        pad.parent.mkdir(parents=True, exist_ok=True)
        pad.write_text(tekst, encoding="utf-8")
        print("  " + naam + " geschreven")

# ---------------------------------------------------------------- 2. de app
src = APP.read_text(encoding="utf-8")
DOE_APP = 'var APP_VERSIE = "v23.42"' not in src
if not DOE_APP:
    print("  index.html staat al op v23.42, die sla ik over")
elif 'var APP_VERSIE = "v23.41"' not in src:
    print("\nDeze index.html staat niet op v23.41. Merge eerst de les van de avondrun:\n"
          "    git pull --rebase\n"
          "    git merge --no-ff origin/curriculum/les-20260811\n"
          "Twee conflicten: APP_VERSIE wordt v23.41, en de zinnen van beide kanten blijven allebei\n"
          "staan. Let op de komma tussen de regel van s174 en die van s176.\n")
    sys.exit(1)

def rep(anker, nieuw, n=1):
    global src
    if not DOE_APP: return
    aantal = src.count(anker)
    assert aantal == n, "anker %d keer gevonden, verwacht %d: %r" % (aantal, n, anker[:90])
    src = src.replace(anker, nieuw, n)

rep('  WORDS.forEach(function(w){\n    var es = String(w.es || "").replace(/^(el|la|los|las|un|una)\\s+/i, "").split(/[\\/(]/)[0].trim();\n    if(!es || /\\s/.test(es) || /[ñÑ]/.test(es)) return;\n    var plat = adivPlat(es);\n    if(ADIV_LEN.indexOf(plat.length) === -1) return;\n    if(zien[plat]) return;\n    zien[plat] = 1;\n    uit.push({id: w.id, es: es, nl: wTrans(w), plat: plat});\n  });',
    '  WORDS.forEach(function(w){\n    /* v23.42: het lidwoord blijft staan in wat je te zien krijgt. Het te raden woord is de kern\n       zonder lidwoord (dat zijn de letters op het bord), maar bij de oplossing hoort "el coche" en\n       niet "coche": het geslacht hoort bij het woord, en een woord dat je zonder lidwoord leert moet\n       je later alsnog een keer met lidwoord leren. */\n    var vol = String(w.es || "").split(/[\\/(]/)[0].trim();\n    var kern = vol.replace(/^(el|la|los|las|un|una)\\s+/i, "");\n    if(!kern || /\\s/.test(kern) || /[ñÑ]/.test(kern)) return;\n    var plat = adivPlat(kern);\n    if(ADIV_LEN.indexOf(plat.length) === -1) return;\n    if(zien[plat]) return;\n    zien[plat] = 1;\n    uit.push({id: w.id, es: vol, nl: wTrans(w), plat: plat});\n  });')

rep('    // Vanaf nu komen ze terug als voorstel met een reden erbij (lesFlowVoorstellen), en dan is\n    // hetzelfde blok ineens iets wat je kiest. Zie lesFlowExtra() voor de opt-in.\n    lesFlowKlaar();\n    return;',
    '    // Vanaf nu komen ze terug als voorstel met een reden erbij (lesFlowVoorstellen), en dan is\n    // hetzelfde blok ineens iets wat je kiest. Zie lesFlowExtra() voor de opt-in.\n    //\n    // v23.42 - en toch komt er één blok terug in de verplichte les: schrijven. Stefan, 11 aug: "in\n    // mijn dagelijkse habit mis ik nu het schrijven, dat zou ook minimaal 3 zinnen ofzo moeten zijn."\n    // Dat is geen terugdraaiing van v20.5 maar een correctie erop: wat toen afhaakte was een blok van\n    // vijf tot tien zinnen ná het punt waarop je al klaar was. Drie zinnen is iets anders dan tien,\n    // en het staat nu ín de les in plaats van erachter. Zelf iets produceren is bovendien het enige\n    // moment van de dag waarop je het Spaans uit je hoofd moet halen in plaats van herkennen.\n    if(allowedSentIds().length){\n      lesFlow.stap = "produceren";\n      lesFlow.vaardigheid = "schrijven";\n      lesFlow.vaardigheidRij = [];\n      lesFlow.gekozenSpel = "vertalen";\n      lesFlow.vertalenTeGaan = lesFlow.vertalenTotaal = SCHRIJF_PER_LES;\n      show("vertalen");\n      return;\n    }\n    lesFlowKlaar();\n    return;')

rep('var lesFlow = null; // {stap: null|"woorden"',
    '/* v23.42: hoeveel zinnen schrijf je in je dagles. Drie, en niet meer: het punt is dat het elke dag\n   gebeurt, niet dat het lang duurt. Groeit dit ooit mee met je doelminuten, verplaats het dan naar\n   dagPortie() waar de andere maten wonen. */\nvar SCHRIJF_PER_LES = 3;\nvar lesFlow = null; // {stap: null|"woorden"')

rep('var APP_VERSIE = "v23.41";', 'var APP_VERSIE = "v23.42";')

# de zeven zinnen van de nieuwe les krijgen uitleg die iets uitlegt, en s167 wordt een echte
# tegenstelling (knap tegenover slank was er geen)
if DOE_APP:
    regels = src.split("\n")
    raak = 0
    for k, regel in enumerate(regels):
        m = re.match(r'^ \{"id":"(s1[67]\d)".*\},?$', regel)
        if not m or m.group(1) not in ZINNEN: continue
        staart = "," if regel.rstrip().endswith(",") else ""
        regels[k] = " " + ZINNEN[m.group(1)] + staart
        raak += 1
    assert raak == len(ZINNEN), "zinnen geraakt: %d van %d" % (raak, len(ZINNEN))
    src = "\n".join(regels)
    APP.write_text(src, encoding="utf-8")
    print("  index.html: lidwoord in Adivina, schrijven in de dagles, %d zinnen met echte uitleg, v23.42" % raak)

v = VERSIE.read_text(encoding="utf-8").strip()
if v != "v23.42":
    VERSIE.write_text("v23.42\n", encoding="utf-8")
    print("  versie.txt: " + v + " -> v23.42")

print("\nklaar. Draai nu de poort:")
print("  CHROMIUM=<pad naar chromium> node test/poort.js")
