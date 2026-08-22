/*
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

/* Dit zijn de VERPLICHTE velden, niet alle toegestane. Extra velden mogen en gaan ongewijzigd mee
   naar index.html (voegToeAanArray schrijft het hele object weg). Zo is "meer" optioneel: een kaart
   zonder tweede betekenis hoort het veld gewoon niet te hebben, en een lege string zou hier dan ook
   als ontbrekend gelden. */
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

/* Het Spaanse woord mag niet op de vraagkant staan. Stefan, 13 aug, met een schermafdruk erbij:
   "soms staat het spaanse woord er ook bij ... de spaanse zin mag nooit al worden getoond."

   Wat er stond, drie keer, alle drie een Grieks -ma-woord dat mannelijk is:

       cv67    es=planeta   nl=planeet (el planeta!)

   Iemand heeft het geslacht als geheugensteun in het antwoordveld gezet. Daarmee staat het antwoord
   op de vraag: je hoeft niets meer te weten om die kaart goed te doen. De juiste plek voor dat
   lidwoord is de Spaanse kant, en daar zegt "el planeta" het al.

   De controle is met opzet smal: alleen een haakje met een lidwoord plus een woord erin. Ruimer kan
   niet, want "de piano" is een prima vertaling van "el piano" en een cognaat is geen lek. */
/* 14 aug (v23.100): deze controle keek alleen naar "(el coche)" tussen haakjes, en dat was de vorm
   die op 13 augustus toevallig was opgevallen. Er waren er drie meer, en samen zaten ze op 80 van de
   1376 Cervantes-kaarten:

     "a pesar de = ondanks; wegen"                        -> antwoord: pesar
     "overblijven; afspreken; quedar bien = goed staan"   -> antwoord: quedar
     "vinger; teen: dedo del pie"                         -> antwoord: dedo

   Alle drie vragen ze je een woord te raden dat er al staat. De regel is nu algemener: de vraagkant
   mag geen woord delen met het antwoord, en geen "=" bevatten (dat is altijd een Spaanse uitdrukking
   met haar vertaling erachter).

   Met één uitzondering, en die is belangrijk: een leenwoord is geen lek. "virus", "club", "motor",
   "crisis", "chorizo" zijn in beide talen hetzelfde woord, en zo'n kaart is gewoon makkelijk, niet
   kapot. */
const LEKT = /\((el|la|los|las)\s+[a-zà-ÿ]+!?\)/i;
function kaal(s) {
  return String(s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
}
function woordenVanKant(s) {
  return kaal(s).split(/[^a-z]+/).filter((w) => w.length > 2);
}
function zelfdeWoordAlsAntwoord(kant, es) {
  // Aan beide kanten het lidwoord eraf, anders geldt "de metro" tegenover "el metro" als lek terwijl
  // het gewoon hetzelfde leenwoord is. Gemeten: zonder deze regel vallen er tientallen goede kaarten
  // uit de app.
  const b = kaal(es).replace(/^(el|la|los|las|un|una) /, "").replace(/[^a-z ]/g, "").trim();
  return kant.split(",").some(function (deel) {
    return kaal(deel).replace(/\([^)]*\)/g, "").replace(/^(de|het|een) /, "")
      .replace(/[^a-z ]/g, "").trim() === b;
  });
}
// Puntkomma's die echt een tweede betekenis inleiden, dus niet die binnen een haakje staan.
function topPuntkomma(s) {
  const uit = [];
  let diep = 0, cur = "";
  for (const ch of String(s || "")) {
    if (ch === "(") diep++; else if (ch === ")") diep--;
    if (ch === ";" && diep === 0) { uit.push(cur.trim()); cur = ""; } else cur += ch;
  }
  if (cur.trim()) uit.push(cur.trim());
  return uit;
}
function lektHetAntwoord(w) {
  if (LEKT.test(String(w.nl || "")) || LEKT.test(String(w.en || ""))) return true;
  const es = String(w.es || "");
  if (!es) return false;
  const esWoorden = new Set(woordenVanKant(es));
  return ["nl", "en"].some(function (k) {
    const kant = String(w[k] || "");
    if (!kant || zelfdeWoordAlsAntwoord(kant, es)) return false;
    if (/=/.test(kant)) return true;
    return woordenVanKant(kant).some((t) => esWoorden.has(t));
  });
}

