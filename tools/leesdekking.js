/* tools/leesdekking.js - hoeveel van een leestekst kan deze lezer al lezen?
   =========================================================================

   WAAROM DIT BESTAAT

   Hu en Nation (2000) en Laufer: om een tekst zonder woordenboek te volgen moet je ongeveer 98
   procent van de lopende woorden kennen; met hulp kom je weg met 95. Onder de 90 is het geen lezen
   meer maar ontcijferen. Dat is dus een meetbare eigenschap van een tekst, en tot nu toe werd hij
   nooit gemeten: de 43 hoofdstukken die er staan zijn geschreven zonder dat iets natelde of ze te
   lezen waren.

   WAT "KENNEN" HIER BETEKENT

   Niet een lemma maar een VORM. Je leest geen infinitieven, je leest camina en caminaban. De
   begroting bestaat daarom uit vormen, en komt uit vier bronnen:

     1. elk Spaans woord dat de app ooit op een kaartje heeft gezet (WORDS, EXTRA_CONTENT)
     2. elk woord uit elke oefenzin (SENTENCES, EXTRA_CONTENT), want die heeft hij gelezen
     3. de volledige presente van elk werkwoord in VERBOS, want die staan in de Conjugador en in
        Rompecabezas, en wie hablo kent leest hablamos
     4. de FREQ-lijst tot een instelbare grens, want dat zijn de woorden die in elke tekst staan

   Plus een lichte vormtoeslag: een regelmatig meervoud (-s, -es) of een vrouwelijke vorm (-o naar
   -a) van iets wat in de begroting staat telt mee. Dat is geen vrijgeleide maar erkenning dat wie
   "el libro" kent niet struikelt over "los libros".

   WAT NIET MEETELT

   Eigennamen tellen apart: Chispa, Córdoba en Franco zijn geen woordenschat en horen de meting niet
   te vervuilen, maar ze verdwijnen ook niet zomaar, want een hoofdstuk vol namen is nog steeds
   zwaar. Ze worden dus los geteld en gerapporteerd.

   GEBRUIK

     node tools/leesdekking.js --meting            de 43 bestaande hoofdstukken, per reeks
     node tools/leesdekking.js --tekst bestand.txt een losse tekst nameten
     node tools/leesdekking.js --zelftest          de proeven hieronder
*/
const fs = require("fs");
const path = require("path");

const INDEX = path.join(__dirname, "..", "index.html");
const FREQ_GRENS = 1000;   // de top van de frequentielijst telt als bekend

/* ---------- lezen uit index.html ----------

   index.html is geen module, dus de arrays worden eruit geknipt en met Function geëvalueerd. Dat is
   dezelfde truc als tools/content-lib.js gebruikt, en om dezelfde reden: er is één bron van
   waarheid en dat is het bestand dat live staat. */
function pakArray(bron, naam) {
  const i = bron.indexOf("\nvar " + naam + " = [");
  if (i === -1) return [];
  const start = bron.indexOf("[", i);
  let diep = 0, j = start, inStr = null, esc = false;
  for (; j < bron.length; j++) {
    const ch = bron[j];
    if (inStr) {
      if (esc) { esc = false; continue; }
      if (ch === "\\") { esc = true; continue; }
      if (ch === inStr) inStr = null;
      continue;
    }
    if (ch === '"' || ch === "'") { inStr = ch; continue; }
    if (ch === "[") diep++;
    else if (ch === "]") { diep--; if (!diep) { j++; break; } }
  }
  try { return new Function("return " + bron.slice(start, j))(); } catch (e) { return []; }
}

