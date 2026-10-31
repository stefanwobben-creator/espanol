# suites-v23.261.py - de vijf suites die op de oude doosregel stonden.
#
# v23.259 vervangt "elke misser kost de promotie, en meestal alle dozen" door een oordeel over
# minstens vijf antwoorden met drie uitkomsten. v23.261 geeft de drill een eigen kanaal dat de
# doos niet raakt. Vijf suites legden de oude regel vast en zijn daarmee niet meer waar.
#
# Ze worden niet versoepeld maar omgeschreven: elke proef die wegvalt krijgt er een tegenproef
# voor terug die de nieuwe grens bewaakt. Wat blijft staan is de vraag waar ze allemaal voor
# bestaan: kan de leerling zijn eigen misser wegpoetsen met een paar makkelijke antwoorden?
import io, os, sys

ROOT = os.path.expanduser(os.environ.get("VAMOS", "~/mnt/espanol"))


def laad(naam):
    p = os.path.join(ROOT, "test/suites", naam)
    return p, io.open(p, encoding="utf-8").read()


def schrijf(p, s):
    io.open(p, "w", encoding="utf-8").write(s)
    print("bijgewerkt:", os.path.basename(p))


def rep(s, anker, nieuw, n=1):
    assert s.count(anker) == n, "anker %d keer, verwacht %d: %r" % (s.count(anker), n, anker[:70])
    return s.replace(anker, nieuw)


# ---------------------------------------------------------------- pw-doosje.js
p, s = laad("pw-doosje.js")
if "87,5 procent" not in s:
    s = rep(s, """    S.gram = {};
    window.today = () => '2026-07-01';
    [true, true, true, false, true, true, true, true].forEach((g) => gramBij('eendag', g, 3, 0, 'microles'));
    uit.eenDag = { box: S.gram['eendag#0'].box, rij: S.gram['eendag#0'].rij,
                   rijVoor: S.gram['eendag#0'].rijVoor };""",
    """    S.gram = {};
    window.today = () => '2026-07-01';
    [true, true, true, false, true, true, true, true].forEach((g) => gramBij('eendag', g, 3, 0, 'microles'));
    uit.eenDag = { box: S.gram['eendag#0'].box, rij: S.gram['eendag#0'].rij,
                   rijVoor: S.gram['eendag#0'].rijVoor };
    /* v23.259: en dezelfde misser met maar TWEE antwoorden eronder. Dat is de grens: acht
       antwoorden zijn een oordeel, twee zijn dat niet, en onder de grens geldt de oude regel. */
    S.gram = {};
    [true, false].forEach((g) => gramBij('tweedag', g, 3, 0, 'microles'));
    uit.tweeOpEenDag = { box: S.gram['tweedag#0'].box, rijVoor: S.gram['tweedag#0'].rijVoor };""")

    s = rep(s, """  ok(gevallen.eenDag.box === 0,
     'CONTROLE: dus die dag eindigt gewoon op nul (doos ' + gevallen.eenDag.box + '). ' +
     'Anders kun je je eigen misser wegpoetsen in dezelfde sessie');""",
    """  /* v23.259: hier stond dat die dag op nul eindigt, "anders kun je je eigen misser wegpoetsen in
     dezelfde sessie". Dat is nu precies wat er wel mag, en dat is geen versoepeling maar een
     ander meetinstrument: zeven van de acht is 87,5 procent, en een oordeel over acht antwoorden
     is iets anders dan een oordeel over twee. De grens staat eronder. */
  ok(gevallen.eenDag.box === 1,
     'acht antwoorden met zeven goed is 87,5 procent en dus een doos omhoog (doos ' + gevallen.eenDag.box + ')');
  ok(gevallen.tweeOpEenDag.box === 0,
     'CONTROLE: met maar twee antwoorden wordt er niets geoordeeld en kost diezelfde misser nog ' +
     'steeds alles (doos ' + gevallen.tweeOpEenDag.box + ')');""")
    schrijf(p, s)
else:
    print("pw-doosje.js: al bijgewerkt")

