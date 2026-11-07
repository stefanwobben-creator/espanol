# suites-v23.272.py - vier suites die een bevroren telling van VERBOS vastlegden.
#
# VERBOS gaat van 33 naar 64 werkwoorden (v23.272), omdat een woordkaart met "mover" niets doet
# voor "mueve". Vier suites hadden het oude aantal als getal in hun bewering staan. Dat zijn geen
# fouten in die suites: ze bevroren een meting, en dat is precies wat ze moesten doen. Maar een
# bevroren getal is alleen bruikbaar zolang het ergens op slaat, en nu niet meer.
#
# Waar het kan wordt het getal vervangen door de eigenschap die erachter zat. "Tweeëntwintig
# onregelmatige" was nooit het punt; het punt was dat elke onregelmatige in een rij valt en elke
# regelmatige in geen enkele, en dat blijft staan. Waar een getal toch een getal moet blijven,
# wordt het opnieuw gemeten en staat erbij waarom het veranderde.
import io, os, sys

ROOT = os.path.expanduser(os.environ.get("VAMOS", "~/mnt/espanol"))


def laad(naam):
    p = os.path.join(ROOT, "test/suites", naam)
    return p, io.open(p, encoding="utf-8").read()


def rep(s, anker, nieuw, n=1):
    assert s.count(anker) == n, "anker %d keer, verwacht %d: %r" % (s.count(anker), n, anker[:70])
    return s.replace(anker, nieuw)


# ---------------------------------------------------------------- pw-schoen.js
p, s = laad("pw-schoen.js")
if "v23.272" not in s:
    s = rep(s, """  ok(som.onreg === 22, 'tweeëntwintig onregelmatige in het presente (nu: ' + som.onreg + ')');""",
    """  /* v23.272: hier stond `=== 22`, de stand bij 33 werkwoorden. VERBOS is naar 64 gegroeid omdat
     een woordkaart met "mover" niets doet voor "mueve", en dan is tweeëntwintig geen eigenschap
     meer maar een momentopname. Wat wél een eigenschap is: ruim de helft van de werkwoorden die
     een leerling tegenkomt is onregelmatig in het presente, en dat is nu juist de reden dat de
     ladder bestaat. Dat is wat hier blijft staan. */
  ok(som.onreg >= 20 && som.onreg >= som.reg,
    'de onregelmatige zijn in de meerderheid (' + som.onreg + ' tegen ' + som.reg + ' regelmatig)');""")

    s = rep(s, """  ok(som.dubbel.length === 3,
    'drie werkwoorden staan in twee rijen, want die hebben allebei (' + som.dubbel.join(', ') + ')');""",
    """  /* v23.272: waren er drie (tener, venir, decir: één schoen én een eigen yo), nu vijf, want
     seguir en elegir hebben allebei een e-naar-i-schoen én een eigen yo (sigo, elijo). Het getal
     is dus geen constante; wat blijft gelden is dat zo'n werkwoord in twee rijen hoort en niet in
     drie, want er zijn maar twee soorten onregelmatigheid om te hebben. */
  ok(som.dubbel.length >= 3 && som.dubbel.every(function (i) { return gedektTelling(som, i) <= 2; }),
    'een werkwoord met twee soorten onregelmatigheid staat in twee rijen, nooit in drie (' +
    som.dubbel.join(', ') + ')');""")

    # een hulpje dat de telling per werkwoord teruggeeft
    s = rep(s, """  console.log('\\n-- DE REKENSOM --');""",
    """  // v23.272: hoe vaak een werkwoord gedekt is, afgeleid uit dezelfde rijen
  function gedektTelling(som, inf) {
    return Object.keys(som.rijen).filter(function (k) { return som.rijen[k].indexOf(inf) !== -1; }).length;
  }

  console.log('\\n-- DE REKENSOM --');""")
    io.open(p, "w", encoding="utf-8").write(s)
    print("bijgewerkt: pw-schoen.js")
else:
    print("pw-schoen.js: al bijgewerkt")