/* ---------- kale zinnen: geen tijdsaanduiding (v23.175) ----------

   Een zin met de tag "kaal-<tijd>" hoort de tijd in de UITGANG te dragen en nergens anders. Staat er
   "ayer" of "todos los días" in, dan kan de leerling de vorm goed kiezen zonder de vorm te kennen.

   Waarom dit een machinale eis is en geen instructie aan het model: het model onthoudt hem twee
   zinnen lang en vergeet hem dan, precies zoals bij de vorm van een woordkaart. Zie WOORDVORM in
   curriculum.js voor hetzelfde patroon en dezelfde aanleiding.

   Deze lijst is met opzet ruim. Hij zal soms een goede zin afkeuren omdat er toevallig "ya" in
   staat, en dat kost één zin die nacht. Een doorgelaten "ayer" kost een oefening die de omweg
   traint die we juist proberen af te leren, en dat merkt niemand ooit. Fout naar de veilige kant
   is hier dus afkeuren. */
const TIJDSWOORDEN = [
  "ayer", "hoy", "mañana", "anoche", "ahora", "antes", "después", "luego", "entonces",
  "siempre", "nunca", "jamás", "todavía", "aún", "ya", "recién", "pronto", "últimamente",
  "mientras", "primero", "finalmente", "antaño", "actualmente", "hoydía"
];
const TIJDSUITDRUKKINGEN = [
  "hace ", "el año pasado", "la semana pasada", "el mes pasado", "el otro día", "el fin de semana pasado",
  "esta mañana", "esta tarde", "esta noche", "esta semana", "este año", "este mes", "este fin de semana",
  "cada día", "cada semana", "cada año", "todos los días", "todas las semanas", "todos los años",
  "de niño", "de niña", "de pequeño", "de pequeña", "de joven", "cuando era", "cuando éramos",
  "a menudo", "a veces", "de repente", "en aquella época", "en ese momento", "en aquel momento",
  "al principio", "al final", "por fin", "desde entonces", "hasta entonces", "una vez", "dos veces",
  "por primera vez", "el lunes", "el martes", "el miércoles", "el jueves", "el viernes",
  "el sábado", "el domingo", "los lunes", "los sábados", "los domingos"
];
/* Geeft de gevonden aanduidingen terug, niet alleen ja of nee: een afkeuring die niet zegt WELK
   woord het was, laat de volgende nacht dezelfde fout maken. */
