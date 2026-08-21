#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.154: het scherm vóór het scherm is weg, en de doosjes hebben weer een naam.

Stefan, 21 aug, na een echte doorloop: "Hier krijg je een grammatica vraag op van 2 van 3 zomaar en
die lijkt uit het niets te komen."

## Wat er op dat scherm stond

Kicker "PRESENTE OF ESTAR + GERUNDIO · STAP 1/3". Titel "⏱ Probeer eens". Regel eronder: "Het
volgende onderwerp in je leervolgorde." Dan drie bolletjes 1-2-3. Dan: "Eerst een voorbeeld, en gok
gerust: het antwoord komt er meteen achteraan, met in één zin waarom." Dan twee knoppen: "Toets me →"
en "Overslaan →".

Zes lagen, en geen woord Spaans. Dat is een scherm waarvan de hele inhoud is: hier komt zo een
vraag. Geen enkele app waar je het mee vergelijkt doet dat, en terecht.

De oorzaak is precies aan te wijzen. gcBouw() bouwt stap 1 met als uitleg de zin uit GC_STAP_TXT.u1,
en die zin gaat niet over Spaans maar over hoe de oefening werkt. gwStapHeeftTekst() kijkt alleen of
er tekst staat, niet waar die tekst over gaat, dus krijgt die stap een eigen uitlegscherm.

Nu: stap 1 is gemarkeerd als procedureel, gwStapHeeftTekst() slaat hem daarom over, en die ene zin
staat als onderregel bóven de eerste vraag. Je begint dus met een Spaanse zin op je scherm in plaats
van met een aankondiging.

## En "Stap klaar: 2/2"

Dat 2/2 is je score, niet je positie. Maar er staat "stap" bij, en boven het scherm staat "STAP 1/3".
Twee tellers die allebei "stap" heten en iets anders bedoelen. Nu: "2 van de 2 goed", en waar je bent
staat er in woorden naast.

## De undefined-regels

Op Voortgang stonden drie regels "undefined 0" onder de balken. INTERVALS is in v23.132 van zeven
naar negen doosjes gegaan; renderStats() had een handgeschreven lijst van zes labels en
krachtTabelHtml() een tweede handgeschreven lijst van negen. Twee lijsten met hetzelfde feit erin, en
allebei losgekoppeld van de data waar het feit vandaan komt.

Nu één functie die het label uit INTERVALS rekent. Een tiende doosje erbij levert vanzelf een naam
op, en "undefined" kan niet meer terugkomen.

Bewaakt door test/suites/pw-gramstap.js.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.154"

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


# ================= 1. de doosjes krijgen hun naam uit de data =================

rep(
    '''function krachtTabelHtml(){''',
    '''/* ================= HOE EEN DOOSJE HEET (v23.154) =================

   Op Voortgang stonden drie regels "undefined 0". INTERVALS is in v23.132 van zeven naar negen
   doosjes gegaan, en er stonden twee handgeschreven labellijsten in het bestand: eentje van zes in
   renderStats() en eentje van negen in krachtTabelHtml(). Allebei losgekoppeld van INTERVALS, dus
   allebei fout te krijgen, en de eerste wás het.

   Staat een feit in de data, dan schrijft geen enkele codeplek dat feit opnieuw. Het aantal dagen
   staat in INTERVALS; hoe dat heet is een som en geen lijst. */
function intervalNaam(dagen){
  var d = dagen || 0;
  if(d <= 0) return ct("nieuw/fout", "new/wrong");
  if(d < 7) return d + " " + (d === 1 ? ct("dag","day") : ct("dagen","days"));
  if(d < 30){
    var w = Math.round(d / 7);
    return w + " " + (w === 1 ? ct("week","week") : ct("weken","weeks"));
  }
  var m = Math.round(d / 30);
  return m + " " + (m === 1 ? ct("maand","month") : ct("maanden","months"));
}
function intervalNamen(){
  return (typeof INTERVALS !== "undefined" ? INTERVALS : [0]).map(intervalNaam);
}

function krachtTabelHtml(){''',
)

rep(
    '''  var lab = ct("nieuw/fout|1 dag|3 dagen|1 week|2 weken|1 maand|2 maanden|4 maanden|8 maanden",
               "new/wrong|1 day|3 days|1 week|2 weeks|1 month|2 months|4 months|8 months").split("|");''',
    '''  var lab = intervalNamen();   // v23.154: uit INTERVALS, niet met de hand''',
)

