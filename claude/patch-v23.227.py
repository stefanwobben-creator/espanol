#!/usr/bin/env python3
# v23.227 - het indefinido krijgt dezelfde soort rijen als het presente
#
# Stefan, 1 sep: "de grammatica dat gaat niet helemaal goed. ik mis daar denk ik goede uitleg /
# instructie op het moment. ik moet zeggen dat werkwoorden vervoegen (presente) nu wel goed gaat dus
# die vorm kunnen we ook voor de andere tijdsvormen voor werkwoorden."
#
# WAT DE METING LAAT ZIEN
#
# De vorm die werkt bestaat al: "De les" (LES_STAPPEN) doet één rijtje per keer in zes stappen, van
# ontmoeten tot nieuwe werkwoorden. En die les werkt al voor elke open tijd. Het verschil zit niet in
# de vorm maar in het AANTAL rijen:
#
#     presente     1 tijdrij + 6 patroonrijen  (de schoen ie/ue/i, yo op -go/-oy, de losse twee)
#     indefinido   1 tijdrij                   en verder niets
#     imperfecto   1 tijdrij                   en verder niets
#     perfecto     1 tijdrij                   en verder niets
#
# CONJ_PATRONEN is namelijk volledig op het presente gebouwd: conjPatroon() leest v.presente en
# lesRij() zet er hardgecodeerd t:"presente" bij. Voor het presente zijn de 22 onregelmatige dus in
# zes behapbare families opgeknipt, elk met een eigen uitleg en een eigen ladder. Voor het
# indefinido staan de twintig onregelmatige in één berg.
#
# Dat is precies wat Stefan voelde: het presente gaat goed omdat het in stukken is geknipt, en de
# andere tijden gaan niet goed omdat dat daar nooit is gebeurd.
#
# DE ZES RIJEN VAN HET INDEFINIDO
#
# Uit de data afgeleid, niet met de hand opgesomd (staat een feit in de data, dan schrijft geen
# enkele codeplek dat feit opnieuw). Van de 33 werkwoorden zijn er 13 regelmatig en 20 niet:
#
#     indef.u       estar, tener, poder, saber, poner     sterke stam met een u
#     indef.i       hacer, querer, venir, decir           sterke stam met een i
#     indef.fui     ser, ir                               allebei fui: één rijtje, twee betekenissen
#     indef.kort    dar, ver                              di, vi: twee letters, geen accenten
#     indef.derde   pedir, dormir, sentir, preferir, leer alleen hij/zij en zij veranderen
#     indef.schrijf empezar, jugar                        alleen de ik-vorm, en alleen op papier
#
# Zes tegen zes. Twee families die zich als eigen rij aandienden zijn er bewust niet: decir (de
# j-stam) en leer (de klinkerstam) zouden allebei een rij van één werkwoord opleveren, en zo'n rij
# kan stap 6 niet lopen ("nu een werkwoord dat je nog niet gezien hebt"). Die stap is juist het
# bewijs dat je een patroon kent en geen woord. Ze staan nu als uitzondering in de rij waar ze
# horen, met hun regel er voluit bij. De sterke stammen (de eerste drie rijen) zijn samen negen werkwoorden en
# ze delen precies één ding: hun uitgangen dragen géén accent. Dat is de zin die deze hele tijd
# ontsluit, en hij stond nergens op het scherm.
#
# WAT ER TECHNISCH VERANDERT
#
# 1. Een patroonrij weet in welke TIJD hij woont (`t`) en hoe je hem herkent (`pas`). Tot nu toe
#    zat dat in conjInPatroon(), die alleen de presente-analyse kende.
# 2. conjPatroonAantal() en conjOnregPool() worden per tijd geteld. Zonder dat zou "in hoeveel
#    rijen staat dit werkwoord" over tijden heen tellen, en dan kiest conjPatroonModel() een
#    voorbeeld dat in zijn eigen tijd juist wél alleen staat.
# 3. De poort. De presente-patronen gaan open bij fase "onreg" (v23.131); een indefinido-patroon
#    gaat open zodra het indefinido zelf open is. Anders krijgt iemand die net begint een rij over
#    dije en dijeron.
#
# WAT DEZE RONDE NIET DOET
#
# Het imperfecto, het perfecto en de subjuntivo. Die krijgen dezelfde behandeling zodra deze
# gezien is: imperfecto heeft er drie uitzonderingen in de hele taal (ser, ir, ver) en dat is één
# rij, het perfecto splitst op regelmatige tegenover onregelmatige deelwoorden, en de subjuntivo op
# de yo-stam tegenover de zes die niets volgen. Eerst deze, dan die.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.227"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = 'id:"indef.u"' not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:110])
    src = src.replace(anker, nieuw, n)

