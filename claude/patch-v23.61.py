#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.61: het materiaal staat vóór de vraag, en niet twee keer.

Stefan, 12 aug, over een grammaticales: "ik kan niet helemaal zeggen waarom, maar op deze manier heb
ik niet het idee van ah nu snap ik het ofzo."

Belangrijk: dit is een ánder soort les dan wat v23.59 verbouwde. Dat ging over de 23 concepten
(el/la, ser/estar). Dit zijn de gegenereerde onderwerpen: `gwVanSpiek()` knipt een spiekbriefkaart in
blokken en plakt bij elk blok een paar toetsvragen. Nagemeten over alle 24, samen 81 stappen:

    elke stap herhaalt zijn eigen tekst in "De hele spiekbrief erbij"   81 van 81   (100%)
    uitleg korter dan 140 tekens                                       48 van 81   (59%)
    stappen die uit een tabel bestaan                                   19

## 1. Alles stond dubbel

`diep` was altijd `c.html`, de héle kaart. Dus op de stap die de tabel toont, stond diezelfde tabel
er nog een keer onder in de uitklapper. Op Stefans schermafdruk staat "Het rijtje" met vijf
uitdrukkingen, en daaronder "De hele spiekbrief erbij" met exact dezelfde vijf.

Nu bevat `diep` alleen wat níét op deze stap staat, en als dat niets is staat er ook geen
uitklapper. Dat is geen kosmetiek: een uitklapper die belooft dat er meer is en dan hetzelfde geeft,
leert je hem nooit meer open te doen.

## 2. Het materiaal kwam ná de vraag

Stefans stap 1 bestond uit één zin: *"Vaste uitdrukkingen om hoeveelheden aan te geven, met of
zonder 'de':"* — dat is de titel nog een keer, en hij eindigt op een dubbele punt. Een zin die
eindigt op een dubbele punt is een aankondiging; het aangekondigde stond in stap 2. Daartussen
kreeg hij vier vragen over dat rijtje.

Bij de concepten is voorbeeld-vóór-regel juist goed: daar valt iets te beredeneren, en gokken maakt
je klaar voor het antwoord. Hier valt niets te beredeneren. *una cucharada **de** aceite* is geen
regel maar een feit per uitdrukking. Gokken zonder de mogelijkheid om het te weten is geen
productieve fout, dat is gokken.

Twee snijregels erbij, allebei precies te formuleren en dus te toetsen:

  - knip nooit tussen een blok dat op een dubbele punt eindigt en het blok erna
  - knip nooit vlak vóór een tabel: die hoort bij de tekst die hem aankondigt

Die twee blokken worden samengevoegd tot één brok, en pas dáárna worden de brokken over de stappen
verdeeld. Op Stefans onderwerp levert dat een eerste stap op met de aankondiging én het rijtje, en
daarna pas de vragen.

## Wat dit niet oplost

*Hoeveelheden* is geen regel maar een lijstje. "Ah, nu snap ik het" kan alleen ontstaan waar een
keuze zit met iets eronder: el of la, ser of estar, por of para. Bij *una pizca de / un poco de /
una cucharada de* valt niets te snappen, alleen te kennen. Deze versie zorgt dat je het rijtje ziet
vóór je erover wordt bevraagd; hij maakt er geen inzicht van, want dat zit er niet in.

Dat onderscheid — regel of lijst — expliciet maken in de app staat op de lijst voor na de lancering.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.61"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "function gwPlak" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_BLOK = '''function gwVerdeel(n, k){'''

A_STAP = '''  var k = Math.min(blokken.length, 4, vragen.length);
  var bGroep = gwVerdeel(blokken.length, k);
  var vGroep = gwVerdeel(vragen.length, k);
  var stappen = bGroep.map(function(g, i){
    var eigen = blokken.slice(g[0], g[1]).join("");
    return {
      kop: gwKopUit(blokken[g[0]], i, false),
      kopEn: gwKopUit((zelfdeVorm ? blokkenEn : blokken)[g[0]], i, true),
      uitleg: eigen,
      uitlegEn: zelfdeVorm ? blokkenEn.slice(g[0], g[1]).join("") : eigen,
      diepKop: "De hele spiekbrief erbij",
      diepKopEn: "The whole cheat sheet",
      diep: c.html,
      diepEn: c.htmlEn || c.html,
      vragen: vragen.slice(vGroep[i][0], vGroep[i][1])
    };
  });'''

