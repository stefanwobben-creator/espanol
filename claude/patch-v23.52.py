#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.52: na je les stuurt de app je niet naar een deur die op slot zit.

Stefan, telefoontest 11 aug, bevinding 4: "als je alles hebt doorlopen, loopt het dood. Je wil dan
zien dat je een spelletje kan doen, dat je Chispa kan voeren, dat je ook lesjes kunt doen."

Nagemeten op een vers A0-profiel, telefoonformaat. Het klaar-scherm heeft wél al alles wat hij
noemt: de tapa-knop voor Chispa, "Nog een les doen", en twee voorstelkaarten. Maar er zaten twee
dingen mis, en het eerste is een echte fout.

## 1. Het eerste voorstel wees naar een gesloten deur

Op dag 1 stelde `lesFlowWinst()` **El Corrector** voor: "10 regels staan op herhaling ... Fouten
zoeken →". Maar `speelKlaar("corr")` is dan `false`: dat spel doet mee vanaf acht vrijgespeelde
zinnen en een vreemde heeft er vijf.

De poort van v23.43 verbergt de tegel in de speeltuin, maar dit voorstel roept `speelNaar("corr")`
rechtstreeks aan. Een tweede deur naar dezelfde gesloten kamer, en precies op het moment dat iemand
voor het eerst besluit of hij doorgaat.

`corrDueHaalbaar()` telt hoeveel regels er op herhaling staan. Dat getal zegt niets over of het spel
kan draaien; daar is `speelKlaar()` voor, en die stond hier niet. Nu wel, en meteen ook bij de
vaardigheidssuggestie eronder.

## 2. En de vaardigheid eronder ook

Het volgende voorstel werd **Escuchar**, en dat spel doet mee vanaf twintig geleerde woorden.
`lesFlowVaardigheidOpen()` keek alleen of je die vaardigheid vandaag al had gedaan, niet of er
materiaal voor is. Eén geval repareren was dus niet genoeg; de regel hoort bij de bron te staan.
Luisteren volgt nu `speelKlaar("audi")`, lezen keek al of er een hoofdstuk open staat, en schrijven
kan altijd (dat werkt met de zinnen van je eigen les). Op dag 1 wordt het voorstel daarmee "Zinnen
vertalen", en dat kan een vreemde met drie woorden echt doen.

## 3. Het tweede voorstel viel net buiten beeld

Gemeten op 390 bij 844:

    LES AFGEROND            top 142   in beeld
    HIER WIN JE HET MEESTE  top 616   in beeld
    OF GEWOON LEUK          top 865   eronder

Eenentwintig pixels. En uitgerekend op dág 1 is die kaart het langst, want dan staat er ook nog "Tot
morgen? Dan komen de woordjes van vandaag precies op tijd terug." Dat is een goede zin, maar hij
duwt het antwoord op "en nu?" van het scherm af.

Die zin verhuist naar onder de knoppen: hij gaat over morgen, dus hij hoeft niet boven de dingen te
staan die over nu gaan. En de twee voorstelkaarten worden één kaart met twee regels. Dat scheelt een
kop, een marge en een kaartrand, en het is ook eerlijker: het zijn geen twee mededelingen maar één
vraag met twee antwoorden. Stefan vroeg om precies dat: "je wil zien dat je een spelletje kan doen,
dat je Chispa kan voeren, dat je ook lesjes kunt doen."

Idempotent.
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.52"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.52: hier stond alleen" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

OUD_CORR = '''  var cd = corrDueHaalbaar();
  if(cd.length >= 3){'''
OUD_TOT = '''    (eersteOoit ? "<p style='margin:8px 0'><b>"+ct("Tot morgen?","See you tomorrow?")+"</b> "+ct("Dan komen de woordjes van vandaag precies op tijd terug: zó blijven ze plakken. Vijf minuutjes, meer niet.","Today's words will come back right on time — that's how they stick. Five minutes, no more.")+"</p>" : "")+'''