function leesBronnen(bestand) {
  const bron = fs.readFileSync(bestand || INDEX, "utf8");
  return {
    /* Alle woordkaarten, en dat zijn er veel meer dan WORDS alleen: K_WORDS zijn de A1-kernwoorden
       (v19.84) en C_WORDS de Cervantes-lijst (v23.15). Allebei hangen ze aan geen enkele les en
       staan ze altijd open, dus ze horen gewoon bij wat de lezer gezien heeft. Ze vergeten was de
       eerste meetfout van deze ronde: hij telde 437 kaarten waar er ruim tweeduizend zijn. En
       B_WORDS erbij, want een A2-leerling krijgt het hele A1-materiaal mee als opfris (zie waar
       WORDS bij het laden opnieuw wordt samengesteld). "hola" staat daar, en stond daarom ten
       onrechte in de eerste lijst met ontbrekende woorden. */
    words: [].concat(pakArray(bron, "WORDS"), pakArray(bron, "B_WORDS"),
                     pakArray(bron, "K_WORDS"), pakArray(bron, "C_WORDS"),
                     pakArray(bron, "L_WORDS")),
    sentences: [].concat(pakArray(bron, "SENTENCES"), pakArray(bron, "B_SENTENCES")),
    verbos: [].concat(pakArray(bron, "VERBOS"), pakArray(bron, "L_VERBOS")),
    freq: pakArray(bron, "FREQ"),
    book: pakArray(bron, "BOOK"),
    audiciones: pakArray(bron, "AUDICIONES")
  };
}

/* ---------- woorden knippen ----------

   Accenten blijven staan: están en estan zijn voor een lezer niet hetzelfde woord, en de app rekent
   dat alleen bij het TYPEN van een antwoord gelijk. Koppeltekens in werkwoordsvormen met een
   voornaamwoord eraan (dímelo) worden niet gesplitst; die staan of vallen als geheel. */