if DOE_APP:
    ontbreekt = [a for a in [A_BLOK, A_STAP] if a not in src]
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
    # ---------- 1. blokken die bij elkaar horen blijven bij elkaar ----------
    rep(A_BLOK, '''/* v23.61: sommige blokken horen bij elkaar en mogen niet over twee stappen verdeeld worden.
   Stefan kreeg als hele uitleg van stap 1: "Vaste uitdrukkingen om hoeveelheden aan te geven, met
   of zonder 'de':" — de titel nog een keer, eindigend op een dubbele punt. Het aangekondigde rijtje
   stond in stap 2, en daartussen kreeg hij er vier vragen over.

   Twee regels, allebei precies te formuleren:
     - een blok dat eindigt op een dubbele punt kondigt het volgende aan en hoort eraan vast
     - vlak vóór een tabel knippen mag niet: die hoort bij de tekst die hem aankondigt

   Het resultaat is een lijst brokken in plaats van losse blokken; die brokken gaan daarna gewoon
   door gwVerdeel(). */
function gwPlak(blokken){
  var plat = function(h){ return String(h || "").replace(/<[^>]*>/g, " ").replace(/\\s+/g, " ").trim(); };
  var brok = [], huidig = [];
  for(var i = 0; i < blokken.length; i++){
    huidig.push(i);
    var deze = blokken[i], volgende = blokken[i + 1];
    var kondigtAan = /[:\\u003a]\\s*$/.test(plat(deze));
    var volgendeIsTabel = !!volgende && /^<table\\b/i.test(volgende);
    if(volgende && (kondigtAan || volgendeIsTabel)) continue;   // aan elkaar plakken
    brok.push(huidig); huidig = [];
  }
  if(huidig.length) brok.push(huidig);
  return brok;
}
function gwVerdeel(n, k){''')

    # ---------- 2. de stappen: brokken, en geen dubbele spiekbrief ----------
    rep(A_STAP, '''  /* v23.61: eerst blokken die bij elkaar horen aan elkaar plakken (zie gwPlak), en pas daarna
     verdelen. Anders belandt een aankondiging in de ene stap en het aangekondigde rijtje in de
     volgende, met de vragen erover ertussenin. */
  var brok = gwPlak(blokken);
  var k = Math.min(brok.length, 4, vragen.length);
  var bGroep = gwVerdeel(brok.length, k);
  var vGroep = gwVerdeel(vragen.length, k);
  var stappen = bGroep.map(function(g, i){
    // van brokindex naar blokindex
    var idx = [];
    for(var b = g[0]; b < g[1]; b++){ idx = idx.concat(brok[b]); }
    var eerste = idx[0];
    var eigen = idx.map(function(j){ return blokken[j]; }).join("");
    var eigenEn = zelfdeVorm ? idx.map(function(j){ return blokkenEn[j]; }).join("") : eigen;
    /* v23.61: diep was c.html, de héle kaart, op élke stap. Dus de stap die de tabel toont had
       diezelfde tabel er nog een keer onder staan in de uitklapper. Gemeten: 81 van 81 stappen.
       Een uitklapper die belooft dat er meer is en dan hetzelfde geeft, leert je hem nooit meer
       open te doen. Nu staat er alleen in wat niet al op deze stap staat, en is hij er niet als
       dat niets is. */
    var rest = [], restEn = [];
    for(var j = 0; j < blokken.length; j++){
      if(idx.indexOf(j) !== -1) continue;
      rest.push(blokken[j]);
      restEn.push(zelfdeVorm ? blokkenEn[j] : blokken[j]);
    }
    var s = {
      kop: gwKopUit(blokken[eerste], i, false),
      kopEn: gwKopUit((zelfdeVorm ? blokkenEn : blokken)[eerste], i, true),
      uitleg: eigen,
      uitlegEn: eigenEn,
      vragen: vragen.slice(vGroep[i][0], vGroep[i][1])
    };
    if(rest.length){
      s.diepKop = "De rest van de spiekbrief";
      s.diepKopEn = "The rest of the cheat sheet";
      s.diep = rest.join("");
      s.diepEn = restEn.join("");
    }
    return s;
  });''')

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
