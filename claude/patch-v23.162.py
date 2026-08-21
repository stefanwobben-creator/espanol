#!/usr/bin/env python3
# v23.162 - de voorspeller viel over een woordzoeker, en een boek uit is een moment
#
# Stefan, 21 aug, drie dingen:
#   1. "de voortgang voorspeller werkt nog niet."
#   2. "het nieuwe boek is er niet."
#   3. "ik had al een keer eerder gezegd dat als een boek uit is, het een feestje moet voelen. Dat
#       is nu ook niet zo."
#
# Alle drie waar, en alle drie iets anders dan ik dacht.
#
# 1. DE VOORSPELLER VIEL OVER DE WOORDENZOEKER
#
# tempoMeting() eindigt met `weken: ws.length`. Er is geen ws in die functie. De ws die JavaScript
# dan pakt is de globale uit de woordenzoeker, twaalfduizend regels verderop:
#
#     var ws = null;                       // regel 23290
#     ws = {grid:grid, woorden:geplaatst, sel:null, foundCells:{}};
#
# Heb je nooit gewoordenzoekerd, dan is ws null en gooit ws.length een TypeError. tempoMeting()
# klapt, en daarmee voortgangBand(), voorspelWaar() en voorspelHtml(). De hele voorspelling. Heb je
# wél gespeeld, dan is ws een object en is weken stilletjes undefined.
#
# Nagemeten met vier weekmetingen in de nieuwe maat, precies de stand van Stefan:
#     tempoMeting('A1')   -> Cannot read properties of null (reading 'length')
#     voortgangBand('A1') -> idem
#     voorspelWaar('A1')  -> idem
#     voorspelHtml()      -> idem
#
# Dus niet "hij heeft nog te weinig weken", zoals ik eerder dacht en zoals de code zelf suggereert.
# Hij heeft nooit gewerkt, voor niemand, sinds v19.90. De reeks die hij nodig heeft heet reeks, en
# dat is ook precies wat er had moeten staan: het aantal weken in dezelfde maat.
#
# Waarom niets dit ving: elke aanroeper heeft een try/catch of een null-check eromheen ("een meter
# mag de app nooit omver duwen"), dus een kapotte voorspeller is niet te onderscheiden van een
# voorspeller die zwijgt omdat er te weinig data is. Die twee zien er op het scherm identiek uit, en
# dat is precies waarom dit maanden kon blijven staan.
#
# 2. HET NIEUWE BOEK STOND OP GEEN ENKELE PLANK
#
# Het leesscherm is een plank, gebouwd uit LEES_REEKSEN, en elke reeks pakt zijn hoofdstukken op
# id-voorvoegsel: "boek-", "receta-", "hist-". De acht Cadiz-hoofdstukken uit v23.157 heten
# "cadiz-1" tot "cadiz-8" en er is geen reeks met pre:"cadiz-". Ze staan dus wel in BOOK, doen wel
# mee in de telling van je leesvoortgang, en zijn op het scherm nergens te vinden.
#
# En dit is dezelfde fout als bij het geluid van gisteren: pw-nieuwestof riep startBoek('cadiz-1')
# rechtstreeks aan en zag dus een boek dat rendert. Via het menu, zoals een mens het doet, bestond
# het niet. Een suite die de voordeur overslaat bewijst niets over de voordeur.
#
# 3. EEN BOEK UIT WAS GEEN MOMENT
#
# finishBoek() viert een hoofdstuk (confetti, tapas, een toast) en daarna closeBoek(). Voor een heel
# boek bestond niets: geen scherm, geen telling, geen spoor. Je las het laatste hoofdstuk van tien
# en kreeg exact dezelfde toast als bij het derde.
#
# Nu: is het laatste hoofdstuk van een reeks af, dan komt er een eigen scherm in plaats van de
# toast. Met wat je gedaan hebt, en die getallen worden afgeleid en niet verzonnen: hoofdstukken,
# woorden Spaans gelezen, en hoeveel dagen er tussen je eerste en je laatste hoofdstuk zaten. Die
# laatste kan alleen als we hem opschrijven, dus S.boek krijgt er een datum bij. Oude regels hebben
# hem niet en dan valt die zin gewoon weg.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.162"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = NIEUW not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:90])
    src = src.replace(anker, nieuw, n)

