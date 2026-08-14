#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.97: twee gratis-punten-lekken, een knop die van naam veranderde, en twee dingen die je niet zag
(punt 17, 18, 19, 21 en 22).

## Punt 17: elke uitgeschakelde knop heette "B1 · binnenkort"

`applySignupLang()` sloot af met:

    document.querySelectorAll("#tab-profiel .row button[disabled]").forEach(function(b){ b.textContent = d.b1; });

Alles wat op dat moment toevallig uitgeschakeld was, kreeg die tekst. `btnSyncLogin` staat tijdens het
synchroniseren op disabled, dus daar stond dan ineens "B1 · binnenkort" op je knop. Ziet eruit alsof
de app kapot is, precies op het scherm waar iemand voor het eerst iets probeert.

De knop heeft nu een id en wordt daarop aangesproken. De knop zelf blijft: zie de kop van v23.47 en
`pw-helling.js`, waar staat dat het grijze B1 er met opzet is, zodat het niveauvoorstel leest als een
voorstel en niet als een uitspraak.

## Punt 18: de rondleiding deelde onbeperkt punten uit

In de rondleiding zit één oefenvraag, en die gaf punten, confetti en een toast. Elke keer. Je kunt de
rondleiding opnieuw openen vanuit de voettekst, dus je dagdoel was te halen zonder ooit iets te leren.

Nu telt hij één keer. Het woordje gaat nog steeds gewoon je herhaalsysteem in, ook bij een tweede
rondje: dat is geen beloning maar boekhouding, en die mag kloppen.

## Punt 19: hetzelfde bij een foutloos toetsje

Twee tapa's per foutloze ronde, met "Opnieuw" er direct onder. Chispa voeren werd daarmee gratis, en
een beloning die gratis is, is geen beloning meer. Nu één keer per toetsje per dag. Morgen weer.

## Punt 21: aanmoedigingen kwamen te laat

De krabbels werden één keer per sessie opgehaald (`dagKrabGehaald`) en daarna nooit meer. Wie 's
ochtends de app opende en 's middags een schouderklopje kreeg, zag dat pas de volgende dag. Voor het
enige sociale dat de app heeft is dat fataal: een reactie die een dag te laat komt, is geen reactie.

Nu wordt er opnieuw opgehaald zodra er meer dan tien minuten voorbij zijn. Niet elke keer: dat zou een
verzoek per schermwissel betekenen.

## Punt 22: "lees de spiekbrief" zonder spiekbrief

Onder een matig toetsje stond de opdracht om de spiekbrief terug te lezen, en er was geen knop
daarheen. Een opdracht die je zelf moet uitvoeren, doet niemand. Er staat nu een knop naast
"Opnieuw", en die gaat naar de kaart die bij dit toetsje hoort.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.97"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.97" not in src
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


# ---------------------------------------------------------------- punt 17
A_B1_HTML = '''        <button class="ghost" disabled style="opacity:.45">B1 · binnenkort</button>'''
N_B1_HTML = '''        <button class="ghost" id="btnB1Straks" disabled style="opacity:.45">B1 · binnenkort</button>'''

A_B1_JS = '''  // B1-knop (heeft geen data-lvl)
  document.querySelectorAll("#tab-profiel .row button[disabled]").forEach(function(b){ b.textContent = d.b1; });'''
N_B1_JS = '''  /* v23.97: hier stond een selector op élke uitgeschakelde knop in dit tabblad. btnSyncLogin staat
     tijdens het synchroniseren op disabled, en dan veranderde die knop ineens in "B1 · binnenkort".
     Dat ziet eruit alsof de app stuk is, op precies het scherm waar iemand voor het eerst iets
     probeert. De knop heeft nu een eigen id. */
  var b1 = document.getElementById("btnB1Straks");
  if(b1) b1.textContent = d.b1;'''

# ---------------------------------------------------------------- punt 18
A_TOUR = '''        addXP(goed ? 2 : 1);
        confetti(goed ? ["🎉","⭐️"] : ["💛"], goed ? 14 : 8);'''
N_TOUR = '''        /* v23.97: dit gaf punten, confetti en een toast, elke keer. De rondleiding is opnieuw te
           openen vanuit de voettekst, dus je dagdoel was te halen zonder iets te leren. Nu telt hij
           één keer. Het woordje gaat hierboven nog wel gewoon je herhaalsysteem in, ook bij een
           tweede rondje: dat is geen beloning maar boekhouding. */
        var eersteRonde = !S.tourBeloond;
        if(eersteRonde){ S.tourBeloond = 1; addXP(goed ? 2 : 1); persist(); }
        confetti(goed ? ["🎉","⭐️"] : ["💛"], goed ? 14 : 8);'''

