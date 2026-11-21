# suites-v23.278.py - vijf suites die de VORM van de opfrisser vastlegden in plaats van zijn maat.
#
# De opfrisser was een stap met vijf vragen. Vanaf v23.278 is hij twee stappen met dezelfde vijf
# vragen en de regel ertussen, omdat Stefan de uitleg bij elke herhaling terug wil zien en hij die
# tot nu toe precies een keer per onderwerp kreeg.
#
# Vijf suites werden daar rood van. Dat is geen fout in die suites: ze legden vast wat er stond, en
# dat is hun werk. Maar vier van de vijf schreven er zelf bij wat ze eigenlijk bedoelden:
#
#   pw-gramflow     "een afgerond onderwerp komt terug als opfrisser"
#   pw-drill        "de drill heeft er meer dan de opfrisser"
#   pw-leermachine  "de grens die hier bewaakt wordt is niet het getal maar de vorm"
#   pw-opfrisles    "een doosje dat staat blijft kort"
#
# Dat is wat er nu staat, en gemeten over alle stappen in plaats van over de eerste.
#
# De vijfde, pw-patroondoos, is een ander geval. Die legde als CONTROLE vast dat een fout in het
# wild het hele concept op nul zet. v23.278 keert dat met opzet om, dus die proef wordt niet
# aangepast maar omgedraaid: de patronen blijven staan, en het onderwerp komt terug via gcStaatFout
# in plaats van via de doos. Allebei de helften worden nagerekend, want zonder de tweede helft is
# deze ronde geen reparatie maar een versoepeling.
import io
import os

ROOT = os.path.expanduser(os.environ.get("VAMOS", "~/mnt/espanol"))


def laad(naam):
    p = os.path.join(ROOT, "test/suites", naam)
    return p, io.open(p, encoding="utf-8").read()


def rep(s, anker, nieuw, n=1):
    assert s.count(anker) == n, "anker %d keer, verwacht %d: %r" % (s.count(anker), n, anker[:80])
    return s.replace(anker, nieuw)


# ---- en de twee metingen die daarvoor nodig zijn ----
p, s2 = laad("pw-gramflow.js")
if "vragenTotaal:" not in s2:
    s2 = rep(s2, """    uit.naKlaar = gwSess ? { id: gwSess.id, stap: gwSess.stap,
                             vragen: (gwOnderwerp(gwSess.id).stappen[gwSess.stap].vragen || []).length,
                             stappen: gwOnderwerp(gwSess.id).stappen.length } : null;""",
    """    uit.naKlaar = gwSess ? { id: gwSess.id, stap: gwSess.stap,
                             vragen: (gwOnderwerp(gwSess.id).stappen[gwSess.stap].vragen || []).length,
                             /* v23.278: en over alle stappen, want de regel staat sinds die ronde
                                tussen de vragen in plaats van nergens. */
                             vragenTotaal: (gwOnderwerp(gwSess.id).stappen || []).reduce(
                               function (a, st) { return a + ((st.vragen || []).length); }, 0),
                             stappen: gwOnderwerp(gwSess.id).stappen.length } : null;""")
    io.open(p, "w", encoding="utf-8").write(s2)
    print("  meting erbij: pw-gramflow.js vragenTotaal")

p, s2 = laad("pw-opfrisles.js")
if "onderhoudN:" not in s2:
    s2 = rep(s2, """opfrisN: GC_OPFRIS_VRAGEN, lesN: GC_OPFRIS_LES_VRAGEN };""",
    """opfrisN: GC_OPFRIS_VRAGEN, lesN: GC_OPFRIS_LES_VRAGEN,
             /* v23.278: en de maat van een onderhoudsbeurt, want een doosje op doos 3 of hoger
                krijgt er sinds die ronde twee in plaats van vijf. */
             onderhoudN: GC_OPFRIS_ONDERHOUD };""")
    io.open(p, "w", encoding="utf-8").write(s2)
    print("  meting erbij: pw-opfrisles.js onderhoudN")

# ---------------------------------------------------------------- pw-gramflow.js
p, s = laad("pw-gramflow.js")
if "een of twee stappen heeft" not in s:
    s = rep(s, """  ok(!!r.naKlaar && r.naKlaar.stappen === 1, 'die één stap heeft');""",
    """  /* v23.278: hier stond `stappen === 1`. De opfrisser heeft er sinds die ronde twee, met de
     regel ertussen: Stefan zag de uitleg van een onderwerp tot dan toe precies een keer in zijn
     leven. Wat deze proef wilde vaststellen staat in de regel erboven en blijft onveranderd: een
     afgerond onderwerp komt terug als OPFRISSER en niet als de hele microles. Dat het er twee
     stappen voor gebruikt is vorm, geen maat. */
  ok(!!r.naKlaar && r.naKlaar.stappen >= 1 && r.naKlaar.stappen <= 2,
    'die een of twee stappen heeft (' + (r.naKlaar || {}).stappen + ')');""")
    s = rep(s, """  ok(!!r.naKlaar && r.naKlaar.vragen === r.opfrisVragen,
    'met ' + r.opfrisVragen + ' vragen erin (' + (r.naKlaar || {}).vragen + ')');""",
    """  /* v23.278: en dit telde de vragen van de EERSTE stap. Sinds de regel tussen de vragen staat is
     dat niet meer hetzelfde als "hoeveel vragen is deze opfrisser", dus telt het nu over alle
     stappen. Het getal komt nog steeds uit de app en niet uit deze suite. */
  ok(!!r.naKlaar && r.naKlaar.vragenTotaal === r.opfrisVragen,
    'met ' + r.opfrisVragen + ' vragen erin (' + (r.naKlaar || {}).vragenTotaal + ')');""")
    io.open(p, "w", encoding="utf-8").write(s)
    print("bijgewerkt: pw-gramflow.js")
