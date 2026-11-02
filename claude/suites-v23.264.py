# suites-v23.264.py - de twee suites die de doosregel vastleggen, bijgewerkt op wat er gemeten is.
#
# De simulatie in pw-doosje (30 dagen, zes antwoorden per dag over vijf patronen, 200 lopen) geeft
# na v23.264 dit beeld, en dat is wat er nu vastgelegd wordt:
#
#     kennisniveau   eindigt op doos 0   eindigt op doos 4 of 5
#     foutloos                     0%                     100%
#     97%                          0%                     100%
#     93%                          0%                      98%
#     85%                          1%                      71%
#     70%                         76%                       1%
#
# Ter vergelijking, uit de kop van diezelfde suite onder de oude regel: 97 procent stond in 22
# procent van de lopen op nul, 93 procent in 45 procent, en haalde maar in 12 procent doos 4 of 5.
# De oude regel strafte dus juist wie het kende.
#
# De klif zit nu tussen 85 en 70 procent, en dat is precies waar "ken je dit" hoort te liggen.
# Dat is wat de controles hieronder bewaken: niet een vast percentage, maar dat de reeks netjes
# oploopt en dat de klif op de goede plek valt.
import io, os, sys

ROOT = os.path.expanduser(os.environ.get("VAMOS", "~/mnt/espanol"))


def laad(naam):
    p = os.path.join(ROOT, "test/suites", naam)
    return p, io.open(p, encoding="utf-8").read()


def rep(s, anker, nieuw, n=1):
    assert s.count(anker) == n, "anker %d keer, verwacht %d: %r" % (s.count(anker), n, anker[:70])
    return s.replace(anker, nieuw)


# ---------------------------------------------------------------- pw-doosje.js
p, s = laad("pw-doosje.js")
if "de klif zit tussen" not in s:
    s = rep(s, """  ok(sim.f15.opNul >= 25,
     'CONTROLE: 85% goed staat nog vaak op nul (' + sim.f15.opNul + '%) — de regel is geen cadeau');
  ok(sim.f30.hoog <= 10,
     'CONTROLE: 70% goed komt vrijwel nooit hoog (' + sim.f30.hoog + '%) — wie het niet kent, komt niet door');""",
    """  /* v23.264: hier stond dat 85 procent nog in een kwart van de lopen op nul moet eindigen, "de
     regel is geen cadeau". Dat was de eis onder de oude regel, die elke misser onherroepelijk
     afstrafte, en onder die regel stond 97 procent ook in 22 procent van de lopen op nul. Dat was
     geen strengheid maar ruis.

     Wat een doosjessysteem werkelijk moet doen is onderscheiden. Daar gaat het nu over: de reeks
     hoort netjes op te lopen met je kennisniveau, en de klif hoort te liggen waar "ken je dit"
     ligt. Gemeten na v23.264: 100, 100, 98, 71, 1 procent in doos 4 of 5. */
  ok(sim.f03.hoog >= sim.f07.hoog && sim.f07.hoog >= sim.f15.hoog && sim.f15.hoog >= sim.f30.hoog,
     'de uitkomst loopt netjes op met je kennisniveau (' +
     [sim.f03.hoog, sim.f07.hoog, sim.f15.hoog, sim.f30.hoog].join(' > ') + ')');
  ok(sim.f15.hoog - sim.f30.hoog >= 40,
     'en de klif zit tussen 85 en 70 procent (' + sim.f15.hoog + '% tegen ' + sim.f30.hoog + '%)');
  ok(sim.f30.hoog <= 10,
     'CONTROLE: 70% goed komt vrijwel nooit hoog (' + sim.f30.hoog + '%) — wie het niet kent, komt niet door');
  ok(sim.f30.opNul >= 50,
     'CONTROLE: en blijft meestal op nul staan (' + sim.f30.opNul + '%)');""")
    io.open(p, "w", encoding="utf-8").write(s)
    print("bijgewerkt: pw-doosje.js")
