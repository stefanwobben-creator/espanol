#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.32: Voortgang wordt een eigen scherm, in de volgorde die Stefan gaf.

Zijn volgorde, letterlijk: je week, je doel, wat je vasthoudt, onderweg, sterke punten, zwakke
plekken, daarna maakt het niet uit.

Het meeste stond er al, alleen op de verkeerde plek en in de verkeerde volgorde. Waar je straks
staat, je doel, de cijferlijst, de herhaalintervallen en sterk/zwak zaten allemaal onder Profiel,
onder je naam, achter een knop die "Alle cijfers" heet. Twee dingen daaraan klopten niet: je
voortgang is geen profielgegeven, en de volgorde was die van de bouwer (eerst de meting, dan de
uitleg, dan pas waar je wat aan hebt).

Wat er nieuw bij komt, en dat is precies wat er nog niet was:

1. Je week. Wat er deze week bij kwam, hoeveel dagen je er was, hoeveel lessen. Het weekbericht is
   in v23.31 van Vandaag afgehaald met de belofte dat het als rapport terug zou komen; dit is dat
   rapport. Delen kan via dezelfde link als altijd.

2. Onderweg. Mijlpalen, uit gegevens die er al zijn: je eerste dag (S.xp), wanneer je de vijftig,
   honderd, tweehonderdvijftig woorden passeerde (de weekmetingen), welk niveau je haalde (het
   peilingslogboek) en hoeveel hoofdstukken je uit hebt. Drie gehaald en twee te gaan, want een
   lijst van vijftien mijlpalen is een takenlijst en geen terugblik.

   Waar geen datum bekend is, staat er geen datum. De hoofdstukken weten niet wanneer ze uit
   gingen (S.boek bewaart alleen dat ze uit zijn), en dan is verzinnen erger dan zwijgen.

Verhuisd, niet gekopieerd. sterkZwakHtml() is uit renderStats gehaald en staat nu als twee losse
blokken bovenaan, en het doel staat compact bij het doelblok in plaats van als alinea onder de
voorspelling. Op je profiel staat nu een regel met een knop erheen: weglaten mag nooit verstoppen
worden.

Een suite erbij: pw-voortgang. En pw-cijferbugs kijkt voortaan op het nieuwe scherm.

Idempotent.
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")
MAP_S = os.path.join(WORTEL, "test", "suites")

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

if "function renderVoortgang" in src:
    print("al toegepast, niets te doen")
    sys.exit(0)
if 'var APP_VERSIE = "v23.31";' not in src:
    print("Deze index.html staat niet op v23.31. Eerst bijtrekken:\n\n    git pull --rebase\n")
    sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:160])
    src = src.replace(anker, nieuw, n)


# ================================================================ 1. opmaak
rep(
    """  /* v23.26: de boekenplank. Een kaart per boek, met de balk die je van Vandaag kent. */""",
    """  /* v23.32: de compacte meetregel van de voortgangspagina. Naam links, balkje, getal rechts.
     Bewust smal: hier staan rijtjes van vijf en die moeten in een oogopslag te vergelijken zijn. */
  .vgMeet{display:grid; grid-template-columns:1fr 84px 62px; align-items:center; gap:10px;
          padding:7px 0; border-top:1px solid var(--border); font-size:.9rem;}
  .vgMeet:first-of-type{border-top:0;}
  .vgMeet .vgStaaf{height:7px; background:#f2eee6; border-radius:4px; overflow:hidden;}
  .vgMeet .vgStaaf i{display:block; height:100%; background:var(--accent); border-radius:4px;}
  .vgMeet .vgStaaf i.zwak{background:var(--red);}
  .vgMeet .vgStaaf i.sterk{background:var(--green);}
  .vgMeet b{text-align:right; font-variant-numeric:tabular-nums;}
  .vgMeet span span{display:block; font-size:.76rem; color:var(--muted);}
  .vgPil{display:inline-block; border:1px solid var(--border); background:#faf7f2; border-radius:999px;
         padding:3px 10px; font-size:.82rem; margin:0 4px 4px 0;}
  .vgPil.aan{background:var(--ink); color:var(--bg); border-color:var(--ink);}
  .vgKoers{display:inline-block; border-radius:999px; padding:2px 10px; font-size:.78rem; font-weight:700;}
  .vgKoers.ja{background:var(--green-soft); color:var(--green);}
  .vgKoers.nee{background:var(--amber-soft); color:var(--amber);}
  .vgMijl{display:flex; gap:10px; padding:8px 0; border-top:1px solid var(--border);}
  .vgMijl:first-of-type{border-top:0;}
  .vgBol{width:26px; height:26px; border-radius:50%; background:var(--accent-soft); color:var(--accent);
         display:flex; align-items:center; justify-content:center; flex:0 0 26px; font-size:.9rem;}
  .vgBol.uit{background:#f2eee6; color:var(--muted);}
  /* v23.26: de boekenplank. Een kaart per boek, met de balk die je van Vandaag kent. */""")

