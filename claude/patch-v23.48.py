#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.48: geen verzonnen werkwoordsvormen meer.

Gevonden bij het nalopen van de content, en het begon met één zin die Stefan op zijn scherm zag:

    Todos los días ___ con mi abuela.  (Elke dag reizende ik met mijn oma.)

Dat is geen typefout maar een sjabloon. Twee van de drieëntwintig grammaticaconcepten bouwen hun
Nederlandse en Engelse vertaling met knip- en plakwerk op de infinitief:

    "Elke dag "+w.nl.replace(/r$/,"")+"de ik met mijn oma."     -> reizen  -> "reizende ik"
    "heb ik veel ge"+w.nl.replace(/en$/,"")+"t."                -> reizen  -> "gereizt"
    "I "+w.en+"ed a lot."                                       -> eat     -> "eated"

Dat is Spaanse morfologie toegepast op Nederlands en Engels: plak er een uitgang achter en hoop het
beste. Voor "werken" komt er toevallig "gewerkt" uit, en dat is precies waarom het zo lang bleef
staan.

Gemeten door elk patroon van alle drieëntwintig concepten tweehonderd keer te draaien en de
uitkomsten te verzamelen:

    1074 gegenereerde varianten
      90 kapotte Nederlandse vormen   (gereizt, gewont, gestudert, geett, gepratt, reizende ik,
                                       wonende ik, etende ik, pratende ik, studerende ik)
      68 kapotte Engelse vormen        (eated, liveed, studyed)
       2 concepten                     (perfindef en indefimperf)

En één die er los van staat: het Engelse sjabloon zette het tijdvak altijd vooraan, dus "Nunca"
werd "Never I eated a lot." Ook met de juiste vorm blijft dat foute woordvolgorde; "never" hoort
tussen het hulpwerkwoord en het deelwoord.

## De reparatie

De vormen worden niet meer afgeleid maar opgeschreven. GC_PAS krijgt er vier velden bij per
werkwoord (nlVt, nlVd, enVt, enVd) en de acht patronen gebruiken die. Zes werkwoorden, vier velden:
vierentwintig woorden die één keer goed moeten staan, in plaats van een regel die voor elk nieuw
werkwoord opnieuw kan misgaan.

    hablar   praatte / gepraat        talked / talked
    trabajar werkte / gewerkt         worked / worked
    estudiar studeerde / gestudeerd   studied / studied
    viajar   reisde / gereisd         travelled / travelled
    comer    at / gegeten             ate / eaten
    vivir    woonde / gewoond         lived / lived

## Ook meegenomen: één zin die geen lijdend voorwerp kan hebben

    Un día ___ algo increíble.

Dat patroon trok uit alle zes de werkwoorden, en drie ervan kunnen daar niet staan: *hablé algo
increíble*, *trabajé algo increíble* en *viajé algo increíble* zijn geen Spaans. Dat is erger dan een
scheve vertaling, want dan oefen je op een zin die niet bestaat. De twee werkwoorden die er wél een
voorwerp bij kunnen hebben, krijgen een vlag `obj`, en dit patroon trekt alleen daaruit. Minder
variatie, maar wel Spaans.

## Wat er niet mis bleek

De andere eenentwintig concepten kwamen schoon door dezelfde generator: geen lege uitleg, geen
dubbele antwoordopties, geen antwoordindex buiten bereik, en overal een Engelse variant. De
patronen met drie of vier opties zijn geen fout: Clasificador filtert daar zelf op twee, de
Grammatica-tab gebruikt ze wel.

Idempotent.
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.48"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "nlVt:" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

