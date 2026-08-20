#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.141: je route en je dagles weten van elkaar.

Stefan, 20 aug: "wat ik trouwens nog raar vind zijn de lessen, dat lijkt beetje los te staan van de
grammatica en lessen die worden opgebouwd, hoe verhoudt dit tot elkaar?"

## Wat er aan de hand is

Er lopen drie ladders door de app, en twee ervan kennen elkaar niet.

**1. De lessen (Cursus).** Tien A2-hoofdstukken uit AULA, elk met een thema, een set woorden, zinnen,
toetsjes en een lijst spiekbriefkaarten (`spiek:[...]`). Les 2 gaat open als les 1 open is: een
lineaire leerlijn.

**2. De grammatica ín je dagles.** Die is wél gekoppeld: `lesFlowGramId()` vraagt `huidigeLes()` en
pakt een onderwerp uit de spiekbrief van precies die les. De uitleg van vandaag gaat dus over de les
waar je nu in zit. Dat werkt.

**3. De routes en de Conjugador (Grammatica-tab).** `GRAM_PADEN` en `CONJ_FASES`: een eigen ladder
door de werkwoordstijden, met een eigen begin, eigen stappen en een eigen eindpunt ("gestold").
Die kent de lessen niet en de lessen kennen hem niet. Je kunt drie weken aan de route werken zonder
dat je dagles het merkt, en je kunt tien lessen doen zonder dat de route opschuift.

Dat is wat je voelt. Het is geen bug maar een ontbrekende verbinding, en die is nooit gelegd omdat
de routes (v23.116) veel later kwamen dan de lessen.

## Wat deze ronde doet

De route wordt onderdeel van je dag, zonder hem de verplichte les in te duwen.

`lesFlowWinst()` kiest na je les één ding waar je het meeste wint. De volgorde was: twee keer
dezelfde fout, dan El Corrector, dan een vaardigheid die lang niet aan bod kwam. De route komt daar
tussen, op plek twee:

  1. twee keer dezelfde fout op hetzelfde onderwerp (dat is het meest urgent en dat blijft)
  2. **de volgende stap van je route** (dit is het enige met een eindpunt: er staat "nog 3 stappen")
  3. El Corrector
  4. een vaardigheid die je vier dagen niet deed

Waarom plek twee en niet plek een: een fout die je twee keer maakte is een gat dat nu dicht moet.
Een route is een plan, en een plan kan een dag wachten.

En op Vandaag staat, vanaf dag twee, één regel onder je plan: welke route loopt, welke stap er nu
is, en hoeveel er nog te gaan zijn. Met een knop die er rechtstreeks heen gaat.

## Wat deze ronde NIET doet

De route wordt geen stap in de verplichte les. Dat zou kunnen, maar de routestappen zijn oefeningen
van vijf tot tien minuten in de speeltuin-views, en die hebben geen "door naar de volgende stap van
je les"-knop. Dat is een eigen ronde, en het is geen goed idee om hem half te doen: dan strand je
halverwege je dagles in een spel.

Bewaakt door test/suites/pw-routedag.js.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.141"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = NIEUW not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()


def _num(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or ""))


DOE_VER = _num(huidig_ver) < _num(NIEUW)

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    if not DOE_APP:
        return
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:220])
    src = src.replace(anker, nieuw, n)


# ------------- 1. waar je route staat, als één ding om te lezen

