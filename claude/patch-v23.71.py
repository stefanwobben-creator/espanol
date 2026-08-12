#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.71: je krijgt je herstelcode op het moment dat je iets te verliezen hebt.

Van de lanceerlijst, punt 4 (Progressie kwijtraken): "Alles staat in localStorage. Er zijn
synccodes, dus herstel kán, maar een vreemde die zijn browser leegt weet niet dat die code bestond.
Het synccode-moment hoort ná de eerste voltooide les, niet ervoor."

Nagekeken waar de code nu staat. `<b id="syncCode">` zit in `#instelBlok`, en dat blok is
standaard `hidden`; je komt er via Meer, dan Profiel, dan de knop "Instellingen". Drie tikken, en
alle drie op plekken waar een vreemde in zijn eerste week niets te zoeken heeft. De code bestáát dus
wel, maar de enige die hem tegenkomt is iemand die al weet dat hij bestaat.

## Wat er nu gebeurt

Na je les staat er, onder de vieringskaart, één blok:

    🔑 Bewaar dit even
    Je voortgang staat in deze browser. Wis je die, of wil je verder op je telefoon,
    dan heb je deze code nodig.

        stefan-x7k2m9p4qa3b
        [ Kopieer ]   [ Ik heb hem ]

    Hij staat later ook bij Meer, Profiel, Instellingen.

Het blijft staan tot je op een van de twee knoppen tikt (`S.codeGezien`). Niet één keer laten zien
en dan weg: dit is het enige in de app waarvan het missen onherstelbaar is, en één keer knipperen op
het moment dat iemand net confetti heeft gezien is geen mededeling.

Waarom hier en niet eerder: vóór je eerste les heb je niets te verliezen, en een app die op scherm
één om een code begint te zwaaien vraagt vertrouwen dat hij nog niet verdiend heeft. Waarom hier en
niet in een pop-up: een pop-up klik je weg zonder te lezen, en dat is precies de handeling die je
hier níét wilt oefenen.

## Eerlijk over wat het niet is

Dit is geen back-up. De code haalt je voortgang van de server, en die server heeft alleen wat er
tijdens het oefenen heen is gestuurd. Dat staat er niet bij, want de zin die het zou uitleggen is
langer dan het hele blok. Wat er wel staat is waar de code voor is, en dat is de vraag die iemand
zich stelt op het moment dat hij hem nodig heeft.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.71"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "function lesFlowCodeHtml" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_INVOEG = '''    "</div>"+
    // v19.57: net klaar met een les is het moment waarop je het idee leuk vindt, niet halverwege
    // een oefening. Vanaf de tweede sessie, en daarna nooit meer zodra je gedeeld hebt.
    // v19.58: hoogstens ÉÉN vraag onder de felicitatie, gekozen door samenKaartNu().
    samenKaartNu(false);
  document.getElementById("btnLesFlowNogEens").onclick = function(){ lesFlowStart(); };'''

A_PLEK = '''function lesFlowVoorstellen(){'''

if DOE_APP:
    ontbreekt = [a for a in [A_INVOEG, A_PLEK] if a not in src]
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
    rep(A_PLEK, '''/* ================= DE HERSTELCODE, NA JE EERSTE LES (v23.71) =================
   Van de lanceerlijst: "een vreemde die zijn browser leegt weet niet dat die code bestond."
   Nagekeken: de code staat in #instelBlok, en dat blok is standaard hidden. Meer, dan Profiel, dan
   Instellingen. De enige die hem tegenkomt is iemand die al weet dat hij bestaat.

   Waarom ná de les en niet eerder: daarvóór heb je niets te verliezen, en om een code zwaaien op
   scherm één vraagt vertrouwen dat de app nog niet verdiend heeft. Waarom geen pop-up: die klik je
   weg zonder te lezen, en dat is precies de handeling die je hier niet wilt oefenen.

   Hij blijft staan tot je hem wegtikt. Dit is het enige in de app waarvan het missen onherstelbaar
   is, en één keer knipperen vlak na de confetti is geen mededeling. */
function lesFlowCodeHtml(){
  if(S.codeGezien) return "";
  var p = null;
  try { p = activeProfile(); } catch(e){ p = null; }
  if(!p) return "";
  var code = "";
  try { code = ensureCode(p); } catch(e){ code = ""; }
  if(!code) return "";
  return "<div class='card' id='codeKaart' style='margin-top:10px'>"+
    "<span class='kicker'>\\ud83d\\udd11 "+ct("Bewaar dit even","Keep this somewhere")+"</span>"+
    "<p style='margin:6px 0 0'>"+
      ct("Je voortgang staat in deze browser. Wis je die, of wil je verder op je telefoon, dan heb je deze code nodig.",
         "Your progress lives in this browser. If you clear it, or want to carry on from your phone, you need this code.")+"</p>"+
    "<p style='margin:10px 0 6px'><b id='codeTekst' style='font-size:1.05rem; letter-spacing:.03em; word-break:break-all'>"+code+"</b></p>"+
    "<div class='row'>"+
      "<button class='ghost' id='btnCodeKopieer'>"+ct("Kopieer","Copy")+"</button>"+
      "<button class='ghost' id='btnCodeGezien'>"+ct("Ik heb hem","Got it")+"</button>"+
    "</div>"+
    "<p class='muted' style='margin:8px 0 0; font-size:.84rem'>"+
      ct("Hij staat later ook bij Meer, Profiel, Instellingen.",
         "You can find it later under More, Profile, Settings.")+"</p></div>";
}
function lesFlowCodeWire(){
  var weg = function(){
    S.codeGezien = true;
    try { persist(); } catch(e){}
    var k = document.getElementById("codeKaart");
    if(k && k.parentNode) k.parentNode.removeChild(k);
  };
  var bg = document.getElementById("btnCodeGezien");
  if(bg) bg.onclick = weg;
  var bk = document.getElementById("btnCodeKopieer");
  if(bk) bk.onclick = function(){
    var t = document.getElementById("codeTekst");
    var code = t ? t.textContent : "";
    /* navigator.clipboard bestaat niet op http en kan geweigerd worden. Dan selecteren we de code,
       zodat kopiëren met de hand nog één handeling is in plaats van overtypen. */
    if(navigator.clipboard && navigator.clipboard.writeText){
      navigator.clipboard.writeText(code).then(function(){
        toast(ct("Gekopieerd \\u2713","Copied \\u2713")); weg();
      }).catch(function(){ codeSelecteer(t); });
    } else { codeSelecteer(t); }
  };
}
function codeSelecteer(t){
  if(!t) return;
  try {
    var r = document.createRange();
    r.selectNodeContents(t);
    var s = window.getSelection();
    s.removeAllRanges(); s.addRange(r);
    toast(ct("Kopieer hem met je toetsenbord of houd hem ingedrukt.",
             "Copy it with your keyboard, or press and hold."));
  } catch(e){}
}
function lesFlowVoorstellen(){''')

    rep(A_INVOEG, '''    "</div>"+
    /* v23.71: de herstelcode, één blok onder de viering, tot je hem wegtikt. Zie lesFlowCodeHtml(). */
    lesFlowCodeHtml()+
    // v19.57: net klaar met een les is het moment waarop je het idee leuk vindt, niet halverwege
    // een oefening. Vanaf de tweede sessie, en daarna nooit meer zodra je gedeeld hebt.
    // v19.58: hoogstens ÉÉN vraag onder de felicitatie, gekozen door samenKaartNu().
    samenKaartNu(false);
  lesFlowCodeWire();
  document.getElementById("btnLesFlowNogEens").onclick = function(){ lesFlowStart(); };''')

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
