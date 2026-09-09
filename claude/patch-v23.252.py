#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v23.252 - de leesplank zegt welke VORM er staat, niet alleen wat het woord betekent
#
# Stefan, 9 september, over Don Quijote: "de leesoefening is te moeilijk, het zijn niet alleen de
# vocabulaire, maar het zijn ook de vervoegingen van de werkwoorden. Hou daar ook rekening mee als je
# het verhaal maakt. Dat ik de tegenwoordige tijd van een werkwoord ken zegt niet dat ik alle vormen
# ken."
#
# ================ EERST GEMETEN ================
#
# Twee metingen, allebei in de eigen gegevens van de app.
#
# EEN. HOEVEEL TIJDEN STAAN ER IN DE TEKSTEN DIE HIJ KRIJGT?
#
# Elke werkwoordsvorm in elke leestekst opgezocht in de vervoegingstabel van de app zelf:
#
#     29 van de 43 teksten gebruiken een tijd buiten het presente
#
# Zijn Conjugador-ladder staat op "het hele presente". Van "Los molinos de viento", de tekst waar hij
# over schreef, staan er imperfecto-, indefinido- en subjuntivo-vormen in. Zijn klacht klopt dus
# precies, en het is te tellen.
#
# En die telling is nog een ONDERGRENS: hij herkent alleen vormen van de 33 werkwoorden in VERBOS,
# en samengestelde tijden ("ha encontrado") en de condicional ("contestaría") vallen er helemaal
# buiten omdat de app die tijden niet kent.
#
# TWEE. EN WAT ZEGT DE APP ALS JE ZO'N VORM AANTIKT?
#
# In de tien Don Quijote-teksten staan 161 herkenbare werkwoordsvormen. Daarvan krijgen er ACHT een
# tijdsaanduiding mee. De andere 153 krijgen alleen een betekenis.
#
# En het interessante zit in wat die betekenis is:
#
#     eran     -> "eran = they were (from ser, imperfect)"      [woordenboek]
#     hizo     -> "hizo = he/she did/made (from hacer)"         [woordenboek]
#     tenían   -> "tenían = they had (from tener, imperfect)"   [woordenboek]
#
# De tijd STAAT er. In het Engels, in een handgeschreven zin, in een profiel dat op Nederlands staat.
# Niet in een veld. Gevolg: de app kan er niets mee (niet opmaken, niet tellen, niet zeggen "deze
# tijd heb je nog niet gehad"), en de lezer alleen als hij Engels leest.
#
#     Staat een feit in een tekst in plaats van in een veld, dan kan alleen de lezer het
#     gebruiken, en alleen als hij die taal spreekt.
#
# Dat is dezelfde vorm als de rest van deze week: v23.246 (de knop droeg zijn antwoordindex niet),
# v23.249 (de zin die beoordeeld werd, ging niet mee), v23.251 (de markering stond er en verloor).
# Het feit bestaat, maar niet op een plek waar de app erbij kan.
#
# ================ WAT ER VERANDERT ================
#
# EEN. DE VORM WORDT AFGELEID, NIET OPGESCHREVEN.
#
# leesVormKaart() bouwt één keer een tabel vorm -> {werkwoord, tijd, persoon} uit VERBOS en
# CONJ_TIEMPOS: dezelfde bron waar de Conjugador uit put. Accentgevoelig, want "de" en "dé" zijn
# twee verschillende woorden en de eerste is een voorzetsel.
#
# Dat werkt meteen voor élke vorm van alle 33 werkwoorden, niet alleen voor de vormen waar iemand
# ooit een Engelse zin bij heeft getypt. Staat een vorm in twee tijden (hablamos is presente én
# indefinido), dan zegt de app dat het er twee zijn en niet welke van de twee: een verkeerde
# diagnose is erger dan geen.
#
# TWEE. DE UITLEG ZEGT HET IN HET NEDERLANDS, EN ZEGT OF JE DIE TIJD AL HAD.
#
# Tik je "eran" aan, dan staat er nu:
#
#     eran   van ser
#     zij/ellos, imperfecto (onvoltooid verleden tijd)
#     Deze tijd heb je in de Conjugador nog niet gehad.
#
# Die laatste regel is het antwoord op zijn zin. Hij hoeft niet te raden waarom een woord dat hij
# kent er anders uitziet; er staat dat het een tijd is die nog niet aan de beurt was. De tijdsnaam
# komt uit conjTiempoNaam(), die het Spaans én de Nederlandse naam geeft, en de persoon uit
# RV_PERSOON: allebei bestonden ze al.
#
# DRIE. EEN TEKST DRAAGT ZIJN TIJDEN, EN DE PLANK ZEGT HET VOORAF.
#
# leesTekstTijden() telt per tekst de vormen buiten je open tijden, uit de tekst zelf. Op de kaart
# van een hoofdstuk staat dat als één regel ("hierin staan ook 6 verleden vormen"), zodat je vooraf
# weet wat je krijgt in plaats van halverwege vast te lopen.
#
# Wat hier NIET gebeurt: teksten wegstoppen. Er zijn er 29 van de 43 met een tijd buiten het
# presente, en die verbergen zou de plank halveren en het lezen zelf slopen. Lezen boven je niveau
# is niet het probleem; niet weten wat je ziet, is het probleem.
#
# WAT DIT BETEKENT VOOR NIEUWE VERHALEN
#
# Zijn tweede zin was: hou daar rekening mee als je het verhaal maakt, ook voor de andere gebruikers.
# De regel die daaruit volgt staat nu meetbaar in de app: een tekst op drempel 0 hoort geen tijd te
# gebruiken die op drempel 0 nog niet open is. pw-leestijden.js drukt die tabel af per tekst, zodat
# de volgende schrijver (ik, of de nachtrun) ziet wat hij doet vóórdat het geleverd wordt. Als eis
# afdwingen kan pas als de bestaande 29 teksten meegenomen zijn; dat is een aparte ronde en die
# belofte staat hier dus als wat ze is: gemeten en zichtbaar, nog niet afgedwongen.
import pathlib
import re
import sys

W = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(W / "claude"))
import patchhulp  # noqa: E402

APP = W / "index.html"
VER = W / "versie.txt"
GEPLAND = "v23.252"

src = APP.read_text(encoding="utf-8")
huidig = VER.read_text(encoding="utf-8").strip()
DOE_APP = "function leesVormKaart(" not in src


def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:110])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    # ---------- EEN: de vorm wordt afgeleid uit de vervoegingstabel ----------
    rep(
        """function leesBetekenis(ruw){""",
        """/* ================= WELKE VORM STAAT ER? (v23.252) =================

   Stefan, 9 september: "dat ik de tegenwoordige tijd van een werkwoord ken zegt niet dat ik alle
   vormen ken."

   Gemeten in de tien Don Quijote-teksten: 161 herkenbare werkwoordsvormen, waarvan er ACHT een
   tijdsaanduiding meekregen. De rest kreeg alleen een betekenis, en bij een handvol stond de tijd
   wél in die betekenis:

       eran   -> "eran = they were (from ser, imperfect)"
       tenían -> "tenían = they had (from tener, imperfect)"

   In het Engels, in een handgeschreven zin, in een profiel dat op Nederlands staat. Niet in een
   veld, dus de app kan er niets mee.

       Staat een feit in een tekst in plaats van in een veld, dan kan alleen de lezer het
       gebruiken, en alleen als hij die taal spreekt.

   Deze tabel leidt het af uit VERBOS en CONJ_TIEMPOS, dezelfde bron waar de Conjugador uit put.
   Daarmee geldt het voor élke vorm van alle werkwoorden die de app kent, en niet alleen voor de
   vormen waar ooit iemand een zin bij heeft getypt.

   ACCENTGEVOELIG, en dat is niet vrijblijvend: "de" is een voorzetsel en "dé" is een vorm van dar.
   Sla je de accenten plat, dan krijgt elk voorzetsel "de" in elke tekst het etiket subjuntivo. Dat
   gebeurde in de eerste meting van deze ronde, en het maakte een telling van 254 vormen waarvan er
   in werkelijkheid 161 waren. */
var _leesVormKaart = null;
function leesVormKaart(){
  if(_leesVormKaart) return _leesVormKaart;
  var k = {};
  try {
    CONJ_TIEMPOS.forEach(function(x){
      VERBOS.forEach(function(v){
        for(var i = 0; i < 6; i++){
          var f = conjVorm(v, i, x.id);
          if(!f) continue;
          var s = String(f).toLowerCase();
          if(!k[s]) k[s] = [];
          k[s].push({inf:v.inf, tijd:x.id, persoon:i});
        }
      });
    });
  } catch(e){ k = {}; }
  _leesVormKaart = k;
  return k;
}
/* Geeft null als het geen bekende vorm is. Staat de vorm in twee tijden (hablamos is presente én
   indefinido), dan zegt hij dat het er twee zijn en niet welke: een verkeerde diagnose is erger
   dan geen. */
function leesVormInfo(ruw){
  var s = String(ruw || "").toLowerCase().replace(/[^a-z\\u00e1\\u00e9\\u00ed\\u00f3\\u00fa\\u00fc\\u00f1]/g, "");
  if(!s) return null;
  var lijst = leesVormKaart()[s];
  if(!lijst || !lijst.length) return null;
  var tijden = [], i;
  for(i = 0; i < lijst.length; i++) if(tijden.indexOf(lijst[i].tijd) === -1) tijden.push(lijst[i].tijd);
  return {inf:lijst[0].inf, tijd:lijst[0].tijd, persoon:lijst[0].persoon,
          tijden:tijden, dubbel:tijden.length > 1};
}
/* Staat deze tijd al open in de Conjugador? Leest conjOpenTijden(), dus er komt geen tweede lijst
   bij en het antwoord verandert vanzelf mee als je een fase haalt. */
function leesTijdOpen(t){
  try { return conjOpenTijden().indexOf(t) !== -1; } catch(e){ return true; }
}
/* Wat een tekst aan werkwoordsvormen bevat die buiten je open tijden vallen. Uit de tekst zelf, dus
   een nieuwe tekst hoeft niets bij te houden en kan er ook niet naast zitten. */
function leesTekstTijden(tekst){
  var kaart = leesVormKaart();
  var woorden = String(tekst || "").toLowerCase().replace(/[^a-z\\u00e1\\u00e9\\u00ed\\u00f3\\u00fa\\u00fc\\u00f1\\s]/g, " ").split(/\\s+/);
  var perTijd = {}, buiten = 0, i, lijst, tijden, j;
  for(i = 0; i < woorden.length; i++){
    lijst = kaart[woorden[i]];
    if(!lijst || !lijst.length) continue;
    tijden = [];
    for(j = 0; j < lijst.length; j++) if(tijden.indexOf(lijst[j].tijd) === -1) tijden.push(lijst[j].tijd);
    if(tijden.length !== 1) continue;          // dubbelzinnig: dat telt niet als "een andere tijd"
    if(leesTijdOpen(tijden[0])) continue;
    perTijd[tijden[0]] = (perTijd[tijden[0]] || 0) + 1;
    buiten++;
  }
  return {buiten:buiten, perTijd:perTijd};
}
/* v23.252: de kale opzoeker heet nu zo, en leesBetekenis() eromheen hangt de vorm eraan. Op die
   manier hoeft geen van de acht uitgangen hierin te weten dat er ook nog een vorm bij hoort. */
function leesBetekenisKaal(ruw){""",
    )
    rep(
        """  var inf = leesNaarInfinitief(plat);
  for(ki = 0; !inf && ki < kaal.length; ki++) inf = leesNaarInfinitief(kaal[ki]);
  if(inf) return {es:inf.inf, nl:inf.nl, id:inf.id, soort:"vorm"};
  return null;
}""",
        """  var inf = leesNaarInfinitief(plat);
  for(ki = 0; !inf && ki < kaal.length; ki++) inf = leesNaarInfinitief(kaal[ki]);
  if(inf) return {es:inf.inf, nl:inf.nl, id:inf.id, soort:"vorm"};
  return null;
}
function leesBetekenis(ruw){
  var b = null, v = null;
  try { b = leesBetekenisKaal(ruw); } catch(e){ b = null; }
  try { v = leesVormInfo(ruw); } catch(e){ v = null; }
  if(!v) return b;
  /* Geen betekenis maar wel een bekende vorm: dan is de infinitief het antwoord. Beter "een vorm
     van salir" dan "staat niet in het woordenboek" bij een woord dat er wel degelijk in staat. */
  if(!b){
    var bi = null;
    try { bi = leesBetekenisKaal(v.inf); } catch(e){ bi = null; }
    if(!bi) return null;
    b = {es:v.inf, nl:bi.nl, id:bi.id, soort:"vorm"};
  }
  b.vorm = v;
  return b;
}""",
    )

    # ---------- TWEE: de uitleg zegt welke vorm, in het Nederlands ----------
    rep(
        """  var extra = "";
  if(b.soort === "vorm" && b.tijd){
    extra = " <span class='muted'>("+b.tijd+(b.persoon ? ", "+b.persoon : "")+")</span>";
  }""",
        """  var extra = "";
  if(b.soort === "vorm" && b.tijd){
    extra = " <span class='muted'>("+b.tijd+(b.persoon ? ", "+b.persoon : "")+")</span>";
  }
  /* v23.252: welke vorm dit is, in het Nederlands, en of je die tijd al gehad hebt.

     Stefan: "dat ik de tegenwoordige tijd van een werkwoord ken zegt niet dat ik alle vormen ken."
     Dit is die regel. Hij komt uit de vervoegingstabel en niet uit een handgeschreven zin, dus hij
     staat er bij élke vorm van elk werkwoord dat de app kent.

     Bij een vorm die in twee tijden voorkomt noemen we ze allebei. Kiezen zou raden zijn. */
  var vormRegel = "";
  if(b.vorm){
    var vp = RV_PERSOON[b.vorm.persoon] || "";
    var vt = b.vorm.dubbel
      ? b.vorm.tijden.map(function(t){ return conjTiempoLabel(t); }).join(ct(" of ", " or "))
      : conjTiempoNaam(b.vorm.tijd);
    vormRegel = "<p class='muted' style='font-size:.85rem; margin:2px 0 0'>" +
      (vp ? "<span class='es'>"+vp+"</span>, " : "") + vt +
      (b.vorm.dubbel ? " <span class='muted'>("+ct("die vorm hoort bij allebei","that form fits both")+")</span>" : "") +
      "</p>";
    if(!b.vorm.dubbel && !leesTijdOpen(b.vorm.tijd)){
      vormRegel += "<p class='muted' style='font-size:.85rem; margin:2px 0 0'>" +
        ct("Deze tijd heb je in de Conjugador nog niet gehad.",
           "You have not reached this tense in the Conjugador yet.") + "</p>";
    }
  }""",
    )
    rep(
        """    "<p>"+b.nl+"</p>"+
    leesMijnKnopHtml(leesNu.doel);""",
        """    "<p>"+b.nl+"</p>"+ vormRegel +
    leesMijnKnopHtml(leesNu.doel);""",
    )

    # ---------- DRIE: kijk naar wat er STAAT voordat je kijkt waar het op lijkt ----------
    #
    # De meting van deze ronde vond er nog een, en het is de grootste van de drie: het woord "de"
    # komt 235 keer voor in de leesteksten en wordt elke keer uitgelegd als "geeft u (van dar,
    # subjuntivo)". Dat is de uitleg van "dé".
    #
    # De oorzaak: het opzoeken gaat over de accentloze vorm, dus "de" en "dé" delen één sleutel, en
    # in die pot zit de zeldzame. Het meest voorkomende voorzetsel van het Spaans krijgt daardoor de
    # verklaring van een werkwoordsvorm die hij in geen van de 43 teksten tegenkomt.
    #
    #     Kijk eerst naar wat er STAAT, en pas daarna naar waar het op lijkt.
    #
    # WAT HIER NIET GEREPAREERD IS. De hele keten eronder (leesLesWoord, leesFreqZoek, LEES_EXTRA)
    # werkt óók op de accentloze sleutel, dus "dé" krijgt nu de betekenisregel van het voorzetsel
    # "de" (lesswoord k158). Alleen de bovenste laag kijkt naar het geschreven woord, en dat is
    # genoeg voor het geval dat 235 keer voorkomt en niet voor het geval dat nul keer voorkomt.
    # "dé" krijgt er wél de juiste vormregel bij (dar, subjuntivo), want die is accentgevoelig.
    # Het staat als RESIDU in pw-leesvorm.js, gemeten en benoemd, niet als opgelost geteld.
    #
    # LEES_LETTERS bestaat precies voor dit soort woorden ("y, o en a zijn juist woorden die op elke
    # bladzijde staan"), dus "de" hoort daar en die controle gaat over het geschreven woord. "dé"
    # valt er daarmee doorheen naar zijn eigen uitleg, zoals het hoort.
    rep(
        """var LEES_LETTERS = {y:["en","and"], o:["of","or"], a:["naar, aan, tot","to, at"],""",
        """/* v23.252: "de" staat hier nu bij, en de controle hieronder kijkt naar het GESCHREVEN woord.
   Gemeten: 235 keer in de leesteksten, en elke keer uitgelegd als "geeft u (van dar, subjuntivo)",
   want dat is de uitleg van "dé" en de accentloze sleutel maakt die twee gelijk. */
var LEES_LETTERS = {y:["en","and"], o:["of","or"], a:["naar, aan, tot","to, at"],
                    de:["van, uit","of, from"],""",
    )
    rep(
        """  if(LEES_LETTERS[plat]) return {es:plat, nl:ct(LEES_LETTERS[plat][0], LEES_LETTERS[plat][1]), soort:"woordenboek"};""",
        """  /* v23.252: op het geschreven woord, met accent en al. Op de accentloze sleutel zou "d\u00e9" hier
     ook binnenkomen en het voorzetsel-antwoord krijgen, en dan hebben we de fout omgedraaid in
     plaats van opgelost. */
  var geschreven = String(ruw || "").toLowerCase().replace(/[^a-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00fc\u00f1]/g, "");
  if(LEES_LETTERS[geschreven]) return {es:geschreven, nl:ct(LEES_LETTERS[geschreven][0], LEES_LETTERS[geschreven][1]), soort:"woordenboek"};""",
    )

    kaal = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    kaal = "\n".join([r.split("//")[0] for r in kaal.split("\n")])
    assert kaal.count("function leesVormKaart(") == 1, "leesVormKaart niet precies een keer"
    assert kaal.count("function leesBetekenisKaal(") == 1, "de kale opzoeker staat er niet"
    assert kaal.count("function leesBetekenis(") == 1, "leesBetekenis niet precies een keer"
    assert kaal.count("function leesTekstTijden(") == 1, "leesTekstTijden niet precies een keer"
    assert kaal.count("vormRegel") == 4, "de vormregel wordt niet gebouwd en getoond"
    assert "de:[\"van, uit\"" in kaal, "het voorzetsel de staat niet in LEES_LETTERS"
    assert kaal.count("LEES_LETTERS[geschreven]") == 3, "de letterlijst wordt niet op het geschreven woord gelezen"
    APP.write_text(src, encoding="utf-8")
    print("index.html: de leesplank zegt welke vorm er staat, en of je die tijd al had")
else:
    print("index.html: stond er al")

nieuw, doe_ver, reden = patchhulp.nummerKiezen(huidig, GEPLAND, DOE_APP)
if reden:
    print("LET OP: " + reden)
if doe_ver:
    patchhulp.zetVersie(APP, VER, huidig, nieuw)
    print("versie.txt: %s -> %s" % (huidig, nieuw))
else:
    print("versie.txt: stond al op " + huidig)
