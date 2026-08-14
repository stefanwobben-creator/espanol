#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.92: een goedkope handeling mag geen dure staat veranderen (punt 1, 2, 5 en 13).

Vier reparaties die op het eerste gezicht niets met elkaar te maken hebben, maar drie ervan zijn
dezelfde fout in drie gedaanten: ergens mocht een kleine handeling een grote, langdurige staat
veranderen. Ze horen daarom in één patch, met deze kop eronder als regel voor de volgende keer.

## Punt 1: aanklikken telde als bewijs dat je een woord kent

`avtSrsBij()` zette `st.k = 1`, met als toelichting "hier typ je het woord zelf". Dat klopte voor
twee van de vijf aanroepers. De andere drie zijn een klik op een meerkeuze-optie (via avtAntwoord)
en het galgje, waar je letters raadt.

Gevolg, en het is groter dan het lijkt. `wCheckNodig()` slaat de Laatste stap over zodra `st.k`
bestaat, dus één klik in Aventura zette dat scherm voorgoed uit voor dat woord. En `answerWord` mag
met `k` doorklimmen tot de laatste doos, dus daarna vulde "wist ik" weer je A1-balk. Precies wat
v20.0 wilde blokkeren. Stefan heeft de Laatste stap in 814 woorden nooit gezien.

Nu draagt `avtSrsBij` een derde parameter `getypt`, en alleen de twee plekken waar je echt intikt
(het kruiswoord en de schrijfronde) geven hem mee. `avtAntwoord` krijgt hem door van zijn eigen
aanroepers: de optieknoppen geven false, het invoerveld geeft true.

## Punt 2: je kon door het wachten heen spelen

`spelSrsBij()` en `avtSrsBij()` keken niet of een woord vandaag aan de beurt was. Drie spellen achter
elkaar met hetzelfde woord brachten het van doos 0 naar doos 3 in tien minuten, met een wachttijd van
zeven dagen erachter, terwijl je het nooit uit een leeg hoofd hebt hoeven halen. Het wachten is het
werkzame bestanddeel; dat kun je niet inhalen door harder te oefenen.

Nu: één doos per dag per woord, via `st.bd` (de dag waarop de doos voor het laatst steeg). Verder
spelen levert nog steeds punten en plezier op, alleen geen extra doos. Dat is ook eerlijker, want
anders wordt vaker spelen beloond met een balk die niets meer meet.

Bewust NIET toegepast op de flashcard zelf: die serveert alleen woorden die vandaag aan de beurt
zijn, dus daar kan het niet gebeuren, behalve bij het herleren na een fout. En dat moet juist wel
dezelfde dag nog een keer langskomen.

## Punt 5: grammatica sprong te snel naar gekend

`gramBij()` verhoogde de doos bij elk goed antwoord. Vijf goede antwoorden in één sessie zetten een
onderwerp van doos 0 naar doos 5, en dan zie je het onderwerp 55 dagen niet meer. Zelfde ziekte,
zelfde medicijn: het aantal goede antwoorden blijft gewoon oplopen, de doos stijgt hoogstens één keer
per dag.

## Punt 13: wat de AI terugstuurt ging ongecontroleerd het scherm op

`af.innerHTML = ... + res.uitleg` zette modeltekst rechtstreeks in de pagina. Staat daar opmaakcode
in, dan wordt die uitgevoerd in plaats van getoond. Er is nu één functie `veiligHtml()` die dat
afvangt, en die staat vlak boven de plek waar hij nodig is.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.92"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.92" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:220])
    src = src.replace(anker, nieuw, n)


# ---------------------------------------------------------------- punt 1 en 2: avtSrsBij
A_AVTSRS = '''function avtSrsBij(w, goed){
  var t = today();
  var st = S.srs[w.id];
  if(!st){ st = {box:0, due:t}; S.newIntro[t] = (S.newIntro[t]||0) + 1; }
  st.n = (st.n||0) + 1;
  if(goed){
    // v20.0: hier typ je het woord zelf, zonder het antwoord voor je. Dat is precies de check die
    // de flashcard niet kan geven, dus die telt ook.
    st.k = 1;
    st.box = Math.min(st.box + 1, INTERVALS.length - 1);
    st.due = addDays(t, INTERVALS[st.box]);
    addXP(2); trackPoging(false);
  } else {'''