# ---------------------------------------------------------------- pw-doos.js
p, s = laad("pw-doos.js")
if "v23.259" not in s:
    s = rep(s, """  /* v23.225: hier stond `=== 3`, oftewel: die dag klimt gewoon. Dat was de andere kant van
     hetzelfde gat. Een dag waarin je het onderwerp een keer mist is geen dag waarop je bewezen
     hebt dat je het kunt, en de datum alleen terugtrekken deed net alsof dat wel zo was. */
  ok(r.echteDag.box === 0,
    'zeven goede antwoorden met één misser ertussen leveren geen promotie op (doos ' + r.echteDag.box + ')');
  ok(r.echteDag.due === r.morgen, 'en het onderwerp komt morgen terug');""",
    """  /* v23.225 zette dit op 0: "een dag waarin je het onderwerp een keer mist is geen dag waarop je
     bewezen hebt dat je het kunt". v23.259 draait dat om, en niet uit mildheid. Zeven van de acht
     is 87,5 procent, en de kans dat iemand die het onderwerp maar voor 60 procent beheerst zo'n
     reeks haalt is 32 procent tegen 36 procent onder de oude tweevragenregel. Het oordeel is dus
     niet zachter geworden maar scherper, en een scherp oordeel hoort ook omhoog te kunnen wijzen.
     De dag met twee antwoorden eronder blijft wel op nul uitkomen; zie punt 1 hierboven. */
  ok(r.echteDag.box === 3,
    'zeven goede antwoorden met één misser ertussen is 87,5 procent en dus een doos omhoog (doos ' + r.echteDag.box + ')');
  ok(r.echteDag.due === addDays(r.vandaag, GRAM_BOX_TEST[3]),
    'en het onderwerp komt pas over ' + GRAM_BOX_TEST[3] + ' dagen terug (' + r.echteDag.due + ')');""")

    # de suite heeft GRAM_BOX en vandaag nodig in node; haal ze uit de pagina
    s = rep(s, """    uit.morgen = addDays(today(), 1);""",
            """    uit.morgen = addDays(today(), 1);
    uit.vandaag = today();
    uit.gramBox = GRAM_BOX.slice();   // v23.259: de suite rekent nu ook met de intervallen""")
    s = rep(s, """  console.log('\\n-- 1. de volgorde van je antwoorden doet er niet toe --');""",
            """  const GRAM_BOX_TEST = r.gramBox;
  const addDays = (d, n) => { const x = new Date(d + 'T12:00:00Z'); x.setUTCDate(x.getUTCDate() + n); return x.toISOString().slice(0, 10); };

  console.log('\\n-- 1. de volgorde van je antwoorden doet er niet toe --');""")
    schrijf(p, s)
else:
    print("pw-doos.js: al bijgewerkt")

# ---------------------------------------------------------------- pw-doorstroom.js
p, s = laad("pw-doorstroom.js")
if "GRAM_LEERBEURTEN + 1" not in s:
    s = rep(s, """  ok(breed.beurten >= 4, 'met de microles erbij telt het grammaticablok ' + breed.beurten + ' beurten');""",
    """  /* v23.259: GRAM_LEERBEURTEN ging van drie naar twee omdat de opfrisser van twee naar vijf
     vragen ging. Het aantal beurten is dus niet meer vast, maar de eis blijft dezelfde als in
     v23.255: meer dan één, en nooit meer dan de constante plus de microles. */
  ok(breed.beurten >= 2 && breed.beurten <= breed.max + 1,
    'met de microles erbij telt het grammaticablok ' + breed.beurten + ' beurten (hoogstens ' +
    (breed.max + 1) + ')');""")
    schrijf(p, s)
else:
    print("pw-doorstroom.js: al bijgewerkt")

