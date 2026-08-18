#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.127: de zevende rij. Door elkaar produceren, en "welk patroon is dit?" gaat eruit.

## De hoofdvraag, toegepast

Stefan: "ja als dat helpt om Spaans te leren ja dan wel. dus ga iedere keer weer terug naar deze
hoofdvraag."

Dus die vraag eerst gesteld over stap 7 zoals ik hem zelf had ingepland, "Welk patroon is dit?".
Het antwoord is nee, en om een reden die ik had moeten zien voor ik hem opschreef:

    vraag je het patroon bij een INFINITIEF     onleerbaar
    vraag je het patroon bij een VERVOEGDE VORM triviaal

Onleerbaar, want welk werkwoord een schoen draagt is lexicaal willekeurig: pensar wordt pienso,
maar pesar wordt peso. Allebei -ar, allebei een e in de stam. Je kunt het niet afleiden, alleen
onthouden. Triviaal in de andere richting, want in "pienso" staat de ie gewoon te lezen.

En bovendien traint labelen het labelen. Skill Acquisition Theory is er ondubbelzinnig over: je
krijgt waar je op oefent. De vaardigheid die Stefan wil is de vorm PRODUCEREN, niet hem benoemen.

## Wat er wel ontbreekt

De zes lessen zijn geblokt: één rij tegelijk, geen andere rij in beeld. De hertoets mengt, maar die
komt pas na drie dagen en is tien vragen lang, pass/fail. Daartussen zit niets.

Dat gat is precies waar de spreidingsliteratuur over gaat: interleaving verslaat blokken op de
UITGESTELDE toets, maar alleen ná het blokken (Rohrer; Nakata & Suzuki voor grammatica). Wat de
route mist is één stap gemengd produceren, zo vaak als je wilt, vandaag.

Stap 7 wordt daarom: **de 22 door elkaar, typen, zonder tabel.**

## Hoe

Niet als nieuw scherm. "De les" onderwijst sinds v23.125 een RIJ, en een rij hoeft geen patroon te
zijn: een zevende rij is de vergaarbak van alle zes. Het enige nieuwe is dat bij zo'n rij élke
vraagstap uit de pool trekt in plaats van uit één modelwerkwoord. Alle zes de stappen, de nakijker,
de voortgang en de overdrachtsstap blijven wat ze waren.

Daarbij één stille fout rechtgezet die er al zat: stap 2, 3 en 4 tekenden de tabel van het
LESWERKWOORD terwijl de vraag over het werkwoord van de opgave ging. Bij een gewone rij zijn dat
dezelfde twee, dus het viel niet op. Bij een gemengde rij zou het scherm het antwoord bij het
verkeerde rijtje laten zoeken.

## De route wordt

    1 -go   2 e->ie   3 o/u->ue   4 e->i   5 -oy   6 de twee losse
    7 de 22 door elkaar          <- was "welk patroon is dit? (komt nog)"
    8 gestold?

