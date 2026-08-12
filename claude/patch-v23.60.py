#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.60: één knop, één rode knop, en je ziet altijd waar je bent.

Stefan, 12 aug, drie ontwerpregels in plaats van drie bugmeldingen:

  1. "er moet altijd een knop zijn die controleert en dan automatisch doorgaat naar volgende"
  2. "dat je altijd in beeld moet zien waar je bent en hoeveel je nog moet"
  3. "een toggle bijv makkelijk of moeilijk zou een toggle ofzo moeten zijn"
  4. "in het 1 zin na Check zie je drie rode buttons als call to action. Dat is vragen om
     moeilijkheden"

Punt 4 is te tellen, en het klopt. Op de live versie stond na Controleer:

    [🧩 TEGELS]  [Moeilijk]        <- de actieve moduskeuze rendert als .primary, dus rood
    [ CONTROLEER ]  [Wissen]       <- rood
    ¡Perfecto! ✓
    [ VOLGENDE ZIN → ]             <- rood

Drie rode knoppen, en twee ervan doen op dat moment niets. v23.57 haalde de invoer weg, en deze
versie haalt de laatste weg: de moduskeuze is geen call to action, dus hij hoort niet in de kleur
van een call to action.

## 1. Eén knop, die controleert en doorgaat

De knop staat nu altijd op dezelfde plek, direct onder je antwoord, en verandert mee:

    vóór    [ Controleer ]
    ná      [ Volgende zin → ]

En bij een goed antwoord gaat hij vanzelf door na 1,9 seconde. Twee tikken voor één handeling is
een tik te veel; dat is Stefans punt en hij heeft gelijk.

Bij een fout antwoord gebeurt dat niet. Dan staat het juiste antwoord er net, en dat is precies het
moment waarop je even moet kunnen kijken. Automatisch doorgaan zou dan de correctie wegvegen.

