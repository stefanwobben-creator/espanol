#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.54: het laadscherm, en de kop die niet meer om een naam vraagt die er nog niet is.

claude/lancering.md, punt 2: "De eerste indruk duurt te lang." Dat stond er als schatting van vijf
tot acht seconden wit scherm, en op 11 augustus is het nagemeten:

    verbinding                    eerste pixels    eerste knop die werkt
    geen rem                          76 ms                0,4 s
    4G (9 Mbit, 85 ms, 2x cpu)       184 ms                2,9 s
    traag 4G (1,6 Mbit, 300 ms)      724 ms               12,8 s

## Wat er nu op dat scherm staat, en dat is erger dan wit

Vandaag opnieuw gemeten, nu met de vraag wat de bezoeker in dat gat ziet. Traag 4G, 390 bij 844,
cpu vier keer geremd:

      964 ms   "¡Vamos …! Chispa ↑"
    13626 ms   het proefscherm verschijnt

Twaalf en een halve seconde lang staat er dus een kop met drie puntjes waar een naam hoort, en een
Chispa-balk. Verder niets. lancering.md zei dat het aanmeldscherm er na 0,7 seconde staat "mét de
naamvelden en de niveauknoppen", en dat klopt niet: `<section id="tab-profiel">` heeft `class=hidden`
in de statische HTML en wordt pas door het script zichtbaar gemaakt.

Dat is niet "de app laadt langzaam". Dat is een pagina die eruitziet alsof hij klaar is en niets
doet. Je tikt, er gebeurt niets, en je concludeert dat het stuk is. Wit had eerlijker geweest.

## Wat deze versie doet

Een laadscherm dat in de statische HTML staat, met zijn stijl in het bestaande <style>-blok, dus
zonder één extra verzoek. Gemeten: het staat er na 964 ms, tegelijk met de rest van de statische
HTML, en het dekt precies het gat af.

  - Een onbepaalde balk, geen percentage. Er ís geen voortgang te melden: het is één script dat
    ofwel bezig is ofwel klaar. Een balk die naar 80% kruipt en daar blijft hangen is een leugen
    met een animatie eromheen.
  - Na zes seconden komt er een regel bij: "Dit duurt alleen de eerste keer." Die staat er niet
    meteen, want bij een snelle verbinding is het scherm dan al weg en zou hij alleen maar
    aankondigen dat er een probleem is dat er niet is.
  - Weg zodra boot() of renderProfileScreen() klaar is, met een korte fade zodat het niet knippert.

## De drie failsafes, en waarom ze er zijn

Een laadscherm is een gordijn dat je voor je eigen app hangt. Blijft het hangen, dan heb je de app
niet trager gemaakt maar onbruikbaar. Dus:

  1. `window.onerror` haalt het gordijn weg. Een scriptfout betekende tot nu toe een half werkende
     app; met een gordijn ervoor zou het een dode app worden.
  2. Een harde noodrem na 30 seconden, ook als er geen fout is opgetreden.
  3. Het minitscript dat dit regelt staat direct ónder het laadscherm in de HTML en is losgekoppeld
     van het grote script. Komt dat grote script er nooit doorheen, dan gaat het gordijn na 30
     seconden alsnog open en zie je tenminste wat er wél is.

## En de kop

lancering.md, punt 5: "De titel toont ¡Vamos …! met een naam die er nog niet is." Dat waren drie
puntjes als plaatshouder, en een vreemde leest daar geen plaatshouder in maar een fout. Het is nu
gewoon "¡Vamos!" tot je een naam hebt, en "¡Vamos Stefan!" daarna. De spatie zit sinds deze versie
aan de naam vast in plaats van in de HTML, anders had je "¡Vamos !" gekregen.

## Wat dit niet oplost

De 2,3 MB zelf. De content zit in het bestand en dat blijft zo tot de eerste grote verbouwing na de
lancering (content per niveau laden). Deze versie maakt de wachttijd niet korter, alleen eerlijk.
Dat is het verschil tussen iemand die wacht en iemand die wegklikt.