if DOE_APP:
    ANKERS = ['var APP_VERSIE = "v23.47";', 'var GC_PAS = [', 'id:"perfindef"', 'id:"indefimperf"']
    ontbreekt = [a for a in ANKERS if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht. Ontbrekende ankers:\n  " +
              "\n  ".join(a[:80] for a in ontbreekt) +
              "\n\nDeze patch bouwt op v23.47. Eerst die draaien, of eerst bijtrekken:\n"
              "\n    git pull --rebase\n")
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    rep('var APP_VERSIE = "v23.47";', 'var APP_VERSIE = "%s";' % NIEUW)

    # ---------- 1. de vormen worden opgeschreven, niet afgeleid ----------
    OUD_PAS = '''var GC_PAS = [
 {inf:"hablar", nl:"praten", en:"talk", part:"hablado", indef:"hablé", imp:"hablaba"},
 {inf:"trabajar", nl:"werken", en:"work", part:"trabajado", indef:"trabajé", imp:"trabajaba"},
 {inf:"estudiar", nl:"studeren", en:"study", part:"estudiado", indef:"estudié", imp:"estudiaba"},
 {inf:"viajar", nl:"reizen", en:"travel", part:"viajado", indef:"viajé", imp:"viajaba"},
 {inf:"comer", nl:"eten", en:"eat", part:"comido", indef:"comí", imp:"comía"},
 {inf:"vivir", nl:"wonen", en:"live", part:"vivido", indef:"viví", imp:"vivía"}
];'''
    NIEUW_PAS = '''/* v23.48: hier stonden alleen de infinitieven, en de patronen hieronder maakten er zelf een
   verleden tijd van door een uitgang achter de stam te plakken. Dat is Spaanse morfologie op
   Nederlands en Engels losgelaten: "reizen" werd "reizende ik" en "gereizt", "eat" werd "eated".
   Bij "werken" komt er toevallig "gewerkt" uit, en dat is precies waarom het zo lang bleef staan.
   Vierentwintig woorden die één keer goed staan zijn beter dan een regel die bij elk nieuw
   werkwoord opnieuw kan misgaan.

   obj: mag er een lijdend voorwerp achter. Alleen deze twee kunnen in "Un día ___ algo increíble"
   staan; *hablé algo increíble* en *viajé algo increíble* zijn geen Spaans, en oefenen op een zin
   die niet bestaat is erger dan een scheve vertaling. */
var GC_PAS = [
 {inf:"hablar", nl:"praten", nlVt:"praatte", nlVd:"gepraat",
  en:"talk", enVt:"talked", enVd:"talked", part:"hablado", indef:"hablé", imp:"hablaba"},
 {inf:"trabajar", nl:"werken", nlVt:"werkte", nlVd:"gewerkt",
  en:"work", enVt:"worked", enVd:"worked", part:"trabajado", indef:"trabajé", imp:"trabajaba"},
 {inf:"estudiar", nl:"studeren", nlVt:"studeerde", nlVd:"gestudeerd", obj:1,
  en:"study", enVt:"studied", enVd:"studied", part:"estudiado", indef:"estudié", imp:"estudiaba"},
 {inf:"viajar", nl:"reizen", nlVt:"reisde", nlVd:"gereisd",
  en:"travel", enVt:"travelled", enVd:"travelled", part:"viajado", indef:"viajé", imp:"viajaba"},
 {inf:"comer", nl:"eten", nlVt:"at", nlVd:"gegeten", obj:1,
  en:"eat", enVt:"ate", enVd:"eaten", part:"comido", indef:"comí", imp:"comía"},
 {inf:"vivir", nl:"wonen", nlVt:"woonde", nlVd:"gewoond",
  en:"live", enVt:"lived", enVd:"lived", part:"vivido", indef:"viví", imp:"vivía"}
];
/* "Never" hoort in het Engels niet vooraan maar tussen het hulpwerkwoord en het deelwoord. Het
   sjabloon zette het tijdvak altijd vooraan en maakte er "Never I have eaten a lot" van. */
function gcEnPerfect(m, vd){
  if(m.en === "Never") return "I have never " + vd + " much.";
  return m.en + " I have " + vd + " a lot.";
}'''
    rep(OUD_PAS, NIEUW_PAS)

    # ---------- 2. perfindef ----------
    rep('''     return {v:m.es+" ___ mucho. ("+m.nl+" heb ik veel ge"+w.nl.replace(/en$/,"")+"t.)",
             vEn:m.es+" ___ mucho. ("+m.en+" I "+w.en+"ed a lot.)",
             o:["he "+w.part, w.indef], g:0,''',
        '''     return {v:m.es+" ___ mucho. ("+m.nl+" heb ik veel "+w.nlVd+".)",
             vEn:m.es+" ___ mucho. ("+gcEnPerfect(m, w.enVd)+")",
             o:["he "+w.part, w.indef], g:0,''')

    rep('''     return {v:m.es+" ___ mucho. ("+m.nl+" heb ik veel ge"+w.nl.replace(/en$/,"")+"t.)",
             vEn:m.es+" ___ mucho. ("+m.en+" I "+w.en+"ed a lot.)",
             o:["he "+w.part, w.indef], g:1,''',
        '''     return {v:m.es+" ___ mucho. ("+m.nl+" heb ik veel "+w.nlVd+".)",
             vEn:m.es+" ___ mucho. ("+m.en+" I "+w.enVt+" a lot.)",
             o:["he "+w.part, w.indef], g:1,''')

    rep('''             vEn:"Nunca ___ en Perú. (I have never "+w.en+"ed in Peru.)",''',
        '''             vEn:"Nunca ___ en Perú. (I have never "+w.enVd+" in Peru.)",''')

    rep('''     return {v:"En "+j+" ___ en Madrid. (In "+j+" heb ik in Madrid ge"+w.nl.replace(/en$/,"")+"d.)",
             vEn:"En "+j+" ___ en Madrid. (In "+j+" I "+w.en+"ed in Madrid.)",''',
        '''     return {v:"En "+j+" ___ en Madrid. (In "+j+" heb ik in Madrid "+w.nlVd+".)",
             vEn:"En "+j+" ___ en Madrid. (In "+j+" I "+w.enVt+" in Madrid.)",''')

    # ---------- 3. indefimperf ----------
    rep('''     return {v:"De niño ___ en Sevilla. (Als kind "+w.nl.replace(/r$/,"")+"de ik in Sevilla.)",''',
        '''     return {v:"De niño ___ en Sevilla. (Als kind "+w.nlVt+" ik in Sevilla.)",''')

    rep('''     return {v:"Ayer ___ tres horas. (Gisteren heb ik drie uur ge"+w.nl.replace(/en$/,"")+"t.)",
             vEn:"Ayer ___ tres horas. (Yesterday I "+w.en+"ed for three hours.)",''',
        '''     return {v:"Ayer ___ tres horas. (Gisteren heb ik drie uur "+w.nlVd+".)",
             vEn:"Ayer ___ tres horas. (Yesterday I "+w.enVt+" for three hours.)",''')

    rep('''     return {v:"Todos los días ___ con mi abuela. (Elke dag "+w.nl.replace(/r$/,"")+"de ik met mijn oma.)",''',
        '''     return {v:"Todos los días ___ con mi abuela. (Elke dag "+w.nlVt+" ik met mijn oma.)",''')

    rep('''   function(){ var w = gcKies(GC_PAS);
     return {v:"Un día ___ algo increíble. (Op een dag "+w.nl.replace(/r$/,"")+"de ik iets ongelooflijks.)",
             vEn:"Un día ___ something incredible. (One day I "+w.en+"ed something incredible.)",''',
        '''   function(){ /* alleen werkwoorden die een lijdend voorwerp kunnen hebben: zie de obj-vlag bij
                   GC_PAS. Met de hele lijst leverde dit patroon *hablé algo increíble* op. */
     var w = gcKies(GC_PAS.filter(function(x){ return x.obj; }));
     return {v:"Un día ___ algo increíble. (Op een dag "+w.nlVt+" ik iets ongelooflijks.)",
             vEn:"Un día ___ algo increíble. (One day I "+w.enVt+" something incredible.)",''')

    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
    print("index.html gepatcht naar %s" % NIEUW)
else:
    print("index.html was al gepatcht")

if DOE_VER:
    with io.open(PAD_VER, "w", encoding="utf-8") as f:
        f.write(NIEUW + "\n")
    print("versie.txt op %s" % NIEUW)
else:
    print("versie.txt stond al op %s" % NIEUW)
