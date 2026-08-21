#!/usr/bin/env python3
# v23.159 - een route in plaats van drie stapels
#
# Stefan, 21 aug: "De hele grammatica sectie voelt niet logisch."
#
# Gemeten op de Grammatica-tab van iemand die alle lessen af heeft (A2):
#
#   23 concepten   onder de kop "De keuzes"
#    5 diepe lessen onder de kop "De diepe lessen"
#   24 onderwerpen onder de kop "Alle onderwerpen"
#   ------
#   52 kaartjes op een scherm, met drie koppen die geen van drieen zeggen wat het verschil is, en
#   waarvan de laatste ("Alle onderwerpen") over 24 van de 52 gaat. Dat is niet vaag maar onwaar.
#
# En er stond dubbel werk in. "Ser of estar" staat er als concept en als diepe les ("Ser vs.
# estar"). Hetzelfde voor perfecto/indefinido en por/para. "Wisselt de klinker mee?" staat er als
# concept en als spiekbriefkaart ("Schoenwerkwoorden"). Twee kaartjes, twee namen, een onderwerp.
#
# De oorzaak van dat laatste is precies aan te wijzen: gwGenLijst() reserveert de spiekbriefkaarten
# die een handgeschreven wizard afdekt, maar niet die een concept afdekt. Terwijl elk concept dat
# gewoon in zijn eigen spiek-veld heeft staan. Het feit stond in de data en werd niet gelezen.
#
# En het derde: er is een echte leervolgorde (GC_ORDE, met voorwaarden in GC_VOOR), en die was
# nergens te zien. De tab liet drie kaartjes zien met een knop naar de rest, en die rest was een
# ongeordende muur van alleen wat open stond. "Nog 20 komen later" zonder te zeggen welke, of
# waarom, of wat je ervoor moet doen.
#
# Wat deze ronde doet:
#
#   1. Elk onderwerp staat nog precies een keer op het scherm.
#   2. De uitgeklapte lijst is de route: genummerd, in leervolgorde, met de gesloten onderwerpen
#      zichtbaar en de voorwaarde erbij genoemd.
#   3. De koppen zeggen wat er staat.
#
# Wat deze ronde NIET doet: de korte opening veranderen. v20.7 ("of beide kan of niet") staat er om
# een goede reden en pw-leermachine bewaakt hem. Drie kaartjes, knop eronder, keuze onthouden.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.159"

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
    # 1. geen dubbelen: een concept dekt zijn eigen spiekbriefkaarten af
    # -----------------------------------------------------------------------
    rep('''function gwGenLijst(){
  // alle automatisch opgeknipte onderwerpen van het actieve track, behalve die al door een
  // handgeschreven wizard worden afgedekt
  var tk = gwTrackKey(), bezet = {};
  GRAMWIZ.forEach(function(o){
    var lijst = o.spiek && o.spiek[tk];
    if(lijst) lijst.forEach(function(i){ bezet[i] = true; });
  });''',
        '''function gwGenLijst(){
  // alle automatisch opgeknipte onderwerpen van het actieve track, behalve die al door een
  // handgeschreven wizard of door een concept worden afgedekt
  var tk = gwTrackKey(), bezet = {};
  GRAMWIZ.forEach(function(o){
    var lijst = o.spiek && o.spiek[tk];
    if(lijst) lijst.forEach(function(i){ bezet[i] = true; });
  });
  /* v23.159, en dit is het soort fout waar de architectuurregel voor bestaat: staat een feit in de
     data, dan hoort geen enkele codeplek het opnieuw te bepalen. Elk concept zegt in zijn spiek-veld
     welke spiekbriefkaarten het afdekt. Die regel gold hierboven wel voor de handgeschreven
     wizards en niet voor de concepten, en dus stond "Wisselt de klinker mee?" (concept zapato,
     spiek a2:[3]) op hetzelfde scherm als "Schoenwerkwoorden (klinkerwissel)" (kaart 3). Gemeten op
     A2: elf kaarten stonden er dubbel, en de lijst gaat van 24 naar 13. */
  GC_CONCEPTEN.forEach(function(c){
    var lijst = c.spiek && c.spiek[tk];
    if(lijst) lijst.forEach(function(i){ bezet[i] = true; });
  });''')

    # -----------------------------------------------------------------------
    # 2. de route: status, rij, en de lijst zelf
    # -----------------------------------------------------------------------
    rep('''// Een conceptkaartje toont geen stappen (het is er maar een) maar de stand van je doosje.
// Dat is het enige getal dat hier iets betekent: wanneer komt dit terug.
function gcKaartHtml(o){
  var st = gramLees(o.concept);
  var status;
  if(st.fout && (st.box || 0) === 0) status = "<span style='color:var(--rood,#c0392b)'>" + ct("fout gegaan", "got this wrong") + "</span>";
  else if(!st.goed && !st.fout) status = ct("nog niet gedaan", "not done yet");
  else status = ct("doos ", "box ") + (st.box || 0) + "/" + (GRAM_BOX.length - 1);
  return "<div class='lesson' data-gclees='" + o.concept + "'>" +''',
        '''// Een conceptkaartje toont geen stappen (het is er maar een) maar de stand van je doosje.
// Dat is het enige getal dat hier iets betekent: wanneer komt dit terug.
/* v23.159: die status stond alleen in gcKaartHtml, en de route hieronder heeft hem ook nodig. Een
   tweede plek die hetzelfde uitrekent is een tweede waarheid, dus hij staat nu een keer. */
function gcStatusHtml(cid){
  var st = gramLees(cid);
  if(st.fout && (st.box || 0) === 0) return "<span style='color:var(--red)'>" + ct("fout gegaan", "got this wrong") + "</span>";
  if(!st.goed && !st.fout) return ct("nog niet gedaan", "not done yet");
  return ct("doos ", "box ") + (st.box || 0) + "/" + (GRAM_BOX.length - 1);
}
/* Waarom staat dit onderwerp nog dicht? "Nog 20 komen later" zei niet welke, niet waarom, en niet
   wat je ervoor moet doen. De voorwaarde staat in GC_VOOR en die is gewoon te lezen. */
function gcSlotReden(cid){
  var v = (GC_VOOR[cid] || []).filter(function(x){ return !gcGedaan(x); })
    .map(function(x){ var c = gcConcept(x); return c ? ct(c.naam, c.naamEn) : x; });
  if(v.length) return ct("eerst: ", "first: ") + v.join(ct(" en ", " and "));
  /* Geen onvervulde voorwaarde: dit onderwerp wacht op een plek. Er staan er hoogstens GC_VENSTER
     nieuw tegelijk open, en dat is het echte antwoord op "waarom kan ik hier niet bij". */
  return ct("opent zodra je een van de open onderwerpen aanpakt",
            "opens once you take on one of the open topics");
}
function gcKaartHtml(o){
  var status = gcStatusHtml(o.concept);
  return "<div class='lesson' data-gclees='" + o.concept + "'>" +''')

    # de rij, en de route-lijst
    rep('''function gcVandaagKaartjes(con){''',
        '''/* v23.159: de route. Genummerd, in leervolgorde, met de gesloten onderwerpen erbij.
   Hetzelfde beeld als het grammaticapad in de Speeltuin (v23.116): een cijfer, een vinkje als het
   af is, een slot als het dicht staat. Twee verschillende beelden voor "waar sta ik" op twee
   tabbladen is precies waarom Stefan schreef dat hij niet weet waar hij wat kan vinden. */
function gcRouteRijHtml(c, nr, vandaagSet){
  var open = gcConceptOpen(c.id), st = gramLees(c.id);
  var af = (st.goed || 0) > 0 && (st.box || 0) > 0 && !(st.fout && (st.box || 0) === 0);
  var nu = !!vandaagSet[c.id];
  /* Het cijfer is de plek in de route en blijft dus altijd staan, ook bij een slot: anders telt de
     lijst 1, 3, 5 en is de route juist niet meer te lezen. Het slot hoort rechts, bij de rest van de
     stand. */
  var merk = af ? "\\u2713" : String(nr);
  var kleur = af ? "var(--green)" : (nu ? "var(--accent)" : "var(--muted)");
  var onder = open ? gcStatusHtml(c.id) : gcSlotReden(c.id);
  return "<div class='lesson gcroute'" + (open ? " data-gclees='" + c.id + "'" : " style='opacity:.5'") + ">" +
    "<div class='lnum' style='color:" + kleur + "'>" + merk + "</div>" +
    "<div class='lbody'><b>" + c.icon + " " + ct(c.naam, c.naamEn) + "</b><span>" + onder + "</span></div>" +
    "<div class='lstatus' style='font-size:.72rem; text-align:right'>" +
      (!open ? "\\ud83d\\udd12"
             : (nu ? "<b style='color:var(--accent)'>" + ct("vandaag", "today") + "</b>" : "\\u25b6")) +
    "</div></div>";
}
function gcRouteHtml(){
  var vandaag = {};
  gcVandaagLijst().forEach(function(c){ vandaag[c.id] = 1; });
  return gcGeordend().map(function(c, i){ return gcRouteRijHtml(c, i + 1, vandaag); }).join("");
}
function gcVandaagKaartjes(con){''')

    # -----------------------------------------------------------------------
    # 3. de koppen zeggen wat er staat, en de diepe lessen met een concept vallen weg
    # -----------------------------------------------------------------------
    rep('''    (con.length
      ? "<p style='margin:14px 0 4px'><b>" + ct("De keuzes", "The choices") + "</b> <span class='muted'>\\u00b7 " + ct("eerst lezen, dan oefenen met elke keer nieuwe voorbeelden", "read first, then practise with fresh examples every time") + "</span></p>" +
        (S.gcAlles
          ? con.map(gcKaartHtml).join("") +
            "<button type='button' class='ghost' id='gcToggleAlles' style='margin-top:8px; font-size:.85rem'>" +
              ct("\\u2190 Alleen wat vandaag telt", "\\u2190 Just what matters today") + "</button>"
          : "<p class='muted' style='margin:0 0 6px; font-size:.8rem'>" + gcVandaagReden() + "</p>" +
            gcVandaagKaartjes(con) +
            "<button type='button' class='ghost' id='gcToggleAlles' style='margin-top:8px; font-size:.85rem'>" +
              ct("Alle " + con.length + " onderwerpen \\u2192", "All " + con.length + " topics \\u2192") + "</button>")
      : "") +
    /* v23.53: verstoppen zonder te zeggen dat je verstopt is precies de fout die de onboarding in
       v23.45 maakte. Het aantal blijft dus zichtbaar. */
    (gcDichtAantal()
      ? "<p class='muted' style='margin:8px 0 0; font-size:.8rem'>" +
        ct("Nog " + gcDichtAantal() + " onderwerpen komen later, als je verder bent.",
           gcDichtAantal() + " more topics unlock as you get further.") + "</p>"
      : "") +''',
        '''    /* v23.159: hier stond "De keuzes", en dat zei niets. Uitgeklapt was het een ongeordende muur
       van alleen wat open stond, met eronder "nog 20 komen later" zonder te zeggen welke of
       waarom. Nu is het de route: genummerd, in de volgorde waarin ze op elkaar bouwen, met de
       gesloten onderwerpen erbij en de voorwaarde erop. De korte opening blijft (v20.7). */
    (con.length
      ? "<p style='margin:14px 0 4px'><b>" + ct("De route", "The route") + "</b> <span class='muted'>\\u00b7 " +
          ct(GC_ORDE.length + " onderwerpen, in de volgorde waarin ze op elkaar bouwen",
             GC_ORDE.length + " topics, in the order they build on each other") + "</span></p>" +
        (S.gcAlles
          ? gcRouteHtml() +
            "<button type='button' class='ghost' id='gcToggleAlles' style='margin-top:8px; font-size:.85rem'>" +
              ct("\\u2190 Alleen wat vandaag telt", "\\u2190 Just what matters today") + "</button>"
          : "<p class='muted' style='margin:0 0 6px; font-size:.8rem'>" + gcVandaagReden() + "</p>" +
            gcVandaagKaartjes(con) +
            "<button type='button' class='ghost' id='gcToggleAlles' style='margin-top:8px; font-size:.85rem'>" +
              ct("De hele route (" + con.length + " open van " + GC_ORDE.length + ") \\u2192",
                 "The whole route (" + con.length + " open of " + GC_ORDE.length + ") \\u2192") + "</button>")
      : "") +
    /* v23.53: verstoppen zonder te zeggen dat je verstopt is precies de fout die de onboarding in
       v23.45 maakte. Het aantal blijft dus zichtbaar. v23.159: uitgeklapt staat het slot er per
       onderwerp bij, en dan is deze regel dubbelop. */
    (gcDichtAantal() && !S.gcAlles
      ? "<p class='muted' style='margin:8px 0 0; font-size:.8rem'>" +
        ct("Nog " + gcDichtAantal() + " onderwerpen komen later, als je verder bent.",
           gcDichtAantal() + " more topics unlock as you get further.") + "</p>"
      : "") +''')

    rep('''    (function(){
      var wz = GRAMWIZ.filter(function(o){ return gcConceptOpen(o.id); });
      return wz.length ? "<p style='margin:14px 0 4px'><b>" + ct("De diepe lessen", "The deep dives") + "</b> <span class='muted'>\\u00b7 " + ct("meer stappen, meer valkuilen, apart geschreven", "more stappen, more pitfalls, written by hand") + "</span></p>" + wz.map(gwKaartHtml).join("") : "";
    })() +'''.replace("more stappen", "more steps"),
        '''    /* v23.159: hier stonden vijf diepe lessen, waarvan drie (serestar, perfindef, porpara) een
       concept met dezelfde naam hebben dat vier regels hoger op hetzelfde scherm staat. Twee
       kaartjes, twee namen, een onderwerp. Die drie zijn nu een knop op de leespagina van hun
       concept; hier blijft over wat echt naast de route staat. */
    (function(){
      var wz = GRAMWIZ.filter(function(o){ return gcConceptOpen(o.id) && !gcConcept(o.id); });
      return wz.length ? "<p style='margin:14px 0 4px'><b>" + ct("Naast de route", "Beside the route") + "</b> <span class='muted'>\\u00b7 " + ct("apart geschreven, met meer stappen en meer valkuilen", "written by hand, with more steps and more pitfalls") + "</span></p>" + wz.map(gwKaartHtml).join("") : "";
    })() +''')

    rep('''    (gen.length
      ? "<p style='margin:18px 0 4px'><b>" + ct("Alle onderwerpen", "All topics") + "</b> <span class='muted'>\\u00b7 " + gen.length + " \\u00b7 " + ct("uit je eigen lessen, met de bijbehorende toetsvragen", "from your own lessons, with their matching quiz questions") + "</span></p>" + gen.map(gwKaartHtml).join("")
      : "") +''',
        '''    /* v23.159: dit heette "Alle onderwerpen" en ging over 24 van de 52 op het scherm. Dat is geen
       vage kop maar een onjuiste. Het zijn de spiekbriefkaarten van je lessen die de route niet
       dekt, en dat is wat er nu staat. */
    (gen.length
      ? "<p style='margin:18px 0 4px'><b>" + ct("Uit je lessen", "From your lessons") + "</b> <span class='muted'>\\u00b7 " + gen.length + " \\u00b7 " + ct("spiekbriefkaarten die niet op de route staan", "cheat sheet cards that are not on the route") + "</span></p>" + gen.map(gwKaartHtml).join("")
      : "") +''')

    # -----------------------------------------------------------------------
    # 4. de leespagina: de diepe les zit er nu aan vast, en vorige/volgende volgt de route
    # -----------------------------------------------------------------------
    rep('''function gcLeesBuur(stap){
  var i = -1;
  GC_CONCEPTEN.forEach(function(c, k){ if(c.id === gcLeesId) i = k; });
  if(i < 0) return null;
  var j = i + stap;
  return (j >= 0 && j < GC_CONCEPTEN.length) ? GC_CONCEPTEN[j] : null;
}''',
        '''function gcLeesBuur(stap){
  /* v23.159: dit liep over GC_CONCEPTEN in bestandsvolgorde, dus "volgende" op de leespagina ging
     een andere kant op dan de route op de tab. Twee volgordes voor dezelfde rij. Nu de route. */
  var rij = gcGeordend(), i = -1;
  rij.forEach(function(c, k){ if(c.id === gcLeesId) i = k; });
  if(i < 0) return null;
  var j = i + stap;
  return (j >= 0 && j < rij.length) ? rij[j] : null;
}
// De handgeschreven diepe les over hetzelfde onderwerp, als die er is.
function gcDiepeLes(cid){
  return GRAMWIZ.filter(function(o){ return o.id === cid; })[0] || null;
}''')

    rep('''      "<button class='primary' id='gcOefen'>" + ct("Oefen dit \\u2192", "Practise this \\u2192") + "</button>" +
      "<button class='ghost' id='gcLeesTerug'>" + ct("\\u2190 Alle onderwerpen", "\\u2190 All topics") + "</button>" +
    "</div>" +''',
        '''      "<button class='primary' id='gcOefen'>" + ct("Oefen dit \\u2192", "Practise this \\u2192") + "</button>" +
      /* v23.159: de diepe les stond als los kaartje op de tab, met bijna dezelfde naam als dit
         onderwerp. Hij hoort hier: eerst de regel, dan de valkuilen. */
      (function(){
        var d = gcDiepeLes(c.id);
        return d ? "<button class='ghost' data-gwstart='" + d.id + "'>" +
          ct("Dieper: " + d.stappen.length + " stappen \\u2192", "Deeper: " + d.stappen.length + " steps \\u2192") + "</button>" : "";
      })() +
      "<button class='ghost' id='gcLeesTerug'>" + ct("\\u2190 De route", "\\u2190 The route") + "</button>" +
    "</div>" +''')

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
