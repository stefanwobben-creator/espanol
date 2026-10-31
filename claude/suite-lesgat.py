# suite-lesgat.py - pw-lesgat telde een kaart die wel uitgelegd is als niet uitgelegd.
#
# WAT ER GEMETEN IS
#
# Welke spiekbriefkaart door welke les geclaimd wordt, in het huidige bestand:
#
#     kaart 29  <-  En la ciudad o en el campo
#     kaart 30  <-  El trabajo y el tiempo libre          (met de hand aangehecht, v23.251)
#     kaart 31  <-  El turismo en España                  (met de hand aangehecht, v23.254)
#     kaart 32  <-  El transporte público en la ciudad    (met de hand aangehecht, v23.258)
#     kaart 33  <-  La tecnología en nuestra vida         (vanochtend, main staat erop rood)
#
# Vijf lessen, vijf kaarten, elke kaart geclaimd door de les die hem meebracht. Die kaart IS de
# uitleg: hij staat in CHEATSHEET, de les wijst hem aan in TRACKS[tk].lessons[].spiek, en de app
# toont hem onder "Uit je lessen". pw-lesgat kijkt alleen naar GC_CONCEPTEN en GRAMWIZ en telt hem
# daarom als onverklaard.
#
# Dat was terecht toen deze suite geschreven werd (24 augustus: 98 van de 281 toetsvragen gingen
# over stof die werkelijk nergens stond, en twaalf kaarten hadden wel een toets en geen les). Sinds
# er lessen binnenkomen die hun eigen spiekbrief meebrengen, meet hij iets anders dan hij denkt.
#
# Het gevolg was niet onschuldig: drie keer is er met de hand een kaart aan een concept gehangen om
# deze suite groen te krijgen, en elke keer stond main daarvoor dagen tot weken dicht. Dat is een
# pleister op een meetfout.
#
# WAT ER VERANDERT
#
# Een kaart die door een les geclaimd wordt, telt als uitgelegd. De harde regel blijft staan voor
# kaarten die door niets geclaimd worden, en dat is precies het geval waarvoor deze suite bestaat.
# Er komt een getal bij dat zichtbaar maakt hoeveel kaarten alleen door hun eigen les gedekt
# worden, zodat die groep niet stilletjes de norm wordt.
import io, os, sys

ROOT = os.path.expanduser(os.environ.get("VAMOS", "~/mnt/espanol"))
P = os.path.join(ROOT, "test/suites/pw-lesgat.js")
s = io.open(P, encoding="utf-8").read()

if "alleenLes" in s:
    print("al bijgewerkt")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global s
    assert s.count(anker) == n, "anker %d keer, verwacht %d: %r" % (s.count(anker), n, anker[:70])
    s = s.replace(anker, nieuw)


# ---- de kop ----
rep("""//   1. HET AANTAL ONVERKLAARDE KAARTEN LOOPT NIET OP. Dit is de eigenlijke regel.""",
    """//   1. HET AANTAL ONVERKLAARDE KAARTEN LOOPT NIET OP. Dit is de eigenlijke regel. Een kaart geldt
//      als uitgelegd zodra IETS hem claimt: een concept, een handgeschreven wizard, of de les die
//      hem meebracht.
//
//      v23.262: dat laatste stond er niet bij, en dat was een meetfout met gevolgen. Gemeten:
//
//          kaart 29  <-  En la ciudad o en el campo
//          kaart 30  <-  El trabajo y el tiempo libre        (met de hand aangehecht, v23.251)
//          kaart 31  <-  El turismo en España                (met de hand aangehecht, v23.254)
//          kaart 32  <-  El transporte público en la ciudad  (met de hand aangehecht, v23.258)
//          kaart 33  <-  La tecnología en nuestra vida       (hierop stond main vanochtend rood)
//
//      Vijf lessen op rij, elke kaart geclaimd door de les die hem meebracht. Die kaart IS de
//      uitleg: hij staat in CHEATSHEET, de les wijst hem aan, en de app toont hem onder "Uit je
//      lessen". Drie keer is er met de hand een kaart aan een concept gehangen om deze suite
//      groen te krijgen, en drie keer stond main daarvoor dagen tot weken dicht. Dat is een
//      pleister op een meetfout, en de meetfout hoort gerepareerd.
//
//      Wat NIET verandert: een kaart die door niets geclaimd wordt, is en blijft rood. Dat is het
//      geval waarvoor deze suite op 24 augustus geschreven is (98 van de 281 toetsvragen over stof
//      die werkelijk nergens stond) en dat geval komt er niet meer in.""")

