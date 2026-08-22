#!/usr/bin/env python3
# v23.175 (alleen gereedschap) - de nachtrun schrijft kale zinnen, en spreekt ze diezelfde nacht in
#
# Stefan, 22 aug: "nou beide, nulmeting en dan de nachtrun." En daarna: "nee direct ook elevenlabs."
#
# EERST GEMETEN, EN DAT SCHEELT EEN HOOP WERK
#
# Over de audio: die is er al. tools/audio-lib.js leest met leesZinnen() ALLE zinnen uit SENTENCES en
# B_SENTENCES, de avondrun spreekt de groep "dictado" elke nacht in, en de app speelt
# audio/dictado/<id>.mp3 af onder de "Hoor hem"-knop. Een nieuwe zin met een gewoon s-id krijgt zijn
# ElevenLabs-opname dus dezelfde nacht, zonder één regel extra. Er komt geen nieuwe groep, geen
# nieuwe stem en geen nieuwe map bij. Dat is precies de bedoeling: een tweede stem voor dezelfde
# soort zin zou het manifest laten denken dat álle zinnen gewijzigd zijn, en dan betaal je één keer
# de hele bibliotheek opnieuw.
#
# WAT ER WEL BIJ MOET
#
# Uit de leerkaart "de vorm in een zin": van de 413 zinnen in de app zijn er maar 17 in het
# indefinido, 5 in het perfecto, 3 in het imperfecto en 1 in het subjuntivo waarin GEEN
# tijdsbijwoord staat. Voor het paar waar Stefan over struikelt, indefinido tegenover imperfecto,
# zijn dat er samen twintig, en dat is één ronde. Het corpus kan de oefening niet dragen, dus de
# zinnen moeten geschreven worden.
#
# DE EIS DIE DEZE ZINNEN ANDERS MAAKT
#
# Sagarra & Ellis 2013 (eye-tracking, 120 leerders van het Spaans): leerders met een morfologisch
# arme moedertaal kijken naar het BIJWOORD, niet naar de uitgang. Staat er "ayer" in de zin, dan is
# de uitgang overbodig en oefent Stefan zijn eigen omweg. Deze zinnen bevatten daarom geen enkele
# tijdsaanduiding: de uitgang draagt de tijd, of niets doet het.
#
# En omdat dat een eis is die een model vergeet zodra de zin verder mooi is, wordt hij MACHINAAL
# gecontroleerd, net als de vorm van een woordkaart. De lijst met tijdswoorden staat in
# content-lib.js en keurt af. Hij zal soms een goede zin afwijzen omdat er toevallig "ya" in staat.
# Dat is de goede kant om te missen: een afgewezen goede zin kost één zin die nacht, een
# doorgelaten "ayer" kost een oefening die het verkeerde traint en dat merkt niemand.
#
# WAT ER NIET IN ZIT
#
# Het imperfecto tegenover het indefinido is in het Nederlands niet te horen: "ik woonde in een
# dorp" kan vivía of viví zijn. Voor die twee tijden vraagt de prompt daarom om een korte
# Nederlandse situatieregel (veld "sit") die de keuze beslist. Zonder dat veld is de oefening
# oneerlijk, en een oneerlijke oefening meet niets.
#
# De app doet met deze zinnen nog niets. Dat is de volgende ronde, en met opzet apart: eerst moet er
# inhoud zijn om mee te bouwen, anders bouw ik weer een oefening en zoek ik er daarna inhoud bij.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
CUR = W / "tools" / "curriculum.js"
CLB = W / "tools" / "content-lib.js"

cur = CUR.read_text(encoding="utf-8")
clb = CLB.read_text(encoding="utf-8")

DOE_CUR = "kaleGaten" not in cur
DOE_CLB = "TIJDSWOORDEN" not in clb
DOE_STUB = "Nepcontent uit --stub, alleen om de pijplijn te testen." in cur
DOE_STUB2 = 'uitleg: "Stub.", ue: "Stub."' in cur

def rep(bron, anker, nieuw, n=1):
    c = bron.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:90])
    return bron.replace(anker, nieuw, n)

# ================================================================ content-lib: de harde eis
TIJDSCHECK = r'''
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
'''

