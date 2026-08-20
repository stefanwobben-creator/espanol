#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.139: het eindscherm in gewone taal, met grammatica en met hoe lang je nog te gaan hebt.

Stefan, 20 aug: "maar mensen snappen woord doosjes omhoog en gered niet. en hier zit niet de
grammatica bij of je voortgang of voorspelling richting je niveau."

## De fout van gisteren

Ik heb in v23.138 een scherm gebouwd dat in mijn eigen jargon praat. "Kaartjes een doosje omhoog" en
"woorden gered" zijn termen uit de SRS-machinerie; er is geen enkele reden waarom een gebruiker zou
weten wat een doosje is. Dat is precies de klacht die v23.66 al eens opleverde ("leuk statistieken
maar hoe moet ik die lezen wat zeggen die?"), en ik ben er opnieuw ingelopen.

De regel die eruit volgt: **zeg wat er gebeurt, niet hoe de machine heet.** Een doos omhoog betekent
dat je een woord een tijd niet hoeft te zien. Dus staat dat er, met het aantal dagen erbij, gerekend
uit de intervallen van precies die woorden.

    was:  7 kaartjes een doosje omhoog
          die komen nu later terug in plaats van morgen

    nu:   7 woorden zie je pas over 3 tot 14 dagen terug
          je had ze goed, dus de app schuift ze vooruit

    was:  3 woorden gered
    nu:   3 woorden die je bijna kwijt was, ken je weer

## Grammatica stond er niet in

`S.gram` houdt per onderwerp bij hoe vaak je het goed en fout had, met een dagstempel (`bd`) op de
goede kant en `laatst` op de foute. Alles wat nodig is om te zeggen wat er vandaag met je grammatica
gebeurde lag er dus al; het werd alleen nergens per dag gelezen. Nu:

    Ser of estar ging vooruit · 18 goed, 7 fout tot nu toe
    Por of para: nog even oefenen · vandaag ging het mis

## En hoe lang je nog te gaan hebt

`voortgangBand()` bestaat sinds v19.83 en rekent uit je eigen weekmetingen een ondergrens en een
bovengrens in weken, met een marge van twee standaardfouten. Hij verschijnt pas na drie
weekmetingen, want met twee punten is elk tempo toeval. Hij stond alleen op het Voortgang-scherm,
en dat is precies het scherm dat je één keer per week opent.

Nu staat de korte versie ook na je les:

    A2 · 612 van de 1284 woorden staan vast
    Op dit tempo nog 12 tot 19 weken

Zijn er nog geen drie weekmetingen, dan staat er wat er waar is: dat we meten en hoeveel weken er
nog nodig zijn. Geen geleend getal.

## Wat er nog steeds niet staat

"Bewezen vast" als teller die elke dag beweegt. Die beweegt niet elke dag: een woord vast krijgen
kost vijf goede beurten over minstens vijfentwintig dagen. Het getal staat er nu wel als stand
("612 van de 1284"), naast de voorspelling, en dat is iets anders dan een teller die vandaag zou
moeten oplopen.

Bewaakt door test/suites/pw-verschoven.js (uitgebreid).
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.139"

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


# ------------- 1. de meting kent ook de wachttijd en de grammatica

rep(
    '''function dagVerschoven(){
  var t = today(), omhoog = 0, gered = 0, vast = [], id, st, w;
  for(id in (S.srs || {})){
    st = S.srs[id];
    if(!st || typeof st !== "object" || st.od !== t) continue;
    omhoog++;
    if((st.f || 0) > 0) gered++;''',
    '''function dagVerschoven(){
  var t = today(), omhoog = 0, gered = 0, vast = [], id, st, w;
  /* v23.139: hoeveel dagen die woorden nu wegblijven. Zonder dit getal moet het scherm het woord
     "doosje" gebruiken om uit te leggen wat er gebeurd is, en dat is machinetaal. Met dit getal kan
     er staan wat er echt gebeurt: je ziet ze een tijd niet. */
  var dagMin = null, dagMax = null, dg;
  for(id in (S.srs || {})){
    st = S.srs[id];
    if(!st || typeof st !== "object" || st.od !== t) continue;
    omhoog++;
    dg = INTERVALS[st.box || 0] || 0;
    if(dagMin === null || dg < dagMin) dagMin = dg;
    if(dagMax === null || dg > dagMax) dagMax = dg;
    if((st.f || 0) > 0) gered++;''',
)

rep(
    '''  return {omhoog:omhoog, gered:gered, nieuw:nieuw, uitLezen:uitLezen, vast:vast,
          tredeVoor: v ? v.dagStart : null, tredeNa: v ? v.trede : null};
}''',
    '''  return {omhoog:omhoog, gered:gered, nieuw:nieuw, uitLezen:uitLezen, vast:vast,
          dagMin:dagMin, dagMax:dagMax, gram:dagGramVerschoven(),
          tredeVoor: v ? v.dagStart : null, tredeNa: v ? v.trede : null};
}
/* v23.139: wat er vandaag met je grammatica gebeurde. S.gram houdt per onderwerp goed, fout en een
   dagstempel bij (bd op de goede kant sinds v23.92, laatst op de foute), dus alles wat hier nodig is
   lag er al. Het werd alleen nergens per dag gelezen. */
function dagGramVerschoven(){
  var t = today(), uit = [], k, g;
  for(k in (S.gram || {})){
    g = S.gram[k];
    if(!g || typeof g !== "object") continue;
    if(g.bd === t) uit.push({id:k, naam:gramNaam(k), vooruit:true, goed:g.goed || 0, fout:g.fout || 0});
    else if(g.laatst === t) uit.push({id:k, naam:gramNaam(k), vooruit:false, goed:g.goed || 0, fout:g.fout || 0});
  }
  return uit.slice(0, 2);
}
/* Waar je staat en hoe lang je nog te gaan hebt, in twee regels. voortgangBand() bestaat sinds
   v19.83 en rekent uit je eigen weekmetingen een marge in weken; hij stond alleen op het
   Voortgang-scherm, en dat is precies het scherm dat je een keer per week opent. */
function dagNiveauHtml(){
  var niv, tel, vast, noem, b;
  try {
    niv = NIV_NAAM[Math.min(poortRang(), NIV_NAAM.length - 1)] || "A1";
    tel = voortgangTellers();
    vast = (tel.dek && tel.dek[niv]) || 0;
    noem = PCIC_NOEMER[niv] || 0;
    b = voortgangBand(niv);
  } catch(e){ return ""; }
  if(!noem) return "";
  var staart;
  if(b && b.onder === 0 && b.boven === 0){
    staart = ct(niv+" is vol.", niv+" is full.");
  } else if(b && b.tempo > 0){
    staart = ct("op dit tempo nog "+(b.boven === null ? "minstens "+b.onder : b.onder+" tot "+b.boven)+" weken",
                "at this pace, "+(b.boven === null ? "at least "+b.onder : b.onder+" to "+b.boven)+" more weeks");
  } else {
    var weken = 0;
    try { weken = metingenNieuweMaat(niv).length; } catch(e){ weken = 0; }
    var nog = Math.max(1, 3 - weken);
    staart = ct("hoe lang je nog te gaan hebt weet de app na nog "+nog+" "+(nog === 1 ? "week" : "weken")+" meten",
                "how long you have to go is known after "+nog+" more "+(nog === 1 ? "week" : "weeks")+" of measuring");
  }
  return dagRegel("<b>"+niv+"</b> \u00b7 "+
    ct(vast+" van de "+noem+" woorden staan vast", vast+" of "+noem+" words are solid")+
    " \u00b7 "+staart);
}''',
)

# ------------- 2. het scherm zegt wat er gebeurt, en past binnen het venster

# pw-naronde bewaakt sinds v23.58 dat het antwoord op "en nu?" binnen het scherm valt en in de
# kaart van de viering zelf staat. Twee kaarten met metingen ervoor duwden dat eruit, en de suite
# werd daar terecht rood op. Dus geen kaarten maar regels, ín de viering.

rep(
    """function dagMetingRij(n, kop, uitleg){
  return "<div style='display:flex; align-items:baseline; gap:10px; padding:5px 0; border-bottom:1px solid var(--border)'>"+
    "<b style='font-size:1.3rem; min-width:1.8em; text-align:right'>"+n+"</b>"+
    "<span style='font-size:.88rem'>"+kop+
      "<span style='display:block; font-size:.78rem; color:var(--muted)'>"+uitleg+"</span></span></div>";
}
function dagVerschovenHtml(){
  var d = dagVerschoven(), r = "";
  if(d.omhoog){
    r += dagMetingRij(d.omhoog, ct("kaartjes een doosje omhoog","cards moved up a box"),
      ct("die komen nu later terug in plaats van morgen","they come back later now instead of tomorrow"));
  }
  if(d.gered){
    r += dagMetingRij(d.gered, ct("woorden gered","words rescued"),
      ct("die had je eerder fout en vandaag weer goed","you had these wrong before and right again today"));
  }
  if(d.nieuw || d.uitLezen){
    r += dagMetingRij(d.nieuw + d.uitLezen, ct("nieuw vandaag","new today"),
      d.uitLezen ? ct("waarvan "+d.uitLezen+" die je zelf aantikte tijdens het lezen",
                      "of which "+d.uitLezen+" you tapped yourself while reading")
                 : ct("uit je dagportie","from today's portion"));
  }
  if(d.tredeNa !== null && d.tredeNa !== d.tredeVoor){
    r += dagMetingRij((d.tredeNa > d.tredeVoor ? "+" : "") + (d.tredeNa - d.tredeVoor),
      ct("op de ladder van zelf maken","on the writing ladder"),
      ct("je staat nu op trede "+d.tredeNa+" van "+VERT_TREDES.length,
         "you are now on step "+d.tredeNa+" of "+VERT_TREDES.length));
  }
  /* Geen lijstje met nullen. Deed je vandaag alleen dingen die niets verschoven, dan is dat het
     eerlijke antwoord en hoort er niets te staan. */
  if(!r) return "";
  var kop = "<div class='card'><span class='kicker'>"+ct("Wat er vandaag verschoof","What moved today")+"</span>"+r+"</div>";
  if(d.vast.length){
    kop += "<div class='card' style='background:var(--green-soft); border-color:#bfe0cd'>"+
      "<span class='kicker'>"+ct("Vast","Solid")+"</span>"+
      d.vast.map(function(x){
        return "<p style='margin:0 0 2px'><span class='es' style='font-weight:700'>"+x.es+"</span> "+
          ct("staat nu vast.","is solid now.")+"</p>"+
          "<p class='muted' style='margin:0 0 6px; font-size:.83rem'>"+
          ct(x.n+" beurten, en de laatste was een check die je niet zelf beoordeelde. Die zie je pas over twee maanden terug.",
             x.n+" turns, and the last one was a check you did not grade yourself. You will not see it again for two months.")+"</p>";
      }).join("")+"</div>";
  }
  return kop;
}""",
    """/* v23.139: regels in plaats van kaarten met grote getallen.

   Twee dingen dwongen dit af. Stefan: "mensen snappen woord doosjes omhoog en gered niet", dus de
   taal moest weg uit de machinerie. En pw-naronde bewaakt sinds v23.58 dat het antwoord op "en nu?"
   binnen het scherm valt en in de kaart van de viering zelf staat; twee kaarten met metingen ervoor
   duwden dat eruit, en die suite werd daar terecht rood op.

   Dus: vier korte regels binnen de viering. Na een les wil je een blik, geen rapport. Het volledige
   verhaal staat op Voortgang, en daar hoort het ook. */
function dagRegel(tekst){
  return "<p class='muted' style='margin:5px 0 0; font-size:.87rem; line-height:1.45'>"+tekst+"</p>";
}
function dagVerschovenHtml(){
  var d = dagVerschoven(), deel = [], r = "";
  if(d.omhoog){
    var wacht = d.dagMin === d.dagMax
      ? ct("over "+d.dagMax+" dagen","in "+d.dagMax+" days")
      : ct("over "+d.dagMin+" tot "+d.dagMax+" dagen","in "+d.dagMin+" to "+d.dagMax+" days");
    deel.push(ct("<b>"+d.omhoog+" woorden</b> zie je pas "+wacht+" terug",
                 "<b>"+d.omhoog+" words</b> you will not see again "+wacht));
  }
  if(d.gered){
    deel.push(ct("<b>"+d.gered+"</b> die je bijna kwijt was, ken je weer",
                 "<b>"+d.gered+"</b> you had nearly lost, you know again"));
  }
  if(d.nieuw || d.uitLezen){
    deel.push(ct("<b>"+(d.nieuw + d.uitLezen)+"</b> voor het eerst gezien"+
                 (d.uitLezen ? " (waarvan "+d.uitLezen+" uit je boek)" : ""),
                 "<b>"+(d.nieuw + d.uitLezen)+"</b> seen for the first time"+
                 (d.uitLezen ? " ("+d.uitLezen+" from your book)" : "")));
  }
  if(deel.length) r += dagRegel(deel.join(" \u00b7 "));
  var tweede = [];
  (d.gram || []).forEach(function(g){
    tweede.push(veiligHtml(g.naam)+" "+(g.vooruit ? ct("ging vooruit","moved forward")
                                                  : ct("kwam terug","came back")));
  });
  if(d.tredeNa !== null && d.tredeNa !== d.tredeVoor){
    tweede.push(ct((d.tredeNa > d.tredeVoor ? "langere" : "kortere")+" zinnen om zelf te maken: trede "+
                   d.tredeNa+" van "+VERT_TREDES.length,
                   (d.tredeNa > d.tredeVoor ? "longer" : "shorter")+" sentences to write: step "+
                   d.tredeNa+" of "+VERT_TREDES.length));
  }
  if(tweede.length) r += dagRegel(tweede.join(" \u00b7 "));
  d.vast.forEach(function(x){
    r += dagRegel("<span class='vast'>\u2713</span> <span class='es'><b>"+x.es+"</b></span> "+
      ct("staat nu vast, na "+x.n+" beurten. Die zie je pas over twee maanden terug.",
         "is solid now, after "+x.n+" turns. You will not see it again for two months."));
  });
  /* Geen lijstje met nullen. Deed je vandaag alleen dingen die niets verschoven, dan is dat het
     eerlijke antwoord en hoort er niets te staan. */
  return r;
}""",
)

rep(
    """function dagNiveauHtml(){
  var niv, tel, vast, noem, b;""",
    """function dagNiveauHtml(){
  var niv, tel, vast, noem, b;""",
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