# ---------------------------------------------------------------- punt 19
A_TAPA = '''    if(pct === 1){ S.tapas = (S.tapas||0) + 2; persist(); confetti(["⭐️","🌮","🎉"], 20); }'''
N_TAPA = '''    /* v23.97: dit gaf twee tapa's per foutloze ronde, met "Opnieuw" er direct onder. Chispa voeren
       werd daarmee gratis, en een beloning die gratis is telt niet meer. Eén keer per toetsje per
       dag; de confetti blijft altijd, want die kost niets en die is de bedoeling. */
    if(pct === 1){
      S.tapaToets = S.tapaToets || {};
      if(S.tapaToets[qz.id] !== today()){
        S.tapaToets[qz.id] = today();
        S.tapas = (S.tapas||0) + 2;
        persist();
      }
      confetti(["⭐️","🌮","🎉"], 20);
    }'''

# ---------------------------------------------------------------- punt 21
A_KRAB = '''  // krabbels komen van de server; één keer per sessie ophalen en dan alleen het nieuwsblok verversen
  if(!dagKrabGehaald && !famCache && typeof api === "function"){
    dagKrabGehaald = true;'''
N_KRAB = '''  /* v23.97: hier stond "één keer per sessie ophalen". Wie 's ochtends de app opende en 's middags
     een schouderklopje kreeg, zag dat pas de volgende dag. Voor het enige sociale dat de app heeft is
     dat fataal: een reactie die een dag te laat komt is geen reactie.
     Nu opnieuw ophalen zodra er tien minuten voorbij zijn. Niet bij elke schermwissel, want dan wordt
     het een verzoek per tik. */
  var krabOud = !dagKrabGehaald || (Date.now() - dagKrabGehaald) > 10 * 60 * 1000;
  if(krabOud && typeof api === "function"){
    dagKrabGehaald = Date.now();'''

A_KRAB_VAR = '''var dagKrabGehaald = false;'''
N_KRAB_VAR = '''var dagKrabGehaald = 0;   // v23.97: het tijdstip van de laatste ophaal, niet meer een ja/nee'''

# ---------------------------------------------------------------- punt 22
A_KNOPPEN = '''    el.innerHTML = "<span class='kicker'>"+quizTitel(qz)+"</span>"+
      "<p class='big'>"+st.score+" / "+gesteld+"</p><p>"+msg+"</p>"+
      "<div class='row'><button class='primary' id='btnRetry'>"+ct("Opnieuw","Again")+"</button>"+
      "<button class='ghost' id='btnMenu'>"+ct("Terug naar toetsjes","Back to quizzes")+"</button></div>";
    document.getElementById("btnRetry").onclick = function(){ startQuiz(qz.id); };
    document.getElementById("btnMenu").onclick = closeQuiz;'''
N_KNOPPEN = '''    /* v23.97: onder een matig toetsje stond "lees de spiekbrief en probeer opnieuw", en er was geen
       knop daarheen. Een opdracht die je zelf moet uitvoeren doet niemand, dus stond die zin er voor
       niets. Nu een knop ernaast, alleen als er ook echt een kaart bij dit toetsje hoort. */
    var heeftSpiek = !!(qz.spiek && qz.spiek.length);
    el.innerHTML = "<span class='kicker'>"+quizTitel(qz)+"</span>"+
      "<p class='big'>"+st.score+" / "+gesteld+"</p><p>"+msg+"</p>"+
      "<div class='row'><button class='primary' id='btnRetry'>"+ct("Opnieuw","Again")+"</button>"+
      (heeftSpiek ? "<button class='ghost' id='btnNaarSpiek'>"+ct("Spiekbrief","Cheat sheet")+"</button>" : "")+
      "<button class='ghost' id='btnMenu'>"+ct("Terug naar toetsjes","Back to quizzes")+"</button></div>";
    document.getElementById("btnRetry").onclick = function(){ startQuiz(qz.id); };
    var bns = document.getElementById("btnNaarSpiek");
    if(bns) bns.onclick = function(){ closeQuiz(); show("spiekbrief"); };
    document.getElementById("btnMenu").onclick = closeQuiz;'''

if DOE_APP:
    ontbreekt = [n for n, a in (
        ("de B1-knop", A_B1_HTML), ("de hernoemer", A_B1_JS), ("de rondleidingsvraag", A_TOUR),
        ("de tapa's van een foutloos toetsje", A_TAPA), ("het ophalen van krabbels", A_KRAB),
        ("dagKrabGehaald", A_KRAB_VAR), ("de knoppen onder de toetsuitslag", A_KNOPPEN)) if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht; %s staat er niet zoals verwacht.\n"
              "Deze patch bouwt op v23.96. Eerst bijtrekken:\n\n    git pull --rebase\n" % ", ".join(ontbreekt))
        sys.exit(1)

    rep(A_B1_HTML, N_B1_HTML)
    rep(A_B1_JS, N_B1_JS)
    rep(A_TOUR, N_TOUR)
    rep(A_TAPA, N_TAPA)
    rep(A_KRAB_VAR, N_KRAB_VAR)
    rep(A_KRAB, N_KRAB)
    rep(A_KNOPPEN, N_KNOPPEN)

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