else:
    print("pw-doosje.js: al bijgewerkt")

# ---------------------------------------------------------------- pw-oefensessie.js
p, s = laad("pw-oefensessie.js")
if "GRAM_OORDEEL_NEER" in s:
    s = rep(s, """//   1. DRIE UITKOMSTEN IN PLAATS VAN TWEE. 75 procent of meer is een doos omhoog, 50 tot 74 blijft
//      staan, daaronder een doos omlaag. En omlaag is één doos, niet alles.
//   2. DE GRENS. Onder de vijf antwoorden verandert er niets: dan geldt de oude regel, en die is
//      hard. Zonder deze proef is punt 1 een sluiproute om met twee makkelijke antwoorden te
//      promoveren.""",
    """//   1. EEN DAG HAALT DE DREMPEL OF NIET. 75 procent of meer van je antwoorden op dit ONDERWERP is
//      een doos omhoog, daaronder een doos omlaag. En omlaag is één doos, niet alles.
//
//      v23.264 telt het bewijs over het onderwerp en niet over het losse patroondoosje. Gemeten in
//      Stefans profiel op 1 november: zestien doosjes geraakt, veertien met precies één antwoord,
//      nul met vijf. Een opfrisser van vijf vragen rouleert namelijk over vijf patronen, en elk
//      patroon heeft zijn eigen doosje. Per doosje werd de drempel dus nooit gehaald en gold de
//      hele regel van v23.259 in de praktijk nooit.
//
//      En de middenband van v23.259 is weg: die liet een leerling die 70 procent kent elke dag een
//      beetje klimmen, want zakken vroeg daar minder dan 50 procent. Zie pw-doosje voor de cijfers.
//   2. HET PATROON WAAR JE OP MISGING GAAT NIET MEE OMHOOG, maar valt ook niet terug. Dat is het
//      verschil tussen "je kent dit onderwerp niet" en "deze ene ging mis".
//   3. DE GRENS. Onder de vijf antwoorden verandert er niets: dan geldt de oude regel, en die is
//      hard. Zonder deze proef is punt 1 een sluiproute om met twee makkelijke antwoorden te
//      promoveren.""")

    s = rep(s, """    return {
      min: GRAM_OORDEEL_MIN, op: GRAM_OORDEEL_OP, neer: GRAM_OORDEEL_NEER,
      maxDoos: GRAM_BOX.length - 1, morgen: addDays(today(), 1),
      // 4 van 5 = 80 procent: omhoog
      omhoog: dag(3, [G, G, F, G, G]),
      // 3 van 5 = 60 procent: blijft staan
      blijft: dag(3, [G, F, G, F, G]),
      // 2 van 5 = 40 procent: een doos omlaag, en niet naar nul
      omlaag: dag(3, [F, G, F, G, F]),
      // vier antwoorden met een misser: te weinig voor een oordeel, dus de oude regel
      tekort: dag(3, [G, G, G, F]),
      // de bodem
      bodem: dag(0, [F, F, F, F, G]),
      // het plafond
      plafond: dag(5, [G, G, G, G, G])
    };""",
    """    /* v23.264: vijf antwoorden verdeeld over vijf patronen van hetzelfde onderwerp. Dit is wat
       een opfrisser werkelijk doet, en het geval waarop de regel van v23.259 stukliep. */
    function verdeeld(vanaf, rij) {
      S.gram = {};
      rij.forEach(function (g, i) {
        S.gram['proef#' + i] = { box: vanaf, due: '', goed: 0, fout: 0, laatst: '', bd: '' };
      });
      rij.forEach(function (g, i) { gramBij('proef', g, 3, i, 'sessie'); });
      return rij.map(function (g, i) { return S.gram['proef#' + i].box; });
    }
    return {
      min: GRAM_OORDEEL_MIN, op: GRAM_OORDEEL_OP,
      maxDoos: GRAM_BOX.length - 1, morgen: addDays(today(), 1),
      // 4 van 5 = 80 procent: omhoog
      omhoog: dag(3, [G, G, F, G, G]),
      // 3 van 5 = 60 procent: onder de drempel, dus een doos omlaag
      zestig: dag(3, [G, F, G, F, G]),
      // 2 van 5 = 40 procent: ook een doos omlaag, en niet naar nul
      omlaag: dag(3, [F, G, F, G, F]),
      // vier antwoorden met een misser: te weinig voor een oordeel, dus de oude regel
      tekort: dag(3, [G, G, G, F]),
      // de bodem
      bodem: dag(0, [F, F, F, F, G]),
      // het plafond
      plafond: dag(5, [G, G, G, G, G]),
      // vijf patronen, vier goed en één mis: de vier omhoog, de misser blijft staan
      perPatroon: verdeeld(2, [G, G, F, G, G]),
      // en als het onderwerp als geheel zakt, zakt ook het patroon dat je goed had
      perPatroonZwak: verdeeld(2, [G, F, F, F, G])
    };""")

    s = rep(s, """  console.log('   omhoog ' + doos.omhoog.box + ' · blijft ' + doos.blijft.box +
    ' · omlaag ' + doos.omlaag.box + ' · tekort ' + doos.tekort.box);
  ok(doos.min === 5, 'een oordeel gaat over minstens ' + doos.min + ' antwoorden');
  ok(doos.omhoog.box === 4, 'vier van de vijf goed (80%) is een doos omhoog: 3 → ' + doos.omhoog.box);
  ok(doos.blijft.box === 3, 'drie van de vijf (60%) blijft staan: 3 → ' + doos.blijft.box);
  ok(doos.blijft.due === doos.morgen, 'en komt morgen terug');
  ok(doos.omlaag.box === 2, 'twee van de vijf (40%) is EEN doos omlaag: 3 → ' + doos.omlaag.box);
  ok(doos.omlaag.due === doos.morgen, 'en komt ook morgen terug');""",
    """  console.log('   omhoog ' + doos.omhoog.box + ' · 60% ' + doos.zestig.box +
    ' · omlaag ' + doos.omlaag.box + ' · tekort ' + doos.tekort.box +
    ' · per patroon ' + JSON.stringify(doos.perPatroon));
  ok(doos.min === 5, 'een oordeel gaat over minstens ' + doos.min + ' antwoorden');
  ok(doos.omhoog.box === 4, 'vier van de vijf goed (80%) is een doos omhoog: 3 → ' + doos.omhoog.box);
  ok(doos.zestig.box === 2, 'drie van de vijf (60%) haalt de drempel niet: 3 → ' + doos.zestig.box);
  ok(doos.zestig.due === doos.morgen, 'en komt morgen terug');
  ok(doos.omlaag.box === 2, 'twee van de vijf (40%) is EEN doos omlaag en niet naar nul: 3 → ' + doos.omlaag.box);
  ok(doos.omlaag.due === doos.morgen, 'en komt ook morgen terug');

  console.log('\\n-- 1b. vijf patronen, vier goed en één mis --');
  ok(JSON.stringify(doos.perPatroon) === JSON.stringify([3, 3, 2, 3, 3]),
    'de vier goede patronen gaan omhoog, het gemiste blijft staan: ' + JSON.stringify(doos.perPatroon));
  ok(JSON.stringify(doos.perPatroonZwak) === JSON.stringify([1, 1, 1, 1, 1]),
    'maar zakt het onderwerp als geheel, dan zakt ook wat je goed had: ' + JSON.stringify(doos.perPatroonZwak));""")

    io.open(p, "w", encoding="utf-8").write(s)
    print("bijgewerkt: pw-oefensessie.js")
else:
    print("pw-oefensessie.js: al bijgewerkt")
