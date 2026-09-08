#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v23.251 - twee patronen: een markering die verliest, en een ronde die niemand bewaart
#
# Stefan, 8 september, met twee schermafbeeldingen: "de fout dat het goede antwoord groen moet (niet
# de balk eronder) is nog niet overal opgelost. en dat een spel altijd opnieuw moet beginnen ook
# niet. je moet even kijken naar de onderliggende patronen om dit structureel op te lossen, anders
# gaan we pleister plakken maar we moeten naar de oorzaak."
#
# Terecht. Dus eerst gemeten, allebei, en de oorzaak bleek in geen van beide gevallen te zijn wat
# ik ervan verwacht had.
#
# ================ PATROON EEN: DE MARKERING WORDT GEZET EN VERLIEST ================
#
# Mijn verwachting was: er is een scherm dat keuzeMerk() niet aanroept. Fout. Het scherm op zijn
# schermafbeelding (de grammatica-microles) roept het gewoon aan, regel 36651:
#
#     var klasse = "ghost gw-optie";
#     if(beantwoord) klasse += " " + keuzeMerk(i, q.g, gwSess.gekozen);
#
# De klasse staat er dus op. Gemeten in de browser, per knopklasse, met en zonder "juist":
#
#     .opt                        wit -> groen        zichtbaar
#     .opt .audOpt                wit -> groen        zichtbaar
#     .ghost .gw-optie            wit -> WIT          NIET zichtbaar
#     .ghost                      wit -> WIT          NIET zichtbaar
#     .ghost .gw-optie [disabled] wit, opacity 0.5    NIET zichtbaar, en half doorzichtig
#
# De oorzaak is de cascade, en hij is exact:
#
#     button.ghost{ background:var(--card); border:1.5px solid var(--border); }   (0,1,1)
#     .juist      { background:var(--green-soft); border-color:var(--green); }    (0,1,0)
#
# Een element-plus-klasse is specifieker dan een klasse. button.ghost wint dus altijd van .juist,
# ongeacht de volgorde in het bestand. Op .opt-knoppen werkt de markering wel, want .opt is óók maar
# een klasse en staat zes regels eerder, dus daar beslist de volgorde in ons voordeel.
#
#     Een klasse die een TOESTAND aanzet en even zwak is als de klasse die de VORM bepaalt,
#     is zichtbaar op de ene knop en onzichtbaar op de andere, en niemand ziet waarom.
#
# En er zit een tweede laag op: beantwoorde knoppen krijgen disabled, en button.ghost:disabled zet
# opacity op 0.5. Dat is precies het bleke grijs van zijn schermafbeelding.
#
# WAT ERAAN GEDAAN WORDT
#
# De twee toestandsklassen winnen nu van elke vormklasse (!important op precies deze declaraties,
# want dat is waar toestandsklassen voor bestaan), en een gemarkeerde knop blijft ondoorzichtig ook
# als hij uitgeschakeld is.
#
# Maar dat is de reparatie, niet de oorzaak. De oorzaak is dat NIETS dit meet. Er stond een proef op
# "wordt keuzeMerk aangeroepen", en die stond groen terwijl het scherm wit bleef: een proef die het
# mechanisme meet in plaats van de uitkomst. Vandaar pw-markering.js, die de bron van de app leest,
# er élke knopklasse uit haalt waar ooit een antwoord op gemarkeerd wordt, en per klasse de ECHTE
# berekende kleur vergelijkt. Komt er morgen een zesde antwoordscherm bij met weer een andere
# knopklasse, dan valt die vanzelf binnen de meting.
#
#     Meet de uitkomst, niet het mechanisme. Anders bewaakt de proef je goede bedoeling.
#
# ================ PATROON TWEE: DE RONDE LEEFT IN EEN VARIABELE ================
#
# Gemeten: negen spellen gestart, één stap gezet, pagina herladen, en gekeken of DEZELFDE ronde
# terugkwam (niet: of er weer een ronde was, want dat is iets anders).
#
#     brok        een NIEUWE ronde, i terug op 0
#     omkeer      een nieuwe ronde
#     tijdvorm    een nieuwe ronde
#     zin         een nieuwe ronde
#     clasificador een nieuwe ronde
#     les         niets, leeg scherm
#     woordenzoeker niets
#     adivina     DEZELFDE ronde, met je gokken erin
#
# Eén van de acht herstelt. De oorzaak staat in vijf regels die je in één grep naast elkaar ziet:
#
#     if(!brokSpel)     brokStart();
#     if(!omkeerSpel)   omkeerStart();
#     if(!tijdvormSpel) tijdvormStart();
#     if(!zinSpel)      zinStart(null, null);
#     if(!adivSpel && !adivHerstel()) adivNieuw();     <- deze ene
#
# Vier schermen zeggen "leeg? dan een nieuwe". Eén zegt "leeg? probeer eerst te herstellen". En die
# ene is de enige die zijn ronde ook wegschrijft.
#
#     Een tak die "nog niet begonnen" en "je was al bezig" hetzelfde behandelt,
#     kan je voortgang niet bewaren.
#
# Dat is dezelfde vorm als de versiebotsing van v23.247 en als de twee-keer-mis-teller van v23.248:
# twee verschillende situaties die in één tak vallen. Vierde keer in twee weken.
#
# WAT ERAAN GEDAAN WORDT
#
# Eén plek die weet hoe een ronde bewaard wordt, en één plek die het doet.
#
#   SPEL_RONDE      per spel alleen wat niemand anders kan weten: hoe je een opgave herkent
#                   (sleutel) en waar de opgaven vandaan komen (pool). Meer niet.
#   spelRondeSync   in renderFun(), de plek waar élk spel langskomt. Is het geheugen leeg, dan
#                   herstellen; staat er een ronde, dan bewaren. Eén regel, één plek, en een nieuw
#                   spel dat in de tabel komt te staan krijgt het gedrag mee zonder eigen code.
#   speelVers       de enige plek die een spelstand leeggooit (dat staat er sinds v23.191) gooit nu
#                   ook de bewaarde ronde weg. Zonder die regel zou "Nog een" je oude ronde
#                   terugzetten, en dat is precies de val die in v23.232 bij Letras is gedocumenteerd:
#                   een verversing die alleen het geheugen leegmaakt terwijl de opslag hem terugzet,
#                   verandert niets.
#
# De ronde wordt bewaard als SLEUTELS en niet als objecten. De opgaven van omkeer en tijdvorm dragen
# hele werkwoordobjecten met zich mee en die van zin hele zinnen; die in localStorage leggen is
# tientallen kilobytes per spel voor gegevens die al in de app staan. Ontbreekt er bij het herstellen
# ook maar één sleutel in de pool (je bent iets nieuws gaan kunnen, de pool is veranderd), dan wordt
# er niets hersteld en begint er gewoon een nieuwe ronde. Half herstellen zou een ronde opleveren die
# korter is dan hij zegt te zijn.
#
# WAT ER NIET IN ZIT
#
# De woordenzoeker en Crucigrama. Die zijn gemeten en herstellen ook niet, maar hun ronde is een heel
# raster en dat is geen sleutellijst. Ze staan in de proef als gemeten feit en niet als belofte.
import pathlib
import re
import sys

W = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(W / "claude"))
import patchhulp  # noqa: E402

APP = W / "index.html"
VER = W / "versie.txt"
GEPLAND = "v23.251"

src = APP.read_text(encoding="utf-8")
huidig = VER.read_text(encoding="utf-8").strip()
DOE_APP = "function spelRondeSync(" not in src


def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:110])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    # ---------- EEN: de markering wint van de vorm ----------
    rep(
        """  .juist{border-color:var(--green); background:var(--green-soft); color:var(--green); font-weight:700;}
  .jouw{border-color:var(--red); background:var(--red-soft); color:var(--red);}""",
        """  /* v23.251: en deze twee winnen van elke knopklasse.

     Gemeten op 8 september, per knopklasse, met en zonder "juist":

       .opt                          wit -> groen   zichtbaar
       .ghost .gw-optie              wit -> WIT     niet zichtbaar
       .ghost .gw-optie [disabled]   opacity 0.5    niet zichtbaar en half doorzichtig

     De oorzaak is de cascade en hij is exact: button.ghost is een element PLUS een klasse (0,1,1)
     en .juist is alleen een klasse (0,1,0), dus button.ghost wint altijd, ongeacht de volgorde in
     dit bestand. Op .opt werkt het toevallig wel, want dat is ook maar een klasse en hij staat zes
     regels hoger.

         Een klasse die een TOESTAND aanzet en even zwak is als de klasse die de VORM bepaalt,
         is zichtbaar op de ene knop en onzichtbaar op de andere.

     Vandaar !important: dit is waar toestandsklassen voor bestaan. En de opacity terug naar 1,
     want een beantwoorde knop is uitgeschakeld en button.ghost:disabled maakte hem halfdoorzichtig;
     dat is het bleke grijs op Stefans schermafbeelding.

     Dit is de reparatie. De oorzaak is dat niets dit mat, en dat staat in pw-markering.js: die
     leest de bron, haalt er elke knopklasse uit waar een antwoord op gemarkeerd wordt, en
     vergelijkt de ECHTE berekende kleur. Een zesde antwoordscherm valt daar vanzelf onder. */
  .juist{border-color:var(--green) !important; background:var(--green-soft) !important;
         color:var(--green) !important; font-weight:700;}
  .jouw{border-color:var(--red) !important; background:var(--red-soft) !important;
        color:var(--red) !important;}
  .juist:disabled, .jouw:disabled{opacity:1 !important;}""",
    )

    # ---------- TWEE: een ronde overleeft weglopen en herladen ----------
    rep(
        """function renderFun(){
  var el = document.getElementById("funCard");
  if(!el) return;""",
        """/* ================= EEN RONDE OVERLEEFT WEGLOPEN (v23.251) =================

   Stefan, 8 september: "dat een spel altijd opnieuw moet beginnen." Gemeten: negen spellen
   gestart, een stap gezet, pagina herladen, en gekeken of DEZELFDE ronde terugkwam. Eén van de
   acht deed dat. De oorzaak staat in vijf regels die naast elkaar te zetten zijn:

       if(!brokSpel)     brokStart();
       if(!omkeerSpel)   omkeerStart();
       if(!tijdvormSpel) tijdvormStart();
       if(!zinSpel)      zinStart(null, null);
       if(!adivSpel && !adivHerstel()) adivNieuw();     <- de enige die het goed doet

       Een tak die "nog niet begonnen" en "je was al bezig" hetzelfde behandelt,
       kan je voortgang niet bewaren.

   Hieronder staat per spel alleen wat geen enkele andere plek kan weten: hoe je een opgave herkent
   en waar de opgaven vandaan komen. Al het overige (wanneer bewaren, wanneer herstellen, wanneer
   vergeten, welke velden mee moeten) staat één keer, hieronder.

   De ronde wordt als SLEUTELS bewaard en niet als objecten: de opgaven van omkeer en tijdvorm
   dragen hele werkwoordobjecten mee en die van zin hele zinnen. Ontbreekt bij het herstellen ook
   maar één sleutel in de pool, dan herstellen we niets: een halve ronde is korter dan hij zegt te
   zijn. */
var SPEL_RONDE = {
  brok: {
    lees:function(){ return brokSpel; }, zet:function(x){ brokSpel = x; },
    sleutel:function(x){ return String(x); },
    pool:function(){ var r = [], i; for(i = 0; i < BROK_TIJD.length; i++) r.push(i); return r; }
  },
  omkeer: {
    lees:function(){ return omkeerSpel; }, zet:function(x){ omkeerSpel = x; },
    sleutel:function(x){ return x.v.inf + "|" + x.p + "|" + x.t; },
    pool:function(){ return omkeerPool().items; }
  },
  tijdvorm: {
    lees:function(){ return tijdvormSpel; }, zet:function(x){ tijdvormSpel = x; },
    sleutel:function(x){ return x.v.inf + "|" + x.p + "|" + x.t; },
    pool:function(){ return tijdvormPool().items; }
  },
  zin: {
    lees:function(){ return zinSpel; }, zet:function(x){ zinSpel = x; },
    sleutel:function(x){ return x.z.id; },
    pool:function(st){ return zinPool((st && st.tijden) || null); }
  },
  /* de les heeft geen rij maar een rijtje-naam en een stap, dus die krimpt en groeit zelf */
  les: {
    lees:function(){ return lesSpel; }, zet:function(x){ lesSpel = x; },
    krimp:function(st){ return {rij:st.rij, stap:st.stap}; },
    groei:function(k){
      if(!k || !k.rij) return null;
      if(!lesStart(k.rij)) return null;
      if(typeof k.stap === "number") lesSpel.stap = k.stap;
      return lesSpel;
    }
  }
};
/* Alle waarden die geen object zijn gaan mee, en de rij wordt een lijst sleutels. Zo hoeft er per
   spel geen veldenlijst te staan die kan verouderen zodra een spel een teller bijkrijgt. */
function spelRondeKrimp(v, st){
  var e = SPEL_RONDE[v], uit = {}, k, w;
  if(e.krimp) return e.krimp(st);
  for(k in st){
    if(!Object.prototype.hasOwnProperty.call(st, k)) continue;
    if(k === "rij") continue;
    w = st[k];
    if(w === null || typeof w !== "object") uit[k] = w;
    else if(Object.prototype.toString.call(w) === "[object Array]" &&
            w.length && w.join && typeof w[0] !== "object") uit[k] = w.slice();
  }
  uit.rij = [];
  (st.rij || []).forEach(function(x){ uit.rij.push(e.sleutel(x)); });
  return uit;
}
function spelRondeGroei(v, k){
  var e = SPEL_RONDE[v];
  if(e.groei) return e.groei(k);
  if(!k || !k.rij || !k.rij.length) return null;
  var pool = [], op = {}, rij = [], i, s;
  try { pool = e.pool(k) || []; } catch(err){ return null; }
  pool.forEach(function(x){ op[e.sleutel(x)] = x; });
  for(i = 0; i < k.rij.length; i++){
    s = k.rij[i];
    if(!(s in op)) return null;      // de pool is veranderd: liever een nieuwe ronde dan een halve
    rij.push(op[s]);
  }
  var st = {rij:rij};
  for(var f in k){
    if(!Object.prototype.hasOwnProperty.call(k, f) || f === "rij") continue;
    st[f] = k[f];
  }
  return st;
}
function spelRondeBewaar(v){
  var e = SPEL_RONDE[v];
  if(!e) return;
  var st = e.lees();
  if(!st) return;
  S.spelRonde = S.spelRonde || {};
  try { S.spelRonde[v] = {d:today(), k:spelRondeKrimp(v, st)}; persist(); } catch(err){}
}
function spelRondeHerstel(v){
  var e = SPEL_RONDE[v];
  if(!e) return false;
  var bak = null;
  try { bak = (S.spelRonde || {})[v]; } catch(err){ return false; }
  if(!bak || bak.d !== today()) return false;   // een ronde van gisteren is geen ronde van vandaag
  var st = null;
  try { st = spelRondeGroei(v, bak.k); } catch(err){ st = null; }
  if(!st) return false;
  e.zet(st);
  return true;
}
function spelRondeVergeet(v){
  if(!SPEL_RONDE[v]) return;
  try {
    if(S.spelRonde && S.spelRonde[v]){ delete S.spelRonde[v]; persist(); }
  } catch(err){}
}
/* De ene plek. Staat het geheugen leeg, dan herstellen; draait er een ronde, dan bewaren. Elke
   render van een spel komt hierlangs, en elk antwoord tekent opnieuw, dus dit dekt beide kanten
   zonder dat er in een spel iets bij hoeft.

   HERSTELLEN MAG MAAR EEN KEER PER PAGINA, EN DAT IS DE HELE TRUC.

   De eerste versie herstelde bij elke lege stand, en toen kon je in De les niet meer terug naar het
   keuzemenu: dat menu ZET lesSpel op null, en de volgende render zette hem meteen terug. De proef
   pw-schoen viel er als eerste over ("een knop per rij: 0 van de 18"). Dat is dezelfde val die in
   v23.232 bij Letras staat beschreven, dus die maken we hier niet nog een keer.

   Het onderscheid dat we nodig hebben is niet "is de stand leeg" maar "wie heeft hem leeggemaakt".
   Een herlaad wist het geheugen vóórdat wij ook maar één keer gekeken hebben; een knop wist hem
   daarna. Vandaar deze vlag: hij staat leeg zolang de pagina vers is. Leeg gemaakt nadat we al eens
   gekeken hebben, is een keuze van de speler, en dan gooien we de bewaarde ronde ook weg. */
var _spelGezien = {};
function spelRondeSync(v){
  var e = SPEL_RONDE[v];
  if(!e) return;
  if(!e.lees()){
    if(_spelGezien[v]){ spelRondeVergeet(v); return; }   // je hebt hem zelf weggelegd
    _spelGezien[v] = 1;
    spelRondeHerstel(v);
    return;
  }
  _spelGezien[v] = 1;
  spelRondeBewaar(v);
}

function renderFun(){
  var el = document.getElementById("funCard");
  if(!el) return;
  spelRondeSync(funView);""",
    )
    rep(
        """function speelVers(v){
  var g = null;
  try { g = spelInfoVan(v); } catch(e){ g = null; }
  if(g && g.verse){ try { g.verse(); } catch(e){} }
}""",
        """function speelVers(v){
  var g = null;
  try { g = spelInfoVan(v); } catch(e){ g = null; }
  if(g && g.verse){ try { g.verse(); } catch(e){} }
  /* v23.251: en de bewaarde ronde erbij. Zonder deze regel zou verse() het geheugen leegmaken en
     spelRondeSync() hem meteen daarna uit de opslag terugzetten: dan doet "Nog een" niets. Dat is
     letterlijk de val die in v23.232 bij Letras is beschreven, dus die maken we hier niet opnieuw. */
  try { spelRondeVergeet(v); } catch(e){}
}""",
    )

    # ---------- en de poort op main weer dicht ----------
    #
    # main stond al rood voordat deze ronde begon: pw-lesgat telde één spiekkaart met een toetsje en
    # zonder les. Dat is kaart 30, "Gebruik van 'costar' en 'gustar' met activiteiten", vannacht
    # gemaakt door de lesgenerator samen met toetsje q-b1-12 (8 vragen). De generator maakt wel een
    # kaart en een toetsje, maar hangt de kaart aan geen enkel concept, en dan is er uitleg te
    # toetsen die nergens gegeven wordt.
    #
    # Inhoudelijk hoort die kaart bij gustarfamilie: costar werkt precies zoals gustar (me cuesta
    # hablar), en dat is letterlijk wat die kaart uitlegt. Dus daar hangt hij nu aan.
    #
    # DIT IS EEN PLEISTER EN GEEN OORZAAK, en dat hoort er eerlijk bij te staan. De oorzaak is dat
    # de nachtrun naar main duwt zonder de kwaliteitscontrole te draaien die de poort daarna wél
    # doet. Zolang dat zo is maakt hij morgen weer zo'n kaart. Die reparatie hoort in
    # tools/curriculum.js, vóór het publiceren, en staat als openstaand punt in het logboek.
    rep(
        '''  corr:[], spiek:{a2:[18,23]}, wizard:null,''',
        '''
  /* v23.251: kaart 30 erbij ("costar en gustar met activiteiten", vannacht gegenereerd). Die kaart
     had een toetsje van acht vragen en geen enkel concept dat hem claimde, en daar viel pw-lesgat
     op om. Inhoudelijk hoort hij hier: costar werkt precies zoals gustar. */
  corr:[], spiek:{a2:[18,23,30]}, wizard:null,''',
    )

    kaal = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    kaal = "\n".join([r.split("//")[0] for r in kaal.split("\n")])
    assert kaal.count("function spelRondeSync(") == 1, "spelRondeSync niet precies een keer"
    assert kaal.count("spelRondeSync(funView)") == 1, "renderFun roept de synchronisatie niet aan"
    assert kaal.count("spelRondeVergeet(v)") == 3, "vergeten gebeurt niet op de twee plekken die het moeten doen"
    assert kaal.count("_spelGezien[v]") == 3, "het onderscheid herlaad-tegen-knop staat er niet"
    # op de declaraties zelf, niet op een totaal: de app had er al vijftien staan en dan meet een
    # totaal vooral of iemand anders iets heeft toegevoegd
    assert kaal.count("background:var(--green-soft) !important") == 1, "juist wint niet"
    assert kaal.count("background:var(--red-soft) !important") == 1, "jouw wint niet"
    assert ".juist:disabled, .jouw:disabled{opacity:1 !important;}" in kaal, \
        "een gemarkeerde knop blijft niet ondoorzichtig als hij uitgeschakeld is"
    APP.write_text(src, encoding="utf-8")
    print("index.html: de markering wint, en een ronde overleeft het weglopen")
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