# ================================================================ 2. het scherm
rep(
    """  <section id="tab-cursus" class="hidden">
    <div id="cursusCard"></div>
  </section>""",
    """  <section id="tab-cursus" class="hidden">
    <div id="cursusCard"></div>
  </section>

  <!-- v23.32: Voortgang is een eigen scherm geworden. Het stond onder Profiel, achter je naam, en
       je voortgang is geen profielgegeven. De volgorde van de blokken is die van Stefan: je week,
       je doel, wat je vasthoudt, onderweg, sterk, zwak, en daarna de rest. -->
  <section id="tab-voortgang" class="hidden">
    <div id="voortgangCard"></div>
    <div class="card" id="statsCard"></div>
  </section>""")

rep(
    """  <section id="tab-perfil" class="hidden">
    <div class="card" id="perfilCard"></div>
    <div class="card" id="statsCard"></div>""",
    """  <section id="tab-perfil" class="hidden">
    <div class="card" id="perfilCard"></div>
    <div class="card" id="perfNaarVoortgang"></div>""")

rep(
    """  {id:"cursus", label:"Cursus"},   // v19.90: de leerlijn, weg bij het profiel vandaan""",
    """  {id:"cursus", label:"Cursus"},   // v19.90: de leerlijn, weg bij het profiel vandaan
  {id:"voortgang", label:"Voortgang", nav:false},   // v23.32: eigen scherm, weg bij het profiel vandaan""")

# Voortgang hoort ook in het Meer-menu. Niet alleen omdat pw-v1998 eist dat elke tab via de balk of
# via Meer te bereiken is (die eis is terecht en hij sloeg meteen aan), maar omdat de omschrijving bij
# Profiel niet meer klopte: daar staat je voortgang niet meer.
rep(
    """  cursus:{nl:"Cursus",en:"Course",fr:"Cours",de:"Kurs"},""",
    """  cursus:{nl:"Cursus",en:"Course",fr:"Cours",de:"Kurs"},
  voortgang:{nl:"Voortgang",en:"Progress",fr:"Progr\u00e8s",de:"Fortschritt"},""")

rep(
    """    {id:"perfil", ico:"\\uD83D\\uDC64", uit:ct("Je voortgang, je instellingen en wisselen van profiel.",
      "Your progress, your settings and switching profiles.")}""",
    """    /* v23.32: Voortgang staat hier als eigen regel. Niet alleen omdat pw-v1998 eist dat elke tab
       via de balk of via Meer te bereiken is (die eis is terecht), maar omdat de omschrijving bij
       Profiel niet meer klopte: daar staat je voortgang niet meer. */
    {id:"voortgang", ico:"\\uD83D\\uDCC8", uit:ct("Je week, je doel en waar je staat.",
      "Your week, your goal and where you are.")},
    {id:"perfil", ico:"\\uD83D\\uDC64", uit:ct("Je instellingen en wisselen van profiel.",
      "Your settings and switching profiles.")}""")

rep(
    """  if(tabId==="cursus"){ renderCursus(); }""",
    """  if(tabId==="cursus"){ renderCursus(); }
  if(tabId==="voortgang"){ renderVoortgang(); }""")