if DOE_CLB:
    clb = rep(clb, "function valideer(nieuw, inv) {",
              TIJDSCHECK.strip("\n") + "\n\nfunction valideer(nieuw, inv) {")
    clb = rep(clb,
        '    if (!uitlegZegtIets(s.uitleg, s.es))\n'
        '      fouten.push(`${waar}: uitleg legt niets uit; noem een Spaans woord uit de zin of de regel bij naam`);',
        '    if (!uitlegZegtIets(s.uitleg, s.es))\n'
        '      fouten.push(`${waar}: uitleg legt niets uit; noem een Spaans woord uit de zin of de regel bij naam`);\n'
        '    /* v23.175: de harde eis onder de kale zinnen. Zie de kop bij TIJDSWOORDEN. */\n'
        '    if (isKaleZin(s)) {\n'
        '      const tw = tijdsaanduidingen(s.es);\n'
        '      if (tw.length) fouten.push(`${waar}: kale zin met een tijdsaanduiding erin (${tw.join(", ")}); dan draagt de uitgang de tijd niet meer`);\n'
        '      const tijd = String(s.tag).slice(5);\n'
        '      if (["presente","perfecto","indefinido","imperfecto","subjuntivo"].indexOf(tijd) === -1)\n'
        '        fouten.push(`${waar}: tag "${s.tag}" noemt geen bestaande tijd`);\n'
        '      if (tijd === "indefinido" || tijd === "imperfecto") {\n'
        '        /* Het Nederlands hoort het verschil niet: "ik woonde in een dorp" kan vivía of viví\n'
        '           zijn. Zonder een situatieregel is de opgave niet te beslissen en meet hij niets. */\n'
        '        if (!s.sit || String(s.sit).length < 8)\n'
        '          fouten.push(`${waar}: ${tijd} zonder situatieregel ("sit"); in het Nederlands is deze keuze niet te horen`);\n'
        '      }\n'
        '    }')
    clb = rep(clb,
        "module.exports = { altWaarschuwingen, altVoornaamwoorden,",
        "module.exports = { altWaarschuwingen, altVoornaamwoorden, tijdsaanduidingen, isKaleZin,")

# ---- de zelftest die de nachtrun al draait
ZELFTEST = r'''
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

'''

if DOE_CLB:
    clb = rep(clb, "  const droog = pasToe(proef, { droog: true });",
              ZELFTEST.strip("\n") + "\n\n  const droog = pasToe(proef, { droog: true });")

# ================================================================ curriculum: het gat en de prompt
KAAL = r'''
/* ---------- kale zinnen per tijd (v23.175) ----------

   Waarom dit gat niet uit het foutenlog komt zoals alle andere: het is geen gat in wat Stefan fout
   doet maar in wat de app kan vragen. Gemeten op 22 augustus, over alle 413 zinnen, geteld op
   zinnen zonder tijdsaanduiding met precies één eenduidige vervoegde vorm erin:

       presente 154 · indefinido 17 · perfecto 5 · imperfecto 3 · subjuntivo 1

   Voor het paar waar het om gaat, indefinido tegenover imperfecto, zijn dat er samen twintig. Dat is
   één ronde. Vandaar dat de nachtrun ze zelf gaat schrijven, één tijd per nacht, de dunste eerst.

   Het presente staat er niet bij: daar liggen er 154, en meer maken zou de nacht kosten die het
   imperfecto nodig heeft. */
const KAAL_TIJDEN = ["indefinido", "imperfecto", "perfecto", "subjuntivo"];
const KAAL_DOEL = 16;              // zoveel kale zinnen per tijd zijn genoeg voor vier ronden
const KAAL_PER_NACHT = 4;

function kaleGaten(inv) {
  const per = {};
  KAAL_TIJDEN.forEach(t => { per[t] = 0; });
  inv.sentences.forEach(s => {
    const m = /^kaal-([a-z]+)$/.exec(String(s.tag || ""));
    if (m && per[m[1]] !== undefined) per[m[1]]++;
  });
  return KAAL_TIJDEN.map(t => ({ soort: "kaal", tijd: t, tag: "kaal-" + t, heeft: per[t],
                                 tekort: KAAL_DOEL - per[t] }))
    .filter(g => g.tekort > 0)
    .sort((a, b) => b.tekort - a.tekort);
}

const KAAL_UITLEG = {
  indefinido: "één afgeronde gebeurtenis in het verleden",
  imperfecto: "hoe het wás, gewoonte of beschrijving in het verleden",
  perfecto: "iets dat gebeurd is en nu nog telt",
  subjuntivo: "na een uitdrukking van wens, twijfel, gevoel of oordeel"
};

function promptZinnenKaal(gat, ids, inv) {
  const bestaand = inv.sentences.filter(s => s.tag === gat.tag).slice(0, 6)
    .map(s => `- ${s.es} — ${s.nl}`).join("\n");
  const paar = (gat.tijd === "indefinido" || gat.tijd === "imperfecto");
  return `Je maakt oefenmateriaal voor een Nederlandstalige die Spaans leert (A2, AULA 2).

Maak ${ids.length} NIEUWE oefenzinnen in de ${gat.tijd} (${KAAL_UITLEG[gat.tijd]}).

DE EIS DIE ALLES BEPAALT: in de Spaanse zin staat GEEN ENKELE tijdsaanduiding. Geen "ayer", geen
"todos los días", geen "cuando era niño", geen "ya", geen "hace dos años", geen dagen van de week.
De werkwoordsuitgang moet het enige zijn dat vertelt wanneer het gebeurde.

Waarom: onderzoek met eye-tracking laat zien dat leerders met een moedertaal zonder rijke
werkwoordsvervoeging naar het bijwoord kijken en de uitgang overslaan. Staat er "ayer", dan kan de
leerling de goede vorm kiezen zonder de vorm te kennen, en dan oefent hij zijn eigen omweg. Deze eis
wordt machinaal gecontroleerd; een zin met een tijdswoord erin wordt afgekeurd.
${paar ? `
EN OMDAT HET NEDERLANDS HET VERSCHIL NIET HOORT: "ik woonde in een dorp" kan zowel vivía als viví
zijn. Geef daarom bij elke zin een veld "sit": één korte Nederlandse regel die de situatie schetst
zodat de keuze te maken is. Bijvoorbeeld "je vertelt hoe het vroeger elke zomer ging" (imperfecto)
of "je vertelt over die ene avond" (indefinido). Zonder dat veld is de opgave niet te beslissen.
` : ""}
Bestaande zinnen van deze soort (niet herhalen):
${bestaand || "(nog geen)"}

${STIJL}
- Gebruik exact deze ids in deze volgorde: ${ids.join(", ")}
- "tag" is exact "${gat.tag}".
- "uitleg" noemt de vorm zelf en waarom deze tijd hier hoort.

Antwoord met UITSLUITEND JSON: een object met precies een sleutel "zinnen", met daarin de lijst.
{"zinnen":[${JSON.stringify(Object.assign({}, VOORBEELD_ZIN, paar ? { sit: "je vertelt over die ene avond" } : {}))}]}`;
}
'''

