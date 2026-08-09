#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.14: punt 1 en 2 van claude/voortgangsinzicht.md.

Een cijferfunctie, voortgangCijfers(), en twee schermen die hem allebei aanroepen. Vandaag krijgt
de geoefend-teller en het foutpercentage erbij; het profiel krijgt de lange lijst waarin elk getal
een regel uitleg heeft. De tweede sommen op het profiel (boxes[5] als "stevig", boxes[3]+boxes[4]
als "onderweg") gaan weg: dat waren precies de twee stukken code over hetzelfde getal waar dit
scherm al drie keer op is vastgelopen.

Idempotent: draait hij twee keer, dan doet de tweede keer niets.
"""
import io, sys, os

PAD = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol/index.html")

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

if "function voortgangCijfers()" in src:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    """Vervang anker door nieuw. Faalt hard als het anker niet precies n keer voorkomt."""
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (
        gevonden, n, anker[:160])
    src = src.replace(anker, nieuw, n)


# ---------------------------------------------------------------- 1. de cijferfunctie
rep(
    """  for(k in opweg){ n = niv[k]; if(n) dekw[n]++; }
  return {stevig:stevig, bijna:bijna, geoefend:geoefend, dek:dek, dekw:dekw};
}
""",
    """  for(k in opweg){ n = niv[k]; if(n) dekw[n]++; }
  return {stevig:stevig, bijna:bijna, geoefend:geoefend, dek:dek, dekw:dekw};
}

/* ================= EEN FUNCTIE VOOR ALLE CIJFERS (v23.14) =================
   De valkuil van dit onderwerp, in een zin: elke keer dat het misging, ging het mis doordat er
   twee stukken code over hetzelfde getal bestonden. In v23.0 stond hetzelfde niveau op Vandaag op
   100 procent en op je profiel op 0 procent, allebei zonder te zeggen welk stuk ze maten. En tot
   deze versie noemde het profiel boxes[5] "stevig", terwijl de balk daarboven het aantal Cervantes
   sleutels telde dat een echte check heeft gehad. Twee sommen, een naam.

   Vanaf nu levert deze ene functie de cijfers en roepen alle schermen hem aan. Wil een scherm iets
   anders laten zien, dan kiest het een ander veld uit dit object. Het schrijft geen tweede som.

   Wat er bewust niet in zit is een oordeel. Geen "te makkelijk, precies goed, te uitdagend" bij het
   foutpercentage: die grens zou uit het 85 procent onderzoek moeten komen (Wilson e.a., Nature
   Communications 2019) en dat gaat over leeralgoritmes op binaire classificatie, niet over
   woordenschat. De band hoort uit S.meting te komen, uit Stefans eigen reeks, en die is op 8
   augustus gestart. Tot die tijd staat er een kaal percentage en staat erbij dat de band nog wordt
   opgebouwd. Een geleende grens is een verzonnen grens. */