function tokens(tekst) {
  return String(tekst || "")
    .toLowerCase()
    .replace(/[«»"""'']/g, " ")
    .replace(/[^a-záéíóúüñ¿¡?!.,;:()\s-]/g, " ")
    .replace(/[¿¡?!.,;:()]/g, " ")
    .split(/[\s-]+/)
    .filter(function (w) { return w && /[a-záéíóúüñ]/.test(w); });
}

// Een eigennaam herkennen we aan een hoofdletter midden in de zin. Ruw, maar genoeg om Córdoba van
// ciudad te onderscheiden, en het alternatief is een namenlijst die altijd achterloopt.
function eigennamen(tekst) {
  const uit = {};
  String(tekst || "").split(/(?<=[.!?¿¡\n])\s+|^/).forEach(function (zin) {
    const w = zin.trim().split(/\s+/);
    w.forEach(function (x, i) {
      const kaal = x.replace(/[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ]/g, "");
      if (!kaal || i === 0) return;
      if (/^[A-ZÁÉÍÓÚÑ]/.test(kaal)) uit[kaal.toLowerCase()] = 1;
    });
  });
  return uit;
}

/* ---------- de begroting ---------- */
function begroting(b, opt) {
  opt = opt || {};
  const set = new Set();
  const voeg = function (t) { tokens(t).forEach(function (w) { set.add(w); }); };

  (b.words || []).forEach(function (w) { voeg(w.es); voeg(w.meer); voeg(w.ej); });
  (b.sentences || []).forEach(function (s) { voeg(s.es); });
  (b.verbos || []).forEach(function (v) {
    voeg(v.inf);
    (v.presente || []).forEach(voeg);
    (v.indefinido || []).forEach(voeg);
    (v.imperfecto || []).forEach(voeg);
    if (v.participio) voeg(v.participio);
    if (v.gerundio) voeg(v.gerundio);
  });
  const grens = opt.freqGrens === undefined ? FREQ_GRENS : opt.freqGrens;
  (b.freq || []).slice(0, grens).forEach(function (f) { voeg(Array.isArray(f) ? f[0] : f); });
  (opt.extra || []).forEach(voeg);

  /* De werkwoordstoeslag. Wie een infinitief kent EN de tijden heeft gehad, leest een regelmatige
     vorm van dat werkwoord. De app leert presente, indefinido en imperfecto (zie TIJDEN en de
     vormladder), dus die drie worden regelmatig uitgeklapt, plus het deelwoord en het gerundio.
     Onregelmatige vormen worden niet verzonnen: die staan of in VERBOS of ze tellen niet mee. */
  const UITG = {
    ar: ["o","as","a","amos","áis","an", "é","aste","ó","amos","asteis","aron", "aba","abas","aba","ábamos","abais","aban", "ado","ando"],
    er: ["o","es","e","emos","éis","en", "í","iste","ió","imos","isteis","ieron", "ía","ías","ía","íamos","íais","ían", "ido","iendo"],
    ir: ["o","es","e","imos","ís","en", "í","iste","ió","imos","isteis","ieron", "ía","ías","ía","íamos","íais","ían", "ido","iendo"]
  };
  const infs = new Set();
  set.forEach(function (w) { if (/(ar|er|ir)$/.test(w) && w.length > 3) infs.add(w); });
  infs.forEach(function (inf) {
    const t = inf.slice(-2), stam = inf.slice(0, -2);
    (UITG[t] || []).forEach(function (e) { set.add(stam + e); });
  });

  /* De vormtoeslag. Wie el libro kent struikelt niet over los libros, en wie rojo kent niet over
     roja. Verder niets: dit is een toeslag en geen generator van alles wat er zou kunnen bestaan. */
  const met = new Set(set);
  set.forEach(function (w) {
    met.add(w + "s");
    met.add(w + "es");
    if (/o$/.test(w)) { met.add(w.slice(0, -1) + "a"); met.add(w.slice(0, -1) + "as"); met.add(w + "s"); }
    if (/a$/.test(w)) met.add(w + "s");
  });
  return met;
}

/* ---------- de meting ---------- */
function dekking(tekst, budget, opt) {
  opt = opt || {};
  const namen = opt.namenTellen === false ? {} : eigennamen(tekst);
  const vrij = {};
  (opt.vrij || []).forEach(function (w) { tokens(w).forEach(function (t) { vrij[t] = 1; }); });
  const t = tokens(tekst);
  const onbekend = {}, naamTel = {};
  let bekend = 0, naamN = 0;
  t.forEach(function (w) {
    if (namen[w]) { naamN++; naamTel[w] = (naamTel[w] || 0) + 1; return; }
    if (budget.has(w) || vrij[w]) { bekend++; return; }
    onbekend[w] = (onbekend[w] || 0) + 1;
  });
  const telt = t.length - naamN;
  return {
    tokens: t.length, namen: naamN, geteld: telt, bekend: bekend,
    pct: telt ? (100 * bekend / telt) : 100,
    onbekend: Object.keys(onbekend).sort(function (a, b) { return onbekend[b] - onbekend[a]; })
      .map(function (w) { return { w: w, n: onbekend[w] }; }),
    namenLijst: Object.keys(naamTel)
  };
}

module.exports = { leesBronnen, begroting, dekking, tokens, eigennamen, FREQ_GRENS };

/* ---------- gereedschap ---------- */
if (require.main === module) {
  const args = process.argv.slice(2);

  if (args.includes("--zelftest")) {
    let mis = 0;
    const proef = function (goed, wat) { console.log((goed ? "  ok   " : "  FOUT ") + wat); if (!goed) mis++; };

    const b = begroting({ words: [{ es: "el libro" }], sentences: [{ es: "Tengo un libro rojo." }],
                          verbos: [{ inf: "hablar", presente: ["hablo", "hablas", "habla", "hablamos", "habláis", "hablan"] }],
                          freq: [["de"], ["la"], ["en"]] });
    proef(b.has("libro") && b.has("rojo"), "woorden uit kaartjes en zinnen staan in de begroting");
    proef(b.has("hablamos"), "en de hele presente van een werkwoord (hablamos)");
    proef(b.has("libros"), "het regelmatige meervoud telt mee (libros)");
    proef(b.has("roja"), "en de vrouwelijke vorm (roja)");
    proef(b.has("hablaban") && b.has("hablé") && b.has("hablado"),
      "en de regelmatige indefinido, imperfecto en het deelwoord (hablaban, hablé, hablado)");
    proef(!b.has("hablara") && !b.has("fue"),
      "CONTROLE: wat de app niet leert wordt niet verzonnen (geen subjuntivo imperfecto, geen onregelmatige fue)");

    const d1 = dekking("Tengo un libro rojo en la casa.", b);
    proef(d1.onbekend.length === 1 && d1.onbekend[0].w === "casa",
      "een onbekend woord wordt gevonden: " + JSON.stringify(d1.onbekend));
    proef(Math.round(d1.pct) === 86, "en het percentage klopt (" + d1.pct.toFixed(1) + "%, 6 van de 7)");

    const d2 = dekking("Hablamos con Córdoba y con Granada sobre el libro.", b);
    proef(d2.namen === 2, "eigennamen worden apart geteld (" + d2.namenLijst.join(", ") + ")");
    proef(d2.geteld === d2.tokens - 2, "en tellen niet mee in de noemer");

    const d3 = dekking("El califa vive en el califa grande.", b, { vrij: ["el califa"] });
    proef(d3.onbekend.filter(function (x) { return x.w === "califa"; }).length === 0,
      "een vrijgesteld kernwoord telt als bekend");

    proef(tokens("¿Dónde está la estación? ¡Allí!").length === 5,
      "leestekens verdwijnen: " + JSON.stringify(tokens("¿Dónde está la estación? ¡Allí!")));

    console.log(mis ? "\n" + mis + " FOUT" : "\nalles goed");
    process.exit(mis ? 1 : 0);
  }

  const bron = leesBronnen();
  const budget = begroting(bron);
  console.log("begroting: " + budget.size + " vormen (FREQ-top " + FREQ_GRENS + " meegerekend)");

  if (args.includes("--tekst")) {
    const f = args[args.indexOf("--tekst") + 1];
    const d = dekking(fs.readFileSync(f, "utf8"), budget);
    console.log(f + ": " + d.pct.toFixed(1) + "% van " + d.geteld + " woorden (" + d.namen + " namen apart)");
    console.log("  onbekend: " + d.onbekend.map(function (x) { return x.w + (x.n > 1 ? "×" + x.n : ""); }).join(", "));
    process.exit(0);
  }

  // --meting: de bestaande hoofdstukken en luisterscenes
  const perReeks = {};
  (bron.book || []).forEach(function (h) {
    const reeks = String(h.id || "").split("-")[0];
    const d = dekking(h.tekst || "", budget);
    if (!perReeks[reeks]) perReeks[reeks] = { n: 0, bekend: 0, geteld: 0, slecht: [] };
    const r = perReeks[reeks];
    r.n++; r.bekend += d.bekend; r.geteld += d.geteld;
    r.slecht.push({ id: h.id, pct: d.pct, titel: h.titel });
  });
  console.log("\n--- leesboek, per reeks ---");
  Object.keys(perReeks).forEach(function (k) {
    const r = perReeks[k];
    r.slecht.sort(function (a, b) { return a.pct - b.pct; });
    console.log("  " + k.padEnd(6) + r.n + " hoofdstukken · " + (100 * r.bekend / r.geteld).toFixed(1) + "%" +
      "   zwaarste: " + r.slecht.slice(0, 2).map(function (x) { return x.id + " " + x.pct.toFixed(0) + "%"; }).join(", "));
  });

  let aN = 0, aB = 0, aG = 0;
  (bron.audiciones || []).forEach(function (sc) {
    const t = (sc.regels || sc.lineas || []).map(function (r) { return r.es || r.texto || r; }).join(" ");
    const d = dekking(t, budget);
    aN++; aB += d.bekend; aG += d.geteld;
  });
  if (aG) console.log("\n--- luisteren ---\n  " + aN + " scenes · " + (100 * aB / aG).toFixed(1) + "%");
}