# ---------------------------------------------------------------- pw-drill.js
p, s = laad("pw-drill.js")
if "'drill'" not in s:
    s = rep(s, """    function dag(vanaf, rij) {
      S.gram = S.gram || {};
      S.gram.proef = { box: vanaf, due: '', goed: 0, fout: 0, laatst: '', bd: '' };
      rij.forEach(function (g) { gramBij('proef', g, 3); });
      return { box: S.gram.proef.box, due: S.gram.proef.due };
    }
    const drillNaMisser = dag(3, [false, true, true, true, true, true]);
    const schoon = dag(3, [true, true, true, true, true]);
    return { drillNaMisser: drillNaMisser, schoon: schoon, morgen: addDays(today(), 1) };""",
    """    /* v23.261: het kanaal gaat mee. Tot nu toe reed deze proef op "overig", en dan toetste hij
       niet de drill maar de algemene regel. Dat die twee toevallig hetzelfde deden kwam doordat
       elke misser onherroepelijk alles kostte; sinds v23.259 is dat niet meer zo en moet de proef
       zeggen welk kanaal hij bedoelt. */
    function dag(vanaf, rij, kanaal) {
      S.gram = S.gram || {};
      S.gram.proef = { box: vanaf, due: '', goed: 0, fout: 0, laatst: '', bd: '' };
      rij.forEach(function (g) { gramBij('proef', g, 3, null, kanaal || 'microles'); });
      return { box: S.gram.proef.box, due: S.gram.proef.due, goed: S.gram.proef.goed };
    }
    const drillNaMisser = dag(3, [false, true, true, true, true, true], 'drill');
    const drillSchoon = dag(3, [true, true, true, true, true, true, true, true], 'drill');
    const schoon = dag(3, [true, true, true, true, true]);
    return { drillNaMisser: drillNaMisser, drillSchoon: drillSchoon, schoon: schoon,
             morgen: addDays(today(), 1), vandaag: today() };""")

    s = rep(s, """  ok(doos.drillNaMisser.box === 0, 'vijf goede antwoorden in een drill duwen het doosje niet omhoog');
  ok(doos.drillNaMisser.due === doos.morgen, 'het onderwerp komt gewoon morgen terug');
  ok(doos.schoon.box === 4, 'CONTROLE: zonder die misser klimt dezelfde reeks wél (' + doos.schoon.box + ')');""",
    """  /* v23.261: op het scherm van de drill staat "ze tellen niet mee voor je doosje", en vanaf nu
     dwingt de code dat af in plaats van dat het toevallig uitkwam. Een drillantwoord werkt de
     tellers bij (dat is geschiedenis) maar raakt doos en vervaldatum niet aan. */
  ok(doos.drillNaMisser.box === 3, 'een drill laat je doosje staan waar het stond (' + doos.drillNaMisser.box + ')');
  ok(doos.drillNaMisser.due === '', 'en verzet de vervaldatum niet ("' + doos.drillNaMisser.due + '")');
  ok(doos.drillNaMisser.goed === 5, 'de tellers lopen wel door: ' + doos.drillNaMisser.goed + ' goed');
  ok(doos.drillSchoon.box === 3,
    'ook acht keer goed in een drill promoveert niet (' + doos.drillSchoon.box + '), want dit meet of je de uitleg net gelezen hebt');
  ok(doos.schoon.box === 4, 'CONTROLE: dezelfde reeks via een echt kanaal klimt wél (' + doos.schoon.box + ')');""")
    schrijf(p, s)
else:
    print("pw-drill.js: al bijgewerkt")

# ---------------------------------------------------------------- pw-leermachine.js
p, s = laad("pw-leermachine.js")
if "GC_OPFRIS_VRAGEN" not in s.split("pw-gramflow.js")[0][-400:] or "inFlow.vragen <= 3" in s:
    s = rep(s, """  ok(inFlow.stappen === 1 && inFlow.vragen >= 1 && inFlow.vragen <= 3,
    'en het is één korte stap, geen tweede les (' + inFlow.stappen + ' stappen, ' + inFlow.vragen + ' vragen)');""",
    """  /* v23.259: het aantal ging van twee naar vijf, want onder de vijf antwoorden velt gramBij geen
     oordeel en zou de nieuwe doosregel nooit gelden in de dagles. De grens die hier bewaakt wordt
     is niet het getal maar de vorm: ÉÉN stap, dus geen tweede microles, en niet eindeloos lang. */
  ok(inFlow.stappen === 1 && inFlow.vragen >= 1 && inFlow.vragen <= 8,
    'en het is één korte stap, geen tweede les (' + inFlow.stappen + ' stappen, ' + inFlow.vragen + ' vragen)');""")
    schrijf(p, s)
else:
    print("pw-leermachine.js: al bijgewerkt")
