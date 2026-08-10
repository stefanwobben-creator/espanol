#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
De alt-poort: een geaccepteerd alternatief mag de voornaamwoorden niet veranderen.

Uit de nachtrun van 10 aug, als watch-item opgeschreven: de avondrun leverde s158 (Mi hija se parece
a mi...) met als geaccepteerd alternatief "mi hija me parece pero...". Dat is precies de fout die de
eigen uitleg van die zin verbiedt, en nota bene dezelfde parecer/parecerse-verwarring die Stefan zelf
maakt. De zin drilt dus een regel en keurt tegelijk het foute antwoord goed.

Dat is erger dan een zin die wordt afgekeurd. Een afgekeurde zin merk je 's ochtends; een fout
alternatief merkt niemand, en het leert je precies verkeerd.

De oorzaak zit in de reparatie van 9 aug. herstelAlt() vult het alt-veld machinaal zodat de poort
niet meer alles afkeurt, maar hij normaliseert alleen: hij kijkt niet of het alternatief hetzelfde
zegt als de zin. De poort werd blij en de inhoud werd slechter.

De regel die dat afvangt, zonder Spaans te hoeven begrijpen: een alternatief mag afwijken in
woordvolgorde, accenten en leestekens, maar niet in welke wederkerende voornaamwoorden erin staan.
Verander je se in me, dan verander je de grammatica, en dat is nou net wat de zin toetst.

Twee dingen die ik eerst fout had en heb nagemeten op alle 517 zinnen en alternatieven die nu in de
app staan:

1. Enclitisch vastgeplakte voornaamwoorden moeten meetellen, anders geeft elke verplaatsing vals
   alarm (prestarme, duchandose, vistiendomelo: dat waren er dertien). Ze worden er dus afgepeld,
   maximaal drie lagen diep, en alleen als wat overblijft op ar/er/ir/ando/iendo/yendo eindigt.
2. os telt niet mee. Het botst met het gewone meervoud op -eros: companeros zou anders als een
   voornaamwoord os gelezen worden, met compañer als "werkwoordstam". In alle 517 regels komt os
   geen enkele keer als los woord voor, dus het kost niets en het scheelt vals alarm.

Ik heb ook geprobeerd om enclitische gebiedende wijs op het accent te herkennen (vamonos, sientate).
Dat werkt niet: op deze inhoud levert het pelicula, telefonos, moviles en pequenos op en precies een
terechte treffer. Dus niet gedaan. Zo'n zin geeft straks een waarschuwingsregel die iemand wegwuift,
en dat is de goedkope kant om fout te zitten.

Nagerekend op alle 356 alt-varianten: een daarvan geeft een waarschuwing (s154, waar "nos falta" een
echte herformulering is). Op de fout van 10 aug slaat hij wel aan.

Idempotent. Tooling, dus geen APP_VERSIE.
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "tools", "content-lib.js")
PAD_CUR = os.path.join(WORTEL, "tools", "curriculum.js")

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()
with io.open(PAD_CUR, encoding="utf-8") as f:
    cur = f.read()

# Per bestand kijken of het al gedaan is, en niet op een van de twee. Dat had ik eerst wel zo, en
# toen sloeg hij curriculum.js stilletjes over omdat content-lib.js al klaar was.
DOE_LIB = "altVoornaamwoorden" not in src
DOE_CUR = "function meldAlt" not in cur
if not DOE_LIB and not DOE_CUR:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    if not DOE_LIB:
        return
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:160])
    src = src.replace(anker, nieuw, n)


def repc(anker, nieuw, n=1):
    global cur
    if not DOE_CUR:
        return
    gevonden = cur.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:160])
    cur = cur.replace(anker, nieuw, n)


rep(
    """function valideer(nieuw, inv) {""",
    """/* De voornaamwoorden waar het om gaat: de wederkerende en persoonlijke. os staat er niet bij, dat
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

function valideer(nieuw, inv) {""")

rep(
    """module.exports = { INDEX, VERSIE, inventaris, leesArray, leesLessen, leesExtra,""",
    """module.exports = { altWaarschuwingen, altVoornaamwoorden,
                   INDEX, VERSIE, inventaris, leesArray, leesLessen, leesExtra,""")

# ------------------------------------------------------- pasToe geeft ze mee terug
# Een waarschuwing die alleen in de code staat is geen waarschuwing. pasToe is de enige plek waar
# inhoud de app in gaat, dus daar wordt hij berekend, en hij reist mee met het antwoord.
rep(
    """  const voor = inventaris();
  const fouten = valideer(nieuw, voor);
  if (fouten.length) return { ok: false, fouten };""",
    """  const voor = inventaris();
  const fouten = valideer(nieuw, voor);
  const waarschuwingen = altWaarschuwingen(nieuw);
  if (fouten.length) return { ok: false, fouten, waarschuwingen };""")

