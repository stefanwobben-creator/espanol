#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.142: je les vandaag is een blok, en de balk loopt met je mee.

Stefan, 20 aug: "wat ik nog steeds niet snap is dat als ik naar vandaag [ga] ik niet de blokken zie
wat ik vandaag ga doen. Het prototype wat je maakte was goed, ik snap niet waarom we dit niet live
doorvoeren."

## Wat er mis was

Het plan bestaat sinds v23.135 en het klopt: vijf blokken, met aantallen die uit dezelfde functies
komen die de les draaien. Maar het stond er als grijze kleine letters (`class='muted'`, .82rem)
onder een Chispa-begroeting, tussen twee andere grijze regels in. Wie het niet wist, las het niet
als "dit ga ik doen" maar als voetnoot.

En op twee momenten stond het er helemaal niet:

  * **Na je les.** Was je klaar, dan verdween de hele band (plan én knop), dus het scherm waar je
    "wat heb ik vandaag gedaan" vraagt gaf geen antwoord.
  * **Tijdens je les.** De banner zei "stap 4 van 5 · Lezen", in woorden. Waar dat vierde blok zit
    in het geheel, hoe groot het is en wat er nog komt: nergens.

## Wat er nu staat

Het prototype had drie dingen die hier ontbraken, en die komen alle drie over.

**1. Een balk op schaal.** Vijf staafjes waarvan de breedte de tijd van dat blok is. Je ziet in één
oogopslag dat woordjes twee keer zo groot is als grammatica. Dezelfde balk staat in de banner
tijdens je les, met het blok waar je nu in zit in de accentkleur en de blokken die je gehad hebt
zachter. Dat is de "waar ben ik"-vraag beantwoord zonder te tellen.

**2. Rijen die je kunt lezen.** Genummerd bolletje, vetgedrukte naam, wat erin zit, en rechts de
minuten. Geen muted-grijs meer voor de naam: het plan is het onderwerp van dat scherm, niet een
terzijde.

**3. Waar het blok voor is.** Elk blok krijgt een label: leren, begrijpen, zelf maken, sneller.
Dat zijn Nation's vier draden (2007) in gewone woorden, en het is de reden dat de les er zo uitziet.
Eén regel eronder legt het uit, en alleen als alle vier de draden er vandaag echt zijn: een belofte
die niet klopt is erger dan geen belofte (v23.135).

En na je les staat het plan er nog, met alles afgevinkt, onder de kop "Dit deed je vandaag".

## Wat dit niet doet

De verhouding tussen de blokken verandert niet. Die is wat hij is (v23.140), en of die klopt is een
eigen ronde met een eigen meting. Dit gaat alleen over wat je ziet.

Bewaakt door test/suites/pw-blokken.js.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.142"

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


# ------------- 1. de opmaak van een blok

rep(
    """  .ritme{display:flex; gap:8px; flex-wrap:wrap; margin-top:8px;}""",
    """  .ritme{display:flex; gap:8px; flex-wrap:wrap; margin-top:8px;}
  /* v23.142: het dagplan als blokken. De breedte van een staafje is de tijd van dat blok, dus de
     balk is op schaal: je ziet dat woordjes twee keer zo groot is als grammatica zonder te lezen. */
  .dagbalk{display:flex; gap:3px; margin:8px 0 2px;}
  .dagbalk i{height:6px; border-radius:3px; background:var(--border);}
  .dagbalk i.vol{background:var(--accent-soft);}
  .dagbalk i.aan{background:var(--accent);}
  .dagplan{margin:2px 0 4px;}
  .dagrij{display:flex; gap:10px; align-items:baseline; padding:5px 0;}
  .dagrij + .dagrij{border-top:1px solid var(--border);}
  .dagrij .n{flex:0 0 20px; height:20px; line-height:19px; text-align:center; border-radius:999px;
             background:var(--bg); border:1px solid var(--border); font-size:.72rem; font-weight:800;
             color:var(--muted);}
  .dagrij.aan .n{background:var(--accent); border-color:var(--accent); color:#fff;}
  .dagrij.gehad{opacity:.55;}
  .dagrij .w{flex:1; font-size:.92rem;}
  .dagrij .w .muted{font-size:.85rem;}
  .dagrij .d{display:inline-block; margin-left:6px; font-size:.66rem; text-transform:uppercase;
             letter-spacing:.05em; color:var(--muted); border:1px solid var(--border);
             border-radius:999px; padding:1px 7px; white-space:nowrap;}
  .dagrij .t{font-size:.82rem; color:var(--muted); white-space:nowrap;}""",
)

# ------------- 2. elk blok weet waar het voor is

rep(
    """    blokken.push({stap:"woorden", naam:ct("Woordjes","Words"),
      wat:nWoord + " " + ct("kaartjes","cards") + (nNieuw ? " (" + nNieuw + " " + ct("nieuw","new") + ")" : ""),
      sec:nWoord * sec});""",
    """    blokken.push({stap:"woorden", naam:ct("Woordjes","Words"), draad:ct("leren","study"),
      wat:nWoord + " " + ct("kaartjes","cards") + (nNieuw ? " (" + nNieuw + " " + ct("nieuw","new") + ")" : ""),
      sec:nWoord * sec});""",
)