if DOE_CUR:
    cur = rep(cur, "function promptZinnenVerschijnsel(gat, ids, inv) {",
              KAAL.strip("\n") + "\n\nfunction promptZinnenVerschijnsel(gat, ids, inv) {")

    # maakZinnen kiest de prompt
    cur = rep(cur,
        '  const prompt = gat.soort === "woorden" ? promptZinnenWoorden(gat, ids) : promptZinnenVerschijnsel(gat, ids, inv);',
        '  const prompt = gat.soort === "kaal" ? promptZinnenKaal(gat, ids, inv)\n'
        '    : gat.soort === "woorden" ? promptZinnenWoorden(gat, ids) : promptZinnenVerschijnsel(gat, ids, inv);')

    # sit meenemen: de map() gooit onbekende velden niet weg, maar de stub moet er ook een hebben
    cur = rep(cur,
        '      uitleg: "Nepcontent uit --stub, alleen om de pijplijn te testen.",\n'
        '      ue: "Stub content, only to test the pipeline.", tag: gat.tag\n'
        '    }));',
        '      uitleg: "Nepcontent uit --stub, alleen om de pijplijn te testen.",\n'
        '      ue: "Stub content, only to test the pipeline.", tag: gat.tag,\n'
        '      /* v23.175: ook de stub moet een situatieregel meenemen, anders keurt valideer() de\n'
        '         proeflevering af en meldt --stub een fout die er in het echt niet is. */\n'
        '      sit: gat.soort === "kaal" ? "proefsituatie uit --stub" : undefined\n'
        '    }));')

    # de eigen stap in main, naast het toetsje
    cur = rep(cur,
        '  const padKrap = vrd.krapsteDagen !== null && vrd.krapsteDagen < VOORRAAD_DREMPEL_DAGEN;',
        '  /* v23.175: de kale zinnen krijgen een eigen stap en staan niet op de gatenstapel. Twee\n'
        '     redenen. Ze komen niet uit het foutenlog, dus hun "score" staat op geen enkele schaal\n'
        '     naast die van de andere gaten; dat is precies de fout die op 11 augustus de woordgaten\n'
        '     stelselmatig liet winnen. En als ze wél op die stapel stonden, zouden ze in elke nacht\n'
        '     met genoeg echte fouten nooit aan de beurt komen, en dan duurt het maanden. Eén tijd per\n'
        '     nacht, de dunste eerst. */\n'
        '  const kaal = kaleGaten(inv);\n'
        '  const padKrap = vrd.krapsteDagen !== null && vrd.krapsteDagen < VOORRAAD_DREMPEL_DAGEN;')

    cur = rep(cur,
        '  HART.staat.beloofd = { gaten: Math.min(OPT.max, gaten.length), toetsje: an.toetsGaten.length ? 1 : 0,\n'
        '                         nieuweLes: verlengen ? 1 : 0 };',
        '  HART.staat.beloofd = { gaten: Math.min(OPT.max, gaten.length), toetsje: an.toetsGaten.length ? 1 : 0,\n'
        '                         kaal: kaal.length ? 1 : 0, nieuweLes: verlengen ? 1 : 0 };')

    cur = rep(cur,
        '  if (an.toetsGaten.length) console.log(`  nieuw toetsje bij: ${an.toetsGaten[0].tag}`);',
        '  if (an.toetsGaten.length) console.log(`  nieuw toetsje bij: ${an.toetsGaten[0].tag}`);\n'
        '  if (kaal.length) console.log(`  ${KAAL_PER_NACHT} kale zinnen in de ${kaal[0].tijd} ` +\n'
        '    `(er liggen er ${kaal[0].heeft} van de ${KAAL_DOEL})`);\n'
        '  else console.log("  kale zinnen: alle tijden zitten aan " + KAAL_DOEL);')

    cur = rep(cur,
        '  if (!gaten.length && !an.toetsGaten.length && !verlengen) console.log("  niets te doen");',
        '  if (!gaten.length && !an.toetsGaten.length && !kaal.length && !verlengen) console.log("  niets te doen");')

    cur = rep(cur,
        '  if (an.toetsGaten.length) {\n'
        '    const gat = an.toetsGaten[0];',
        '  /* --- de kale zinnen (v23.175) --- */\n'
        '  if (kaal.length) {\n'
        '    const gat = kaal[0];\n'
        '    const n = Math.min(KAAL_PER_NACHT, gat.tekort);\n'
        '    console.log(`  ${gat.tag}: ${n} kale zinnen maken…`);\n'
        '    const ruw = await maakZinnen(gat, n, inv, reparatie.sentences, motor);\n'
        '    const goed = await keurZinnen(ruw, motor);\n'
        '    if (!goed.length) console.error(`    ${gat.tag}: niets overgebleven`);\n'
        '    else {\n'
        '      /* NIET aan een les hangen, om dezelfde reden als het toetsje hieronder: een extra zin\n'
        '         in de lesindeling verhoogt de eis om de volgende les te ontgrendelen. Deze zinnen\n'
        '         worden op hun tag gevonden, niet via een les. */\n'
        '      reparatie.sentences = reparatie.sentences.concat(goed);\n'
        '      console.log(`    ${goed.length} kale zinnen goedgekeurd (${gat.heeft} + ${goed.length} van de ${KAAL_DOEL})`);\n'
        '    }\n'
        '  }\n'
        '  if (an.toetsGaten.length) {\n'
        '    const gat = an.toetsGaten[0];')

    cur = rep(cur,
        '  HART.staat.geleverd = { zinnen: reparatie.sentences.length, toetsjes: reparatie.quizzes.length,\n'
        '                          nieuweLes: nieuweLes ? 1 : 0 };',
        '  HART.staat.geleverd = { zinnen: reparatie.sentences.length, toetsjes: reparatie.quizzes.length,\n'
        '                          kaal: reparatie.sentences.filter(s => /^kaal-/.test(s.tag || "")).length,\n'
        '                          nieuweLes: nieuweLes ? 1 : 0 };')

    cur = rep(cur,
        '  const b = HART.staat.beloofd || { gaten: 0, toetsje: 0, nieuweLes: 0 };\n'
        '  const beloofd = b.gaten + b.toetsje + b.nieuweLes;',
        '  const b = HART.staat.beloofd || { gaten: 0, toetsje: 0, kaal: 0, nieuweLes: 0 };\n'
        '  const beloofd = b.gaten + b.toetsje + (b.kaal || 0) + b.nieuweLes;')

    cur = rep(cur,
        '  if (beloofd === 0) HART.staat.reden = "niets te doen: geen gaten, geen toetsgaten, voorraad ruim genoeg";',
        '  if (beloofd === 0) HART.staat.reden = "niets te doen: geen gaten, geen toetsgaten, kale zinnen compleet, voorraad ruim genoeg";')

    # het rapport noemt de stand, ook als er niets te doen is
    cur = rep(cur,
        '  toon("grammatica-toetsjes", an.toetsGaten, g => `${g.tag} (${g.titel}): ${g.fouten} fouten · spiekkaart ${JSON.stringify(g.spiek)}`);',
        '  toon("grammatica-toetsjes", an.toetsGaten, g => `${g.tag} (${g.titel}): ${g.fouten} fouten · spiekkaart ${JSON.stringify(g.spiek)}`);\n'
        '  /* v23.175: de stand van de kale zinnen hoort in het verslag, ook als er niets te doen is.\n'
        '     "er is niets te doen" en "hier ligt al genoeg" zijn niet hetzelfde; zie de verzadigde\n'
        '     onderwerpen hierboven, waar dat onderscheid uit dezelfde overweging is ontstaan. */\n'
        '  console.log("— kale zinnen (geen tijdsaanduiding, de uitgang draagt de tijd) —");\n'
        '  KAAL_TIJDEN.forEach(t => {\n'
        '    const n = inv.sentences.filter(s => s.tag === "kaal-" + t).length;\n'
        '    console.log(`  ${t}: ${n} van de ${KAAL_DOEL}` + (n >= KAAL_DOEL ? " · vol" : ""));\n'
        '  });')