rep(
    '''  // v19.67: ook dit scherm sprak Nederlands tegen een Engelse gebruiker.
  var boxLabels = ct("nieuw/fout|1 dag|3 dagen|1 week|2 weken|1 maand","new/wrong|1 day|3 days|1 week|2 weeks|1 month").split("|");''',
    '''  /* v19.67: ook dit scherm sprak Nederlands tegen een Engelse gebruiker.
     v23.154: en het telde zes namen bij negen doosjes, dus er stonden drie regels "undefined 0"
     op het scherm. Nu uit INTERVALS. */
  var boxLabels = intervalNamen();''',
)

# ================= 2. stap 1 is geen scherm meer, maar een regel =================

rep(
    '''    stappen.push({kop:GC_STAP_TXT.nl.k1, kopEn:GC_STAP_TXT.en.k1,
      uitleg:"<p>" + GC_STAP_TXT.nl.u1 + "</p>", uitlegEn:"<p>" + GC_STAP_TXT.en.u1 + "</p>",
      vragen:vb.slice(0, 2)});''',
    '''    /* v23.154: `procedureel` erbij, en dat is het hele punt van deze ronde. Deze uitleg gaat niet
       over Spaans maar over hoe de oefening werkt, en toch kreeg hij een eigen scherm met een knop
       "Toets me →". Stefan, 21 aug: "die lijkt uit het niets te komen." Terecht: op dat scherm stond
       geen woord Spaans. De zin blijft, maar als onderregel bij de eerste vraag. */
    stappen.push({kop:GC_STAP_TXT.nl.k1, kopEn:GC_STAP_TXT.en.k1, procedureel:true,
      uitleg:"<p>" + GC_STAP_TXT.nl.u1 + "</p>", uitlegEn:"<p>" + GC_STAP_TXT.en.u1 + "</p>",
      vragen:vb.slice(0, 2)});''',
)

rep(
    '''function gwStapHeeftTekst(o, i){
  try {
    var s = o && o.stappen && o.stappen[i];
    if(!s) return true;
    return !!String(ct(s.uitleg, s.uitlegEn) || "").replace(/<[^>]*>/g, "").trim();
  } catch(e){ return true; }
}''',
    '''function gwStapHeeftTekst(o, i){
  try {
    var s = o && o.stappen && o.stappen[i];
    if(!s) return true;
    // v23.154: een stap waarvan de uitleg over de oefening gaat en niet over Spaans, krijgt geen
    // eigen scherm. Zie gcBouw.
    if(s.procedureel) return false;
    return !!String(ct(s.uitleg, s.uitlegEn) || "").replace(/<[^>]*>/g, "").trim();
  } catch(e){ return true; }
}''',
)

rep(
    '''    var html = kop +
      "<span class='kicker'>"+ct("Vraag ","Question ")+(gwSess.vraag+1)+"/"+stap.vragen.length+"</span>"+
      "<p class='big' style='margin:6px 0 12px'>"+gwVraagTekst(q)+"</p>"+''',
    '''    var html = kop +
      "<span class='kicker'>"+ct("Vraag ","Question ")+(gwSess.vraag+1)+"/"+stap.vragen.length+"</span>"+
      /* v23.154: de zin die eerst een heel scherm vulde staat nu hier, bij de eerste vraag, waar hij
         hoort: het is een gebruiksaanwijzing en die lees je terwijl je het doet. */
      (stap.procedureel && gwSess.vraag === 0
        ? "<p class='muted' style='margin:4px 0 0; font-size:.85rem'>"+
            String(ct(stap.uitleg, stap.uitlegEn) || "").replace(/<[^>]*>/g, "")+"</p>"
        : "")+
      "<p class='big' style='margin:6px 0 12px'>"+gwVraagTekst(q)+"</p>"+''',
)

# ================= 3. twee tellers die allebei "stap" heetten =================

rep(
    '''        ct("Stap klaar: ","Step done: ")+gwSess.goed+"/"+totaal+
      "</div>"+''',
    '''        /* v23.154: hier stond "Stap klaar: 2/2", en dat 2/2 is je score en niet je positie. Boven
           het scherm staat tegelijk "STAP 1/3". Twee tellers die allebei "stap" heten en iets anders
           bedoelen is precies waarom Stefan schreef dat hij niet weet wanneer wat gebeurt. */
        ct(gwSess.goed+" van de "+totaal+" goed", gwSess.goed+" out of "+totaal+" correct")+
        (o.stappen.length > 1
          ? " \\u00b7 " + ct("deel "+(gwSess.stap+1)+" van "+o.stappen.length+" van dit onderwerp",
                            "part "+(gwSess.stap+1)+" of "+o.stappen.length+" of this topic")
          : "")+
      "</div>"+''',
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
