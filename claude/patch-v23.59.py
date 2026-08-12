#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.59: de grammatica begint met een voorbeeld, niet met vijf alinea's.

Stefan, 11 én 12 augustus: "ik vind sowieso het concept van hoe we nu grammatica doen nog niet
perfect, veel tekst, weinig voorbeelden, weinig stap voor stap, dat kan denk ik nog meer micro
steps." En na de telefoontest van 12 aug: "blijft ook staan."

Nagemeten met een schermafdruk, 390 bij 844, concept *el of la* op een vers A0-profiel:

    EL OF LA · STAP 1/1
    📘 El of la
    ① El of la is geen kwestie van gevoel. Je kunt het bijna altijd aan de uitgang zien.
      la bij -a, en bij -ción, -sión, -dad, -tad en -umbre. Die groep kent op dit niveau
      geen uitzonderingen.
      el bij -o, en bij -or.
      De valkuil is een handjevol woorden dat uit het Grieks komt en op -ma of -a eindigt:
      el problema, el tema, el idioma, el mapa, el día. Die leer je los, en daarna is de
      rest gewoon regel.
      Leer een woord daarom nooit kaal. Niet casa maar la casa, want het lidwoord hoort erbij.
    [ TOETS ME → ]  [← Terug]

**Stap 1 van 1.** Vijf alinea's, 544 tekens, en pas daarna een vraag. Dat is geen micro-stap, dat
is een pagina uit een grammaticaboek met een knop eronder.

## Wat er al lag, en niet gebruikt werd

Elk concept heeft `patronen`: functies die een vers voorbeeld genereren, elk mét een uitleg van
precies één zin in het veld `w`. *"Er staat een bijvoeglijk naamwoord achter, dus muy."* Dat is de
micro-stap. Hij bestond al, hij stond alleen ná vijf alinea's en achter een knop.

En de wizardmachinerie kan al meerdere stappen aan: `o.stappen` is een lijst, `gwVolgendeStap()`
loopt eroverheen, en na elk antwoord toont `renderGramWiz()` al `gwWaarom(q)`, en dát is precies dat
ene zinnetje. `gcBouw()` maakte er alleen altijd één stap van.

## Wat het nu is

    stap 1/3   Probeer eens        één regel kader, dan 2 verse voorbeelden
    stap 2/3   Nog twee            geen tekst, meteen 2 verse voorbeelden
    stap 3/3   Waarom dat zo is    de begripsvraag, en de hele regel als naslag eronder

Na elk voorbeeld staat de regel van één zin uit dat patroon. Je gokt, je krijgt gelijk of niet, en
je leest één zin waarom. Dat is de kleinste eenheid die er is.

Er komt geen letter nieuwe content bij. De lange uitleg verhuist naar stap 3 en is daar naslag
in plaats van toegangspoort, en de begripsvraag ("wat is het echte verschil tussen ser en estar?")
stond op plek één en staat nu op plek vijf, want dat is een vraag die je pas kúnt beantwoorden als
je vier voorbeelden hebt gezien.

## Één stap zonder tekst kon nog niet

`gwStart()` en `gwVolgendeStap()` zetten de fase altijd op "uitleg", en een stap zonder uitleg gaf
dus een leeg scherm met een knop "Toets me". Nu slaan ze die fase over als er niets te lezen valt.
Dat is één regel op twee plekken, en het is de enige verandering aan de machinerie zelf.

## Waarom een voorbeeld vóór de regel, en niet andersom

Omdat gokken en fout zitten je klaarmaakt voor het antwoord. Dat is het hele idee achter de
foutenlus die deze app al gebruikt voor woorden en zinnen; de grammatica was de enige plek waar we
het nog omgekeerd deden. De eerste stap zegt dat met zoveel woorden ("gok gerust"), zodat niemand
denkt dat hij iets gemist heeft.