if DOE_APP:
    for a in ['var APP_VERSIE = "v23.51";', OUD_CORR, OUD_TOT, 'var v = lesFlowVaardigheidOpen();']:
        if a not in src:
            print("Deze index.html ziet er niet uit zoals verwacht; anker ontbreekt:\n  " + a[:80] +
                  "\n\nEerst bijtrekken, dan pas patchen:\n\n    git pull --rebase\n")
            sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    rep('var APP_VERSIE = "v23.51";', 'var APP_VERSIE = "%s";' % NIEUW)

    # ---------- 1. geen voorstel naar een spel dat dicht staat ----------
    rep(OUD_CORR,
        '''  /* v23.52: hier stond alleen corrDueHaalbaar().length >= 3, en dat telt hoeveel regels er op
     herhaling staan. Dat zegt niets over of het spel kan draaien. Op dag 1 stelde de app hierdoor
     El Corrector voor terwijl speelKlaar("corr") false is (acht vrijgespeelde zinnen nodig, een
     vreemde heeft er vijf): de poort van v23.43 verbergt de tegel wél, maar dit voorstel roept
     speelNaar("corr") rechtstreeks aan. Een tweede deur naar dezelfde gesloten kamer, precies op
     het moment dat iemand besluit of hij doorgaat. */
  var corrKan = true;
  try { corrKan = speelKlaar("corr"); } catch(e){ corrKan = true; }
  var cd = corrKan ? corrDueHaalbaar() : [];
  if(cd.length >= 3){''')

    # ---------- 2. de zin over morgen staat onder de knoppen ----------
    rep(OUD_TOT, '')
    rep('''    "<div class='row'><button class='primary' id='btnLesFlowTerug'>"+ct("Klaar voor vandaag ✓","Done for today ✓")+"</button>"+
    "<button class='ghost' id='btnLesFlowNogEens'>"+ct("Nog een les doen","Do another session")+"</button></div></div>"+''',
        '''    "<div class='row'><button class='primary' id='btnLesFlowTerug'>"+ct("Klaar voor vandaag ✓","Done for today ✓")+"</button>"+
    "<button class='ghost' id='btnLesFlowNogEens'>"+ct("Nog een les doen","Do another session")+"</button></div>"+
    /* v23.52: deze zin stond boven de knoppen, en juist op dag 1 (de enige dag dat hij verschijnt)
       duwde hij daarmee het antwoord op "en nu?" van het scherm af: de tweede voorstelkaart begon op
       865 pixels in een venster van 844. Hij gaat over morgen, dus hij hoeft niet boven de dingen te
       staan die over nu gaan. */
    (eersteOoit ? "<p class='muted' style='margin:10px 0 0'><b>"+ct("Tot morgen?","See you tomorrow?")+"</b> "+ct("Dan komen de woordjes van vandaag precies op tijd terug: zó blijven ze plakken. Vijf minuutjes, meer niet.","Today's words will come back right on time — that's how they stick. Five minutes, no more.")+"</p>" : "")+
    "</div>"+''')

    # ---------- 3. de vaardigheidssuggestie kent de poort ook ----------
    rep('''function lesFlowVaardigheidOpen(){
  var t = today();
  var open = VAARDIGHEDEN.filter(function(v){ return S.lesFlowSpel[v] !== t; });
  if(!open.length) return null;
  if(open.indexOf("lezen") !== -1 && !lesFlowBoekHoofdstuk()){
    open = open.filter(function(v){ return v !== "lezen"; });
    if(!open.length) return null;
  }
  return open[0];
}''',
        '''function lesFlowVaardigheidOpen(){
  var t = today();
  var open = VAARDIGHEDEN.filter(function(v){ return S.lesFlowSpel[v] !== t; });
  if(!open.length) return null;
  if(open.indexOf("lezen") !== -1 && !lesFlowBoekHoofdstuk()){
    open = open.filter(function(v){ return v !== "lezen"; });
    if(!open.length) return null;
  }
  /* v23.52: hier werd alleen gekeken of je die vaardigheid vandaag al had gedaan, niet of er
     materiaal voor is. Op dag 1 stelde de app daardoor Escuchar voor, en dat doet mee vanaf twintig
     geleerde woorden. Lezen keek al of er een hoofdstuk open staat; luisteren volgt nu dezelfde
     poort als het spel. Schrijven blijft altijd kunnen: dat werkt met de zinnen van je eigen les. */
  open = open.filter(function(v){
    if(v !== "luisteren") return true;
    try { return speelKlaar("audi"); } catch(e){ return true; }
  });
  if(!open.length) return null;
  return open[0];
}''')

    # ---------- 4. één kaart in plaats van twee ----------
    rep(r'''function lesFlowVoorstelHtml(v, i){
  return "<div class='card' style='margin-top:10px'>" +
    "<span class='kicker'>" + (i === 0 ? ct("Hier win je het meeste", "This is where you gain most")
                                       : ct("Of gewoon leuk", "Or just fun")) + "</span>" +
    "<p style='margin:4px 0 2px; font-size:1.05rem'><b>" + v.icon + " " + v.kop + "</b></p>" +
    "<p class='muted' style='margin:0 0 10px; font-size:.9rem'>" + v.waarom + "</p>" +
    "<button class='ghost' data-voorstel='" + i + "'>" + v.knop + " \u2192</button></div>";
}''',
        r'''/* v23.52: dit waren twee losse kaarten, elk met een eigen kop, en de tweede begon op 859 pixels in
   een venster van 844. Precies het antwoord op "en nu?" viel dus van het scherm. Het zijn ook geen
   twee mededelingen maar één vraag met twee antwoorden, dus staan ze nu in één kaart. */
function lesFlowVoorstellenHtml(vs){
  if(!vs.length) return "";
  return "<div class='card' style='margin-top:10px'><span class='kicker'>" +
    ct("En nu?", "What now?") + "</span>" +
    vs.map(function(v, i){
      return "<div style='margin:" + (i ? "14px" : "4px") + " 0 0'>" +
        "<p style='margin:0 0 2px; font-size:1.05rem'><b>" + v.icon + " " + v.kop + "</b>" +
        "<span class='muted' style='font-size:.8rem'> \u00b7 " +
          (i === 0 ? ct("hier win je het meeste", "this is where you gain most")
                   : ct("of gewoon leuk", "or just fun")) + "</span></p>" +
        "<p class='muted' style='margin:0 0 8px; font-size:.9rem'>" + v.waarom + "</p>" +
        "<button class='ghost' data-voorstel='" + i + "'>" + v.knop + " \u2192</button></div>";
    }).join("") + "</div>";
}''')
    rep('    voorstellen.map(lesFlowVoorstelHtml).join("")+', '    lesFlowVoorstellenHtml(voorstellen)+')

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