N_AVTSRS = '''/* v23.92: `getypt` erbij, en het is geen detail.

   Hier stond onvoorwaardelijk `st.k = 1` met de toelichting "hier typ je het woord zelf". Dat gold
   voor twee van de vijf aanroepers. De andere drie zijn een klik op een meerkeuze-optie en het
   galgje. Een klik uit vier is geen productie, en `k` is definitief: `wCheckNodig()` slaat de
   Laatste stap over zodra hij bestaat, en `answerWord` mag er de laatste doos mee halen op een
   zelfbeoordeling. Eén klik in Aventura zette de hele bewijsvoering van v20.0 uit voor dat woord.

   En de dagrem (`st.bd`): de doos mag hoogstens één keer per dag stijgen. Zonder die rem brachten
   drie spellen achter elkaar hetzelfde woord in tien minuten naar doos 3. Het wachten is wat werkt;
   dat kun je niet inhalen door meer te spelen. Punten en plezier blijven, de doos niet. */
function avtSrsBij(w, goed, getypt){
  var t = today();
  var st = S.srs[w.id];
  if(!st){ st = {box:0, due:t}; S.newIntro[t] = (S.newIntro[t]||0) + 1; }
  st.n = (st.n||0) + 1;
  if(goed){
    if(getypt) st.k = 1;
    if(st.bd !== t){
      st.bd = t;
      st.box = Math.min(st.box + 1, getypt ? INTERVALS.length - 1 : Math.max(0, INTERVALS.length - 2));
      st.due = addDays(t, INTERVALS[st.box]);
    }
    addXP(2); trackPoging(false);
  } else {'''

# ---------------------------------------------------------------- punt 1: de aanroepers
A_ANTW = 'function avtAntwoord(op){'
A_ANTW_GOED = '''    else { avtSrsBij(w, true); }'''
A_ANTW_FOUT = '''    else { avtSrsBij(w, false); }'''

A_AHOR = '''      a.af = "goed"; a.reeks++;
      if(wOrig) avtSrsBij(wOrig, true); else { addXP(2); updateBadge(); }'''
A_KRUIS = '''          wo.klaar = true;
          if(wOrig) avtSrsBij(wOrig, true); else { addXP(2); updateBadge(); }'''
A_SCHRIJF = '''        avtSrsBij(dw, goedc);'''

A_KNOP = '''      b.onclick = function(){ avtAntwoord(g.opties[+b.getAttribute("data-avto")]); };'''
A_INVOER = '''        avtAntwoord({goed:goedb});'''

# ---------------------------------------------------------------- punt 2: spelSrsBij
A_SPEL = '''  if((st.box || 0) >= SPEL_PLAFOND) return false;
  var t = today();
  st.box = Math.min((st.box || 0) + 1, SPEL_PLAFOND);'''

N_SPEL = '''  if((st.box || 0) >= SPEL_PLAFOND) return false;
  var t = today();
  // v23.92: de dagrem. Zie de kop van avtSrsBij: drie spellen op één middag brachten een woord
  // van doos 0 naar doos 3 zonder dat je het ooit hebt hoeven ophalen.
  if(st.bd === t) return false;
  st.bd = t;
  st.box = Math.min((st.box || 0) + 1, SPEL_PLAFOND);'''

# ---------------------------------------------------------------- punt 5: gramBij
A_GRAM = '''  if(goed){
    st.goed++;
    st.box = Math.min((st.box || 0) + 1, GRAM_BOX.length - 1);
    st.due = addDays(today(), GRAM_BOX[st.box]);
  } else {'''

N_GRAM = '''  if(goed){
    st.goed++;
    /* v23.92: dezelfde dagrem als bij de woorden. Vijf goede antwoorden in één sessie zetten dit
       onderwerp van doos 0 naar doos 5, en dan zag je het 55 dagen niet meer, na één goede bui.
       Het aantal goede antwoorden loopt gewoon door; alleen de doos wacht op morgen. */
    if(st.bd !== today()){
      st.bd = today();
      st.box = Math.min((st.box || 0) + 1, GRAM_BOX.length - 1);
      st.due = addDays(today(), GRAM_BOX[st.box]);
    }
  } else {'''