# ---- de meting ----
rep("""    const metLes = {};
    gcGeordend().forEach(function (c) { ((c.spiek || {})[tk] || []).forEach(function (i) { metLes[i] = 1; }); });
    GRAMWIZ.forEach(function (o) { ((o.spiek || {})[tk] || []).forEach(function (i) { metLes[i] = 1; }); });""",
    """    const metLes = {}, metConcept = {};
    gcGeordend().forEach(function (c) { ((c.spiek || {})[tk] || []).forEach(function (i) { metLes[i] = 1; metConcept[i] = 1; }); });
    GRAMWIZ.forEach(function (o) { ((o.spiek || {})[tk] || []).forEach(function (i) { metLes[i] = 1; metConcept[i] = 1; }); });
    /* v23.262: en de lessen zelf. Een les brengt haar eigen spiekbriefkaart mee en claimt hem hier;
       die kaart is de uitleg en staat in de app onder "Uit je lessen". metConcept houdt apart bij
       wat een echt concept dekt, zodat de groep "alleen door de eigen les" zichtbaar blijft. */
    const uitLes = {};
    (((window.TRACKS || {})[tk] || {}).lessons || []).forEach(function (l) {
      (l.spiek || []).forEach(function (i) { metLes[i] = 1; if (!metConcept[i]) uitLes[i] = l.titel || l.id; });
    });""")

rep("""      n: lijst.length,
      vragenTotaal: lijst.reduce(function (a, i) { return a + vragen[i]; }, 0),
      alleVragen: QUIZZES.reduce(function (a, q) { return a + (q.vragen || []).length; }, 0)
    };""",
    """      n: lijst.length,
      vragenTotaal: lijst.reduce(function (a, i) { return a + vragen[i]; }, 0),
      alleVragen: QUIZZES.reduce(function (a, q) { return a + (q.vragen || []).length; }, 0),
      // welke kaarten alleen door hun eigen les gedekt worden, en door geen enkel concept
      alleenLes: Object.keys(uitLes).map(Number).sort(function (a, b) { return a - b; })
        .map(function (i) { return i + ' "' + uitLes[i] + '"'; })
    };""")

rep("""  ok(gat.n <= GATEN_MAX,
    'het aantal onverklaarde kaarten loopt niet op (' + gat.n + ' van maximaal ' + GATEN_MAX + ')');""",
    """  ok(gat.n <= GATEN_MAX,
    'het aantal onverklaarde kaarten loopt niet op (' + gat.n + ' van maximaal ' + GATEN_MAX + ')');
  /* Geen eis maar een getal. Een kaart die alleen door zijn eigen les wordt gedekt is uitgelegd,
     maar hij heeft geen opgeknipte microles en staat niet op de route. Zolang dat er een handvol
     zijn is dat de normale gang van zaken; loopt het op naar tientallen, dan is het leerpad in
     tweeën gegroeid en hoort daar een ronde aan besteed te worden. */
  console.log('   alleen door hun eigen les gedekt: ' +
    (gat.alleenLes.length ? gat.alleenLes.join(' | ') : 'geen'));""")

io.open(P, "w", encoding="utf-8").write(s)
print("bijgewerkt:", P)