if DOE_APP:
    # =========================================================================================
    # 1. de verwachte regelmatige vormen op één plek
    #
    # conjRegelmatigIn() rekende ze zelf uit en gooide ze weg. De nieuwe herkenners hebben ze
    # nodig om te kunnen zeggen WELKE plek afwijkt, dus staan ze nu apart.
    # =========================================================================================
    rep("""function conjRegelmatigIn(v, t){
  var m = VERBOS.filter(function(w){ return w.inf === LES_MODEL[conjGroep(v)]; })[0];
  if(!m || !conjHeeftTijd(v, t) || !conjHeeftTijd(m, t)) return false;
  var s = v.inf.slice(0, -2), ms = m.inf.slice(0, -2);
  var verwacht = conjAlleVormen(m, t).map(function(f){ return f.split(ms).join(s); });
  return JSON.stringify(verwacht) === JSON.stringify(conjAlleVormen(v, t));
}""",
"""/* v23.227: de zes vormen die dit werkwoord in deze tijd zou hebben als het zich netjes gedroeg.
   Stond ingebakken in conjRegelmatigIn(), die ze uitrekende en weggooide. De patroonherkenners van
   het indefinido hebben ze nodig om te kunnen zeggen wélke plek afwijkt, en twee plekken die
   hetzelfde uitrekenen zijn twee waarheden. */
function conjVerwachtIn(v, t){
  var m = VERBOS.filter(function(w){ return w.inf === LES_MODEL[conjGroep(v)]; })[0];
  if(!m || !conjHeeftTijd(v, t) || !conjHeeftTijd(m, t)) return null;
  var s = v.inf.slice(0, -2), ms = m.inf.slice(0, -2);
  return conjAlleVormen(m, t).map(function(f){ return f.split(ms).join(s); });
}
function conjRegelmatigIn(v, t){
  var verwacht = conjVerwachtIn(v, t);
  if(!verwacht) return false;
  return JSON.stringify(verwacht) === JSON.stringify(conjAlleVormen(v, t));
}""")

    # =========================================================================================
    # 2. de herkenners van het indefinido
    # =========================================================================================
    rep("""var CONJ_PATRONEN = [""",
"""/* ================= DE RIJEN VAN HET INDEFINIDO (v23.227) =================

   Zes families, alle zes uit de vormen zelf afgeleid en niet uit een lijstje werkwoorden. Zet
   iemand er morgen een werkwoord bij, dan valt het vanzelf in de goede rij; een handgeschreven
   lijst zou dan stil achterlopen.

   DE ZIN DIE DEZE TIJD ONTSLUIT staat in indefSterk(): bij de negen sterke stammen dragen de
   uitgangen géén accent. hablé en habló hebben er een, estuve en estuvo niet. Dat ene verschil is
   waaraan je ze herkent, en het stond nergens op het scherm. */
function indefVormen(v){
  try { return conjHeeftTijd(v, "indefinido") ? conjAlleVormen(v, "indefinido") : null; }
  catch(e){ return null; }
}
function indefStam(v){
  var f = indefVormen(v);
  return f ? conjKaal(f[0]).slice(0, -1) : "";   // estuve -> estuv, hice -> hic, dije -> dij
}
/* Een sterke stam: de ik-vorm eindigt op een onbeklemtoonde e en de hij-vorm op een
   onbeklemtoonde o. Bij een regelmatig werkwoord staat daar juist wél een accent. */
function indefSterk(v){
  var f = indefVormen(v);
  if(!f) return false;
  return /e$/.test(f[0]) && !/[\\u00e1\\u00e9\\u00ed\\u00f3\\u00fa]/.test(f[0]) &&
         /o$/.test(f[2]) && !/[\\u00e1\\u00e9\\u00ed\\u00f3\\u00fa]/.test(f[2]);
}
/* De klinker van de sterke stam. "qu" telt niet mee als u: die u is een spelregel en geen klank,
   en zonder deze regel zou querer (quis) in de u-rij landen in plaats van bij de i.

   Geen aparte j-rij: dije heeft een i in de stam en hoort dus gewoon bij de i-groep. De j valt daar
   op zijn plek als uitzondering op één uitgang (dijeron, niet dijieron), en dat is beter dan een
   eigen rij met één werkwoord erin. Een rij met één werkwoord kan stap 6 niet lopen, en die stap
   ("nu een werkwoord dat je nog niet gezien hebt") is juist het bewijs dat je een patroon kent en
   geen woord. */
function indefSterkSoort(v){
  if(!indefSterk(v)) return null;
  var s = indefStam(v);
  return /u/.test(s.split("qu").join("k")) ? "u" : "i";
}
/* Geen enkele letter van de infinitief komt terug: ser en ir worden allebei fui. Dat ze samenvallen
   is het hele punt van deze rij, en het is de verwarring die je in elke tekst tegenkomt. */
function indefSuppletief(v){
  var f = indefVormen(v);
  if(!f) return false;
  return conjKaal(f[0]).charAt(0) !== conjKaal(v.inf).charAt(0);
}
function indefKort(v){
  var f = indefVormen(v);
  return !!f && !indefSuppletief(v) && conjKaal(f[0]).length <= 2;
}
/* Alleen de derde personen wijken af: pidi\\u00f3 en pidieron, leyó en leyeron. Twee verschillende
   oorzaken (de klinker verspringt, of de i wordt een y) maar op het scherm precies één regel: de
   rest van het rijtje is gewoon. */
function indefAlleenDerde(v){
  var f = indefVormen(v), w = conjVerwachtIn(v, "indefinido");
  if(!f || !w) return false;
  /* Zonder accenten vergeleken, en dat is precies waarom leer hier hoort. Le\u00edste draagt een
     accent dat comiste niet heeft, maar dat is dezelfde botsing van klinkers die ook de y van
     ley\u00f3 veroorzaakt: \u00e9\u00e9n oorzaak, en de plek waar het zichtbaar wordt is dezelfde als bij pedir. */
  var kaal = function(x){ return conjKaal(x); };
  var zelfde = [0, 1, 3, 4].every(function(i){ return kaal(f[i]) === kaal(w[i]); });
  return zelfde && (kaal(f[2]) !== kaal(w[2]) || kaal(f[5]) !== kaal(w[5]));
}
/* Alleen de ik-vorm, en alleen op papier: empec\\u00e9 en jugu\\u00e9 klinken precies zoals je ze zou
   verwachten. De c en de gu staan er om de klank te bewaren, niet om hem te veranderen. */
function indefAlleenSchrijf(v){
  var f = indefVormen(v), w = conjVerwachtIn(v, "indefinido");
  if(!f || !w) return false;
  var rest = [1, 2, 3, 4, 5].every(function(i){ return f[i] === w[i]; });
  return rest && f[0] !== w[0];
}

var CONJ_PATRONEN = [""")

    # =========================================================================================
    # 3. elke rij weet zijn tijd en zijn herkenner
    # =========================================================================================
    for sleutel, pas in [
        ('{id:"schoen.ie", soort:"schoen", sleutel:"ie",',
         '{id:"schoen.ie", t:"presente", pas:function(v){ return conjPatroon(v).wissel === "ie"; },'),
        ('{id:"schoen.ue", soort:"schoen", sleutel:"ue",',
         '{id:"schoen.ue", t:"presente", pas:function(v){ return conjPatroon(v).wissel === "ue"; },'),
        ('{id:"yo.go", soort:"yo", sleutel:"go",',
         '{id:"yo.go", t:"presente", pas:function(v){ return conjPatroon(v).yo === "go"; },'),
        ('{id:"yo.oy", soort:"yo", sleutel:"oy",',
         '{id:"yo.oy", t:"presente", pas:function(v){ return conjPatroon(v).yo === "oy"; },'),
        ('{id:"schoen.i", soort:"schoen", sleutel:"i",',
         '{id:"schoen.i", t:"presente", pas:function(v){ return conjPatroon(v).wissel === "i"; },'),
        ('{id:"yo.los", soort:"yo", sleutel:"los",',
         '{id:"yo.los", t:"presente", pas:function(v){ return conjPatroon(v).yo === "los"; },'),
    ]:
        rep(sleutel, pas)

    # =========================================================================================
    # 4. de zeven nieuwe rijen
    # =========================================================================================
    rep("""   vorm:"s\\u00e9 en veo. Verder doen ze allebei gewoon mee.",
   vormEn:"s\\u00e9 and veo. Otherwise they behave normally."}
];""",
"""   vorm:"s\\u00e9 en veo. Verder doen ze allebei gewoon mee.",
   vormEn:"s\\u00e9 and veo. Otherwise they behave normally."},

  /* v23.227: en dezelfde behandeling voor het indefinido. Zie de kop bij indefVormen() voor waarom
     deze zeven rijen zo lopen. De volgorde is de leervolgorde: eerst de drie sterke stammen die
     samen negen werkwoorden dekken, dan de vier kleine families. */
  {id:"indef.u", t:"indefinido", pas:function(v){ return indefSterkSoort(v) === "u"; },
   es:"el pret\\u00e9rito fuerte: la u",
   nl:"de sterke stam met een u", en:"the strong stem with a u",
   doet:"Vijf werkwoorden krijgen in het indefinido een compleet andere stam, met een u erin. En dan gebeurt er iets dat voor alle sterke stammen geldt: de uitgangen dragen G\\u00c9\\u00c9N accent. Vergelijk habl\\u00e9 en habl\\u00f3 met estuve en estuvo. Dat ene verschil is waaraan je ze herkent.",
   doetEn:"Five verbs take a completely different stem in the preterite, with a u in it. And then something happens that holds for every strong stem: the endings carry NO accent. Compare habl\\u00e9 and habl\\u00f3 with estuve and estuvo. That one difference is how you spot them.",
   vorm:"estuve, tuve, pude, supe, puse. En dan: -e, -iste, -o, -imos, -isteis, -ieron.",
   vormEn:"estuve, tuve, pude, supe, puse. And then: -e, -iste, -o, -imos, -isteis, -ieron."},
  {id:"indef.i", t:"indefinido", pas:function(v){ return indefSterkSoort(v) === "i"; },
   es:"el pret\\u00e9rito fuerte: la i",
   nl:"de sterke stam met een i", en:"the strong stem with an i",
   doet:"Dezelfde sterke stam, andere klinker: hier zit een i. De uitgangen zijn precies dezelfde en dragen ook hier geen accent. Bij hacer verandert alleen de hij-vorm nog van schrijfwijze, want hice + o zou \\\"hico\\\" klinken.",
   doetEn:"The same strong stem, another vowel: here it is an i. The endings are exactly the same and carry no accent either. With hacer only the he-form changes its spelling, because hice + o would sound like \\\"hico\\\".",
   vorm:"hice, quise, vine. En hizo, met een z.",
   vormEn:"hice, quise, vine. And hizo, with a z."},
  {id:"indef.fui", t:"indefinido", pas:indefSuppletief,
   es:"fui: ser e ir",
   nl:"fui: ser en ir zijn hetzelfde", en:"fui: ser and ir are identical",
   doet:"Ser en ir hebben in het indefinido precies hetzelfde rijtje, letter voor letter. Fui betekent dus \\\"ik was\\\" \\u00e9n \\\"ik ging\\\", en welke van de twee het is zegt alleen de zin eromheen. Er komt geen enkele letter van de infinitief in terug.",
   doetEn:"Ser and ir have exactly the same row in the preterite, letter for letter. So fui means both \\\"I was\\\" and \\\"I went\\\", and only the surrounding sentence says which. Not a single letter of the infinitive comes back.",
   vorm:"fui, fuiste, fue, fuimos, fuisteis, fueron. Twee werkwoorden, \\u00e9\\u00e9n rijtje.",
   vormEn:"fui, fuiste, fue, fuimos, fuisteis, fueron. Two verbs, one row."},
  {id:"indef.kort", t:"indefinido", pas:indefKort,
   es:"di y vi",
   nl:"de twee kortste vormen", en:"the two shortest forms",
   doet:"Dar en ver zijn de kleinste van de tijd: di en vi, twee letters, zonder accent. Dar pakt bovendien de uitgangen van de -er-groep, terwijl het zelf op -ar eindigt. Twee rijtjes om gewoon te onthouden, en dat mag: twee is te doen.",
   doetEn:"Dar and ver are the smallest of the tense: di and vi, two letters, no accent. Dar also takes the -er endings while it ends in -ar itself. Two rows to simply memorise, and that is fine: two is doable.",
   vorm:"di, diste, dio, dimos, disteis, dieron. En vi, viste, vio, vimos, visteis, vieron.",
   vormEn:"di, diste, dio, dimos, disteis, dieron. And vi, viste, vio, vimos, visteis, vieron."},
  {id:"indef.derde", t:"indefinido", pas:indefAlleenDerde, model:"pedir",
   es:"solo la tercera persona",
   nl:"alleen hij/zij en zij veranderen", en:"only the third persons change",
   doet:"Vier van de zes vormen zijn hier volkomen gewoon. Alleen bij hij/zij en bij zij gebeurt er iets: bij de -ir-werkwoorden verspringt de klinker (pidi\\u00f3, durmi\\u00f3, sinti\\u00f3) en bij leer wordt de i een y, omdat drie klinkers achter elkaar niet uit te spreken zijn. Andere oorzaak, dezelfde plek.",
   doetEn:"Four of the six forms are completely ordinary here. Only at he/she and at they does something happen: in the -ir verbs the vowel shifts (pidi\\u00f3, durmi\\u00f3, sinti\\u00f3) and in leer the i becomes a y, because three vowels in a row cannot be pronounced. Different cause, same place.",
   vorm:"ped\\u00ed, pediste, PIDI\\u00d3, pedimos, pedisteis, PIDIERON.",
   vormEn:"ped\\u00ed, pediste, PIDI\\u00d3, pedimos, pedisteis, PIDIERON."},
  {id:"indef.schrijf", t:"indefinido", pas:indefAlleenSchrijf,
   es:"solo la ortograf\\u00eda",
   nl:"alleen de schrijfwijze van yo", en:"only the spelling of the yo form",
   doet:"Deze twee zijn eigenlijk gewoon regelmatig. Alleen de ik-vorm wordt anders geschreven, en alleen om de klank te bewaren: empez\\u00e9 zou met een z voor een e als een s klinken, en jug\\u00e9 zou de g zacht maken. Je hoort niets bijzonders, je ziet het alleen.",
   doetEn:"These two are really just regular. Only the I-form is spelled differently, and only to keep the sound: empez\\u00e9 with a z before an e would sound like an s, and jug\\u00e9 would soften the g. You hear nothing special, you only see it.",
   vorm:"empec\\u00e9 en jugu\\u00e9. Verder: empezaste, empez\\u00f3, jugaste, jug\\u00f3.",
   vormEn:"empec\\u00e9 and jugu\\u00e9. Then: empezaste, empez\\u00f3, jugaste, jug\\u00f3."}
];""")

    # =========================================================================================
    # 5. de herkenning, de telling en de poort worden per tijd
    # =========================================================================================
    rep("""function conjInPatroon(v, pat){
  var p = conjPatroon(v);
  return pat.soort === "schoen" ? p.wissel === pat.sleutel : p.yo === pat.sleutel;
}""",
"""/* v23.227: elke rij draagt zijn eigen herkenner. Hier stond een keuze tussen "schoen" en "yo", en
   allebei lazen ze conjPatroon(), die alleen naar v.presente kijkt. Een rij in een andere tijd
   paste daar niet in, en dat is precies waarom er nooit een gekomen is. */
function conjInPatroon(v, pat){
  if(!pat || typeof pat.pas !== "function") return false;
  try { return !!pat.pas(v); } catch(e){ return false; }
}
function conjPatroonTijd(pat){ return (pat && pat.t) || "presente"; }""")
    rep("""/* In hoeveel rijen staat dit werkwoord? Drie staan er in twee (tener, venir, decir). */
function conjPatroonAantal(v){
  var n = 0;
  CONJ_PATRONEN.forEach(function(p){ if(conjInPatroon(v, p)) n++; });
  return n;
}""",
"""/* In hoeveel rijen staat dit werkwoord? In het presente staan er drie in twee (tener, venir,
   decir).

   v23.227: per tijd geteld. Zonder die grens zou het over tijden heen tellen, en dan zou
   conjPatroonModel() bij het indefinido een voorbeeld afwijzen dat daar juist alleen staat omdat
   het toevallig ook in een presente-rij zit. */
function conjPatroonAantal(v, t){
  var tijd = t || "presente", n = 0;
  CONJ_PATRONEN.forEach(function(p){
    if(conjPatroonTijd(p) === tijd && conjInPatroon(v, p)) n++;
  });
  return n;
}""")
    rep("""function conjPatroonModel(id){
  var pool = conjPatroonPool(id);
  for(var i = 0; i < pool.length; i++) if(conjPatroonAantal(pool[i]) === 1) return pool[i];
  return pool[0] || null;
}""",
"""function conjPatroonModel(id){
  var pat = conjPatroonVan(id), pool = conjPatroonPool(id), t = conjPatroonTijd(pat), i;
  /* v23.227: een rij mag zijn voorbeeld zelf aanwijzen. Zonder dat kiest de volgorde van VERBOS,
     en bij "alleen de derde persoon verandert" leverde dat leer op: het enige werkwoord in die rij
     waarbij het NIET de klinker is die verspringt. Het uitzonderlijkste geval als voorbeeld. */
  if(pat && pat.model){
    for(i = 0; i < pool.length; i++) if(pool[i].inf === pat.model) return pool[i];
  }
  for(i = 0; i < pool.length; i++) if(conjPatroonAantal(pool[i], t) === 1) return pool[i];
  return pool[0] || null;
}""")
    rep("""function conjOnregPool(){
  return VERBOS.filter(function(v){ return conjPatroonAantal(v) > 0; });
}""",
"""function conjOnregPool(){
  return VERBOS.filter(function(v){ return conjPatroonAantal(v, "presente") > 0; });
}""")
    rep("""function conjPatroonOpen(){
  var nodig = conjFaseIdx(CONJ_PATROON_FASE);
  if(nodig < 0) return true;
  return conjOpenMax() >= nodig;
}""",
"""function conjPatroonOpen(pat){
  /* v23.227: een rij van een andere tijd erft de poort van die tijd en niet die van het presente.
     Anders zou iemand die net begint een rij over dije en dijeron aangeboden krijgen. */
  var t = conjPatroonTijd(pat);
  if(t !== "presente") return conjOpenTijden().indexOf(t) !== -1;
  var nodig = conjFaseIdx(CONJ_PATROON_FASE);
  if(nodig < 0) return true;
  return conjOpenMax() >= nodig;
}""")

    # =========================================================================================
    # 6. de les: de rij weet nu zelf in welke tijd hij staat
    # =========================================================================================
    rep("""  var pat = conjPatroonVan(id);
  if(!pat) return null;
  var pool = conjPatroonPool(id);
  if(!pool.length) return null;
  var v0 = conjPatroonModel(id);
  return {id:id, t:"presente", tijd:false, es:pat.es, nl:pat.nl, en:pat.en,
          doet:pat.doet, doetEn:pat.doetEn, vorm:pat.vorm, vormEn:pat.vormEn,
          vb:conjVorm(v0, 0, "presente"), vbNl:conjGloss(v0), vbEn:conjGloss(v0), v:v0,
          pool:function(lesV){ return pool.filter(function(w){ return w.inf !== lesV.inf; }); }};""",
"""  var pat = conjPatroonVan(id);
  if(!pat) return null;
  var pool = conjPatroonPool(id);
  if(!pool.length) return null;
  var v0 = conjPatroonModel(id);
  /* v23.227: de tijd komt uit de rij zelf. Hier stond "presente" hardgecodeerd, en dat was de
     tweede reden dat er nooit een rij in een andere tijd kon bestaan. */
  var pt = conjPatroonTijd(pat);
  return {id:id, t:pt, tijd:false, es:pat.es, nl:pat.nl, en:pat.en,
          doet:pat.doet, doetEn:pat.doetEn, vorm:pat.vorm, vormEn:pat.vormEn,
          vb:conjVorm(v0, 0, pt), vbNl:conjGloss(v0), vbEn:conjGloss(v0), v:v0,
          pool:function(lesV){ return pool.filter(function(w){ return w.inf !== lesV.inf; }); }};""")
    rep("""  var uit = conjOpenTijden().slice();
  if(!conjPatroonOpen()) return uit;   // v23.131: zie conjPatroonOpen()
  CONJ_PATRONEN.forEach(function(p){ if(conjPatroonPool(p.id).length) uit.push(p.id); });""",
"""  var uit = conjOpenTijden().slice();
  /* v23.227: per rij vragen of hij open is. Hier stond één poort voor alle patronen, en die keek
     naar de presente-fase. */
  CONJ_PATRONEN.forEach(function(p){
    if(conjPatroonOpen(p) && conjPatroonPool(p.id).length) uit.push(p.id);
  });""")
    # het overzicht van "de zes rijen" gaat over het presente
    rep("""            ? ct("De zes rijen: ", "The six rows: ") +
              CONJ_PATRONEN.map(function(pt){ return ct(pt.nl, pt.en) + " (" + conjPatroonPool(pt.id).length + ")"; }).join(", ")""",
"""            /* v23.227: alleen de rijen van deze tijd. De mengrij gaat over het presente, en sinds
               het indefinido zijn eigen rijen heeft zou dit anders zeven vreemde namen erbij zetten. */
            ? ct("De zes rijen: ", "The six rows: ") +
              CONJ_PATRONEN.filter(function(pt){ return conjPatroonTijd(pt) === (x.t || "presente"); })
                .map(function(pt){ return ct(pt.nl, pt.en) + " (" + conjPatroonPool(pt.id).length + ")"; }).join(", ")""")