rep(
    """    blokken.push({stap:"grammatica", naam:ct("Grammatica","Grammar"),
      wat:gram.length + " " + (gram.length === 1 ? ct("onderwerp","topic") : ct("onderwerpen","topics")),
      sec:gBeurten * sec});""",
    """    blokken.push({stap:"grammatica", naam:ct("Grammatica","Grammar"), draad:ct("leren","study"),
      wat:gram.length + " " + (gram.length === 1 ? ct("onderwerp","topic") : ct("onderwerpen","topics")),
      sec:gBeurten * sec});""",
)

rep(
    """    blokken.push({stap:"toetsjes", naam:ct("Toetsje","Quiz"),
      wat:qn + " " + ct("vragen","questions"), sec:qn * sec});""",
    """    /* De draad "sneller" is een keuze en geen vanzelfsprekendheid. Nation's vierde draad is
       vloeiendheid: werken met wat je al kent, onder tijdsdruk, zonder nieuwe stof. Het toetsje put
       uit de lessen die je al gehad hebt, dus dat is de dichtstbijzijnde van de vier. Wie hem
       taalgerichte studie zou noemen heeft ook een punt; dan staan er drie blokken "leren" en één
       "begrijpen", en dan klopt de regel onder het plan niet meer. */
    blokken.push({stap:"toetsjes", naam:ct("Toetsje","Quiz"), draad:ct("sneller","fluency"),
      wat:qn + " " + ct("vragen","questions"), sec:qn * sec});""",
)

rep(
    """    blokken.push({stap:"input",
      naam: inputV === "lezen" ? ct("Lezen","Reading") : ct("Luisteren","Listening"),""",
    """    blokken.push({stap:"input", draad:ct("begrijpen","input"),
      naam: inputV === "lezen" ? ct("Lezen","Reading") : ct("Luisteren","Listening"),""",
)

rep(
    """    blokken.push({stap:"produceren", naam:ct("Schrijven","Writing"),
      wat:SCHRIJF_PER_LES + " " + ct("zinnen","sentences"), sec:SCHRIJF_PER_LES * SCHRIJF_SEC});""",
    """    blokken.push({stap:"produceren", naam:ct("Schrijven","Writing"), draad:ct("zelf maken","output"),
      wat:SCHRIJF_PER_LES + " " + ct("zinnen","sentences"), sec:SCHRIJF_PER_LES * SCHRIJF_SEC});""",
)

# ------------- 3. de balk, en het plan als blokken