rep(
    '''function lesFlowWinst(){''',
    '''/* ================= DE ROUTE IN JE DAG (v23.141) =================

   Stefan: "de lessen lijken beetje los te staan van de grammatica, hoe verhoudt dit tot elkaar?"

   Er lopen drie ladders door de app. De lessen (Cursus) en de grammatica-stap van je dagles zijn
   wél gekoppeld: lesFlowGramId() vraagt huidigeLes() en pakt een onderwerp uit de spiekbrief van
   precies die les. De routes (GRAM_PADEN, v23.116) en de Conjugador staan er los van: je kunt drie
   weken aan een route werken zonder dat je dagles het merkt.

   Deze functie is de verbinding. Niet door de route de verplichte les in te duwen (de routestappen
   zijn oefeningen van vijf tot tien minuten zonder "door"-knop, dus dan strand je halverwege je
   les), maar door hem te laten zien op de twee momenten waarop je beslist wat je nu doet: onder je
   dagplan, en na je les. */
function routeStand(){
  var p = null, i = -1;
  try { p = gramPadNu(); } catch(e){ p = null; }
  if(!p || !p.stappen) return null;
  try { i = gramPadVolgende(p); } catch(e){ i = -1; }
  if(i < 0) return null;
  var open = 0, j, x;
  for(j = i; j < p.stappen.length; j++){
    try { x = gramPadStap(p, j); } catch(e){ x = null; }
    if(x && x.bestaat && !x.af) open++;
  }
  var s = p.stappen[i];
  return {p:p, i:i, s:s, titel:ct(p.nl, p.en), stap:ct(s.nl, s.en), open:open,
          begonnen: (function(){ try { return gramPadBegonnen(p); } catch(e){ return false; } })()};
}
function routeRegelHtml(){
  var r = routeStand();
  if(!r) return "";
  return "<p class='muted' style='margin:8px 0 0; font-size:.82rem'>"+
    ct("Je route: <b>"+r.titel+"</b>. Nu: "+r.stap+", nog "+r.open+" "+(r.open === 1 ? "stap" : "stappen")+". ",
       "Your route: <b>"+r.titel+"</b>. Now: "+r.stap+", "+r.open+" "+(r.open === 1 ? "step" : "steps")+" to go. ")+
    "<button class='mini' id='btnRouteDag' style='margin-top:4px'>"+
      ct("Naar je route","To your route")+"</button></p>";
}
function routeRegelWire(){
  var b = document.getElementById("btnRouteDag");
  if(!b) return;
  b.onclick = function(){
    var r = routeStand();
    if(r) gramPadGa(r.p, r.i);
  };
}
/* Als voorstel na je les. Eén object in dezelfde vorm als de rest (icon, kop, waarom, knop, doe),
   zodat het door dezelfde lijst en dezelfde knoppen loopt. */
function routeVoorstel(){
  var r = routeStand();
  if(!r) return null;
  return {icon:"\\ud83e\\udded",
    kop:ct("Je route: "+r.stap, "Your route: "+r.stap),
    waarom:ct("Dit is de volgende stap van "+r.titel+". Nog "+r.open+" "+(r.open === 1 ? "stap" : "stappen")+
              " en die tijd staat gestold: dan kun je hem maken zonder erbij na te denken.",
              "This is the next step of "+r.titel+". "+r.open+" "+(r.open === 1 ? "step" : "steps")+
              " to go and that tense is set: then you can produce it without thinking."),
    knop:ct("Volgende stap","Next step"),
    doe:function(){ gramPadGa(r.p, r.i); }};
}

function lesFlowWinst(){''',
)

# ------------- 2. de route als tweede prioriteit na je les

rep(
    '''  var corrKan = true;
  try { corrKan = speelKlaar("corr"); } catch(e){ corrKan = true; }''',
    '''  /* v23.141: de route komt hier, op plek twee. Een fout die je twee keer maakte (hierboven) is een
     gat dat nu dicht moet; een route is een plan en dat kan een dag wachten. Maar hij gaat vóór El
     Corrector en vóór de vaardigheidskeuze, want hij is het enige voorstel met een eindpunt: er
     staat bij hoeveel stappen er nog zijn. */
  var rv = null;
  try { rv = routeVoorstel(); } catch(e){ rv = null; }
  if(rv) return rv;
  var corrKan = true;
  try { corrKan = speelKlaar("corr"); } catch(e){ corrKan = true; }''',
)

# ------------- 3. en op Vandaag, onder je plan

rep(
    '''        : toonPlan ? dagPlanHtml()
                   : "<p class='muted' style='margin:6px 0 0'>"+portieTxt+"</p>")+''',
    '''        : toonPlan ? dagPlanHtml() + routeRegelHtml()   /* v23.141: en waar je route staat */
                   : "<p class='muted' style='margin:6px 0 0'>"+portieTxt+"</p>")+''',
)

rep(
    """  dagBordWire(listEl);""",
    """  dagBordWire(listEl);
  routeRegelWire();   // v23.141: de knop bij de routeregel onder je dagplan""",
)

# ---------------------------------------------------------------- wegschrijven
if DOE_APP:
    src = re.sub(r'var APP_VERSIE = "[^"]+"', 'var APP_VERSIE = "%s"' % NIEUW, src, count=1)
    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
    print("index.html bijgewerkt naar %s" % NIEUW)

if DOE_VER:
    with io.open(PAD_VER, "w", encoding="utf-8") as f:
        f.write(NIEUW + "\n")
    print("versie.txt -> %s" % NIEUW)