if DOE_APP:
    # -----------------------------------------------------------------------
    # 1. de voorspeller
    # -----------------------------------------------------------------------
    rep('''  return {gem:gem, marge:2 * Math.sqrt(v / d.length), weken:ws.length, nu:reeks[reeks.length - 1]};''',
        '''  /* v23.162: hier stond `weken: ws.length`, en er is geen ws in deze functie. JavaScript pakte dan
     de globale ws van de woordenzoeker (var ws = null, twaalfduizend regels verderop). Nooit
     gewoordenzoekerd betekende dus een TypeError op ws.length, en daarmee klapte tempoMeting en
     alles wat eraan hangt: voortgangBand, voorspelWaar en voorspelHtml. De hele voorspelling, voor
     iedereen, sinds v19.90.

     Niets ving het, en dat is het echte probleem: elke aanroeper vangt fouten af ("een meter mag de
     app nooit omver duwen"), dus een kapotte voorspeller ziet er op het scherm precies zo uit als
     een voorspeller die nog zwijgt omdat er te weinig weken zijn. */
  return {gem:gem, marge:2 * Math.sqrt(v / d.length), weken:reeks.length, nu:reeks[reeks.length - 1]};''')

    # -----------------------------------------------------------------------
    # 2. het boek op de plank
    # -----------------------------------------------------------------------
    rep(''' {id:"franco", pre:"hist-", nl:"España: los años de Franco", en:"España: los años de Franco", stem:true,''',
        ''' /* v23.162: de acht hoofdstukken van v23.157 stonden wel in BOOK maar op geen enkele plank, want
    de plank zoekt op id-voorvoegsel en er was geen reeks met pre:"cadiz-". Ze telden mee in je
    leesvoortgang en waren nergens te vinden. */
 {id:"cadiz", pre:"cadiz-", nl:"Un año en Cádiz", en:"Un año en Cádiz", stem:true,
  soortNl:"verhaal", soortEn:"story",
  omNl:"Een jaar in het zuiden, van de eerste dag op een onbekend adres tot de carnaval waarop je meezingt.",
  omEn:"A year in the south, from your first day at an unfamiliar address to the carnival where you sing along."},
 {id:"franco", pre:"hist-", nl:"España: los años de Franco", en:"España: los años de Franco", stem:true,''')

    # -----------------------------------------------------------------------
    # 3. een boek uit is een moment
    # -----------------------------------------------------------------------
    rep('''function renderBoekMenu(){''',
        '''/* ================= EEN BOEK UIT (v23.162) =================

   Stefan: "ik had al een keer eerder gezegd dat als een boek uit is, het een feestje moet voelen.
   Dat is nu ook niet zo."

   Klopte. finishBoek() vierde een hoofdstuk en verder niets: het laatste hoofdstuk van tien gaf
   dezelfde toast als het derde. Een boek uitlezen in een vreemde taal is het soort ding waar je een
   jaar later nog aan terugdenkt, en de app liet het voorbijgaan.

   De getallen hieronder worden afgeleid en niet verzonnen. Hoofdstukken en woorden staan in BOOK;
   de dagen komen uit de datum die S.boek sinds deze versie per hoofdstuk bewaart. Heeft een oude
   regel die datum niet, dan valt die zin weg in plaats van dat er iets geschats komt te staan. */
function boekReeksHst(r){
  return BOOK.filter(function(x){ return String(x.id).indexOf(r.pre) === 0; });
}
function boekReeksAf(r){
  var hst = boekReeksHst(r);
  return hst.length > 0 && hst.every(function(x){ return S.boek[x.id] && S.boek[x.id].done; });
}
function boekReeksCijfers(r){
  var hst = boekReeksHst(r), woorden = 0, dagen = [];
  hst.forEach(function(h){
    woorden += String(h.tekst || "").split(/\\s+/).filter(Boolean).length;
    var st = S.boek[h.id];
    if(st && st.d) dagen.push(st.d);
  });
  dagen.sort();
  var spanne = null;
  if(dagen.length > 1){
    var v = Math.round((new Date(dagen[dagen.length - 1]) - new Date(dagen[0])) / 86400000);
    if(v >= 1) spanne = v;
  }
  return {hoofdstukken:hst.length, woorden:woorden, spanne:spanne, van:dagen[0] || null};
}
/* Het scherm zelf. Geen toast: een toast verdwijnt terwijl je hem leest, en dit is juist het moment
   waarop je even mag stilstaan. */
function boekUitScherm(r){
  var c = boekReeksCijfers(r);
  var el = document.getElementById("lezenCard");
  if(!el) return;
  el.innerHTML = "<span class='kicker'>" + ct("Uit \\ud83c\\udf89", "Finished \\ud83c\\udf89") + "</span>" +
    "<h2 style='margin:2px 0 10px'>" + (profLang() === "nl" ? r.nl : r.en) + "</h2>" +
    "<p class='big' style='margin:0 0 4px'>" +
      ct("Je hebt een boek in het Spaans uitgelezen.", "You finished a book in Spanish.") + "</p>" +
    "<div class='feedback ok' style='margin-top:12px'>" +
      c.hoofdstukken + " " + ct("hoofdstukken", "chapters") + " \\u00b7 " +
      c.woorden + " " + ct("woorden Spaans", "words of Spanish") +
      (c.spanne ? " \\u00b7 " + ct("in " + c.spanne + " dagen", "in " + c.spanne + " days") : "") +
    "</div>" +
    "<p class='muted' style='margin-top:10px'>" +
      ct("Dat is geen oefening meer. Dat is lezen.", "That is not practice any more. That is reading.") + "</p>" +
    "<div class='row' style='margin-top:12px'>" +
      "<button class='primary' id='btnBoekUitDoor'>" + ct("Naar de plank \\u2192", "To the shelf \\u2192") + "</button>" +
    "</div>";
  var b = document.getElementById("btnBoekUitDoor");
  if(b) b.onclick = function(){ closeBoek(); };
}
function renderBoekMenu(){''')

    # De emoji in dit blok staan als echte tekens in index.html, niet als \u-escapes, dus het anker
    # loopt er bewust omheen: twee kleine ankers in plaats van een blok met tekens die je in een
    # patchscript niet wilt overtypen.
    rep('''  S.boek[h.id] = {done:true, score:besteScore, reflectie: refl || (vorige && vorige.reflectie) || ""};
  persist();''',
        '''  /* v23.162: de datum erbij. Zonder die datum kan het slotscherm van een boek niet zeggen hoe
     lang je erover deed, en dat is precies het soort getal waar zo'n moment van leeft. Oude regels
     hebben hem niet; dan valt die zin weg in plaats van dat er iets geschats komt te staan. */
  var reedsD = (vorige && vorige.d) || null;
  S.boek[h.id] = {done:true, score:besteScore, reflectie: refl || (vorige && vorige.reflectie) || "",
                  d: reedsD || today()};
  persist();''')

    rep('''  if(eersteKeer) verdiend += 3;
  if(pct === 1) verdiend += 2;
''',
        '''  if(eersteKeer) verdiend += 3;
  if(pct === 1) verdiend += 2;
  /* v23.162: is dit het laatste hoofdstuk van het boek, dan is dit geen hoofdstukmoment meer.
     De reeks moet nu af zijn en het mag niet eerder al af geweest zijn, anders viert hij mee bij
     elke herlezing. */
  var reeks = leesReeksVan(h);
  var boekUit = false;
  try { boekUit = eersteKeer && reeks && boekReeksAf(reeks) && !(S.boekUit && S.boekUit[reeks.id]); }
  catch(e){ boekUit = false; }
  if(boekUit){
    verdiend += 10;
    S.tapas = (S.tapas||0) + verdiend;
    S.boekUit = S.boekUit || {};
    S.boekUit[reeks.id] = today();
    persist();
    confetti(["\\ud83c\\udf89","\\ud83d\\udcda","\\u2728","\\ud83c\\udf8a"], 60);
    boekUitScherm(reeks);
    return;
  }
''')

    # en de plank onthoudt het: een uitgelezen boek ziet er anders uit dan een half boek
    rep('''      "<div class='row' style='margin-top:10px'><button class='"+(af ? "ghost" : "primary")+"' data-reeks='"+r.id+"'>"+
        (af && af < hst.length ? ct("Verder lezen","Keep reading")
                               : (af ? ct("Nog eens lezen","Read again") : ct("Beginnen","Start")))+" \\u2192</button></div>"+
      "</div>";''',
        '''      /* v23.162: een uitgelezen boek hoort er anders uit te zien dan een half boek. Anders is het
         feestje van vorige week op de plank niet terug te vinden, en dan was het geen moment maar
         een animatie. */
      ((S.boekUit && S.boekUit[r.id])
        ? "<p style='margin:6px 0 0; font-size:.9rem'><b>\\ud83c\\udf89 " +
            ct("Uitgelezen", "Finished") + "</b> <span class='muted'>\\u00b7 " +
            ct("op " + S.boekUit[r.id], "on " + S.boekUit[r.id]) + "</span></p>"
        : "")+
      "<div class='row' style='margin-top:10px'><button class='"+(af ? "ghost" : "primary")+"' data-reeks='"+r.id+"'>"+
        (af && af < hst.length ? ct("Verder lezen","Keep reading")
                               : (af ? ct("Nog eens lezen","Read again") : ct("Beginnen","Start")))+" \\u2192</button></div>"+
      "</div>";''')

    src = src.replace('var APP_VERSIE = "%s"' % huidig_ver, 'var APP_VERSIE = "%s"' % NIEUW)
    APP.write_text(src, encoding="utf-8")
    print("index.html: bijgewerkt naar", NIEUW)
else:
    print("index.html: al op", NIEUW)

if DOE_VER:
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt:", NIEUW)
else:
    print("versie.txt: al op", huidig_ver)