# ================================================================ 3. de blokken
rep(
    """function renderCompetenties(){""",
    """/* ================= DE VOORTGANGSPAGINA (v23.32) =================
   Zes blokken in de volgorde die Stefan gaf, en daarna wat er al stond. De volgorde is niet
   willekeurig: hij begint bij de week die net voorbij is (dat is het stuk dat je meteen snapt),
   dan waar je heen wilt, dan waar je staat, en pas daarna de uitsplitsingen.

   Alle getallen komen uit functies die er al waren. Er wordt hier niets opnieuw uitgerekend, en dat
   is de enige reden dat dit scherm te vertrouwen is: een tweede telling naast voortgangCijfers()
   was elke keer de oorzaak als er twee getallen over hetzelfde ding op het scherm stonden. */
function vgSomDek(m, nivs){
  var s = 0, i;
  for(i = 0; i < nivs.length; i++) s += ((m && m.dek) || {})[nivs[i]] || 0;
  return s;
}
// De weekmetingen op volgorde, met het bewezen deel opgeteld over de niveaus van je balk.
function vgWeken(nivs){
  var ws = Object.keys(S.meting || {}).sort(), uit = [], i, m;
  for(i = 0; i < ws.length; i++){
    m = S.meting[ws[i]];
    if(!m) continue;
    uit.push({week:ws[i], d:m.d, vast:vgSomDek(m, nivs), geoefend:m.geoefend || 0,
              pog:m.pog || 0, fout:m.fout || 0});
  }
  return uit;
}
function vgRij(naam, sub, pct, cijf, soort){
  return "<div class='vgMeet'><span>"+naam+(sub ? "<span>"+sub+"</span>" : "")+"</span>"+
    "<span class='vgStaaf'><i class='"+(soort || "")+"' style='width:"+
      Math.max(2, Math.min(100, pct))+"%'></i></span><b>"+cijf+"</b></div>";
}

/* ---------- 1. Je week ---------- */
function vgWeekHtml(c){
  var t = today(), i, d, dagen = 0;
  for(i = 0; i < 7; i++){ d = addDays(t, -i); if((S.xp || {})[d] > 0) dagen++; }
  var wk = vgWeken(c.samen.nivs);
  var groei = wk.length > 1 ? wk[wk.length-1].vast - wk[wk.length-2].vast : null;
  var lessen = afgemaakt7(), tv = tijdVenster(7);
  var h = "<div class='card'><span class='kicker'>"+ct("Je week","Your week")+" \\ud83d\\udc40</span>";
  /* De kop is de aanwas en niet de stand. De stand loopt altijd op, dus die kan niet zeggen of dit
     een goede week was; de aanwas wel. Zonder tweede weekmeting staat er geen aanwas, want een
     verschil met niets is geen verschil. */
  if(groei === null){
    h += "<p style='margin:0 0 6px'>"+ct("Je eerste weekmeting staat er. Vanaf de volgende staat hier "+
      "hoeveel er die week bij kwam.","Your first weekly measurement is in. From the next one on, this "+
      "shows how much came in that week.")+"</p>";
  } else {
    h += "<div class='vgKop'><div class='vgGroot'>"+(groei >= 0 ? "+" : "")+groei+"</div>"+
      "<div class='vgBij'>"+ct("woorden erbij deze week","words added this week")+"</div></div>";
  }
  h += "<div class='statgrid' style='margin-top:8px'>"+
    "<div class='stat'><b>"+dagen+"/7</b><span class='muted'>"+ct("dagen geoefend","days practised")+"</span></div>"+
    "<div class='stat'><b>"+lessen+"</b><span class='muted'>"+ct("lessen afgemaakt","sessions finished")+"</span></div>"+
    "</div>";
  var los = [];
  los.push("\\ud83d\\udd25 " + streakNow() + " " + ct("dagen op rij","days in a row"));
  if(tv.perDag !== null) los.push(tv.perDag + " " + ct("minuten per dag","minutes a day"));
  if(c.fout7.pct !== null) los.push(c.fout7.pct + "% " + ct("fout","wrong"));
  h += "<p class='muted' style='margin:8px 0 0; font-size:.86rem'>"+los.join(" \\u00b7 ")+"</p>";
  /* Delen gaat via de link die er al is. Geen tweede deelweg erbij: die link laat precies vijf
     getallen zien en niets anders, en dat is een belofte die we niet per scherm opnieuw moeten
     uitvinden. */
  h += "<div class='row' style='margin-top:10px'>"+
    (maatjeAan()
      ? "<button class='primary' id='btnVgWeekDeel'>"+ct("Stuur je week \\ud83d\\udd17","Send your week \\ud83d\\udd17")+"</button>"
      : "<button class='ghost' id='btnVgWeekMaatje'>"+ct("Iemand laten meekijken \\ud83d\\udc40","Let someone follow along \\ud83d\\udc40")+"</button>")+
    "</div></div>";
  return h;
}

/* ---------- 2. Je doel ---------- */
function vgDoelHtml(){
  var mi = doelMinuten(), ds = doelStand();
  var h = "<div class='card'><span class='kicker'>"+ct("Je doel","Your goal")+"</span><p style='margin:0 0 6px'>"+
    "<span class='vgPil aan'>"+mi+" "+ct("min per dag","min a day")+"</span>";
  if(ds) h += "<span class='vgPil aan'>"+ds.niv+" "+ct("vol","full")+"</span>"+
              "<span class='vgPil aan'>"+datumUit(ds.datum)+"</span>";
  h += "<span class='vgPil' id='btnVgDoel' style='cursor:pointer'>"+ct("wijzigen","change")+"</span></p>";
  if(!ds){
    h += "<p class='muted' style='margin:0; font-size:.86rem'>"+
      ct("Je hebt nog geen niveaudoel. Het stuurt niets aan; het geeft de app iets om je gemeten tempo "+
         "naast te leggen.",
         "You have no level goal yet. It drives nothing; it gives the app something to hold your "+
         "measured pace against.")+"</p></div>";
    return h;
  }
  if(ds.klaar){
    h += "<p style='margin:0'>"+"<span class='vgKoers ja'>"+ct("gehaald","reached")+"</span> "+
      ct(ds.niv+" staat vol.", ds.niv+" is full.")+"</p></div>";
    return h;
  }
  h += "<div class='statgrid' style='grid-template-columns:1fr 1fr 1fr; margin-top:8px'>"+
    "<div class='stat'><b>"+(ds.nodig === null ? "\\u2013" : getal1(ds.nodig))+"</b><span class='muted'>"+
      ct("per week nodig","a week needed")+"</span></div>"+
    "<div class='stat'><b>"+(ds.tempo === null ? "\\u2013" : getal1(ds.tempo))+"</b><span class='muted'>"+
      ct("haal je nu","you're doing")+"</span></div>"+
    "<div class='stat'><b>"+Math.max(0, ds.weken)+"</b><span class='muted'>"+
      ct("weken te gaan","weeks to go")+"</span></div></div>";
  if(ds.tempo === null){
    h += "<p class='muted' style='margin:8px 0 0; font-size:.86rem'>"+
      ct("Wat je nu haalt is nog niet te meten; daar zijn drie weekmetingen voor nodig.",
         "What you're doing isn't measurable yet; that needs three weekly measurements.")+"</p>";
  } else if(ds.nodig !== null && ds.tempo >= ds.nodig){
    h += "<p style='margin:8px 0 0; font-size:.9rem'><span class='vgKoers ja'>"+ct("op koers","on track")+
      "</span> "+ct("In dit tempo ben je er op tijd.","At this pace you'll get there in time.")+"</p>";
  } else {
    /* Geen rood. Stefan, v19.90: een deadline die je mist is een indicator die liegt. Het doel is
       een richting, en het getal dat telt blijft hoe vaak je terugkomt. */
    h += "<p style='margin:8px 0 0; font-size:.9rem'><span class='vgKoers nee'>"+ct("later","later")+
      "</span> "+ct("In dit tempo wordt het later dan je datum. Dat is geen fout; een doel is hier een "+
                    "richting.",
                    "At this pace it'll be later than your date. That's not a failure; a goal here is "+
                    "a direction.")+"</p>";
  }
  return h + "</div>";
}

/* ---------- 3. Wat je vasthoudt ---------- */
function vgLijnHtml(c){
  var wk = vgWeken(c.samen.nivs);
  if(wk.length < 2) return "";
  /* De schaal loopt tot je eigen hoogste punt en niet tot de noemer. Eerst deed hij dat wel, en dan
     plakt een reeks van 20 naar 54 als een streep tegen de bodem: een groeigrafiek die geen groei
     laat zien. De noemer staat een regel hoger al in de balk; deze lijn beantwoordt een andere
     vraag, namelijk of het de goede kant op gaat. Het hoogste getal staat erbij, anders is een
     eigen schaal een truc. */
  var top = 0, i, x, y, d = "", pad = "";
  for(i = 0; i < wk.length; i++) top = Math.max(top, wk[i].vast);
  if(top <= 0) return "";
  top = Math.ceil(top * 1.15);
  var W = 600, H = 130, L = 8, R = 8, T = 10, B = 18;
  for(i = 0; i < wk.length; i++){
    x = L + (W - L - R) * (i / (wk.length - 1));
    y = T + (H - T - B) * (1 - wk[i].vast / top);
    d += (i ? " L " : "M ") + Math.round(x) + " " + Math.round(y);
    pad += (i ? " L " : "M ") + Math.round(x) + " " + Math.round(y);
  }
  pad += " L " + (W - R) + " " + (H - B) + " L " + L + " " + (H - B) + " Z";
  return "<svg viewBox='0 0 "+W+" "+H+"' style='width:100%; height:auto; display:block; margin:10px 0 2px'>"+
    "<path d='"+pad+"' fill='var(--accent-soft)'></path>"+
    "<path d='"+d+"' fill='none' stroke='var(--accent)' stroke-width='2.5'></path>"+
    "<circle cx='"+Math.round(W - R)+"' cy='"+Math.round(T + (H-T-B) * (1 - wk[wk.length-1].vast/top))+
      "' r='4' fill='var(--accent)'></circle>"+
    "</svg>"+
    "<p class='muted' style='margin:0; font-size:.8rem'>"+
      ct("Bewezen vast, van <b>"+wk[0].vast+"</b> op "+datumUit(wk[0].d)+" naar <b>"+
         wk[wk.length-1].vast+"</b> nu, over "+wk.length+" weekmetingen.",
         "Proven solid, from <b>"+wk[0].vast+"</b> on "+datumUit(wk[0].d)+" to <b>"+
         wk[wk.length-1].vast+"</b> now, across "+wk.length+" weekly measurements.")+"</p>";
}

/* ---------- 4. Onderweg ---------- */
/* Mijlpalen uit gegevens die er al zijn. Waar geen datum bekend is staat er geen datum: S.boek
   bewaart alleen dát een hoofdstuk uit is, niet wanneer, en dan is verzinnen erger dan zwijgen. */
function vgMijlpalen(c){
  var uit = [], wk = vgWeken(c.samen.nivs), i, j, drempels = [50, 100, 250, 500, 812];
  var dagen = Object.keys(S.xp || {}).filter(function(x){ return S.xp[x] > 0; }).sort();
  if(dagen.length) uit.push({e:"\\ud83c\\udf31", t:ct("Je eerste dag","Your first day"),
                             d:datumUit(dagen[0]), dsort:dagen[0], aan:true});
  for(i = 0; i < drempels.length; i++){
    var dr = drempels[i], gevonden = null;
    for(j = 0; j < wk.length; j++){ if(wk[j].vast >= dr){ gevonden = wk[j]; break; } }
    if(gevonden){
      uit.push({e:"\\ud83d\\udcaf", t:ct(dr+" woorden bewezen vast", dr+" words proven solid"),
                d:datumUit(gevonden.d), dsort:gevonden.d, aan:true});
    } else if(c.samen.vast < dr){
      uit.push({e:"\\ud83c\\udfaf", t:ct(dr+" woorden bewezen vast", dr+" words proven solid"),
                d:ct("nog "+(dr - c.samen.vast)+" te gaan", (dr - c.samen.vast)+" to go"),
                aan:false});
      break;
    }
  }
  var lg = (S.peil && S.peil.log) || [];
  for(i = 0; i < lg.length; i++){
    if(lg[i] && lg[i].punt / (PCIC_NOEMER[lg[i].niv] || 1) >= POORT_PCT){
      uit.push({e:"\\ud83c\\udfc5", t:ct(lg[i].niv+" gehaald", lg[i].niv+" reached"),
                d:datumUit(lg[i].d), dsort:lg[i].d, aan:true});
      break;
    }
  }
  var af = BOOK.filter(function(h){ return S.boek[h.id] && S.boek[h.id].done; }).length;
  if(af > 0) uit.push({e:"\\ud83d\\udcd6", t:ct(af+" "+(af === 1 ? "hoofdstuk" : "hoofdstukken")+" uit",
                                                af+" "+(af === 1 ? "chapter" : "chapters")+" read"),
                       d:"", aan:true});
  if(af < BOOK.length){
    uit.push({e:"\\ud83d\\udcda", t:ct("Een boek uit","A whole book"),
              d:ct("nog "+(BOOK.length - af)+" hoofdstukken", (BOOK.length - af)+" chapters to go"),
              aan:false});
  }
  return uit;
}
function vgOnderwegHtml(c){
  var mp = vgMijlpalen(c);
  if(!mp.length) return "";
  /* Op datum, niet op de volgorde waarin ik ze toevallig opzocht. Bij het bouwen stond "A1 gehaald
     11 juli" onder "50 woorden vast 3 augustus", en een terugblik die door elkaar loopt is geen
     terugblik. Wat geen datum heeft gaat achteraan. */
  var gehaald = mp.filter(function(m){ return m.aan; }).sort(function(a, b){
    if(!a.dsort) return 1;
    if(!b.dsort) return -1;
    return a.dsort < b.dsort ? -1 : 1;
  });
  var open = mp.filter(function(m){ return !m.aan; }).slice(0, 2);
  /* Drie gehaald en twee te gaan. Een lijst van vijftien mijlpalen is een takenlijst en geen
     terugblik, en dan lees je hem één keer en daarna nooit meer. */
  var toon = gehaald.slice(-3).concat(open);
  return "<div class='card'><span class='kicker'>"+ct("Onderweg","Along the way")+"</span>"+
    toon.map(function(m){
      return "<div class='vgMijl'><div class='vgBol"+(m.aan ? "" : " uit")+"'>"+m.e+"</div>"+
        "<div><b"+(m.aan ? "" : " class='muted'")+">"+m.t+"</b>"+
        (m.d ? "<br><span class='muted' style='font-size:.84rem'>"+m.d+"</span>" : "")+"</div></div>";
    }).join("")+"</div>";
}

/* ---------- 5 en 6. Sterke punten en zwakke plekken ---------- */
/* Stond als één blok onderaan renderStats, met de sterke kant eerst. Nu twee kaarten, want Stefan
   zette ze in zijn volgorde ook los neer, en omdat je een zwakke plek pas gaat oefenen als hij niet
   tussen goed nieuws staat. De telling is niet veranderd: zwakkePunten() doet hem nog steeds. */
/* Een sterk punt moet ook echt sterk zijn. Bij het bouwen stond hier "sterke punten: 23%, 0%, 0%",
   want de lijst nam gewoon de bovenste drie van wat er was. Drie nullen onder het kopje sterk is
   geen bemoediging maar een leugen, en precies het soort getal waardoor je de rest van het scherm
   ook niet meer gelooft. Dus een drempel: minstens de helft van de weg naar het maanddoosje, en
   minstens twee thema's die dat halen, anders staat de kaart er niet. */
var VG_STERK = 50;
function vgSterkHtml(){
  var z = zwakkePunten();
  var sterk = z.themas.filter(function(x){ return x.kracht >= VG_STERK; }).slice(-3).reverse();
  if(sterk.length < 2) return "";
  return "<div class='card'><span class='kicker'>"+ct("Sterke punten","Strong points")+"</span>"+
    sterk.map(function(x){
      return vgRij(x.naam, ct(x.gehad+" van de "+x.n+" woorden gehad", x.gehad+" of "+x.n+" words seen"),
                   x.kracht, x.kracht+"%", "sterk");
    }).join("")+
    "<p class='muted' style='margin:8px 0 0; font-size:.8rem'>"+
      ct("Deze hoef je even niet te doen. Dat is ook informatie.",
         "You can leave these alone for now. That's information too.")+"</p></div>";
}
function vgZwakHtml(){
  var z = zwakkePunten();
  var h = "";
  /* Alleen thema's waar je aan begonnen bent. Een thema dat je nooit zag staat op nul procent en
     kwam daardoor bovenaan de zwakke plekken te staan, terwijl er niets zwaks aan is: je bent er
     gewoon nog niet geweest. Dat is een aanbod, geen tekort, en het staat al op Vandaag als nieuwe
     woorden. Drie gehad is de ondergrens: daaronder meet je ruis. */
  var aangeraakt = z.themas.filter(function(x){ return x.gehad >= 3; });
  if(aangeraakt.length >= 3){
    h += aangeraakt.slice(0, 3).map(function(x){
      return vgRij(x.naam, ct(x.gehad+" van de "+x.n+" woorden gehad", x.gehad+" of "+x.n+" words seen"),
                   x.kracht, x.kracht+"%", "zwak");
    }).join("");
  }
  var wankel = z.regels.filter(function(x){ return x.kracht < 60; });
  if(wankel.length >= 2){
    h += wankel.slice(0, 3).map(function(x){
      return vgRij(x.naam, ct(x.fout+" fout van "+x.beurten+" beurten", x.fout+" wrong of "+x.beurten+" turns"),
                   x.kracht, x.kracht+"%", "zwak");
    }).join("");
  }
  /* Eerst de regels bouwen, dan pas de kaart. Andersom stond er een kaart met alleen een kopje en
     een alinea uitleg over een lijst die er niet was, en dat is de leegste vorm van iets beloven. */
  if(!h) return "";
  return "<div class='card'><span class='kicker'>"+ct("Zwakke plekken","Weak spots")+"</span>"+h+
    "<p class='muted' style='margin:8px 0 0; font-size:.8rem'>"+
    ct("Van alle woorden die dit thema op jouw niveau heeft: hoe ver ze in de doosjes staan. Woorden "+
       "die je nooit zag tellen voor nul. Niet op fouten geteld, want een thema dat je vaak oefent "+
       "verzamelt vanzelf de meeste fouten.",
       "Of all the words this topic has at your level: how far they sit in the boxes. Words you never "+
       "saw count as zero. Not counted on mistakes: a topic you practise a lot collects the most.")+
    "</p></div>";
}

function renderVoortgang(){
  var c = voortgangCijfers();
  var el = document.getElementById("voortgangCard");
  el.innerHTML =
    vgWeekHtml(c) +
    vgDoelHtml() +
    "<div class='card' id='vgVastKaart'>"+dagBasisRegelHtml({legenda:true})+vgLijnHtml(c)+"</div>" +
    vgOnderwegHtml(c) +
    vgSterkHtml() +
    vgZwakHtml();
  var bd = document.getElementById("btnVgWeekDeel");
  if(bd) bd.onclick = function(){ maatjeDeel("voortgang"); };
  var bm = document.getElementById("btnVgWeekMaatje");
  if(bm) bm.onclick = function(){ show("perfil"); };
  var bg = document.getElementById("btnVgDoel");
  if(bg) bg.onclick = function(){ show("perfil"); };
  renderStats();
}

function renderCompetenties(){""")

