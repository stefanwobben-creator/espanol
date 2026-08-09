#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.22: de betekenis komt bij het woord te staan, en de luistervragen verklappen geen geslacht meer.

Twee dingen die Stefan tijdens het lezen tegenkwam.

1. De betekenis stond onderaan de kaart. Bij een hoofdstuk van driehonderd woorden betekent dat
   scrollen naar beneden, lezen, en dan de zin terugzoeken. Dan is de hulp duurder dan het probleem
   en lees je alsnog met DeepL ernaast. Hij staat nu als tooltip vlak bij het woord dat je aantikte,
   boven of onder de regel, net wat past.

2. De luistervragen vroegen "Hoeveel betaalt zij?" en "Wat wil hij drinken?", terwijl je aan twee
   stemmen niet kunt horen wie de klant is en wie de verkoper. Dan toetst de vraag iets wat de
   opname niet zegt, en een fout antwoord betekent niet dat je het niet verstond. De vragen vragen nu
   naar wat er gebeurt in plaats van naar wie het doet.

Idempotent.
"""
import io, sys, os

PAD = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol/index.html")

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

if "leesTooltipPlaats" in src:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:160])
    src = src.replace(anker, nieuw, n)


# ---------------------------------------------------------------- 1. de tooltip
rep(
    """  .leesUit{position:sticky; bottom:0; background:var(--card); border-top:1px solid var(--border);
           padding:10px 2px 4px; margin-top:10px;}
  .leesUit .es{font-weight:700;}
  .leesUit p{margin:2px 0;}
""",
    """  /* v23.22: de betekenis hoort bij het woord en niet onder de bladzijde. Onderaan betekent scrollen,
     en na het scrollen moet je je zin terugzoeken; dan is de hulp duurder dan het opzoeken zelf. */
  .leesUit{position:absolute; z-index:30; max-width:250px; background:var(--card);
           border:1px solid var(--border); border-radius:10px; padding:8px 10px;
           box-shadow:0 6px 20px rgba(45,42,38,.16); font-size:.92rem; line-height:1.3;}
  .leesUit.weg{display:none;}
  .leesUit .es{font-weight:700;}
  .leesUit p{margin:2px 0;}