# ---------------------------------------------------------------- punt 13: de AI-uitvoer
A_AI_OK = '''        af.innerHTML = "<div class='feedback ok'>\U0001f916 Claude: ja, jouw variant is ook goed Spaans! (+4 "+xpw()+")<br>"+res.uitleg+"</div>";'''
A_AI_FOUT = '''        af.innerHTML = "<div class='feedback fout'>\U0001f916 Claude: helaas, niet helemaal. "+res.uitleg+"</div>";'''

A_AI_HAAK = '''  var ba = document.getElementById("btnAiCheck");
  if(ba) ba.onclick = function(){'''

N_AI_HAAK = '''  var ba = document.getElementById("btnAiCheck");
  if(ba) ba.onclick = function(){'''

A_VEILIG_PLEK = '''function aiFoutTekst('''

if DOE_APP:
    ontbreekt = [n for n, a in (
        ("avtSrsBij", A_AVTSRS), ("avtAntwoord", A_ANTW), ("het galgje", A_AHOR),
        ("het kruiswoord", A_KRUIS), ("de schrijfronde", A_SCHRIJF), ("de optieknoppen", A_KNOP),
        ("het invoerveld", A_INVOER), ("spelSrsBij", A_SPEL), ("gramBij", A_GRAM),
        ("de AI-uitslag", A_AI_OK), ("aiFoutTekst", A_VEILIG_PLEK)) if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht; %s staat er niet zoals verwacht.\n"
              "Deze patch bouwt op v23.91. Eerst bijtrekken:\n\n    git pull --rebase\n" % ", ".join(ontbreekt))
        sys.exit(1)

    rep(A_AVTSRS, N_AVTSRS)
    rep(A_ANTW, 'function avtAntwoord(op, getypt){')
    rep(A_ANTW_GOED, '    else { avtSrsBij(w, true, getypt); }')
    rep(A_ANTW_FOUT, '    else { avtSrsBij(w, false, getypt); }')
    # het galgje: je raadt letters, dat is geen intikken
    rep(A_AHOR, A_AHOR.replace('avtSrsBij(wOrig, true)', 'avtSrsBij(wOrig, true, false)'))
    # het kruiswoord en de schrijfronde: hier tik je het woord blind in
    rep(A_KRUIS, A_KRUIS.replace('avtSrsBij(wOrig, true)', 'avtSrsBij(wOrig, true, true)'))
    rep(A_SCHRIJF, '        avtSrsBij(dw, goedc, true);')
    rep(A_KNOP, '      b.onclick = function(){ avtAntwoord(g.opties[+b.getAttribute("data-avto")], false); };')
    rep(A_INVOER, '        avtAntwoord({goed:goedb}, true);')

    rep(A_SPEL, N_SPEL)
    rep(A_GRAM, N_GRAM)

    # punt 13
    rep(A_VEILIG_PLEK, '''/* v23.92: wat een taalmodel terugstuurt is tekst, geen opmaak. Het ging hier rechtstreeks als
   innerHTML het scherm op, dus stond er per ongeluk opmaakcode in, dan werd die uitgevoerd in
   plaats van getoond. */
function veiligHtml(s){
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
function aiFoutTekst(''')
    rep(A_AI_OK, A_AI_OK.replace('+res.uitleg+', '+veiligHtml(res.uitleg)+'))
    rep(A_AI_FOUT, A_AI_FOUT.replace('+res.uitleg+', '+veiligHtml(res.uitleg)+'))

    src = re.sub(r'var APP_VERSIE = "[^"]+";', 'var APP_VERSIE = "%s";' % NIEUW, src, count=1)
    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
    print("index.html gepatcht naar %s" % NIEUW)
else:
    print("index.html was al gepatcht")

if DOE_VER:
    with io.open(PAD_VER, "w", encoding="utf-8") as f:
        f.write(NIEUW + "\n")
    print("versie.txt op %s" % NIEUW)
else:
    print("versie.txt stond al op %s" % NIEUW)