# ================================================================ 4. wat er al stond
rep(
    """  el.innerHTML = koersHtml + voorspelHtml() +
    cijferLijstHtml()+""",
    """  /* v23.32: sterkZwakHtml() staat hier niet meer. Hij is als twee losse kaarten naar boven
     verhuisd, in de volgorde die Stefan gaf. Verhuisd en niet gekopieerd: de telling zit nog steeds
     in zwakkePunten() en die is niet aangeraakt. */
  el.innerHTML = koersHtml + voorspelHtml() +
    cijferLijstHtml()+""")

rep(
    """    krachtTabelHtml()+
    sterkZwakHtml()+""",
    """    krachtTabelHtml()+""")

# de knop op Vandaag wijst naar het nieuwe scherm
rep(
    """  var bl = document.getElementById("btnLijnMeer");
  if(bl) bl.onclick = function(){ show("perfil"); };""",
    """  var bl = document.getElementById("btnLijnMeer");
  // v23.32: naar het voortgangsscherm, niet meer naar je profiel
  if(bl) bl.onclick = function(){ show("voortgang"); };""")

# en op je profiel staat de weg erheen
rep(
    """  if(tabId==="perfil"){
    // v19.71: wie zijn profiel opent komt kijken hoe het gaat, niet hoe het is ingesteld.
    // De lade gaat dus dicht bij binnenkomst, maar niet bij een hertekening terwijl je erin bezig bent.
    instelOpen = false;
    renderPerfil(); renderStats();""",
    """  if(tabId==="perfil"){
    // v19.71: wie zijn profiel opent komt kijken hoe het gaat, niet hoe het is ingesteld.
    // De lade gaat dus dicht bij binnenkomst, maar niet bij een hertekening terwijl je erin bezig bent.
    instelOpen = false;
    renderPerfil();
    /* v23.32: de cijfers zijn naar hun eigen scherm verhuisd. Hier staat de weg erheen, want
       weglaten mag nooit verstoppen worden. */
    var pnv = document.getElementById("perfNaarVoortgang");
    if(pnv){
      pnv.innerHTML = "<h2 style='margin:0 0 4px'>"+ct("Je voortgang","Your progress")+"</h2>"+
        "<p class='muted' style='margin:0 0 8px; font-size:.9rem'>"+
          ct("Je week, je doel, wat je vasthoudt en waar je zwakke plekken zitten staan op hun eigen "+
             "scherm.",
             "Your week, your goal, what you're holding on to and where the gaps are live on their "+
             "own screen.")+"</p>"+
        "<div class='row'><button class='primary' id='btnNaarVoortgang'>"+
          ct("Bekijk je voortgang","See your progress")+" \\u2192</button></div>";
      var bnv = document.getElementById("btnNaarVoortgang");
      if(bnv) bnv.onclick = function(){ show("voortgang"); };
    }""")