Idempotent.
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.54"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = 'id="laadScherm"' not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_STYLE_EIND = '''  details.gwdiep .inner{font-size:.92rem; line-height:1.5; padding-top:8px;}
</style>'''

A_BODY = '''<body>
<div class="wrap">
  <header>
    <h1>¡Vamos <span id="userName" class="naamknop" title="Profiel & groepen">…</span>!</h1>'''

A_UN_LEEG = '''  document.getElementById("userName").textContent = "…";'''
A_UN_NAAM = '''  document.getElementById("userName").textContent = p.name;'''
A_SLOT = '''  if(profiles.active && activeProfile()){ boot(); } else { renderProfileScreen(); }
})();'''

if DOE_APP:
    ANKERS = ['var APP_VERSIE = "v23.53";', A_STYLE_EIND, A_BODY, A_UN_LEEG, A_UN_NAAM, A_SLOT]
    ontbreekt = [a for a in ANKERS if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht. Ontbrekende ankers:\n  " +
              "\n  ".join(a[:90].replace("\n", " / ") for a in ontbreekt) +
              "\n\nDeze patch bouwt op v23.53. Eerst bijtrekken:\n\n    git pull --rebase\n")
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    rep('var APP_VERSIE = "v23.53";', 'var APP_VERSIE = "%s";' % NIEUW)

    # ---------- 1. de stijl, in het bestaande blok zodat er geen verzoek bij komt ----------
    rep(A_STYLE_EIND, '''  details.gwdiep .inner{font-size:.92rem; line-height:1.5; padding-top:8px;}
  /* --- laadscherm v23.54 ---
     Gemeten op traag 4G (1,6 Mbit, 300 ms rtt, cpu 4x geremd): de statische HTML staat er na 964 ms,
     het script is pas na 13,6 seconden klaar. In dat gat zag je "¡Vamos …! Chispa ↑" en verder
     niets: een pagina die eruitziet alsof hij klaar is en niet reageert. Deze stijl staat in het
     bestaande blok en niet in een eigen bestand, want een extra verzoek op zo'n verbinding kost
     precies de tijd die we hier proberen te winnen. */
  #laadScherm{position:fixed; inset:0; z-index:9999; background:var(--bg); display:flex;
              align-items:center; justify-content:center; padding:24px;
              transition:opacity .22s ease;}
  #laadScherm .laadbin{width:100%; max-width:320px; text-align:center;}
  #laadScherm .laadlogo{font-size:1.9rem; font-weight:800; color:var(--ink); margin:0 0 18px;}
  /* een onbepaalde balk en geen percentage: er is niets te melden dat waar is. Het is één script
     dat bezig is of klaar. Een balk die naar 80% kruipt en daar blijft hangen is een leugen met
     een animatie eromheen. */
  #laadScherm .laadbaan{height:6px; border-radius:3px; background:var(--border); overflow:hidden;}
  #laadScherm .laadloop{height:100%; width:40%; border-radius:3px; background:var(--accent);
                        animation:laadloop 1.15s ease-in-out infinite;}
  @keyframes laadloop{0%{transform:translateX(-110%)} 100%{transform:translateX(310%)}}
  #laadScherm p{margin:14px 0 0; font-size:.95rem; color:var(--muted); line-height:1.45;}
  #laadScherm #laadTxt2{margin-top:6px; font-size:.85rem;}
  @media (prefers-reduced-motion: reduce){
    #laadScherm .laadloop{animation:none; width:100%; opacity:.5;}
  }
</style>''')

    # ---------- 2. het scherm zelf, plus de drie failsafes ----------
    rep(A_BODY, '''<body>
<!-- v23.54: het laadscherm staat vóór alles en in de statische HTML, zodat het meekomt met de
     eerste 964 ms in plaats van met het script van 2,3 MB. Het maakt de wachttijd niet korter;
     het maakt hem eerlijk. -->
<div id="laadScherm" role="status" aria-live="polite">
  <div class="laadbin">
    <div class="laadlogo">¡Vamos!</div>
    <div class="laadbaan"><div class="laadloop"></div></div>
    <p id="laadTxt">Even geduld, we zetten je Spaans klaar.</p>
    <p id="laadTxt2" class="hidden">Dit duurt alleen de eerste keer.</p>
  </div>
</div>
<script>
/* v23.54. Een laadscherm is een gordijn dat je voor je eigen app hangt: blijft het hangen, dan heb
   je de app niet traag gemaakt maar onbruikbaar. Dit stukje staat daarom los van het grote script
   en direct onder het scherm zelf, en het heeft drie noodremmen. */
(function(){
  var el = document.getElementById("laadScherm");
  if(!el) return;
  var weg = function(){
    if(!el || !el.parentNode) return;
    var d = el; el = null;
    d.style.opacity = "0";
    setTimeout(function(){ if(d && d.parentNode) d.parentNode.removeChild(d); }, 240);
  };
  window.__laadWeg = weg;
  /* De regel over "de eerste keer" komt pas na zes seconden. Meteen zou hij een probleem
     aankondigen dat er op een snelle verbinding niet is: daar is dit scherm al weg. */
  setTimeout(function(){
    var b = document.getElementById("laadTxt2");
    if(b) b.classList.remove("hidden");
  }, 6000);
  /* 1. een scriptfout betekende tot nu toe een half werkende app; met een gordijn ervoor zou het
        een dode app worden. */
  window.addEventListener("error", function(){ setTimeout(weg, 400); });
  /* 2. en een noodrem voor het geval het grote script er nooit doorheen komt. */
  setTimeout(weg, 30000);
})();
</script>
<div class="wrap">
  <header>
    <!-- v23.54: hier stond "¡Vamos …!" met drie puntjes als plaatshouder voor een naam die er nog
         niet is. Een vreemde leest daar geen plaatshouder in maar een fout. De spatie zit nu aan
         de naam vast in plaats van in de HTML, anders staat er "¡Vamos !". -->
    <h1>¡Vamos<span id="userName" class="naamknop" title="Profiel &amp; groepen"></span>!</h1>''')

    rep(A_UN_LEEG, '  document.getElementById("userName").textContent = "";')
    rep(A_UN_NAAM, '  document.getElementById("userName").textContent = p.name ? " " + p.name : "";')

    # ---------- 3. het gordijn gaat open als er iets achter staat ----------
    rep(A_SLOT, '''  if(profiles.active && activeProfile()){ boot(); } else { renderProfileScreen(); }
  /* v23.54: derde noodrem is dat dit de normale weg is. Pas hier staat er echt iets achter het
     gordijn: boot() heeft de knoppen aangesloten of renderProfileScreen() heeft het aanmeldscherm
     getekend. Alles daarvoor weghalen zou het probleem terugbrengen dat we net hebben opgelost. */
  try { if(window.__laadWeg) window.__laadWeg(); } catch(e){}
})();''')

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