else:
    print("pw-gramflow.js: al bijgewerkt")

# ---------------------------------------------------------------- pw-drill.js
p, s = laad("pw-drill.js")
if "hoogstens twee stappen" not in s:
    s = rep(s, """      opfrisStappen: opfris ? opfris.stappen.length : -1,
      opfris: opfris ? opfris.stappen[0].vragen.length : -1,""",
    """      opfrisStappen: opfris ? opfris.stappen.length : -1,
      /* v23.278: over alle stappen. De opfrisser heeft er sinds die ronde twee, met de regel
         ertussen, en "hoeveel vragen is dit" is dan niet meer de eerste stap. */
      opfris: opfris ? opfris.stappen.reduce(function (a, s) { return a + s.vragen.length; }, 0) : -1,""")
    s = rep(s, """  ok(maten.opfrisStappen === 1, 'nog steeds één stap: een opfrisser is geen tweede microles');""",
    """  /* v23.278: hier stond `=== 1`. Zie de kop van patch-v23.278: de opfrisser is twee stappen
     geworden met de regel ertussen. Wat deze proef bewaakt staat in de regel eronder en verandert
     niet: de drill is groter dan de opfrisser. Dat is zijn hele bestaansreden. */
  ok(maten.opfrisStappen <= 2, 'en hoogstens twee stappen: een opfrisser is geen tweede microles (' +
    maten.opfrisStappen + ')');""")
    io.open(p, "w", encoding="utf-8").write(s)
    print("bijgewerkt: pw-drill.js")
else:
    print("pw-drill.js: al bijgewerkt")

# ---------------------------------------------------------------- pw-leermachine.js
p, s = laad("pw-leermachine.js")
if "eersteUitleg" not in s:
    s = rep(s, """             vragen: gwSess ? ((gwOnderwerp(gwSess.id).stappen || [])[0] || {}).vragen.length : -1 };""",
    """             /* v23.278: over alle stappen, want de opfrisser heeft er sinds die ronde twee met
                de regel ertussen. En of je meteen in de oefening belandt staat niet in het aantal
                stappen maar in de uitleg van de EERSTE: die hoort leeg te zijn. */
             vragen: gwSess ? (gwOnderwerp(gwSess.id).stappen || []).reduce(function (a, s) {
               return a + ((s.vragen || []).length); }, 0) : -1,
             eersteUitleg: gwSess ? String(ct((((gwOnderwerp(gwSess.id).stappen || [])[0] || {}).uitleg),
               (((gwOnderwerp(gwSess.id).stappen || [])[0] || {}).uitlegEn)) || '').trim().length : -1 };""")
    s = rep(s, """  ok(inFlow.stappen === 1 && inFlow.vragen >= 1 && inFlow.vragen <= 8,
    'en het is één korte stap, geen tweede les (' + inFlow.stappen + ' stappen, ' + inFlow.vragen + ' vragen)');""",
    """  /* v23.278: hier stond `stappen === 1`. De opfrisser is twee stappen geworden met de regel
     ertussen (Stefan, 21 november: "iedere keer weer uitleg dan toetsen"). De kop hierboven zegt
     het zelf: de grens is niet het getal maar de vorm. Die vorm is nog steeds "kort, en je begint
     met een vraag en niet met een scherm vol tekst", en dat is wat er nu staat. */
  ok(inFlow.stappen <= 2 && inFlow.vragen >= 1 && inFlow.vragen <= 8,
    'en het is kort, geen tweede les (' + inFlow.stappen + ' stappen, ' + inFlow.vragen + ' vragen)');
  ok(inFlow.eersteUitleg === 0,
    'en de eerste stap zet je meteen aan het werk, zonder scherm vol tekst (' + inFlow.eersteUitleg + ' tekens)');""")
    io.open(p, "w", encoding="utf-8").write(s)
    print("bijgewerkt: pw-leermachine.js")
else:
    print("pw-leermachine.js: al bijgewerkt")