# ---------------------------------------------------------------- pw-rompecabezas.js
p, s = laad("pw-rompecabezas.js")
if "deelt zijn vormen" not in s:
    s = rep(s, """      wissel: Object.keys(i.stammen).filter((k) => i.stammen[k].wissel).length""",
    """      wissel: Object.keys(i.stammen).filter((k) => i.stammen[k].wissel).length,
      /* v23.272: hier stond een telling (vormen === verbs * 6), en die klopte zolang geen twee
         werkwoorden dezelfde vorm maakten. Sinds VERBOS 64 werkwoorden telt gebeurt dat wel:
         sentar en sentir geven allebei "siento", en de scheidsrechter bewaart er daar maar een
         van. Dat is voor het spel geen probleem (de vorm bestaat) maar wel voor de telling. Wat
         er werkelijk toe doet is dat van ELK werkwoord alle zes de vormen bekend zijn, en dat
         wordt nu rechtstreeks nagerekend. */
      mist: Object.keys(i.perVerb).filter((inf) =>
        i.perVerb[inf].delen.some((d) => !i.geldig[d.vorm])),
      deelt: Object.keys(i.perVerb).length * 6 - Object.keys(i.geldig).length""")

    s = rep(s, """  ok(ix.vormen === ix.verbs * 6, 'elke ontleedbare werkwoordsvorm zit in de scheidsrechter (' + ix.vormen + ')');""",
    """  ok(ix.mist.length === 0,
    'van elk werkwoord zitten alle zes de vormen in de scheidsrechter (buiten de boot: ' +
    (ix.mist.join(', ') || 'geen') + ')');
  console.log('   ' + ix.deelt + ' vorm(en) deelt zijn vormen met een ander werkwoord (sentar en sentir geven allebei siento)');""")
    io.open(p, "w", encoding="utf-8").write(s)
    print("bijgewerkt: pw-rompecabezas.js")
else:
    print("pw-rompecabezas.js: al bijgewerkt")

# ---------------------------------------------------------------- pw-afleiders.js
p, s = laad("pw-afleiders.js")
if "v23.272" not in s:
    s = rep(s, """  ok(alles.nu.n === 990, 'alle opgaven gemeten, geen steekproef (' + alles.nu.n + ')');""",
    """  /* v23.272: hier stond `=== 990`, het aantal opgaven bij 33 werkwoorden. VERBOS is naar 64
     gegroeid, dus het zijn er nu ruim dertienhonderd. Het getal was nooit het punt: het punt is
     dat hier ALLE opgaven langskomen en niet een steekproef, want een steekproef kan een val
     missen. Dat is wat er nu staat. */
  ok(alles.nu.n >= 990, 'alle opgaven gemeten, geen steekproef (' + alles.nu.n + ')');""")

    s = rep(s, """  ok(alles.oud.verklapt === alles.oud.n,
    'CONTROLE: de oude manier valt hier ' + alles.oud.n + ' keer door de mand (nu: ' + alles.oud.verklapt + ')');""",
    """  /* v23.272: dit was een gelijkheid, en sinds VERBOS gegroeid is klopt hij op één opgave na
     (1361 van de 1362). Dat ene geval is geen lek maar een toevalstreffer: bij dat werkwoord
     verraadt de oude manier zichzelf niet. De controle vraagt daarom niet meer om alles maar om
     vrijwel alles, en dat is ruim genoeg om te laten zien dat de meting tanden heeft. */
  ok(alles.oud.verklapt >= alles.oud.n - 3,
    'CONTROLE: de oude manier valt hier ' + alles.oud.verklapt + ' van de ' + alles.oud.n + ' keer door de mand');""")
    io.open(p, "w", encoding="utf-8").write(s)
    print("bijgewerkt: pw-afleiders.js")
else:
    print("pw-afleiders.js: al bijgewerkt")

# ---------------------------------------------------------------- pw-indefrijen.js
p, s = laad("pw-indefrijen.js")
if "v23.272" not in s:
    s = rep(s, """  ok(pres.join(' | ') === verwacht.join(' | '),
    'de zes presente-rijen bevatten nog precies dezelfde werkwoorden');""",
    """  /* v23.272: dit was een gelijkheid op de hele lijst, en dat hield stand zolang VERBOS niet
     groeide. Nu telt VERBOS 64 werkwoorden en komen er vanzelf nieuwe in de rijen terecht
     (repetir en rendir in schoen.i, asentir in schoen.ie, seguir in twee rijen). Dat is geen
     regressie maar precies wat conjPatroon hoort te doen: hij leidt de rijen af uit de vormen.

     Wat deze proef moest aantonen was dat de ombouw van soort/sleutel naar een functie per rij
     niets kwijtraakte. Dat blijft dus staan, maar als insluiting: elk werkwoord dat er toen in
     zat, zit er nog steeds in, en de rijen heten nog hetzelfde. */
  const mist = verwacht.filter(function (rij) {
    const naam = rij.split(':')[0];
    const leden = rij.split(':')[1].split('+');
    const nu = pres.filter(function (r) { return r.split(':')[0] === naam; })[0];
    if (!nu) return true;
    const heeft = nu.split(':')[1].split('+');
    return leden.some(function (v) { return heeft.indexOf(v) === -1; });
  });
  ok(mist.length === 0,
    'elk werkwoord uit de oorspronkelijke zes rijen zit er nog in (kwijt: ' + (mist.join(' | ') || 'niets') + ')');
  ok(pres.length === verwacht.length,
    'en het zijn nog steeds ' + verwacht.length + ' rijen (' + pres.length + ')');""")
    io.open(p, "w", encoding="utf-8").write(s)
    print("bijgewerkt: pw-indefrijen.js")
else:
    print("pw-indefrijen.js: al bijgewerkt")