# ---- de tegenlezer krijgt de eis erbij
if DOE_CUR:
    cur = rep(cur, "function promptTegenlezerZinnen(items) {",
        '/* v23.175: de tegenlezer krijgt de kale-zin-eis erbij. De machinale lijst in content-lib\n'
        '   vangt de bekende woorden; deze vangt wat een lijst niet kan vangen, zoals een zin waarin de\n'
        '   tijd uit de context blijkt in plaats van uit de uitgang ("nací en Sevilla" heeft geen\n'
        '   tijdswoord maar iedereen weet dat geboren worden af is). */\n'
        "function promptTegenlezerZinnen(items) {")

# ================================================================ de stub die nooit meer werkte
#
# Gevonden bij het uitproberen van het pad hierboven: `node tools/curriculum.js --stub --droog` keurt
# elke proefzin af met "uitleg legt niets uit". Dat is niet nieuw en het komt niet door de kale
# zinnen: uitlegZegtIets() eist sinds v23.101 dat de uitleg een Spaans woord uit de zin noemt of de
# regel bij naam, en de stubtekst noemt geen van beide. De stub is dus al weken onbruikbaar, en de
# stub is juist het gereedschap waarmee je de pijplijn nakijkt zonder een model te betalen.
if DOE_STUB:
    cur = rep(cur,
        '      uitleg: "Nepcontent uit --stub, alleen om de pijplijn te testen.",\n'
        '      ue: "Stub content, only to test the pipeline.", tag: gat.tag,',
        '      /* De uitleg moet door uitlegZegtIets() komen, dus hij noemt een woord uit zijn eigen\n'
        '         zin. Stond hier "Nepcontent uit --stub", en dan keurt valideer() elke proeflevering\n'
        '         af en test --stub alleen nog dat afkeuren werkt. */\n'
        '      uitleg: "prueba is vrouwelijk, dus la frase de prueba en niet el frase.",\n'
        '      ue: "prueba is feminine, so la frase de prueba and not el frase.", tag: gat.tag,')

if DOE_STUB2:
    # dezelfde fout in de stub van maakNieuweLes(), en daar keurde hij de hele proefles af
    cur = rep(cur,
        '''es: "Prueba número " + (i + 1) + ".", alt: ["prueba numero " + (i + 1)], uitleg: "Stub.", ue: "Stub.", tag: "stub" })),''',
        '''es: "Prueba número " + (i + 1) + ".", alt: ["prueba numero " + (i + 1)],
        uitleg: "prueba is vrouwelijk: la prueba, niet el prueba.",
        ue: "prueba is feminine: la prueba, not el prueba.", tag: "stub" })),''')

CUR.write_text(cur, encoding="utf-8")
CLB.write_text(clb, encoding="utf-8")
print("tools/curriculum.js: " + ("kale zinnen toegevoegd" if DOE_CUR else "stond er al"))
print("tools/content-lib.js: " + ("tijdswoordcontrole toegevoegd" if DOE_CLB else "stond er al"))