rep(
    '''function dagPlanHtml(nu, stappen){
  var p = dagPlan();
  var rij = stappen && stappen.length ? stappen : p.stappen;
  var blokken = p.blokken.filter(function(b){ return rij.indexOf(b.stap) !== -1; });
  if(!blokken.length) return "";
  var iNu = nu ? rij.indexOf(nu) : -1;
  var rest = 0;
  blokken.forEach(function(b){ if(iNu < 0 || rij.indexOf(b.stap) >= iNu) rest += b.sec; });
  var restMin = Math.max(1, Math.round(rest / 60));
  var kop = (iNu > 0 ? ct("Nog ongeveer "+restMin+" min","About "+restMin+" min to go")
                     : ct("Je les vandaag","Your session today")+" · "+
                       ct("ongeveer "+p.min+" min","about "+p.min+" min")) +
            (p.gemeten ? ct(", gerekend met jouw tempo",", based on your own pace")
                       : ct(", geschat",", estimated"));
  var r = "<p class='muted' style='margin:8px 0 2px; font-size:.82rem'><b>"+kop+"</b></p>";
  blokken.forEach(function(b){
    var gehad = iNu > 0 && rij.indexOf(b.stap) < iNu;
    r += "<div style='display:flex; gap:8px; align-items:baseline; font-size:.85rem; padding:1px 0"+
         (gehad ? "; opacity:.5" : "")+"'>"+
      "<span class='muted' style='min-width:1.1em; text-align:right'>"+(gehad ? "\\u2713" : b.nr)+"</span>"+
      "<span style='flex:1'>"+(gehad ? b.naam : "<b>"+b.naam+"</b>")+
        " <span class='muted'>"+b.wat+"</span></span>"+
      "<span class='muted' style='white-space:nowrap'>"+b.min+" min</span></div>";
  });
  return r;
}''',
    '''/* v23.142: één plek die uitrekent welke blokken er in beeld zijn en waar je staat. Twee weergaven
   lezen eruit: de balk (in de banner tijdens je les) en het lijstje (op Vandaag). Twee plekken die
   dat zelf uitrekenen zijn twee waarheden.

   nu === "klaar" betekent: alles gehad. Dat is het scherm ná je les, waar de vraag niet meer is wat
   je gaat doen maar wat je gedaan hebt. */
function dagPlanStand(nu, stappen){
  var p = dagPlan();
  var rij = stappen && stappen.length ? stappen : p.stappen;
  var blokken = p.blokken.filter(function(b){ return rij.indexOf(b.stap) !== -1; });
  var klaar = nu === "klaar";
  var iNu = klaar ? rij.length : (nu ? rij.indexOf(nu) : -1);
  return {p:p, rij:rij, blokken:blokken, klaar:klaar, iNu:iNu};
}
/* De balk op schaal. De breedte van een staafje is de tijd van dat blok, dus je ziet de verhouding
   zonder een getal te lezen. Vóór je begint staat alles zacht ingekleurd (dit is wat je gaat doen);
   tijdens je les is het blok waar je in zit vol en de rest leeg. */
function dagBalkHtml(nu, stappen){
  var s = dagPlanStand(nu, stappen);
  if(s.blokken.length < 2) return "";
  var r = "<div class='dagbalk'>";
  s.blokken.forEach(function(b){
    var i = s.rij.indexOf(b.stap);
    var kl = s.iNu < 0 ? "vol" : (i < s.iNu ? "vol" : (i === s.iNu ? "aan" : ""));
    r += "<i style='flex:"+Math.max(1, Math.round(b.sec))+"' class='"+kl+"'></i>";
  });
  return r + "</div>";
}
function dagPlanHtml(nu, stappen){
  var s = dagPlanStand(nu, stappen);
  if(!s.blokken.length) return "";
  var rest = 0;
  s.blokken.forEach(function(b){ if(s.iNu < 0 || s.rij.indexOf(b.stap) >= s.iNu) rest += b.sec; });
  var restMin = Math.max(1, Math.round(rest / 60));
  var kop = s.klaar
    ? ct("Dit deed je vandaag","What you did today")
    : (s.iNu > 0 ? ct("Nog ongeveer "+restMin+" min","About "+restMin+" min to go")
                 : ct("Je les vandaag","Your session today")+" · "+
                   ct("ongeveer "+s.p.min+" min","about "+s.p.min+" min")) +
      (s.p.gemeten ? ct(", gerekend met jouw tempo",", based on your own pace")
                   : ct(", geschat",", estimated"));
  var r = "<p style='margin:10px 0 0; font-size:.86rem'><b>"+kop+"</b></p>"+
          dagBalkHtml(nu, stappen)+"<div class='dagplan'>";
  s.blokken.forEach(function(b){
    var i = s.rij.indexOf(b.stap);
    var gehad = s.iNu > 0 && i < s.iNu;
    r += "<div class='dagrij"+(gehad ? " gehad" : "")+(i === s.iNu ? " aan" : "")+"'>"+
      "<span class='n'>"+(gehad ? "\\u2713" : b.nr)+"</span>"+
      "<span class='w'><b>"+b.naam+"</b> <span class='muted'>"+b.wat+"</span>"+
        (b.draad ? "<span class='d'>"+b.draad+"</span>" : "")+"</span>"+
      "<span class='t'>"+b.min+" min</span></div>";
  });
  r += "</div>";
  /* Waarom de blokken zijn zoals ze zijn, in één regel: Nation's vier draden (2007) in gewone
     woorden. Alleen als ze er alle vier echt zijn. Een uitleg over vier draden onder een plan met
     drie blokken is precies het soort belofte dat niet klopt (v23.135). */
  if(!s.klaar && dagDradenCompleet(s.blokken)){
    r += "<p class='muted' style='margin:2px 0 0; font-size:.8rem'>"+ct(
      "Elke dag raak je alle vier de manieren aan waarop een taal binnenkomt: leren, begrijpen, zelf maken, en sneller worden in wat je al kent.",
      "Every day you touch all four ways a language goes in: study, understanding, producing, and getting faster at what you already know.")+"</p>";
  }
  return r;
}
function dagDradenCompleet(blokken){
  var gezien = {}, n = 0;
  (blokken || []).forEach(function(b){
    if(b.draad && !gezien[b.draad]){ gezien[b.draad] = 1; n++; }
  });
  return n >= 4;
}''',
)

# ------------- 4. de balk loopt mee door je les

rep(
    '''        chispaZegHtml(f.es, ct(f.nl, f.en || f.nl))+
      "</div>"+
    "</div>"+
  "</div>";
}''',
    '''        chispaZegHtml(f.es, ct(f.nl, f.en || f.nl))+
      "</div>"+
    "</div>"+
    /* v23.142: dezelfde balk als op Vandaag, met het blok waar je nu in zit vol. De kicker hierboven
       zegt "stap 4 van 5" in woorden; dit zegt waar dat vierde blok zit en hoe groot het is. */
    dagBalkHtml(lesFlow.stap, lesFlow.stappen)+
  "</div>";
}''',
)

# ------------- 5. en na je les staat het er nog

rep(
    '''    (afgesloten || (gedaanVandaag && !hervat) ? "" :''',
    '''    /* v23.142: was je klaar, dan verdween hier de hele band en gaf het dagscherm geen antwoord op
       "wat heb ik vandaag gedaan". Nu staat het plan er nog, afgevinkt. */
    (afgesloten || (gedaanVandaag && !hervat) ? (toonPlan ? dagPlanHtml("klaar") : "") :''',
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
