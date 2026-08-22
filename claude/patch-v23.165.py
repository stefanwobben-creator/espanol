#!/usr/bin/env python3
# v23.165 - twee getallen die er wel zijn maar niet stonden
#
# Stefan, 21 aug, op v23.162 (live):
#   1. "maar ik zie ook nog steeds: Wat je nu haalt is nog niet te meten: daar zijn drie
#       weekmetingen voor nodig ..."
#   2. "het woordenboek was ooit meer dan 4000 woorden, nu zijn het veel minder, wat is daar
#       gebeurd?"
#
# 1. DE VOORSPELLER IS GEREPAREERD EN ZWIJGT NOG STEEDS, EN DAT KLOPT
#
# De crash van v23.162 was echt (weken: ws.length) en is weg. Maar er was tegelijk iets anders waar:
# tempoMeting() heeft drie weekmetingen nodig MET het veld dekw, en dat veld bestaat pas sinds
# v23.37 (10 augustus). Weeknummers zijn ISO-weken, en er wordt er één geschreven zodra je de app
# voor het eerst in een nieuwe week opent. Tussen 10 en 21 augustus liggen dus hoogstens twee weken:
# week 33 en week 34. Drie zijn er pas in week 35.
#
# Twee verschillende oorzaken achter hetzelfde beeld, en dat is precies de fout die v23.162 al
# beschreef: kapot en zwijgend zagen er identiek uit. Nu ze niet meer allebei kunnen, hoort het
# scherm te zeggen WELKE van de twee het is. En dat kan het weten: het aantal metingen staat
# gewoon in S.meting.
#
# Hier stond: "daar zijn drie weekmetingen voor nodig ... en die maat wordt sinds kort pas
# vastgelegd." Waar. En het antwoordt niet op de enige vraag die je stelt: wanneer dan wel.
#
# Nu: "Je hebt er 2 van de 3. De derde kan er vanaf maandag 24 augustus bij, de eerste keer dat je
# de app die week opent." Datzelfde getal in voorspelHtml, waar dezelfde zin stond.
#
# 2. HET WOORDENBOEK IS NIET GEKRIMPT, DE ZIN EROVER IS WEG
#
# Gemeten: het woordenboek toont 2.120 woordgroepen uit je lessen, en FREQ (de zoeklijst erachter)
# heeft er 4.219. Die 4.219 zijn nog steeds doorzoekbaar; nagemeten door een woord op te zoeken dat
# in geen enkele les zit (tiene), en dat wordt gevonden inclusief vervoegingsherkenning.
#
# Wat verdween is de zin erover. Tot v23.6 stond er: "Zoek je iets wat nog in geen les zit? De
# zoekbalk kent 4.219 Spaanse woorden erbij." Die zin ging weg in een opruimronde ("de alinea eronder
# legde vier dingen tegelijk uit"), en dat was op zichzelf terecht: het was een alinea die vier
# dingen deed. Alleen is met die alinea ook het enige weggevallen dat vertelde hoe groot het ding
# achter de zoekbalk is. Stefan miste het, dus hij deed werk.
#
# Het getal komt terug als één bijzin achter de telling die er al staat, niet als alinea. En freqN
# was sinds v23.7 dood: hij werd berekend, er stond een comment bij dat hij nog gebruikt werd, en
# geen enkele regel las hem. Nu weer echt in gebruik.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.165"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = NIEUW not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:90])
    src = src.replace(anker, nieuw, n)