if DOE_APP:
    # =========================================================================================
    # de controles
    # =========================================================================================
    for nodig in ["function conjVerwachtIn(", "function indefSterk(", "function indefSterkSoort(",
                  "function indefSuppletief(", "function indefKort(", "function indefAlleenDerde(",
                  "function indefAlleenSchrijf(", "function conjPatroonTijd(",
                  'id:"indef.u"', 'id:"indef.i"', 'id:"indef.fui"',
                  'id:"indef.kort"', 'id:"indef.derde"', 'id:"indef.schrijf"']:
        assert nodig in src, "ontbreekt: " + nodig
    # geen enkele rij mag nog op de oude manier herkend worden
    assert "soort:\"schoen\"" not in src and "soort:\"yo\"" not in src, \
        "er staat nog een rij met de oude soort/sleutel-herkenning"
    assert src.count("pas:function(v)") == 8, \
        "verwacht acht rijen met een herkenner ter plekke (6 presente + 2 sterke stammen), kreeg %d" % src.count("pas:function(v)")
    for f in ["indefVormen", "indefStam", "indefSterk", "indefSterkSoort", "indefSuppletief",
              "indefKort", "indefAlleenDerde", "indefAlleenSchrijf",
              "conjVerwachtIn", "conjPatroonTijd"]:
        n = src.count("function " + f + "(")
        assert n == 1, "%s staat %d keer in het bestand (JavaScript hijst, dus de laatste wint stil)" % (f, n)
    assert src.count("pas:indef") == 4, \
        "verwacht vier rijen die hun herkenner bij naam noemen, kreeg %d" % src.count("pas:indef")
    n = len(re.findall(r'\{id:"(?:schoen|yo|indef)\.', src))
    assert n == 12, "verwacht twaalf patroonrijen (6 presente + 6 indefinido), kreeg %d" % n
    assert 'model:"pedir"' in src, "de derde-persoonsrij wijst zijn voorbeeld niet aan"
    assert 'conjPatroonAantal(v, "presente")' in src, "conjOnregPool telt niet meer per tijd"
    assert 't:"presente", tijd:false' not in src, "lesRij zet de tijd nog hardgecodeerd"
    APP.write_text(src, encoding="utf-8")
    print("index.html: zes rijen voor het indefinido erbij, patronen weten hun tijd")
else:
    print("index.html: stonden er al")

if DOE_VER:
    a = APP.read_text(encoding="utf-8")
    b = a.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    assert a != b, "APP_VERSIE niet gevonden op " + huidig_ver
    APP.write_text(b, encoding="utf-8")
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: %s -> %s" % (huidig_ver, NIEUW))
else:
    print("versie.txt: stond al op " + huidig_ver)