var MEET_WEKEN = 10;   // zoveel weekmetingen zijn er nodig voordat je eigen reeks iets zegt
function voortgangCijfers(){
  var tel = voortgangTellers();
  var niv = balkNiveau();
  var noem = PCIC_NOEMER[niv] || 0;
  var vast = (tel.dek && tel.dek[niv]) || 0;
  // onderweg is nooit minder dan vast: dekw telt vanaf doos 3, dek vanaf de laatste doos
  var actief = Math.max(vast, (tel.dekw && tel.dekw[niv]) || 0);
  var sch = null;
  try { sch = niveauSchatting(niv); } catch(e){ sch = null; }
  var geschat = sch ? Math.max(0, sch.punt - actief) : 0;
  var kpi = leerKpi();
  var tk = null;
  try { tk = terugkomKpi(); } catch(e){ tk = null; }
  var sw = S.sweep || {}, swN = (sw.goed || 0) + (sw.fout || 0);
  return {
    niv: niv,
    noem: noem,
    vast: vast,                                     // bewezen vast: laatste doos plus een echte check
    onderweg: Math.max(0, actief - vast),           // doos 3 of hoger, nog niet vast
    actief: actief,                                 // de kop op Vandaag: vast plus onderweg
    schat: sch,                                     // null zolang de peiling niets zegt
    geschat: geschat,                               // wat de peiling erbij schat, boven actief
    ongezien: Math.max(0, noem - actief - geschat),
    geoefend: tel.geoefend,                         // elk woord dat ooit in S.srs kwam, loopt alleen op
    stevig: tel.stevig,                             // over alle niveaus, niet alleen dit
    bijna: tel.bijna,
    dek: tel.dek, dekw: tel.dekw,
    fout7: kpi.recent,                              // {pog, fout, pct}, pct is null bij te weinig pogingen
    foutTrend: kpi.trend,
    weken: Object.keys(S.meting || {}).length,
    terugkom: tk,
    dagen: dagenTotaal(),
    // hoe goed schat je jezelf in: uit S.sweep, pas als er tien woorden nagekeken zijn
    zelf: swN >= 10 ? {n:swN, goed:(sw.goed || 0), pct:Math.round(100 * (sw.goed || 0) / swN)} : null
  };
}
""")

# ---------------------------------------------------------------- 2. de balk leest de cijferfunctie
rep(
    """function dagBasisRegelHtml(){
  var t = voortgangTellers();
  var niv = balkNiveau();
  var n = PCIC_NOEMER[niv] || 390;
  var d = (t.dek && t.dek[niv]) || 0;
  var w = Math.max(d, (t.dekw && t.dekw[niv]) || 0);
  var sch = null, aanbod = null;
  try { sch = niveauSchatting(niv); } catch(e){ sch = null; }
  try { aanbod = peilAanbod(); } catch(e){ aanbod = null; }
  if(w <= 0 && !sch && !aanbod) return "";
""",
    """/* v23.14: de getallen komen uit voortgangCijfers(), niet meer uit een eigen som hier. De vorm
   blijft precies zoals hij was. opt.legenda mag op false: op je profiel staat de lange lijst er
   direct onder, en dan zou de legenda dezelfde vier getallen twee keer op een scherm zetten. */
function dagBasisRegelHtml(opt){
  var c = voortgangCijfers();
  var niv = c.niv;
  var n = c.noem || 390;
  var d = c.vast;
  var w = c.actief;
  var sch = c.schat, aanbod = null;
  try { aanbod = peilAanbod(); } catch(e){ aanbod = null; }
  if(w <= 0 && !sch && !aanbod) return "";
""")

LEG_OUD = '''    "<div class='vgLegenda'>"+'''
LEG_NIEUW = '''    ((opt && opt.legenda === false) ? "" :
    "<div class='vgLegenda'>"+'''
rep(LEG_OUD, LEG_NIEUW)

rep(
    """      (lgRest > 0 ? "<span><i class='vgDot vgRest'></i><b>"+lgRest+"</b> "+ct("nog niet gezien","not seen yet")+"</span>" : "")+
    "</div>"+""",
    """      (lgRest > 0 ? "<span><i class='vgDot vgRest'></i><b>"+lgRest+"</b> "+ct("nog niet gezien","not seen yet")+"</span>" : "")+
    "</div>")+""")

# De legenda las in een andere volgorde dan de balk tekende: onderweg eerst, terwijl de balk links
# begint met bewezen vast. Nu lopen ze gelijk, van donker naar grijs, net als in de opdracht.
rep(
    """      "<span><i class='vgDot vgOnderweg'></i><b>"+lgOnderweg+"</b> "+ct("onderweg","on the way")+"</span>"+
      "<span><i class='vgDot vgVast'></i><b>"+d+"</b> "+ct("bewezen vast","proven solid")+"</span>"+""",
    """      "<span><i class='vgDot vgVast'></i><b>"+d+"</b> "+ct("bewezen vast","proven solid")+"</span>"+
      "<span><i class='vgDot vgOnderweg'></i><b>"+lgOnderweg+"</b> "+ct("onderweg","on the way")+"</span>"+""")

# De dode zin over hetzelfde getal
rep(
    """  var kop = pctD, pctS = 0, merk = "", regel, stap = "";
  if(sch){
    kop = Math.round(100 * sch.punt / n);
    pctS = Math.max(0, kop - pctD - pctW);
    var e0 = peilEerste(niv);
    if(e0) merk = "<i class='merk' style='left:"+Math.max(0, Math.min(99, Math.round(100 * e0.punt / n)))+"%'></i>";
    regel = ct("Je kent er naar schatting <b>"+sch.punt+"</b> van de "+n+" "+niv+"-woorden, ergens tussen "+
                 sch.onder+" en "+sch.boven+". Daarvan staan er <b>"+d+"</b> hier vast.",
               "You know an estimated <b>"+sch.punt+"</b> of the "+n+" "+niv+" words, somewhere between "+
                 sch.onder+" and "+sch.boven+". <b>"+d+"</b> of those are solid here.");
    stap = dagBasisStapHtml(niv, sch, d);
  } else {
    regel = ct("<b>"+d+"</b> van de "+n+" "+niv+"-woorden staan stevig"+(w > d ? ", <b>"+(w - d)+"</b> zijn onderweg" : "")+".",
               "<b>"+d+"</b> of the "+n+" "+niv+" words are solid"+(w > d ? ", <b>"+(w - d)+"</b> on the way" : "")+".");
  }
""",
    """  /* v23.14: hier stond ook een variabele "regel" met de zin "je kent er naar schatting X van de
     390". Die zin is er in v23.2 uitgehaald omdat hij hetzelfde getal nog een keer zei, maar de
     twee stukken tekst die hem opbouwden bleven staan. Dood, en juist over dit getal: precies het
     soort restant waar per ongeluk weer een tweede weergave uit groeit. Weg. */
  var kop = pctD, pctS = 0, merk = "", stap = "";
  if(sch){
    kop = Math.round(100 * sch.punt / n);
    pctS = Math.max(0, kop - pctD - pctW);
    var e0 = peilEerste(niv);
    if(e0) merk = "<i class='merk' style='left:"+Math.max(0, Math.min(99, Math.round(100 * e0.punt / n)))+"%'></i>";
    stap = dagBasisStapHtml(niv, sch, d);
  }
""")

# ---------------------------------------------------------------- 3. Vandaag: de twee kerncijfers
rep(
    """/* De stap. Niet als los blokje ergens anders op het scherm, maar als een zin onder dezelfde balk,""",
    """/* ================= DE TWEE KERNCIJFERS OP VANDAAG (v23.14) =================
   Punt 1 van de werklijst. Naast de balk hoort op Vandaag te staan hoeveel woorden je geoefend
   hebt en hoe vaak je fout zit. De geoefend-teller is met opzet de teller die alleen oploopt: dat
   is het enige getal op dit scherm dat nooit tegenvalt, en het meet precies wat jij gedaan hebt.
   Het foutpercentage staat ernaast en meet hoe zwaar het je valt.

   Er hangt geen oordeel aan. Zie de uitleg bij voortgangCijfers(): de grens tussen te makkelijk en
   te uitdagend hoort uit Stefans eigen weekmetingen te komen, en die reeks is net begonnen. Wat er
   wel bij staat is hoe ver die reeks is, zodat het getal niet doet alsof het al iets weet.

   Allebei volgen ze de regel van v20.1: ze verschijnen als ze iets zeggen en anders niet. */
function dagKerncijfersHtml(){
  var c = voortgangCijfers(), tegels = "";
  if(c.geoefend > 0){
    tegels += "<div class='stat'><b>"+c.geoefend+"</b><span class='muted'>"+
      ct("woorden geoefend","words practised")+"</span></div>";
  }
  if(c.fout7.pct !== null){
    tegels += "<div class='stat'><b>"+c.fout7.pct+"%</b><span class='muted'>"+
      ct("fout, laatste 7 dagen","wrong, last 7 days")+"</span></div>";
  }
  if(!tegels) return "";
  return "<div class='statgrid' style='margin-top:10px'>"+tegels+"</div>"+
    (c.fout7.pct === null ? "" :
      "<p class='muted' style='margin:6px 0 0; font-size:.8rem'>"+
        ct(weekMetingZin(c.weken)+" Vanaf ongeveer "+MEET_WEKEN+" kan de app uit je eigen reeks "+
           "aflezen wat voor jou een goede stand is; tot die tijd staat er geen oordeel bij.",
           weekMetingZin(c.weken)+" From about "+MEET_WEKEN+" on the app can read from "+
           "your own series what a good rate is for you; until then no verdict is attached.")+"</p>");
}
// een getal van een is enkelvoud, ook in een zin die je zelden ziet. "Er liggen 1 weekmetingen"
// leest als een sjabloon dat niemand heeft nagelopen, en dan gaat de lezer aan de rest ook twijfelen.
function weekMetingZin(n){
  if(profLang() === "nl") return n === 1 ? "Er ligt 1 weekmeting." : "Er liggen "+n+" weekmetingen.";
  return n === 1 ? "There is 1 weekly measurement." : "There are "+n+" weekly measurements.";
}
/* De stap. Niet als los blokje ergens anders op het scherm, maar als een zin onder dezelfde balk,""")

rep(
    """  var rel = dagRelevantie();
  var basis = rel.basis ? dagBasisRegelHtml() : "";
  if(!basis && !rel.lijn) return "";
  return "<div class='card' id='lijnKaart'>"+basis+""",
    """  var rel = dagRelevantie();
  var basis = rel.basis ? dagBasisRegelHtml() : "";
  // v23.14: de twee kerncijfers horen bij de balk en niet in een eigen kaart. Ze kunnen er ook
  // staan als de balk zwijgt (wie geoefend heeft zonder dat er al iets onderweg is), dus ze zijn
  // een eigen reden om deze kaart te tonen.
  var kern = dagKerncijfersHtml();
  if(!basis && !kern && !rel.lijn) return "";
  return "<div class='card' id='lijnKaart'>"+basis+kern+""")

# ---------------------------------------------------------------- 4. de opmaak van de lange lijst
rep(
    """  .vgDot.vgRest{background:#e8e1d4;}
""",
    """  .vgDot.vgRest{background:#e8e1d4;}
  /* v23.14: de lange lijst op je profiel. Getal links, betekenis rechts, een regel per getal. */
  .cijfLijst{margin-top:4px;}
  .cijfRij{display:flex; gap:12px; align-items:baseline; padding:9px 0; border-bottom:1px solid var(--border);}
  .cijfRij:last-child{border-bottom:0;}
  .cijfW{flex:0 0 92px; text-align:right; font-weight:800; font-size:1.05rem; letter-spacing:-.02em;}
  .cijfT{flex:1; font-size:.92rem; line-height:1.35;}
  .cijfT span{display:block; font-size:.82rem; color:var(--muted); margin-top:2px;}
""")

# ---------------------------------------------------------------- 5. de lange lijst zelf
rep(
    """function renderStats(){""",
    """/* ================= DE LANGE LIJST OP JE PROFIEL (v23.14) =================
   Punt 2 van de werklijst. Stefan wilde op Vandaag een simpel overzicht en op zijn profiel een
   lange lijst met alles in cijfers, met per cijfer een regel wat het betekent. Dat laatste is de
   hele opdracht: een getal zonder die regel is een getal dat je zelf moet uitleggen, en dan legt
   iedereen het anders uit.

   Elk getal hier komt uit voortgangCijfers(). Er wordt in deze functie niets opnieuw uitgerekend.
   Een rij die niets te zeggen heeft staat er niet: dezelfde regel als v20.1.

   Wat hier bewust niet staat: hoe vaak je per week terugkomt en hoeveel dagen je erbij was. Die
   staan een stuk hoger op ditzelfde scherm, bij "Waar je staat". Twee keer hetzelfde getal op een
   scherm maakt allebei de keren ongeloofwaardig. De Cervantes-dekking per niveau staat om dezelfde
   reden onder de vouw "Per niveau", ook daar uit dezelfde tellers. */
function cijferRij(waarde, label, uitleg){
  return "<div class='cijfRij'><div class='cijfW'>"+waarde+"</div>"+
    "<div class='cijfT'>"+label+"<span>"+uitleg+"</span></div></div>";
}
function cijferLijstHtml(){
  var c = voortgangCijfers(), r = "";
  r += cijferRij(c.actief, ct("woorden houd je actief bij op "+c.niv, "words you actively keep up at "+c.niv),
    ct("Dit is het getal dat op Vandaag boven de balk staat: bewezen vast plus onderweg, van de "+
       c.noem+" woorden die het Instituto Cervantes voor "+c.niv+" telt.",
       "This is the number above the bar on Today: proven solid plus on the way, out of the "+
       c.noem+" words the Instituto Cervantes counts for "+c.niv+"."));
  r += cijferRij(c.vast, ct("bewezen vast","proven solid"),
    ct("Vijf goede beurten over vijfentwintig dagen, met een check die je niet zelf beoordeelt. "+
       "Dit getal loopt daardoor achter op wat je kunt, en dat hoort: het meet bewijs, geen gevoel.",
       "Five correct turns across twenty five days, with a check you do not grade yourself. "+
       "So this number lags behind what you can do, and that is right: it measures proof, not feeling."));
  r += cijferRij(c.onderweg, ct("onderweg","on the way"),
    ct("Woorden met een herhaalinterval van een week of langer die nog niet vast staan. Dit is de "+
       "groep die de komende weken naar bewezen vast schuift.",
       "Words with a review interval of a week or more that are not solid yet. This is the group "+
       "moving to proven solid over the coming weeks."));
  if(c.schat){
    r += cijferRij(c.schat.punt, ct("geschat totaal op "+c.niv, "estimated total at "+c.niv),
      ct("Uit je peiling, en dat is een steekproef. Ergens tussen "+c.schat.onder+" en "+c.schat.boven+
         ". De marge hoort erbij: dit is een schatting en geen telling.",
         "From your check, which is a sample. Somewhere between "+c.schat.onder+" and "+c.schat.boven+
         ". The margin belongs to it: this is an estimate and not a count."));
  }
  if(c.ongezien > 0){
    r += cijferRij(c.ongezien, ct("nog niet gezien","not seen yet"),
      ct("Woorden van "+c.niv+" die je hier nog niet bent tegengekomen. Dit getal daalt vanzelf "+
         "zolang je nieuwe woorden blijft krijgen.",
         "Words at "+c.niv+" you have not met here yet. This number drops on its own as long as "+
         "you keep getting new words."));
  }
  r += cijferRij(c.geoefend, ct("woorden ooit geoefend","words practised ever"),
    ct("Elk woord dat je hier ooit hebt aangeraakt. Dit is de enige teller die alleen oploopt, ook "+
       "als een woord daarna weer wegzakt. Hij meet wat jij gedaan hebt, niet wat blijft hangen.",
       "Every word you have ever touched here. This is the only counter that only goes up, even if "+
       "a word slips back later. It measures what you did, not what stuck."));
  if(c.fout7.pct === null){
    r += cijferRij(ct("nog niets","none yet"), ct("fout in de laatste 7 dagen","wrong in the last 7 days"),
      ct("Nog te weinig pogingen om een percentage te tonen. Deze meting telt vanaf 28 juli en niet "+
         "met terugwerkende kracht, want pogingen werden daarvoor niet bijgehouden.",
         "Too few attempts to show a percentage. This measurement counts from 28 July and not "+
         "retroactively, because attempts were not tracked before that."));
  } else {
    var tr = "";
    if(c.foutTrend !== null && c.foutTrend < 0){
      tr = ct(" Dat is "+Math.abs(c.foutTrend)+" procentpunt lager dan de week ervoor.",
              " That is "+Math.abs(c.foutTrend)+" percentage points lower than the week before.");
    } else if(c.foutTrend !== null && c.foutTrend > 0){
      tr = ct(" Dat is "+c.foutTrend+" procentpunt hoger dan de week ervoor.",
              " That is "+c.foutTrend+" percentage points higher than the week before.");
    } else if(c.foutTrend !== null){
      tr = ct(" Gelijk aan de week ervoor."," The same as the week before.");
    }
    r += cijferRij(c.fout7.pct + "%", ct("fout in de laatste 7 dagen","wrong in the last 7 days"),
      ct(c.fout7.fout+" van de "+c.fout7.pog+" pogingen ging fout."+tr+" Er staat geen oordeel bij: "+
         "welke stand voor jou het beste werkt komt uit je eigen weekmetingen. "+weekMetingZin(c.weken)+
         " Daarvan zijn er ongeveer "+MEET_WEKEN+" nodig.",
         c.fout7.fout+" of "+c.fout7.pog+" attempts went wrong."+tr+" No verdict is attached: which "+
         "rate works best for you comes from your own weekly measurements. "+weekMetingZin(c.weken)+
         " About "+MEET_WEKEN+" of those are needed."));
  }
  if(c.zelf){
    r += cijferRij(c.zelf.pct + "%", ct("van je eigen inschatting klopte","of your own judgement was right"),
      ct("Bij de inhaalslag zei je van een hoop woorden dat je ze kende. Van de "+c.zelf.n+" die "+
         "daarna zijn nagekeken had je er "+c.zelf.goed+" goed. Dat is niet je niveau, dat is hoe "+
         "goed je jezelf inschat.",
         "In the catch up round you said you knew a pile of words. Of the "+c.zelf.n+" checked since, "+
         "you got "+c.zelf.goed+" right. That is not your level, that is how well you judge yourself."));
  }
  r += cijferRij(corrStevig()+"/"+corrBereikbaar().length, ct("grammaticaregels stevig","grammar rules solid"),
    ct("Regels uit El Corrector die je vaak genoeg goed hebt toegepast. De noemer is wat er met jouw "+
       "woorden nu te oefenen valt, niet alle regels van het Spaans.",
       "Rules from El Corrector you applied correctly often enough. The denominator is what is "+
       "practisable with your words right now, not all the rules of Spanish."));
  r += cijferRij(Object.keys(S.done).length+"/"+SENTENCES.length, ct("zinnen gehaald","sentences done"),
    ct("Hele zinnen die je goed hebt geschreven. Een zin vraagt meer dan een woord: je moet ook de "+
       "volgorde en de vervoeging kloppend krijgen.",
       "Whole sentences you wrote correctly. A sentence asks more than a word: you also have to get "+
       "the order and the conjugation right."));
  r += cijferRij(Object.keys(S.quiz).length+"/"+QUIZZES.length, ct("toetsjes gemaakt","quizzes taken"),
    ct("Afgeronde toetsjes. Dit zegt iets over hoeveel je hebt afgemaakt, niet over hoeveel je kunt.",
       "Finished quizzes. This says something about how much you completed, not about how much you know."));
  return "<h2 style='margin-top:16px'>"+ct("Alles in cijfers","Every number")+"</h2>"+
    "<p class='muted' style='margin:0 0 4px'>"+
      ct("Elk getal met een regel erbij wat het betekent. Ze komen allemaal uit dezelfde som, dus ze "+
         "kunnen elkaar niet tegenspreken.",
         "Every number with a line on what it means. They all come from the same calculation, so they "+
         "cannot contradict each other.")+"</p>"+
    "<div class='cijfLijst'>"+r+"</div>";
}

function renderStats(){""")

# ---------------------------------------------------------------- 6. de tweede sommen weg
rep(
    """  var zinnenGoed = Object.keys(S.done).length;
  var quizzesDone = Object.keys(S.quiz).length;
  var kpi = leerKpi();
""",
    """""")

rep(
    """  // v19.87: box 5 is stevig (dat is stevigDrempel(), en dat is wat de A1-balk telt),
  // box 3 en 4 zijn onderweg. Hiervoor heette box 3 ook "stevig", waardoor hetzelfde
  // scherm twee verschillende getallen stevig noemde.
  var vast = boxes[5];
  var opweg = boxes[3] + boxes[4];
""",
    """  /* v23.14. Hier stond vast = boxes[5] en opweg = boxes[3] + boxes[4]. Dat was de tweede som:
     boxes[5] telt de laatste doos zonder de echte check eronder, terwijl de balk twee regels
     hoger juist alleen telt wat die check heeft gehad. Hetzelfde woord "stevig", twee uitkomsten,
     op een scherm. Nu komen ze allebei uit voortgangCijfers(), net als de balk. */
  var c = voortgangCijfers();
  var vast = c.stevig;
  var opweg = c.bijna;
""")

rep(
    """      ct("Je bent met <b>"+seen+"</b> woorden bezig geweest: <b>"+vast+"</b> staan stevig, <b>"+opweg+"</b> zijn onderweg.",
         "You've worked on <b>"+seen+"</b> words: <b>"+vast+"</b> are solid, <b>"+opweg+"</b> on their way.")+""",
    """      ct("Je bent met <b>"+c.geoefend+"</b> woorden bezig geweest: <b>"+vast+"</b> staan stevig, <b>"+opweg+"</b> zijn onderweg.",
         "You've worked on <b>"+c.geoefend+"</b> words: <b>"+vast+"</b> are solid, <b>"+opweg+"</b> on their way.")+""")

rep(
    """      (vast === 0 && seen > 0 ?""",
    """      (vast === 0 && c.geoefend > 0 ?""")

rep(
    """  var seen = 0;
  WORDS.forEach(function(w){ var st=S.srs[w.id]; if(st){ seen++; boxes[st.box]++; } });
""",
    """  WORDS.forEach(function(w){ var st=S.srs[w.id]; if(st){ boxes[st.box]++; } });
""")

# ---------------------------------------------------------------- 7. de oude tegels vervangen
rep(
    """  // v19.90: hier stond een liggend streepje als leegwaarde. Weg ermee, en meteen
  // in woorden: een tegel die "nog niets" zegt is duidelijker dan een teken.
  var kpiTegelWaarde = kpi.recent.pct === null ? ct("nog niets","none yet") : kpi.recent.pct + "%";
  var kpiTekst;
  if(kpi.recent.pct === null){
    kpiTekst = ct("Nog te weinig pogingen deze week om een foutpercentage te tonen (deze meting begint te tellen vanaf 28 juli, niet met terugwerkende kracht).",
      "Not enough attempts this week to show an error rate yet (this measurement starts counting from 28 July, not retroactively).");
  } else if(kpi.trend === null){
    kpiTekst = ct("Foutpercentage laatste 7 dagen: <b>"+kpi.recent.pct+"%</b> ("+kpi.recent.fout+" van de "+kpi.recent.pog+" pogingen fout). Nog geen trend te tonen: daarvoor moet de week ervoor ook genoeg pogingen hebben.",
      "Error rate over the last 7 days: <b>"+kpi.recent.pct+"%</b> ("+kpi.recent.fout+" of "+kpi.recent.pog+" attempts wrong). No trend yet: the week before needs enough attempts too.");
  } else {
    var trendTekst = kpi.trend < 0 ? ct("\u2193 "+Math.abs(kpi.trend)+" procentpunt beter dan de week ervoor","\u2193 "+Math.abs(kpi.trend)+" percentage points better than the week before")
      : kpi.trend > 0 ? ct("\u2191 "+kpi.trend+" procentpunt hoger dan de week ervoor","\u2191 "+kpi.trend+" percentage points higher than the week before")
      : ct("gelijk aan de week ervoor","the same as the week before");
    kpiTekst = ct("Foutpercentage laatste 7 dagen: <b>"+kpi.recent.pct+"%</b> ("+kpi.recent.fout+" van de "+kpi.recent.pog+" pogingen fout), ",
                  "Error rate over the last 7 days: <b>"+kpi.recent.pct+"%</b> ("+kpi.recent.fout+" of "+kpi.recent.pog+" attempts wrong), ")+trendTekst+".";
  }
""",
    """  /* v23.14. Hier werd de foutpercentage-tegel en de zin eronder opgebouwd. Allebei staan ze nu in
     de lange lijst, waar het getal ook een regel uitleg krijgt in plaats van alleen een label. */
""")

rep(
    """    "<h2 style='margin-top:16px'>"+ct("Wat je kunt","What you can do")+"</h2>"+
    "<p class='muted' style='margin:0 0 8px'>"+ct("Deze cijfers gaan over Spaans.","These numbers are about Spanish.")+"</p>"+
    "<div class='statgrid'>"+
    "<div class='stat'><b>"+vast+"</b><span class='muted'>"+ct("woorden stevig","words solid")+"</span></div>"+
    "<div class='stat'><b>"+opweg+"</b><span class='muted'>"+ct("woorden onderweg","words on the way")+"</span></div>"+
    "<div class='stat'><b>"+corrStevig()+"/"+corrBereikbaar().length+"</b><span class='muted'>"+ct("grammaticaregels stevig","grammar rules solid")+"</span></div>"+
    "<div class='stat'><b>"+kpiTegelWaarde+"</b><span class='muted'>"+ct("fout (laatste 7 dagen)","wrong (last 7 days)")+"</span></div>"+
    "<div class='stat'><b>"+zinnenGoed+"/"+SENTENCES.length+"</b><span class='muted'>"+ct("zinnen gehaald","sentences done")+"</span></div>"+
    "<div class='stat'><b>"+quizzesDone+"/"+QUIZZES.length+"</b><span class='muted'>"+ct("toetsjes gemaakt","quizzes taken")+"</span></div>"+
    "</div>"+
    "<p class='muted' style='margin-top:6px'>"+kpiTekst+"</p>"+""",
    """    cijferLijstHtml()+""")

# ---------------------------------------------------------------- 8. het profiel zonder dubbele legenda
rep(
    """  return "<h2>"+ct("Waar je staat","Where you are")+"</h2>"+
    dagBasisRegelHtml()+""",
    """  /* v23.14: zonder legenda. Die vier getallen staan een stuk lager op ditzelfde scherm in de
     lange lijst, daar met een regel uitleg erbij. Hier zou het een tweede weergave van dezelfde
     som zijn, en dat is precies wat dit scherm niet meer doet. */
  return "<h2>"+ct("Waar je staat","Where you are")+"</h2>"+
    dagBasisRegelHtml({legenda:false})+""")

# ---------------------------------------------------------------- 9. de inhaalslag wijst naar de lijst
rep(
    """    if(gedaan >= 10){
      var pct = Math.round(100 * (sw.goed || 0) / gedaan);
      html += "<p class='muted' style='margin:6px 0'>"+
        ct("Van de "+gedaan+" al nagekeken woorden had je er <b>"+pct+"%</b> goed. Dat is niet je niveau, dat is hoe goed je jezelf inschat.",
           "Of the "+gedaan+" checked so far you got <b>"+pct+"%</b> right. That's not your level, that's how well you judge yourself.")+"</p>";
    } else {""",
    """    if(gedaan >= 10){
      /* v23.14: het percentage stond hier, en het staat nu in de lange lijst hieronder, waar het
         net als elk ander getal een regel uitleg heeft. Het werd hier ook nog eens apart
         uitgerekend, en dat is de tweede som die dit scherm niet meer mag hebben. */
      html += "<p class='muted' style='margin:6px 0'>"+
        ct("Van de "+gedaan+" al nagekeken woorden staat bij de cijfers hieronder hoe vaak je inschatting klopte.",
           "How often your judgement was right, over the "+gedaan+" checked so far, is with the numbers below.")+"</p>";
    } else {""")

# ---------------------------------------------------------------- 9b. dezelfde zin, twee regels hoger
# Deze stond er al: "Er liggen 1 weekmetingen". Nu er twee regels lager wel enkelvoud staat, is het
# verschil zichtbaar op een scherm, en dan gaat een lezer aan allebei twijfelen.
rep(
    """      ct("Nog niet te zeggen. Er liggen "+gemeten+" weekmetingen; vanaf drie kan hier een strook staan in plaats van een gok. Nog <b>"+nog+"</b> "+(nog === 1 ? "week" : "weken")+" te gaan.",
         "Can't be said yet. There are "+gemeten+" weekly measurements; from three on a band can appear here instead of a guess. <b>"+nog+"</b> more "+(nog === 1 ? "week" : "weeks")+" to go.")+"</p>"+""",
    """      ct("Nog niet te zeggen. "+weekMetingZin(gemeten)+" Vanaf drie kan hier een strook staan in plaats van een gok. Nog <b>"+nog+"</b> "+(nog === 1 ? "week" : "weken")+" te gaan.",
         "Can't be said yet. "+weekMetingZin(gemeten)+" From three on a band can appear here instead of a guess. <b>"+nog+"</b> more "+(nog === 1 ? "week" : "weeks")+" to go.")+"</p>"+""")

# ---------------------------------------------------------------- 10. versie
rep("""var APP_VERSIE = "v23.13";""", """var APP_VERSIE = "v23.14";""")

with io.open(PAD, "w", encoding="utf-8") as f:
    f.write(src)
print("v23.14 toegepast op", PAD)