Wie de zin nog wil horen tikt de luisterknop, en dan stopt de doorloop meteen. Datzelfde geldt voor
"Meer uitleg". Dat was het bezwaar tegen automatisch doorgaan in v23.51 ("dan pak je het moment af
waarop je de zin nog kunt horen"), en zo blijft dat moment bestaan voor wie het wil zonder dat
iedereen erop moet wachten.

## 2. Waar je bent, zonder te zoeken

Boven de zin stond alleen "ZIN 1/3" in het grijze kopregeltje. Daar staat nu een balkje bij, in
dezelfde vorm als de balk van de helling. Op één regel: hoeveel je hebt gedaan, hoeveel er nog zijn,
en hoe ver dat is.

## 3. De moduskeuze is een schakelaar, geen knoppenrij

Twee losse knoppen waarvan de actieve rood is, leest als twee acties waarvan er één aanstaat. Het is
één instelling met twee standen. Dus is het nu één pil met twee vakjes, in de zachte accentkleur in
plaats van in de knalkleur, en kleiner. Dezelfde functie, en niet langer de derde rode knop.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.60"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "function zinDoorloop" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_STIJL = '''  details.gwdiep .inner{font-size:.92rem; line-height:1.5; padding-top:8px;}'''

A_MODUS = '''  return "<div class='row' id='"+rowId+"' style='gap:6px; margin:2px 0 10px'>"+
    (metTegels
      ? "<button type='button' class='"+(modus==="tegels"?"primary":"ghost")+" modus-toets' data-m='tegels' style='padding:6px 13px; font-size:0.85rem'>🧩 "+ct("Tegels","Tiles")+"</button>"
      : "<button type='button' class='"+(modus==="makkelijk"?"primary":"ghost")+" modus-toets' data-m='makkelijk' style='padding:6px 13px; font-size:0.85rem'>🟢 "+ct("Makkelijk","Easy")+"</button>")+
    "<button type='button' class='"+(modus==="moeilijk"?"primary":"ghost")+" modus-toets' data-m='moeilijk' style='padding:6px 13px; font-size:0.85rem'>🔴 "+ct("Moeilijk","Hard")+"</button>"+
    "</div>";'''

A_KICKER = '''    "<span class='kicker'>"+(scopeLesson?"Les "+scopeLesson.num+" · ":"")+(inFlowVertalen ? ct("Zin ","Sentence ")+((lesFlow.vertalenTotaal||5)-lesFlow.vertalenTeGaan+1)+"/"+(lesFlow.vertalenTotaal||5) : ct("Vertalen · niveau ","Translate · level ")+s.lvl+" · "+doneCount+"/"+allowIds.length+ct(" gehaald"," done"))+"</span>"+'''

A_WIRE = '''  var br = document.getElementById("btnRetry");
  if(br) br.onclick = function(){ renderSentence(false); };'''

if DOE_APP:
    ontbreekt = [a for a in [A_STIJL, A_MODUS, A_KICKER, A_WIRE] if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht. Ontbrekende ankers:\n  " +
              "\n  ".join(a[:100].replace("\n", " / ") for a in ontbreekt) +
              "\n\nEerst bijtrekken:\n\n    git pull --rebase\n")
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    # ---------- 1. de stijl van de schakelaar en van de doorloopbalk ----------
    rep(A_STIJL, '''  details.gwdiep .inner{font-size:.92rem; line-height:1.5; padding-top:8px;}
  /* --- schakelaar v23.60 ---
     Stefan: "een toggle bijv makkelijk of moeilijk zou een toggle ofzo moeten zijn." Het waren twee
     losse knoppen waarvan de actieve .primary kreeg, en dat is de knalkleur die in deze app "doe
     dit nu" betekent. Na Controleer stonden er daardoor drie rode knoppen op één scherm, waarvan
     twee niets meer deden. Het is geen actie maar een instelling met twee standen, dus is het nu
     één pil in de zachte accentkleur. */
  .segrij{display:inline-flex; border:1.5px solid var(--border); border-radius:999px;
          overflow:hidden; margin:2px 0 10px; background:var(--card);}
  .segrij button{border:none; background:none; padding:5px 13px; font-size:.82rem; font-weight:700;
                 color:var(--muted); cursor:pointer; white-space:nowrap;}
  .segrij button.aan{background:var(--accent-soft); color:var(--accent);}
  .segrij button + button{border-left:1.5px solid var(--border);}
  /* de dunne balk die aftelt tot de volgende zin; tikken waar dan ook zet hem stil */
  .doorbalk{height:3px; border-radius:2px; background:var(--border); overflow:hidden; margin:8px 0 0;}
  .doorbalk > div{height:100%; width:0; background:var(--accent); animation:doorloop 1.9s linear forwards;}
  @keyframes doorloop{from{width:0} to{width:100%}}
  @media (prefers-reduced-motion: reduce){ .doorbalk > div{animation:none; width:100%; opacity:.4;} }''')

    # ---------- 2. de moduskeuze wordt een schakelaar ----------
    rep(A_MODUS, '''  /* v23.60: dit was een rij losse knoppen waarvan de actieve .primary kreeg. Zie de stijl bij
     .segrij voor het waarom; kort: het is een instelling, geen call to action. */
  function seg(m, label){
    return "<button type='button' class='modus-toets"+(modus===m?" aan":"")+"' data-m='"+m+"'"+
      (modus===m?" aria-pressed='true'":"")+">"+label+"</button>";
  }
  return "<div class='segrij' id='"+rowId+"' role='group'>"+
    (metTegels ? seg("tegels", "🧩 "+ct("Tegels","Tiles"))
               : seg("makkelijk", "🟢 "+ct("Makkelijk","Easy")))+
    seg("moeilijk", "🔴 "+ct("Moeilijk","Hard"))+
    "</div>";''')

    # ---------- 3. je ziet waar je bent ----------
    rep(A_KICKER, '''    /* v23.60. Stefan: "dat je altijd in beeld moet zien waar je bent en hoeveel je nog moet."
       Het stond er wel ("Zin 1/3") maar als grijs kopregeltje zonder vorm. Nu met dezelfde balk als
       de helling erbij, zodat je het ziet zonder te lezen. */
    "<span class='kicker'>"+(scopeLesson?"Les "+scopeLesson.num+" · ":"")+(inFlowVertalen ? ct("Zin ","Sentence ")+((lesFlow.vertalenTotaal||5)-lesFlow.vertalenTeGaan+1)+"/"+(lesFlow.vertalenTotaal||5) : ct("Vertalen · niveau ","Translate · level ")+s.lvl+" · "+doneCount+"/"+allowIds.length+ct(" gehaald"," done"))+"</span>"+
    (function(){
      var nu, tot;
      if(inFlowVertalen){ tot = lesFlow.vertalenTotaal || 5; nu = tot - lesFlow.vertalenTeGaan; }
      else { tot = allowIds.length; nu = doneCount; }
      if(!tot) return "";
      return "<div class='progressbar' style='margin:2px 0 8px'><div style='width:"+
        Math.round(100 * Math.max(0, Math.min(nu, tot)) / tot)+"%'></div></div>";
    })()+''')

    # ---------- 4. één knop, die controleert en doorgaat ----------
    rep(A_WIRE, '''  var br = document.getElementById("btnRetry");
  if(br) br.onclick = function(){ renderSentence(false); };
  /* v23.60. Stefan: "er moet altijd een knop zijn die controleert en dan automatisch doorgaat naar
     volgende." Twee tikken voor één handeling is er een te veel. Alleen bij een goed antwoord: bij
     een fout staat het juiste antwoord er net, en dat is het moment waarop je even moet kunnen
     kijken. */
  if(gehaald && !retryable) zinDoorloop(fb, bn);''')

    rep('''function checkSentence(){
  var s = sIdx;''', '''/* v23.60: de doorloop naar de volgende zin. Hij telt zichtbaar af met een dun balkje, en elke tik
   in het feedbackblok zet hem stil. Dat laatste is het antwoord op het bezwaar uit v23.51: wie de
   zin nog wil horen tikt de luisterknop en houdt daarmee vanzelf de tijd stil. Wie niets doet gaat
   door, en dat is verreweg de meeste mensen. */
var zinDoorTimer = null;
function zinDoorStop(){
  if(zinDoorTimer){ clearTimeout(zinDoorTimer); zinDoorTimer = null; }
  var b = document.querySelector(".doorbalk");
  if(b && b.parentNode) b.parentNode.removeChild(b);
}
function zinDoorloop(fb, bn){
  zinDoorStop();
  if(!fb || !bn) return;
  var balk = document.createElement("div");
  balk.className = "doorbalk";
  balk.innerHTML = "<div></div>";
  /* na de hele knoppenrij en niet naast de knop: de rij is een flexbox, en een balkje van drie
     pixels dat daarin belandt wordt platgedrukt tot niets. Eerst gemeten, toen pas verplaatst. */
  var rij = bn.parentNode;
  if(rij && rij.parentNode) rij.parentNode.insertBefore(balk, rij.nextSibling);
  else if(rij) rij.appendChild(balk);
  fb.addEventListener("click", zinDoorStop, true);
  zinDoorTimer = setTimeout(function(){
    zinDoorTimer = null;
    var k = document.getElementById("btnNext");
    if(k) k.click();
  }, 1900);
}
function checkSentence(){
  zinDoorStop();
  var s = sIdx;''')

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
