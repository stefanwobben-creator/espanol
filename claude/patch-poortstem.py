# patch-poortstem.py - de poort roept zijn rode suites om als GitHub-annotatie.
#
# WAAROM
#
# De poort staat sinds 11 oktober rood op deel 4 van 4 en groen op alle andere delen, twee pushes
# lang, precies 97 seconden per keer. Lokaal draaien diezelfde 42 suites groen (376s rekentijd,
# ongeveer 94s wandklok, dus de run is wel afgemaakt: er is echt iets rood, geen crash).
#
# Het probleem is niet de poort maar het zicht erop: de logs van een Actions-run zijn alleen te
# lezen als je bent ingelogd, en dat ben ik niet. Annotaties zijn dat wel, voor iedereen, via de
# API. Dus laat de poort zijn rode suites als annotatie neerzetten in plaats van alleen in het log.
#
# Dit verandert niets aan wat de poort toetst of wanneer hij dichtgaat.
import io, os, sys

P = os.path.expanduser("~/mnt/espanol/test/poort.js")
s = io.open(P, encoding="utf-8").read()

if "::error title=" in s:
    print("al gepatcht")
    sys.exit(0)

def rep(anker, nieuw, n=1):
    global s
    assert s.count(anker) == n, "anker %d keer gevonden, verwacht %d: %r" % (s.count(anker), n, anker[:60])
    s = s.replace(anker, nieuw)

ANKER = "      if (r.se) console.log((r.se || '').split('\\n').slice(-8).join('\\n'));"

NIEUW = ANKER + """
      // In GitHub Actions is het log alleen te lezen als je bent ingelogd; annotaties zijn dat
      // altijd. Dus zet elke rode suite daar ook neer, met de regels die ertoe doen.
      if (process.env.GITHUB_ACTIONS) {
        const kern = (raak.length ? raak : regels.slice(-25)).slice(-12)
          .concat((r.se || '').split('\\n').filter(Boolean).slice(-5));
        const plat = kern.join('\\n')
          .replace(/%/g, '%25').replace(/\\r/g, '%0D').replace(/\\n/g, '%0A').slice(0, 3000);
        console.log('::error title=' + r.f + (r.timeout ? ' (liep vast)' : '') + '::' + plat);
      }"""

rep(ANKER, NIEUW)

ANKER2 = "  console.log(rood.length ? 'POORT DICHT: ' + rood.map((r) => r.f).join(', ') : 'POORT OPEN');"
NIEUW2 = ANKER2 + """
  if (process.env.GITHUB_ACTIONS && rood.length) {
    console.log('::error title=poort dicht::' + rood.map((r) => r.f).join(', '));
  }"""
rep(ANKER2, NIEUW2)

io.open(P, "w", encoding="utf-8").write(s)
print("gepatcht:", P)
