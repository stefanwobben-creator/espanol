#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.24: de opzoeker pakt niet meer het verkeerde woord uit een uitdrukking.

Stefan tikte in hoofdstuk 3 op "pequeña" en kreeg "als kind, toen ik klein was". Dat is de vertaling
van "de pequeño", een vaste uitdrukking, en niet van het woord dat er stond.

De oorzaak: leesLesWoord() zocht per leswoord of het aangetikte woord ergens tussen de losse woorden
van de vertaling zat. Voor "de pequeño / de pequeña" is "pequeña" een van die losse woorden, dus dat
was een treffer. En omdat de A2-lessen (w-nummers) in de woordenlijst vóór het A1-materiaal
(b-nummers) staan, kwam die uitdrukking eerder langs dan het gewone woord "pequeño / pequeña = klein"
dat er ook gewoon in staat.

De regel is nu: een treffer waarbij het hele lemma het woord is gaat altijd voor. Pas als er nergens
zo'n treffer is, mag een woord uit een uitdrukking, en dan staat er ook bij dat het uit een
uitdrukking komt in plaats van dat het net doet alsof het de betekenis van dat ene woord is.

Dat laatste is de eigenlijke fout, meer nog dan de volgorde: de tooltip beweerde iets met dezelfde
stelligheid als bij een goede treffer. Een opzoeker die af en toe zelfverzekerd het verkeerde zegt,
is erger dan een die soms niets weet.

Idempotent.
"""
import io, sys, os

PAD = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol/index.html")
HIER = os.path.dirname(os.path.abspath(__file__))
with io.open(os.path.join(HIER, "lees-extra.js"), encoding="utf-8") as f:
    LEESEXTRA = f.read().strip()

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

if "uitdrukking:true" in src:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:160])
    src = src.replace(anker, nieuw, n)


rep(
    """function leesLesWoord(plat){
  var art = {el:1, la:1, los:1, las:1, un:1, una:1}, i, w, delen, j, kern;
  for(i = 0; i < WORDS.length; i++){
    w = WORDS[i];
    delen = String(w.es).toLowerCase().split(/[\\/,]/);
    for(j = 0; j < delen.length; j++){
      kern = delen[j].trim().split(/\\s+/).filter(function(t){ return !art[t]; }).join(" ");
      if(stripAcc(kern).replace(/[^a-z ]/g, "").split(" ").indexOf(plat) !== -1){
        return {es:w.es, nl:wTrans(w), id:w.id};
      }
    }
  }
  return null;
}""",
    """/* v23.24. Hier stond een functie die trefzeker leek maar te grof zocht: hij keek of het aangetikte
   woord ergens tussen de losse woorden van een leswoord zat. Voor "de pequeño / de pequeña" (als
   kind) is "pequeña" zo'n los woord, dus wie op pequeña tikte kreeg "als kind, toen ik klein was",
   terwijl "pequeño / pequeña = klein" gewoon in dezelfde lijst staat. De A2-lessen staan alleen
   eerder in de woordenlijst dan het A1-materiaal, en dus won de uitdrukking.

   Nu zijn het twee functies. leesLesWoord() geeft alleen een treffer als het hele lemma het woord
   is. Uitdrukkingen komen via leesUitdrukking(), en die wordt pas geprobeerd als het woordenboek en
   de vormherkenning allebei niets gaven. Dat is ook de goede volgorde: por, todo, hace en mundo
   staan gewoon in de frequentielijst, en die hoorden nooit als "por favor" of "todo el mundo" te
   verschijnen.

   Wat tussen haakjes staat telt niet mee bij het vergelijken: "cerca (de)" en "tocar (un
   instrumento)" zijn gewoon cerca en tocar. */