function tijdsaanduidingen(es){
  const t = String(es || "").toLowerCase();
  const uit = [];
  TIJDSUITDRUKKINGEN.forEach(u => { if (t.includes(u)) uit.push(u.trim()); });
  const woorden = t.replace(/[¿?¡!.,;:()"]/g, " ").split(/\s+/);
  TIJDSWOORDEN.forEach(w => { if (woorden.includes(w)) uit.push(w); });
  return uit;
}
function isKaleZin(s){ return /^kaal-[a-z]+$/.test(String((s && s.tag) || "")); }

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
    if (lektHetAntwoord(w))
      fouten.push(`${waar}: de vertaling verklapt het Spaanse woord ("${w.nl}"). Zet het Spaans op de Spaanse kant, of in "meer".`);
    /* v23.100: één betekenis op de vraagkant. Een puntkomma betekende tot vandaag "en hier komt nog
       een betekenis", en dan vraagt de kaart niet meer welk woord je zoekt maar welke van drie er
       bedoeld wordt. Dat is geen taalvraag. De rest hoort in `meer`, dat pas ná het antwoord
       verschijnt. Puntkomma's binnen haakjes tellen niet mee: "pakken, nemen (Spanje; grof in
       Lat-Am!)" is één betekenis met een gebruiksnotitie. */
    if (topPuntkomma(String(w.nl || "")).length > 1)
      fouten.push(`${waar}: meerdere betekenissen op de vraagkant ("${w.nl}"). Zet de eerste in "nl" en de rest in "meer".`);
    if (w.meer !== undefined && typeof w.meer !== "string")
      fouten.push(`${waar}: "meer" moet tekst zijn`);
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
    /* v23.175: de harde eis onder de kale zinnen. Zie de kop bij TIJDSWOORDEN. */
    if (isKaleZin(s)) {
      const tw = tijdsaanduidingen(s.es);
      if (tw.length) fouten.push(`${waar}: kale zin met een tijdsaanduiding erin (${tw.join(", ")}); dan draagt de uitgang de tijd niet meer`);
      const tijd = String(s.tag).slice(5);
      if (["presente","perfecto","indefinido","imperfecto","subjuntivo"].indexOf(tijd) === -1)
        fouten.push(`${waar}: tag "${s.tag}" noemt geen bestaande tijd`);
      if (tijd === "indefinido" || tijd === "imperfecto") {
        /* Het Nederlands hoort het verschil niet: "ik woonde in een dorp" kan vivía of viví
           zijn. Zonder een situatieregel is de opgave niet te beslissen en meet hij niets. */
        if (!s.sit || String(s.sit).length < 8)
          fouten.push(`${waar}: ${tijd} zonder situatieregel ("sit"); in het Nederlands is deze keuze niet te horen`);
      }
    }
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

module.exports = { altWaarschuwingen, altVoornaamwoorden, tijdsaanduidingen, isKaleZin,
                   INDEX, VERSIE, inventaris, leesArray, leesLessen, leesExtra,
                   valideer, pasToe, volgendeId, voegToeAanArray, bumpVersie,
                   altNorm, altKaal, herstelAlt, lektHetAntwoord, topPuntkomma };

/* ---------- zelftest ---------- */

if (require.main === module && process.argv.includes("--zelftest")) {
  /* 14 aug: deze zelftest stond FOUT te printen en eindigde op 0, elke nacht, ongezien. Twee
     proefzinnen hadden `uitleg: "Proef."` uit de tijd vóór uitlegZegtIets() bestond, dus de
     "correcte proeflevering" was al een tijd niet meer correct. De inhoud van de app was niet stuk;
     de test was verouderd.

     Dat is nu tweemaal gerepareerd. De proefzinnen leggen echt iets uit, en het belangrijkste:
     `mis` telt de regels die schoon hadden moeten zijn en de test eindigt rood als er één bij zit.
     Een controle die alleen praat is geen controle. */
  let mis = 0;
  const zegGewoon = console.log;
  console.log = function () {
    const regel = Array.prototype.map.call(arguments, String).join(" ");
    if (/\b(FOUT|MISLUKT|GEMIST)\b/.test(regel)) mis++;
    zegGewoon.apply(console, arguments);
  };
  process.on("exit", function () {
    console.log = zegGewoon;
    if (mis) {
      zegGewoon("\n" + mis + " van de controles hierboven zou schoon moeten zijn. Dit is rood.");
      process.exitCode = 1;
    } else {
      zegGewoon("\nalles goed");
    }
  });
  const inv = inventaris();
  console.log("gelezen:", inv.words.length, "leswoorden,", (inv.kern||[]).length, "kernwoorden,", inv.sentences.length, "zinnen,",
              inv.quizzes.length, "toetsjes,", inv.cheat.length, "spiekkaarten,", inv.perLes.length, "lessen");
  const idW = volgendeId(inv.words, "w"), idS = volgendeId(inv.sentences, "s");
  const proef = {
    words: [{ id: idW(1), es: "la prueba", nl: "de proef", en: "the test", tag: "zelftest" }],
    sentences: [{ id: idS(1), lvl: 1, nl: "Dit is een proef.", en: "This is a test.", es: "Esta es una prueba.",
                  alt: ["esta es una prueba"],
                  uitleg: "Prueba is vrouwelijk, dus una prueba en niet un prueba.",
                  ue: "Prueba is feminine, so una prueba and not un prueba.", tag: "zelftest" }],
    lessen: { [inv.perLes[0].id]: { words: [idW(1)], sents: [idS(1)] } }
  };
  const f = valideer(proef, inv);
  console.log("validatie van een correcte proeflevering:", f.length ? "FOUT: " + f.join("; ") : "schoon ✓");
  const stuk = JSON.parse(JSON.stringify(proef));
  stuk.sentences[0].alt = ["iets anders"];
  stuk.words[0].id = inv.words[0].id;
  const f2 = valideer(stuk, inv);
  console.log("validatie van een kapotte levering vindt", f2.length, "fouten:", f2.join(" | "));
  /* De woordkaartvorm (14 aug, v23.100/101). Twee regels die de avondrun vannacht voor het eerst moet
     halen. Beide zijn triviaal "groen" te krijgen door ze nooit te laten toeslaan, dus staan de
     controlegevallen ernaast: een leenwoord en een kaart mét meer-veld moeten er glad doorheen. */
  const kaartGeval = (w, wat) => {
    const f3 = valideer({ words: [Object.assign({ id: idW(1), tag: "zelftest" }, w)] }, inv);
    const raak = f3.some(x => /verklapt|meerdere betekenissen|"meer" moet/.test(x));
    console.log("  " + wat + ": " + (raak ? "gezien" : "doorgelaten"));
    return raak;
  };
  const kaartGoed =
    kaartGeval({ es: "pesar", nl: "a pesar de = ondanks", en: "to weigh" }, "een kaart die het antwoord verklapt") &&
    kaartGeval({ es: "el dedo", nl: "vinger; teen", en: "finger" }, "een kaart met twee betekenissen op de vraagkant") &&
    kaartGeval({ es: "la mesa", nl: "de tafel", en: "table", meer: ["lijst"] }, "een meer-veld dat geen tekst is") &&
    !kaartGeval({ es: "el virus", nl: "het virus", en: "virus" }, "CONTROLE: een leenwoord") &&
    !kaartGeval({ es: "el dedo", nl: "de vinger", en: "finger", meer: "teen is el dedo del pie" }, "CONTROLE: een goede kaart met meer");
  console.log("woordkaartvorm: " + (kaartGoed ? "klopt ✓" : "FOUT"));
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
      uitleg: "Bij costar is het onderwerp de activiteit (hablar), dus enkelvoud: cuesta.",
      ue: "With costar the subject is the activity (hablar), so singular: cuesta.",
      tag: "zelftest", ...herstelAlt({ es: "Me cuesta hablar rápido.", alt: [] }) }] }, inv);
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

  /* De kale zinnen (v23.175). De eis is: in een zin met de tag kaal-<tijd> staat geen enkele
     tijdsaanduiding, want dan draagt de uitgang de tijd niet meer. Twee kanten, want een lijst die
     alles afkeurt is net zo nutteloos als een lijst die niets ziet. */
  const kaalZiet = [
    ["Ayer comí paella con mi hermana.", "ayer"],
    ["Todos los días desayuno café.", "todos los días"],
    ["Cuando era niño vivía en Lugo.", "cuando era"],
    ["Ya he terminado el trabajo.", "ya"],
    ["Los sábados salimos a cenar.", "los sábados"]
  ].every(p => tijdsaanduidingen(p[0]).length > 0);
  const kaalStil = [
    "Comí paella con mi hermana.",
    "Mi hermana trabaja en un hospital.",
    "Hemos perdido las llaves del coche."
  ].every(es => tijdsaanduidingen(es).length === 0);
  console.log("tijdsaanduidingen gezien:", kaalZiet ? "klopt \u2713" : "GEMIST");
  console.log("CONTROLE: en geen vals alarm op kale zinnen:", kaalStil ? "klopt \u2713" :
    "FOUT: " + JSON.stringify(["Comí paella con mi hermana.", "Mi hermana trabaja en un hospital.",
      "Hemos perdido las llaves del coche."].map(tijdsaanduidingen)));

  const kaalZin = (es, extra) => Object.assign({
    id: idS(3), lvl: 2, nl: "Ik at paella met mijn zus.", en: "I ate paella with my sister.",
    es, alt: [altKaal(es)], tag: "kaal-indefinido",
    uitleg: "comí is de yo-vorm van comer in het indefinido.",
    ue: "comí is the yo form of comer in the indefinido.", sit: "je vertelt over die ene avond"
  }, extra || {});
  const kMet = valideer({ sentences: [kaalZin("Ayer comí paella con mi hermana.")] }, inv);
  const kZonder = valideer({ sentences: [kaalZin("Comí paella con mi hermana.")] }, inv);
  const kGeenSit = valideer({ sentences: [kaalZin("Comí paella con mi hermana.", { sit: undefined })] }, inv);
  console.log("valideer keurt een kale zin met ayer af:",
    kMet.some(x => /tijdsaanduiding/.test(x)) ? "ja \u2713" : "GEMIST");
  console.log("CONTROLE: dezelfde zin zonder ayer komt erdoor:",
    kZonder.length ? "FOUT: " + kZonder.join("; ") : "ja \u2713");
  console.log("een indefinido-zin zonder situatieregel wordt afgekeurd:",
    kGeenSit.some(x => /situatieregel/.test(x)) ? "ja \u2713" : "GEMIST");

  const droog = pasToe(proef, { droog: true });
  console.log("droge schrijfbeurt:", droog.ok ? "ok, wordt " + droog.versie : "MISLUKT: " + droog.fouten);
  if (droog.ok) {
    fs.writeFileSync("/tmp/vamos-droog.html", droog.src);
    console.log("resultaat weggeschreven naar /tmp/vamos-droog.html (index.html is niet aangeraakt)");
  }
}