""")

# ---------------------------------------------------------------- 2. plaatsen bij het woord
rep(
    """function leesToon(woord){
  var el = document.getElementById("leesUitleg");
  if(!el) return;""",
    """/* Onder het woord als het past, anders erboven, en altijd binnen de kaart. Gerekend met
   getBoundingClientRect en niet met offsetTop, want de alinea's zitten in elementen met hun eigen
   positie en dan klopt offsetTop niet meer zodra er ergens iets verandert aan de opmaak. */
function leesTooltipPlaats(el, span){
  var kaart = document.getElementById("lezenCard");
  if(!kaart) return;
  var rk = kaart.getBoundingClientRect(), rs = span.getBoundingClientRect();
  el.classList.remove("weg");
  el.style.left = "0px";
  el.style.top = "0px";
  var breedte = el.offsetWidth, hoogte = el.offsetHeight;
  var links = rs.left - rk.left + (rs.width / 2) - (breedte / 2);
  links = Math.max(6, Math.min(links, kaart.clientWidth - breedte - 6));
  var onder = rs.bottom - rk.top + 8;
  var boven = rs.top - rk.top - hoogte - 8;
  // past hij nog op het scherm als hij eronder staat? Zo niet, dan erboven.
  var plaatsBoven = (rs.bottom + hoogte + 12 > window.innerHeight) && boven > 0;
  el.style.left = Math.round(links) + "px";
  el.style.top = Math.round(plaatsBoven ? boven : onder) + "px";
}
function leesVerberg(){
  var el = document.getElementById("leesUitleg");
  if(el) el.classList.add("weg");
  var kaart = document.getElementById("lezenCard");
  var aan = kaart && kaart.querySelector(".lw.aan");
  if(aan) aan.classList.remove("aan");
}
function leesToon(woord, span){
  var el = document.getElementById("leesUitleg");
  if(!el) return;""")

rep(
    """  if(!b){
    el.innerHTML = "<p><span class='es'>"+woord+"</span></p>"+
      "<p class='muted' style='font-size:.85rem'>"+
        ct("Dit woord staat niet in het woordenboek. Het is genoteerd, zodat het er een keer bij komt.",
           "This word is not in the dictionary. It has been noted, so it can be added later.")+"</p>";
    return;
  }""",
    """  if(!b){
    el.innerHTML = "<p><span class='es'>"+woord+"</span></p>"+
      "<p class='muted' style='font-size:.85rem'>"+
        ct("Staat niet in het woordenboek. Genoteerd.","Not in the dictionary. Noted.")+"</p>";
    if(span) leesTooltipPlaats(el, span);
    return;
  }""")

rep(
    """      extra+"</p>"+
    "<p>"+b.nl+"</p>";
}""",
    """      extra+"</p>"+
    "<p>"+b.nl+"</p>";
  if(span) leesTooltipPlaats(el, span);
}""")

# ---------------------------------------------------------------- 3. de kaart en de klik
rep(
    """    "<div class='leesUit' id='leesUitleg'><p class='muted' style='font-size:.85rem'>"+
      ct("Tik op een woord dat je niet kent, dan staat de betekenis hier.",
         "Tap a word you do not know and its meaning appears here.")+"</p></div>"+""",
    """    "<p class='muted' style='font-size:.82rem; margin:10px 0 0'>"+
      ct("Tik op een woord dat je niet kent.","Tap a word you do not know.")+"</p>"+
    "<div class='leesUit weg' id='leesUitleg'></div>"+""")

rep(
    """  el.onclick = function(ev){
    var t = ev.target;
    if(!t || !t.classList || !t.classList.contains("lw")) return;
    var vorige = el.querySelector(".lw.aan");
    if(vorige) vorige.classList.remove("aan");
    t.classList.add("aan");
    leesToon(t.getAttribute("data-lw"));
  };""",
    """  el.style.position = "relative";
  el.onclick = function(ev){
    var t = ev.target;
    // ergens anders tikken sluit de tooltip: dat is de gebaarloze manier om hem weg te krijgen
    if(!t || !t.classList || !t.classList.contains("lw")){ leesVerberg(); return; }
    var vorige = el.querySelector(".lw.aan");
    if(vorige === t){ leesVerberg(); return; }          // nog eens op hetzelfde woord sluit hem ook
    if(vorige) vorige.classList.remove("aan");
    t.classList.add("aan");
    leesToon(t.getAttribute("data-lw"), t);
  };""")

# ---------------------------------------------------------------- 4. de luistervragen zonder geslacht
VRAGEN = [
    ('q:"Hoeveel betaalt ze uiteindelijk?", qEn:"How much does she end up paying?"',
     'q:"Hoeveel wordt er uiteindelijk betaald?", qEn:"How much is paid in the end?"'),
    ('q:"Hoe wil ze betalen?", qEn:"How does she want to pay?"',
     'q:"Hoe wordt er betaald?", qEn:"How is the payment made?"'),
    ('optsEn:["By card","In cash","Later","She doesn\'t pay"]',
     'optsEn:["By card","In cash","Later","No payment"]'),
    ('opts:["Met kaart","Contant","Later","Ze betaalt niet"]',
     'opts:["Met kaart","Contant","Later","Er wordt niet betaald"]'),
    ('q:"Wat wil hij drinken?", qEn:"What does he want to drink?"',
     'q:"Wat wordt er te drinken besteld?", qEn:"What drink is ordered?"'),
    ('q:"Neemt hij een hoofdgerecht?", qEn:"Is he having a main course?"',
     'q:"Wordt er een hoofdgerecht besteld?", qEn:"Is a main course ordered?"'),
    ('opts:["Nee, hij heeft weinig honger","Ja, hij neemt de vis van de dag"',
     'opts:["Nee, weinig honger","Ja, de vis van de dag"'),
    ('q:"Waar heeft ze last van?", qEn:"What\'s bothering her?"',
     'q:"Wat is de klacht?", qEn:"What is the complaint?"'),
    ('q:"Slikt ze al iets?", qEn:"Is she taking anything yet?"',
     'q:"Wordt er al iets ingenomen?", qEn:"Is anything being taken yet?"'),
    ('opts:["Nee, nog niet","Ja, elke dag","Ja, alleen \'s nachts","Dat zegt ze niet',
     'opts:["Nee, nog niet","Ja, elke dag","Ja, alleen \'s nachts","Dat wordt niet gezegd'),
    ('q:"Hoe lang woont ze er al?", qEn:"How long has she lived there?"',
     'q:"Hoe lang woont Marta er al?", qEn:"How long has Marta lived there?"'),
]
gedaan = 0
for oud, nieuw in VRAGEN:
    if src.count(oud) == 1:
        src = src.replace(oud, nieuw, 1)
        gedaan += 1
    else:
        print("  overgeslagen (niet gevonden of niet uniek):", oud[:60])
print("  luistervragen aangepast:", gedaan, "van", len(VRAGEN))

rep('var APP_VERSIE = "v23.21";', 'var APP_VERSIE = "v23.22";')

with io.open(PAD, "w", encoding="utf-8") as f:
    f.write(src)
print("v23.22 toegepast op", PAD)