function leesLosseDelen(es){
  var art = {el:1, la:1, los:1, las:1, un:1, una:1};
  return String(es).toLowerCase().replace(/\\([^)]*\\)/g, " ").split(/[\\/,]/).map(function(d){
    return stripAcc(d.trim()).replace(/[^a-z ]/g, "").split(" ").filter(function(t){
      return t && !art[t];
    });
  });
}
function leesLesWoord(plat){
  var i, w, delen, j;
  for(i = 0; i < WORDS.length; i++){
    w = WORDS[i];
    delen = leesLosseDelen(w.es);
    for(j = 0; j < delen.length; j++){
      if(delen[j].length === 1 && delen[j][0] === plat) return {es:w.es, nl:wTrans(w), id:w.id};
    }
  }
  return null;
}
function leesUitdrukking(plat){
  var i, w, delen, j, ruw;
  for(i = 0; i < WORDS.length; i++){
    w = WORDS[i];
    delen = leesLosseDelen(w.es);
    for(j = 0; j < delen.length; j++){
      if(delen[j].length > 1 && delen[j].indexOf(plat) !== -1){
        ruw = String(w.es).split(/[\\/,]/)[j];
        return {es:(ruw || w.es).trim(), nl:wTrans(w), id:w.id, uitdrukking:true};
      }
    }
  }
  return null;
}""")

rep(
    """  for(var k = 0; k < pogingen.length; k++){
    if(!pogingen[k] || pogingen[k] === plat || pogingen[k].length < 2) continue;
    hit = leesLesWoord(pogingen[k]) || leesFreqZoek(pogingen[k]);
    if(hit) return {es:hit.es, nl:hit.nl, id:hit.id, soort:"vorm"};
  }
  return null;
}""",
    """  for(var k = 0; k < pogingen.length; k++){
    if(!pogingen[k] || pogingen[k] === plat || pogingen[k].length < 2) continue;
    hit = leesLesWoord(pogingen[k]) || leesFreqZoek(pogingen[k]);
    if(hit) return {es:hit.es, nl:hit.nl, id:hit.id, soort:"vorm"};
  }
  /* Als laatste pas een uitdrukking. Eerder in de rij zou hij het woordenboek overstemmen, en dan
     krijg je "por" uitgelegd als "por favor". */
  hit = leesUitdrukking(plat);
  if(hit) return {es:hit.es, nl:hit.nl, id:hit.id, soort:"les", uitdrukking:true};
  return null;
}""")

rep(
    """  var extra = "";
  if(b.soort === "vorm" && b.tijd){
    extra = " <span class='muted'>("+b.tijd+(b.persoon ? ", "+b.persoon : "")+")</span>";
  }
  el.innerHTML = "<p><span class='es'>"+woord+"</span>"+
      (stripAcc(String(b.es).toLowerCase()) !== stripAcc(String(woord).toLowerCase())
        ? " <span class='muted'>"+ct("van","from")+" <span class='es'>"+b.es+"</span></span>" : "")+
      extra+"</p>"+
    "<p>"+b.nl+"</p>";""",
    """  var extra = "";
  if(b.soort === "vorm" && b.tijd){
    extra = " <span class='muted'>("+b.tijd+(b.persoon ? ", "+b.persoon : "")+")</span>";
  }
  /* Een woord uit een uitdrukking krijgt een ander voorzetsel: "in de uitdrukking" in plaats van
     "van". Anders leest de tooltip als de betekenis van dat ene woord, en dat is het niet. */
  var brug = b.uitdrukking ? ct("in de uitdrukking","in the expression") : ct("van","from");
  el.innerHTML = "<p><span class='es'>"+woord+"</span>"+
      (stripAcc(String(b.es).toLowerCase()) !== stripAcc(String(woord).toLowerCase())
        ? " <span class='muted'>"+brug+" <span class='es'>"+b.es+"</span></span>" : "")+
      extra+"</p>"+
    "<p>"+b.nl+"</p>";""")

# ---------------------------------------------------------------- de gatenlijst uit de teksten
rep(
    """var LEES_LETTERS = {""",
    LEESEXTRA + """
var LEES_LETTERS = {""")

rep(
    """  if(LEES_LETTERS[plat]) return {es:plat, nl:ct(LEES_LETTERS[plat][0], LEES_LETTERS[plat][1]), soort:"woordenboek"};""",
    """  if(LEES_LETTERS[plat]) return {es:plat, nl:ct(LEES_LETTERS[plat][0], LEES_LETTERS[plat][1]), soort:"woordenboek"};
  if(LEES_EXTRA[plat]) return {es:ruw, nl:ct(LEES_EXTRA[plat][0], LEES_EXTRA[plat][1]), soort:"woordenboek"};""")

# meervoud en geslacht ook langs de gatenlijst
rep(
    """    hit = leesLesWoord(pogingen[k]) || leesFreqZoek(pogingen[k]);
    if(hit) return {es:hit.es, nl:hit.nl, id:hit.id, soort:"vorm"};""",
    """    if(LEES_EXTRA[pogingen[k]]){
      return {es:pogingen[k], nl:ct(LEES_EXTRA[pogingen[k]][0], LEES_EXTRA[pogingen[k]][1]), soort:"vorm"};
    }
    hit = leesLesWoord(pogingen[k]) || leesFreqZoek(pogingen[k]);
    if(hit) return {es:hit.es, nl:hit.nl, id:hit.id, soort:"vorm"};""")

# ---------------------------------------------------------------- een naam is geen gat
rep(
    """  if(!b){
    el.innerHTML = "<p><span class='es'>"+woord+"</span></p>"+
      "<p class='muted' style='font-size:.85rem'>"+
        ct("Staat niet in het woordenboek. Genoteerd.","Not in the dictionary. Noted.")+"</p>";
    if(span) leesTooltipPlaats(el, span);
    return;
  }""",
    """  if(!b){
    /* Een woord met een hoofdletter dat nergens in staat is bijna altijd een naam: Chispa, Guernica,
       doña Inés. "Staat niet in het woordenboek" leest daar als een storing, terwijl er niets mis is.
       Het wordt wel gewoon genoteerd, want als je op een naam tikt wilde je iets weten. */
    var naam = /^[A-ZÁÉÍÓÚÑ]/.test(String(woord));
    el.innerHTML = "<p><span class='es'>"+woord+"</span></p>"+
      "<p class='muted' style='font-size:.85rem'>"+
        (naam ? ct("Een naam, van een persoon of een plaats.","A name, of a person or a place.")
              : ct("Staat niet in het woordenboek. Genoteerd.","Not in the dictionary. Noted."))+"</p>";
    if(span) leesTooltipPlaats(el, span);
    return;
  }""")

rep('var APP_VERSIE = "v23.23";', 'var APP_VERSIE = "v23.24";')

with io.open(PAD, "w", encoding="utf-8") as f:
    f.write(src)
print("v23.24 toegepast op", PAD)