rep(
    """  if (opties.droog) return { ok: true, droog: true, versie: bump.versie, src };""",
    """  if (opties.droog) return { ok: true, droog: true, versie: bump.versie, src, waarschuwingen };""")

rep(
    """  return { ok: true, versie: bump.versie, aantallen: verwacht };""",
    """  return { ok: true, versie: bump.versie, aantallen: verwacht, waarschuwingen };""")

# ------------------------------------------------------- zelftest (node tools/content-lib.js --zelftest)
# Vaste gevallen, geen telling op de echte inhoud: die telling loopt op zodra er een terechte
# herformulering bij komt, en dan zou de zelftest rood staan om iets wat klopt. De echte inhoud
# wordt wel gemeld, als cijfer om naar te kijken.
rep(
    """  const droog = pasToe(proef, { droog: true });""",
    """  const altFout = altWaarschuwingen({ sentences: [{ id: "s158", es: "Mi hija se parece a mi.",
      alt: ["mi hija me parece pero es distinta"] }] });
  console.log("de fout van 10 aug (se wordt me):", altFout.length === 1 ? "gezien \\u2713" : "GEMIST");
  const altStil = altWaarschuwingen({ sentences: [
    { id: "t1", es: "\\u00bfMe lo puedes prestar?", alt: ["\\u00bfpuedes prest\\u00e1rmelo?"] },
    { id: "t2", es: "Se est\\u00e1 duchando.", alt: ["est\\u00e1 duch\\u00e1ndose"] },
    { id: "t3", es: "Te lo voy a decir.", alt: ["voy a dec\\u00edrtelo"] },
    { id: "t4", es: "Mis compa\\u00f1eros llegan tarde.", alt: ["llegan tarde mis compa\\u00f1eros"] },
    { id: "t5", es: "Quiero escribirlas hoy.", alt: ["hoy quiero escribirlas"] }
  ] });
  console.log("verplaatst voornaamwoord en -eros geven geen vals alarm:",
    altStil.length ? "FOUT: " + altStil.join("; ") : "klopt \\u2713");
  console.log("op de inhoud van nu:", altWaarschuwingen(inv).length + " alt om na te lezen");

  const droog = pasToe(proef, { droog: true });""")

# ------------------------------------------------------- en de nachtrun schrijft ze op
# Twee plekken waar de nachtrun inhoud wegschrijft: de reparatiezinnen en de nieuwe les. Allebei
# krijgen dezelfde regel, want de fout van 10 aug kwam uit de eerste maar kan net zo goed uit de
# tweede komen.
repc(
    """  let versie = null;
  if (reparatie.sentences.length || reparatie.quizzes.length) {
    const res = lib.pasToe(reparatie, { droog: OPT.droog });
    if (!res.ok) { console.error("AFGEKEURD:\\n - " + res.fouten.join("\\n - ")); return 1; }""",
    """  let versie = null;
  if (reparatie.sentences.length || reparatie.quizzes.length) {
    const res = lib.pasToe(reparatie, { droog: OPT.droog });
    meldAlt(res);
    if (!res.ok) { console.error("AFGEKEURD:\\n - " + res.fouten.join("\\n - ")); return 1; }""")

repc(
    """      const res = lib.pasToe(nieuweLes, { droog: true });   // altijd eerst droog: dit gaat via een PR""",
    """      const res = lib.pasToe(nieuweLes, { droog: true });   // altijd eerst droog: dit gaat via een PR
      meldAlt(res);""")

repc(
    """/* Precies een plek waar de hartslag wordt weggeschreven, en die ligt buiten main, zodat ook een
   klapper er nog in komt. */""",
    """/* De alt-waarschuwingen uit pasToe op het scherm. Ze keuren niets af, dus ze horen niet bij de
   fouten, maar ze moeten wel in het verslag staan: dit is precies het soort ding dat niemand ooit
   meer terugvindt als het alleen in de code zit. Zie patch-altpoort.py voor de aanleiding. */
function meldAlt(res) {
  const w = (res && res.waarschuwingen) || [];
  if (!w.length) return;
  console.log("— alt om na te lezen —");
  w.forEach(r => console.log("  " + r));
}

/* Precies een plek waar de hartslag wordt weggeschreven, en die ligt buiten main, zodat ook een
   klapper er nog in komt. */""")

if DOE_LIB:
    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
if DOE_CUR:
    with io.open(PAD_CUR, "w", encoding="utf-8") as f:
        f.write(cur)
print("alt-poort toegevoegd aan " + ", ".join(
    [p for p, d in [(PAD, DOE_LIB), (PAD_CUR, DOE_CUR)] if d]))