# ---------------------------------------------------------------- pw-opfrisles.js
p, s = laad("pw-opfrisles.js")
if "opDrieN" not in s:
    s = rep(s, """  ok(bouw.opDrie.stappen.length === 1, 'CONTROLE: één stap (' + bouw.opDrie.stappen.length + ')');
  ok(bouw.opDrie.stappen[0].n === bouw.opfrisN,
     'CONTROLE: en ' + bouw.opDrie.stappen[0].n + ' vragen, want dit is een opfrisser (afgesproken: ' + bouw.opfrisN + ')');""",
    """  /* v23.278: hier stond "één stap" en "vijf vragen". Twee dingen zijn sindsdien veranderd en
     allebei met opzet. De opfrisser heeft de regel ertussen gekregen, dus twee stappen. En een
     doosje op doos 3 of hoger is ONDERHOUD geworden en krijgt er twee in plaats van vijf, omdat de
     dagles er sinds diezelfde ronde drie van aanbiedt in plaats van een.

     Wat deze proef meet verandert daar niet van: een doosje dat staat krijgt geen terugvalles.
     Sterker nog, het is nu korter dan het was, en dat is de kant op die deze proef bedoelde. */
  const opDrieN = bouw.opDrie.stappen.reduce(function (a, st) { return a + st.n; }, 0);
  ok(bouw.opDrie.stappen.length <= 2,
     'CONTROLE: hoogstens twee stappen (' + bouw.opDrie.stappen.length + ')');
  ok(opDrieN === bouw.onderhoudN,
     'CONTROLE: en ' + opDrieN + ' vragen, want doos 3 is onderhoud (afgesproken: ' + bouw.onderhoudN + ')');
  ok(opDrieN < bouw.opfrisN,
     'CONTROLE: dus korter dan een gewone opfrisser (' + opDrieN + ' tegen ' + bouw.opfrisN + ')');""")
    io.open(p, "w", encoding="utf-8").write(s)
    print("bijgewerkt: pw-opfrisles.js")
else:
    print("pw-opfrisles.js: al bijgewerkt")

# ---------------------------------------------------------------- pw-patroondoos.js
p, s = laad("pw-patroondoos.js")
if "komtTerug" not in s:
    s = rep(s, """    return { kaal: gramLees('genero#') , sleutels: Object.keys(S.gram).sort(),
             p0: gramLees('genero#0').box, p2: gramLees('genero#2').box,
             bare: (S.gram.genero || {}).box, bareDue: (S.gram.genero || {}).due,
             concept: gramLees('genero').box, morgen: addDays(today(), 1) };""",
    """    /* v23.278: het ledger erbij, want dat is wat gcStaatFout() leest om te beslissen of een
       onderwerp terug moet komen. gramBij() schrijft het zelf via gramLog(). */
    return { kaal: gramLees('genero#') , sleutels: Object.keys(S.gram).sort(),
             p0: gramLees('genero#0').box, p2: gramLees('genero#2').box,
             bare: (S.gram.genero || {}).box, bareDue: (S.gram.genero || {}).due,
             concept: gramLees('genero').box, kaalBox: gramLees('genero').kaalBox,
             komtTerug: gcStaatFout(gramLees('genero'), 'genero'),
             morgen: addDays(today(), 1) };""")
    s = rep(s, """  ok(wild.concept === 0, 'CONTROLE: en het concept zegt daardoor wél nul, want dat is zijn zwakste doosje');""",
    """  /* ================= v23.278 DRAAIT DEZE PROEF OM, EN DAT IS DE HELE RONDE =================

     Hier stond: "CONTROLE: en het concept zegt daardoor wél nul, want dat is zijn zwakste doosje."
     Dat was waar en het was ook het probleem.

     Gemeten bij Stefan op 20 november: genero had 249 antwoorden, alle vijf de patronen stonden op
     doos 5 met 93 tot 100 procent goed, en het kale doosje op doos 1. Het kale doosje is de plek
     waar fouten uit de vrije zinnen landen, en het krijgt nooit gerichte oefening omdat de microles
     naar de patroondoosjes schrijft. Het kan dus alleen omlaag, en het hield genero weken in de
     focus: op 13 van de 17 dagen dat hij grammatica deed kwam genero terug.

     Vanaf nu komt het oordeel van de patronen. Maar het kale doosje mag zijn andere taak houden,
     en die staat hieronder: een verse fout in het wild brengt het onderwerp dezelfde week terug.
     Zonder die tweede helft is deze ronde geen reparatie maar een versoepeling, dus ze worden
     allebei nagerekend. */
  ok(wild.concept === Math.min(wild.p0, wild.p2) && wild.concept > 0,
    'het concept blijft staan op het zwakste PATROON (' + wild.concept + ', patronen ' +
      wild.p0 + ' en ' + wild.p2 + ')');
  ok(wild.kaalBox === 0,
    'en het kale doosje staat op nul, want daar landde de fout (' + wild.kaalBox + ')');
  ok(wild.komtTerug === true,
    'en het onderwerp komt er wel degelijk door terug: gcStaatFout zegt ja');""")
    io.open(p, "w", encoding="utf-8").write(s)
    print("bijgewerkt: pw-patroondoos.js")
else:
    print("pw-patroondoos.js: al bijgewerkt")