Acht stappen, en nu bestaan ze alle acht. De teller gaat van 0/7 naar 0/8.
"""

import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.127"

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


# ------------- 1. de zevende rij: alle 22 door elkaar

rep(
    '''function lesId(t){ return "les." + t; }''',
    '''/* De werkwoorden die in minstens \\u00e9\\u00e9n patroonrij staan: de 22 onregelmatige van het presente.
   Niet geteld maar afgeleid, zodat het getal 22 nergens als getal in dit bestand staat. */
function conjOnregPool(){
  return VERBOS.filter(function(v){ return conjPatroonAantal(v) > 0; });
}
/* ===== v23.127: een rij hoeft geen patroon te zijn =====

   Stefan: "ja als dat helpt om Spaans te leren ja dan wel. dus ga iedere keer weer terug naar deze
   hoofdvraag."

   Die vraag gesteld over de stap die hier stond ingepland, "Welk patroon is dit?", geeft nee. Welk
   werkwoord een schoen draagt is lexicaal willekeurig (pensar \\u2192 pienso, maar pesar \\u2192 peso), dus
   vanuit de infinitief is het onleerbaar; en vanuit de vervoegde vorm staat de ie gewoon te lezen,
   dus dan is het triviaal. Bovendien traint labelen het labelen, en de vaardigheid die je wilt is
   de vorm produceren.

   Wat de route w\\u00e9l mist is de stap tussen blokken en de hertoets in: gemengd produceren, zo vaak
   als je wilt, vandaag. Interleaving verslaat blokken op de uitgestelde toets, maar alleen n\\u00e1 het
   blokken.

   Dat is deze rij: geen patroon maar de vergaarbak van alle zes. Het enige wat een mengrij anders
   doet is dat \\u00e9lke vraagstap uit de pool trekt in plaats van uit \\u00e9\\u00e9n modelwerkwoord. */
var LES_MIXRIJEN = [
  {id:"presente.mix", t:"presente",
   es:"las seis, mezcladas", nl:"de zes patronen door elkaar", en:"the six patterns, mixed",
   doet:"Alle onregelmatige werkwoorden van het presente door elkaar, uit alle zes de rijen. Tot nu toe deed je \\u00e9\\u00e9n rij tegelijk; hier moet je bij elk werkwoord zelf weten welke kant het op gaat.",
   doetEn:"All the irregular present-tense verbs mixed, from all six rows. Until now you did one row at a time; here you have to know for yourself which way each verb goes.",
   vorm:"Geen tabel, en geen aankondiging welk patroon eraan komt. Dat is het punt: door elkaar is de laatste stap, niet de eerste.",
   vormEn:"No table, and no warning which pattern is coming. That is the point: mixing comes last, not first.",
   pool:function(){ return conjOnregPool(); }}
];
function lesMixVan(id){
  for(var i = 0; i < LES_MIXRIJEN.length; i++) if(LES_MIXRIJEN[i].id === id) return LES_MIXRIJEN[i];
  return null;
}

function lesId(t){ return "les." + t; }''',
)

rep(
    '''  var pat = conjPatroonVan(id);
  if(!pat) return null;
  var pool = conjPatroonPool(id);
  if(!pool.length) return null;
  var v0 = conjPatroonModel(id);
  return {id:id, t:"presente", tijd:false, es:pat.es, nl:pat.nl, en:pat.en,
          doet:pat.doet, doetEn:pat.doetEn, vorm:pat.vorm, vormEn:pat.vormEn,
          vb:conjVorm(v0, 0, "presente"), vbNl:conjGloss(v0), vbEn:conjGloss(v0), v:v0,
          pool:function(lesV){ return pool.filter(function(w){ return w.inf !== lesV.inf; }); }};
}''',
    '''  var mix = lesMixVan(id);
  if(mix){
    var mp = mix.pool();
    if(mp.length < 2) return null;
    var m0 = mp[0];
    return {id:id, t:mix.t, tijd:false, mix:true, es:mix.es, nl:mix.nl, en:mix.en,
            doet:mix.doet, doetEn:mix.doetEn, vorm:mix.vorm, vormEn:mix.vormEn,
            vb:conjVorm(m0, 0, mix.t), vbNl:conjGloss(m0), vbEn:conjGloss(m0), v:m0,
            pool:function(lesV){ return mp.filter(function(w){ return w.inf !== (lesV || {}).inf; }); }};
  }
  var pat = conjPatroonVan(id);
  if(!pat) return null;
  var pool = conjPatroonPool(id);
  if(!pool.length) return null;
  var v0 = conjPatroonModel(id);
  return {id:id, t:"presente", tijd:false, es:pat.es, nl:pat.nl, en:pat.en,
          doet:pat.doet, doetEn:pat.doetEn, vorm:pat.vorm, vormEn:pat.vormEn,
          vb:conjVorm(v0, 0, "presente"), vbNl:conjGloss(v0), vbEn:conjGloss(v0), v:v0,
          pool:function(lesV){ return pool.filter(function(w){ return w.inf !== lesV.inf; }); }};
}''',
)

rep(
    '''function lesRijIds(){
  var uit = conjOpenTijden().slice();
  CONJ_PATRONEN.forEach(function(p){ if(conjPatroonPool(p.id).length) uit.push(p.id); });
  return uit;
}''',
    '''function lesRijIds(){
  var uit = conjOpenTijden().slice();
  CONJ_PATRONEN.forEach(function(p){ if(conjPatroonPool(p.id).length) uit.push(p.id); });
  /* de mengrijen achteraan: door elkaar is de laatste stap, niet de eerste */
  LES_MIXRIJEN.forEach(function(m){ if(lesRij(m.id)) uit.push(m.id); });
  return uit;
}''',
)

# ------------- 2. bij een mengrij trekt elke vraagstap uit de pool

rep(
    '''function lesOpgaveNu(){
  if(!lesSpel) return null;
  var rij = lesPersoonRij(lesSpel.stap);
  if(lesStapId(lesSpel.stap) === "overdracht"){
    var o = lesOverNu();
    return o.length ? o[lesSpel.i % o.length] : null;
  }
  return {v:lesSpel.v, p:rij[lesSpel.i % rij.length]};
}''',
    '''function lesOpgaveNu(){
  if(!lesSpel) return null;
  var rij = lesPersoonRij(lesSpel.stap);
  /* v23.127: bij een mengrij is er geen modelwerkwoord om op terug te vallen, dus trekt \\u00e9lke
     vraagstap uit de pool. Bij een gewone rij verandert er niets. */
  var r = lesRij(lesSpel.rij);
  if(lesStapId(lesSpel.stap) === "overdracht" || (r && r.mix)){
    var o = lesOverNu();
    return o.length ? o[lesSpel.i % o.length] : null;
  }
  return {v:lesSpel.v, p:rij[lesSpel.i % rij.length]};
}''',
)

# ------------- 3. het scherm toonde de tabel van het leswerkwoord, niet van de opgave

rep(
    '''      if(!L.opties) L.opties = geschud(conjAlleVormen(v, L.t).filter(function(f, i, a){ return a.indexOf(f) === i; })).slice(0, 4);
      if(L.opties.indexOf(goedeVorm) === -1) L.opties = geschud([goedeVorm].concat(L.opties.slice(0, 3)));
      html += "<p class='muted'>" + ct("Welke vorm hoort bij <b>" + CONJ_PRONOMBRES[p] + "</b>?",
                                       "Which form goes with <b>" + CONJ_PRONOMBRES[p] + "</b>?") + "</p>" +
        "<div class='card'>" + lesTabelHtml(v, L.t, -1) + "</div>" +''',
    '''      /* v23.127: qv en niet v. Dit stond er al fout: de tabel en de keuzes kwamen van het
         leswerkwoord terwijl de vraag over het werkwoord van de opgave ging. Bij een gewone rij
         zijn dat dezelfde twee, dus het viel niet op; bij een mengrij zou het scherm het antwoord
         bij het verkeerde rijtje laten zoeken. */
      if(!L.opties) L.opties = geschud(conjAlleVormen(qv, L.t).filter(function(f, i, a){ return a.indexOf(f) === i; })).slice(0, 4);
      if(L.opties.indexOf(goedeVorm) === -1) L.opties = geschud([goedeVorm].concat(L.opties.slice(0, 3)));
      html += "<p class='muted'>" + ct("Welke vorm hoort bij <b>" + CONJ_PRONOMBRES[p] + "</b> van <b>" + qv.inf + "</b>?",
                                       "Which form goes with <b>" + CONJ_PRONOMBRES[p] + "</b> of <b>" + qv.inf + "</b>?") + "</p>" +
        "<div class='card'>" + lesTabelHtml(qv, L.t, -1) + "</div>" +''',
)

rep(
    '''          : ct("Zonder tabel. <b>" + CONJ_PRONOMBRES[p] + "</b> van <b>" + v.inf + "</b>, in de " + x.es + ".",
               "No table. <b>" + CONJ_PRONOMBRES[p] + "</b> of <b>" + v.inf + "</b>, in the " + x.es + ".")) + "</p>" +
        (verberg >= 0 ? "<div class='card'>" + lesTabelHtml(v, L.t, verberg) + "</div>" : "") +''',
    '''          : ct("Zonder tabel. <b>" + CONJ_PRONOMBRES[p] + "</b> van <b>" + qv.inf + "</b>, in de " + x.es + ".",
               "No table. <b>" + CONJ_PRONOMBRES[p] + "</b> of <b>" + qv.inf + "</b>, in the " + x.es + ".")) + "</p>" +
        (verberg >= 0 ? "<div class='card'>" + lesTabelHtml(qv, L.t, verberg) + "</div>" : "") +''',
)

# stap 3 (het gat) toont bij een mengrij ook welk werkwoord het is, anders is het gat onoplosbaar
rep(
    '''      html += "<p class='muted'>" + (verberg >= 0
          ? ct("Vul het gat in: <b>" + CONJ_PRONOMBRES[p] + "</b>", "Fill the gap: <b>" + CONJ_PRONOMBRES[p] + "</b>")''',
    '''      html += "<p class='muted'>" + (verberg >= 0
          ? ct("Vul het gat in: <b>" + CONJ_PRONOMBRES[p] + "</b> van <b>" + qv.inf + "</b>",
               "Fill the gap: <b>" + CONJ_PRONOMBRES[p] + "</b> of <b>" + qv.inf + "</b>")''',
)

# de zin "in de <rij>" leest alleen goed als de rij een tijd is
rep(
    '''          : ct("Zonder tabel. <b>" + CONJ_PRONOMBRES[p] + "</b> van <b>" + qv.inf + "</b>, in de " + x.es + ".",
               "No table. <b>" + CONJ_PRONOMBRES[p] + "</b> of <b>" + qv.inf + "</b>, in the " + x.es + ".")) + "</p>" +''',
    '''          : ct("Zonder tabel. <b>" + CONJ_PRONOMBRES[p] + "</b> van <b>" + qv.inf + "</b>" + (x.tijd ? ", in de " + x.es : "") + ".",
               "No table. <b>" + CONJ_PRONOMBRES[p] + "</b> of <b>" + qv.inf + "</b>" + (x.tijd ? ", in the " + x.es : "") + ".")) + "</p>" +''',
)

# ------------- 4. "in deze rij" past niet bij 22 werkwoorden

rep(
    '''      (x.tijd ? "" :
        "<p class='muted' style='margin:8px 0 0; font-size:.85rem'>" +
          ct("In deze rij: ", "In this row: ") +
          conjPatroonPool(L.rij).map(function(w){ return w.inf; }).join(", ") + "</p>") + "</div>" +''',
    '''      (x.tijd ? "" :
        "<p class='muted' style='margin:8px 0 0; font-size:.85rem'>" +
          (x.mix
            /* de 22 opsommen leest als een muur; de zes rijen zijn juist wat je hier moet zien */
            ? ct("De zes rijen: ", "The six rows: ") +
              CONJ_PATRONEN.map(function(pt){ return ct(pt.nl, pt.en) + " (" + conjPatroonPool(pt.id).length + ")"; }).join(", ")
            : ct("In deze rij: ", "In this row: ") +
              conjPatroonPool(L.rij).map(function(w){ return w.inf; }).join(", ")) + "</p>") + "</div>" +''',
)

# ------------- 5. de route: stap 7 bestaat nu

rep(
    '''     {brok:"presente.patroon", soort:"keuze", view:null,
      nl:"Welk patroon is dit?", en:"Which pattern is this?",
      subNl:"Komt nog. Door elkaar herkennen is de laatste stap, niet de eerste.",
      subEn:"Coming. Telling them apart comes last, not first."},''',
    '''     /* v23.127: hier stond "Welk patroon is dit?", en die stap gaat eruit. Vanuit de infinitief is
        het patroon onleerbaar (pensar \\u2192 pienso, pesar \\u2192 peso) en vanuit de vervoegde vorm
        triviaal, en labelen traint labelen. Wat de route mist is gemengd produceren. */
     {brok:"les.presente.mix", soort:"les", view:"les", arg:"presente.mix",
      nl:"De zes door elkaar", en:"The six, mixed",
      subNl:"Alle onregelmatige werkwoorden uit alle zes de rijen, zonder tabel en zonder aankondiging welk patroon eraan komt.",
      subEn:"All the irregular verbs from all six rows, with no table and no warning which pattern is coming."},''',
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