Idempotent.
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.59"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "GC_STAP_TXT" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_BOUW = '''  var vragen = [begrip].concat(gcMaakVragen(c, GC_VOORBEELDEN));
  var st = gramLees(c.id);
  var pitch = st.fout ? "Hier ging je " + st.fout + (st.fout === 1 ? " keer" : " keer") + " de mist in. Nieuwe voorbeelden."
                      : "De beslissing, en dan " + GC_VOORBEELDEN + " verse voorbeelden.";
  var pitchEn = st.fout ? "You slipped up here " + st.fout + (st.fout === 1 ? " time" : " times") + ". Fresh examples."
                        : "The decision, then " + GC_VOORBEELDEN + " fresh examples.";
  return {id:"concept-" + c.id, concept:c.id, icon:c.icon,
    titel:c.naam, titelEn:c.naamEn, pitch:pitch, pitchEn:pitchEn,
    stappen:[{kop:c.naam, kopEn:c.naamEn,
      uitleg:c.uitleg, uitlegEn:c.uitlegEn,
      vragen:vragen}]};
}'''

A_MAAK = '''function gcMaakVragen(c, n){
  // roteer over de patronen: vier keer hetzelfde patroon leert de oppervlakte, vier verschillende
  // patronen dwingen de beslissing af. Dat is het hele idee van minimale paren.
  var uit = [], gezien = {}, ronde = 0, poging = 0, start = Math.floor(Math.random() * c.patronen.length);'''

A_START = '''  gwSess = {id:id, stap:s, fase:"uitleg", vraag:0, goed:0, fout:0, gekozen:null};
  navPush({t:"gramwiz", id:id});
  renderCheat();'''

A_VOLGENDE = '''    gwSess.stap++; gwSess.fase = "uitleg"; gwSess.vraag = 0; gwSess.goed = 0; gwSess.fout = 0; gwSess.gekozen = null;
    renderCheat();'''

if DOE_APP:
    ontbreekt = [a for a in [A_BOUW, A_MAAK, A_START, A_VOLGENDE] if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht. Ontbrekende ankers:\n  " +
              "\n  ".join(a[:100].replace("\n", " / ") for a in ontbreekt) +
              "\n\nEerst bijtrekken:\n\n    git pull --rebase\n")
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    # ---------- 0. de eerste keer krijg je de patronen in de volgorde van de auteur ----------
    rep(A_MAAK, '''function gcMaakVragen(c, n){
  // roteer over de patronen: vier keer hetzelfde patroon leert de oppervlakte, vier verschillende
  // patronen dwingen de beslissing af. Dat is het hele idee van minimale paren.
  /* v23.59: het beginpunt was altijd willekeurig, en met de voorbeelden vooraan (in plaats van na
     vijf alinea's uitleg) gaat dat opeens pijn doen. Gemeten op el-of-la: de allereerste vraag die
     een vreemde kreeg was "___ tema", en dat is juist de uitzondering (Grieks, ziet er vrouwelijk
     uit, is mannelijk). De uitzondering vóór de regel.

     De patronen staan bij elk concept al in de volgorde waarin ze horen: bij genero eerst GC_GEN_LA
     (de regel), dan pas GC_GEN_TRAP (de val). Dus wie een concept voor het eerst doet, begint bij
     patroon nul. Wie het al eens deed krijgt weer een willekeurig beginpunt, want dan is variatie
     meer waard dan volgorde. De inhoud blijft in beide gevallen vers gegenereerd: je kunt nog
     steeds geen antwoord onthouden. */
  var eerder = false;
  try { var g = gramLees(c.id); eerder = ((g.goed || 0) + (g.fout || 0)) > 0; } catch(e){ eerder = false; }
  var uit = [], gezien = {}, ronde = 0, poging = 0,
      start = eerder ? Math.floor(Math.random() * c.patronen.length) : 0;''')

    # ---------- 1. drie micro-stappen in plaats van één lange ----------
    rep(A_BOUW, '''  /* v23.59. Stefan, twee telefoontests achter elkaar: "veel tekst, weinig voorbeelden, weinig stap
     voor stap, dat kan denk ik nog meer micro steps." Gemeten op el-of-la: stap 1 van 1, vijf
     alinea's, 544 tekens, en pas dáárna een vraag.

     Wat ervoor nodig was lag er al. Elk patroon genereert een vers voorbeeld mét een uitleg van
     precies één zin (het veld w), en renderGramWiz toont die zin al na elk antwoord. De wizard kan
     ook al meerdere stappen aan. Alleen gcBouw maakte er altijd één van, met de lange tekst ervoor.

     Nu: voorbeeld, keuze, één zin waarom. Drie keer. En de lange tekst achteraan als naslag, want
     daar is hij goed voor. De begripsvraag ("wat is het echte verschil tussen ser en estar?") stond
     op plek één en staat nu op plek vijf: dat is een vraag die je pas kúnt beantwoorden als je vier
     voorbeelden hebt gezien.

     Geen letter nieuwe content. Alleen een andere volgorde en andere porties. */
  var vb = gcMaakVragen(c, GC_VOORBEELDEN);
  var st = gramLees(c.id);
  var pitch = st.fout ? "Hier ging je " + st.fout + (st.fout === 1 ? " keer" : " keer") + " de mist in. Nieuwe voorbeelden."
                      : "Vier verse voorbeelden, en de regel erachter.";
  var pitchEn = st.fout ? "You slipped up here " + st.fout + (st.fout === 1 ? " time" : " times") + ". Fresh examples."
                        : "Four fresh examples, and the rule behind them.";
  var stappen = [];
  // stap 1: meteen een voorbeeld. Eén regel kader, zodat niemand denkt dat hij iets gemist heeft.
  if(vb.length){
    stappen.push({kop:GC_STAP_TXT.nl.k1, kopEn:GC_STAP_TXT.en.k1,
      uitleg:"<p>" + GC_STAP_TXT.nl.u1 + "</p>", uitlegEn:"<p>" + GC_STAP_TXT.en.u1 + "</p>",
      vragen:vb.slice(0, 2)});
  }
  // stap 2: geen tekst meer, alleen doen
  if(vb.length > 2){
    stappen.push({kop:GC_STAP_TXT.nl.k2, kopEn:GC_STAP_TXT.en.k2,
      uitleg:"", uitlegEn:"", vragen:vb.slice(2)});
  }
  // stap 3: nu pas de vraag naar de regel zelf, met de hele uitleg eronder als naslag
  stappen.push({kop:GC_STAP_TXT.nl.k3, kopEn:GC_STAP_TXT.en.k3,
    uitleg:"", uitlegEn:"",
    diep:c.uitleg, diepEn:c.uitlegEn,
    diepKop:GC_STAP_TXT.nl.d, diepKopEn:GC_STAP_TXT.en.d,
    vragen:[begrip]});
  return {id:"concept-" + c.id, concept:c.id, icon:c.icon,
    titel:c.naam, titelEn:c.naamEn, pitch:pitch, pitchEn:pitchEn,
    stappen:stappen};
}''')

    # de vaste zinnetjes, vlak boven gcBouw
    rep('function gcBouw(id){', '''/* v23.59: de enige tekst die hierbij is gekomen. Vier koppen en één zin, gedeeld door alle
   drieentwintig concepten, zodat de micro-stappen geen nieuwe content per concept vragen. */
var GC_STAP_TXT = {
  nl:{k1:"Probeer eens", u1:"Eerst een voorbeeld, en gok gerust: het antwoord komt er meteen achteraan, met in één zin waarom.",
      k2:"Nog twee", k3:"Waarom dat zo is", d:"De hele regel"},
  en:{k1:"Give it a go", u1:"An example first, and feel free to guess: the answer comes right after, with one line on why.",
      k2:"Two more", k3:"Why that is", d:"The full rule"}
};
function gcBouw(id){''')

    # ---------- 2. een stap zonder tekst slaat de leesfase over ----------
    rep(A_START, '''  /* v23.59: stappen zonder uitleg bestaan sinds deze versie (de voorbeeldstappen gaan meteen naar
     de vraag). Zonder deze regel kreeg je daar een leeg scherm met een knop "Toets me". */
  gwSess = {id:id, stap:s, fase:gwStapHeeftTekst(o, s) ? "uitleg" : "toets",
            vraag:0, goed:0, fout:0, gekozen:null};
  navPush({t:"gramwiz", id:id});
  renderCheat();''')

    rep(A_VOLGENDE, '''    gwSess.stap++;
    gwSess.fase = gwStapHeeftTekst(o, gwSess.stap) ? "uitleg" : "toets";
    gwSess.vraag = 0; gwSess.goed = 0; gwSess.fout = 0; gwSess.gekozen = null;
    renderCheat();''')

    rep('function gwStart(id, stap){', '''// v23.59: heeft deze stap iets te lezen? Zo niet, dan is de leesfase een leeg scherm met een knop.
function gwStapHeeftTekst(o, i){
  try {
    var s = o && o.stappen && o.stappen[i];
    if(!s) return true;
    return !!String(ct(s.uitleg, s.uitlegEn) || "").replace(/<[^>]*>/g, "").trim();
  } catch(e){ return true; }
}
function gwStart(id, stap){''')

    import re
    src = re.sub(r'var APP_VERSIE = "[^"]+";', 'var APP_VERSIE = "%s";' % NIEUW, src, count=1)
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