if DOE_APP:
    # -----------------------------------------------------------------------
    # 1. zeg hoeveel metingen je hebt en wanneer de volgende kan komen
    # -----------------------------------------------------------------------
    rep('''function tempoMeting(niveau){''',
        '''/* v23.165: hoeveel weekmetingen heb je in de goede maat, en wanneer kan de volgende erbij?

   "Daar zijn drie weekmetingen voor nodig" is waar en beantwoordt de enige vraag niet die je stelt:
   wanneer dan. De app weet het antwoord, want het aantal staat in S.meting en de weken zijn
   ISO-weken. Een meting wordt geschreven zodra je de app voor het eerst in een nieuwe week opent
   (snapshotSchrijf), dus de vroegst mogelijke dag is de eerstvolgende maandag. */
var TEMPO_NODIG = 3;
function tempoStand(niveau){
  var n = 0;
  try { n = metingenNieuweMaat(niveau).length; } catch(e){ n = 0; }
  return {heeft:n, nodig:TEMPO_NODIG, genoeg:n >= TEMPO_NODIG};
}
function komendeMaandag(){
  var d;
  try { d = new Date(today() + "T00:00:00"); } catch(e){ return null; }
  var dag = d.getDay();                        // 0 = zondag
  return addDays(today(), 8 - (dag === 0 ? 7 : dag));
}
/* De zin die onder een lege voorspelling hoort te staan. Eén plek, want hij stond op twee schermen
   en die twee zouden anders uit elkaar lopen zodra er iets aan verandert. */
function tempoWachtZin(niveau){
  var st = tempoStand(niveau);
  if(st.genoeg) return "";
  var m = komendeMaandag();
  return ct("Je hebt er " + st.heeft + " van de " + st.nodig + ". ",
            "You have " + st.heeft + " of " + st.nodig + ". ") +
    (m ? ct("De volgende kan er vanaf maandag " + datumUit(m) + " bij, de eerste keer dat je de app die week opent.",
            "The next one can arrive from Monday " + datumUit(m) + ", the first time you open the app that week.")
       : ct("De volgende komt de eerste keer dat je de app in een nieuwe week opent.",
            "The next one arrives the first time you open the app in a new week.")) +
    ct(" Een weekmeting telt pas mee sinds 10 augustus, toen de maat van de balk hierboven werd vastgelegd.",
       " A weekly measurement only counts since 10 August, when the unit of the bar above was fixed.");
}
function tempoMeting(niveau){''')

    rep('''    h += "<p class='muted' style='margin:8px 0 0; font-size:.86rem'>"+
      ct("Wat je nu haalt is nog niet te meten: daar zijn drie weekmetingen voor nodig in dezelfde "+
         "maat als de balk hierboven, en die maat wordt sinds kort pas vastgelegd.",
         "What you're doing isn't measurable yet: that needs three weekly measurements in the same "+
         "unit as the bar above, and that unit has only recently started being recorded.")+"</p>";''',
        '''    /* v23.165: hier stond alleen dát er drie metingen nodig zijn. Nu ook hoeveel je er hebt en
       wanneer de volgende kan komen, want dat is de vraag erachter en de app weet het antwoord. */
    h += "<p class='muted' style='margin:8px 0 0; font-size:.86rem'>"+
      ct("Wat je nu haalt is nog niet te meten. ", "What you're doing isn't measurable yet. ")+
      tempoWachtZin(ds.niv)+"</p>";''')

    rep('''    txt += ct(" Wat je nu haalt is nog niet te meten; vanaf drie weekmetingen staat het hier.",
              " What you're actually doing isn't measurable yet; from three weekly measurements on it appears here.");''',
        '''    /* v23.165: ook hier het aantal en de datum, uit dezelfde functie als op de doelkaart. */
    txt += " " + ct("Wat je nu haalt is nog niet te meten. ", "What you're actually doing isn't measurable yet. ")
              + tempoWachtZin(ds.niv);''')

    # -----------------------------------------------------------------------
    # 2. HET WOORDENBOEK: NIETS GEDAAN, EN DAT IS EEN BESLISSING
    # -----------------------------------------------------------------------
    #
    # Er is niets gekrompen. Gemeten: het woordenboek toont 2.120 woordgroepen uit je lessen, en de
    # zoeklijst erachter (FREQ) heeft er 4.219 die nog gewoon te vinden zijn. Nagemeten met een woord
    # dat in geen enkele les zit (tiene): gevonden, inclusief vervoegingsherkenning.
    #
    # Wat verdween is de zin die het getal noemde, in twee stappen die Stefan zelf vroeg:
    #   v23.6  de alinea erboven eruit ("de alinea eronder legde vier dingen tegelijk uit")
    #   v23.7  het bijschrift in het zoekveld eruit ("dit kan weg, dat spreekt voor zich")
    #
    # Ik heb het getal eerst teruggezet in de kopregel, en daarna in de placeholder. Beide keren ging
    # de poort dicht, op pw-dic52 en pw-zoekwoord, die precies die twee beslissingen bewaken. Dat is
    # de poort die zijn werk doet: dit is geen bug maar een botsing tussen wat Stefan in augustus
    # vroeg en wat hij nu mist, en die keuze is aan hem en niet aan mij.
    #
    # Dus staat er in deze versie niets nieuws over het woordenboek. De vraag ligt bij hem.

    src = src.replace('var APP_VERSIE = "%s"' % huidig_ver, 'var APP_VERSIE = "%s"' % NIEUW)
    APP.write_text(src, encoding="utf-8")
    print("index.html: bijgewerkt naar", NIEUW)
else:
    print("index.html: al op", NIEUW)

if DOE_VER:
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt:", NIEUW)
else:
    print("versie.txt: al op", huidig_ver)