rep('var APP_VERSIE = "v23.31";', 'var APP_VERSIE = "v23.32";')

with io.open(PAD, "w", encoding="utf-8") as f:
    f.write(src)
with io.open(PAD_VER, "w", encoding="utf-8") as f:
    f.write("v23.32\n")
print("v23.32 toegepast op", PAD)

# ================================================================ 5. de suites
pad_cb = os.path.join(MAP_S, "pw-cijferbugs.js")
with io.open(pad_cb, encoding="utf-8") as f:
    cb = f.read()
if "v23.32" in cb:
    print("  pw-cijferbugs.js: al bijgewerkt")
else:
    aantal = cb.count("try { show('perfil'); } catch (e) {}")
    assert aantal == 1, "pw-cijferbugs: anker komt %d keer voor" % aantal
    cb = cb.replace("try { show('perfil'); } catch (e) {}",
                    "// v23.32: de cijfers staan op hun eigen scherm, niet meer onder Profiel\n"
                    "    try { show('voortgang'); } catch (e) {}", 1)
    aantal = cb.count("const tekst = await page.evaluate(() => (document.getElementById('statsCard') || {}).innerText || '');")
    assert aantal == 1, "pw-cijferbugs: tweede anker komt %d keer voor" % aantal
    cb = cb.replace("const tekst = await page.evaluate(() => (document.getElementById('statsCard') || {}).innerText || '');",
                    "const tekst = await page.evaluate(() => {\n"
                    "    try { show('voortgang'); } catch (e) {}\n"
                    "    return (document.getElementById('statsCard') || {}).innerText || '';\n"
                    "  });", 1)
    with io.open(pad_cb, "w", encoding="utf-8") as f:
        f.write(cb)
    print("  pw-cijferbugs.js: bijgewerkt")

SUITE = r'''// v23.32: Voortgang is een eigen scherm, in de volgorde die Stefan gaf.
//
// Wat deze suite vastlegt, en waarom precies dit:
//   - de zes blokken staan er, in zijn volgorde. Een volgorde die niemand bewaakt is een volgorde
//     die bij de volgende versie omvalt, en dan is het weer het scherm van de bouwer.
//   - de cijfers op dit scherm komen uit voortgangCijfers(). Dat is de hele afspraak van dit
//     hoofdstuk: één functie levert de getallen, alle schermen roepen hem aan.
//   - wat hier weg is bij Profiel, is daar niet verstopt maar staat er met een knop erheen.
//   - sterk en zwak staan hier één keer, niet ook nog onderaan bij de cijfers.
const { chromium } = require('playwright');
let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }
const U = 'http://localhost:8321/espanol-stefan.html';

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 420, height: 900 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));

  await page.goto(U); await page.waitForTimeout(300);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.goto(U); await page.waitForTimeout(700);
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'Voort' + Date.now());
  await page.click('button:has-text("A1 ·")');
  await page.click('#btnNewProf');
  await page.waitForTimeout(900);
  await page.evaluate(() => {
    S.lang = 'nl'; S.tour = true;
    try { persist(); } catch (e) {}
    const w = document.getElementById('tourWrap'); if (w && w.remove) w.remove();
  });

  // een profiel met genoeg geschiedenis om alle blokken iets te laten zeggen
  await page.evaluate(() => {
    const map = pcicMap(), niv = pcicNiv();
    const a1 = Object.keys(map).filter((k) => (map[k] || []).some((s) => niv[s] === 'A1'));
    a1.slice(0, 120).forEach((k) => { S.srs[k] = { box: 5, k: 1, due: addDays(today(), 30), n: 9 }; });
    a1.slice(120, 200).forEach((k) => { S.srs[k] = { box: 3, due: addDays(today(), 3), n: 3 }; });
    /* Sterk en zwak gaan over thema's, en die hangen aan de tag van een leswoord. Zonder dit stukje
       heeft dit profiel wel Cervantes-sleutels maar geen thema's, en dan staan blok 5 en 6 er
       terecht niet. Twee tags helemaal vast, twee tags net begonnen: dat is precies het verschil dat
       die twee kaarten horen te laten zien. */
    const perKey = {};
    WORDS.forEach((w) => {
      if (!themaMeetelt(w.tag)) return;
      const k = themaSleutel(w.tag);
      (perKey[k] = perKey[k] || []).push(w);
    });
    // op tag groeperen werkt niet: de tag van een woord en de sleutel van een thema zijn niet
    // hetzelfde, en "familie" komt als tag wel voor maar als thema niet
    const keys = Object.keys(perKey).filter((k) => perKey[k].length >= 8);
    keys.slice(0, 2).forEach((k) => perKey[k].forEach((w) => {
      S.srs[w.id] = { box: 5, k: 1, due: addDays(today(), 30), n: 9 };
    }));
    keys.slice(2, 4).forEach((k) => perKey[k].forEach((w) => {
      S.srs[w.id] = { box: 1, due: addDays(today(), 1), n: 1 };
    }));
    const t = today();
    for (let i = 0; i < 10; i++) S.xp[addDays(t, -i)] = 20;
    for (let i = 0; i < 5; i++) S.lesFlow[addDays(t, -i)] = true;
    S.meting = {
      '2026-W30': { d: addDays(t, -21), dek: { A1: 40 }, stevig: 40, geoefend: 90, pog: 200, fout: 60 },
      '2026-W31': { d: addDays(t, -14), dek: { A1: 78 }, stevig: 78, geoefend: 150, pog: 220, fout: 55 },
      '2026-W32': { d: addDays(t, -7), dek: { A1: 120 }, stevig: 120, geoefend: 200, pog: 240, fout: 50 }
    };
    try { persist(); } catch (e) {}
  });

  console.log('\n-- het scherm bestaat en is bereikbaar vanaf Vandaag --');
  await page.evaluate(() => { scopeLesson = null; show('lessen'); });
  await page.waitForTimeout(400);
  const knop = await page.evaluate(() => !!document.getElementById('btnLijnMeer'));
  ok(knop, 'op Vandaag staat de knop naar je cijfers');
  await page.evaluate(() => { document.getElementById('btnLijnMeer').click(); });
  await page.waitForTimeout(500);
  const open = await page.evaluate(() => ({
    zichtbaar: !document.getElementById('tab-voortgang').classList.contains('hidden'),
    profiel: !document.getElementById('tab-perfil').classList.contains('hidden')
  }));
  ok(open.zichtbaar, 'de knop brengt je op het voortgangsscherm');
  ok(!open.profiel, 'en niet meer op je profiel');

  console.log('\n-- de zes blokken staan in Stefans volgorde --');
  const volgorde = await page.evaluate(() => {
    const kop = [...document.querySelectorAll('#voortgangCard .kicker')].map((k) => k.innerText.trim());
    return kop;
  });
  const wil = ['Je week', 'Je doel', 'Waar je staat', 'Onderweg', 'Sterke punten', 'Zwakke plekken'];
  // de kickers staan in kapitalen op het scherm (text-transform), dus vergelijken zonder hoofdletters
  wil.forEach((w, i) => {
    ok((volgorde[i] || '').toLowerCase().indexOf(w.toLowerCase()) === 0,
      'blok ' + (i + 1) + ' is "' + w + '" (' + (volgorde[i] || 'niets') + ')');
  });

  console.log('\n-- de getallen komen uit voortgangCijfers --');
  const cijf = await page.evaluate(() => {
    const c = voortgangCijfers();
    const kaart = document.getElementById('vgVastKaart');
    return { samen: JSON.parse(JSON.stringify(c.samen)),
             tekst: (kaart ? kaart.innerText : '').replace(/\s+/g, ' ') };
  });
  ok(cijf.tekst.indexOf(String(cijf.samen.actief)) !== -1,
    'wat je actief bijhoudt staat er (' + cijf.samen.actief + ')');
  ok(cijf.tekst.indexOf(String(cijf.samen.noem)) !== -1,
    'en de noemer erbij (' + cijf.samen.noem + ')');

  console.log('\n-- je week rekent met het verschil, niet met de stand --');
  const week = await page.evaluate(() => {
    const k = [...document.querySelectorAll('#voortgangCard .card')][0];
    return (k ? k.innerText : '').replace(/\s+/g, ' ');
  });
  ok(/\+42/.test(week), 'de aanwas van de laatste twee weekmetingen staat er (+42)');
  ok(/\/7/.test(week), 'met het aantal dagen dat je er was');

  console.log('\n-- sterk en zwak staan er één keer --');
  const dubbel = await page.evaluate(() => {
    const t = document.getElementById('tab-voortgang').innerText;
    return { sterk: (t.match(/Sterke punten/g) || []).length,
             zwak: (t.match(/Zwakke plekken/g) || []).length,
             oud: (t.match(/Dit beheers je/g) || []).length };
  });
  ok(dubbel.sterk <= 1 && dubbel.zwak <= 1, 'niet twee keer hetzelfde blok op één scherm');
  ok(dubbel.oud === 0, 'en het oude gecombineerde blok is weg, niet blijven staan');

  console.log('\n-- weggelaten is niet verstopt --');
  await page.evaluate(() => show('perfil'));
  await page.waitForTimeout(400);
  const prof = await page.evaluate(() => ({
    knop: !!document.getElementById('btnNaarVoortgang'),
    stats: !!document.querySelector('#tab-perfil #statsCard')
  }));
  ok(prof.knop, 'op je profiel staat een knop naar je voortgang');
  ok(!prof.stats, 'en de cijfers staan er niet ook nog een keer');

  const echt = errors.filter((e) => !/Failed to load resource|net::/.test(e));
  ok(echt.length === 0, 'geen JS-fouten (' + echt.length + ')');
  if (echt.length) echt.forEach((e) => console.log('  -> ' + e));

  await browser.close();
  console.log(fout === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fout + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fout === 0 ? 0 : 1);
})();
'''

pad_v = os.path.join(MAP_S, "pw-voortgang.js")
if os.path.exists(pad_v):
    print("  pw-voortgang.js: bestaat al")
else:
    with io.open(pad_v, "w", encoding="utf-8") as f:
        f.write(SUITE)
    print("  pw-voortgang.js: aangemaakt")
